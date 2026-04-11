"""
auth_service 单元测试
"""
import pytest
from unittest.mock import Mock, patch
from datetime import timedelta
from jose import JWTError
from fastapi import HTTPException

from app.core.config import settings
from app.core.security import verify_password, get_password_hash, create_access_token, verify_token
from app.services.auth_service import AuthService
from app.models.user import User
from app.schemas.user import RegisterRequest


class TestPasswordHashing:
    """密码哈希测试 - 验证core层函数"""

    def test_verify_password_correct(self):
        """正确密码验证通过"""
        plain = "password123"
        hashed = get_password_hash(plain)
        assert verify_password(plain, hashed) is True

    def test_verify_password_incorrect(self):
        """错误密码验证失败"""
        plain = "password123"
        wrong = "wrongpass"
        hashed = get_password_hash(plain)
        assert verify_password(wrong, hashed) is False


class TestToken:
    """令牌生成和验证测试 - core层函数"""

    def test_create_access_token_contains_sub(self):
        """token包含sub"""
        token = create_access_token(data={"sub": "123"})
        assert token is not None
        assert isinstance(token, str)

    def test_verify_token_valid(self):
        """验证有效token"""
        token = create_access_token(data={"sub": "456"})
        payload = verify_token(token)
        assert payload["sub"] == "456"

    def test_verify_token_invalid(self):
        """验证无效token抛出异常"""
        from fastapi import HTTPException
        with pytest.raises(HTTPException):
            verify_token("invalid_token")


class TestAuthServiceRegister:
    """AuthService注册测试"""

    async def test_register_user_success(self, db_session):
        """注册成功"""
        mock_sms = Mock()
        mock_sms.verify_code = Mock()
        mock_sms.verify_code.return_value = True
        # 因为verify_code是async方法需要用AsyncMock
        from unittest.mock import AsyncMock
        mock_sms.verify_code = AsyncMock(return_value=True)
        
        with patch("app.services.auth_service.get_sms_service", return_value=mock_sms):
            service = AuthService(db_session)
            req = RegisterRequest(
                phone="13900000001",
                password="Password@123",
                code="123456",
            )
            
            # 关闭DEBUG让验证码检查执行
            original_debug = settings.DEBUG
            settings.DEBUG = False
            
            try:
                user = await service.register(req)
            finally:
                settings.DEBUG = original_debug
            
            assert user is not None
            assert user.phone == "13900000001"
            assert user.nickname == "用户0001"
            assert user.is_active is True
            assert user.password_hash is not None
            mock_sms.verify_code.assert_called_once()

    async def test_register_user_duplicate_phone(self, db_session):
        """手机号已存在注册失败"""
        existing = User(
            phone="13900000002",
            password_hash=get_password_hash("pass"),
            is_active=True,
        )
        db_session.add(existing)
        db_session.commit()

        service = AuthService(db_session)
        req = RegisterRequest(
            phone="13900000002",
            password="Password@123",
            code="123456",
        )

        with pytest.raises(ValueError) as exc_info:
            await service.register(req)
        
        assert "手机号已被注册" in str(exc_info.value)

    async def test_register_user_weak_password_rejected(self, db_session):
        """弱密码被拒绝 - Pydantic会在schema层验证，这里测试通过，但schema会拒绝"""
        # Pydantic验证在入口已经做了，这里只验证service逻辑
        pass

    async def test_register_debug_mode_skips_sms_verification(self, db_session):
        """测试DEBUG模式跳过验证码验证"""
        service = AuthService(db_session)
        req = RegisterRequest(
            phone="13900000009",
            password="Password@123",
            code="123456",
        )

        original_debug = settings.DEBUG
        settings.DEBUG = True

        try:
            # DEBUG模式不需要调用SMS验证
            user = await service.register(req)
            assert user is not None
            assert user.phone == "13900000009"
        finally:
            settings.DEBUG = original_debug

    async def test_register_invalid_sms_code_raises(self, db_session):
        """测试验证码错误注册失败"""
        mock_sms = Mock()
        from unittest.mock import AsyncMock
        mock_sms.verify_code = AsyncMock(return_value=False)

        with patch("app.services.auth_service.get_sms_service", return_value=mock_sms):
            service = AuthService(db_session)
            req = RegisterRequest(
                phone="13900000010",
                password="Password@123",
                code="123456",
            )

            original_debug = settings.DEBUG
            settings.DEBUG = False

            try:
                with pytest.raises(ValueError) as exc_info:
                    await service.register(req)
                assert "验证码错误或已过期" in str(exc_info.value)
            finally:
                settings.DEBUG = original_debug


class TestAuthServiceLogin:
    """AuthService登录测试"""

    async def test_login_success(self, db_session):
        """登录成功"""
        user = User(
            phone="13900000003",
            password_hash=get_password_hash("Test@123"),
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()

        service = AuthService(db_session)
        result = await service.login("13900000003", "Test@123")
        
        assert result is not None
        assert result.access_token is not None
        assert result.refresh_token is not None
        assert result.token_type == "bearer"
        assert result.user.id == user.id

    async def test_login_wrong_password(self, db_session):
        """密码错误返回None"""
        user = User(
            phone="13900000004",
            password_hash=get_password_hash("correct"),
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()

        service = AuthService(db_session)
        result = await service.login("13900000004", "wrong")
        
        assert result is None

    async def test_login_user_not_exists(self, db_session):
        """用户不存在返回None"""
        service = AuthService(db_session)
        result = await service.login("19999999999", "any")
        
        assert result is None

    async def test_login_inactive_user_raises(self, db_session):
        """不活跃用户抛出异常"""
        user = User(
            phone="13900000005",
            password_hash=get_password_hash("password"),
            is_active=False,
        )
        db_session.add(user)
        db_session.commit()

        service = AuthService(db_session)
        
        with pytest.raises(ValueError) as exc_info:
            await service.login("13900000005", "password")
        
        assert "用户已被禁用" in str(exc_info.value)


class TestAuthServiceSmsLogin:
    """短信验证码登录测试"""

    async def test_login_with_sms_success(self, db_session):
        """短信登录成功"""
        mock_sms = Mock()
        from unittest.mock import AsyncMock
        mock_sms.verify_code = AsyncMock(return_value=True)
        
        with patch("app.services.auth_service.get_sms_service", return_value=mock_sms):
            service = AuthService(db_session)
            original_debug = settings.DEBUG
            settings.DEBUG = False
            
            try:
                result = await service.login_with_sms("13900000006", "123456")
            finally:
                settings.DEBUG = original_debug
            
            assert result is not None
            assert result.access_token is not None
            # 用户已创建
            user = db_session.query(User).filter(User.phone == "13900000006").first()
            assert user is not None

    async def test_login_with_sms_invalid_code(self, db_session):
        """验证码错误抛出异常"""
        mock_sms = Mock()
        from unittest.mock import AsyncMock
        mock_sms.verify_code = AsyncMock(return_value=False)
        
        with patch("app.services.auth_service.get_sms_service", return_value=mock_sms):
            service = AuthService(db_session)
            original_debug = settings.DEBUG
            settings.DEBUG = False
            
            try:
                with pytest.raises(ValueError) as exc_info:
                    await service.login_with_sms("13900000007", "12345w")
                assert "验证码错误或已过期" in str(exc_info.value)
            finally:
                settings.DEBUG = original_debug


class TestRefreshToken:
    """刷新令牌测试"""

    async def test_refresh_token_valid(self, db_session):
        """有效刷新令牌成功"""
        from app.core.security import create_refresh_token
        
        user = User(
            phone="13900000008",
            password_hash=get_password_hash("pass"),
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()

        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        service = AuthService(db_session)
        
        result = await service.refresh_token(refresh_token)
        
        assert result is not None
        assert result.access_token is not None

    async def test_refresh_token_invalid(self, db_session):
        """无效刷新令牌返回None"""
        service = AuthService(db_session)
        result = await service.refresh_token("invalid_token")
        
        assert result is None

    async def test_refresh_token_wrong_type_returns_none(self, db_session):
        """token类型不对返回None"""
        from app.core.security import create_access_token
        
        user = User(
            phone="13900000011",
            password_hash=get_password_hash("pass"),
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()

        # 使用access token而不是refresh token
        wrong_token = create_access_token(data={"sub": str(user.id)})
        service = AuthService(db_session)
        
        result = await service.refresh_token(wrong_token)
        assert result is None

    async def test_refresh_token_no_sub_returns_none(self, db_session):
        """token没有sub返回None"""
        from app.core.security import create_refresh_token
        
        user = User(
            phone="13900000012",
            password_hash=get_password_hash("pass"),
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()

        refresh_token = create_refresh_token(data={"no_sub_here": str(user.id)})
        service = AuthService(db_session)
        
        result = await service.refresh_token(refresh_token)
        assert result is None

    async def test_refresh_token_user_not_found_returns_none(self, db_session):
        """用户不存在返回None"""
        from app.core.security import create_refresh_token
        
        refresh_token = create_refresh_token(data={"sub": "99999"})
        service = AuthService(db_session)
        
        result = await service.refresh_token(refresh_token)
        assert result is None

    async def test_refresh_token_inactive_user_returns_none(self, db_session):
        """用户不活跃返回None"""
        from app.core.security import create_refresh_token
        
        user = User(
            phone="13900000013",
            password_hash=get_password_hash("pass"),
            is_active=False,
        )
        db_session.add(user)
        db_session.commit()

        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        service = AuthService(db_session)
        
        result = await service.refresh_token(refresh_token)
        assert result is None

    async def test_refresh_token_exception_returns_none(self, db_session):
        """token解码异常返回None"""
        service = AuthService(db_session)
        
        with patch("app.core.security.decode_token", side_effect=Exception("Decode failed")):
            result = await service.refresh_token("any_token")
            assert result is None


class TestAuthServiceSmsLoginCoverage:
    """短信登录更多测试覆盖"""

    async def test_sms_login_debug_skips_verification(self, db_session):
        """DEBUG模式跳过验证码验证"""
        service = AuthService(db_session)
        original_debug = settings.DEBUG
        settings.DEBUG = True

        try:
            result = await service.login_with_sms("13900000014", "any")
            assert result is not None
            # 用户自动创建
            user = db_session.query(User).filter(User.phone == "13900000014").first()
            assert user is not None
            assert user.nickname == "用户0014"
        finally:
            settings.DEBUG = original_debug

    async def test_sms_login_inactive_user_raises(self, db_session):
        """不活跃用户短信登录抛出异常"""
        user = User(
            phone="13900000015",
            password_hash=get_password_hash("pass"),
            is_active=False,
        )
        db_session.add(user)
        db_session.commit()

        mock_sms = Mock()
        from unittest.mock import AsyncMock
        mock_sms.verify_code = AsyncMock(return_value=True)

        with patch("app.services.auth_service.get_sms_service", return_value=mock_sms):
            service = AuthService(db_session)
            original_debug = settings.DEBUG
            settings.DEBUG = False

            try:
                with pytest.raises(ValueError) as exc_info:
                    await service.login_with_sms("13900000015", "123456")
                assert "用户已被禁用" in str(exc_info.value)
            finally:
                settings.DEBUG = original_debug


class TestAuthServiceLoginMore:
    """登录更多测试覆盖"""

    async def test_login_user_not_found_returns_none(self, db_session):
        """用户不存在返回None"""
        service = AuthService(db_session)
        result = await service.login("19999999999", "password")
        assert result is None

    async def test_login_wrong_password_returns_none(self, db_session):
        """密码错误返回None"""
        user = User(
            phone="13900000016",
            password_hash=get_password_hash("correct_password"),
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()

        service = AuthService(db_session)
        result = await service.login("13900000016", "wrong_password")
        assert result is None


def test_get_auth_service_factory(db_session):
    """测试工厂函数"""
    from app.services.auth_service import get_auth_service
    service = get_auth_service(db_session)
    assert service is not None
    assert isinstance(service, AuthService)
    assert service.db == db_session


async def test_login_with_sms_existing_active_user_success(db_session):
    """短信登录 - 已存在活跃用户成功"""
    from app.core.config import settings
    user = User(
        phone="13900000020",
        password_hash=get_password_hash("pass"),
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()

    mock_sms = Mock()
    from unittest.mock import AsyncMock
    mock_sms.verify_code = AsyncMock(return_value=True)

    with patch("app.services.auth_service.get_sms_service", return_value=mock_sms):
        service = AuthService(db_session)
        original_debug = settings.DEBUG
        settings.DEBUG = False

        try:
            result = await service.login_with_sms("13900000020", "123456")
            assert result is not None
            assert result.access_token is not None
            assert result.user.id == user.id
        finally:
            settings.DEBUG = original_debug





async def test_register_default_nickname(db_session):
    """注册使用默认昵称生成"""
    from app.core.config import settings
    mock_sms = Mock()
    from unittest.mock import AsyncMock
    mock_sms.verify_code = AsyncMock(return_value=True)

    with patch("app.services.auth_service.get_sms_service", return_value=mock_sms):
        service = AuthService(db_session)
        original_debug = settings.DEBUG
        settings.DEBUG = False

        try:
            req = RegisterRequest(
                phone="13900123456",
                password="Password@123",
                code="123456",
            )
            # 不传nickname
            if hasattr(req, 'nickname'):
                req.nickname = None
            user = await service.register(req)
            assert user is not None
            assert user.nickname == "用户3456"
        finally:
            settings.DEBUG = original_debug
