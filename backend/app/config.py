import secrets
import sys

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置,可通过环境变量或 backend/.env 覆盖。"""

    # 安全(SECRET_KEY 必须通过环境变量或 .env 显式设置;未设置时每次启动生成临时随机密钥,
    # 所有登录会话将随之失效,禁止在任何分支回退到硬编码默认值)
    SECRET_KEY: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # 登录安全
    LOGIN_MAX_ATTEMPTS: int = 5
    LOGIN_LOCK_MINUTES: int = 15
    CAPTCHA_TTL_MINUTES: int = 5

    # 数据库
    DATABASE_URL: str = "sqlite:///./admin.db"

    # Swagger 文档(生产环境建议 false)
    DOCS_ENABLED: bool = True

    # CORS 允许来源(逗号分隔)
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    def model_post_init(self, __context) -> None:
        if not self.SECRET_KEY:
            self.SECRET_KEY = secrets.token_urlsafe(48)
            print(
                "⚠️  未配置 SECRET_KEY,已自动生成临时随机密钥(重启后所有登录会话失效)。\n"
                "    生产环境必须在 backend/.env 中设置固定值,生成命令:\n"
                '    python -c "import secrets; print(secrets.token_urlsafe(48))"',
                file=sys.stderr,
            )

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()
