from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .middleware import operation_log_middleware
from .migrations import run_migrations
from .routers import auth, dashboard, logs, products, roles, users

app = FastAPI(title="后台管理系统 API", version="2.0.0")

# 开发环境允许前端跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 操作日志中间件(记录 /api 写操作)
app.middleware("http")(operation_log_middleware)

# 启动时建表 + 轻量迁移
run_migrations()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(roles.router)
app.include_router(products.router)
app.include_router(dashboard.router)
app.include_router(logs.router)


@app.get("/")
def root():
    return {"message": "后台管理系统 API", "docs": "/docs", "version": "2.0.0"}
