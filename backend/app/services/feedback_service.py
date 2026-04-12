"""
用户反馈与成长系统服务
提供用户反馈、成长目标管理等功能
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from app.models import (
    User,
    Message,
    AiAssistant,
    FeedbackType,
    FeedbackStatus,
    MessageFeedback,
    AssistantFeedback,
    AppFeedback,
    UserGrowthGoal,
    GrowthMilestone,
    AIAdviceHistory,
    UserReflection,
)


class FeedbackService:
    """用户反馈服务"""
    
    def submit_message_feedback(
        self,
        db: Session,
        user_id: int,
        message_id: int,
        rating: int,
        helpful: int = 0,
        comment: Optional[str] = None
    ) -> MessageFeedback:
        """
        提交消息反馈
        """
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
    
    def submit_assistant_feedback(
        self,
        db: Session,
        user_id: int,
        assistant_id: int,
        rating: int,
        personality_match: Optional[int] = None,
        communication_style: Optional[int] = None,
        comment: Optional[str] = None
    ) -> AssistantFeedback:
        """
        提交助手反馈
        """
        feedback = AssistantFeedback(
            user_id=user_id,
            assistant_id=assistant_id,
            rating=rating,
            personality_match=personality_match,
            communication_style=communication_style,
            comment=comment
        )
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        return feedback
    
    def submit_app_feedback(
        self,
        db: Session,
        feedback_type: FeedbackType,
        title: str,
        content: str,
        user_id: Optional[int] = None,
        priority: int = 3,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AppFeedback:
        """
        提交应用反馈
        """
        feedback = AppFeedback(
            user_id=user_id,
            feedback_type=feedback_type,
            title=title,
            content=content,
            priority=priority,
            metadata=metadata
        )
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        return feedback
    
    def get_message_feedbacks(
        self,
        db: Session,
        message_id: Optional[int] = None,
        user_id: Optional[int] = None,
        limit: int = 50
    ) -> List[MessageFeedback]:
        """
        获取消息反馈列表
        """
        query = db.query(MessageFeedback)
        
        if message_id:
            query = query.filter(MessageFeedback.message_id == message_id)
        if user_id:
            query = query.filter(MessageFeedback.user_id == user_id)
        
        return query.order_by(desc(MessageFeedback.created_at)).limit(limit).all()
    
    def get_assistant_feedbacks(
        self,
        db: Session,
        assistant_id: Optional[int] = None,
        user_id: Optional[int] = None,
        limit: int = 50
    ) -> List[AssistantFeedback]:
        """
        获取助手反馈列表
        """
        query = db.query(AssistantFeedback)
        
        if assistant_id:
            query = query.filter(AssistantFeedback.assistant_id == assistant_id)
        if user_id:
            query = query.filter(AssistantFeedback.user_id == user_id)
        
        return query.order_by(desc(AssistantFeedback.created_at)).limit(limit).all()
    
    def get_assistant_average_rating(
        self,
        db: Session,
        assistant_id: int
    ) -> Optional[float]:
        """
        获取助手平均评分
        """
        avg_rating = db.query(func.avg(AssistantFeedback.rating)).filter(
            AssistantFeedback.assistant_id == assistant_id
        ).scalar()
        
        return avg_rating


class GrowthService:
    """用户成长服务"""
    
    def create_growth_goal(
        self,
        db: Session,
        user_id: int,
        goal_type: str,
        title: str,
        description: Optional[str] = None,
        target_date: Optional[datetime] = None
    ) -> UserGrowthGoal:
        """
        创建成长目标
        """
        goal = UserGrowthGoal(
            user_id=user_id,
            goal_type=goal_type,
            title=title,
            description=description,
            target_date=target_date
        )
        db.add(goal)
        db.commit()
        db.refresh(goal)
        return goal
    
    def update_growth_goal(
        self,
        db: Session,
        goal_id: int,
        user_id: int,
        progress: Optional[float] = None,
        is_active: Optional[int] = None,
        **kwargs
    ) -> Optional[UserGrowthGoal]:
        """
        更新成长目标
        """
        goal = db.query(UserGrowthGoal).filter(
            UserGrowthGoal.id == goal_id,
            UserGrowthGoal.user_id == user_id
        ).first()
        
        if not goal:
            return None
        
        if progress is not None:
            goal.progress = max(0, min(100, progress))
        if is_active is not None:
            goal.is_active = is_active
        
        for key, value in kwargs.items():
            if hasattr(goal, key):
                setattr(goal, key, value)
        
        db.commit()
        db.refresh(goal)
        
        # 检查是否达到里程碑
        if progress and progress >= 100:
            self._check_and_award_milestone(db, user_id, goal)
        
        return goal
    
    def get_user_growth_goals(
        self,
        db: Session,
        user_id: int,
        is_active: Optional[int] = None
    ) -> List[UserGrowthGoal]:
        """
        获取用户成长目标列表
        """
        query = db.query(UserGrowthGoal).filter(UserGrowthGoal.user_id == user_id)
        
        if is_active is not None:
            query = query.filter(UserGrowthGoal.is_active == is_active)
        
        return query.order_by(desc(UserGrowthGoal.created_at)).all()
    
    def _check_and_award_milestone(
        self,
        db: Session,
        user_id: int,
        goal: UserGrowthGoal
    ):
        """
        检查并颁发里程碑
        """
        # 检查是否已存在该里程碑
        existing = db.query(GrowthMilestone).filter(
            GrowthMilestone.user_id == user_id,
            GrowthMilestone.milestone_type == f"goal_complete_{goal.goal_type}"
        ).first()
        
        if not existing:
            milestone = GrowthMilestone(
                user_id=user_id,
                milestone_type=f"goal_complete_{goal.goal_type}",
                title=f"完成{goal.title}目标",
                description="恭喜你完成了这个成长目标！",
                achieved_at=datetime.utcnow(),
                reward_points=100
            )
            db.add(milestone)
            db.commit()
    
    def get_user_milestones(
        self,
        db: Session,
        user_id: int
    ) -> List[GrowthMilestone]:
        """
        获取用户里程碑列表
        """
        return db.query(GrowthMilestone).filter(
            GrowthMilestone.user_id == user_id
        ).order_by(desc(GrowthMilestone.created_at)).all()
    
    def save_ai_advice(
        self,
        db: Session,
        user_id: int,
        advice_type: str,
        content: str,
        conversation_id: Optional[int] = None
    ) -> AIAdviceHistory:
        """
        保存AI建议
        """
        advice = AIAdviceHistory(
            user_id=user_id,
            conversation_id=conversation_id,
            advice_type=advice_type,
            content=content
        )
        db.add(advice)
        db.commit()
        db.refresh(advice)
        return advice
    
    def update_ai_advice_outcome(
        self,
        db: Session,
        advice_id: int,
        user_id: int,
        action_taken: int = 1,
        outcome: Optional[str] = None
    ) -> Optional[AIAdviceHistory]:
        """
        更新AI建议结果
        """
        advice = db.query(AIAdviceHistory).filter(
            AIAdviceHistory.id == advice_id,
            AIAdviceHistory.user_id == user_id
        ).first()
        
        if advice:
            advice.action_taken = action_taken
            advice.outcome = outcome
            db.commit()
            db.refresh(advice)
        
        return advice
    
    def get_user_ai_advice(
        self,
        db: Session,
        user_id: int,
        limit: int = 20
    ) -> List[AIAdviceHistory]:
        """
        获取用户AI建议历史
        """
        return db.query(AIAdviceHistory).filter(
            AIAdviceHistory.user_id == user_id
        ).order_by(desc(AIAdviceHistory.created_at)).limit(limit).all()
    
    def create_reflection(
        self,
        db: Session,
        user_id: int,
        reflection_type: str,
        content: str,
        insights: Optional[Dict[str, Any]] = None,
        mood_before: Optional[str] = None,
        mood_after: Optional[str] = None
    ) -> UserReflection:
        """
        创建反思记录
        """
        reflection = UserReflection(
            user_id=user_id,
            reflection_type=reflection_type,
            content=content,
            insights=insights,
            mood_before=mood_before,
            mood_after=mood_after
        )
        db.add(reflection)
        db.commit()
        db.refresh(reflection)
        return reflection
    
    def get_user_reflections(
        self,
        db: Session,
        user_id: int,
        reflection_type: Optional[str] = None,
        limit: int = 20
    ) -> List[UserReflection]:
        """
        获取用户反思记录
        """
        query = db.query(UserReflection).filter(UserReflection.user_id == user_id)
        
        if reflection_type:
            query = query.filter(UserReflection.reflection_type == reflection_type)
        
        return query.order_by(desc(UserReflection.created_at)).limit(limit).all()


def get_feedback_service() -> FeedbackService:
    """获取反馈服务实例"""
    return FeedbackService()


def get_growth_service() -> GrowthService:
    """获取成长服务实例"""
    return GrowthService()
