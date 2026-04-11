"""
对话服务
"""
from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_redis
from app.models import Conversation, Message, AiAssistant, User
from app.models.chat import MessageType, ConversationStatus
from app.services.rag.generator import get_generator
from app.services.member_service import get_member_service
from app.services.content_filter import get_content_filter
from app.services.persona_context_builder import get_persona_builder


class ChatService:
    """对话服务"""

    # 上下文消息数量
    CONTEXT_MESSAGES = 10

    async def create_conversation(
        self,
        db: Session,
        user_id: int,
        assistant_id: int,
        title: Optional[str] = None,
        ) -> Conversation:
        """创建新对话"""
        session_id = f"chat_{user_id}_{int(datetime.now().timestamp())}"

        user = db.query(User).filter(User.id == user_id).first()
        user_mbti = user.mbti_type if user else None

        conversation = Conversation(
            user_id=user_id,
            session_id=session_id,
            assistant_id=assistant_id,
            title=title or "新对话",
            user_mbti=user_mbti,
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        return conversation

    async def send_message(
        self,
        db: Session,
        user_id: int,
        session_id: Optional[str],
        assistant_id: Optional[int],
        content: str,
    ) -> Dict[str, Any]:
        """发送消息并获取回复"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("用户不存在")

        member_level = user.member_level.value if hasattr(user.member_level, 'value') else user.member_level
        member_expire_at = user.member_expire_at

        redis_client = await get_redis()
        member_svc = get_member_service()
        allowed, msg, remaining = await member_svc.check_message_limit(
            user_id, member_level, member_expire_at, redis_client
        )
        if not allowed:
            raise ValueError(msg)

        content_filter = get_content_filter()
        passed, _ = await content_filter.check_text(content)
        if not passed:
            return {
                "session_id": None,
                "conversation_id": None,
                "user_message": None,
                "assistant_message": {
                    "id": None,
                    "role": "assistant",
                    "content": content_filter.get_blocked_response(),
                    "created_at": datetime.now(),
                },
                "references": [],
                "content_blocked": True,
            }

        # 获取或创建对话
        conversation = None
        if session_id:
            conversation = db.query(Conversation).filter(
                Conversation.session_id == session_id,
                Conversation.user_id == user_id,
            ).first()

        if not conversation:
            if not assistant_id:
                raise ValueError("需要指定助手ID")
            conversation = await self.create_conversation(
                db=db,
                user_id=user_id,
                assistant_id=assistant_id,
            )

        # 保存用户消息
        user_message = Message(
            conversation_id=conversation.id,
            role="user",
            content=content,
            message_type=MessageType.TEXT,
        )
        db.add(user_message)

        # 获取历史消息构建上下文
        history_messages = db.query(Message).filter(
            Message.conversation_id == conversation.id,
        ).order_by(Message.created_at.desc()).limit(self.CONTEXT_MESSAGES).all()

        conversation_context = "\n".join([
            f"{msg.role}: {msg.content}"
            for msg in reversed(history_messages)
        ])

        # 获取助手信息
        assistant = None
        if conversation.assistant_id:
            assistant = db.query(AiAssistant).filter(
                AiAssistant.id == conversation.assistant_id
            ).first()

        assistant_info = None
        if assistant:
            assistant_info = {
                "name": assistant.name,
                "personality": assistant.personality,
                "speaking_style": assistant.speaking_style,
                "greeting": assistant.greeting,
            }

        user_mbti = user.mbti_type

        # 获取用户画像上下文（MBTI + SBTI + 依恋风格）
        persona_builder = get_persona_builder()
        persona_context = await persona_builder.build_user_context(user)

        # 调用RAG生成回答
        generator = get_generator()
        result = await generator.generate(
            query=content,
            user_mbti=user_mbti,
            conversation_context=conversation_context,
            assistant_info=assistant_info,
            persona_context=persona_context,
        )

        # 保存助手回复
        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=result["answer"],
            message_type=MessageType.TEXT,
        )
        db.add(assistant_message)

        # 更新对话
        conversation.message_count += 2
        conversation.updated_at = datetime.now()
        if not conversation.title or conversation.title == "新对话":
            conversation.title = content[:30] + "..." if len(content) > 30 else content

        db.commit()
        db.refresh(conversation)
        db.refresh(user_message)
        db.refresh(assistant_message)

        if member_level == "free":
            await member_svc.increment_message_count(user_id, redis_client)

        return {
            "session_id": conversation.session_id,
            "conversation_id": conversation.id,
            "user_message": {
                "id": user_message.id,
                "role": user_message.role,
                "content": user_message.content,
                "created_at": user_message.created_at,
            },
            "assistant_message": {
                "id": assistant_message.id,
                "role": assistant_message.role,
                "content": assistant_message.content,
                "created_at": assistant_message.created_at,
            },
            "references": result.get("references", []),
        }

    def get_conversations(
        self,
        db: Session,
        user_id: int,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Conversation]:
        """获取用户对话列表"""
        return db.query(Conversation).filter(
            Conversation.user_id == user_id,
        ).order_by(desc(Conversation.updated_at)).offset(offset).limit(limit).all()

    def get_conversation(
        self,
        db: Session,
        user_id: int,
        session_id: str,
    ) -> Optional[Conversation]:
        """获取对话详情"""
        return db.query(Conversation).filter(
            Conversation.session_id == session_id,
            Conversation.user_id == user_id,
        ).first()

    def get_messages(
        self,
        db: Session,
        conversation_id: int,
        limit: int = 50,
        before_id: Optional[int] = None,
    ) -> List[Message]:
        """获取对话消息"""
        query = db.query(Message).filter(
            Message.conversation_id == conversation_id,
        )
        if before_id:
            query = query.filter(Message.id < before_id)
        return query.order_by(Message.created_at.asc()).limit(limit).all()

    def collect_message(
        self,
        db: Session,
        user_id: int,
        message_id: int,
    ) -> bool:
        """收藏消息"""
        message = db.query(Message).filter(
            Message.id == message_id,
        ).first()
        if not message:
            return False

        message.is_collected = not message.is_collected
        db.commit()
        return message.is_collected

    def close_conversation(
        self,
        db: Session,
        user_id: int,
        session_id: str,
    ) -> bool:
        """关闭对话"""
        conversation = db.query(Conversation).filter(
            Conversation.session_id == session_id,
            Conversation.user_id == user_id,
        ).first()
        if not conversation:
            return False

        conversation.status = ConversationStatus.CLOSED
        db.commit()
        return True


# 全局服务实例
_chat_service: Optional[ChatService] = None


def get_chat_service() -> ChatService:
    """获取对话服务实例"""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service