"""
数据分析API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.analytics import UserActivity, AnalyticsMetric, UserBehavior, EventType
from app.schemas.analytics import (
    UserActivityCreate, UserActivityResponse,
    AnalyticsMetricCreate, AnalyticsMetricResponse,
    UserBehaviorResponse, UserBehaviorUpdate,
    AnalyticsSummaryResponse, EventStatsResponse
)
from app.api.deps import get_current_user, get_current_admin
from app.models.user import User
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.post("/activities", response_model=UserActivityResponse, summary="记录用户活动")
def create_user_activity(
    activity: UserActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """记录用户活动"""
    db_activity = AnalyticsService.track_user_activity(
        db=db,
        user_id=current_user.id,
        event_type=activity.event_type,
        event_name=activity.event_name,
        event_data=activity.event_data,
        ip_address=activity.ip_address,
        user_agent=activity.user_agent
    )
    return db_activity


@router.get("/activities", response_model=List[UserActivityResponse], summary="获取用户活动列表")
def get_user_activities(
    event_type: Optional[str] = Query(None, description="事件类型"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    limit: int = Query(100, ge=1, le=1000, description="限制数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户活动列表"""
    query = db.query(UserActivity).filter(UserActivity.user_id == current_user.id)
    
    if event_type:
        query = query.filter(UserActivity.event_type == event_type)
    if start_time:
        query = query.filter(UserActivity.created_at >= start_time)
    if end_time:
        query = query.filter(UserActivity.created_at <= end_time)
    
    activities = query.order_by(UserActivity.created_at.desc()).limit(limit).all()
    return activities


@router.post("/metrics", response_model=AnalyticsMetricResponse, summary="创建分析指标")
def create_analytics_metric(
    metric: AnalyticsMetricCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """创建分析指标（仅管理员）"""
    db_metric = AnalyticsMetric(
        metric_name=metric.metric_name,
        metric_value=metric.metric_value,
        metric_date=metric.metric_date,
        dimension=metric.dimension,
        dimension_value=metric.dimension_value
    )
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    return db_metric


@router.get("/metrics", response_model=List[AnalyticsMetricResponse], summary="获取分析指标")
def get_analytics_metrics(
    metric_name: Optional[str] = Query(None, description="指标名称"),
    dimension: Optional[str] = Query(None, description="维度"),
    dimension_value: Optional[str] = Query(None, description="维度值"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """获取分析指标（仅管理员）"""
    query = db.query(AnalyticsMetric)
    
    if metric_name:
        query = query.filter(AnalyticsMetric.metric_name == metric_name)
    if dimension:
        query = query.filter(AnalyticsMetric.dimension == dimension)
    if dimension_value:
        query = query.filter(AnalyticsMetric.dimension_value == dimension_value)
    if start_date:
        query = query.filter(AnalyticsMetric.metric_date >= start_date)
    if end_date:
        query = query.filter(AnalyticsMetric.metric_date <= end_date)
    
    metrics = query.order_by(AnalyticsMetric.metric_date.desc()).all()
    return metrics


@router.get("/user-behaviors", response_model=List[UserBehaviorResponse], summary="获取用户行为")
def get_user_behaviors(
    behavior_type: Optional[str] = Query(None, description="行为类型"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户行为"""
    query = db.query(UserBehavior).filter(UserBehavior.user_id == current_user.id)
    
    if behavior_type:
        query = query.filter(UserBehavior.behavior_type == behavior_type)
    
    behaviors = query.order_by(UserBehavior.frequency.desc()).all()
    return behaviors


@router.get("/user-behavior-stats", response_model=Dict[str, Any], summary="获取用户行为统计")
def get_user_behavior_stats(
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户行为统计"""
    stats = AnalyticsService.get_user_behavior_stats(
        db=db,
        user_id=current_user.id,
        days=days
    )
    return stats


@router.get("/system-analytics", response_model=Dict[str, Any], summary="获取系统分析数据")
def get_system_analytics(
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """获取系统分析数据（仅管理员）"""
    analytics = AnalyticsService.get_system_analytics(
        db=db,
        days=days
    )
    return analytics


@router.get("/user-retention", response_model=Dict[str, Any], summary="获取用户留存率")
def get_user_retention(
    days: int = Query(7, ge=1, le=30, description="留存天数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """获取用户留存率（仅管理员）"""
    retention = AnalyticsService.get_user_retention(
        db=db,
        days=days
    )
    return retention


@router.get("/summary", response_model=AnalyticsSummaryResponse, summary="获取分析摘要")
def get_analytics_summary(
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """获取分析摘要（仅管理员）"""
    start_date = datetime.now() - timedelta(days=days)
    
    # 统计用户数量
    total_users = db.query(User).filter(User.created_at >= start_date).count()
    
    # 统计活动数量
    total_activities = db.query(UserActivity).filter(UserActivity.created_at >= start_date).count()
    
    # 统计事件类型分布
    from sqlalchemy import func
    event_stats = db.query(
        UserActivity.event_type,
        func.count(UserActivity.id).label('count')
    ).filter(
        UserActivity.created_at >= start_date
    ).group_by(
        UserActivity.event_type
    ).all()
    
    event_stats_list = [
        EventStatsResponse(event_type=stat.event_type.value, count=stat.count)
        for stat in event_stats
    ]
    
    return AnalyticsSummaryResponse(
        total_users=total_users,
        total_activities=total_activities,
        event_stats=event_stats_list,
        period_days=days
    )
