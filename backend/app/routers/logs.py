from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import require_permission
from ..database import get_db

router = APIRouter(prefix="/api/logs", tags=["日志管理"])


@router.get("/operation", response_model=schemas.PageResult[schemas.OperationLogOut])
def list_operation_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    username: str = "",
    method: str = "",
    _: models.User = Depends(require_permission("log:view")),
    db: Session = Depends(get_db),
):
    query = db.query(models.OperationLog)
    if username:
        query = query.filter(models.OperationLog.username.like(f"%{username}%"))
    if method:
        query = query.filter(models.OperationLog.method == method.upper())
    total = query.count()
    items = (
        query.order_by(models.OperationLog.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {"total": total, "items": items}


@router.get("/login", response_model=schemas.PageResult[schemas.LoginLogOut])
def list_login_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    username: str = "",
    success: int = Query(0, ge=0, le=2),  # 0 全部 / 1 成功 / 2 失败
    _: models.User = Depends(require_permission("log:view")),
    db: Session = Depends(get_db),
):
    query = db.query(models.LoginLog)
    if username:
        query = query.filter(models.LoginLog.username.like(f"%{username}%"))
    if success == 1:
        query = query.filter(models.LoginLog.success == 1)
    elif success == 2:
        query = query.filter(models.LoginLog.success == 0)
    total = query.count()
    items = (
        query.order_by(models.LoginLog.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {"total": total, "items": items}
