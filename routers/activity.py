from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any, Optional

from database import get_session
from models import Activity, User, School # 引入 School
from routers.auth import get_current_user

router = APIRouter(prefix="/api/v1/activity", tags=["活动管理"])

class ActivityCreate(BaseModel):
    title: str
    start_time: datetime
    end_time: datetime
    form_config: Dict[str, Any]

@router.post("/create", summary="创建招新活动（仅超管）")
def create_activity(
    data: ActivityCreate, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "super":
        raise HTTPException(status_code=403, detail="权限不足，仅超级管理员可操作")

    if data.end_time <= data.start_time:
        raise HTTPException(status_code=400, detail="结束时间必须晚于开始时间")

    # --- 修复：确保有学校ID ---
    school_id = current_user.school_id
    if not school_id:
        # 如果超管没绑定学校，先检查数据库里有没有默认学校，没有就建一个
        default_school = session.exec(select(School).where(School.id == 1)).first()
        if not default_school:
            default_school = School(name="默认测试大学", short_name="TEST")
            session.add(default_school)
            session.commit()
            session.refresh(default_school)
        
        school_id = default_school.id
        # 顺便把超管和这个学校绑定
        current_user.school_id = school_id
        session.add(current_user)
        session.commit()

    new_activity = Activity(
        school_id=school_id,
        title=data.title,
        start_time=data.start_time,
        end_time=data.end_time,
        form_config=data.form_config
    )
    session.add(new_activity)
    session.commit()
    session.refresh(new_activity)

    return {"msg": "活动创建成功", "activity_id": new_activity.id, "title": new_activity.title}