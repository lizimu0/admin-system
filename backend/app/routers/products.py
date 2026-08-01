import io
from datetime import datetime
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import require_permission
from ..database import get_db

router = APIRouter(prefix="/api/products", tags=["商品管理"])


@router.get("", response_model=schemas.PageResult[schemas.ProductOut])
def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    keyword: str = "",
    category: str = "",
    _: models.User = Depends(require_permission("product:view")),
    db: Session = Depends(get_db),
):
    query = db.query(models.Product)
    if keyword:
        query = query.filter(models.Product.name.like(f"%{keyword}%"))
    if category:
        query = query.filter(models.Product.category == category)
    total = query.count()
    items = (
        query.order_by(models.Product.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {"total": total, "items": items}


@router.get("/categories", response_model=list[str])
def product_categories(
    _: models.User = Depends(require_permission("product:view")),
    db: Session = Depends(get_db),
):
    rows = db.query(models.Product.category).distinct().all()
    return [r[0] for r in rows if r[0]]


@router.get("/export")
def export_products(
    keyword: str = "",
    category: str = "",
    _: models.User = Depends(require_permission("product:view")),
    db: Session = Depends(get_db),
):
    """导出商品列表为 Excel(支持关键字/分类筛选)。"""
    query = db.query(models.Product)
    if keyword:
        query = query.filter(models.Product.name.like(f"%{keyword}%"))
    if category:
        query = query.filter(models.Product.category == category)
    products = query.order_by(models.Product.id.desc()).all()

    wb = Workbook()
    ws = wb.active
    ws.title = "商品列表"
    ws.append(["ID", "商品名称", "分类", "价格", "库存", "状态", "描述", "创建时间"])
    for p in products:
        ws.append(
            [
                p.id,
                p.name,
                p.category,
                p.price,
                p.stock,
                "在售" if p.status == "on" else "下架",
                p.description,
                p.created_at.strftime("%Y-%m-%d %H:%M:%S") if p.created_at else "",
            ]
        )

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"商品列表_{ts}.xlsx"
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": (
                f'attachment; filename="products_{ts}.xlsx"; '
                f"filename*=UTF-8''{quote(filename)}"
            )
        },
    )


@router.post("", response_model=schemas.ProductOut)
def create_product(
    body: schemas.ProductCreate,
    _: models.User = Depends(require_permission("product:add")),
    db: Session = Depends(get_db),
):
    product = models.Product(**body.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.put("/{product_id}", response_model=schemas.ProductOut)
def update_product(
    product_id: int,
    body: schemas.ProductUpdate,
    _: models.User = Depends(require_permission("product:edit")),
    db: Session = Depends(get_db),
):
    product = (
        db.query(models.Product).filter(models.Product.id == product_id).first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    data = body.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    _: models.User = Depends(require_permission("product:delete")),
    db: Session = Depends(get_db),
):
    product = (
        db.query(models.Product).filter(models.Product.id == product_id).first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    db.delete(product)
    db.commit()
    return {"message": "删除成功"}
