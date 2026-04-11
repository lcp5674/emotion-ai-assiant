"""
数据分析相关Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

from app.models.analytics import EventType


class UserActivityCreate(BaseModel):
    """用户活动创建"""
    event_type: EventType = Field(..., description="事件类型")
    event_name: str = Field(..., description="事件名称")
    event_data: Optional[str] = Field(None, description="事件数据")
    ip_address: Optional[str] = Field(None, description="IP地址")
    user_agent: Optional[str] = Field(None, description="用户代理")


class UserActivityResponse(BaseModel):
    """用户活动响应"""
    id: int
    user_id: int
    event_type: EventType
    event_name: str
    event_data: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class AnalyticsMetricCreate(BaseModel):
    """分析指标创建"""
    metric_name: str = Field(..., description="指标名称")
    metric_value: float = Field(..., description="指标值")
    metric_date: datetime = Field(..., description="指标日期")
    dimension: Optional[str] = Field(None, description="维度")
    dimension_value: Optional[str] = Field(None, description="维度值")


class AnalyticsMetricResponse(BaseModel):
    """分析指标响应"""
    id: int
    metric_name: str
    metric_value: float
    metric_date: datetime
    dimension: Optional[str]
    dimension_value: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class UserBehaviorResponse(BaseModel):
    """用户行为响应"""
    id: int
    user_id: int
    behavior_type: str
    behavior_data: Optional[str]
    frequency: int
    last_occurred_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserBehaviorUpdate(BaseModel):
    """用户行为更新"""
    behavior_data: Optional[str] = Field(None, description="行为数据")
    frequency: Optional[int] = Field(None, description="行为频率")


class EventStatsResponse(BaseModel):
    """事件统计响应"""
    event_type: str
    count: int


class AnalyticsSummaryResponse(BaseModel):
    """分析摘要响应"""
    total_users: int
    total_activities: int
    event_stats: List[EventStatsResponse]
    period_days: int
