"""
客服系统相关Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

from app.models.support import TicketStatus, TicketPriority


class SupportTicketCreate(BaseModel):
    """创建工单"""
    title: str = Field(..., description="工单标题")
    description: str = Field(..., description="工单描述")
    category: Optional[str] = Field(None, description="工单类别")
    attachment_url: Optional[str] = Field(None, description="附件URL")
    priority: TicketPriority = Field(TicketPriority.MEDIUM, description="工单优先级")


class SupportTicketUpdate(BaseModel):
    """更新工单"""
    title: Optional[str] = Field(None, description="工单标题")
    description: Optional[str] = Field(None, description="工单描述")
    status: Optional[TicketStatus] = Field(None, description="工单状态")
    priority: Optional[TicketPriority] = Field(None, description="工单优先级")
    assigned_to: Optional[int] = Field(None, description="分配给")
    category: Optional[str] = Field(None, description="工单类别")
    attachment_url: Optional[str] = Field(None, description="附件URL")


class SupportTicketResponse(BaseModel):
    """工单响应"""
    id: int
    user_id: int
    title: str
    description: str
    status: TicketStatus
    priority: TicketPriority
    assigned_to: Optional[int]
    category: Optional[str]
    attachment_url: Optional[str]
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True


class TicketMessageCreate(BaseModel):
    """创建工单消息"""
    content: str = Field(..., description="消息内容")
    attachment_url: Optional[str] = Field(None, description="附件URL")


class TicketMessageResponse(BaseModel):
    """工单消息响应"""
    id: int
    ticket_id: int
    sender_id: int
    sender_type: str
    content: str
    attachment_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ChatbotMessageCreate(BaseModel):
    """创建智能客服消息"""
    content: str = Field(..., description="消息内容")
    message_type: str = Field("text", description="消息类型")


class ChatbotMessageResponse(BaseModel):
    """智能客服消息响应"""
    id: int
    conversation_id: int
    sender_type: str
    content: str
    message_type: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatbotConversationResponse(BaseModel):
    """智能客服对话响应"""
    id: int
    user_id: int
    session_id: str
    status: bool
    created_at: datetime
    updated_at: datetime
    ended_at: Optional[datetime]

    class Config:
        from_attributes = True
