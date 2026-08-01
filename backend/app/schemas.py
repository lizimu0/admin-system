from datetime import datetime
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PageResult(BaseModel, Generic[T]):
    total: int
    items: List[T]


# ---------- 认证 ----------
class LoginRequest(BaseModel):
    username: str
    password: str
    captcha_id: str = ""
    captcha_code: str = ""


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CaptchaResponse(BaseModel):
    captcha_id: str
    image: str  # base64 PNG


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class ProfileUpdate(BaseModel):
    nickname: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


# ---------- 日志 ----------
class LoginLogOut(BaseModel):
    id: int
    username: Optional[str] = None
    ip: Optional[str] = None
    success: int
    message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class OperationLogOut(BaseModel):
    id: int
    user_id: Optional[int] = None
    username: Optional[str] = None
    method: Optional[str] = None
    path: Optional[str] = None
    status_code: Optional[int] = None
    params: Optional[str] = None
    ip: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- 角色 ----------
class RoleOut(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str] = None
    permissions: List[str] = []
    created_at: datetime

    class Config:
        from_attributes = True


class RoleCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    permissions: List[str] = []


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[List[str]] = None


# ---------- 用户 ----------
class UserOut(BaseModel):
    id: int
    username: str
    nickname: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    status: str
    role_id: Optional[int] = None
    created_at: datetime
    role: Optional[RoleOut] = None

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    username: str
    password: str
    nickname: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    status: str = "active"
    role_id: Optional[int] = None


class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None
    role_id: Optional[int] = None
    password: Optional[str] = None


# ---------- 商品 ----------
class ProductOut(BaseModel):
    id: int
    name: str
    category: Optional[str] = None
    price: float
    stock: int
    status: str
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ProductCreate(BaseModel):
    name: str
    category: Optional[str] = None
    price: float = 0
    stock: int = 0
    status: str = "on"
    description: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    status: Optional[str] = None
    description: Optional[str] = None
