"""
数据分析服务
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.models.analytics import UserActivity, AnalyticsMetric, UserBehavior, EventType
from app.models.user import User


class AnalyticsService:
    """数据分析服务"""

    @staticmethod
    def track_user_activity(
        db: Session,
        user_id: int,
        event_type: EventType,
        event_name: str,
        event_data: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> UserActivity:
        """跟踪用户活动"""
        activity = UserActivity(
            user_id=user_id,
            event_type=event_type,
            event_name=event_name,
            event_data=event_data,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.add(activity)
        db.commit()
        db.refresh(activity)
        return activity

    @staticmethod
    def record_analytics_metric(
        db: Session,
        metric_name: str,
        metric_value: float,
        metric_date: datetime,
        dimension: Optional[str] = None,
        dimension_value: Optional[str] = None
    ) -> AnalyticsMetric:
        """记录分析指标"""
        metric = AnalyticsMetric(
            metric_name=metric_name,
            metric_value=metric_value,
            metric_date=metric_date,
            dimension=dimension,
            dimension_value=dimension_value
        )
        db.add(metric)
        db.commit()
        db.refresh(metric)
        return metric

    @staticmethod
    def update_user_behavior(
        db: Session,
        user_id: int,
        behavior_type: str,
        behavior_data: Optional[str] = None
    ) -> UserBehavior:
        """更新用户行为"""
        # 查找是否已存在该行为
        behavior = db.query(UserBehavior).filter(
            UserBehavior.user_id == user_id,
            UserBehavior.behavior_type == behavior_type
        ).first()

        if behavior:
            # 更新现有行为
            behavior.frequency += 1
            behavior.last_occurred_at = datetime.now()
            if behavior_data:
                behavior.behavior_data = behavior_data
        else:
            # 创建新行为
            behavior = UserBehavior(
                user_id=user_id,
                behavior_type=behavior_type,
                behavior_data=behavior_data
            )
            db.add(behavior)

        db.commit()
        db.refresh(behavior)
        return behavior

    @staticmethod
    def get_user_behavior_stats(
        db: Session,
        user_id: int,
        days: int = 30
    ) -> Dict[str, Any]:
        """获取用户行为统计"""
        start_date = datetime.now() - timedelta(days=days)

        # 统计活动次数
        activity_count = db.query(UserActivity).filter(
            UserActivity.user_id == user_id,
            UserActivity.created_at >= start_date
        ).count()

        # 统计不同类型的活动
        activity_types = db.query(
            UserActivity.event_type,
            func.count(UserActivity.id).label('count')
        ).filter(
            UserActivity.user_id == user_id,
            UserActivity.created_at >= start_date
        ).group_by(
            UserActivity.event_type
        ).all()

        # 统计用户行为
        behaviors = db.query(UserBehavior).filter(
            UserBehavior.user_id == user_id
        ).order_by(UserBehavior.frequency.desc()).all()

        return {
            "activity_count": activity_count,
            "activity_types": [
                {"type": at.event_type.value, "count": at.count}
                for at in activity_types
            ],
            "top_behaviors": [
                {
                    "type": b.behavior_type,
                    "frequency": b.frequency,
                    "last_occurred": b.last_occurred_at
                }
                for b in behaviors[:5]
            ]
        }

    @staticmethod
    def get_system_analytics(
        db: Session,
        days: int = 30
    ) -> Dict[str, Any]:
        """获取系统分析数据"""
        start_date = datetime.now() - timedelta(days=days)

        # 统计用户数量
        new_users = db.query(User).filter(
            User.created_at >= start_date
        ).count()

        # 统计活动数量
        total_activities = db.query(UserActivity).filter(
            UserActivity.created_at >= start_date
        ).count()

        # 统计事件类型分布
        event_distribution = db.query(
            UserActivity.event_type,
            func.count(UserActivity.id).label('count')
        ).filter(
            UserActivity.created_at >= start_date
        ).group_by(
            UserActivity.event_type
        ).all()

        # 统计每日活动趋势
        daily_activity = db.query(
            func.date(UserActivity.created_at).label('date'),
            func.count(UserActivity.id).label('count')
        ).filter(
            UserActivity.created_at >= start_date
        ).group_by(
            func.date(UserActivity.created_at)
        ).order_by(
            func.date(UserActivity.created_at)
        ).all()

        return {
            "new_users": new_users,
            "total_activities": total_activities,
            "event_distribution": [
                {"event_type": ed.event_type.value, "count": ed.count}
                for ed in event_distribution
            ],
            "daily_activity": [
                {"date": str(da.date), "count": da.count}
                for da in daily_activity
            ]
        }

    @staticmethod
    def get_user_retention(
        db: Session,
        days: int = 7
    ) -> Dict[str, Any]:
        """获取用户留存率"""
        # 计算起始日期
        start_date = datetime.now() - timedelta(days=days*2)
        end_date = datetime.now() - timedelta(days=days)

        # 获取在起始日期范围内注册的用户
        new_users = db.query(User).filter(
            User.created_at >= start_date,
            User.created_at < end_date
        ).all()

        new_user_ids = [user.id for user in new_users]
        total_new_users = len(new_user_ids)

        if total_new_users == 0:
            return {"retention_rate": 0, "total_new_users": 0, "retained_users": 0}

        # 统计这些用户在后续days天内的活动
        retained_users = db.query(UserActivity.user_id).filter(
            UserActivity.user_id.in_(new_user_ids),
            UserActivity.created_at >= end_date,
            UserActivity.created_at < datetime.now()
        ).distinct().count()

        retention_rate = (retained_users / total_new_users) * 100 if total_new_users > 0 else 0

        return {
            "retention_rate": round(retention_rate, 2),
            "total_new_users": total_new_users,
            "retained_users": retained_users
        }
