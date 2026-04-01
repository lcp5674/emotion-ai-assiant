"""
安全中间件 - CSP、安全头等
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from typing import Callable
import loguru

from app.core.config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """安全响应头中间件"""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # 添加安全头
        # X-Content-Type-Options - 防止MIME类型嗅探
        response.headers["X-Content-Type-Options"] = "nosniff"

        # X-Frame-Options - 防止点击劫持
        response.headers["X-Frame-Options"] = "DENY"

        # X-XSS-Protection - XSS保护(现代浏览器主要用CSP)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer-Policy - 控制Referer头
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Content-Security-Policy - 内容安全策略
        if not settings.DEBUG:
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self'; "
                "connect-src 'self' wss: ws:; "
                "frame-ancestors 'none';"
            )
        else:
            # 开发环境CSP更宽松
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https: http:; "
                "font-src 'self'; "
                "connect-src 'self' ws: wss: http:; "
            )

        # Strict-Transport-Security - 强制HTTPS(生产环境)
        if not settings.DEBUG:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Permissions-Policy - 控制浏览器API访问
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), payment=()"
        )

        return response


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """请求大小限制中间件"""

    def __init__(self, app, max_size: int = 10 * 1024 * 1024):  # 默认10MB
        super().__init__(app)
        self.max_size = max_size

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_size:
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={"detail": "请求内容过大"},
            )

        # 检查流式请求
        if (
            request.method in ["POST", "PUT", "PATCH"]
            and not content_length
        ):
            # 读取并检查大小
            try:
                body = await request.body()
                if len(body) > self.max_size:
                    return JSONResponse(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        content={"detail": "请求内容过大"},
                    )
            except Exception as e:
                loguru.warning(f"读取请求体失败: {e}")

        return await call_next(request)
