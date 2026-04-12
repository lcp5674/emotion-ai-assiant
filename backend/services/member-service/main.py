"""
会员服务 - 微服务入口
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import loguru

from app.core.config import settings
from app.core.database import init_db, close_db
from app.api.v1 import member_router, payment_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    loguru.logger.info(f"Starting Member Service v{settings.APP_VERSION}")

    # 初始化数据库
    try:
        await init_db()
        loguru.logger.info("Database initialized")
    except Exception as e:
        loguru.logger.warning(f"Database initialization skipped: {e}")

    yield

    # 关闭时
    loguru.logger.info("Shutting down...")
    await close_db()


# 创建FastAPI应用
app = FastAPI(
    title="Member Service",
    version=settings.APP_VERSION,
    description="会员服务 - 心灵伴侣AI",
    lifespan=lifespan,
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(member_router, prefix="/api/v1/member")
app.include_router(payment_router, prefix="/api/v1/payment")


# 健康检查
@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "service": "member-service",
        "version": settings.APP_VERSION,
    }


# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "Member Service",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
