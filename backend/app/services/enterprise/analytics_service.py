"""
企业级数据分析服务
提供企业级数据统计、报表生成和数据分析功能
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import User, Enterprise, EnterpriseUser, Conversation, Message


class EnterpriseAnalyticsService:
    """企业级数据分析服务"""
    
    def get_enterprise_summary(self, db: Session, enterprise_id: int) -> Dict[str, Any]:
        """获取企业概览数据"""
        # 获取企业用户数量
        user_count = db.query(func.count(EnterpriseUser.id)).filter(
            EnterpriseUser.enterprise_id == enterprise_id
        ).scalar()
        
        # 获取企业对话数量
        conversation_count = db.query(func.count(Conversation.id)).join(
            EnterpriseUser, Conversation.user_id == EnterpriseUser.user_id
        ).filter(
            EnterpriseUser.enterprise_id == enterprise_id
        ).scalar()
        
        # 获取企业消息数量
        message_count = db.query(func.count(Message.id)).join(
            Conversation, Message.conversation_id == Conversation.id
        ).join(
            EnterpriseUser, Conversation.user_id == EnterpriseUser.user_id
        ).filter(
            EnterpriseUser.enterprise_id == enterprise_id
        ).scalar()
        
        return {
            "user_count": user_count,
            "conversation_count": conversation_count,
            "message_count": message_count
        }
    
    def get_user_activity(self, db: Session, enterprise_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """获取用户活动数据"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 获取每日活跃用户数
        daily_activity = db.query(
            func.date(Conversation.created_at).label('date'),
            func.count(func.distinct(Conversation.user_id)).label('active_users')
        ).join(
            EnterpriseUser, Conversation.user_id == EnterpriseUser.user_id
        ).filter(
            EnterpriseUser.enterprise_id == enterprise_id,
            Conversation.created_at >= start_date
        ).group_by(
            func.date(Conversation.created_at)
        ).order_by(
            func.date(Conversation.created_at)
        ).all()
        
        return [
            {"date": str(activity.date), "active_users": activity.active_users}
            for activity in daily_activity
        ]
    
    def get_usage_metrics(self, db: Session, enterprise_id: int, days: int = 30) -> Dict[str, Any]:
        """获取使用指标"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 获取消息数量趋势
        message_trend = db.query(
            func.date(Message.created_at).label('date'),
            func.count(Message.id).label('message_count')
        ).join(
            Conversation, Message.conversation_id == Conversation.id
        ).join(
            EnterpriseUser, Conversation.user_id == EnterpriseUser.user_id
        ).filter(
            EnterpriseUser.enterprise_id == enterprise_id,
            Message.created_at >= start_date
        ).group_by(
            func.date(Message.created_at)
        ).order_by(
            func.date(Message.created_at)
        ).all()
        
        # 获取用户使用时长（模拟数据）
        # 实际项目中需要根据实际情况计算
        
        return {
            "message_trend": [
                {"date": str(trend.date), "message_count": trend.message_count}
                for trend in message_trend
            ]
        }
    
    def generate_enterprise_report(self, db: Session, enterprise_id: int, report_type: str = "monthly") -> Dict[str, Any]:
        """生成企业报表"""
        if report_type == "monthly":
            days = 30
        elif report_type == "quarterly":
            days = 90
        elif report_type == "yearly":
            days = 365
        else:
            days = 30
        
        summary = self.get_enterprise_summary(db, enterprise_id)
        user_activity = self.get_user_activity(db, enterprise_id, days)
        usage_metrics = self.get_usage_metrics(db, enterprise_id, days)
        
        return {
            "report_type": report_type,
            "period_days": days,
            "summary": summary,
            "user_activity": user_activity,
            "usage_metrics": usage_metrics,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def export_enterprise_data(self, db: Session, enterprise_id: int, format: str = "csv") -> Optional[bytes]:
        """导出企业数据"""
        # 这里实现数据导出逻辑
        # 实际项目中需要根据格式生成相应的文件
        pass


def get_enterprise_analytics_service() -> EnterpriseAnalyticsService:
    """获取企业数据分析服务实例"""
    return EnterpriseAnalyticsService()
