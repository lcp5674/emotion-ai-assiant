"""
SSE流式对话服务
"""
from typing import AsyncGenerator, Optional
import json
import asyncio
import loguru

from app.services.rag.generator import get_generator
from app.services.rag.retriever import get_retriever


class StreamChatService:
    CONTEXT_MESSAGES = 10

    async def stream_generate(
        self,
        query: str,
        user_mbti: Optional[str] = None,
        conversation_context: Optional[str] = None,
        assistant_info: Optional[dict] = None,
    ) -> AsyncGenerator[str, None]:
        """流式生成回复"""

        retriever = get_retriever()
        generator = get_generator()

        try:
            docs = await retriever.retrieve_with_expand(
                query=query,
                user_mbti=user_mbti,
                conversation_context=conversation_context,
            )
        except Exception as e:
            loguru.logger.warning(f"检索失败: {e}")
            docs = []

        system_prompt = generator._build_system_prompt(assistant_info, user_mbti)
        user_prompt = generator._build_user_prompt(query, docs)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            from app.services.llm.factory import chat_stream
            async for chunk in chat_stream(messages, temperature=0.8, max_tokens=1500):
                yield f"data: {json.dumps({'type': 'content', 'content': chunk})}\n\n"
        except Exception as e:
            loguru.logger.error(f"流式生成失败: {e}")
            fallback = "抱歉，我现在遇到了一些问题，让我们换个话题聊聊吧。"
            for char in fallback:
                yield f"data: {json.dumps({'type': 'content', 'content': char})}\n\n"
                await asyncio.sleep(0.02)

        yield f"data: {json.dumps({'type': 'done'})}\n\n"


_stream_service = None


def get_stream_service() -> StreamChatService:
    global _stream_service
    if _stream_service is None:
        _stream_service = StreamChatService()
    return _stream_service
