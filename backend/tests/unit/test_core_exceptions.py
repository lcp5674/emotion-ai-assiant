"""
core/exceptions.py 单元测试
"""
import pytest
from app.core.exceptions import (
    AppException,
    AuthenticationException,
    AuthorizationException,
    NotFoundException,
    ValidationException,
    BusinessLogicException,
)


class TestAppException:
    """基础应用异常测试"""

    def test_app_exception_defaults(self):
        """测试默认参数"""
        exc = AppException()
        assert exc.status_code == 500
        assert exc.message == "Internal Server Error"

    def test_app_exception_custom(self):
        """测试自定义参数"""
        exc = AppException(message="自定义错误", status_code=400)
        assert exc.status_code == 400
        assert exc.message == "自定义错误"
        assert "自定义错误" in str(exc)


class TestSpecificExceptions:
    """具体异常类型测试"""

    def test_authentication_exception(self):
        """认证异常默认状态码"""
        exc = AuthenticationException()
        assert exc.status_code == 401

        exc_custom = AuthenticationException("自定义认证失败")
        assert exc_custom.message == "自定义认证失败"

    def test_business_logic_exception(self):
        """业务异常"""
        exc = BusinessLogicException()
        assert exc.status_code == 400

        exc = BusinessLogicException("业务逻辑错误")
        assert exc.message == "业务逻辑错误"

    def test_not_found_exception(self):
        """找不到资源异常"""
        exc = NotFoundException()
        assert exc.status_code == 404

        exc = NotFoundException("用户不存在")
        assert exc.message == "用户不存在"

    def test_authorization_exception(self):
        """权限不足异常"""
        exc = AuthorizationException()
        assert exc.status_code == 403

    def test_validation_exception(self):
        """验证失败异常"""
        exc = ValidationException()
        assert exc.status_code == 422

        exc = ValidationException("参数格式错误")
        assert exc.message == "参数格式错误"
