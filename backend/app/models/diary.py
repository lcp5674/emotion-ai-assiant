"""
情感日记模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Date, JSON, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class MoodLevel(enum.Enum):
    """心情等级"""
    TERRIBLE = "terrible"      # 很糟糕
    BAD = "bad"                # 不好
    NEUTRAL = "neutral"        # 一般
    GOOD = "good"              # 不错
    EXCELLENT = "excellent"    # 很棒


class EmotionType(enum.Enum):
    """情绪类型"""
    HAPPY = "happy"            # 开心
    EXCITED = "excited"        # 兴奋
    GRATEFUL = "grateful"      # 感恩
    PEACEFUL = "peaceful"      # 平静
    ANXIOUS = "anxious"        # 焦虑
    SAD = "sad"                # 伤心
    ANGRY = "angry"            # 生气
    FRUSTRATED = "frustrated"  # 挫败
    LONELY = "lonely"          # 孤独
    CONFUSED = "confused"      # 困惑
    HOPEFUL = "hopeful"        # 充满希望
    MOTIVATED = "motivated"    # 有动力


class EmotionDiary(Base):
    """情感日记表"""
    __tablename__ = "emotion_diaries"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")

    # 日期和心情
    date = Column(Date, nullable=False, index=True, comment="日期")
    mood_score = Column(Integer, nullable=False, comment="心情评分 1-10")
    mood_level = Column(SQLEnum(MoodLevel), nullable=True, comment="心情等级")

    # 情绪
    primary_emotion = Column(SQLEnum(EmotionType), nullable=True, comment="主要情绪")
    secondary_emotions = Column(JSON, nullable=True, comment="次要情绪列表")
    emotion_tags = Column(String(500), nullable=True, comment="情绪标签，逗号分隔")

    # 内容
    content = Column(Text, nullable=True, comment="日记内容")
    summary = Column(String(500), nullable=True, comment="AI生成的摘要")

    # AI分析
    ai_analysis = Column(Text, nullable=True, comment="AI情绪分析")
    ai_suggestion = Column(Text, nullable=True, comment="AI建议")
    analysis_status = Column(String(20), default="pending", comment="分析状态: pending/processing/completed/failed")

    # 标签和分类
    tags = Column(String(500), nullable=True, comment="自定义标签，逗号分隔")
    category = Column(String(50), nullable=True, comment="分类：工作/感情/生活/学习/其他")

    # 社交分享
    is_shared = Column(Boolean, default=False, comment="是否分享")
    share_public = Column(Boolean, default=False, comment="是否公开分享")

    # 状态
    is_active = Column(Boolean, default=True, comment="是否启用")
    is_deleted = Column(Boolean, default=False, comment="是否删除")

    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    user = relationship("User", back_populates="diaries")

    def __repr__(self):
        return f"<EmotionDiary(user_id={self.user_id}, date={self.date}, mood={self.mood_score})>"


class MoodRecord(Base):
    """心情快速记录表（用于多次记录）"""
    __tablename__ = "mood_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")

    mood_score = Column(Integer, nullable=False, comment="心情评分 1-10")
    mood_level = Column(SQLEnum(MoodLevel), nullable=True, comment="心情等级")
    emotion = Column(SQLEnum(EmotionType), nullable=True, comment="情绪")
    note = Column(String(200), nullable=True, comment="简短备注")
    location = Column(String(200), nullable=True, comment="位置（可选）")
    activity = Column(String(100), nullable=True, comment="正在做的事")

    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    # 关系
    user = relationship("User")

    def __repr__(self):
        return f"<MoodRecord(user_id={self.user_id}, mood={self.mood_score}, time={self.created_at})>"


class DiaryTag(Base):
    """日记标签表"""
    __tablename__ = "diary_tags"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    name = Column(String(50), nullable=False, comment="标签名称")
    color = Column(String(20), nullable=True, comment="标签颜色")
    use_count = Column(Integer, default=0, comment="使用次数")

    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    # 关系
    user = relationship("User")

    __table_args__ = ()
