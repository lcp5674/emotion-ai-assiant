"""
RAG相关服务单元测试
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

from app.services.rag.retriever import Retriever, get_retriever
from app.services.rag.generator import Generator, get_generator
from app.services.rag.vectorstore import VectorStore, get_vector_store
from app.services.rag.vectorstore import InMemoryStore
from app.services.rag.knowledge_data import get_knowledge_articles


class TestRetriever:
    """知识检索器单元测试"""

    def test_init(self):
        """测试初始化"""
        retriever = Retriever()
        assert retriever is not None

    async def test_retrieve_knowledge(self):
        """测试检索知识"""
        with patch("app.services.rag.retriever.get_vector_store") as mock_get_vs:
            mock_vs = Mock()
            mock_vs.similarity_search.return_value = []
            mock_get_vs.return_value = mock_vs
            
            retriever = Retriever()
            results = await retriever.retrieve("什么是抑郁症")
            assert isinstance(results, list)


class TestGenerator:
    """RAG生成器单元测试"""

    def test_init(self):
        """测试初始化"""
        generator = Generator()
        assert generator is not None

    def test_build_system_prompt(self):
        """测试构建系统prompt"""
        generator = Generator()
        prompt = generator._build_system_prompt()
        assert "情感助手" in prompt
        assert "温暖" in prompt
        assert "同理心" in prompt

    def test_build_system_prompt_with_assistant(self):
        """测试带助手信息构建prompt"""
        generator = Generator()
        prompt = generator._build_system_prompt(
            assistant_info={"personality": "温暖理性", "speaking_style": "温和友好"}
        )
        assert "温暖理性" in prompt
        assert "温和友好" in prompt

    def test_build_user_prompt(self):
        """测试构建用户prompt"""
        generator = Generator()
        prompt = generator._build_user_prompt("如何应对焦虑", [])
        assert "如何应对焦虑" in prompt

    async def test_generate_response(self):
        """测试生成响应"""
        from app.services.llm.factory import chat
        with patch("app.services.rag.generator.chat") as mock_chat:
            mock_chat.return_value = "这是生成的回复"
            
            generator = Generator()
            response = await generator.generate(
                query="测试问题"
            )
            assert response["answer"] == "这是生成的回复"
            assert "references" in response


class TestVectorStore:
    """向量存储单元测试"""

    def test_get_vector_store_memory(self):
        """测试获取内存存储"""
        from app.core.config import settings
        original_type = settings.VECTOR_DB_TYPE
        settings.VECTOR_DB_TYPE = "memory"
        
        store = get_vector_store()
        assert isinstance(store, InMemoryStore)
        
        settings.VECTOR_DB_TYPE = original_type

    def test_init_in_memory(self):
        """测试初始化内存存储"""
        store = InMemoryStore()
        assert store is not None
        assert hasattr(store, 'similarity_search')
        assert hasattr(store, 'add_texts')

    async def test_add_texts_in_memory(self):
        """测试添加文本到内存存储"""
        store = InMemoryStore()
        texts = ["这是第一篇知识文档", "这是第二篇知识文档"]
        metadatas = [{"category": "emotion"}, {"category": "psychology"}]
        
        ids = await store.add_texts(texts, metadatas)
        assert len(ids) == 2
        assert isinstance(ids[0], str)

    async def test_similarity_search_in_memory(self):
        """测试内存存储相似搜索"""
        store = InMemoryStore()
        await store.add_texts(["如何应对焦虑", "抑郁症是什么"], 
                            [{"category": "anxiety"}, {"category": "depression"}])
        
        results = await store.similarity_search("焦虑")
        assert len(results) >= 1
        # 第一个应该是焦虑相关
        assert "焦虑" in results[0]["text"]


class TestKnowledgeData:
    """知识数据加载测试"""

    def test_load_knowledge_data(self):
        """测试加载知识数据"""
        knowledge = get_knowledge_articles()
        # 应该能加载到默认知识
        assert isinstance(knowledge, list)
        # 至少应该有一些条目
        assert len(knowledge) > 0

    def test_articles_are_valid(self):
        """测试文章格式正确"""
        knowledge = get_knowledge_articles()
        for article in knowledge:
            assert "title" in article
            assert "content" in article
            assert "category" in article
            assert len(article["content"]) > 0
