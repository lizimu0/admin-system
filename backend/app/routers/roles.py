from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import require_permission
from ..database import get_db

router = APIRouter(prefix="/api/roles", tags=["角色管理"])


@router.get("", response_model=schemas.PageResult[schemas.RoleOut])
def list_roles(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    keyword: str = "",
    _: models.User = Depends(require_permission("role:view")),
    db: Session = Depends(get_db),
):
    query = db.query(models.Role)
    if keyword:
        query = query.filter(models.Role.name.like(f"%{keyword}%"))
    total = query.count()
    items = (
        query.order_by(models.Role.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {"total": total, "items": items}


@router.get("/all", response_model=list[schemas.RoleOut])
def all_roles(
    _: models.User = Depends(require_permission("role:view")),
    db: Session = Depends(get_db),
):
    return db.query(models.Role).all()


@router.post("", response_model=schemas.RoleOut)
def create_role(
    body: schemas.RoleCreate,
    _: models.User = Depends(require_permission("role:add")),
    db: Session = Depends(get_db),
):
    if db.query(models.Role).filter(models.Role.code == body.code).first():
        raise HTTPException(status_code=400, detail="角色编码已存在")
    role = models.Role(
        name=body.name,
        code=body.code,
        description=body.description,
        permissions=body.permissions,
    )
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


@router.put("/{role_id}", response_model=schemas.RoleOut)
def update_role(
    role_id: int,
    body: schemas.RoleUpdate,
    _: models.User = Depends(require_permission("role:edit")),
    db: Session = Depends(get_db),
):
    role = db.query(models.Role).filter(models.Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    data = body.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(role, key, value)
    db.commit()
    db.refresh(role)
    return role


@router.delete("/{role_id}")
def delete_role(
    role_id: int,
    _: models.User = Depends(require_permission("role:delete")),
    db: Session = Depends(get_db),
):
    role = db.query(models.Role).filter(models.Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    if db.query(models.User).filter(models.User.role_id == role_id).count() > 0:
        raise HTTPException(status_code=400, detail="该角色下仍有用户,无法删除")
    db.delete(role)
    db.commit()
    return {"message": "删除成功"}
