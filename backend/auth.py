# auth.py
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = "SUPER_SECRET_KEY"
ALGORITHM = "HS256"
ACCESS_EXPIRE_MIN = 60 * 24  # 24h

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str):
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict):
    to_encode = data.copy()
    to_encode["exp"] = datetime.utcnow() + timedelta(minutes=ACCESS_EXPIRE_MIN)
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
