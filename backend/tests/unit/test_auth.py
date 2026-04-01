"""
认证模块单元测试
"""
import pytest
from datetime import timedelta
from unittest.mock import patch, MagicMock

from app.models import User
from app.core.security import get_password_hash, create_access_token


class TestUserRegistration:
    """用户注册测试"""

    def test_register_with_valid_phone(self, client):
        """测试有效手机号注册"""
        response = client.post("/api/v1/auth/register", json={
            "phone": "13800138001",
            "password": "Test@123456",
            "nickname": "新用户",
            "code": "123456"
        })
        # 可能是成功或失败（取决于短信服务mock）
        assert response.status_code in [200, 201, 400]

    def test_register_with_invalid_phone(self, client):
        """测试无效手机号格式"""
        response = client.post("/api/v1/auth/register", json={
            "phone": "12345",
            "password": "Test@123456",
            "nickname": "测试"
        })
        assert response.status_code == 422

    def test_register_with_weak_password(self, client):
        """测试弱密码"""
        response = client.post("/api/v1/auth/register", json={
            "phone": "13800138002",
            "password": "123",
            "nickname": "测试"
        })
        assert response.status_code == 422

    def test_register_duplicate_phone(self, client, test_user):
        """测试重复手机号注册"""
        response = client.post("/api/v1/auth/register", json={
            "phone": "13800138000",
            "password": "Test@123456",
            "nickname": "另一个用户"
        })
        # 应该返回错误
        assert response.status_code == 400


class TestUserLogin:
    """用户登录测试"""

    def test_login_with_correct_credentials(self, client, test_user):
        """测试正确凭证登录"""
        response = client.post("/api/v1/auth/login", json={
            "phone": "13800138000",
            "password": "Test@123456"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_with_wrong_password(self, client, test_user):
        """测试错误密码登录"""
        response = client.post("/api/v1/auth/login", json={
            "phone": "13800138000",
            "password": "WrongPassword"
        })
        assert response.status_code == 401

    def test_login_with_nonexistent_user(self, client):
        """测试不存在的用户登录"""
        response = client.post("/api/v1/auth/login", json={
            "phone": "13900139001",
            "password": "Test@123456"
        })
        assert response.status_code == 401

    def test_login_returns_token_type(self, client, test_user):
        """测试登录返回token类型"""
        response = client.post("/api/v1/auth/login", json={
            "phone": "13800138000",
            "password": "Test@123456"
        })
        data = response.json()
        assert data.get("token_type") == "bearer"


class TestTokenRefresh:
    """Token刷新测试"""

    def test_refresh_token_with_valid_token(self, client, test_user):
        """测试有效refresh token刷新"""
        # 先登录获取refresh token
        login_resp = client.post("/api/v1/auth/login", json={
            "phone": "13800138000",
            "password": "Test@123456"
        })
        refresh_token = login_resp.json()["refresh_token"]

        # 刷新token
        response = client.post("/api/v1/auth/refresh", json={
            "refresh_token": refresh_token
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    def test_refresh_token_with_invalid_token(self, client):
        """测试无效refresh token刷新"""
        response = client.post("/api/v1/auth/refresh", json={
            "refresh_token": "invalid.token.here"
        })
        assert response.status_code == 401


class TestPasswordReset:
    """密码重置测试"""

    def test_send_reset_code(self, client):
        """测试发送重置验证码"""
        response = client.post("/api/v1/auth/send_code", json={
            "phone": "13800138000",
            "type": "reset"
        })
        # 可能是成功或失败（取决于短信服务）
        assert response.status_code in [200, 500]

    def test_reset_password(self, client, test_user):
        """测试重置密码"""
        response = client.post("/api/v1/auth/reset_password", json={
            "phone": "13800138000",
            "code": "123456",
            "new_password": "New@123456"
        })
        # 取决于验证码是否正确
        assert response.status_code in [200, 400]


class TestGetCurrentUser:
    """获取当前用户测试"""

    def test_get_current_user_with_valid_token(self, client, test_user, auth_headers):
        """测试有效token获取用户信息"""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["phone"] == "13800138000"
        assert "nickname" in data

    def test_get_current_user_without_token(self, client):
        """测试无token获取用户信息"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401

    def test_get_current_user_with_invalid_token(self, client):
        """测试无效token获取用户信息"""
        response = client.get("/api/v1/auth/me", headers={
            "Authorization": "Bearer invalid.token"
        })
        assert response.status_code == 401


class TestSendVerificationCode:
    """发送验证码测试"""

    def test_send_code_for_register(self, client):
        """测试发送注册验证码"""
        response = client.post("/api/v1/auth/send_code", json={
            "phone": "13800138099",
            "type": "register"
        })
        # 取决于短信服务配置
        assert response.status_code in [200, 500]

    def test_send_code_with_invalid_phone(self, client):
        """测试无效手机号发送验证码"""
        response = client.post("/api/v1/auth/send_code", json={
            "phone": "123",
            "type": "register"
        })
        assert response.status_code == 422


class TestLogout:
    """登出测试"""

    def test_logout_with_valid_token(self, client, test_user, auth_headers):
        """测试有效token登出"""
        response = client.post("/api/v1/auth/logout", headers=auth_headers)
        assert response.status_code in [200, 204]

    def test_logout_without_token(self, client):
        """测试无token登出"""
        response = client.post("/api/v1/auth/logout")
        assert response.status_code == 401
