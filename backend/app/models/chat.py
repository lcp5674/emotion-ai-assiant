"""
对话模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class MessageType(enum.Enum):
    """消息类型"""
    TEXT = "text"
    VOICE = "voice"
    IMAGE = "image"


class ConversationStatus(enum.Enum):
    """对话状态"""
    ACTIVE = "active"
    CLOSED = "closed"


class Conversation(Base):
    """对话表"""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    session_id = Column(String(64), index=True, nullable=False, comment="会话ID")
    assistant_id = Column(Integer, ForeignKey("ai_assistants.id"), nullable=True, comment="助手ID")

    # 对话信息
    title = Column(String(200), nullable=True, comment="对话标题")
    message_count = Column(Integer, default=0, comment="消息数")
    status = Column(Enum(ConversationStatus), default=ConversationStatus.ACTIVE, comment="状态")

    # 用户画像 (冗余存储提高查询性能)
    user_mbti = Column(String(4), nullable=True, comment="用户MBTI类型")

    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    assistant = relationship("AiAssistant")

    def __repr__(self):
        return f"<Conversation(id={self.id}, session_id={self.session_id})>"


class Message(Base):
    """消息表"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False, comment="对话ID")

    # 消息内容
    role = Column(String(20), nullable=False, comment="角色(user/assistant/system)")
    content = Column(Text, nullable=False, comment="消息内容")
    message_type = Column(Enum(MessageType), default=MessageType.TEXT, comment="消息类型")

    # 扩展
    extra = Column(Text, nullable=True, comment="扩展信息JSON")

    # 情绪分析
    emotion = Column(String(50), nullable=True, comment="检测到的情绪")
    sentiment_score = Column(Integer, nullable=True, comment="情感得分(-100到100)")

    # 收藏
    is_collected = Column(Boolean, default=False, comment="是否收藏")

    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    # 关系
    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, role={self.role}, content={self.content[:20]}...)>"


class MessageCollection(Base):
    """消息收藏表"""
    __tablename__ = "message_collections"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False, comment="消息ID")

    note = Column(String(500), nullable=True, comment="收藏备注")

    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    # 关系
    user = relationship("User")
    message = relationship("Message")

    def __repr__(self):
        return f"<MessageCollection(user_id={self.user_id}, message_id={self.message_id})>"