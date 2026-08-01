import io
from datetime import datetime
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user, hash_password, require_permission
from ..database import get_db

router = APIRouter(prefix="/api/users", tags=["用户管理"])


@router.get("", response_model=schemas.PageResult[schemas.UserOut])
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    keyword: str = "",
    _: models.User = Depends(require_permission("user:view")),
    db: Session = Depends(get_db),
):
    query = db.query(models.User)
    if keyword:
        like = f"%{keyword}%"
        query = query.filter(
            models.User.username.like(like)
            | models.User.nickname.like(like)
            | models.User.email.like(like)
            | models.User.phone.like(like)
        )
    total = query.count()
    items = (
        query.order_by(models.User.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {"total": total, "items": items}


@router.post("", response_model=schemas.UserOut)
def create_user(
    body: schemas.UserCreate,
    _: models.User = Depends(require_permission("user:add")),
    db: Session = Depends(get_db),
):
    exists = (
        db.query(models.User).filter(models.User.username == body.username).first()
    )
    if exists:
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = models.User(
        username=body.username,
        password=hash_password(body.password),
        nickname=body.nickname,
        email=body.email,
        phone=body.phone,
        status=body.status,
        role_id=body.role_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/{user_id}", response_model=schemas.UserOut)
def update_user(
    user_id: int,
    body: schemas.UserUpdate,
    _: models.User = Depends(require_permission("user:edit")),
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    data = body.model_dump(exclude_unset=True)
    password = data.pop("password", None)
    for key, value in data.items():
        setattr(user, key, value)
    if password:
        user.password = hash_password(password)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    _: models.User = Depends(require_permission("user:delete")),
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    db.delete(user)
    db.commit()
    return {"message": "删除成功"}


@router.get("/roles/options", response_model=list[schemas.RoleOut])
def user_role_options(
    _: models.User = Depends(require_permission("user:view")),
    db: Session = Depends(get_db),
):
    """用户表单中角色下拉框数据源。"""
    return db.query(models.Role).all()


@router.get("/export")
def export_users(
    keyword: str = "",
    _: models.User = Depends(require_permission("user:view")),
    db: Session = Depends(get_db),
):
    """导出用户列表为 Excel(支持关键字筛选)。"""
    query = db.query(models.User)
    if keyword:
        like = f"%{keyword}%"
        query = query.filter(
            models.User.username.like(like)
            | models.User.nickname.like(like)
            | models.User.email.like(like)
            | models.User.phone.like(like)
        )
    users = query.order_by(models.User.id.desc()).all()

    wb = Workbook()
    ws = wb.active
    ws.title = "用户列表"
    ws.append(["ID", "用户名", "昵称", "邮箱", "手机号", "角色", "状态", "创建时间"])
    for u in users:
        ws.append(
            [
                u.id,
                u.username,
                u.nickname,
                u.email,
                u.phone,
                u.role.name if u.role else "",
                "启用" if u.status == "active" else "禁用",
                u.created_at.strftime("%Y-%m-%d %H:%M:%S") if u.created_at else "",
            ]
        )

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"用户列表_{ts}.xlsx"
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": (
                f'attachment; filename="users_{ts}.xlsx"; '
                f"filename*=UTF-8''{quote(filename)}"
            )
        },
    )
