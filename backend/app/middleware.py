"""操作日志中间件:记录 /api 下所有写操作(非 GET/OPTIONS/HEAD)。

- 读取请求体(Starlette 会缓存 body,不影响下游解析)
- 对 password / captcha_code / token 等敏感字段脱敏
- 记录失败不影响主请求(异常吞掉并打日志)
"""
import json
import logging

from starlette.requests import Request

from . import models
from .auth import decode_token
from .database import SessionLocal

logger = logging.getLogger(__name__)

# 敏感字段:记录日志时替换为 ***
SENSITIVE_FIELDS = {
    "password",
    "old_password",
    "new_password",
    "captcha_code",
    "token",
    "authorization",
}
# 无需记录日志的路径(避免噪声)
SKIP_PATHS = {"/api/auth/login", "/api/auth/captcha"}
# 仅记录写操作
WRITE_METHODS = {"POST", "PUT", "DELETE", "PATCH"}
MAX_PARAMS_LEN = 2000


def _redact(data):
    if isinstance(data, dict):
        for k, v in list(data.items()):
            if k in SENSITIVE_FIELDS:
                data[k] = "***"
            else:
                _redact(v)
    elif isinstance(data, list):
        for item in data:
            _redact(item)


def _extract_user(request: Request):
    auth = request.headers.get("authorization", "")
    if auth.lower().startswith("bearer "):
        user_id = decode_token(auth[7:])
        if user_id is None:
            return None
        db = SessionLocal()
        try:
            user = db.query(models.User).filter(models.User.id == user_id).first()
            return (user.id, user.username) if user else None
        finally:
            db.close()
    return None


async def operation_log_middleware(request: Request, call_next):
    method = request.method
    path = request.url.path
    should_log = (
        path.startswith("/api")
        and method in WRITE_METHODS
        and path not in SKIP_PATHS
    )

    user = _extract_user(request) if should_log else None
    params = None
    ip = request.client.host if request.client else ""

    if should_log:
        try:
            raw = await request.body()
            if raw:
                parsed = json.loads(raw)
                _redact(parsed)
                params = json.dumps(parsed, ensure_ascii=False)[:MAX_PARAMS_LEN]
        except Exception:
            # body 无法解析(如 multipart),只记录基本信息
            params = None

    response = await call_next(request)

    if should_log:
        try:
            db = SessionLocal()
            try:
                db.add(
                    models.OperationLog(
                        user_id=user[0] if user else None,
                        username=user[1] if user else None,
                        method=method,
                        path=path,
                        status_code=response.status_code,
                        params=params,
                        ip=ip,
                    )
                )
                db.commit()
            finally:
                db.close()
        except Exception:
            logger.exception("写入操作日志失败")

    return response
