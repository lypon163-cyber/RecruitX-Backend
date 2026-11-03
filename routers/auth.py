from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session, select
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional

from database import get_session
from models import User
from security import verify_password, create_access_token, get_password_hash, SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/api/v1/auth", tags=["认证管理"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# --- 辅助函数：获取当前登录用户 ---
def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="登录已过期或凭证无效",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise credentials_exception
    return user

# --- 接口 1：初始化测试超管（仅用来测试） ---
@router.post("/init-super", summary="初始化一个测试超级管理员")
def init_super_admin(session: Session = Depends(get_session)):
    existing = session.exec(select(User).where(User.username == "admin")).first()
    if existing:
        return {"msg": "超管已存在，账号: admin, 密码: 123456"}
    
    new_user = User(
        username="admin",
        password=get_password_hash("123456"),
        role="super"
    )
    session.add(new_user)
    session.commit()
    return {"msg": "创建成功，账号: admin, 密码: 123456"}

# --- 接口 2：登录获取 Token ---
@router.post("/login", summary="管理员登录")
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == form_data.username)).first()
    
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="账号或密码错误")
    
    # 生成通行证
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# --- 接口 3：获取当前登录人信息 ---
@router.get("/me", summary="获取当前登录人信息")
def read_users_me(current_user: User = Depends(get_current_user)):
    return {"username": current_user.username, "role": current_user.role}