from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel
from sqlalchemy import JSON, Column

# 1. 学校/组织表
class School(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, description="学校或组织名称")
    short_name: str = Field(description="简称，用于生成专属码")

# 2. 管理员表 (超管和分管)
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, description="登录账号")
    password: str = Field(description="加密后的密码")
    role: str = Field(default="sub", description="角色: super(超管) / sub(分管)")
    school_id: Optional[int] = Field(default=None, foreign_key="school.id")

# 3. 学生表
class Student(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    openid: str = Field(index=True, unique=True, description="微信OpenID")
    name: str = Field(index=True, description="学生姓名")
    student_no: str = Field(index=True, description="学号")
    phone: str = Field(description="手机号")

# 4. 部门表
class Department(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    school_id: int = Field(foreign_key="school.id")
    name: str = Field(description="部门名称，如：宣传部")
    sub_admin_id: Optional[int] = Field(default=None, foreign_key="user.id")

# 5. 招新活动表
class Activity(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    school_id: int = Field(foreign_key="school.id")
    title: str = Field(description="活动名称")
    form_config: dict = Field(default={}, sa_column=Column(JSON), description="问卷配置JSON")
    start_time: datetime = Field(description="报名开始时间")
    end_time: datetime = Field(description="报名截止时间")

# 6. 报名记录表 (最核心的表)
class Application(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    activity_id: int = Field(foreign_key="activity.id")
    student_id: int = Field(foreign_key="student.id")
    wish_1_dept_id: int = Field(description="第一志愿部门ID")
    wish_2_dept_id: Optional[int] = Field(default=None, description="第二志愿部门ID")
    form_data: dict = Field(default={}, sa_column=Column(JSON), description="学生填写的问卷答案")
    tg_code: str = Field(index=True, unique=True, description="8位专属TG码")
    status: str = Field(default="submitted", description="状态: submitted, passed, interview, accepted, rejected")
    pdf_url: Optional[str] = Field(default=None, description="生成的PDF文件地址")

# 7. 面试记录表
class Interview(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    application_id: int = Field(foreign_key="application.id")
    admin_id: int = Field(foreign_key="user.id")
    ai_summary: Optional[str] = Field(default=None, description="AI个人陈述总结")
    score: Optional[int] = Field(default=None, description="面试打分")
    comment: Optional[str] = Field(default=None, description="面试官评语")

# 8. 签到记录表
class Checkin(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    application_id: int = Field(foreign_key="application.id")
    checkin_type: str = Field(default="scan", description="签到方式: scan(扫码) / manual(手动)")
    checkin_time: datetime = Field(default_factory=datetime.utcnow, description="签到时间")