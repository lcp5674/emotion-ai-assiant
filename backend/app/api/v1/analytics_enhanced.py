"""
增强的数据分析API
包含情感趋势分析、用户行为智能洞察等API端点
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime

from app.core.database import get_db
from app.models.user import User
from app.api.deps import get_current_user, get_current_admin
from app.services.analytics_service_enhanced import EnhancedAnalyticsService

router = APIRouter()


@router.get("/sentiment/trends", summary="获取情感趋势分析")
def get_sentiment_trends(
    period: str = Query("daily", description="周期: daily, weekly, monthly, yearly"),
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    user_id: Optional[int] = Query(None, description="用户ID（仅管理员可指定其他用户）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取情感趋势分析"""
    target_user_id = user_id if (user_id and current_user.is_admin) else current_user.id
    return EnhancedAnalyticsService.get_sentiment_analysis(
        db=db,
        user_id=target_user_id,
        period=period,
        days=days
    )


@router.get("/sentiment/health", summary="获取情感健康度评分")
def get_sentiment_health_score(
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    user_id: Optional[int] = Query(None, description="用户ID（仅管理员可指定其他用户）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取情感健康度评分"""
    target_user_id = user_id if (user_id and current_user.is_admin) else current_user.id
    from app.services.analytics_service_enhanced import SentimentTrend
    return SentimentTrend.get_sentiment_health_score(
        db=db,
        user_id=target_user_id,
        days=days
    )


@router.get("/behavior/usage-patterns", summary="获取使用习惯模式识别")
def get_usage_patterns(
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    user_id: Optional[int] = Query(None, description="用户ID（仅管理员可指定其他用户）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取使用习惯模式识别"""
    target_user_id = user_id if (user_id and current_user.is_admin) else current_user.id
    from app.services.analytics_service_enhanced import UserBehaviorInsight
    return UserBehaviorInsight.identify_usage_patterns(
        db=db,
        user_id=target_user_id,
        days=days
    )


@router.get("/behavior/active-hours", summary="获取活跃时段分析")
def get_active_hours(
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    user_id: Optional[int] = Query(None, description="用户ID（仅管理员可指定其他用户）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取活跃时段分析"""
    target_user_id = user_id if (user_id and current_user.is_admin) else current_user.id
    from app.services.analytics_service_enhanced import UserBehaviorInsight
    return UserBehaviorInsight.analyze_active_hours(
        db=db,
        user_id=target_user_id,
        days=days
    )


@router.get("/behavior/content-preferences", summary="获取内容偏好挖掘")
def get_content_preferences(
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    user_id: Optional[int] = Query(None, description="用户ID（仅管理员可指定其他用户）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取内容偏好挖掘"""
    target_user_id = user_id if (user_id and current_user.is_admin) else current_user.id
    from app.services.analytics_service_enhanced import UserBehaviorInsight
    return UserBehaviorInsight.mine_content_preferences(
        db=db,
        user_id=target_user_id,
        days=days
    )


@router.get("/behavior/insights", summary="获取用户行为智能洞察")
def get_user_behavior_insights(
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    user_id: Optional[int] = Query(None, description="用户ID（仅管理员可指定其他用户）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户行为智能洞察（完整报告）"""
    target_user_id = user_id if (user_id and current_user.is_admin) else current_user.id
    return EnhancedAnalyticsService.get_user_behavior_insights(
        db=db,
        user_id=target_user_id,
        days=days
    )


@router.get("/report/comprehensive", summary="获取用户综合分析报告")
def get_comprehensive_user_report(
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    user_id: Optional[int] = Query(None, description="用户ID（仅管理员可指定其他用户）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户综合分析报告（包含情感分析和行为洞察）"""
    target_user_id = user_id if (user_id and current_user.is_admin) else current_user.id
    return EnhancedAnalyticsService.get_comprehensive_user_report(
        db=db,
        user_id=target_user_id,
        days=days
    )


@router.get("/system/insights", summary="获取系统级洞察报告")
def get_system_wide_insights(
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """获取系统级洞察报告（仅管理员）"""
    return EnhancedAnalyticsService.get_system_wide_insights(
        db=db,
        days=days
    )
