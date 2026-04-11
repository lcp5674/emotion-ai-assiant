"""
sms_service 单元测试
"""
import pytest
from unittest.mock import Mock, patch

from app.core.config import settings
from app.services.sms_service import SmsService, get_sms_service


class TestSmsService:
    """短信服务单元测试"""

    def test_get_sms_service_singleton(self):
        """测试短信服务是单例"""
        service1 = get_sms_service()
        service2 = get_sms_service()
        assert service1 is service2

    def test_init_with_config(self):
        """测试使用配置初始化"""
        service = SmsService()
        assert service is not None
        # 检查配置是否加载
        assert hasattr(service, 'provider')
        assert service.provider == settings.SMS_PROVIDER.lower()

    async def test_send_verify_code_mock_provider(self):
        """测试发送验证码（mock provider）"""
        original_provider = settings.SMS_PROVIDER
        settings.SMS_PROVIDER = "mock"
        
        try:
            service = SmsService()
            result = await service.send_verify_code("13800138000", "123456")
            # mock模式应该返回成功
            assert result is True
        finally:
            settings.SMS_PROVIDER = original_provider

    async def test_send_verify_code_alibaba_not_configured_fallback(self):
        """测试alibaba未配置降级到mock"""
        original_provider = settings.SMS_PROVIDER
        original_access_key = settings.ALIBABA_ACCESS_KEY_ID
        original_access_secret = settings.ALIBABA_ACCESS_KEY_SECRET
        
        settings.SMS_PROVIDER = "alibaba"
        settings.ALIBABA_ACCESS_KEY_ID = ""
        settings.ALIBABA_ACCESS_KEY_SECRET = ""
        
        try:
            service = SmsService()
            result = await service.send_verify_code("13800138000", "123456")
            # 未配置降级到mock，仍然返回成功
            assert result is True
        finally:
            settings.SMS_PROVIDER = original_provider
            settings.ALIBABA_ACCESS_KEY_ID = original_access_key
            settings.ALIBABA_ACCESS_KEY_SECRET = original_access_secret

    async def test_send_verify_code_alibaba_import_error_fallback(self):
        """测试阿里云SDK未安装降级到mock"""
        original_provider = settings.SMS_PROVIDER
        original_access_key = settings.ALIBABA_ACCESS_KEY_ID
        original_access_secret = settings.ALIBABA_ACCESS_KEY_SECRET
        
        settings.SMS_PROVIDER = "alibaba"
        settings.ALIBABA_ACCESS_KEY_ID = "test_key"
        settings.ALIBABA_ACCESS_KEY_SECRET = "test_secret"
        
        try:
            # 模拟ImportError
            with patch("builtins.__import__", side_effect=ImportError):
                service = SmsService()
                result = await service.send_verify_code("13800138000", "123456")
                # SDK未安装降级到mock，返回成功
                assert result is True
        finally:
            settings.SMS_PROVIDER = original_provider
            settings.ALIBABA_ACCESS_KEY_ID = original_access_key
            settings.ALIBABA_ACCESS_KEY_SECRET = original_access_secret

    async def test_send_verify_code_alibaba_general_exception_fallback(self):
        """测试阿里云异常降级到mock"""
        original_provider = settings.SMS_PROVIDER
        original_access_key = settings.ALIBABA_ACCESS_KEY_ID
        original_access_secret = settings.ALIBABA_ACCESS_KEY_SECRET
        
        settings.SMS_PROVIDER = "alibaba"
        settings.ALIBABA_ACCESS_KEY_ID = "test_key"
        settings.ALIBABA_ACCESS_KEY_SECRET = "test_secret"
        
        try:
            service = SmsService()
            # 让_alibaba发送抛出异常
            with patch.object(service, '_send_alibaba', side_effect=Exception("API Error")):
                # 实际上还是会调用_send_mock
                with patch.object(service, '_send_mock', return_value=True):
                    result = await service.send_verify_code("13800138000", "123456")
                    assert result is True
        finally:
            settings.SMS_PROVIDER = original_provider
            settings.ALIBABA_ACCESS_KEY_ID = original_access_key
            settings.ALIBABA_ACCESS_KEY_SECRET = original_access_secret

    def test_mock_send_always_success(self):
        """mock发送总是成功"""
        from app.core.config import settings
        original_provider = settings.SMS_PROVIDER
        settings.SMS_PROVIDER = "mock"
        
        service = SmsService()
        # 即使任何手机号，mock都返回成功
        assert service._send_mock("13800000000", "123456") is not None
        # 异步返回bool
        assert hasattr(service._send_mock, '__await__')
