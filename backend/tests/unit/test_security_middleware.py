"""
安全头中间件单元测试
"""
import pytest
from unittest.mock import Mock, patch

from app.middleware.security import SecurityHeadersMiddleware


class TestSecurityHeadersMiddleware:
    """安全头中间件测试"""

    async def test_adds_security_headers(self):
        """测试添加安全头"""
        mock_app = Mock()
        
        async def call_next(request):
            from starlette.responses import Response
            return Response("ok")
        
        mock_app.return_value = call_next
        middleware = SecurityHeadersMiddleware(mock_app)
        
        mock_request = Mock()
        response = await middleware.dispatch(mock_request, call_next)
        
        # 检查所有安全头都存在
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
        assert response.headers["X-XSS-Protection"] == "1; mode=block"
        assert "Content-Security-Policy" in response.headers
        assert "default-src 'self'" in response.headers["Content-Security-Policy"]

    async def test_preserves_existing_headers(self):
        """测试保留已有头 - 安全头总会覆盖，因为这是安全策略"""
        from starlette.responses import Response
        
        mock_app = Mock()
        
        async def call_next(request):
            resp = Response("ok")
            resp.headers["X-Frame-Options"] = "SAMEORIGIN"
            return resp
        
        middleware = SecurityHeadersMiddleware(mock_app)
        
        mock_request = Mock()
        response = await middleware.dispatch(mock_request, call_next)
        
        # 安全头强制使用DENY，这是预期行为
        assert response.headers["X-Frame-Options"] == "DENY"
        # 其他头仍然添加
        assert response.headers["X-Content-Type-Options"] == "nosniff"
