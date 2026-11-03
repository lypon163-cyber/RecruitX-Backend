from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import Optional

from database import get_session
from models import Department, User, School
from routers.auth import get_current_user

router = APIRouter(prefix="/api/v1/department", tags=["部门管理"])

class DeptCreate(BaseModel):
    name: str

@router.post("/create", summary="超管创建部门")
def create_department(
    data: DeptCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "super":
        raise HTTPException(status_code=403, detail="仅超管可建部门")
    
    # 建部门
    new_dept = Department(
        school_id=current_user.school_id or 1,
        name=data.name
    )
    session.add(new_dept)
    session.commit()
    session.refresh(new_dept)
    return {"msg": "部门创建成功", "dept_id": new_dept.id, "name": new_dept.name}