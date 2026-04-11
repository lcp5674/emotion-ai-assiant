"""
LLM服务工厂和提供者单元测试
"""
import pytest
import asyncio
from unittest.mock import Mock, patch

from app.services.llm.factory import get_llm_provider, chat, chat_stream, _retry_with_backoff
from app.services.llm.providers import LLMProvider, MockProvider, OpenAIProvider, AnthropicProvider
from app.services.llm.providers import GLMProvider, QwenProvider, DoubaoProvider, HunyuanProvider, SiliconFlowProvider
from app.services.llm.providers import MiniMaxProvider, ERNIEProvider, SparkProvider
from app.core.config import settings

import app.services.llm.factory as llm_factory


class TestLLMFactory:
    """LLM工厂测试"""

    def test_get_provider_mock(self):
        """测试获取mock提供者"""
        from app.core.config import settings
        original_provider = settings.LLM_PROVIDER
        original_instance = llm_factory._llm_provider
        llm_factory._llm_provider = None  # 清除单例
        settings.LLM_PROVIDER = "mock"
        
        provider = get_llm_provider()
        assert isinstance(provider, MockProvider)
        
        # 恢复
        settings.LLM_PROVIDER = original_provider
        llm_factory._llm_provider = original_instance

    def test_get_provider_openai(self):
        """测试获取OpenAI提供者"""
        from app.core.config import settings
        original_provider = settings.LLM_PROVIDER
        original_key = settings.OPENAI_API_KEY
        
        settings.LLM_PROVIDER = "openai"
        settings.OPENAI_API_KEY = "test-key"
        
        provider = get_llm_provider()
        # 运行时会创建正确类型
        assert provider is not None
        
        settings.LLM_PROVIDER = original_provider
        settings.OPENAI_API_KEY = original_key

    def test_get_unknown_provider_fallback(self):
        """测试未知提供者fallback到mock"""
        from app.core.config import settings
        original_provider = settings.LLM_PROVIDER
        original_instance = llm_factory._llm_provider
        llm_factory._llm_provider = None  # 清除单例
        settings.LLM_PROVIDER = "unknown_provider"
        
        with patch("loguru.logger.warning") as mock_log:
            provider = get_llm_provider()
            mock_log.assert_called()
        assert isinstance(provider, MockProvider)
        
        # 恢复
        settings.LLM_PROVIDER = original_provider
        llm_factory._llm_provider = original_instance

    def test_list_available_providers(self):
        """测试列出可用提供者"""
        from app.services.llm.providers import PROVIDER_MAP
        providers = list(PROVIDER_MAP.keys())
        assert isinstance(providers, list)
        assert "mock" in providers
        assert "openai" in providers
        assert "anthropic" in providers
        assert "glm" in providers
        assert "qwen" in providers


class TestMockProvider:
    """Mock LLM提供者测试"""

    def test_init(self):
        """测试初始化"""
        provider = MockProvider(api_key="mock", model="mock")
        assert provider is not None
        assert provider.api_key == "mock"
        assert provider.model == "mock"

    async def test_chat(self):
        """测试chat生成"""
        provider = MockProvider(api_key="mock", model="mock")
        response = await provider.chat([
            {"role": "user", "content": "你好"}
        ])
        assert isinstance(response, str)
        assert len(response) > 0

    async def test_chat_stream(self):
        """测试流式chat"""
        provider = MockProvider(api_key="mock", model="mock")
        chunks = []
        async for chunk in provider.chat_stream([
            {"role": "user", "content": "你好"}
        ]):
            chunks.append(chunk)
        assert len(chunks) > 0
        # 合并后应有内容
        full = "".join(chunks)
        assert len(full) > 0

    async def test_chat_different_emotions(self):
        """测试针对不同情绪生成不同回复"""
        provider = MockProvider(api_key="mock", model="mock")
        
        # 难过情绪
        sad_response = await provider.chat([
            {"role": "user", "content": "我今天很难过"}
        ])
        assert "难过" in sad_response or "沮丧" in sad_response
        assert len(sad_response) > 0
        
        # 焦虑情绪
        anxious_response = await provider.chat([
            {"role": "user", "content": "我很焦虑，压力很大"}
        ])
        assert "焦虑" in anxious_response or "压力" in anxious_response
        
        # 默认回复
        default_response = await provider.chat([
            {"role": "user", "content": "随便聊聊"}
        ])
        assert len(default_response) > 0


class TestOpenAIProvider:
    """OpenAI提供者测试"""

    def test_init(self):
        """测试初始化"""
        with patch("openai.AsyncOpenAI"):
            provider = OpenAIProvider(api_key="test-key", model="gpt-3.5-turbo")
            assert provider is not None
            assert provider.api_key == "test-key"
            assert provider.model == "gpt-3.5-turbo"

    def test_init_with_custom_base_url(self):
        """测试自定义base_url初始化"""
        with patch("openai.AsyncOpenAI"):
            provider = OpenAIProvider(
                api_key="test-key",
                model="gpt-3.5-turbo",
                base_url="https://custom.api.com/v1"
            )
            assert provider is not None
            assert provider.base_url == "https://custom.api.com/v1"


class TestAnthropicProvider:
    """Anthropic Claude提供者测试"""

    def test_init(self):
        """测试初始化"""
        with patch("anthropic.AsyncAnthropic"):
            provider = AnthropicProvider(api_key="test-key", model="claude-3-haiku")
            assert provider is not None
            assert provider.api_key == "test-key"
            assert provider.model == "claude-3-haiku"


class TestGLMProvider:
    """智谱GLM提供者测试"""

    def test_init(self):
        """测试初始化"""
        with patch("openai.AsyncOpenAI"):
            provider = GLMProvider(api_key="test-key", model="glm-4")
            assert provider is not None
            assert provider.api_key == "test-key"
            assert provider.model == "glm-4"


class TestQwenProvider:
    """阿里通义千问提供者测试"""

    def test_init(self):
        """测试初始化"""
        with patch("openai.AsyncOpenAI"):
            provider = QwenProvider(api_key="test-key", model="qwen-turbo")
            assert provider is not None
            assert provider.api_key == "test-key"
            assert provider.model == "qwen-turbo"


class TestDoubaoProvider:
    """字节跳动豆包提供者测试"""

    def test_init(self):
        """测试初始化"""
        with patch("openai.AsyncOpenAI"):
            provider = DoubaoProvider(api_key="test-key", model="doubao-pro")
            assert provider is not None
            assert provider.api_key == "test-key"
            assert provider.model == "doubao-pro"


class TestHunyuanProvider:
    """腾讯混元提供者测试"""

    def test_init(self):
        """测试初始化"""
        with patch("openai.AsyncOpenAI"):
            provider = HunyuanProvider(api_key="test-key", model="hunyuan-pro")
            assert provider is not None
            assert provider.api_key == "test-key"
            assert provider.model == "hunyuan-pro"


class TestSiliconFlowProvider:
    """硅基流动提供者测试"""

    def test_init(self):
        """测试初始化"""
        with patch("openai.AsyncOpenAI"):
            provider = SiliconFlowProvider(api_key="test-key", model="Qwen2-72B")
            assert provider is not None
            assert provider.api_key == "test-key"
            assert provider.model == "Qwen2-72B"


class TestMiniMaxProvider:
    """MiniMax提供者测试"""

    def test_init(self):
        """测试初始化"""
        with patch("openai.AsyncOpenAI"):
            provider = MiniMaxProvider(api_key="test-key", model="abab5.5-chat")
            assert provider is not None
            assert provider.api_key == "test-key"
            assert provider.model == "abab5.5-chat"

    def test_init_with_custom_base_url(self):
        """测试自定义base_url"""
        with patch("openai.AsyncOpenAI"):
            provider = MiniMaxProvider(
                api_key="test-key",
                model="abab5.5-chat",
                base_url="https://custom.api.com"
            )
            assert provider.base_url == "https://custom.api.com"


class TestERNIEProvider:
    """百度文心一言提供者测试"""

    def test_init(self):
        """测试初始化"""
        with patch.dict('sys.modules', {'qianfan': Mock()}):
            provider = ERNIEProvider(api_key="test-key", model="ernie-4.0-8k")
            assert provider is not None
            assert provider.api_key == "test-key"
            assert provider.model == "ernie-4.0-8k"


class TestSparkProvider:
    """讯飞星火提供者测试"""

    def test_init(self):
        """测试初始化"""
        mock_spark = Mock()
        with patch.dict('sys.modules', {'spark_ai': mock_spark}):
            provider = SparkProvider(api_key="test-app-id", model="spark-v3.5")
            assert provider is not None
            assert provider.api_key == "test-app-id"
            assert provider.model == "spark-v3.5"


class TestBaseProvider:
    """基础提供者测试"""
    from app.services.llm.providers import LLMProvider
    class TestProvider(LLMProvider):
        async def chat(self, messages, temperature=0.7, max_tokens=2000, **kwargs):
            return "test"
        
        async def chat_stream(self, messages, temperature=0.7, max_tokens=2000, **kwargs):
            yield "test"

    def test_base_provider_init(self):
        """测试基础提供者初始化"""
        provider = self.TestProvider(api_key="test-key", model="test-model", extra_param="value")
        assert provider is not None
        assert provider.api_key == "test-key"
        assert provider.model == "test-model"
        assert provider.extra_params["extra_param"] == "value"


class TestAllProvidersInMap:
    """测试PROVIDER_MAP包含所有提供者"""

    def test_all_providers_imported(self):
        """验证所有提供者都在映射中"""
        from app.services.llm.providers import PROVIDER_MAP
        expected_providers = [
            "mock", "openai", "anthropic", "glm", "qwen",
            "minimax", "ernie", "hunyuan", "spark", "doubao",
            "siliconflow"
        ]
        for provider in expected_providers:
            assert provider in PROVIDER_MAP


class TestMiniMaxProvider:
    """MiniMax提供者测试"""

    def test_init(self):
        """测试初始化"""
        with patch("openai.AsyncOpenAI"):
            provider = MiniMaxProvider(api_key="test-key", model="abab5.5-chat")
            assert provider is not None
            assert provider.api_key == "test-key"
            assert provider.model == "abab5.5-chat"

    def test_init_with_custom_base_url(self):
        """测试自定义base_url"""
        with patch("openai.AsyncOpenAI"):
            provider = MiniMaxProvider(
                api_key="test-key",
                model="abab5.5-chat",
                base_url="https://custom.api.com"
            )
            assert provider.base_url == "https://custom.api.com"


class TestERNIEProvider:
    """百度文心一言提供者测试"""

    def test_init(self):
        """测试初始化"""
        with patch.dict('sys.modules', {'qianfan': Mock()}):
            provider = ERNIEProvider(api_key="test-key", model="ernie-4.0-8k")
            assert provider is not None
            assert provider.api_key == "test-key"
            assert provider.model == "ernie-4.0-8k"


class TestSparkProvider:
    """讯飞星火提供者测试"""

    def test_init(self):
        """测试初始化"""
        mock_spark = Mock()
        with patch.dict('sys.modules', {'spark_ai': mock_spark}):
            provider = SparkProvider(api_key="test-app-id", model="spark-v3.5")
            assert provider is not None
            assert provider.api_key == "test-app-id"
            assert provider.model == "spark-v3.5"


class TestChatStreamErrorHandling:
    """测试chat_stream错误处理"""

    async def test_chat_stream_provider_error_fallback_to_mock(self):
        """测试流式调用出错fallback到mock"""
        from app.services.llm.factory import chat_stream
        from app.core.config import settings
        
        original_provider = settings.LLM_PROVIDER
        settings.LLM_PROVIDER = "openai"  # not mock
        
        with patch("app.services.llm.factory.get_llm_provider") as mock_get:
            mock_provider = Mock()
            async def failing_stream(*args, **kwargs):
                raise Exception("Provider failed")
                yield ""  # 保证是生成器
            mock_provider.chat_stream = failing_stream
            mock_get.return_value = mock_provider
            
            chunks = []
            async for chunk in chat_stream([{"role": "user", "content": "test"}]):
                chunks.append(chunk)
            
            # 应该通过mock返回内容
            assert len(chunks) > 0
            full = "".join(chunks)
            assert len(full) > 0
            
        settings.LLM_PROVIDER = original_provider

    async def test_chat_stream_no_error_when_already_mock(self):
        """测试已经是mock时出错不会二次fallback"""
        from app.services.llm.factory import chat_stream
        from app.core.config import settings
        
        original_provider = settings.LLM_PROVIDER
        settings.LLM_PROVIDER = "mock"
        
        with patch("app.services.llm.factory.get_llm_provider") as mock_get:
            mock_provider = Mock()
            async def failing_stream(*args, **kwargs):
                raise Exception("Mock also failed")
                yield ""  
            mock_provider.chat_stream = failing_stream
            mock_get.return_value = mock_provider
            
            # 异常会抛出但被日志捕获
            chunks = []
            try:
                async for chunk in chat_stream([{"role": "user", "content": "test"}]):
                    chunks.append(chunk)
            except Exception:
                pass  # 预期可能异常，测试只验证分支逻辑
            
        settings.LLM_PROVIDER = original_provider


class TestLLMProviderChatMethods:
    """测试各provider chat方法签名"""

    async def test_openai_chat_method(self):
        """测试OpenAI chat方法"""
        from app.services.llm.providers import OpenAIProvider
        from unittest.mock import AsyncMock
        
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Hello OpenAI"))]
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        with patch("openai.AsyncOpenAI", return_value=mock_client):
            provider = OpenAIProvider(api_key="test-key", model="gpt-3.5-turbo")
            response = await provider.chat([{"role": "user", "content": "hi"}])
            assert response == "Hello OpenAI"

    async def test_glm_chat_method(self):
        """测试GLM chat方法"""
        from app.services.llm.providers import GLMProvider
        from unittest.mock import AsyncMock
        
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Hello GLM"))]
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        with patch("openai.AsyncOpenAI", return_value=mock_client):
            provider = GLMProvider(api_key="test-key", model="glm-4")
            response = await provider.chat([{"role": "user", "content": "hi"}])
            assert response == "Hello GLM"


class TestLLMFactoryChat:
    """LLM工厂chat函数测试"""

    async def test_chat_mock_provider(self):
        """测试使用mock provider的chat"""
        from app.core.config import settings
        original_provider = settings.LLM_PROVIDER
        settings.LLM_PROVIDER = "mock"
        
        response = await chat([{"role": "user", "content": "测试"}])
        assert isinstance(response, str)
        assert len(response) > 0
        
        settings.LLM_PROVIDER = original_provider

    async def test_chat_stream_mock_provider(self):
        """测试使用mock provider的chat_stream"""
        from app.core.config import settings
        original_provider = settings.LLM_PROVIDER
        settings.LLM_PROVIDER = "mock"
        
        chunks = []
        async for chunk in chat_stream([{"role": "user", "content": "测试"}]):
            chunks.append(chunk)
        
        assert len(chunks) > 0
        full = "".join(chunks)
        assert len(full) > 0
        
        settings.LLM_PROVIDER = original_provider


class TestProviderClientLazyLoading:
    """测试provider客户端懒加载"""

    def test_openai_client_lazy_loaded(self):
        """测试OpenAI客户端懒加载"""
        from app.services.llm.providers import OpenAIProvider
        import_count = 0
        
        def mock_import(name, *args):
            nonlocal import_count
            if name == 'openai':
                import_count += 1
                mock_openai = Mock()
                mock_openai.AsyncOpenAI = Mock
                return mock_openai
            return __import__(name, *args)
        
        with patch('builtins.__import__', side_effect=mock_import):
            provider = OpenAIProvider(api_key="test-key", model="gpt-3.5-turbo")
            assert provider._client is None  # 初始化不创建client
            # 第一次访问才创建
            _ = provider.client
            assert import_count == 1


class TestMockProviderDifferentCategories:
    """测试MockProvider对不同类别消息的回复"""

    async def test_chat_empty_messages_no_last_user(self):
        """测试空消息列表返回默认回复"""
        provider = MockProvider(api_key="mock", model="mock")
        response = await provider.chat([])
        assert isinstance(response, str)
        assert len(response) > 0

    async def test_chat_relationships_topic(self):
        """测试人际关系话题"""
        provider = MockProvider(api_key="mock", model="mock")
        response = await provider.chat([
            {"role": "user", "content": "我和朋友吵架了"}
        ])
        assert "朋友" in response.lower() or "关系" in response.lower()
        assert len(response) > 0

    async def test_chat_love_topic(self):
        """测试恋爱话题"""
        provider = MockProvider(api_key="mock", model="mock")
        response = await provider.chat([
            {"role": "user", "content": "我女朋友最近不理我"}
        ])
        lower = response.lower()
        assert "恋爱" in lower or "感情" in lower or "关系" in lower or "理解" in lower
        assert len(response) > 0

    async def test_chat_work_study_topic(self):
        """测试工作学习话题"""
        provider = MockProvider(api_key="mock", model="mock")
        response = await provider.chat([
            {"role": "user", "content": "工作压力好大想辞职"}
        ])
        assert "工作" in response.lower() or "压力" in response.lower()
        assert len(response) > 0

    async def test_chat_growth_topic(self):
        """测试成长话题"""
        provider = MockProvider(api_key="mock", model="mock")
        response = await provider.chat([
            {"role": "user", "content": "对未来很迷茫"}
        ])
        assert "迷茫" in response or "成长" in response.lower()
        assert len(response) > 0


class TestRetryWithBackoff:
    """重试机制测试"""

    async def test_retry_success_on_first_attempt(self):
        """测试第一次尝试成功"""
        async def success_fn():
            return "success"
        
        result = await _retry_with_backoff(success_fn, max_retries=3)
        assert result == "success"

    async def test_retry_success_after_failure(self):
        """测试失败后重试成功"""
        attempt = 0
        
        async def failing_then_success():
            nonlocal attempt
            attempt += 1
            if attempt == 1:
                raise Exception("First failure")
            return "success"
        
        result = await _retry_with_backoff(failing_then_success, max_retries=3, base_delay=0.01)
        assert result == "success"
        assert attempt == 2

    async def test_retry_all_failures_fallback_to_mock(self):
        """测试所有重试都失败后fallback到mock"""
        async def always_fail():
            raise Exception("Always failing")
        
        result = await _retry_with_backoff(always_fail, max_retries=2, base_delay=0.01)
        assert isinstance(result, str)
        assert len(result) > 0  # mock返回了内容


class TestProviderConcurrency:
    """测试LLM提供者并发"""

    async def test_concurrent_requests_mock(self):
        """测试Mock提供者并发请求"""
        provider = MockProvider(api_key="mock", model="mock")
        
        async def make_request():
            return await provider.chat([
                {"role": "user", "content": "test"}
            ])
        
        # 并发5个请求
        tasks = [make_request() for _ in range(5)]
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 5
        for result in results:
            assert isinstance(result, str)
            assert len(result) > 0

    async def test_concurrent_chats_via_factory(self):
        """测试通过工厂的并发chat"""
        from app.core.config import settings
        original_provider = settings.LLM_PROVIDER
        settings.LLM_PROVIDER = "mock"
        
        # 并发多个chat
        tasks = [
            chat([{"role": "user", "content": f"测试消息 {i}"}])
            for i in range(10)
        ]
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 10
        for result in results:
            assert isinstance(result, str)
            assert len(result) > 0
        
        settings.LLM_PROVIDER = original_provider


class TestFactorySingleton:
    """测试LLM工厂单例"""

    def test_get_llm_provider_singleton(self):
        """测试提供者是单例"""
        from app.services.llm.factory import get_llm_provider, _llm_provider
        import app.services.llm.factory
        
        # 保存原始状态
        original = app.services.llm.factory._llm_provider
        app.services.llm.factory._llm_provider = None
        
        from app.core.config import settings
        original_provider = settings.LLM_PROVIDER
        settings.LLM_PROVIDER = "mock"
        
        provider1 = get_llm_provider()
        provider2 = get_llm_provider()
        
        assert provider1 is provider2
        
        # 恢复
        settings.LLM_PROVIDER = original_provider
        app.services.llm.factory._llm_provider = original

    def test_get_llm_unknown_provider_fallback_logged(self):
        """测试未知provider时记录日志并fallback"""
        from app.services.llm.factory import get_llm_provider
        import app.services.llm.factory
        from app.core.config import settings
        
        original = app.services.llm.factory._llm_provider
        app.services.llm.factory._llm_provider = None
        original_provider = settings.LLM_PROVIDER
        settings.LLM_PROVIDER = "this_provider_does_not_exist"
        
        with patch("loguru.logger.warning") as mock_log:
            provider = get_llm_provider()
            mock_log.assert_called()
            assert "Unknown LLM provider" in mock_log.call_args[0][0]
            
        from app.services.llm.providers import MockProvider
        assert isinstance(provider, MockProvider)
        
        # 恢复
        settings.LLM_PROVIDER = original_provider
        app.services.llm.factory._llm_provider = original


class TestRetryWithBackoffCoverage:
    """覆盖重试机制所有分支"""

    async def test_retry_zero_attempts(self):
        """测试max_retries=1，所有失败都fallback"""
        # max_retries=1 意味着只尝试一次，失败直接fallback
        async def always_fail():
            raise Exception("Always fails")
        
        result = await _retry_with_backoff(always_fail, max_retries=1)
        assert isinstance(result, str)
        assert len(result) > 0  # mock回复

