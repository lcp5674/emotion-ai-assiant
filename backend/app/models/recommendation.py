"""
推荐系统数据模型
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Float, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import enum


class ContentType(str, enum.Enum):
    """内容类型"""
    ARTICLE = "article"
    QUOTE = "quote"
    EXERCISE = "exercise"
    MEDITATION = "meditation"
    VIDEO = "video"
    AUDIO = "audio"


class RecommendationReason(str, enum.Enum):
    """推荐原因"""
    MBTI_MATCH = "mbti_match"
    MOOD_MATCH = "mood_match"
    POPULAR = "popular"
    RECENT = "recent"
    USER_HISTORY = "user_history"
    SIMILAR_USER = "similar_user"


class UserContentInteraction(Base):
    """用户内容交互记录"""
    __tablename__ = "user_content_interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content_id = Column(Integer, ForeignKey("knowledge_articles.id"), nullable=True)
    content_type = Column(SQLEnum(ContentType), nullable=False)
    interaction_type = Column(String(50), nullable=False)  # view, like, share, complete, bookmark
    duration = Column(Integer, nullable=True)  # 浏览时长（秒）
    rating = Column(Float, nullable=True)  # 评分（1-5）
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User")


class UserPreference(Base):
    """用户偏好"""
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    preferred_content_types = Column(JSON, nullable=True)  # 偏好的内容类型
    preferred_topics = Column(JSON, nullable=True)  # 偏好的话题
    learning_goal = Column(String(255), nullable=True)  # 学习目标
    time_preference = Column(String(50), nullable=True)  # 时间偏好
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="preference")


class ContentTag(Base):
    """内容标签"""
    __tablename__ = "content_tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    category = Column(String(50), nullable=True)  # 标签分类
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ContentTagRelation(Base):
    """内容-标签关系"""
    __tablename__ = "content_tag_relations"
    
    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("knowledge_articles.id"), nullable=False)
    tag_id = Column(Integer, ForeignKey("content_tags.id"), nullable=False)
    weight = Column(Float, default=1.0)  # 标签权重
    created_at = Column(DateTime, default=datetime.utcnow)


class RecommendationHistory(Base):
    """推荐历史记录"""
    __tablename__ = "recommendation_histories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content_id = Column(Integer, ForeignKey("knowledge_articles.id"), nullable=False)
    recommendation_reason = Column(SQLEnum(RecommendationReason), nullable=False)
    score = Column(Float, nullable=False)  # 推荐分数
    clicked = Column(Integer, default=0)  # 是否点击
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User")
