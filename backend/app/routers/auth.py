from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import (
    create_access_token,
    get_client_ip,
    get_current_user,
    hash_password,
    verify_password,
)
from ..captcha import generate_captcha, verify_captcha
from ..config import settings
from ..database import get_db

router = APIRouter(prefix="/api/auth", tags=["认证"])


def _record_login(db: Session, username: str, ip: str, success: bool, message: str):
    """记录登录日志。"""
    try:
        db.add(
            models.LoginLog(
                username=username,
                ip=ip,
                success=1 if success else 0,
                message=message,
            )
        )
        db.commit()
    except Exception:
        db.rollback()


@router.get("/captcha", response_model=schemas.CaptchaResponse)
def captcha():
    return generate_captcha()


@router.post("/login", response_model=schemas.TokenResponse)
def login(body: schemas.LoginRequest, request: Request, db: Session = Depends(get_db)):
    ip = get_client_ip(request)

    # 1. 校验验证码
    if not body.captcha_id or not verify_captcha(body.captcha_id, body.captcha_code):
        _record_login(db, body.username, ip, False, "验证码错误")
        raise HTTPException(status_code=400, detail="验证码错误")

    # 2. 校验账号密码
    user = (
        db.query(models.User)
        .filter(models.User.username == body.username)
        .first()
    )

    # 锁定检查
    if user and user.locked_until and user.locked_until > datetime.now():
        minutes_left = max(1, int((user.locked_until - datetime.now()).total_seconds() // 60) + 1)
        _record_login(db, body.username, ip, False, "账号已被锁定")
        raise HTTPException(status_code=423, detail=f"密码错误次数过多,账号已锁定,请 {minutes_left} 分钟后再试")

    if not user or not verify_password(body.password, user.password):
        message = "用户名或密码错误"
        if user:
            user.failed_attempts = (user.failed_attempts or 0) + 1
            if user.failed_attempts >= settings.LOGIN_MAX_ATTEMPTS:
                user.locked_until = datetime.now() + timedelta(minutes=settings.LOGIN_LOCK_MINUTES)
                user.failed_attempts = 0
                message = f"密码错误次数过多,账号已锁定,请 {settings.LOGIN_LOCK_MINUTES} 分钟后再试"
            db.commit()
        _record_login(db, body.username, ip, False, message)
        raise HTTPException(status_code=400, detail=message)

    if user.status != "active":
        _record_login(db, body.username, ip, False, "账号已被禁用")
        raise HTTPException(status_code=403, detail="账号已被禁用")

    # 登录成功:清零失败计数与锁定
    if user.failed_attempts or user.locked_until:
        user.failed_attempts = 0
        user.locked_until = None
        db.commit()
    _record_login(db, body.username, ip, True, "登录成功")

    return schemas.TokenResponse(access_token=create_access_token(user.id))


@router.get("/me", response_model=schemas.UserOut)
def me(current_user: models.User = Depends(get_current_user)):
    return current_user


@router.put("/profile", response_model=schemas.UserOut)
def update_profile(
    body: schemas.ProfileUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = body.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(current_user, key, value)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/change-password")
def change_password(
    body: schemas.ChangePasswordRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(body.old_password, current_user.password):
        raise HTTPException(status_code=400, detail="原密码错误")
    if len(body.new_password) < 6:
        raise HTTPException(status_code=400, detail="新密码长度不能少于 6 位")
    if body.new_password == body.old_password:
        raise HTTPException(status_code=400, detail="新密码不能与原密码相同")
    current_user.password = hash_password(body.new_password)
    db.commit()
    return {"message": "密码修改成功"}
