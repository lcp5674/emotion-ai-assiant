"""
用户长期记忆Schema定义
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============ 长期记忆 ============

class UserMemoryCreate(BaseModel):
    """创建记忆请求"""
    memory_type: str = Field(..., description="记忆类型")
    content: str = Field(..., description="记忆内容")
    importance: Optional[int] = Field(2, description="重要程度 1-4")
    summary: Optional[str] = Field(None, description="记忆摘要")
    keywords: Optional[str] = Field(None, description="关键词，逗号分隔")
    source: Optional[str] = Field("conversation", description="来源")
    source_conversation_id: Optional[int] = Field(None, description="来源对话ID")
    source_message_id: Optional[int] = Field(None, description="来源消息ID")
    confidence: Optional[float] = Field(1.0, description="置信度")


class UserMemoryUpdate(BaseModel):
    """更新记忆请求"""
    content: Optional[str] = None
    summary: Optional[str] = None
    keywords: Optional[str] = None
    importance: Optional[int] = None
    memory_type: Optional[str] = None
    is_verified: Optional[bool] = None
    is_active: Optional[bool] = None


class UserMemoryResponse(BaseModel):
    """记忆响应"""
    id: int
    user_id: int
    memory_type: str
    importance: int
    content: str
    summary: Optional[str]
    keywords: Optional[str]
    source: str
    source_conversation_id: Optional[int]
    source_message_id: Optional[int]
    confidence: float
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime]
    last_accessed_at: Optional[datetime]

    class Config:
        orm_mode = True


class UserMemoryListResponse(BaseModel):
    """记忆列表响应"""
    total: int
    page: int
    page_size: int
    has_next: bool
    data: List[UserMemoryResponse]


class MemoryStatisticsResponse(BaseModel):
    """记忆统计响应"""
    total_count: int
    by_type: Dict[str, int]
    by_importance: Dict[int, int]


# ============ 记忆洞察 ============

class MemoryInsightCreate(BaseModel):
    """创建洞察请求"""
    insight_type: str = Field(..., description="洞察类型")
    content: str = Field(..., description="洞察内容")
    supporting_memory_ids: Optional[List[int]] = Field(None, description="支持的记忆ID列表")
    confidence: Optional[float] = Field(0.5, description="置信度")


class MemoryInsightResponse(BaseModel):
    """洞察响应"""
    id: int
    user_id: int
    insight_type: str
    insight_content: str
    supporting_memory_ids: Optional[str]
    confidence: float
    is_accepted: Optional[bool]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# ============ 用户偏好 ============

class UserPreferenceSet(BaseModel):
    """设置偏好请求"""
    category: str = Field(..., description="分类")
    key: str = Field(..., description="键")
    value: Any = Field(..., description="值")
    source: Optional[str] = Field("user", description="来源")


class UserPreferenceResponse(BaseModel):
    """偏好响应"""
    id: int
    category: str
    key: str
    value: str
    value_type: str
    source: str
    created_at: datetime
    updated_at: datetime
