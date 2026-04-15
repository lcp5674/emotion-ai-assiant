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

# 尝试导入监控模块（可选）
try:
    from prometheus_client import Counter, Gauge, Histogram
    from fastapi_metrics import PrometheusMiddleware, metrics
    METRICS_AVAILABLE = True
    # 定义监控指标
    REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP Requests', ['method', 'endpoint', 'status'])
    REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP Request Latency', ['method', 'endpoint'])
    ACTIVE_USERS = Gauge('active_users', 'Number of active users')
    ERROR_COUNT = Counter('error_count', 'Total Error Count', ['error_type'])
except ImportError:
    METRICS_AVAILABLE = False
    loguru.logger.warning("监控模块不可用，跳过监控功能")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    loguru.logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    # 初始化监控服务
    try:
        from app.services.monitoring_service import get_monitoring_service
        monitoring = get_monitoring_service()
        # 注册Webhook告警处理器（如果配置了）
        if hasattr(settings, 'ALERT_WEBHOOK_URL') and settings.ALERT_WEBHOOK_URL:
            from app.services.monitoring_service import WebhookAlertHandler
            monitoring.register_alert_handler(WebhookAlertHandler(settings.ALERT_WEBHOOK_URL))
            loguru.logger.info("监控告警Webhook已配置")
        loguru.logger.info("监控服务已初始化")
    except Exception as e:
        loguru.logger.warning(f"监控服务初始化失败: {e}")

    # 初始化数据库
    try:
        await init_db()
        loguru.logger.info("Database initialized")

        # 初始化AI助手数据
        from app.services.mbti_service import seed_assistants
        db = SessionLocal()
        try:
            await seed_assistants(db)
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

# 安全头中间件 - 已启用
try:
    from app.middleware.security import SecurityHeadersMiddleware
    app.add_middleware(SecurityHeadersMiddleware)
    loguru.logger.info("安全头中间件已启用")
except ImportError:
    loguru.logger.warning("安全头中间件加载失败")

# 请求大小限制中间件
try:
    from app.middleware.security import RequestSizeLimitMiddleware
    app.add_middleware(RequestSizeLimitMiddleware, max_size=10 * 1024 * 1024)  # 10MB
except ImportError:
    loguru.logger.warning("请求大小限制中间件加载失败")

# 监控中间件
try:
    from app.middleware.monitoring import MonitoringMiddleware
    app.add_middleware(MonitoringMiddleware)
except ImportError:
    loguru.logger.warning("监控中间件加载失败")

# Prometheus监控中间件（如果可用）
if METRICS_AVAILABLE:
    app.add_middleware(PrometheusMiddleware, app_name=settings.APP_NAME)

# 注册路由
app.include_router(api_router, prefix="/api/v1")


# 健康检查
@app.get("/health")
async def health_check():
    """健康检查"""
    try:
        from app.middleware.monitoring import check_health
        health_status = await check_health()
        health_status.update({
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
        })
        return health_status
    except Exception as e:
        return {
            "status": "ok",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
        }

# Prometheus指标端点（如果可用）
if METRICS_AVAILABLE:
    app.add_route("/metrics", metrics)


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
    from fastapi.responses import JSONResponse
    from fastapi import Request
    
    # 全局异常处理器
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """全局异常处理"""
        loguru.logger.error(f"未处理的异常: {exc}")
        return JSONResponse(
            status_code=500,
            content={"detail": "服务器内部错误", "message": str(exc)[:200]},
        )
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )