from collections import Counter
from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models
from ..auth import require_permission
from ..database import get_db

router = APIRouter(prefix="/api/dashboard", tags=["数据看板"])


@router.get("/summary")
def summary(
    _: models.User = Depends(require_permission("dashboard:view")),
    db: Session = Depends(get_db),
):
    return {
        "user_count": db.query(models.User).count(),
        "role_count": db.query(models.Role).count(),
        "product_count": db.query(models.Product).count(),
        "product_on_count": db.query(models.Product)
        .filter(models.Product.status == "on")
        .count(),
    }


@router.get("/growth")
def user_growth(
    _: models.User = Depends(require_permission("dashboard:view")),
    db: Session = Depends(get_db),
):
    """近 7 日新增用户数。"""
    today = date.today()
    start = today - timedelta(days=6)
    users = (
        db.query(models.User)
        .filter(models.User.created_at >= start)
        .all()
    )
    counter = Counter(u.created_at.date() for u in users)
    days = [start + timedelta(days=i) for i in range(7)]
    return [
        {"date": d.strftime("%m-%d"), "count": counter.get(d, 0)}
        for d in days
    ]


@router.get("/categories")
def product_categories_distribution(
    _: models.User = Depends(require_permission("dashboard:view")),
    db: Session = Depends(get_db),
):
    """商品分类分布。"""
    products = db.query(models.Product).all()
    counter = Counter(p.category or "未分类" for p in products)
    return [{"name": name, "value": count} for name, count in counter.items()]
