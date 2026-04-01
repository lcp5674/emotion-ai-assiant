"""
对话相关Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class MessageSchema(BaseModel):
    """消息"""
    id: int
    role: str
    content: str
    message_type: str = "text"
    emotion: Optional[str] = None
    sentiment_score: Optional[int] = None
    is_collected: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationSchema(BaseModel):
    """对话"""
    id: int
    session_id: str
    title: Optional[str] = None
    assistant_id: Optional[int] = None
    assistant_name: Optional[str] = None
    message_count: int = 0
    status: str = "active"
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatSendRequest(BaseModel):
    """发送消息请求"""
    session_id: Optional[str] = None
    assistant_id: Optional[int] = None
    content: str = Field(..., min_length=1, max_length=2000)
    message_type: str = "text"


class ChatSendResponse(BaseModel):
    """发送消息响应"""
    session_id: str
    conversation_id: int
    message: MessageSchema
    assistant_reply: MessageSchema


class ConversationListResponse(BaseModel):
    """对话列表响应"""
    total: int
    list: List[ConversationSchema]


class MessageListResponse(BaseModel):
    """消息列表响应"""
    total: int
    list: List[MessageSchema]


class ChatHistoryRequest(BaseModel):
    """对话历史请求"""
    session_id: str
    limit: int = Field(default=50, le=100)
    before_id: Optional[int] = None


class MessageCollectRequest(BaseModel):
    """收藏消息请求"""
    message_id: int
    note: Optional[str] = None


class ConversationCreateRequest(BaseModel):
    """创建对话请求"""
    assistant_id: int
    title: Optional[str] = None


class ConversationTitleUpdate(BaseModel):
    """更新对话标题"""
    title: str = Field(..., min_length=1, max_length=200)