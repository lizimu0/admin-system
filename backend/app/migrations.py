"""轻量数据库迁移:建新表 + 为已存在的表补齐缺失列。

SQLite 无内置迁移,这里用 inspector 检查表结构,
对缺失列执行 ALTER TABLE ADD COLUMN,保留已有数据。
生产环境请替换为 Alembic。
"""
import logging

from sqlalchemy import inspect, text

from .database import Base, engine

logger = logging.getLogger(__name__)


def _sqlite_type(mapped_type):
    """把 SQLAlchemy 列类型映射为 SQLite 可用的类型字符串。"""
    t = str(mapped_type).lower()
    if "datetime" in t:
        return "datetime"
    if "json" in t:
        return "text"
    if "float" in t:
        return "float"
    if "bool" in t or "boolean" in t:
        return "integer"
    if "int" in t:
        return "integer"
    return "text"


def run_migrations():
    """启动时调用:建新表,并为已有表补齐缺失列。"""
    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)
    with engine.begin() as conn:
        for table, table_obj in Base.metadata.tables.items():
            existing_cols = {c["name"] for c in inspector.get_columns(table)}
            for col in table_obj.columns:
                if col.name in existing_cols:
                    continue
                # 默认值只在 SQLite 直写常量时生效;datetime/json 无法简单表达,忽略 default
                default = ""
                if col.default is not None and col.default.is_scalar:
                    dv = col.default.arg
                    if isinstance(dv, (int, float)):
                        default = f" DEFAULT {dv}"
                sql_type = _sqlite_type(col.type)
                stmt = f"ALTER TABLE {table} ADD COLUMN {col.name} {sql_type}{default}"
                logger.info("迁移: %s", stmt)
                conn.execute(text(stmt))

    logger.info("数据库迁移完成")
