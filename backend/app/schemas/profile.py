"""
深度画像相关Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class CompletionStatus(str, Enum):
    """完成状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    PARTIAL = "partial"


class MbtiSection(BaseModel):
    """MBTI部分"""
    type: str
    communication_style: str
    emotional_pattern: str


class SbtiSection(BaseModel):
    """SBTI部分"""
    top5_themes: List[str]
    relationship_advantages: List[str]


class AttachmentSection(BaseModel):
    """依恋风格部分"""
    style: str
    triggers: List[str] = []
    needs: List[str] = []


class IntegratedInsights(BaseModel):
    """整合洞察"""
    relationship_pattern: str
    effective_communication: str
    avoid_topics: List[str] = []


class AiCompanionRecommendation(BaseModel):
    """AI伴侣推荐"""
    companion_type: str
    matching_reason: str
    suggested_topics: List[str] = []
    interaction_tips: List[str] = []


class DeepPersonaProfile(BaseModel):
    """深度画像响应"""
    user_id: int
    completion_status: CompletionStatus
    completion_percentage: int
    mbti: Optional[MbtiSection] = None
    sbti: Optional[SbtiSection] = None
    attachment: Optional[AttachmentSection] = None
    integrated_insights: Optional[IntegratedInsights] = None
    ai_companion_recommendation: Optional[AiCompanionRecommendation] = None
    generated_at: datetime


class ProfileSummary(BaseModel):
    """画像摘要（用于对话上下文）"""
    user_id: int
    summary: str
    personality_tags: List[str] = []
    relationship_style: str = ""
    communication_tips: List[str] = []


class GenerateProfileRequest(BaseModel):
    """生成画像请求"""
    force_regenerate: bool = Field(default=False, description="是否强制重新生成")


class AiPartnerItem(BaseModel):
    """AI伴侣项"""
    id: int
    name: str
    avatar: Optional[str] = None
    mbti_type: str
    personality: Optional[str] = None
    attachment_style: Optional[str] = None
    match_reason: str
    match_score: Optional[float] = None
    tags: List[str] = []


class AiPartnerListResponse(BaseModel):
    """AI伴侣列表响应"""
    total: int
    list: List[AiPartnerItem]
