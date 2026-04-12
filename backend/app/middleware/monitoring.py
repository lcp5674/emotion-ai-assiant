"""
监控中间件
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
from app.core.database import get_db
from app.services.cache_service import get_cache_service
import loguru

from app.main import REQUEST_COUNT, REQUEST_LATENCY, ACTIVE_USERS, ERROR_COUNT


class MonitoringMiddleware(BaseHTTPMiddleware):
    """监控中间件"""

    async def dispatch(self, request: Request, call_next) -> Response:
        """处理请求"""
        # 增加活跃用户计数
        ACTIVE_USERS.inc()

        # 记录请求开始时间
        start_time = time.time()

        try:
            # 处理请求
            response = await call_next(request)

            # 计算请求延迟
            latency = time.time() - start_time

            # 记录请求指标
            endpoint = request.url.path
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=endpoint,
                status=response.status_code
            ).inc()
            REQUEST_LATENCY.labels(
                method=request.method,
                endpoint=endpoint
            ).observe(latency)

            return response

        except Exception as e:
            # 记录错误
            ERROR_COUNT.labels(error_type=type(e).__name__).inc()
            loguru.logger.error(f"Request error: {e}")
            raise

        finally:
            # 减少活跃用户计数
            ACTIVE_USERS.dec()


async def check_health() -> dict:
    """健康检查"""
    health_status = {
        "status": "ok",
        "components": {
            "database": "ok",
            "cache": "ok"
        }
    }

    # 检查数据库连接
    try:
        db = next(get_db())
        db.execute("SELECT 1")
        db.close()
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["components"]["database"] = f"error: {str(e)}"

    # 检查缓存连接
    try:
        cache_service = get_cache_service()
        await cache_service.ping()
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["components"]["cache"] = f"error: {str(e)}"

    return health_status
