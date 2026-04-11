"""
content_filter_service 单元测试
"""
import pytest
from unittest.mock import patch, Mock

from app.core.config import settings
from app.services.content_filter import ContentFilterService


class TestContentFilterService:
    """ContentFilterService单元测试"""

    def test_init(self):
        """测试初始化"""
        service = ContentFilterService()
        assert service is not None
        assert hasattr(service, 'check_text')
        assert hasattr(service, 'get_blocked_response')

    def test_check_keyword_clean_content(self):
        """测试关键词检测 - 干净内容"""
        service = ContentFilterService()
        # 使用本地关键词检测
        ok, matches = service._check_keyword("这是一段正常的测试内容，表达了今天的好心情。")
        assert ok is True
        assert len(matches) == 0

    def test_check_keyword_sensitive_content(self):
        """测试关键词检测 - 敏感内容"""
        service = ContentFilterService()
        ok, matches = service._check_keyword("我想自杀，活着没意思")
        assert ok is False
        assert len(matches) > 0
        assert "自杀" in matches

    def test_check_keyword_multiple_sensitive(self):
        """测试关键词检测 - 多个敏感词"""
        service = ContentFilterService()
        ok, matches = service._check_keyword("这个地方有暴力和毒品")
        assert ok is False
        assert "暴力" in matches
        assert "毒品" in matches

    def test_check_keyword_case_insensitive(self):
        """测试关键词检测 - 大小写不敏感"""
        service = ContentFilterService()
        ok, matches = service._check_keyword("我想自杀".upper())
        assert ok is False
        assert "自杀" in matches

    def test_check_keyword_empty_content(self):
        """测试关键词检测 - 空内容"""
        service = ContentFilterService()
        ok, matches = service._check_keyword("")
        assert ok is True
        assert len(matches) == 0

    def test_get_blocked_response(self):
        """测试获取被拦截后的回复"""
        service = ContentFilterService()
        response = service.get_blocked_response()
        assert isinstance(response, str)
        assert len(response) > 0
        assert "抱歉" in response

    async def test_check_text_keyword_provider(self):
        """测试check_text使用关键词 provider"""
        original_provider = settings.CONTENT_FILTER_PROVIDER
        settings.CONTENT_FILTER_PROVIDER = "keyword"
        try:
            service = ContentFilterService()
            ok, matches = await service.check_text("正常内容")
            assert ok is True
            ok, matches = await service.check_text("我想自杀")
            assert ok is False
        finally:
            settings.CONTENT_FILTER_PROVIDER = original_provider

    async def test_check_text_alibaba_provider_not_configured(self):
        """测试check_text使用alibaba provider但未配置，降级到关键词"""
        original_provider = settings.CONTENT_FILTER_PROVIDER
        original_access_key = settings.ALIBABA_CONTENT_ACCESS_KEY
        settings.CONTENT_FILTER_PROVIDER = "alibaba"
        settings.ALIBABA_CONTENT_ACCESS_KEY = ""
        try:
            service = ContentFilterService()
            ok, matches = await service.check_text("我想自杀")
            assert ok is False
            assert "自杀" in matches
        finally:
            settings.CONTENT_FILTER_PROVIDER = original_provider
            settings.ALIBABA_CONTENT_ACCESS_KEY = original_access_key

    async def test_check_text_alibaba_import_error(self):
        """测试check_text阿里云SDK未安装降级到关键词"""
        original_provider = settings.CONTENT_FILTER_PROVIDER
        original_access_key = settings.ALIBABA_CONTENT_ACCESS_KEY
        original_secret = settings.ALIBABA_CONTENT_ACCESS_SECRET
        settings.CONTENT_FILTER_PROVIDER = "alibaba"
        settings.ALIBABA_CONTENT_ACCESS_KEY = "fake_key"
        settings.ALIBABA_CONTENT_ACCESS_SECRET = "fake_secret"
        try:
            service = ContentFilterService()
            # 模拟ImportError
            with patch("builtins.__import__", side_effect=ImportError):
                ok, matches = await service.check_text("我想自杀")
                assert ok is False
                assert "自杀" in matches
        finally:
            settings.CONTENT_FILTER_PROVIDER = original_provider
            settings.ALIBABA_CONTENT_ACCESS_KEY = original_access_key
            settings.ALIBABA_CONTENT_ACCESS_SECRET = original_secret

    async def test_check_text_alibaba_general_exception(self):
        """测试check_text阿里云调用异常降级到关键词"""
        original_provider = settings.CONTENT_FILTER_PROVIDER
        original_access_key = settings.ALIBABA_CONTENT_ACCESS_KEY
        original_secret = settings.ALIBABA_CONTENT_ACCESS_SECRET
        settings.CONTENT_FILTER_PROVIDER = "alibaba"
        settings.ALIBABA_CONTENT_ACCESS_KEY = "fake_key"
        settings.ALIBABA_CONTENT_ACCESS_SECRET = "fake_secret"
        try:
            service = ContentFilterService()
            # 模拟正常导入但调用时异常
            with patch.object(service, '_check_alibaba', side_effect=Exception("API Error")):
                ok, matches = await service.check_text("我想自杀")
                assert ok is False
                assert "自杀" in matches
        finally:
            settings.CONTENT_FILTER_PROVIDER = original_provider
            settings.ALIBABA_CONTENT_ACCESS_KEY = original_access_key
            settings.ALIBABA_CONTENT_ACCESS_SECRET = original_secret
