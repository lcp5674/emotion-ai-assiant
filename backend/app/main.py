"""
心灵伴侣AI - 主应用入口
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import loguru

from app.core.config import settings
from app.core.database import init_db, close_db, SessionLocal
from app.api.v1 import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    loguru.logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    # 初始化数据库
    try:
        await init_db()
        loguru.logger.info("Database initialized")

        # 初始化AI助手数据
        from app.services.mbti_service import seed_assistants
        db = SessionLocal()
        try:
            seed_assistants(db)
        finally:
            db.close()
    except Exception as e:
        loguru.logger.warning(f"Database initialization skipped: {e}")

    yield

    # 关闭时
    loguru.logger.info("Shutting down...")
    await close_db()


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI情感助手 - 心灵伴侣",
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

# 限流中间件
try:
    from app.middleware.rate_limit import RateLimitMiddleware
    app.add_middleware(RateLimitMiddleware, requests_per_minute=120)
except ImportError:
    loguru.logger.warning("限流中间件加载失败")

# 安全头中间件
try:
    from app.middleware.security import SecurityHeadersMiddleware
    app.add_middleware(SecurityHeadersMiddleware)
except ImportError:
    loguru.logger.warning("安全头中间件加载失败")

# 请求大小限制中间件
try:
    from app.middleware.security import RequestSizeLimitMiddleware
    app.add_middleware(RequestSizeLimitMiddleware, max_size=10 * 1024 * 1024)  # 10MB
except ImportError:
    loguru.logger.warning("请求大小限制中间件加载失败")

# 性能监控中间件
try:
    from app.middleware.performance import performance_middleware
    app.middleware("http")(performance_middleware)
except ImportError:
    loguru.logger.warning("性能监控中间件加载失败")

# 注册路由
app.include_router(api_router, prefix="/api/v1")


# 健康检查
@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )