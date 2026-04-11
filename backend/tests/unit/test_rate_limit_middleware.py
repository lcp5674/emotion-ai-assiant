"""
速率限制中间件单元测试
"""
import pytest
from unittest.mock import Mock, patch

from app.middleware.rate_limit import RateLimitMiddleware


class TestRateLimitMiddleware:
    """速率限制中间件测试"""

    async def test_allowed_request(self):
        """测试允许请求通过"""
        mock_app = Mock()
        
        async def call_next(request):
            from starlette.responses import Response
            return Response("ok")
        
        mock_app.return_value = call_next
        
        mock_request = Mock()
        mock_request.client = Mock()
        mock_request.client.host = "127.0.0.1"
        
        mock_redis = Mock()
        mock_redis.get = Mock(return_value="10")
        mock_redis.incr = Mock(return_value=11)
        mock_redis.expire = Mock()

        with patch("app.middleware.rate_limit.get_redis", return_value=mock_redis):
            middleware = RateLimitMiddleware(mock_app)
            with patch("app.middleware.rate_limit.settings") as mock_settings:
                mock_settings.RATE_LIMIT_ENABLED = True
                mock_settings.RATE_LIMIT_REQUESTS = 100
                mock_settings.RATE_LIMIT_WINDOW = 60
                response = await middleware.dispatch(mock_request, call_next)
        
        assert response.status_code == 200
        assert response.text == "ok"

    async def test_blocked_exceed_limit(self):
        """测试超过限制被阻止"""
        mock_app = Mock()
        
        async def call_next(request):
            from starlette.responses import Response
            return Response("ok")
        
        mock_app.return_value = call_next
        
        mock_request = Mock()
        mock_request.client = Mock()
        mock_request.client.host = "127.0.0.1"
        
        mock_redis = Mock()
        mock_redis.get = Mock(return_value="101")

        with patch("app.middleware.rate_limit.get_redis", return_value=mock_redis):
            middleware = RateLimitMiddleware(mock_app)
            with patch("app.middleware.rate_limit.settings") as mock_settings:
                mock_settings.RATE_LIMIT_ENABLED = True
                mock_settings.RATE_LIMIT_REQUESTS = 100
                mock_settings.RATE_LIMIT_WINDOW = 60
                response = await middleware.dispatch(mock_request, call_next)
        
        assert response.status_code == 429
        assert "Too Many Requests" in response.text

    async def test_disabled_passthrough(self):
        """测试禁用限速直接放行"""
        mock_app = Mock()
        
        async def call_next(request):
            from starlette.responses import Response
            return Response("ok")
        
        mock_app.return_value = call_next
        
        mock_request = Mock()
        mock_request.client = Mock()
        mock_request.client.host = "127.0.0.1"
        
        middleware = RateLimitMiddleware(mock_app)
        with patch("app.middleware.rate_limit.settings") as mock_settings:
            mock_settings.RATE_LIMIT_ENABLED = False
            response = await middleware.dispatch(mock_request, call_next)
        
        assert response.status_code == 200
        assert response.text == "ok"

    async def test_first_request(self):
        """测试第一个请求"""
        mock_app = Mock()
        
        async def call_next(request):
            from starlette.responses import Response
            return Response("ok")
        
        mock_app.return_value = call_next
        
        mock_request = Mock()
        mock_request.client = Mock()
        mock_request.client.host = "127.0.0.1"
        
        mock_redis = Mock()
        mock_redis.get = Mock(return_value=None)
        mock_redis.incr = Mock(return_value=1)
        mock_redis.expire = Mock()

        with patch("app.middleware.rate_limit.get_redis", return_value=mock_redis):
            middleware = RateLimitMiddleware(mock_app)
            with patch("app.middleware.rate_limit.settings") as mock_settings:
                mock_settings.RATE_LIMIT_ENABLED = True
                mock_settings.RATE_LIMIT_REQUESTS = 100
                mock_settings.RATE_LIMIT_WINDOW = 60
                response = await middleware.dispatch(mock_request, call_next)
        
        assert response.status_code == 200
        mock_redis.expire.assert_called_once()

    async def test_redis_error_allow(self):
        """测试Redis出错时允许通过(故障开放)"""
        mock_app = Mock()
        
        async def call_next(request):
            from starlette.responses import Response
            return Response("ok")
        
        mock_app.return_value = call_next
        
        mock_request = Mock()
        mock_request.client = Mock()
        mock_request.client.host = "127.0.0.1"
        
        mock_redis = Mock()
        mock_redis.get = Mock(side_effect=Exception("Redis down"))

        with patch("app.middleware.rate_limit.get_redis", return_value=mock_redis):
            middleware = RateLimitMiddleware(mock_app)
            with patch("app.middleware.rate_limit.settings") as mock_settings:
                mock_settings.RATE_LIMIT_ENABLED = True
                mock_settings.RATE_LIMIT_REQUESTS = 100
                mock_settings.RATE_LIMIT_WINDOW = 60
                response = await middleware.dispatch(mock_request, call_next)
        
        # Redis出错时仍然允许请求通过，保证可用性
        assert response.status_code == 200

    async def test_no_client_host(self):
        """测试没有客户端地址"""
        mock_app = Mock()
        
        async def call_next(request):
            from starlette.responses import Response
            return Response("ok")
        
        mock_app.return_value = call_next
        
        mock_request = Mock()
        mock_request.client = None  # 没有client信息
        
        mock_redis = Mock()
        
        with patch("app.middleware.rate_limit.get_redis", return_value=mock_redis):
            middleware = RateLimitMiddleware(mock_app)
            with patch("app.middleware.rate_limit.settings") as mock_settings:
                mock_settings.RATE_LIMIT_ENABLED = True
                mock_settings.RATE_LIMIT_REQUESTS = 100
                mock_settings.RATE_LIMIT_WINDOW = 60
                response = await middleware.dispatch(mock_request, call_next)
        
        # 无法识别客户端直接放行
        assert response.status_code == 200
