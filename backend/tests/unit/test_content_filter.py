"""
content_filter 单元测试
"""
import pytest
from unittest.mock import Mock, patch

from app.core.config import settings
from app.services.content_filter import ContentFilterService, get_content_filter, SENSITIVE_WORDS


class TestContentFilterInit:
    """内容过滤服务初始化测试"""

    def test_init_default_provider(self):
        """测试初始化默认提供商"""
        original_provider = settings.CONTENT_FILTER_PROVIDER
        settings.CONTENT_FILTER_PROVIDER = "keyword"
        try:
            service = ContentFilterService()
            assert service.provider == "keyword"
            assert service._sensitive_pattern is not None
        finally:
            settings.CONTENT_FILTER_PROVIDER = original_provider

    def test_singleton_factory(self):
        """测试单例工厂"""
        service1 = get_content_filter()
        service2 = get_content_filter()
        assert service1 is service2


class TestContentFilterKeywordCheck:
    """本地关键词检测测试"""

    def test_check_keyword_clean_text_passed(self):
        """干净文本通过检测"""
        service = ContentFilterService()
        service.provider = "keyword"
        passed, matches = service._check_keyword("你好，今天心情很好")
        assert passed is True
        assert len(matches) == 0

    def test_check_keyword_sensitive_word_detected(self):
        """检测到敏感词返回False"""
        service = ContentFilterService()
        text = "我想自杀"
        passed, matches = service._check_keyword(text)
        assert passed is False
        assert "自杀" in matches
        assert len(matches) >= 1

    def test_check_keyword_case_insensitive(self):
        """检测大小写不敏感"""
        service = ContentFilterService()
        text = "我想自杀".upper()
        passed, matches = service._check_keyword(text)
        assert passed is False
        assert len(matches) == 1

    def test_check_keyword_multiple_sensitive_words(self):
        """多个敏感词都被检测到"""
        service = ContentFilterService()
        text = "色情和暴力内容"
        passed, matches = service._check_keyword(text)
        assert passed is False
        assert "色情" in matches
        assert "暴力" in matches
        assert len(matches) == 2

    def test_check_keyword_duplicate_words_deduplicated(self):
        """重复敏感词去重"""
        service = ContentFilterService()
        text = "自杀自杀自杀"
        passed, matches = service._check_keyword(text)
        assert passed is False
        assert len(matches) == 1  # 去重
        assert "自杀" in matches


class TestContentFilterCheckTextRouting:
    """check_text 根据provider路由测试"""

    async def test_check_text_routes_to_keyword(self):
        """provider=keyword 路由到 _check_keyword"""
        service = ContentFilterService()
        service.provider = "keyword"
        # 干净文本
        passed, matches = await service.check_text("这是正常文本")
        assert passed is True

    async def test_check_text_routes_to_alibaba(self):
        """provider=alibaba 路由到 _check_alibaba"""
        service = ContentFilterService()
        service.provider = "alibaba"
        with patch.object(service, '_check_alibaba') as mock_check:
            mock_check.return_value = (True, [])
            await service.check_text("测试文本")
            mock_check.assert_called_once_with("测试文本")


class TestContentFilterAlibabaCheck:
    """阿里云检测测试"""

    async def test_alibaba_not_configured_fallback_keyword(self):
        """阿里云未配置降级到关键词"""
        import loguru
        service = ContentFilterService()
        original_key = settings.ALIBABA_CONTENT_ACCESS_KEY
        settings.ALIBABA_CONTENT_ACCESS_KEY = ""
        try:
            with patch.object(loguru.logger, 'warning') as mock_log:
                result_passed, result_matches = await service._check_alibaba("文本包含自杀")
                # 降级检测到敏感词
                assert result_passed is False
                assert "自杀" in result_matches
                mock_log.assert_called()
                # 第一个调用是阿里云未配置警告
                first_call_args = mock_log.call_args_list[0][0][0]
                assert "阿里云内容安全未配置" in first_call_args
        finally:
            settings.ALIBABA_CONTENT_ACCESS_KEY = original_key

    async def test_alibaba_sdk_not_installed_fallback(self):
        """阿里云SDK未安装降级到关键词 - 使用try/except捕获ImportError路径"""
        import loguru
        service = ContentFilterService()
        original_key = settings.ALIBABA_CONTENT_ACCESS_KEY
        settings.ALIBABA_CONTENT_ACCESS_KEY = "test_key"
        settings.ALIBABA_CONTENT_ACCESS_SECRET = "test_secret"
        
        # 由于阿里云SDK在当前环境确实未安装，直接执行就能进入ImportError分支
        with patch.object(loguru.logger, 'warning') as mock_log:
            # 调用 _check_alibaba - 会进入try并触发ImportError
            result_passed, result_matches = await service._check_alibaba("文本包含自杀")
            # 降级检测到敏感词
            assert result_passed is False
            assert "自杀" in result_matches
            # 确认日志被记录
            mock_log.assert_called()
            # 检查日志消息
            has_warning = any(
                "阿里云SDK未安装" in call[0][0]
                for call in mock_log.call_args_list
            )
            assert has_warning
        
        settings.ALIBABA_CONTENT_ACCESS_KEY = original_key

    async def test_alibaba_api_exception_fallback_keyword(self):
        """阿里云API异常降级到关键词"""
        service = ContentFilterService()
        original_key = settings.ALIBABA_CONTENT_ACCESS_KEY
        settings.ALIBABA_CONTENT_ACCESS_KEY = "test_key"
        settings.ALIBABA_CONTENT_ACCESS_SECRET = "test_secret"

        # 模拟已导入但API调用异常
        mock_client = Mock()
        mock_client.text_scan = Mock(side_effect=Exception("API connection error"))
        
        #  mock import 返回我们的模拟模块
        mock_module = Mock()
        mock_module.Client = Mock(return_value=mock_client)
        mock_module.models = Mock()
        mock_module.models.TextScanRequest = Mock
        mock_module.credentials = Mock()
        mock_module.credentials.AccessKeyCredential = Mock
        
        with patch.dict('sys.modules', {
            'aliyungo_cs20151209': mock_module,
            'aliyungo_cs20151209.client': mock_module,
            'aliyungo_cs20151209.models': mock_module.models,
            'aliyungo_cs20151209.credentials': mock_module.credentials,
        }):
            with patch("loguru.logger.error") as mock_log:
                result_passed, result_matches = await service._check_alibaba("文本包含自杀")
                assert result_passed is False
                assert "自杀" in result_matches
                mock_log.assert_called()
                assert "内容安全检测异常" in mock_log.call_args[0][0]

        settings.ALIBABA_CONTENT_ACCESS_KEY = original_key

    async def test_alibaba_response_pass(self):
        """阿里云检测通过返回True"""
        service = ContentFilterService()
        original_key = settings.ALIBABA_CONTENT_ACCESS_KEY
        settings.ALIBABA_CONTENT_ACCESS_KEY = "test_key"
        settings.ALIBABA_CONTENT_ACCESS_SECRET = "test_secret"

        # 模拟响应
        mock_response = Mock()
        mock_response.body = Mock()
        mock_data_item = Mock()
        mock_data_item.suggestion = "pass"
        mock_response.body.data = [mock_data_item]

        mock_client = Mock()
        mock_client.text_scan = Mock(return_value=mock_response)

        mock_module = Mock()
        mock_module.Client = Mock(return_value=mock_client)
        mock_module.models = Mock()
        mock_module.models.TextScanRequest = Mock
        mock_module.credentials = Mock()
        mock_module.credentials.AccessKeyCredential = Mock

        with patch.dict('sys.modules', {
            'aliyungo_cs20151209': mock_module,
            'aliyungo_cs20151209.client': mock_module,
            'aliyungo_cs20151209.models': mock_module.models,
            'aliyungo_cs20151209.credentials': mock_module.credentials,
        }):
            result_passed, result_matches = await service._check_alibaba("干净文本没有敏感词")
            assert result_passed is True
            assert len(result_matches) == 0

        settings.ALIBABA_CONTENT_ACCESS_KEY = original_key

    async def test_alibaba_response_reject(self):
        """阿里云检测不通过返回False"""
        service = ContentFilterService()
        original_key = settings.ALIBABA_CONTENT_ACCESS_KEY
        settings.ALIBABA_CONTENT_ACCESS_KEY = "test_key"
        settings.ALIBABA_CONTENT_ACCESS_SECRET = "test_secret"

        mock_response = Mock()
        mock_response.body = Mock()
        mock_data_item = Mock()
        mock_data_item.suggestion = "block"
        mock_response.body.data = [mock_data_item]

        mock_client = Mock()
        mock_client.text_scan = Mock(return_value=mock_response)

        mock_module = Mock()
        mock_module.Client = Mock(return_value=mock_client)
        mock_module.models = Mock()
        mock_module.models.TextScanRequest = Mock
        mock_module.credentials = Mock()
        mock_module.credentials.AccessKeyCredential = Mock

        with patch.dict('sys.modules', {
            'aliyungo_cs20151209': mock_module,
            'aliyungo_cs20151209.client': mock_module,
            'aliyungo_cs20151209.models': mock_module.models,
            'aliyungo_cs20151209.credentials': mock_module.credentials,
        }):
            result_passed, result_matches = await service._check_alibaba("违规内容")
            assert result_passed is False
            assert "content_flagged" in result_matches

        settings.ALIBABA_CONTENT_ACCESS_KEY = original_key


def test_get_blocked_response():
    """测试获取被拦截后的回复文本"""
    service = ContentFilterService()
    response = service.get_blocked_response()
    assert isinstance(response, str)
    assert len(response) > 0
    assert "抱歉" in response
    assert "不适合讨论" in response


def test_empty_sensitive_words_handled():
    """测试空敏感词列表处理"""
    with patch("app.services.content_filter.SENSITIVE_WORDS", set()):
        service = ContentFilterService()
        assert service._sensitive_pattern is None
        passed, matches = service._check_keyword("任何文本")
        assert passed is True
        assert matches == []
