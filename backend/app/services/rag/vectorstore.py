"""
RAG向量存储服务 - 使用真实Embedding模型
"""
from typing import Optional, List, Dict, Any
import loguru

from app.core.config import settings


class VectorStore:
    """向量存储基类"""

    def __init__(self):
        from app.services.embedding_service import EmbeddingFactory
        self.embedding_dim = EmbeddingFactory.get_dimension()
        self._embedding_service = None

    async def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """获取文本embeddings - 使用真实Embedding服务"""
        if self._embedding_service is None:
            from app.services.embedding_service import EmbeddingFactory
            self._embedding_service = EmbeddingFactory.get_embedding()
        return await self._embedding_service.embed(texts)

    async def add_texts(self, texts: List[str], metadatas: Optional[List[Dict]] = None) -> List[str]:
        """添加文本到向量库"""
        raise NotImplementedError

    async def similarity_search(self, query: str, top_k: int = 5, filter: Optional[Dict] = None) -> List[Dict]:
        """相似度搜索"""
        raise NotImplementedError

    async def delete(self, ids: List[str]) -> None:
        """删除向量"""
        raise NotImplementedError


class MilvusStore(VectorStore):
    """Milvus向量存储"""

    def __init__(self):
        super().__init__()
        self.client = None
        self.collection = None

    async def _get_client(self):
        if self.client is None:
            from pymilvus import connections
            connections.connect(
                host=settings.MILVUS_HOST,
                port=settings.MILVUS_PORT,
            )
            self.client = connections
        return self.client

    async def add_texts(self, texts: List[str], metadatas: Optional[List[Dict]] = None) -> List[str]:
        """添加文本到Milvus"""
        try:
            from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility

            # 连接
            await self._get_client()

            # 获取或创建collection
            collection_name = settings.MILVUS_COLLECTION
            if not utility.has_collection(collection_name):
                # 创建collection
                fields = [
                    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
                    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.embedding_dim),
                ]
                schema = CollectionSchema(fields=fields, description="Emotion knowledge base")
                collection = Collection(name=collection_name, schema=schema)

                # 创建索引
                index_params = {
                    "metric_type": "L2",
                    "index_type": "IVF_FLAT",
                    "params": {"nlist": 128}
                }
                collection.create_index(field_name="embedding", index_params=index_params)
            else:
                collection = Collection(name=collection_name)

            # 使用真实Embedding服务生成向量
            embeddings = await self._get_embeddings(texts)

            # 插入数据
            data = [texts, embeddings]
            if metadatas:
                # 添加metadata字段
                metadata_dict = {}
                for key in metadatas[0].keys():
                    metadata_dict[key] = [m.get(key, "") for m in metadatas]
                data.append(metadata_dict["category"])

            ids = collection.insert(data)
            collection.flush()

            loguru.logger.info(f"Milvus: Added {len(texts)} texts, dimension: {self.embedding_dim}")
            return [str(id) for id in ids.primary_keys]

        except Exception as e:
            loguru.logger.error(f"Milvus add_texts error: {e}")
            return []

    async def similarity_search(self, query: str, top_k: int = 5, filter: Optional[Dict] = None) -> List[Dict]:
        """Milvus相似度搜索"""
        try:
            from pymilvus import connections, Collection

            await self._get_client()

            collection = Collection(name=settings.MILVUS_COLLECTION)
            collection.load()

            # 使用真实Embedding服务生成query向量
            query_embedding = (await self._get_embeddings([query]))[0]

            # 搜索
            search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
            results = collection.search(
                data=[query_embedding],
                anns_field="embedding",
                param=search_params,
                limit=top_k,
                output_fields=["text", "category"]
            )

            # 整理结果
            docs = []
            for hits in results:
                for hit in hits:
                    docs.append({
                        "id": str(hit.id),
                        "text": hit.entity.get("text"),
                        "category": hit.entity.get("category"),
                        "distance": hit.distance,
                    })

            return docs

        except Exception as e:
            loguru.logger.error(f"Milvus similarity_search error: {e}")
            return []

    async def delete(self, ids: List[str]) -> None:
        """删除向量"""
        try:
            from pymilvus import Collection
            collection = Collection(name=settings.MILVUS_COLLECTION)
            # Milvus删除需要使用delete_expr
            for id_str in ids:
                collection.delete(f"id == {id_str}")
            collection.flush()
        except Exception as e:
            loguru.logger.error(f"Milvus delete error: {e}")


class QdrantStore(VectorStore):
    """Qdrant向量存储"""

    def __init__(self):
        super().__init__()
        self.client = None

    async def _get_client(self):
        if self.client is None:
            from qdrant_client import QdrantClient
            self.client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
        return self.client

    async def add_texts(self, texts: List[str], metadatas: Optional[List[Dict]] = None) -> List[str]:
        """添加文本到Qdrant"""
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import Distance, VectorParams, PointStruct, Payload

            client = await self._get_client()

            # 确保collection存在
            collection_name = settings.QDRANT_COLLECTION
            collections = client.get_collections().collections
            if not any(c.name == collection_name for c in collections):
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=self.embedding_dim, distance=Distance.COSINE),
                )

            # 使用真实Embedding服务生成向量
            embeddings = await self._get_embeddings(texts)

            # 构建points
            points = []
            for i, (text, embedding) in enumerate(zip(texts, embeddings)):
                payload = {"text": text}
                if metadatas and i < len(metadatas):
                    payload.update(metadatas[i])

                points.append(PointStruct(
                    id=i,
                    vector=embedding,
                    payload=payload
                ))

            # 插入
            client.upsert(collection_name=collection_name, points=points)

            loguru.logger.info(f"Qdrant: Added {len(texts)} texts, dimension: {self.embedding_dim}")
            return [str(i) for i in range(len(texts))]

        except Exception as e:
            loguru.logger.error(f"Qdrant add_texts error: {e}")
            return []

    async def similarity_search(self, query: str, top_k: int = 5, filter: Optional[Dict] = None) -> List[Dict]:
        """Qdrant相似度搜索"""
        try:
            from qdrant_client import QdrantClient

            client = await self._get_client()

            # 使用真实Embedding服务生成query向量
            query_embedding = (await self._get_embeddings([query]))[0]

            # 搜索
            results = client.search(
                collection_name=settings.QDRANT_COLLECTION,
                query_vector=query_embedding,
                limit=top_k,
            )

            # 整理结果
            docs = []
            for result in results:
                docs.append({
                    "id": str(result.id),
                    "text": result.payload.get("text"),
                    "category": result.payload.get("category"),
                    "score": result.score,
                })

            return docs

        except Exception as e:
            loguru.logger.error(f"Qdrant similarity_search error: {e}")
            return []

    async def delete(self, ids: List[str]) -> None:
        """删除向量"""
        try:
            client = await self._get_client()
            client.delete(
                collection_name=settings.QDRANT_COLLECTION,
                points_selector=[int(i) for i in ids]
            )
        except Exception as e:
            loguru.logger.error(f"Qdrant delete error: {e}")


class InMemoryStore(VectorStore):
    """内存向量存储 (开发/测试用)"""

    _initialized: bool = False
    _texts: List[str] = []
    _embeddings: List[List[float]] = []
    _metadatas: List[Dict] = []

    def __init__(self):
        super().__init__()
        # 延迟初始化知识库
        if not InMemoryStore._initialized:
            import asyncio
            asyncio.create_task(self._init_knowledge_base())
            InMemoryStore._initialized = True

        # 引用类级别的数据
        self.texts = InMemoryStore._texts
        self.embeddings = InMemoryStore._embeddings
        self.metadatas = InMemoryStore._metadatas

    async def _init_knowledge_base(self) -> None:
        """初始化知识库"""
        try:
            from app.services.rag.knowledge_data import get_knowledge_articles
            articles = get_knowledge_articles()

            texts = []
            metas = []
            for article in articles:
                texts.append(article["content"])
                metas.append({
                    "title": article["title"],
                    "category": article["category"],
                    "tags": article.get("tags", ""),
                    "mbti_types": article.get("mbti_types", ""),
                })

            # 使用真实Embedding服务生成向量
            embeddings = await self._get_embeddings(texts)

            # 更新类级别数据
            InMemoryStore._texts = texts
            InMemoryStore._embeddings = embeddings
            InMemoryStore._metadatas = metas

            loguru.logger.info(f"知识库已初始化: {len(articles)} 篇文章, embedding维度: {self.embedding_dim}")
        except Exception as e:
            loguru.logger.warning(f"知识库初始化失败: {e}")
            loguru.logger.warning(f"知识库初始化失败: {e}")

    async def add_texts(self, texts: List[str], metadatas: Optional[List[Dict]] = None) -> List[str]:
        """添加文本"""
        start_id = len(self.texts)

        # 使用真实Embedding服务生成向量
        new_embeddings = await self._get_embeddings(texts)

        self.texts.extend(texts)
        self.embeddings.extend(new_embeddings)
        if metadatas:
            self.metadatas.extend(metadatas)
        else:
            self.metadatas.extend([{} for _ in texts])

        return [str(i) for i in range(start_id, start_id + len(texts))]

    async def similarity_search(self, query: str, top_k: int = 5, filter: Optional[Dict] = None) -> List[Dict]:
        """余弦相似度搜索"""
        if not self.texts:
            return []

        # 使用真实Embedding服务生成query向量
        query_embedding = (await self._get_embeddings([query]))[0]

        # 计算余弦相似度
        scores = []
        for i, embedding in enumerate(self.embeddings):
            score = self._cosine_similarity(query_embedding, embedding)
            scores.append((i, score))

        scores.sort(key=lambda x: x[1], reverse=True)

        results = []
        for idx, score in scores[:top_k]:
            results.append({
                "id": str(idx),
                "text": self.texts[idx],
                "category": self.metadatas[idx].get("category", ""),
                "score": score,
            })

        return results

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot_product / (norm1 * norm2)

    async def delete(self, ids: List[str]) -> None:
        """删除向量"""
        ids_to_delete = set(int(i) for i in ids)
        new_texts = []
        new_embeddings = []
        new_metadatas = []
        for i, (t, e, m) in enumerate(zip(self.texts, self.embeddings, self.metadatas)):
            if i not in ids_to_delete:
                new_texts.append(t)
                new_embeddings.append(e)
                new_metadatas.append(m)
        self.texts = new_texts
        self.embeddings = new_embeddings
        self.metadatas = new_metadatas


def get_vector_store() -> VectorStore:
    """获取向量存储实例"""
    db_type = settings.VECTOR_DB_TYPE.lower()

    if db_type == "milvus":
        return MilvusStore()
    elif db_type == "qdrant":
        return QdrantStore()
    elif db_type == "memory":
        return InMemoryStore()
    else:
        # 默认使用内存存储
        return InMemoryStore()