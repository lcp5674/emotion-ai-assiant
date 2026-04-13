"""
对话满意度评价服务
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta

from app.models.feedback import MessageFeedback, ConversationFeedback
from app.models.chat import Message, Conversation
from app.models import User
from app.core.exceptions import BusinessLogicException


class FeedbackService:
    """反馈服务"""

    def __init__(self):
        pass

    def create_message_feedback(
        self,
        db: Session,
        user_id: int,
        message_id: int,
        rating: int,
        helpful: int = 0,
        comment: Optional[str] = None
    ) -> MessageFeedback:
        """
        创建消息反馈
        """
        # 检查消息是否存在
        message = db.query(Message).filter(Message.id == message_id).first()
        if not message:
            raise BusinessLogicException("消息不存在")

        # 检查消息所属的对话是否属于当前用户
        conversation = db.query(Conversation).filter(
            Conversation.id == message.conversation_id,
            Conversation.user_id == user_id
        ).first()
        if not conversation:
            raise BusinessLogicException("无权对该消息进行评价")

        # 检查是否已评价过
        existing_feedback = db.query(MessageFeedback).filter(
            MessageFeedback.message_id == message_id,
            MessageFeedback.user_id == user_id
        ).first()
        if existing_feedback:
            # 更新现有反馈
            existing_feedback.rating = rating
            existing_feedback.helpful = helpful
            existing_feedback.comment = comment
            db.commit()
            db.refresh(existing_feedback)
            return existing_feedback

        # 创建新反馈
        feedback = MessageFeedback(
            user_id=user_id,
            message_id=message_id,
            rating=rating,
            helpful=helpful,
            comment=comment
        )
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        return feedback

    def get_message_feedback(
        self,
        db: Session,
        user_id: int,
        message_id: int
    ) -> Optional[MessageFeedback]:
        """
        获取消息反馈
        """
        return db.query(MessageFeedback).filter(
            MessageFeedback.message_id == message_id,
            MessageFeedback.user_id == user_id
        ).first()

    def create_conversation_feedback(
        self,
        db: Session,
        user_id: int,
        conversation_id: int,
        overall_rating: int,
        empathy_rating: int,
        helpfulness_rating: int,
        tags: Optional[List[str]] = None,
        improvement_suggestion: Optional[str] = None,
        is_satisfied: bool = True
    ) -> dict:
        """
        创建对话满意度评价
        """
        # 检查对话是否存在
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        ).first()
        if not conversation:
            raise BusinessLogicException("对话不存在")

        # 检查是否已评价过
        existing_feedback = db.query(ConversationFeedback).filter(
            ConversationFeedback.conversation_id == conversation_id,
            ConversationFeedback.user_id == user_id
        ).first()
        if existing_feedback:
            # 更新现有反馈
            existing_feedback.overall_rating = overall_rating
            existing_feedback.empathy_rating = empathy_rating
            existing_feedback.helpfulness_rating = helpfulness_rating
            existing_feedback.tags = tags
            existing_feedback.improvement_suggestion = improvement_suggestion
            existing_feedback.is_satisfied = is_satisfied
            db.commit()
            db.refresh(existing_feedback)
            return self._format_conversation_feedback(existing_feedback)

        # 创建新反馈
        feedback = ConversationFeedback(
            user_id=user_id,
            conversation_id=conversation_id,
            overall_rating=overall_rating,
            empathy_rating=empathy_rating,
            helpfulness_rating=helpfulness_rating,
            tags=tags,
            improvement_suggestion=improvement_suggestion,
            is_satisfied=is_satisfied
        )
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        return self._format_conversation_feedback(feedback)

    def get_conversation_feedback(
        self,
        db: Session,
        user_id: int,
        conversation_id: int
    ) -> Optional[dict]:
        """
        获取对话反馈
        """
        feedback = db.query(ConversationFeedback).filter(
            ConversationFeedback.conversation_id == conversation_id,
            ConversationFeedback.user_id == user_id
        ).first()
        if feedback:
            return self._format_conversation_feedback(feedback)
        return None

    def get_user_feedback_stats(
        self,
        db: Session,
        user_id: int,
        days: int = 30
    ) -> dict:
        """
        获取用户反馈统计
        """
        start_date = datetime.utcnow() - timedelta(days=days)

        # 获取总对话数和平均评分
        stats = db.query(
            func.count(ConversationFeedback.id).label('total'),
            func.avg(ConversationFeedback.overall_rating).label('avg_overall'),
            func.avg(ConversationFeedback.empathy_rating).label('avg_empathy'),
            func.avg(ConversationFeedback.helpfulness_rating).label('avg_helpfulness'),
            func.avg(ConversationFeedback.is_satisfied.cast(db.bind.dialect.name == 'postgresql' and 1 or 0)).label('satisfaction_rate')
        ).filter(
            ConversationFeedback.user_id == user_id,
            ConversationFeedback.created_at >= start_date
        ).first()

        # 获取最近反馈
        recent_feedbacks = db.query(ConversationFeedback).filter(
            ConversationFeedback.user_id == user_id
        ).order_by(ConversationFeedback.created_at.desc()).limit(10).all()

        # 获取热门标签
        top_tags = self._get_top_tags(db, user_id, days)

        return {
            "total_conversations": stats.total or 0,
            "avg_overall_rating": round(float(stats.avg_overall or 0), 2),
            "avg_empathy_rating": round(float(stats.avg_empathy or 0), 2),
            "avg_helpfulness_rating": round(float(stats.avg_helpfulness or 0), 2),
            "satisfaction_rate": round(float(stats.satisfaction_rate or 0) * 100, 2),
            "top_tags": top_tags,
            "recent_feedbacks": [self._format_conversation_feedback(f) for f in recent_feedbacks]
        }

    def get_system_feedback_stats(
        self,
        db: Session,
        days: int = 7
    ) -> dict:
        """
        获取系统反馈统计（管理员用）
        """
        start_date = datetime.utcnow() - timedelta(days=days)

        # 获取统计
        stats = db.query(
            func.count(ConversationFeedback.id).label('total'),
            func.avg(ConversationFeedback.overall_rating).label('avg_overall'),
            func.avg(ConversationFeedback.empathy_rating).label('avg_empathy'),
            func.avg(ConversationFeedback.helpfulness_rating).label('avg_helpfulness'),
            func.sum(ConversationFeedback.is_satisfied.cast(db.bind.dialect.name == 'postgresql' and 1 or 0)).label('satisfied_count')
        ).filter(
            ConversationFeedback.created_at >= start_date
        ).first()

        total = stats.total or 1
        satisfied = stats.satisfied_count or 0

        return {
            "period_days": days,
            "total_feedbacks": total,
            "avg_overall_rating": round(float(stats.avg_overall or 0), 2),
            "avg_empathy_rating": round(float(stats.avg_empathy or 0), 2),
            "avg_helpfulness_rating": round(float(stats.avg_helpfulness or 0), 2),
            "satisfaction_rate": round((satisfied / total) * 100, 2) if total > 0 else 0,
            "top_tags": self._get_top_tags(db, None, days)
        }

    def _get_top_tags(self, db: Session, user_id: Optional[int], days: int) -> List[str]:
        """获取热门标签"""
        from collections import Counter
        start_date = datetime.utcnow() - timedelta(days=days)

        query = db.query(ConversationFeedback.tags).filter(
            ConversationFeedback.created_at >= start_date
        )
        if user_id:
            query = query.filter(ConversationFeedback.user_id == user_id)

        feedbacks = query.all()
        all_tags = []
        for f in feedbacks:
            if f.tags:
                all_tags.extend(f.tags)

        tag_counts = Counter(all_tags)
        return [tag for tag, _ in tag_counts.most_common(5)]

    def _format_conversation_feedback(self, feedback: ConversationFeedback) -> dict:
        """格式化对话反馈"""
        return {
            "id": feedback.id,
            "conversation_id": feedback.conversation_id,
            "overall_rating": feedback.overall_rating,
            "empathy_rating": feedback.empathy_rating,
            "helpfulness_rating": feedback.helpfulness_rating,
            "tags": feedback.tags,
            "improvement_suggestion": feedback.improvement_suggestion,
            "is_satisfied": feedback.is_satisfied,
            "created_at": feedback.created_at
        }


# 全局实例
_feedback_service: Optional[FeedbackService] = None


def get_feedback_service() -> FeedbackService:
    """获取反馈服务实例"""
    global _feedback_service
    if _feedback_service is None:
        _feedback_service = FeedbackService()
    return _feedback_service
