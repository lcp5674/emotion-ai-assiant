"""
RAG检索服务
"""
from typing import List, Dict, Any, Optional
import loguru

from app.services.rag.vectorstore import get_vector_store


class Retriever:
    """RAG检索器"""

    def __init__(self):
        self.vector_store = get_vector_store()

    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        category: Optional[str] = None,
        mbti_types: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """检索相关文档

        Args:
            query: 查询文本
            top_k: 返回数量
            category: 文章分类过滤
            mbti_types: MBTI类型过滤

        Returns:
            检索结果列表
        """
        # 1. 向量检索
        docs = await self.vector_store.similarity_search(query, top_k * 2)

        # 2. 过滤
        filtered_docs = []
        for doc in docs:
            if category and doc.get("category") != category:
                continue
            filtered_docs.append(doc)

        # 3. 返回top_k
        return filtered_docs[:top_k]

    async def retrieve_with_expand(
        self,
        query: str,
        user_mbti: Optional[str] = None,
        conversation_context: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """增强检索 (包含用户MBTI和对话上下文)"""
        # 扩展查询
        expanded_query = query

        if user_mbti:
            # 添加MBTI相关关键词
            mbti_keywords = {
                "ISTJ": "务实 可靠 传统 实际",
                "ISFJ": "忠诚 关怀 传统 稳定",
                "INFJ": "理想 洞察 创造 坚定",
                "INTJ": "战略 独立 理性 完美",
                "ISTP": "灵活 实用 观察 动手",
                "ISFP": "艺术 温和 敏感 自由",
                "INFP": "理想 创意 同理 内在",
                "INTP": "逻辑 抽象 思考 独立",
                "ESTP": "行动 灵活 务实 冒险",
                "ESFP": "热情 表演 活跃 友好",
                "ENFP": "创意 热情 灵感 活力",
                "ENTP": "创新 辩论 智力 挑战",
                "ESTJ": "组织 传统 效率 领导",
                "ESFJ": "社交 传统 关怀 责任",
                "ENFJ": "领导 同理 魅力 理想",
                "ENTJ": "领导 决断 战略 效率",
            }
            if user_mbti in mbti_keywords:
                expanded_query = f"{query} {mbti_keywords[user_mbti]}"

        if conversation_context:
            # 将历史对话作为上下文
            expanded_query = f"{conversation_context}\n\n当前问题: {query}"

        # 检索
        return await self.retrieve(expanded_query)


# 全局检索器实例
_retriever: Optional[Retriever] = None


def get_retriever() -> Retriever:
    """获取检索器实例"""
    global _retriever
    if _retriever is None:
        _retriever = Retriever()
    return _retriever