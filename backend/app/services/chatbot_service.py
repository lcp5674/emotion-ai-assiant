"""
智能客服服务
"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from app.models.support import ChatbotConversation, ChatbotMessage
from app.models.user import User
from app.services.llm.factory import get_llm_provider
from app.core.config import settings


class ChatbotService:
    """智能客服服务"""

    @staticmethod
    def create_conversation(db: Session, user_id: int) -> ChatbotConversation:
        """创建智能客服对话"""
        session_id = str(uuid.uuid4())
        conversation = ChatbotConversation(
            user_id=user_id,
            session_id=session_id
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation

    @staticmethod
    def get_conversation(db: Session, conversation_id: int, user_id: int) -> Optional[ChatbotConversation]:
        """获取对话"""
        return db.query(ChatbotConversation).filter(
            ChatbotConversation.id == conversation_id,
            ChatbotConversation.user_id == user_id
        ).first()

    @staticmethod
    def get_user_conversations(db: Session, user_id: int, limit: int = 100) -> List[ChatbotConversation]:
        """获取用户的对话列表"""
        return db.query(ChatbotConversation).filter(
            ChatbotConversation.user_id == user_id
        ).order_by(ChatbotConversation.created_at.desc()).limit(limit).all()

    @staticmethod
    def end_conversation(db: Session, conversation_id: int, user_id: int) -> Optional[ChatbotConversation]:
        """结束对话"""
        conversation = ChatbotService.get_conversation(db, conversation_id, user_id)
        if conversation and conversation.status:
            conversation.status = False
            conversation.ended_at = datetime.now()
            db.commit()
            db.refresh(conversation)
        return conversation

    @staticmethod
    async def send_message(
        db: Session,
        conversation_id: int,
        user_id: int,
        content: str,
        message_type: str = "text"
    ) -> Dict[str, Any]:
        """发送消息并获取AI回复"""
        conversation = ChatbotService.get_conversation(db, conversation_id, user_id)
        if not conversation:
            raise ValueError("对话不存在")
        
        if not conversation.status:
            raise ValueError("对话已结束")
        
        # 添加用户消息
        user_message = ChatbotMessage(
            conversation_id=conversation_id,
            sender_type="user",
            content=content,
            message_type=message_type
        )
        db.add(user_message)
        
        # 生成AI回复
        ai_response = await ChatbotService.generate_ai_response(
            db=db,
            conversation=conversation,
            user_message=content
        )
        
        # 添加AI消息
        bot_message = ChatbotMessage(
            conversation_id=conversation_id,
            sender_type="bot",
            content=ai_response,
            message_type="text"
        )
        db.add(bot_message)
        
        db.commit()
        db.refresh(bot_message)
        
        return {
            "user_message": user_message,
            "bot_message": bot_message
        }

    @staticmethod
    async def generate_ai_response(
        db: Session,
        conversation: ChatbotConversation,
        user_message: str
    ) -> str:
        """生成AI回复"""
        # 获取对话历史
        history_messages = db.query(ChatbotMessage).filter(
            ChatbotMessage.conversation_id == conversation.id
        ).order_by(ChatbotMessage.created_at).all()
        
        # 构建对话历史
        history = []
        for msg in history_messages:
            role = "user" if msg.sender_type == "user" else "assistant"
            history.append({
                "role": role,
                "content": msg.content
            })
        
        # 添加当前用户消息
        history.append({
            "role": "user",
            "content": user_message
        })
        
        try:
            # 使用LLM生成回复
            llm = get_llm_provider()
            response = await llm.chat(
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个智能客服助手，负责回答用户的问题，提供帮助和支持。请保持友好、专业的语气。"
                    }
                ] + history,
                temperature=0.7,
                max_tokens=1000
            )
            return response
        except Exception as e:
            # 出错时返回默认回复
            return "感谢您的咨询，我们会尽快为您解答。"

    @staticmethod
    def get_conversation_messages(
        db: Session,
        conversation_id: int,
        user_id: int
    ) -> List[ChatbotMessage]:
        """获取对话消息"""
        conversation = ChatbotService.get_conversation(db, conversation_id, user_id)
        if not conversation:
            raise ValueError("对话不存在")
        
        return db.query(ChatbotMessage).filter(
            ChatbotMessage.conversation_id == conversation_id
        ).order_by(ChatbotMessage.created_at).all()
