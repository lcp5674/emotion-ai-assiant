"""
大模型服务接口定义
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List


class LLMProvider(ABC):
    """大模型提供商基类"""

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
        # 转换消息格式
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
        self.base_url = base_url or "https://ark.cn-beijing.volces.com/api/v3"
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


# Provider映射
PROVIDER_MAP = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "glm": GLMProvider,
    "qwen": QwenProvider,
    "minimax": MiniMaxProvider,
    "ernie": ERNIEProvider,
    "hunyuan": HunyuanProvider,
    "spark": SparkProvider,
    "doubao": DoubaoProvider,
    "siliconflow": SiliconFlowProvider,
}