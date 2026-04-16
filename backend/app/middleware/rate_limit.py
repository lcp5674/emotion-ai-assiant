"""
限流中间件 - 基于Redis滑动窗口
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time
import loguru

from app.core.database import get_redis


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute

    async def dispatch(self, request: Request, call_next):
        if request.url.path in ["/health", "/", "/docs", "/openapi.json", "/redoc"]:
            return await call_next(request)

        client_ip = self._get_client_ip(request)
        key = f"ratelimit:{client_ip}:{int(time.time() / 60)}"

        try:
            redis_client = await get_redis()
            current = await redis_client.incr(key.encode("utf-8") if isinstance(key, str) else key)

            if current == 1:
                await redis_client.expire(key.encode("utf-8") if isinstance(key, str) else key, 60)

            ttl = await redis_client.ttl(key.encode("utf-8") if isinstance(key, str) else key)
            remaining = max(0, self.requests_per_minute - current)

            if current > self.requests_per_minute:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": "请求过于频繁，请稍后再试",
                        "retry_after": ttl,
                    },
                    headers={
                        "Retry-After": str(ttl),
                        "X-RateLimit-Limit": str(self.requests_per_minute),
                        "X-RateLimit-Remaining": str(remaining),
                    },
                )

            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            return response

        except Exception as e:
            loguru.logger.warning(f"限流检查失败: {e}")
            return await call_next(request)

    def _get_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        return request.client.host if request.client else "unknown"


async def check_rate_limit(user_id: int, action: str, limit: int, window: int = 60) -> tuple[bool, int]:
    """
    检查用户特定操作的限流
    
    Args:
        user_id: 用户ID
        action: 操作类型
        limit: 限制次数
        window: 时间窗口(秒)
    
    Returns:
        tuple: (是否通过, 剩余次数)
    """
    key = f"ratelimit:user:{user_id}:{action}:{int(time.time() / window)}"
    key_bytes = key.encode("utf-8") if isinstance(key, str) else key

    try:
        redis_client = await get_redis()
        current = await redis_client.incr(key_bytes)

        if current == 1:
            await redis_client.expire(key_bytes, window)

        remaining = max(0, limit - current)
        return current <= limit, remaining

    except Exception as e:
        loguru.logger.warning(f"限流检查失败: {e}")
        return True, limit
