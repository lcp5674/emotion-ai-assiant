"""
客服系统模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class TicketStatus(enum.Enum):
    """工单状态"""
    PENDING = "pending"      # 待处理
    PROCESSING = "processing"  # 处理中
    RESOLVED = "resolved"    # 已解决
    CLOSED = "closed"        # 已关闭


class TicketPriority(enum.Enum):
    """工单优先级"""
    LOW = "low"        # 低
    MEDIUM = "medium"    # 中
    HIGH = "high"       # 高
    URGENT = "urgent"     # 紧急


class SupportTicket(Base):
    """工单表"""
    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    title = Column(String(255), nullable=False, comment="工单标题")
    description = Column(Text, nullable=False, comment="工单描述")
    status = Column(Enum(TicketStatus), default=TicketStatus.PENDING, comment="工单状态")
    priority = Column(Enum(TicketPriority), default=TicketPriority.MEDIUM, comment="工单优先级")
    assigned_to = Column(Integer, nullable=True, comment="分配给")
    category = Column(String(100), nullable=True, comment="工单类别")
    attachment_url = Column(String(500), nullable=True, comment="附件URL")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    resolved_at = Column(DateTime, nullable=True, comment="解决时间")

    # 关系
    user = relationship("User", backref="tickets")
    messages = relationship("TicketMessage", back_populates="ticket", cascade="all, delete-orphan")


class TicketMessage(Base):
    """工单消息表"""
    __tablename__ = "ticket_messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ticket_id = Column(Integer, ForeignKey("support_tickets.id"), nullable=False, comment="工单ID")
    sender_id = Column(Integer, nullable=False, comment="发送者ID")
    sender_type = Column(Enum("user", "admin"), nullable=False, comment="发送者类型")
    content = Column(Text, nullable=False, comment="消息内容")
    attachment_url = Column(String(500), nullable=True, comment="附件URL")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    # 关系
    ticket = relationship("SupportTicket", back_populates="messages")


class ChatbotConversation(Base):
    """智能客服对话表"""
    __tablename__ = "chatbot_conversations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    session_id = Column(String(100), nullable=False, comment="会话ID")
    status = Column(Boolean, default=True, comment="会话状态")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    ended_at = Column(DateTime, nullable=True, comment="结束时间")

    # 关系
    user = relationship("User", backref="chatbot_conversations")
    messages = relationship("ChatbotMessage", back_populates="conversation", cascade="all, delete-orphan")


class ChatbotMessage(Base):
    """智能客服消息表"""
    __tablename__ = "chatbot_messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("chatbot_conversations.id"), nullable=False, comment="对话ID")
    sender_type = Column(Enum("user", "bot"), nullable=False, comment="发送者类型")
    content = Column(Text, nullable=False, comment="消息内容")
    message_type = Column(String(50), default="text", comment="消息类型")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    # 关系
    conversation = relationship("ChatbotConversation", back_populates="messages")
