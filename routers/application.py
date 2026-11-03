import random
import string
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any, Optional

from database import get_session
from models import Application, Activity, Student, Department, User
from routers.auth import get_current_user

router = APIRouter(prefix="/api/v1/application", tags=["报名管理"])

class ApplicationSubmit(BaseModel):
    student_id: int
    activity_id: int
    wish_1_dept_id: int
    wish_2_dept_id: Optional[int] = None
    form_data: Dict[str, Any]

def generate_tg_code():
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choices(characters, k=8))

@router.post("/submit", summary="学生提交报名")
def submit_application(data: ApplicationSubmit, session: Session = Depends(get_session)):
    activity = session.get(Activity, data.activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")

    student = session.get(Student, data.student_id)
    if not student:
        student = Student(
            id=data.student_id, openid=f"test_{data.student_id}", name="测试学生", 
            student_no=f"2026{data.student_id}", phone="13800000000"
        )
        session.add(student)
        session.commit()

    # 覆盖旧数据防止报错
    existing = session.exec(select(Application).where(Application.student_id == data.student_id, Application.activity_id == data.activity_id)).first()
    if existing:
        session.delete(existing)
        session.commit()

    tg_code = generate_tg_code()
    while session.exec(select(Application).where(Application.tg_code == tg_code)).first():
        tg_code = generate_tg_code()

    new_app = Application(
        activity_id=data.activity_id, student_id=data.student_id,
        wish_1_dept_id=data.wish_1_dept_id, wish_2_dept_id=data.wish_2_dept_id,
        form_data=data.form_data, tg_code=tg_code, status="submitted"
    )
    session.add(new_app)
    session.commit()
    session.refresh(new_app)
    return {"msg": "报名提交成功", "tg_code": new_app.tg_code}

# --- 新增：部门管理员看本部门简历 ---
@router.get("/dept-list", summary="分管看本部门的报名列表")
def get_dept_applications(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # 1. 找到当前管理员管理的部门
    dept = session.exec(select(Department).where(Department.sub_admin_id == current_user.id)).first()
    if not dept:
        raise HTTPException(status_code=404, detail="你还未被分配管理部门")

    # 2. 找出第一志愿或第二志愿是这个部门的报名记录
    apps = session.exec(
        select(Application).where(
            (Application.wish_1_dept_id == dept.id) | (Application.wish_2_dept_id == dept.id)
        )
    ).all()
    return {"dept_name": dept.name, "total": len(apps), "data": apps}

# --- 新增：扫码签到接口 ---
@router.post("/checkin/{tg_code}", summary="现场扫码签到")
def checkin(
    tg_code: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    app = session.exec(select(Application).where(Application.tg_code == tg_code)).first()
    if not app:
        raise HTTPException(status_code=404, detail="无效的报名码")
    if app.status == "interview":
        raise HTTPException(status_code=400, detail="该学生已签到，请勿重复操作")
    
    app.status = "interview"
    session.add(app)
    session.commit()
    return {"msg": "签到成功", "student_id": app.student_id, "ai_summary": "这是AI生成的总结（开发中）"}
    # --- 新增：获取活动统计数据 (供超管看板使用) ---
@router.get("/stats", summary="获取报名与签到统计")
def get_stats(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # 统计总报名人数
    total_apps = len(session.exec(select(Application)).all())
    
    # 统计已签到人数 (状态为 interview 的)
    checked_in = len(session.exec(select(Application).where(Application.status == "interview")).all())
    
    # 统计已录取人数
    accepted = len(session.exec(select(Application).where(Application.status == "accepted")).all())

    return {
        "msg": "success",
        "data": {
            "total": total_apps,
            "checkin": checked_in,
            "accepted": accepted
        }
    }