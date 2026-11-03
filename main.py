from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from database import engine
import models

# 这里必须包含 department
from routers import auth, activity, application, department

SQLModel.metadata.create_all(engine)

app = FastAPI(title="招新快线 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载路由
app.include_router(auth.router)
app.include_router(activity.router)
app.include_router(application.router)
# 这里必须有 department.router
app.include_router(department.router)

@app.get("/")
def read_root():
    return {"message": "Hello RecruitX! 数据库已连接！"}