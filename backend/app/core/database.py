"""
数据库连接管理
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from typing import Generator
import redis.asyncio as redis
import loguru

from app.core.config import settings

# 判断数据库类型
db_url = settings.DATABASE_URL_ if hasattr(settings, 'DATABASE_URL_') and settings.DATABASE_URL_ else settings.database_url

# SQLite特殊配置
if db_url and db_url.startswith('sqlite'):
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False},
        echo=settings.DEBUG,
    )
else:
    # MySQL/PostgreSQL配置
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_recycle=3600,
        pool_size=10,
        max_overflow=20,
        echo=settings.DEBUG,
    )

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Redis连接池
_redis_pool = None


async def get_redis() -> redis.Redis:
    """获取Redis连接"""
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = redis.ConnectionPool(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB,
            decode_responses=True,
            max_connections=50,
        )
    return redis.Redis(connection_pool=_redis_pool)


async def init_db():
    """初始化数据库表"""
    from app.models import user, mbti, chat, knowledge

    Base.metadata.create_all(bind=engine)


async def close_db():
    """关闭数据库连接"""
    engine.dispose()
    if _redis_pool:
        await _redis_pool.disconnect()