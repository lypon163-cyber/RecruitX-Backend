import time
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = "your-super-secret-key-please-change-in-production"
ALGORITHM = "HS256"
# 改成10年，也就是 60分钟 * 24小时 * 365天 * 10年
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 365 * 10 

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    # 使用最标准的 Unix 时间戳，绝对不会算错年份
    expire = int(time.time()) + (ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt