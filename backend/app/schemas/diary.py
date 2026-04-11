"""
情感日记相关的请求和响应模型
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime


# ============ 查询模型 ============
class DiaryQuery(BaseModel):
    """日记查询参数"""
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    mood_level: Optional[str] = None
    emotion: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(10, ge=1, le=100, description="每页数量")


# ============ 请求模型 ============

class MoodCreate(BaseModel):
    """心情快速记录请求"""
    mood_score: int = Field(..., ge=1, le=10, description="心情评分 1-10")
    mood_level: Optional[str] = None
    emotion: Optional[str] = None
    note: Optional[str] = Field(None, max_length=200, description="简短备注")
    location: Optional[str] = Field(None, max_length=200, description="位置")
    activity: Optional[str] = Field(None, max_length=100, description="正在做的事")


class DiaryCreate(BaseModel):
    """日记创建请求"""
    date: str = Field(..., description="日期 YYYY-MM-DD")
    mood_score: int = Field(..., ge=1, le=10, description="心情评分 1-10")
    mood_level: Optional[str] = None
    primary_emotion: Optional[str] = None
    secondary_emotions: Optional[List[str]] = None
    emotion_tags: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50, description="分类")
    tags: Optional[str] = Field(None, max_length=500, description="标签，逗号分隔")
    is_shared: bool = False
    share_public: bool = False


class DiaryUpdate(BaseModel):
    """日记更新请求"""
    mood_score: Optional[int] = Field(None, ge=1, le=10, description="心情评分 1-10")
    mood_level: Optional[str] = None
    primary_emotion: Optional[str] = None
    secondary_emotions: Optional[List[str]] = None
    emotion_tags: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50, description="分类")
    tags: Optional[str] = Field(None, max_length=500, description="标签")
    is_shared: Optional[bool] = None
    share_public: Optional[bool] = None


class TagCreate(BaseModel):
    """标签创建请求"""
    name: str = Field(..., max_length=50, description="标签名称")
    color: Optional[str] = Field(None, max_length=20, description="标签颜色")


class TagUpdate(BaseModel):
    """标签更新请求"""
    name: Optional[str] = Field(None, max_length=50, description="标签名称")
    color: Optional[str] = Field(None, max_length=20, description="标签颜色")


# ============ 响应模型 ============

class MoodRecordSchema(BaseModel):
    """心情记录响应"""
    id: int
    mood_score: int
    mood_level: Optional[str] = None
    emotion: Optional[str] = None
    note: Optional[str] = None
    location: Optional[str] = None
    activity: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DiaryTagSchema(BaseModel):
    """日记标签响应"""
    id: int
    name: str
    color: Optional[str] = None
    use_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class DiarySummarySchema(BaseModel):
    """日记摘要响应"""
    id: int
    date: str
    mood_score: int
    mood_level: Optional[str] = None
    primary_emotion: Optional[str] = None
    secondary_emotions: Optional[List[str]] = None
    summary: Optional[str] = None
    tags: Optional[str] = None
    category: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @field_validator('date', mode='before')
    def format_date(cls, v):
        if isinstance(v, date):
            return v.isoformat()
        return v

    class Config:
        from_attributes = True


class DiaryDetailSchema(BaseModel):
    """日记详情响应"""
    id: int
    date: str
    mood_score: int
    mood_level: Optional[str] = None
    primary_emotion: Optional[str] = None
    secondary_emotions: Optional[List[str]] = None
    emotion_tags: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    ai_analysis: Optional[str] = None
    ai_suggestion: Optional[str] = None
    analysis_status: str
    is_shared: bool
    share_public: bool
    created_at: datetime
    updated_at: datetime

    @field_validator('date', mode='before')
    def format_date(cls, v):
        if isinstance(v, date):
            return v.isoformat()
        return v

    class Config:
        from_attributes = True


class DiaryListResponse(BaseModel):
    """日记列表响应"""
    total: int
    page: int
    page_size: int
    has_next: bool
    data: List[DiarySummarySchema]


class MoodTrendPoint(BaseModel):
    """心情趋势点"""
    date: str
    mood_score: int
    mood_level: Optional[str] = None
    primary_emotion: Optional[str] = None
    count: int = 1
    
    @field_validator('date', mode='before')
    def format_date(cls, v):
        if isinstance(v, date):
            return v.isoformat()
        return v


class MoodTrendResponse(BaseModel):
    """心情趋势响应"""
    time_range: str
    start_date: str
    end_date: str
    avg_score: float
    trend_data: List[MoodTrendPoint]
    emotion_distribution: Dict[str, int]
    mood_distribution: Dict[str, int]


class DiaryStatsResponse(BaseModel):
    """日记统计响应"""
    total_count: int
    current_streak: int
    max_streak: int
    avg_mood: float
    most_common_emotion: Optional[str] = None
    avg_words_per_day: float
    categories: Dict[str, int]
    this_month_count: int
    last_month_count: int


class AnalysisResponse(BaseModel):
    """AI分析响应"""
    status: str
    analysis: Optional[str] = None
    suggestion: Optional[str] = None
    keywords: Optional[List[str]] = None


# ============ 配置模型 ============

class EmotionConfig(BaseModel):
    """情绪配置"""
    name: str
    label: str
    color: str
    emoji: str
    description: str


class MoodConfig(BaseModel):
    """心情配置"""
    level: str
    label: str
    score_range: List[int]
    color: str
    emoji: str
    description: str
