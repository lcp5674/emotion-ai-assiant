"""
监控中间件 - 集成监控告警服务
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import asyncio
from app.core.database import get_db
import loguru

from app.main import REQUEST_COUNT, REQUEST_LATENCY, ACTIVE_USERS, ERROR_COUNT

# 延迟导入避免循环依赖
_monitoring_service = None


def _get_monitoring_service():
    global _monitoring_service
    if _monitoring_service is None:
        from app.services.monitoring_service import get_monitoring_service
        _monitoring_service = get_monitoring_service()
    return _monitoring_service


class MonitoringMiddleware(BaseHTTPMiddleware):
    """监控中间件"""

    async def dispatch(self, request: Request, call_next) -> Response:
        """处理请求"""
        # 增加活跃用户计数
        ACTIVE_USERS.inc()

        # 记录请求开始时间
        start_time = time.time()

        # 获取用户ID（如果已认证）
        user_id = None
        try:
            if hasattr(request.state, "user"):
                user_id = request.state.user.id
        except Exception:
            pass

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

            # 异步记录到监控系统
            asyncio.create_task(
                _get_monitoring_service().record_request_metric(
                    endpoint=endpoint,
                    method=request.method,
                    status_code=response.status_code,
                    latency_ms=latency * 1000,
                    user_id=user_id
                )
            )

            return response

        except Exception as e:
            # 记录错误
            ERROR_COUNT.labels(error_type=type(e).__name__).inc()
            loguru.logger.error(f"Request error: {e}")

            # 发送告警
            try:
                asyncio.create_task(
                    _get_monitoring_service().alert_service_down(
                        service_name=f"{request.method} {request.url.path}",
                        error=str(e)
                    )
                )
            except Exception:
                pass

            raise

        finally:
            # 减少活跃用户计数
            ACTIVE_USERS.dec()


async def check_health() -> dict:
    """健康检查"""
    monitoring = _get_monitoring_service()
    return await monitoring.check_system_health()
