"""
增强的数据分析相关Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class SentimentHealthLevel(str, Enum):
    """情感健康级别"""
    EXCELLENT = "excellent"
    GOOD = "good"
    MODERATE = "moderate"
    NEEDS_ATTENTION = "needs_attention"
    UNKNOWN = "unknown"


class SentimentTrendData(BaseModel):
    """情感趋势数据"""
    dates: List[str] = Field(..., description="日期列表")
    sentiments: List[float] = Field(..., description="情感得分列表")
    activity_counts: List[int] = Field(..., description="活动数量列表")


class SentimentTrendsResponse(BaseModel):
    """情感趋势响应"""
    period: str = Field(..., description="周期: daily, weekly, monthly, yearly")
    days: int = Field(..., description="统计天数")
    trends: SentimentTrendData = Field(..., description="趋势数据")
    avg_sentiment: float = Field(..., description="平均情感得分")


class TurningPoint(BaseModel):
    """情感转折点"""
    date: str = Field(..., description="日期")
    previous_sentiment: float = Field(..., description="之前的情感得分")
    current_sentiment: float = Field(..., description="当前的情感得分")
    change: float = Field(..., description="变化值")
    direction: str = Field(..., description="变化方向: positive, negative")


class SentimentHealthDetails(BaseModel):
    """情感健康度详情"""
    avg_sentiment: float = Field(..., description="平均情感得分")
    sentiment_variance: float = Field(..., description="情感方差")
    period_days: int = Field(..., description="统计天数")


class SentimentHealthScoreResponse(BaseModel):
    """情感健康度评分响应"""
    health_score: float = Field(..., description="健康度得分 (0-100)")
    level: SentimentHealthLevel = Field(..., description="健康级别")
    details: SentimentHealthDetails = Field(..., description="详细信息")


class SentimentAnalysisResponse(BaseModel):
    """完整情感分析响应"""
    trends: SentimentTrendsResponse = Field(..., description="情感趋势")
    turning_points: List[TurningPoint] = Field(..., description="情感转折点")
    health_score: SentimentHealthScoreResponse = Field(..., description="情感健康度评分")


class UsagePattern(BaseModel):
    """使用模式"""
    pattern_type: str = Field(..., description="模式类型")
    description: str = Field(..., description="模式描述")
    data: Dict[str, Any] = Field(..., description="模式数据")


class UsagePatternsResponse(BaseModel):
    """使用习惯模式识别响应"""
    patterns: List[UsagePattern] = Field(..., description="模式列表")
    total_activities: int = Field(..., description="总活动数量")
    period_days: int = Field(..., description="统计天数")


class PeakHour(BaseModel):
    """高峰时段"""
    hour: int = Field(..., description="小时 (0-23)")
    count: int = Field(..., description="活动数量")


class ActiveHoursResponse(BaseModel):
    """活跃时段分析响应"""
    hourly_distribution: Dict[int, int] = Field(..., description="每小时分布")
    peak_hours: List[PeakHour] = Field(..., description="高峰时段")
    most_active_time: Optional[str] = Field(None, description="最活跃的时间段")
    period_days: int = Field(..., description="统计天数")


class ContentPreferencesResponse(BaseModel):
    """内容偏好挖掘响应"""
    top_event_types: List[tuple] = Field(..., description="热门事件类型")
    content_interaction_count: int = Field(..., description="内容交互数量")
    preference_score: Dict[str, float] = Field(..., description="偏好分数")
    period_days: int = Field(..., description="统计天数")


class UserBehaviorInsightsResponse(BaseModel):
    """用户行为智能洞察响应"""
    usage_patterns: UsagePatternsResponse = Field(..., description="使用习惯模式")
    active_hours: ActiveHoursResponse = Field(..., description="活跃时段分析")
    content_preferences: ContentPreferencesResponse = Field(..., description="内容偏好挖掘")


class ComprehensiveUserReportResponse(BaseModel):
    """用户综合分析报告响应"""
    user_id: int = Field(..., description="用户ID")
    report_date: str = Field(..., description="报告生成日期")
    period_days: int = Field(..., description="统计天数")
    sentiment_analysis: SentimentAnalysisResponse = Field(..., description="情感分析")
    behavior_insights: UserBehaviorInsightsResponse = Field(..., description="行为洞察")


class HealthDistribution(BaseModel):
    """健康度分布"""
    excellent: int = Field(..., description="优秀用户数")
    good: int = Field(..., description="良好用户数")
    moderate: int = Field(..., description="中等用户数")
    needs_attention: int = Field(..., description="需要关注用户数")


class SystemWideInsightsResponse(BaseModel):
    """系统级洞察报告响应"""
    total_users: int = Field(..., description="总用户数")
    avg_health_score: float = Field(..., description="平均健康度得分")
    avg_activity_count: float = Field(..., description="平均活动数量")
    health_distribution: HealthDistribution = Field(..., description="健康度分布")
    period_days: int = Field(..., description="统计天数")
