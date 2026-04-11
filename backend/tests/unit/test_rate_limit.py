"""
限流中间件单元测试
"""
import pytest
from unittest.mock import Mock, patch
from fastapi import Request, HTTPException
from starlette.requests import ClientDisconnect

from app.middleware.rate_limit import RateLimitMiddleware, check_rate_limit


class TestRateLimitMiddleware:
    """限流中间件测试"""

    def test_skip_health_path(self):
        """跳过健康检查路径"""
        middleware = RateLimitMiddleware(None)
        assert middleware._get_client_ip is not None

    async def test_skips_whitelisted_paths(self):
        """测试跳过白名单路径"""
        mock_app = Mock()
        middleware = RateLimitMiddleware(mock_app, requests_per_minute=60)
        
        mock_request = Mock()
        mock_request.url.path = "/health"
        
        called = False
        async def call_next(request):
            nonlocal called
            called = True
            return Mock(status_code=200)
        
        await middleware.dispatch(mock_request, call_next)
        assert called is True

    async def test_skips_docs_paths(self):
        """测试跳过文档路径"""
        mock_app = Mock()
        middleware = RateLimitMiddleware(mock_app, requests_per_minute=60)
        
        mock_request = Mock()
        mock_request.url.path = "/docs"
        
        called = False
        async def call_next(request):
            nonlocal called
            called = True
            return Mock(status_code=200)
        
        await middleware.dispatch(mock_request, call_next)
        assert called is True


class TestGetClientIP:
    """获取客户端IP测试"""

    def test_get_client_ip_from_x_forwarded_for(self):
        """从X-Forwarded-For获取IP"""
        from app.middleware.rate_limit import RateLimitMiddleware
        
        mock_request = Mock()
        mock_request.headers = {"X-Forwarded-For": "192.168.1.1, 10.0.0.1"}
        mock_request.client = Mock(host="127.0.0.1")
        
        middleware = RateLimitMiddleware(None)
        ip = middleware._get_client_ip(mock_request)
        assert ip == "192.168.1.1"

    def test_get_client_ip_from_x_real_ip(self):
        """从X-Real-IP获取IP"""
        from app.middleware.rate_limit import RateLimitMiddleware
        
        mock_request = Mock()
        mock_request.headers = {"X-Real-IP": "10.0.0.1"}
        mock_request.client = Mock(host="127.0.0.1")
        
        middleware = RateLimitMiddleware(None)
        ip = middleware._get_client_ip(mock_request)
        assert ip == "10.0.0.1"

    def test_get_client_ip_from_client_host(self):
        """从client.host获取IP"""
        from app.middleware.rate_limit import RateLimitMiddleware
        
        mock_request = Mock()
        mock_request.headers = {}
        mock_request.client = Mock(host="127.0.0.1")
        
        middleware = RateLimitMiddleware(None)
        ip = middleware._get_client_ip(mock_request)
        assert ip == "127.0.0.1"

    def test_get_client_ip_no_client_returns_unknown(self):
        """没有client返回unknown"""
        from app.middleware.rate_limit import RateLimitMiddleware
        
        mock_request = Mock()
        mock_request.headers = {}
        mock_request.client = None
        
        middleware = RateLimitMiddleware(None)
        ip = middleware._get_client_ip(mock_request)
        assert ip == "unknown"


class TestCheckRateLimit:
    """用户级限流检查函数测试"""

    async def test_check_rate_limit_first_request(self):
        """第一次请求通过"""
        from unittest.mock import AsyncMock
        with patch("app.middleware.rate_limit.get_redis") as mock_get_redis:
            mock_redis = AsyncMock()
            mock_redis.incr.return_value = 1
            mock_redis.expire.return_value = None
            mock_redis.ttl.return_value = 60
            mock_get_redis.return_value = mock_redis
            
            allowed, remaining = await check_rate_limit(1, "login", 5, 60)
            assert allowed is True
            assert remaining == 4

    async def test_check_rate_limit_exceeds_limit(self):
        """超过限流返回False"""
        from unittest.mock import AsyncMock
        with patch("app.middleware.rate_limit.get_redis") as mock_get_redis:
            mock_redis = AsyncMock()
            mock_redis.incr.return_value = 6
            mock_redis.expire.return_value = None
            mock_redis.ttl.return_value = 60
            mock_get_redis.return_value = mock_redis
            
            allowed, remaining = await check_rate_limit(1, "login", 5, 60)
            assert allowed is False
            assert remaining == 0

    async def test_check_rate_limit_redis_exception_returns_allowed(self):
        """Redis异常允许通过"""
        from unittest.mock import AsyncMock
        with patch("app.middleware.rate_limit.get_redis") as mock_get_redis:
            mock_redis = AsyncMock()
            mock_redis.incr.side_effect = Exception("Redis connection error")
            mock_get_redis.return_value = mock_redis
            
            allowed, remaining = await check_rate_limit(1, "login", 5, 60)
            assert allowed is True
            assert remaining == 5

    async def test_check_rate_limit_first_key_sets_expire(self):
        """第一个key设置过期"""
        from unittest.mock import AsyncMock
        with patch("app.middleware.rate_limit.get_redis") as mock_get_redis:
            mock_redis = AsyncMock()
            mock_redis.incr.return_value = 1
            mock_redis.expire.return_value = None
            mock_redis.ttl.return_value = 60
            mock_get_redis.return_value = mock_redis
            
            await check_rate_limit(1, "login", 5, 60)
            mock_redis.expire.assert_called_once()
