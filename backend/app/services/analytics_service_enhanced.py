"""
增强的数据分析服务
包含情感趋势深度分析、用户行为智能洞察等功能
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, and_, case
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict, Counter

from app.models.analytics import UserActivity, AnalyticsMetric, UserBehavior, EventType
from app.models.user import User


class SentimentTrend:
    """情感趋势分析"""
    
    @staticmethod
    def calculate_sentiment_score(activities: List[UserActivity]) -> float:
        """
        基于活动类型计算情感得分
        积极事件: +1, 中性: 0, 消极: -1
        """
        sentiment_map = {
            EventType.LOGIN: 0.5,
            EventType.REGISTER: 0.8,
            EventType.PAGE_VIEW: 0.2,
            EventType.CLICK: 0.3,
            EventType.DIARY_CREATE: 0.7,
            EventType.ASSESSMENT_COMPLETE: 0.6,
            EventType.PAYMENT: 0.9,
            EventType.FORM_SUBMIT: 0.4,
            EventType.API_CALL: 0.1,
            EventType.CHAT_MESSAGE: 0.5
        }
        
        if not activities:
            return 0.0
        
        scores = [sentiment_map.get(act.event_type, 0.0) for act in activities]
        return float(np.mean(scores))
    
    @staticmethod
    def get_sentiment_trends(db: Session, user_id: Optional[int] = None, 
                            period: str = "daily", days: int = 30) -> Dict[str, Any]:
        """
        获取情感趋势分析
        period: daily, weekly, monthly, yearly
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        query = db.query(UserActivity).filter(
            UserActivity.created_at >= start_date,
            UserActivity.created_at <= end_date
        )
        
        if user_id:
            query = query.filter(UserActivity.user_id == user_id)
        
        activities = query.order_by(UserActivity.created_at).all()
        
        trends_data = defaultdict(list)
        current_period_start = start_date
        
        while current_period_start < end_date:
            if period == "daily":
                period_end = current_period_start + timedelta(days=1)
                period_label = current_period_start.strftime("%Y-%m-%d")
            elif period == "weekly":
                period_end = current_period_start + timedelta(days=7)
                period_label = f"{current_period_start.strftime('%Y-%m-%d')} to {period_end.strftime('%Y-%m-%d')}"
            elif period == "monthly":
                next_month = current_period_start.month % 12 + 1
                next_year = current_period_start.year + (1 if current_period_start.month == 12 else 0)
                period_end = datetime(next_year, next_month, 1)
                period_label = current_period_start.strftime("%Y-%m")
            elif period == "yearly":
                period_end = datetime(current_period_start.year + 1, 1, 1)
                period_label = current_period_start.strftime("%Y")
            else:
                period_end = current_period_start + timedelta(days=1)
                period_label = current_period_start.strftime("%Y-%m-%d")
            
            period_activities = [act for act in activities 
                                if current_period_start <= act.created_at < period_end]
            sentiment_score = SentimentTrend.calculate_sentiment_score(period_activities)
            
            trends_data["dates"].append(period_label)
            trends_data["sentiments"].append(sentiment_score)
            trends_data["activity_counts"].append(len(period_activities))
            
            current_period_start = period_end
        
        return {
            "period": period,
            "days": days,
            "trends": trends_data,
            "avg_sentiment": float(np.mean(trends_data["sentiments"])) if trends_data["sentiments"] else 0.0
        }
    
    @staticmethod
    def detect_turning_points(sentiments: List[float], dates: List[str], 
                             threshold: float = 0.2) -> List[Dict[str, Any]]:
        """检测情感转折点"""
        turning_points = []
        
        for i in range(1, len(sentiments)):
            change = sentiments[i] - sentiments[i-1]
            if abs(change) >= threshold:
                turning_points.append({
                    "date": dates[i],
                    "previous_sentiment": sentiments[i-1],
                    "current_sentiment": sentiments[i],
                    "change": change,
                    "direction": "positive" if change > 0 else "negative"
                })
        
        return turning_points
    
    @staticmethod
    def get_sentiment_health_score(db: Session, user_id: Optional[int] = None, 
                                   days: int = 30) -> Dict[str, Any]:
        """计算情感健康度评分系统"""
        trends = SentimentTrend.get_sentiment_trends(db, user_id, "daily", days)
        sentiments = trends["trends"]["sentiments"]
        
        if not sentiments:
            return {
                "health_score": 50,
                "level": "unknown",
                "details": {}
            }
        
        avg_sentiment = float(np.mean(sentiments))
        sentiment_variance = float(np.var(sentiments))
        
        score = avg_sentiment * 100
        
        if sentiment_variance > 0.1:
            score -= 10
        
        score = max(0, min(100, score))
        
        if score >= 80:
            level = "excellent"
        elif score >= 60:
            level = "good"
        elif score >= 40:
            level = "moderate"
        else:
            level = "needs_attention"
        
        return {
            "health_score": round(score, 2),
            "level": level,
            "details": {
                "avg_sentiment": round(avg_sentiment, 3),
                "sentiment_variance": round(sentiment_variance, 5),
                "period_days": days
            }
        }


class UserBehaviorInsight:
    """用户行为智能洞察"""
    
    @staticmethod
    def identify_usage_patterns(db: Session, user_id: int, days: int = 30) -> Dict[str, Any]:
        """识别使用习惯模式"""
        start_date = datetime.now() - timedelta(days=days)
        
        activities = db.query(UserActivity).filter(
            UserActivity.user_id == user_id,
            UserActivity.created_at >= start_date
        ).all()
        
        if not activities:
            return {"patterns": [], "total_activities": 0}
        
        daily_pattern = defaultdict(int)
        for act in activities:
            day_key = act.created_at.strftime("%A")
            daily_pattern[day_key] += 1
        
        consecutive_days = UserBehaviorInsight._calculate_consecutive_days(activities)
        avg_session_length = UserBehaviorInsight._calculate_avg_session_length(activities)
        
        patterns = [
            {
                "pattern_type": "daily_activity",
                "description": "每日活动分布",
                "data": dict(daily_pattern)
            },
            {
                "pattern_type": "consistency",
                "description": "使用连续性",
                "data": {
                    "max_consecutive_days": consecutive_days["max"],
                    "current_streak": consecutive_days["current"]
                }
            },
            {
                "pattern_type": "engagement",
                "description": "参与度指标",
                "data": {
                    "avg_session_minutes": round(avg_session_length, 2),
                    "total_sessions": UserBehaviorInsight._count_sessions(activities)
                }
            }
        ]
        
        return {
            "patterns": patterns,
            "total_activities": len(activities),
            "period_days": days
        }
    
    @staticmethod
    def analyze_active_hours(db: Session, user_id: int, days: int = 30) -> Dict[str, Any]:
        """分析活跃时段"""
        start_date = datetime.now() - timedelta(days=days)
        
        activities = db.query(UserActivity).filter(
            UserActivity.user_id == user_id,
            UserActivity.created_at >= start_date
        ).all()
        
        if not activities:
            return {"hourly_distribution": {}, "peak_hours": []}
        
        hourly_counts = defaultdict(int)
        for act in activities:
            hour = act.created_at.hour
            hourly_counts[hour] += 1
        
        peak_hours = sorted(hourly_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            "hourly_distribution": dict(hourly_counts),
            "peak_hours": [{"hour": h, "count": c} for h, c in peak_hours],
            "most_active_time": UserBehaviorInsight._categorize_time(peak_hours[0][0]) if peak_hours else None,
            "period_days": days
        }
    
    @staticmethod
    def mine_content_preferences(db: Session, user_id: int, days: int = 30) -> Dict[str, Any]:
        """内容偏好挖掘"""
        start_date = datetime.now() - timedelta(days=days)
        
        activities = db.query(UserActivity).filter(
            UserActivity.user_id == user_id,
            UserActivity.created_at >= start_date
        ).all()
        
        event_types = Counter([act.event_type.value for act in activities])
        
        content_interactions = []
        for act in activities:
            if act.event_data:
                content_interactions.append(act.event_data)
        
        return {
            "top_event_types": event_types.most_common(5),
            "content_interaction_count": len(content_interactions),
            "preference_score": UserBehaviorInsight._calculate_preference_score(event_types),
            "period_days": days
        }
    
    @staticmethod
    def _calculate_consecutive_days(activities: List[UserActivity]) -> Dict[str, int]:
        """计算连续天数"""
        if not activities:
            return {"max": 0, "current": 0}
        
        active_dates = sorted({act.created_at.date() for act in activities})
        if not active_dates:
            return {"max": 0, "current": 0}
        
        max_streak = 1
        current_streak = 1
        
        for i in range(1, len(active_dates)):
            if (active_dates[i] - active_dates[i-1]).days == 1:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1
        
        today = datetime.now().date()
        current_streak_now = 0
        if active_dates[-1] == today:
            current_streak_now = current_streak
        elif (today - active_dates[-1]).days == 1:
            current_streak_now = current_streak
        
        return {"max": max_streak, "current": current_streak_now}
    
    @staticmethod
    def _calculate_avg_session_length(activities: List[UserActivity], 
                                     session_threshold_minutes: int = 30) -> float:
        """计算平均会话长度"""
        if len(activities) < 2:
            return 0.0
        
        sorted_activities = sorted(activities, key=lambda x: x.created_at)
        sessions = []
        current_session = [sorted_activities[0]]
        
        for i in range(1, len(sorted_activities)):
            time_diff = (sorted_activities[i].created_at - current_session[-1].created_at).total_seconds() / 60
            
            if time_diff <= session_threshold_minutes:
                current_session.append(sorted_activities[i])
            else:
                sessions.append(current_session)
                current_session = [sorted_activities[i]]
        
        sessions.append(current_session)
        
        session_lengths = []
        for session in sessions:
            if len(session) >= 2:
                length = (session[-1].created_at - session[0].created_at).total_seconds() / 60
                session_lengths.append(length)
        
        return float(np.mean(session_lengths)) if session_lengths else 0.0
    
    @staticmethod
    def _count_sessions(activities: List[UserActivity], 
                        session_threshold_minutes: int = 30) -> int:
        """统计会话数量"""
        if not activities:
            return 0
        
        sorted_activities = sorted(activities, key=lambda x: x.created_at)
        sessions = 1
        
        for i in range(1, len(sorted_activities)):
            time_diff = (sorted_activities[i].created_at - sorted_activities[i-1].created_at).total_seconds() / 60
            if time_diff > session_threshold_minutes:
                sessions += 1
        
        return sessions
    
    @staticmethod
    def _categorize_time(hour: int) -> str:
        """将小时归类为时间段"""
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 22:
            return "evening"
        else:
            return "night"
    
    @staticmethod
    def _calculate_preference_score(event_types: Counter) -> Dict[str, float]:
        """计算偏好分数"""
        total = sum(event_types.values())
        if total == 0:
            return {}
        
        scores = {}
        for event_type, count in event_types.items():
            scores[event_type] = round(count / total * 100, 2)
        
        return scores


class EnhancedAnalyticsService:
    """增强的数据分析服务"""
    
    @staticmethod
    def get_sentiment_analysis(db: Session, user_id: Optional[int] = None, 
                              period: str = "daily", days: int = 30) -> Dict[str, Any]:
        """获取完整的情感分析报告"""
        trends = SentimentTrend.get_sentiment_trends(db, user_id, period, days)
        turning_points = SentimentTrend.detect_turning_points(
            trends["trends"]["sentiments"],
            trends["trends"]["dates"]
        )
        health_score = SentimentTrend.get_sentiment_health_score(db, user_id, days)
        
        return {
            "trends": trends,
            "turning_points": turning_points,
            "health_score": health_score
        }
    
    @staticmethod
    def get_user_behavior_insights(db: Session, user_id: int, days: int = 30) -> Dict[str, Any]:
        """获取用户行为智能洞察"""
        usage_patterns = UserBehaviorInsight.identify_usage_patterns(db, user_id, days)
        active_hours = UserBehaviorInsight.analyze_active_hours(db, user_id, days)
        content_preferences = UserBehaviorInsight.mine_content_preferences(db, user_id, days)
        
        return {
            "usage_patterns": usage_patterns,
            "active_hours": active_hours,
            "content_preferences": content_preferences
        }
    
    @staticmethod
    def get_comprehensive_user_report(db: Session, user_id: int, days: int = 30) -> Dict[str, Any]:
        """获取用户综合分析报告"""
        sentiment_analysis = EnhancedAnalyticsService.get_sentiment_analysis(db, user_id, "daily", days)
        behavior_insights = EnhancedAnalyticsService.get_user_behavior_insights(db, user_id, days)
        
        return {
            "user_id": user_id,
            "report_date": datetime.now().isoformat(),
            "period_days": days,
            "sentiment_analysis": sentiment_analysis,
            "behavior_insights": behavior_insights
        }
    
    @staticmethod
    def get_system_wide_insights(db: Session, days: int = 30) -> Dict[str, Any]:
        """获取系统级洞察"""
        users = db.query(User).all()
        user_ids = [user.id for user in users]
        
        all_health_scores = []
        all_activity_counts = []
        
        for user_id in user_ids:
            health_score = SentimentTrend.get_sentiment_health_score(db, user_id, days)
            all_health_scores.append(health_score["health_score"])
            
            activity_count = db.query(UserActivity).filter(
                UserActivity.user_id == user_id,
                UserActivity.created_at >= datetime.now() - timedelta(days=days)
            ).count()
            all_activity_counts.append(activity_count)
        
        avg_health_score = float(np.mean(all_health_scores)) if all_health_scores else 0.0
        avg_activity_count = float(np.mean(all_activity_counts)) if all_activity_counts else 0.0
        
        health_distribution = {
            "excellent": len([s for s in all_health_scores if s >= 80]),
            "good": len([s for s in all_health_scores if 60 <= s < 80]),
            "moderate": len([s for s in all_health_scores if 40 <= s < 60]),
            "needs_attention": len([s for s in all_health_scores if s < 40])
        }
        
        return {
            "total_users": len(user_ids),
            "avg_health_score": round(avg_health_score, 2),
            "avg_activity_count": round(avg_activity_count, 2),
            "health_distribution": health_distribution,
            "period_days": days
        }
