"""
用户反馈与成长系统数据模型
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Float, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import enum


class FeedbackType(str, enum.Enum):
    """反馈类型"""
    MESSAGE_RATING = "message_rating"
    ASSISTANT_RATING = "assistant_rating"
    APP_FEEDBACK = "app_feedback"
    BUG_REPORT = "bug_report"
    FEATURE_REQUEST = "feature_request"


class FeedbackStatus(str, enum.Enum):
    """反馈状态"""
    PENDING = "pending"
    REVIEWED = "reviewed"
    RESOLVED = "resolved"
    CLOSED = "closed"


class MessageFeedback(Base):
    """消息反馈"""
    __tablename__ = "message_feedbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5星
    helpful = Column(Integer, default=0)  # 是否有帮助
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User")


class AssistantFeedback(Base):
    """助手反馈"""
    __tablename__ = "assistant_feedbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assistant_id = Column(Integer, ForeignKey("ai_assistants.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5星
    personality_match = Column(Integer, nullable=True)  # 人格匹配度 1-5
    communication_style = Column(Integer, nullable=True)  # 沟通风格 1-5
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User")


class AppFeedback(Base):
    """应用反馈"""
    __tablename__ = "app_feedbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    feedback_type = Column(SQLEnum(FeedbackType), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(SQLEnum(FeedbackStatus), default=FeedbackStatus.PENDING)
    priority = Column(Integer, default=3)  # 1-5优先级
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User")


class UserGrowthGoal(Base):
    """用户成长目标"""
    __tablename__ = "user_growth_goals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    goal_type = Column(String(100), nullable=False)  # 目标类型：emotion_management, social_skills, self_awareness等
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    target_date = Column(DateTime, nullable=True)
    progress = Column(Float, default=0.0)  # 0-100进度
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User")


class GrowthMilestone(Base):
    """成长里程碑"""
    __tablename__ = "growth_milestones"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    milestone_type = Column(String(100), nullable=False)  # 里程碑类型
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    achieved_at = Column(DateTime, nullable=True)
    reward_points = Column(Integer, default=0)  # 奖励积分
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User")


class AIAdviceHistory(Base):
    """AI建议历史"""
    __tablename__ = "ai_advice_histories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=True)
    advice_type = Column(String(100), nullable=False)  # 建议类型
    content = Column(Text, nullable=False)
    action_taken = Column(Integer, default=0)  # 是否已采取行动
    outcome = Column(Text, nullable=True)  # 结果
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User")
    conversation = relationship("Conversation")


class UserReflection(Base):
    """用户反思记录"""
    __tablename__ = "user_reflections"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reflection_type = Column(String(100), nullable=False)  # 反思类型：daily, weekly, monthly
    content = Column(Text, nullable=False)
    insights = Column(JSON, nullable=True)  # 洞见
    mood_before = Column(String(50), nullable=True)
    mood_after = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User")
