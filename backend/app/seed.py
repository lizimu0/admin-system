"""演示数据初始化脚本: python -m app.seed
幂等:已存在的数据不会重复创建。
"""
import sys

# Windows 控制台默认 GBK,强制 UTF-8 以支持 emoji/中文输出
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from . import models
from .auth import hash_password
from .database import SessionLocal
from .migrations import run_migrations

# 普通用户角色的默认权限(可通过角色管理页面调整)
USER_ROLE_PERMISSIONS = [
    "dashboard:view",
    "user:view",
    "role:view",
    "product:view",
]

PRODUCT_CATEGORIES = ["电子产品", "办公用品", "生活百货", "食品饮料"]


def run():
    run_migrations()
    db = SessionLocal()
    try:
        # --- 角色 ---
        admin_role = db.query(models.Role).filter_by(code="admin").first()
        if not admin_role:
            admin_role = models.Role(
                name="超级管理员",
                code="admin",
                description="拥有全部权限",
                permissions=["*"],
            )
            db.add(admin_role)

        user_role = db.query(models.Role).filter_by(code="user").first()
        if not user_role:
            user_role = models.Role(
                name="普通用户",
                code="user",
                description="仅可查看数据,无增删改权限",
                permissions=USER_ROLE_PERMISSIONS,
            )
            db.add(user_role)
        db.commit()

        # --- 账号 ---
        if not db.query(models.User).filter_by(username="admin").first():
            db.add(
                models.User(
                    username="admin",
                    password=hash_password("admin123"),
                    nickname="管理员",
                    email="admin@example.com",
                    role_id=admin_role.id,
                )
            )
        if not db.query(models.User).filter_by(username="test").first():
            db.add(
                models.User(
                    username="test",
                    password=hash_password("test123"),
                    nickname="测试用户",
                    email="test@example.com",
                    role_id=user_role.id,
                )
            )
        db.commit()

        # --- 演示商品 ---
        if db.query(models.Product).count() == 0:
            for i in range(1, 25):
                db.add(
                    models.Product(
                        name=f"示例商品 {i}",
                        category=PRODUCT_CATEGORIES[i % len(PRODUCT_CATEGORIES)],
                        price=round(9.9 + i * 3.7, 2),
                        stock=i * 6,
                        status="on" if i % 3 else "off",
                        description=f"这是第 {i} 个演示商品,用于展示增删改查功能。",
                    )
                )
            db.commit()

        print("✅ 种子数据初始化完成")
        print(f"   管理员账号: admin / admin123")
        print(f"   普通用户:   test / test123")
    finally:
        db.close()


if __name__ == "__main__":
    run()
