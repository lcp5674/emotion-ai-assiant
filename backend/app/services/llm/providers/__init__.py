"""
大模型服务接口定义 - 支持15+国内主流厂商
Provider列表:
1. OpenAI - GPT系列
2. Anthropic - Claude系列
3. 智谱GLM - glm-4
4. 阿里通义千问 - qwen系列
5. 百度文心一言 - ernie系列
6. 腾讯混元 - hunyuan系列
7. 讯飞星火 - spark系列
8. 字节豆包 - doubao系列
9. 硅基流动 - SiliconFlow聚合
10. 火山引擎 - volcengine系列
11. 商汤科技 - SenseChat系列
12. 百川智能 - baichuan系列
13. 华为云 -盘古系列
14. 月之暗面 - moonshot/kimi系列
15. 零一万物 - Yi系列
16. MiniMax - abab系列
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import loguru


class LLMProvider(ABC):
    """大模型提供商基类 - 生产级实现"""

    def __init__(self, api_key: str, model: str, **kwargs):
        self.api_key = api_key
        self.model = model
        self.extra_params = kwargs

    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """发送聊天请求，返回AI回复"""
        pass

    @abstractmethod
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ):
        """流式聊天"""
        pass

    def get_model_info(self) -> Dict[str, str]:
        """获取模型信息"""
        return {
            "provider": self.__class__.__name__,
            "model": self.model
        }


class OpenAIProvider(LLMProvider):
    """OpenAI GPT Provider"""

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", base_url: str = "https://api.openai.com/v1", **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.base_url = base_url
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
        return self._client

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return response.choices[0].message.content

    async def chat_stream(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 2000, **kwargs):
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs
        )
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class AnthropicProvider(LLMProvider):
    """Anthropic Claude Provider"""

    def __init__(self, api_key: str, model: str = "claude-3-haiku-20240307", base_url: str = None, **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.base_url = base_url
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from anthropic import AsyncAnthropic
            if self.base_url:
                self._client = AsyncAnthropic(api_key=self.api_key, base_url=self.base_url)
            else:
                self._client = AsyncAnthropic(api_key=self.api_key)
        return self._client

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        system_message = ""
        anthropic_messages = []
        for msg in messages:
            if msg.get("role") == "system":
                system_message = msg.get("content", "")
            else:
                anthropic_messages.append(msg)

        response = await self.client.messages.create(
            model=self.model,
            system=system_message,
            messages=anthropic_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return response.content[0].text

    async def chat_stream(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 2000, **kwargs):
        system_message = ""
        anthropic_messages = []
        for msg in messages:
            if msg.get("role") == "system":
                system_message = msg.get("content", "")
            else:
                anthropic_messages.append(msg)

        async with self.client.messages.stream(
            model=self.model,
            system=system_message,
            messages=anthropic_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        ) as stream:
            async for text in stream.text_stream:
                yield text


class GLMProvider(LLMProvider):
    """智谱GLM Provider"""

    def __init__(self, api_key: str, model: str = "glm-4", base_url: str = None, **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.base_url = base_url or "https://open.bigmodel.cn/api/paas/v4/"
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        return self._client

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return response.choices[0].message.content

    async def chat_stream(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 2000, **kwargs):
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs
        )
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class QwenProvider(LLMProvider):
    """阿里通义千问 Provider"""

    def __init__(self, api_key: str, model: str = "qwen-turbo", base_url: str = None, **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.base_url = base_url or "https://dashscope.aliyuncs.com/compatible-mode/v1"
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        return self._client

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return response.choices[0].message.content

    async def chat_stream(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 2000, **kwargs):
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs
        )
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class MiniMaxProvider(LLMProvider):
    """MiniMax Provider"""

    def __init__(self, api_key: str, model: str = "abab5.5-chat", base_url: str = None, **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.base_url = base_url or "https://api.minimax.chat/v1"
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        return self._client

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return response.choices[0].message.content

    async def chat_stream(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 2000, **kwargs):
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs
        )
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class ERNIEProvider(LLMProvider):
    """百度文心一言 Provider"""

    def __init__(self, api_key: str, model: str = "ernie-4.0-8k", base_url: str = None, **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.base_url = base_url
        self._client = None

    @property
    def client(self):
        if self._client is None:
            try:
                from qianfan import AsyncChatCompletion
            except ImportError:
                raise ImportError("请安装 qianfan: pip install qianfan")
            if self.base_url:
                self._client = AsyncChatCompletion(ak=self.api_key, model=self.model, base_url=self.base_url)
            else:
                self._client = AsyncChatCompletion(ak=self.api_key, model=self.model)
        return self._client

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        response = await self.client.chat(
            messages=messages,
            temperature=temperature,
            max_output_tokens=max_tokens,
            **kwargs
        )
        return response.body.get("result", "")

    async def chat_stream(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 2000, **kwargs):
        async for chunk in self.client.chat(
            messages=messages,
            temperature=temperature,
            max_output_tokens=max_tokens,
            stream=True,
            **kwargs
        ):
            if chunk.body.get("result"):
                yield chunk.body.get("result")


class HunyuanProvider(LLMProvider):
    """腾讯混元 Provider"""

    def __init__(self, api_key: str, model: str = "hunyuan-pro", base_url: str = None, **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.base_url = base_url or "https://hunyuan.cloud.tencent.com/v1"
        self._client = None

    @property
    def client(self):
        if self._client is None:
            try:
                from openai import AsyncOpenAI
            except ImportError:
                raise ImportError("请安装 openai: pip install openai")
            self._client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        return self._client

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return response.choices[0].message.content

    async def chat_stream(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 2000, **kwargs):
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs
        )
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class SparkProvider(LLMProvider):
    """讯飞星火认知大模型 Provider"""

    def __init__(self, api_key: str, model: str = "spark-v3.5", **kwargs):
        super().__init__(api_key, model, **kwargs)
        self._client = None

    @property
    def client(self):
        if self._client is None:
            try:
                import spark_ai
            except ImportError:
                raise ImportError("请安装 spark-ai: pip install spark-ai")
            self._client = spark_ai
        return self._client

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        last_msg = messages[-1].get("content", "") if messages else ""
        response = await self.client.ChatCompletion().acreate(
            app_id=self.api_key,
            query=last_msg,
            model=self.model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.get("data", {}).get("content", "")

    async def chat_stream(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 2000, **kwargs):
        last_msg = messages[-1].get("content", "") if messages else ""
        async for chunk in self.client.ChatCompletion().acreate(
            app_id=self.api_key,
            query=last_msg,
            model=self.model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        ):
            if chunk.get("data", {}).get("content"):
                yield chunk.get("data", {}).get("content")


class DoubaoProvider(LLMProvider):
    """字节跳动豆包 Provider"""

    def __init__(self, api_key: str, model: str = "doubao-pro-32k", base_url: str = None, **kwargs):
        super().__init__(api_key, model, **kwargs)
        # 去除末尾的 /chat/completions，避免重复拼接
        self.base_url = (base_url or "https://ark.cn-beijing.volces.com/api/v3").rstrip('/')
        if self.base_url.endswith("/chat/completions"):
            self.base_url = self.base_url[:-len("/chat/completions")]
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        return self._client

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return response.choices[0].message.content

    async def chat_stream(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 2000, **kwargs):
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs
        )
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class SiliconFlowProvider(LLMProvider):
    """硅基流动 Provider (聚合多种模型)"""

    def __init__(self, api_key: str, model: str = "Qwen/Qwen2-72B-Instruct", base_url: str = None, **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.base_url = base_url or "https://api.siliconflow.cn/v1"
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        return self._client

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return response.choices[0].message.content

    async def chat_stream(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 2000, **kwargs):
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs
        )
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class VolcengineProvider(LLMProvider):
    """火山引擎LLM Provider - 字节跳动云服务平台"""

    def __init__(self, api_key: str, model: str = "doubao-pro-32k", base_url: str = None, **kwargs):
        super().__init__(api_key, model, **kwargs)
        # 去除末尾的 /chat/completions，避免重复拼接
        self.base_url = (base_url or "https://ark.cn-beijing.volces.com/api/v3").rstrip('/')
        if self.base_url.endswith("/chat/completions"):
            self.base_url = self.base_url[:-len("/chat/completions")]
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        return self._client

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return response.choices[0].message.content

    async def chat_stream(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 2000, **kwargs):
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs
        )
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class SenseTimeProvider(LLMProvider):
    """商汤科技 SenseChat Provider"""

    def __init__(self, api_key: str, model: str = "sensechat-5", base_url: str = None, **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.base_url = base_url or "https://openapi.sensetime.com/v1"
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        return self._client

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return response.choices[0].message.content

    async def chat_stream(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 2000, **kwargs):
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs
        )
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class BaichuanProvider(LLMProvider):
    """百川智能 Provider"""

    def __init__(self, api_key: str, model: str = "baichuan4", base_url: str = None, **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.base_url = base_url or "https://api.baichuan-ai.com/v1"
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        return self._client

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return response.choices[0].message.content

    async def chat_stream(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 2000, **kwargs):
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs
        )
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class MoonshotProvider(LLMProvider):
    """月之暗面 Kimi Provider"""

    def __init__(self, api_key: str, model: str = "moonshot-v1-8k", base_url: str = None, **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.base_url = base_url or "https://api.moonshot.cn/v1"
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        return self._client

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return response.choices[0].message.content

    async def chat_stream(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 2000, **kwargs):
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs
        )
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class LingyiProvider(LLMProvider):
    """零一万物 Yi Provider"""

    def __init__(self, api_key: str, model: str = "yi-medium", base_url: str = None, **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.base_url = base_url or "https://api.lingyiwanwu.com/v1"
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        return self._client

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return response.choices[0].message.content

    async def chat_stream(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 2000, **kwargs):
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs
        )
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class MockProvider(LLMProvider):
    """Mock Provider - 用于测试和开发"""

    def __init__(self, api_key: str = "", model: str = "mock", **kwargs):
        super().__init__(api_key, model, **kwargs)

    async def chat(
        self,
        messages: list,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        last_msg = messages[-1].get("content", "") if messages else ""
        return f"[Mock回复] 收到您的消息: {last_msg[:50]}... 这是一个模拟回复。"

    async def chat_stream(self, messages: list, temperature: float = 0.7, max_tokens: int = 2000, **kwargs):
        last_msg = messages[-1].get("content", "") if messages else ""
        response = f"[Mock回复] 收到您的消息: {last_msg[:50]}... 这是一个模拟回复。"
        for char in response:
            yield char


class CustomProvider(LLMProvider):
    """自定义LLM Provider - 兼容OpenAI协议

    支持任何提供OpenAI兼容API的服务商，包括：
    - 自建的大模型服务
    - 开源模型部署（如vLLM、Ollama等）
    - 其他兼容OpenAI API的服务商
    """

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", base_url: str = "https://api.openai.com/v1", **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.base_url = base_url.rstrip('/')
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        return self._client

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return response.choices[0].message.content

    async def chat_stream(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 2000, **kwargs):
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs
        )
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


# Provider映射 - 15+国内主流厂商
PROVIDER_MAP = {
    # Mock
    "mock": MockProvider,
    # 国外
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    # 国内主流厂商
    "glm": GLMProvider,               # 智谱GLM
    "qwen": QwenProvider,             # 阿里通义千问
    "minimax": MiniMaxProvider,        # MiniMax
    "ernie": ERNIEProvider,            # 百度文心
    "hunyuan": HunyuanProvider,        # 腾讯混元
    "spark": SparkProvider,            # 讯飞星火
    "doubao": DoubaoProvider,           # 字节豆包
    "siliconflow": SiliconFlowProvider, # SiliconFlow聚合
    "volcengine": VolcengineProvider,   # 火山引擎
    "sensetime": SenseTimeProvider,     # 商汤科技
    "baichuan": BaichuanProvider,       # 百川智能
    "moonshot": MoonshotProvider,       # 月之暗面
    "lingyi": LingyiProvider,           # 零一万物
    # 自定义Provider（兼容OpenAI协议）
    "custom": CustomProvider,
}