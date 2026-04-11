"""
LLM服务工厂和提供者单元测试
"""
import pytest
import asyncio
from unittest.mock import Mock, patch

from app.services.llm.factory import get_llm_provider, chat, chat_stream, _retry_with_backoff
from app.services.llm.providers import LLMProvider, MockProvider, OpenAIProvider, AnthropicProvider
from app.services.llm.providers import GLMProvider, QwenProvider, DoubaoProvider, HunyuanProvider, SiliconFlowProvider
from app.core.config import settings


class TestLLMFactory:
    """LLM工厂测试"""

    def test_get_provider_mock(self):
        """测试获取mock提供者"""
        from app.core.config import settings
        original_provider = settings.LLM_PROVIDER
        settings.LLM_PROVIDER = "mock"
        
        provider = get_llm_provider()
        assert isinstance(provider, MockProvider)
        
        settings.LLM_PROVIDER = original_provider

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
        settings.LLM_PROVIDER = "unknown_provider"
        
        provider = get_llm_provider()
        assert isinstance(provider, MockProvider)
        
        settings.LLM_PROVIDER = original_provider

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
