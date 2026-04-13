"""
对话满意度评价Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class MessageFeedbackCreate(BaseModel):
    """创建消息反馈"""
    message_id: int = Field(..., description="消息ID")
    rating: int = Field(..., ge=1, le=5, description="评分 1-5星")
    helpful: Optional[int] = Field(default=0, description="是否有帮助 0-否 1-是")
    comment: Optional[str] = Field(default=None, max_length=500, description="评价内容")


class MessageFeedbackResponse(BaseModel):
    """消息反馈响应"""
    id: int
    message_id: int
    rating: int
    helpful: int
    comment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationFeedbackCreate(BaseModel):
    """对话满意度评价"""
    conversation_id: int = Field(..., description="对话ID")
    overall_rating: int = Field(..., ge=1, le=5, description="整体评分 1-5星")
    empathy_rating: int = Field(..., ge=1, le=5, description="共情能力评分 1-5星")
    helpfulness_rating: int = Field(..., ge=1, le=5, description="帮助程度评分 1-5星")
    tags: Optional[List[str]] = Field(default=None, description="标签，如：温暖、专业、有用等")
    improvement_suggestion: Optional[str] = Field(default=None, max_length=500, description="改进建议")
    is_satisfied: bool = Field(..., description="是否满意")


class ConversationFeedbackResponse(BaseModel):
    """对话反馈响应"""
    id: int
    conversation_id: int
    overall_rating: int
    empathy_rating: int
    helpfulness_rating: int
    tags: Optional[List[str]]
    improvement_suggestion: Optional[str]
    is_satisfied: bool
    created_at: datetime

    class Config:
        from_attributes = True


class FeedbackStatsResponse(BaseModel):
    """反馈统计"""
    total_conversations: int
    avg_overall_rating: float
    avg_empathy_rating: float
    avg_helpfulness_rating: float
    satisfaction_rate: float
    top_tags: List[str]
    recent_feedbacks: List[ConversationFeedbackResponse]
