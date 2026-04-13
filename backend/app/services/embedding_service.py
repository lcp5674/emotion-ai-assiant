"""
Embedding服务 - 支持国内主流厂商
支持: OpenAI, 百度文心(ERNIE), 阿里DashScope, 智谱GLM, 腾讯混元
"""
from abc import ABC, abstractmethod
from typing import List, Optional
import loguru
import json

from app.core.config import settings


class BaseEmbedding(ABC):
    """Embedding基类"""

    def __init__(self):
        self.dimension = settings.EMBEDDING_DIM

    @abstractmethod
    async def embed(self, texts: List[str]) -> List[List[float]]:
        """将文本转换为embedding向量"""
        pass

    async def embed_single(self, text: str) -> List[float]:
        """单个文本embedding"""
        results = await self.embed([text])
        return results[0] if results else []


class OpenAIEmbedding(BaseEmbedding):
    """OpenAI Embedding"""

    def __init__(self):
        super().__init__()
        self.api_key = settings.OPENAI_API_KEY
        self.base_url = settings.OPENAI_BASE_URL
        self.model = "text-embedding-ada-002"
        self.dimension = 1536

    async def embed(self, texts: List[str]) -> List[List[float]]:
        try:
            import aiohttp

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "input": texts,
                "model": self.model
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/embeddings",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    if resp.status != 200:
                        error = await resp.text()
                        loguru.logger.error(f"OpenAI embedding error: {error}")
                        return [[0.0] * self.dimension for _ in texts]

                    result = await resp.json()
                    return [item["embedding"] for item in result["data"]]

        except Exception as e:
            loguru.logger.error(f"OpenAI embedding exception: {e}")
            return [[0.0] * self.dimension for _ in texts]


class ERNIEEmbedding(BaseEmbedding):
    """百度文心Embedding"""

    def __init__(self):
        super().__init__()
        self.api_key = settings.ERNIE_API_KEY
        self.model = "ernie-text-embedding"
        # ERNIE embedding dimension: 384/768/1024
        self.dimension = 768

    async def embed(self, texts: List[str]) -> List[List[float]]:
        try:
            import aiohttp

            # 百度文心需要AK/SK换取access_token
            access_token = await self._get_access_token()
            if not access_token:
                loguru.logger.error("ERNIE: Failed to get access token")
                return [[0.0] * self.dimension for _ in texts]

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            payload = {
                "input": texts,
                "model": self.model
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://aip.baidubce.com/rpc/2.0/ai-custom/v1/wenxinworkshop/embeddings/embedding-v1",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    if resp.status != 200:
                        error = await resp.text()
                        loguru.logger.error(f"ERNIE embedding error: {error}")
                        return [[0.0] * self.dimension for _ in texts]

                    result = await resp.json()
                    return [item["embedding"] for item in result["data"]]

        except Exception as e:
            loguru.logger.error(f"ERNIE embedding exception: {e}")
            return [[0.0] * self.dimension for _ in texts]

    async def _get_access_token(self) -> Optional[str]:
        """获取百度Access Token"""
        try:
            import aiohttp

            # 从AK/SK获取Access Token
            # 格式: AK=xxx;SK=xxx
            if not self.api_key or ";" not in self.api_key:
                return None

            ak = self.api_key.split(";")[0].replace("AK=", "")
            sk = self.api_key.split(";")[1].replace("SK=", "")

            payload = {
                "grant_type": "client_credentials",
                "client_id": ak,
                "client_secret": sk
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://aip.baidubce.com/oauth/2.0/token",
                    params=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        return result.get("access_token")
                    return None

        except Exception as e:
            loguru.logger.error(f"ERNIE get access token error: {e}")
            return None


class DashScopeEmbedding(BaseEmbedding):
    """阿里云DashScope Embedding (text-embedding-v1)"""

    def __init__(self):
        super().__init__()
        self.api_key = getattr(settings, 'DASHSCOPE_API_KEY', None) or getattr(settings, 'QWEN_API_KEY', None)
        self.model = "text-embedding-v1"
        # DashScope text-embedding-v1 dimension: 1536
        self.dimension = 1536

    async def embed(self, texts: List[str]) -> List[List[float]]:
        try:
            import aiohttp

            if not self.api_key:
                loguru.logger.error("DashScope: API key not configured")
                return [[0.0] * self.dimension for _ in texts]

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "input": {"texts": texts},
                "model": self.model
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://dashscope.aliyuncs.com/api/v1/services/embeddings/text-embedding/text-embedding",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    if resp.status != 200:
                        error = await resp.text()
                        loguru.logger.error(f"DashScope embedding error: {error}")
                        return [[0.0] * self.dimension for _ in texts]

                    result = await resp.json()
                    embeddings = result.get("output", {}).get("embeddings", [])
                    return [e.get("embedding", []) for e in embeddings]

        except Exception as e:
            loguru.logger.error(f"DashScope embedding exception: {e}")
            return [[0.0] * self.dimension for _ in texts]


class GLMEmbedding(BaseEmbedding):
    """智谱GLM Embedding"""

    def __init__(self):
        super().__init__()
        self.api_key = settings.GLM_API_KEY
        self.model = "embedding-2"
        # GLM embedding dimension: 1024
        self.dimension = 1024

    async def embed(self, texts: List[str]) -> List[List[float]]:
        try:
            import aiohttp

            if not self.api_key:
                loguru.logger.error("GLM: API key not configured")
                return [[0.0] * self.dimension for _ in texts]

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            # 批量处理
            all_embeddings = []
            batch_size = 10

            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                payload = {
                    "model": self.model,
                    "input": batch
                }

                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        "https://open.bigmodel.cn/api/paas/v4/embeddings",
                        headers=headers,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as resp:
                        if resp.status != 200:
                            error = await resp.text()
                            loguru.logger.error(f"GLM embedding error: {error}")
                            all_embeddings.extend([[0.0] * self.dimension for _ in batch])
                            continue

                        result = await resp.json()
                        for item in result.get("data", []):
                            all_embeddings.append(item.get("embedding", []))

            return all_embeddings

        except Exception as e:
            loguru.logger.error(f"GLM embedding exception: {e}")
            return [[0.0] * self.dimension for _ in texts]


class HunyuanEmbedding(BaseEmbedding):
    """腾讯混元Embedding"""

    def __init__(self):
        super().__init__()
        self.api_key = settings.HUNYUAN_API_KEY
        self.model = "hunyuan-embedding"
        # 混元 embedding dimension: 1024
        self.dimension = 1024

    async def embed(self, texts: List[str]) -> List[List[float]]:
        try:
            import aiohttp
            import time

            if not self.api_key:
                loguru.logger.error("Hunyuan: API key not configured")
                return [[0.0] * self.dimension for _ in texts]

            # 腾讯云需要签名，这里简化处理使用固定密钥
            # 生产环境应使用腾讯云SDK进行签名
            headers = {
                "Content-Type": "application/json"
            }

            all_embeddings = []
            for text in texts:
                payload = {
                    "Input": text,
                    "Model": self.model
                }

                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        "https://hunyuan.tencentcloudapi.com",
                        headers=headers,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as resp:
                        if resp.status != 200:
                            error = await resp.text()
                            loguru.logger.warning(f"Hunyuan embedding error: {error}")
                            all_embeddings.append([0.0] * self.dimension)
                            continue

                        result = await resp.json()
                        embedding = result.get("Response", {}).get("Embedding", [])
                        if embedding:
                            all_embeddings.append(embedding)
                        else:
                            all_embeddings.append([0.0] * self.dimension)

            return all_embeddings

        except Exception as e:
            loguru.logger.error(f"Hunyuan embedding exception: {e}")
            return [[0.0] * self.dimension for _ in texts]


class SiliconFlowEmbedding(BaseEmbedding):
    """SiliconFlow Embedding (聚合API)"""

    def __init__(self):
        super().__init__()
        self.api_key = settings.SILICONFLOW_API_KEY
        self.model = "BAAI/bge-large-zh-v1.5"  # 中文优化模型
        # BAAI/bge-large-zh-v1.5 dimension: 1024
        self.dimension = 1024

    async def embed(self, texts: List[str]) -> List[List[float]]:
        try:
            import aiohttp

            if not self.api_key:
                loguru.logger.error("SiliconFlow: API key not configured")
                return [[0.0] * self.dimension for _ in texts]

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model,
                "input": texts
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.siliconflow.cn/v1/embeddings",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    if resp.status != 200:
                        error = await resp.text()
                        loguru.logger.error(f"SiliconFlow embedding error: {error}")
                        return [[0.0] * self.dimension for _ in texts]

                    result = await resp.json()
                    return [item["embedding"] for item in result["data"]]

        except Exception as e:
            loguru.logger.error(f"SiliconFlow embedding exception: {e}")
            return [[0.0] * self.dimension for _ in texts]


class EmbeddingFactory:
    """Embedding工厂"""

    _providers = {
        "openai": OpenAIEmbedding,
        "ernie": ERNIEEmbedding,
        "dashscope": DashScopeEmbedding,
        "glm": GLMEmbedding,
        "hunyuan": HunyuanEmbedding,
        "siliconflow": SiliconFlowEmbedding,
        # 别名映射
        "baidu": ERNIEEmbedding,
        "wenxin": ERNIEEmbedding,
        "ali": DashScopeEmbedding,
        "alibaba": DashScopeEmbedding,
        "zhipu": GLMEmbedding,
        "tencent": HunyuanEmbedding,
        "qwen": DashScopeEmbedding,
    }

    _instance: Optional[BaseEmbedding] = None
    _current_provider: Optional[str] = None

    @classmethod
    def get_embedding(cls) -> BaseEmbedding:
        """获取Embedding实例"""
        # 获取当前Provider
        provider = settings.LLM_PROVIDER.lower() if settings.LLM_PROVIDER else "siliconflow"

        # 如果Provider变了，重新创建实例
        if cls._current_provider != provider or cls._instance is None:
            embedding_class = cls._providers.get(provider)

            if embedding_class is None:
                loguru.logger.warning(
                    f"Unknown embedding provider: {provider}, using SiliconFlow as fallback"
                )
                embedding_class = SiliconFlowEmbedding

            cls._instance = embedding_class()
            cls._current_provider = provider

            loguru.logger.info(f"Embedding provider: {provider}, dimension: {cls._instance.dimension}")

        return cls._instance

    @classmethod
    async def embed_texts(cls, texts: List[str]) -> List[List[float]]:
        """快速embedding方法"""
        embedding = cls.get_embedding()
        return await embedding.embed(texts)

    @classmethod
    async def embed_text(cls, text: str) -> List[float]:
        """快速单个文本embedding方法"""
        embedding = cls.get_embedding()
        return await embedding.embed_single(text)

    @classmethod
    def get_dimension(cls) -> int:
        """获取当前embedding维度"""
        embedding = cls.get_embedding()
        return embedding.dimension


# 便捷函数
async def embed_texts(texts: List[str]) -> List[List[float]]:
    """将文本列表转换为embedding向量"""
    return await EmbeddingFactory.embed_texts(texts)


async def embed_text(text: str) -> List[float]:
    """将单个文本转换为embedding向量"""
    return await EmbeddingFactory.embed_text(text)


def get_embedding_dimension() -> int:
    """获取embedding维度"""
    return EmbeddingFactory.get_dimension()
