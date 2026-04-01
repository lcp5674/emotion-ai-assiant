"""
RAG生成服务 - 结合检索结果生成回答
"""
from typing import List, Dict, Any, Optional
import json
import loguru

from app.services.llm.factory import chat
from app.services.rag.retriever import get_retriever


class Generator:
    """RAG生成器"""

    def __init__(self):
        self.retriever = get_retriever()

    async def generate(
        self,
        query: str,
        user_mbti: Optional[str] = None,
        conversation_context: Optional[str] = None,
        assistant_info: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """生成回答

        Args:
            query: 用户问题
            user_mbti: 用户MBTI类型
            conversation_context: 对话上下文
            assistant_info: 助手信息

        Returns:
            生成的回答和引用
        """
        # 1. 检索相关知识
        docs = await self.retriever.retrieve_with_expand(
            query=query,
            user_mbti=user_mbti,
            conversation_context=conversation_context,
        )

        # 2. 构建提示词
        system_prompt = self._build_system_prompt(assistant_info, user_mbti)
        user_prompt = self._build_user_prompt(query, docs)

        # 3. 调用LLM生成
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            answer = await chat(messages, temperature=0.8, max_tokens=1500)
        except Exception as e:
            loguru.logger.error(f"LLM generate error: {e}")
            answer = "抱歉，我现在有点累，让我休息一下再和你聊天好吗？"

        # 4. 返回结果
        return {
            "answer": answer,
            "references": [
                {
                    "text": doc.get("text", "")[:200] + "...",
                    "category": doc.get("category", ""),
                }
                for doc in docs[:3]
            ],
            "has_reference": len(docs) > 0,
        }

    def _build_system_prompt(self, assistant_info: Optional[Dict] = None, user_mbti: Optional[str] = None) -> str:
        """构建系统提示词"""
        base_prompt = """你是一个温暖、有同理心的AI情感助手"心灵伴侣"。你的职责是：
1. 倾听用户的情感和困惑
2. 提供情绪支持和心理疏导
3. 用专业但易懂的方式解释心理学知识
4. 给出积极、正向的建议

重要原则：
- 始终保持温暖、理解的语气
- 不评判、不批评用户
- 尊重用户的感受和选择
- 必要时建议寻求专业帮助
- 回答要简洁、有重点，不要过长"""

        # 添加助手个性化信息
        if assistant_info:
            personality = assistant_info.get("personality", "")
            speaking_style = assistant_info.get("speaking_style", "")
            if personality:
                base_prompt += f"\n\n你的性格特点：{personality}"
            if speaking_style:
                base_prompt += f"\n你的说话风格：{speaking_style}"

        # 添加用户MBTI信息
        if user_mbti:
            base_prompt += f"\n\n当前用户的MBTI类型是：{user_mbti}"

        return base_prompt

    def _build_user_prompt(self, query: str, docs: List[Dict[str, Any]]) -> str:
        """构建用户提示词"""
        prompt = f"用户的问题是：{query}\n"

        if docs:
            prompt += "\n以下是一些相关的知识参考：\n"
            for i, doc in enumerate(docs, 1):
                text = doc.get("text", "")[:500]
                category = doc.get("category", "")
                prompt += f"\n【参考{i}】({category})\n{text}\n"

            prompt += "\n请根据以上参考知识，结合你的理解，回答用户的问题。"

        return prompt


# 全局生成器实例
_generator: Optional[Generator] = None


def get_generator() -> Generator:
    """获取生成器实例"""
    global _generator
    if _generator is None:
        _generator = Generator()
    return _generator