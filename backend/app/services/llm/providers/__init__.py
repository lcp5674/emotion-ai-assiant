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


class MockProvider(LLMProvider):
    """模拟大模型服务 (用于开发测试)"""

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """模拟回复"""
        # 获取最后一条用户消息
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break

        # 根据消息内容返回适当的模拟回复
        return self._generate_mock_response(user_message)

    async def chat_stream(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 2000, **kwargs):
        """模拟流式回复"""
        response = await self.chat(messages, temperature, max_tokens, **kwargs)
        for char in response:
            yield char

    def _generate_mock_response(self, user_message: str) -> str:
        """生成模拟回复"""
        message_lower = user_message.lower()

        # 情绪支持类回复
        if any(word in message_lower for word in ["难过", "伤心", "哭", "沮丧", "郁闷", "失落"]):
            return (
                "我能感受到你现在的难过和沮丧。 "
                "请记住，经历这些负面情绪是完全正常的。 "
                "你有没有想过，是什么事情让你感到这样呢？ "
                "如果愿意的话，可以和我聊聊，我把耳朵借给你。 "
                "无论发生什么，我都会在这里陪着你。"
            )

        # 焦虑压力类
        if any(word in message_lower for word in ["焦虑", "担心", "紧张", "害怕", "压力"]):
            return (
                "听起来你正在经历一些焦虑和压力。 "
                "当感到焦虑时，试着深呼吸几次，"
                "把你的注意力慢慢转移到当下的感受上。 "
                "你愿意告诉我是什么让你感到焦虑吗？ "
                "有时候，把心里的担忧说出来会好受一些。"
            )

        # 人际关系类
        if any(word in message_lower for word in ["朋友", "家人", "同事", "对象", "男朋友", "女朋友", "老公", "老婆", "父母"]):
            return (
                "人际关系的复杂让我们有时会感到困惑和疲惫。 "
                "每个人都有自己的想法和感受，"
                "理解与沟通是建立良好关系的关键。 "
                "你愿意具体说说发生了什么吗？ "
                "或许我们可以一起想想办法。"
            )

        # 恋爱相关
        if any(word in message_lower for word in ["恋爱", "喜欢", "表白", "追", "分手", "约会", "女朋友", "男朋友"]):
            return (
                "恋爱中的喜怒哀乐都是那么真实而美好。 "
                "在感情中，保持真诚和尊重是最重要的。 "
                "你愿意分享一些关于这段感情的故事吗？ "
                "无论结果如何，经历本身就是一种成长。"
            )

        # 自我成长类
        if any(word in message_lower for word in ["成长", "改变", "目标", "梦想", "迷茫", "困惑"]):
            return (
                "每个人都会在人生的不同阶段感到迷茫，"
                "这恰恰是自我探索的开始。 "
                "试着问问自己：什么对你来说真正重要？ "
                "你希望成为什么样的人？ "
                "一小步一小步地前行，你会找到属于自己的方向。"
            )

        # 工作学习类
        if any(word in message_lower for word in ["工作", "学习", "考试", "上班", "辞职", "创业"]):
            return (
                "工作或学习的压力确实让人感到疲惫。 "
                "记得照顾好自己的身心健康，"
                "适当休息和放松很重要。 "
                "你最近怎么样？有什么想吐槽的吗？ "
                "有时候倾诉也是很好的解压方式。"
            )

        # 默认温暖回复
        return (
            "谢谢你的分享。 "
            "我在这里用心倾听你的每一句话。 "
            "你最近生活中有什么开心的事情吗？ "
            "或者有什么想聊聊的？ "
            "无论是什么，我都在这里陪着你。"
        )


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
    "mock": MockProvider,
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