"""
安全工具模块单元测试
"""
import pytest
from datetime import timedelta
from fastapi import HTTPException

from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token,
    generate_verify_code,
    mask_phone,
)


class TestPasswordHash:
    """密码哈希测试"""

    def test_get_password_hash_generates_valid_hash(self):
        """测试密码哈希生成"""
        password = "Test@123456"
        hashed = get_password_hash(password)

        assert hashed != password
        assert len(hashed) > 0

    def test_verify_password_with_correct_password(self):
        """测试正确密码验证"""
        password = "Test@123456"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_with_incorrect_password(self):
        """测试错误密码验证"""
        password = "Test@123456"
        hashed = get_password_hash(password)

        assert verify_password("WrongPassword", hashed) is False

    def test_same_password_generates_different_hashes(self):
        """测试相同密码生成不同哈希（加盐）"""
        password = "Test@123456"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2


class TestTokenCreation:
    """令牌创建测试"""

    def test_create_access_token(self):
        """测试创建访问令牌"""
        data = {"sub": "1"}
        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token(self):
        """测试创建刷新令牌"""
        data = {"sub": "1"}
        token = create_refresh_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_token_contains_required_data(self):
        """测试令牌包含必要数据"""
        data = {"sub": "123"}
        token = create_access_token(data)
        payload = decode_token(token)

        assert payload["sub"] == "123"

    def test_access_token_has_correct_type(self):
        """测试访问令牌类型正确"""
        data = {"sub": "1"}
        token = create_access_token(data)
        payload = verify_token(token)

        assert payload["type"] == "access"

    def test_refresh_token_has_correct_type(self):
        """测试刷新令牌类型正确"""
        data = {"sub": "1"}
        token = create_refresh_token(data)
        payload = decode_token(token)

        assert payload["type"] == "refresh"

    def test_token_with_custom_expiry(self):
        """测试自定义过期时间"""
        data = {"sub": "1"}
        expires = timedelta(minutes=30)
        token = create_access_token(data, expires_delta=expires)
        payload = decode_token(token)

        assert "exp" in payload


class TestTokenValidation:
    """令牌验证测试"""

    def test_verify_token_with_valid_token(self):
        """测试验证有效令牌"""
        data = {"sub": "1"}
        token = create_access_token(data)

        payload = verify_token(token)
        assert payload["sub"] == "1"

    def test_verify_token_with_invalid_token(self):
        """测试验证无效令牌"""
        invalid_token = "invalid.token.here"

        with pytest.raises(HTTPException) as exc_info:
            verify_token(invalid_token)

        assert exc_info.value.status_code == 401

    def test_verify_token_with_wrong_type(self):
        """测试验证错误类型的令牌"""
        # 使用refresh token作为access token
        data = {"sub": "1"}
        refresh_token = create_refresh_token(data)

        with pytest.raises(HTTPException) as exc_info:
            verify_token(refresh_token)

        assert exc_info.value.status_code == 401
        assert "无效的令牌类型" in str(exc_info.value.detail)

    def test_decode_token_without_type_check(self):
        """测试解码令牌（不检查类型）"""
        data = {"sub": "1"}
        refresh_token = create_refresh_token(data)

        payload = decode_token(refresh_token)
        assert payload["sub"] == "1"
        assert payload["type"] == "refresh"


class TestVerifyCode:
    """验证码测试"""

    def test_generate_verify_code_length(self):
        """测试验证码长度"""
        code = generate_verify_code(6)

        assert len(code) == 6

    def test_generate_verify_code_numeric(self):
        """测试验证码是数字"""
        code = generate_verify_code(6)

        assert code.isdigit() is True

    def test_generate_verify_code_custom_length(self):
        """测试自定义长度验证码"""
        code = generate_verify_code(4)

        assert len(code) == 4

    def test_generate_verify_code_unique(self):
        """测试验证码随机性（连续生成不同）"""
        codes = set()
        for _ in range(100):
            codes.add(generate_verify_code(6))

        # 应该基本都是不同的
        assert len(codes) > 90


class TestPhoneMasking:
    """手机号脱敏测试"""

    def test_mask_phone_with_valid_number(self):
        """测试11位手机号脱敏"""
        phone = "13800138000"
        masked = mask_phone(phone)

        assert masked == "138****8000"
        assert len(masked) == len(phone)
        assert "****" in masked

    def test_mask_phone_with_short_number(self):
        """测试不足11位手机号不处理"""
        phone = "12345"
        masked = mask_phone(phone)

        assert masked == phone

    def test_mask_phone_with_empty_string(self):
        """测试空字符串"""
        phone = ""
        masked = mask_phone(phone)

        assert masked == phone

    def test_mask_phone_with_other_length(self):
        """测试其他长度不处理"""
        phone = "1234567890123"  # 13位
        masked = mask_phone(phone)

        assert masked == phone


class TestEdgeCases:
    """边界情况测试"""

    def test_empty_password_hash(self):
        """测试空密码哈希"""
        # 即使空密码也应该能生成哈希
        hashed = get_password_hash("")

        assert len(hashed) > 0
        assert verify_password("", hashed) is True

    def test_very_long_password(self):
        """测试非常长的密码"""
        long_password = "a" * 1000
        hashed = get_password_hash(long_password)

        assert verify_password(long_password, hashed) is True
        assert not verify_password("wrong", hashed)

    def test_token_with_special_characters_in_sub(self):
        """测试sub包含特殊字符"""
        data = {"sub": "user-123!@#$"}
        token = create_access_token(data)
        payload = verify_token(token)

        assert payload["sub"] == "user-123!@#$"
