from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(200), nullable=False)
    nickname = Column(String(50))
    email = Column(String(100))
    phone = Column(String(20))
    status = Column(String(20), default="active")  # active / disabled
    role_id = Column(Integer, ForeignKey("roles.id"))
    # 登录安全
    failed_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    role = relationship("Role")


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    description = Column(String(200))
    permissions = Column(JSON, default=list)  # 如 ["user:view","user:add"],SQLite 存储为 TEXT
    created_at = Column(DateTime, default=datetime.now)


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50))
    price = Column(Float, default=0)
    stock = Column(Integer, default=0)
    status = Column(String(20), default="on")  # on / off
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)


class LoginLog(Base):
    """登录日志:每次登录尝试(成功/失败/锁定)都会记录。"""

    __tablename__ = "login_logs"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), index=True)
    ip = Column(String(50))
    success = Column(Integer, default=0)  # 1 成功 / 0 失败
    message = Column(String(200))
    created_at = Column(DateTime, default=datetime.now, index=True)


class OperationLog(Base):
    """操作日志:记录用户增删改操作。"""

    __tablename__ = "operation_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    username = Column(String(50), index=True)
    method = Column(String(10))
    path = Column(String(200))
    status_code = Column(Integer)
    params = Column(Text)  # JSON 字符串(已脱敏)
    ip = Column(String(50))
    created_at = Column(DateTime, default=datetime.now, index=True)
