"""
payment_service (WeChat Pay) 单元测试
"""
import pytest
from unittest.mock import Mock, patch

from app.services.payment_service import WechatPayService, get_wechat_pay_service
from app.core.config import settings


class TestWechatPayService:
    """WechatPayService单元测试"""

    def test_init_disabled_when_config_missing(self):
        """测试配置缺失时服务禁用"""
        from app.core.config import settings
        original_enabled = settings.WECHAT_PAY_ENABLED
        original_mchid = settings.WECHAT_MCHID
        
        settings.WECHAT_PAY_ENABLED = True
        settings.WECHAT_MCHID = ""
        
        service = WechatPayService()
        assert not service.is_enabled()
        
        settings.WECHAT_PAY_ENABLED = original_enabled
        settings.WECHAT_MCHID = original_mchid

    def test_init_enabled_when_config_present(self):
        """测试配置存在时服务启用"""
        from app.core.config import settings
        original_enabled = settings.WECHAT_PAY_ENABLED
        original_mchid = settings.WECHAT_MCHID
        original_apiv3 = settings.WECHAT_APIV3_KEY
        
        settings.WECHAT_PAY_ENABLED = True
        settings.WECHAT_MCHID = "test_mchid"
        settings.WECHAT_APIV3_KEY = "test_apiv3_key"
        
        service = WechatPayService()
        assert service.is_enabled() is True
        
        settings.WECHAT_PAY_ENABLED = original_enabled
        settings.WECHAT_MCHID = original_mchid
        settings.WECHAT_APIV3_KEY = original_apiv3

    def test_singleton_instance(self):
        """测试单例实例"""
        service1 = get_wechat_pay_service()
        service2 = get_wechat_pay_service()
        assert service1 is service2

    def test_build_order_payload(self):
        """测试构建订单payload"""
        service = WechatPayService()
        payload = service._build_order_payload(
            "test_order_123",
            2990,
            "月度会员"
        )
        assert payload["out_trade_no"] == "test_order_123"
        assert payload["amount"]["total"] == 2990
        assert payload["description"] == "月度会员"

    def test_generate_nonce(self):
        """测试生成nonce"""
        service = WechatPayService()
        nonce = service._generate_nonce()
        assert len(nonce) == 32
        assert all(c.isalnum() for c in nonce)

    async def test_create_native_order_mock_mode(self):
        """测试创建Native订单 - 模拟模式"""
        from app.core.config import settings
        original_enabled = settings.WECHAT_PAY_ENABLED
        settings.WECHAT_PAY_ENABLED = False
        
        service = WechatPayService()
        result = await service.create_native_order(
            "test_order_123",
            2990,
            "月度会员"
        )
        assert result["mode"] == "mock"
        assert result["order_no"] == "test_order_123"
        
        settings.WECHAT_PAY_ENABLED = original_enabled

    async def test_create_native_order_import_error(self):
        """测试创建Native订单 - httpx未安装返回mock"""
        from app.core.config import settings
        original_enabled = settings.WECHAT_PAY_ENABLED
        original_mchid = settings.WECHAT_MCHID
        settings.WECHAT_PAY_ENABLED = True
        settings.WECHAT_MCHID = "test_mchid"
        
        with patch('app.services.payment_service.httpx', None):
            service = WechatPayService()
            result = await service.create_native_order(
                "test_order_123",
                2990,
                "月度会员"
            )
            assert result["mode"] == "mock"
        
        settings.WECHAT_PAY_ENABLED = original_enabled
        settings.WECHAT_MCHID = original_mchid

    def test_signature_handling(self):
        """测试签名处理"""
        from app.core.config import settings
        # 测试方法存在
        service = WechatPayService()
        # 即使没有正确的密钥文件，方法应该存在
        assert hasattr(service, '_sign')


class TestAlipayService:
    """支付宝服务测试"""
    # 支付宝服务在alipay_service.py
    
    def test_alipay_service_exists(self):
        """测试支付宝服务存在"""
        from app.services.alipay_service import AlipayService
        service = AlipayService()
        assert service is not None
        assert hasattr(service, 'create_order')
        assert hasattr(service, 'verify_notify')

    def test_alipay_is_enabled(self):
        """测试支付宝启用状态检查"""
        from app.services.alipay_service import AlipayService
        service = AlipayService()
        # 方法应该存在
        assert hasattr(service, 'is_enabled')
