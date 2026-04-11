"""
core/security.py 单元测试 - 密码处理和令牌
"""
import pytest
from unittest.mock import patch
from fastapi import HTTPException

from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token,
    get_current_user_id,
    generate_verify_code,
    mask_phone,
)


class TestPasswordHandling:
    """密码处理测试"""

    def test_verify_correct_password(self):
        """验证正确密码返回True"""
        password = "my_secret_password"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True

    def test_verify_incorrect_password(self):
        """验证错误密码返回False"""
        password = "my_secret_password"
        wrong_password = "wrong_password"
        hashed = get_password_hash(password)
        assert verify_password(wrong_password, hashed) is False

    def test_hash_consistency(self):
        """相同密码生成不同hash(因为盐)"""
        password = "test_password"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        # 加盐后应该不同
        assert hash1 != hash2


class TestJWTToken:
    """JWT令牌测试"""

    def test_create_and_decode_token(self):
        """创建然后解码令牌"""
        subject = {"sub": "123"}  # JWT payload
        token = create_access_token(subject)
        assert isinstance(token, str)
        assert len(token) > 0
        
        decoded = decode_token(token)
        assert decoded is not None
        assert decoded["sub"] == "123"
        assert decoded["type"] == "access"

    def test_decode_invalid_token(self):
        """解码无效令牌抛出异常"""
        invalid_token = "this.is.not.valid"
        with pytest.raises(HTTPException):
            decode_token(invalid_token)

    def test_create_refresh_token(self):
        """创建刷新令牌"""
        subject = {"sub": "123"}
        token = create_refresh_token(subject)
        assert isinstance(token, str)
        decoded = decode_token(token)
        assert decoded["type"] == "refresh"

    def test_verify_token_wrong_type(self):
        """验证错误类型令牌"""
        token = create_refresh_token({"sub": "123"})
        with pytest.raises(HTTPException):
            verify_token(token)

    def test_verify_token_success(self):
        """验证成功access令牌"""
        token = create_access_token({"sub": "123"})
        payload = verify_token(token)
        assert payload["sub"] == "123"


class TestHelperFunctions:
    """辅助函数测试"""

    def test_generate_verify_code(self):
        """生成验证码"""
        code = generate_verify_code()
        assert len(code) == 6
        assert code.isdigit()

        code8 = generate_verify_code(8)
        assert len(code8) == 8

    def test_mask_phone(self):
        """手机号脱敏"""
        masked = mask_phone("13900001234")
        assert masked == "139****1234"
        # 非11位不处理
        assert mask_phone("12345") == "12345"


class TestGetCurrentUserId:
    """获取当前用户ID测试"""

    async def test_get_current_user_id_success(self):
        """成功获取用户ID"""
        token = create_access_token({"sub": "123"})
        user_id = await get_current_user_id(token)
        assert user_id == 123

    async def test_get_current_user_id_no_sub(self):
        """没有sub抛出异常"""
        token = create_access_token({})
        with pytest.raises(HTTPException):
            await get_current_user_id(token)
