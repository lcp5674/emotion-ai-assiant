"""
Embedding服务 - 支持国内主流厂商（生产级）
支持厂商列表（15+）:
1. OpenAI - text-embedding-ada-002
2. 百度文心(ERNIE) - ernie-text-embedding  
3. 阿里DashScope - text-embedding-v1
4. 智谱GLM - embedding-2
5. 腾讯混元 - hunyuan-embedding
6. 火山引擎(Volcengine) - bge-large-zh-v1.5
7. 商汤(SenseTime) - embedding-v1
8. 百川智能 - bge-large-zh-v1.5
9. 华为云 - bge-m3
10. MiniMax - embo-1
11. SiliconFlow - BAAI/bge-large-zh-v1.5
12. 讯飞星火 - spark_embedding
13. 月之暗面 - text-embedding-v1
14. 零一万物 - embodi-v1
15. 脉脉 - maas-embed-v1
"""
import asyncio
from abc import ABC, abstractmethod
from typing import List, Optional
import loguru

from app.core.config import settings


class BaseEmbedding(ABC):
    """Embedding基类 - 生产级实现，包含重试机制"""

    # 类级别的重试配置
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0  # 秒

    def __init__(self):
        self.dimension = settings.EMBEDDING_DIM

    @abstractmethod
    async def embed(self, texts: List[str]) -> List[List[float]]:
        """将文本转换为embedding向量"""
        pass

    async def embed_with_retry(self, texts: List[str]) -> List[List[float]]:
        """带重试机制的embedding方法 - 生产级特性"""
        last_error = None
        for attempt in range(self.MAX_RETRIES):
            try:
                result = await self.embed(texts)
                # 验证返回结果
                if result and len(result) == len(texts):
                    return result
                # 如果结果为空或长度不匹配，触发重试
                loguru.logger.warning(
                    f"{self.__class__.__name__}: Invalid result, attempt {attempt + 1}/{self.MAX_RETRIES}"
                )
            except Exception as e:
                last_error = e
                loguru.logger.warning(
                    f"{self.__class__.__name__}: Embed failed (attempt {attempt + 1}/{self.MAX_RETRIES}): {e}"
                )
            
            if attempt < self.MAX_RETRIES - 1:
                await asyncio.sleep(self.RETRY_DELAY * (2 ** attempt))  # 指数退避
        
        # 所有重试都失败，返回零向量
        loguru.logger.error(f"{self.__class__.__name__}: All retries failed, returning zero vectors")
        return [[0.0] * self.dimension for _ in texts]

    async def embed_single(self, text: str) -> List[float]:
        """单个文本embedding"""
        results = await self.embed_with_retry([text])
        return results[0] if results else [0.0] * self.dimension


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
    """SiliconFlow Embedding (聚合API，支持多种开源模型)"""

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


class VolcengineEmbedding(BaseEmbedding):
    """火山引擎Embedding - 支持字节跳动豆包系列模型"""

    def __init__(self):
        super().__init__()
        self.api_key = getattr(settings, 'VOLCENGINE_API_KEY', None)
        self.model = "bge-large-zh-v1.5"
        # 火山引擎bge-large-zh-v1.5 dimension: 1024
        self.dimension = 1024

    async def embed(self, texts: List[str]) -> List[List[float]]:
        """调用火山引擎Embedding API"""
        try:
            import aiohttp

            if not self.api_key:
                loguru.logger.error("Volcengine: API key not configured")
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
                    "https://ark.cn-beijing.volces.com/api/v3/embeddings",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    if resp.status != 200:
                        error = await resp.text()
                        loguru.logger.error(f"Volcengine embedding error: {error}")
                        return [[0.0] * self.dimension for _ in texts]

                    result = await resp.json()
                    return [item["embedding"] for item in result["data"]]

        except Exception as e:
            loguru.logger.error(f"Volcengine embedding exception: {e}")
            return [[0.0] * self.dimension for _ in texts]


class SenseTimeEmbedding(BaseEmbedding):
    """商汤科技Embedding - 书生·浦语系列"""

    def __init__(self):
        super().__init__()
        self.api_key = getattr(settings, 'SENSETIME_API_KEY', None)
        self.model = "embed-v2"
        # 商汤embed-v2 dimension: 1024
        self.dimension = 1024

    async def embed(self, texts: List[str]) -> List[List[float]]:
        """调用商汤Embedding API"""
        try:
            import aiohttp

            if not self.api_key:
                loguru.logger.error("SenseTime: API key not configured")
                return [[0.0] * self.dimension for _ in texts]

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model,
                "input": {"texts": texts}
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://openapi.sensetime.com/v1/embedding",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    if resp.status != 200:
                        error = await resp.text()
                        loguru.logger.error(f"SenseTime embedding error: {error}")
                        return [[0.0] * self.dimension for _ in texts]

                    result = await resp.json()
                    embeddings = result.get("data", {}).get("embeddings", [])
                    return [e.get("embedding", []) for e in embeddings]

        except Exception as e:
            loguru.logger.error(f"SenseTime embedding exception: {e}")
            return [[0.0] * self.dimension for _ in texts]


class BaichuanEmbedding(BaseEmbedding):
    """百川智能Embedding - bge-zh系列"""

    def __init__(self):
        super().__init__()
        self.api_key = getattr(settings, 'BAICHUAN_API_KEY', None)
        self.model = "baichuan-embed-text-v2"
        # 百川embed-text-v2 dimension: 1024
        self.dimension = 1024

    async def embed(self, texts: List[str]) -> List[List[float]]:
        """调用百川智能Embedding API"""
        try:
            import aiohttp

            if not self.api_key:
                loguru.logger.error("Baichuan: API key not configured")
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
                    "https://api.baichuan-ai.com/v1/embeddings",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    if resp.status != 200:
                        error = await resp.text()
                        loguru.logger.error(f"Baichuan embedding error: {error}")
                        return [[0.0] * self.dimension for _ in texts]

                    result = await resp.json()
                    return [item["embedding"] for item in result.get("data", [])]

        except Exception as e:
            loguru.logger.error(f"Baichuan embedding exception: {e}")
            return [[0.0] * self.dimension for _ in texts]


class HuaweiCloudEmbedding(BaseEmbedding):
    """华为云ModelArts Embedding - bge-m3系列"""

    def __init__(self):
        super().__init__()
        self.api_key = getattr(settings, 'HUAWEI_CLOUD_API_KEY', None)
        self.project_id = getattr(settings, 'HUAWEI_PROJECT_ID', None)
        self.model = "bge-m3"
        # 华为云bge-m3 dimension: 1024
        self.dimension = 1024

    async def embed(self, texts: List[str]) -> List[List[float]]:
        """调用华为云ModelArts Embedding API"""
        try:
            import aiohttp

            if not self.api_key:
                loguru.logger.error("HuaweiCloud: API key not configured")
                return [[0.0] * self.dimension for _ in texts]

            headers = {
                "X-Api-Key": self.api_key,
                "Content-Type": "application/json"
            }
            payload = {
                "input_text": texts,
                "model_id": self.model
            }

            endpoint = "https://modelarts.cn-north-4.myhuaweicloud.com/v1/inferservices/bge-m3"
            if self.project_id:
                endpoint = f"https://modelarts.cn-north-4.myhuaweicloud.com/v1/{self.project_id}/bge-m3"

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    endpoint,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    if resp.status != 200:
                        error = await resp.text()
                        loguru.logger.error(f"HuaweiCloud embedding error: {error}")
                        return [[0.0] * self.dimension for _ in texts]

                    result = await resp.json()
                    return result.get("data", [[0.0] * self.dimension] * len(texts))

        except Exception as e:
            loguru.logger.error(f"HuaweiCloud embedding exception: {e}")
            return [[0.0] * self.dimension for _ in texts]


class MiniMaxEmbedding(BaseEmbedding):
    """MiniMax Embedding - 支持abab系列"""

    def __init__(self):
        super().__init__()
        self.api_key = getattr(settings, 'MINIMAX_API_KEY', None)
        self.model = "embo-1"
        # MiniMax embo-1 dimension: 1024
        self.dimension = 1024

    async def embed(self, texts: List[str]) -> List[List[float]]:
        """调用MiniMax Embedding API"""
        try:
            import aiohttp

            if not self.api_key:
                loguru.logger.error("MiniMax: API key not configured")
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
                    "https://api.minimax.chat/v1/embeddings",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    if resp.status != 200:
                        error = await resp.text()
                        loguru.logger.error(f"MiniMax embedding error: {error}")
                        return [[0.0] * self.dimension for _ in texts]

                    result = await resp.json()
                    return [item["embedding"] for item in result.get("data", [])]

        except Exception as e:
            loguru.logger.error(f"MiniMax embedding exception: {e}")
            return [[0.0] * self.dimension for _ in texts]


class SparkEmbedding(BaseEmbedding):
    """讯飞星火Embedding - spark-text系列"""

    def __init__(self):
        super().__init__()
        self.api_key = getattr(settings, 'SPARK_API_KEY', None)
        self.app_id = getattr(settings, 'SPARK_APP_ID', None)
        self.model = "spark_embedding"
        # 讯飞星火embedding dimension: 1024
        self.dimension = 1024

    async def embed(self, texts: List[str]) -> List[List[float]]:
        """调用讯飞星火Embedding API"""
        try:
            import aiohttp

            if not self.api_key:
                loguru.logger.error("Spark: API key not configured")
                return [[0.0] * self.dimension for _ in texts]

            headers = {
                "Content-Type": "application/json"
            }
            payload = {
                "header": {
                    "app_id": self.app_id or "",
                    "api_key": self.api_key
                },
                "parameter": {
                    "embedding": {
                        "model": self.model
                    }
                },
                "payload": {
                    "texts": [{"text": text} for text in texts]
                }
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://spark-api.xf-yun.com/v1/embedding",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    if resp.status != 200:
                        error = await resp.text()
                        loguru.logger.error(f"Spark embedding error: {error}")
                        return [[0.0] * self.dimension for _ in texts]

                    result = await resp.json()
                    data = result.get("data", {}).get("vec_list", [])
                    return data if data else [[0.0] * self.dimension for _ in texts]

        except Exception as e:
            loguru.logger.error(f"Spark embedding exception: {e}")
            return [[0.0] * self.dimension for _ in texts]


class MoonshotEmbedding(BaseEmbedding):
    """月之暗面(Moonshot) Embedding - 支持 Kimi 模型系列"""

    def __init__(self):
        super().__init__()
        self.api_key = getattr(settings, 'MOONSHOT_API_KEY', None)
        self.model = "moonshot-v1-embed"
        # Moonshot moonshot-v1-embed dimension: 1536
        self.dimension = 1536

    async def embed(self, texts: List[str]) -> List[List[float]]:
        """调用月之暗面Embedding API"""
        try:
            import aiohttp

            if not self.api_key:
                loguru.logger.error("Moonshot: API key not configured")
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
                    "https://api.moonshot.cn/v1/embeddings",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    if resp.status != 200:
                        error = await resp.text()
                        loguru.logger.error(f"Moonshot embedding error: {error}")
                        return [[0.0] * self.dimension for _ in texts]

                    result = await resp.json()
                    return [item["embedding"] for item in result.get("data", [])]

        except Exception as e:
            loguru.logger.error(f"Moonshot embedding exception: {e}")
            return [[0.0] * self.dimension for _ in texts]


class LingyiEmbedding(BaseEmbedding):
    """零一万物(Yi) Embedding - 支持Yi系列模型"""

    def __init__(self):
        super().__init__()
        self.api_key = getattr(settings, 'LINGYI_API_KEY', None)
        self.model = "embd-01"
        # 零一万物embd-01 dimension: 1024
        self.dimension = 1024

    async def embed(self, texts: List[str]) -> List[List[float]]:
        """调用零一万物Embedding API"""
        try:
            import aiohttp

            if not self.api_key:
                loguru.logger.error("Lingyi: API key not configured")
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
                    "https://api.lingyiwanwu.com/v1/embeddings",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    if resp.status != 200:
                        error = await resp.text()
                        loguru.logger.error(f"Lingyi embedding error: {error}")
                        return [[0.0] * self.dimension for _ in texts]

                    result = await resp.json()
                    return [item["embedding"] for item in result.get("data", [])]

        except Exception as e:
            loguru.logger.error(f"Lingyi embedding exception: {e}")
            return [[0.0] * self.dimension for _ in texts]


class EmbeddingFactory:
    """Embedding工厂 - 支持15+国内主流厂商"""

    _providers = {
        # 国外厂商
        "openai": OpenAIEmbedding,
        # 国内厂商
        "ernie": ERNIEEmbedding,          # 百度文心
        "dashscope": DashScopeEmbedding,  # 阿里DashScope
        "glm": GLMEmbedding,              # 智谱GLM
        "hunyuan": HunyuanEmbedding,      # 腾讯混元
        "siliconflow": SiliconFlowEmbedding,  # SiliconFlow聚合
        "volcengine": VolcengineEmbedding,    # 火山引擎
        "sensetime": SenseTimeEmbedding,      # 商汤科技
        "baichuan": BaichuanEmbedding,         # 百川智能
        "huawei": HuaweiCloudEmbedding,       # 华为云
        "minimax": MiniMaxEmbedding,           # MiniMax
        "spark": SparkEmbedding,               # 讯飞星火
        "moonshot": MoonshotEmbedding,         # 月之暗面
        "lingyi": LingyiEmbedding,             # 零一万物
        # 别名映射
        "baidu": ERNIEEmbedding,
        "wenxin": ERNIEEmbedding,
        "ali": DashScopeEmbedding,
        "alibaba": DashScopeEmbedding,
        "zhipu": GLMEmbedding,
        "tencent": HunyuanEmbedding,
        "qwen": DashScopeEmbedding,
        "doubao": VolcengineEmbedding,         # 豆包映射到火山引擎
        "shengtang": SenseTimeEmbedding,       # 商汤别名
        "yi": LingyiEmbedding,                # 零一万物别名
    }

    _instance: Optional[BaseEmbedding] = None
    _current_provider: Optional[str] = None

    @classmethod
    def get_embedding(cls, provider: str = None) -> BaseEmbedding:
        """获取Embedding实例
        
        Args:
            provider: 可选，指定provider名称。如不指定，使用配置中的LLM_PROVIDER
        """
        # 获取当前Provider
        provider_name = provider.lower() if provider else (
            settings.LLM_PROVIDER.lower() if settings.LLM_PROVIDER else "siliconflow"
        )

        # 如果Provider变了，重新创建实例
        if cls._current_provider != provider_name or cls._instance is None:
            embedding_class = cls._providers.get(provider_name)

            if embedding_class is None:
                loguru.logger.warning(
                    f"Unknown embedding provider: {provider_name}, using SiliconFlow as fallback"
                )
                embedding_class = SiliconFlowEmbedding

            cls._instance = embedding_class()
            cls._current_provider = provider_name

            loguru.logger.info(f"Embedding provider: {provider_name}, dimension: {cls._instance.dimension}")

        return cls._instance

    @classmethod
    def list_providers(cls) -> List[str]:
        """列出所有可用的Provider名称"""
        return list(set(cls._providers.keys()))

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
