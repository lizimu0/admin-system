<p align="center">
  <img src="docs/banner.svg" alt="后台管理系统" width="640">
</p>

<p align="center">
  <a href="https://github.com/lizimu0/admin-system"><img src="https://img.shields.io/github/stars/lizimu0/admin-system?style=flat&label=Stars"></a>
  <img src="https://img.shields.io/badge/Vue-3.5-42b883.svg">
  <img src="https://img.shields.io/badge/Element%20Plus-2.8-409eff.svg">
  <img src="https://img.shields.io/badge/Vite-5.x-646cff.svg">
  <img src="https://img.shields.io/badge/FastAPI-0.1xx-009688.svg">
  <img src="https://img.shields.io/badge/Python-3.12-3776ab.svg">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg"></a>
</p>

# 后台管理系统

基于 **Vue 3 + Element Plus + Pinia + ECharts**(前端)与 **FastAPI + SQLAlchemy + SQLite + JWT**(后端)的全栈后台管理系统,开箱即用。

> 📄 **生产部署请参阅 [部署指南](docs/部署指南.md)**,含 Nginx 反向代理、systemd 守护、HTTPS 等完整步骤。

## 功能

- **登录认证**: JWT Token,登录态持久化
- **安全增强**: 登录图形验证码、连续 5 次失败锁定 15 分钟、登录日志
- **操作日志审计**: 记录所有增删改操作(操作人/接口/参数/IP),敏感字段自动脱敏
- **个人中心**: 修改基本资料、修改密码
- **数据导出**: 用户 / 商品列表一键导出 Excel(支持按当前筛选条件)
- **数据看板**: 统计卡片 + 近 7 日新增用户折线图 + 商品分类饼图
- **用户管理**: 分页 / 搜索 / 新增 / 编辑 / 删除 / 启用禁用
- **角色管理**: 角色 CRUD + 权限树配置
- **权限控制**: 基于角色的菜单过滤 + 按钮级权限指令 `v-permission` + 后端二次校验
- **前端体验**: 403 / 404 错误页、面包屑、标签页导航
- **配置化**: 后端配置走 `.env` 环境变量,前端 API 地址可配
- **商品管理**: 通用 CRUD 示例模块(可作为新业务模块模板)

## 演示账号

| 账号 | 角色 | 权限 |
|------|------|------|
| `admin` | 超级管理员 | 全部权限 |
| `test` | 普通用户 | 仅查看,无增删改 |

初始密码不再固定:执行 `python -m app.seed` 时优先读取环境变量 `ADMIN_INITIAL_PASSWORD` / `TEST_INITIAL_PASSWORD`(可在 `backend/.env` 中设置),未设置则**随机生成并打印在脚本输出中**,避免仓库文档中的固定密码成为生产环境默认凭据。

## 目录结构

```
├── backend/               # FastAPI 后端
│   └── app/
│       ├── main.py        # 应用入口
│       ├── models.py      # 数据模型(User / Role / Product)
│       ├── schemas.py     # 请求/响应模型
│       ├── auth.py        # JWT 认证与权限校验
│       ├── seed.py        # 演示数据初始化
│       └── routers/       # 各业务接口
└── frontend/              # Vue 3 前端
    └── src/
        ├── router/        # 路由 + 登录守卫
        ├── store/         # Pinia 用户状态
        ├── api/           # Axios 封装与接口
        ├── layout/        # 主布局(侧边栏 + 顶栏)
        ├── directives/    # v-permission 权限指令
        └── views/         # 页面
```

## 启动方式

### 1. 启动后端(端口 8000)

```bash
cd E:\后台管理系统\backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env     # 首次:生成配置文件(可修改密钥等)
python -m app.seed         # 初始化演示数据(首次)
uvicorn app.main:app --port 8000 --reload
```

- 接口文档(Swagger): http://localhost:8000/docs
- 配置项见 `backend\.env`:`SECRET_KEY`(生产必改)、`LOGIN_MAX_ATTEMPTS`、`LOGIN_LOCK_MINUTES`、`CAPTCHA_TTL_MINUTES`、`DATABASE_URL`、`CORS_ORIGINS`
- 登录需先获取验证码(`GET /api/auth/captcha`),登录接口带 `captcha_id` / `captcha_code`

### 2. 启动前端(端口 5173)

```bash
cd E:\后台管理系统\frontend
npm install
npm run dev
```

浏览器打开 **http://localhost:5173** 即可访问。

> 前端开发服务器已配置 `/api` 代理到 `http://127.0.0.1:8000`,开发时无跨域问题。

## 权限码说明

角色权限以权限码形式存储在 `roles.permissions` 字段(JSON 数组),超级管理员为 `["*"]`:

| 权限码 | 含义 |
|--------|------|
| `dashboard:view` | 查看看板 |
| `user:view / add / edit / delete` | 用户管理增删改查 |
| `role:view / add / edit / delete` | 角色管理增删改查 |
| `product:view / add / edit / delete` | 商品管理增删改查 |
| `log:view` | 查看操作日志 / 登录日志 |

新增业务模块时,在角色管理页的权限树中补充对应权限码,并在后端路由的写接口上加 `require_permission("xxx:add")` 即可。

## 许可证

[MIT License](LICENSE) © 2026 [lizimu0](https://github.com/lizimu0)
