"""演示数据初始化脚本: python -m app.seed
幂等:已存在的数据不会重复创建。

初始密码策略:
- 优先读取环境变量 ADMIN_INITIAL_PASSWORD / TEST_INITIAL_PASSWORD(推荐在 .env 中设置);
- 未配置时随机生成并仅在创建时打印一次,避免仓库文档中的固定密码成为生产环境默认凭据。
"""
import os
import secrets
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


def initial_password(env_name: str) -> str:
    """从环境变量读取初始密码,未配置则随机生成 12 位密码。"""
    value = os.getenv(env_name, "").strip()
    if value:
        return value
    return secrets.token_urlsafe(9)


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
        created: list[tuple[str, str]] = []
        admin_password = initial_password("ADMIN_INITIAL_PASSWORD")
        if not db.query(models.User).filter_by(username="admin").first():
            db.add(
                models.User(
                    username="admin",
                    password=hash_password(admin_password),
                    nickname="管理员",
                    email="admin@example.com",
                    role_id=admin_role.id,
                )
            )
            created.append(("admin", admin_password))
        test_password = initial_password("TEST_INITIAL_PASSWORD")
        if not db.query(models.User).filter_by(username="test").first():
            db.add(
                models.User(
                    username="test",
                    password=hash_password(test_password),
                    nickname="测试用户",
                    email="test@example.com",
                    role_id=user_role.id,
                )
            )
            created.append(("test", test_password))
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
        if created:
            print("   以下账号为本次新建,初始密码仅在本次输出(请立即保存或登录后修改):")
            for username, password in created:
                print(f"     {username} / {password}")
            if not os.getenv("ADMIN_INITIAL_PASSWORD"):
                print("   提示: 在 backend/.env 中设置 ADMIN_INITIAL_PASSWORD / TEST_INITIAL_PASSWORD 可固定初始密码")
        else:
            print("   账号已存在,初始密码保持不变")
    finally:
        db.close()


if __name__ == "__main__":
    run()
