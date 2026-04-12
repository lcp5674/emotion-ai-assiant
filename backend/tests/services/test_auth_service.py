"""
认证服务单元测试
"""
import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from app.models import User
from app.services.auth_service import get_auth_service
from app.core.security import get_password_hash, verify_password


class TestAuthService:
    """认证服务测试"""

    @pytest.fixture
    def mock_db(self):
        """模拟数据库会话"""
        return Mock(spec=Session)

    @pytest.fixture
    def auth_service(self):
        """认证服务实例"""
        return get_auth_service()

    @pytest.fixture
    def mock_user(self):
        """模拟用户"""
        user = Mock(spec=User)
        user.id = 1
        user.phone = "13800138000"
        user.password_hash = get_password_hash("Test@123456")
        user.is_active = True
        return user

    def test_verify_password(self):
        """测试密码验证"""
        password = "Test@123456"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True
        assert verify_password("wrong", hashed) is False

    def test_get_password_hash(self):
        """测试密码哈希"""
        password = "Test@123456"
        hashed = get_password_hash(password)
        assert hashed != password
        assert len(hashed) > 60

    @patch('app.services.auth_service.get_password_hash')
    def test_create_user(self, mock_get_password_hash, auth_service, mock_db, mock_user):
        """测试创建用户"""
        # 准备
        mock_get_password_hash.return_value = "hashed_password"
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock(side_effect=lambda x: setattr(x, 'id', 1))

        # 执行
        user = auth_service.create_user(
            db=mock_db,
            phone="13800138000",
            password="Test@123456",
            nickname="测试用户"
        )

        # 验证
        assert user is not None
        assert user.phone == "13800138000"
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_get_user_by_phone(self, auth_service, mock_db, mock_user):
        """测试通过手机号获取用户"""
        # 准备
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        # 执行
        user = auth_service.get_user_by_phone(mock_db, "13800138000")

        # 验证
        assert user == mock_user

    def test_get_user_by_id(self, auth_service, mock_db, mock_user):
        """测试通过ID获取用户"""
        # 准备
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        # 执行
        user = auth_service.get_user_by_id(mock_db, 1)

        # 验证
        assert user == mock_user

    def test_update_last_login(self, auth_service, mock_db, mock_user):
        """测试更新最后登录时间"""
        # 准备
        mock_db.commit = Mock()

        # 执行
        auth_service.update_last_login(mock_db, mock_user)

        # 验证
        mock_db.commit.assert_called_once()
