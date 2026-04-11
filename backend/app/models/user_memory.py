"""
用户长期记忆模型 - 存储用户的重要信息、偏好、生活事件等
用于AI提供更个性化的对话体验
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class MemoryType(enum.Enum):
    """记忆类型"""
    PERSONAL_INFO = "personal_info"      # 个人基本信息
    PREFERENCE = "preference"            # 偏好设置
    LIFE_EVENT = "life_event"            # 生活事件
    RELATIONSHIP = "relationship"        # 人际关系
    GOAL = "goal"                        # 目标计划
    EMOTIONAL_PATTERN = "emotional_pattern"  # 情绪模式
    IMPORTANT_DATE = "important_date"   # 重要日期
    VALUE = "value"                      # 价值观/信念


class MemoryImportance(enum.Enum):
    """重要程度"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class UserLongTermMemory(Base):
    """用户长期记忆表"""
    __tablename__ = "user_long_term_memory"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")

    # 记忆信息
    memory_type = Column(String(50), nullable=False, index=True, comment="记忆类型")
    importance = Column(Integer, default=2, comment="重要程度 1-4")
    content = Column(Text, nullable=False, comment="记忆内容")
    summary = Column(String(500), nullable=True, comment="记忆摘要")

    # 关键词便于检索
    keywords = Column(String(500), nullable=True, comment="关键词，逗号分隔")

    # 元数据
    source = Column(String(50), default="conversation", comment="来源: conversation/diary/user_input")
    source_conversation_id = Column(Integer, nullable=True, comment="来源对话ID")
    source_message_id = Column(Integer, nullable=True, comment="来源消息ID")

    # 置信度 (AI提取的置信度 0-1)
    confidence = Column(Float, default=1.0, comment="置信度")

    # 有效性
    is_active = Column(Boolean, default=True, comment="是否有效")
    is_verified = Column(Boolean, default=False, comment="是否经用户确认")

    # 时间
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    last_accessed_at = Column(DateTime, nullable=True, comment="最后访问时间")

    # 关系
    user = relationship("User")

    def __repr__(self):
        return f"<UserLongTermMemory(user_id={self.user_id}, type={self.memory_type}, importance={self.importance})>"


class UserMemoryInsight(Base):
    """用户记忆洞察表 - AI从长期记忆中提取的洞察总结"""
    __tablename__ = "user_memory_insights"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")

    # 洞察信息
    insight_type = Column(String(50), nullable=False, comment="洞察类型")
    insight_content = Column(Text, nullable=False, comment="洞察内容")
    supporting_memory_ids = Column(String(200), nullable=True, comment="支持的记忆ID列表，逗号分隔")

    # 置信度
    confidence = Column(Float, default=0.5, comment="置信度")

    # 状态
    is_accepted = Column(Boolean, nullable=True, comment="用户是否接受该洞察")

    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    user = relationship("User")

    def __repr__(self):
        return f"<UserMemoryInsight(user_id={self.user_id}, type={self.insight_type})>"


class UserPreference(Base):
    """用户偏好表 - 结构化存储用户偏好"""
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")

    # 偏好分类
    category = Column(String(50), nullable=False, comment="分类")
    key = Column(String(100), nullable=False, comment="键")
    value = Column(Text, nullable=False, comment="值")
    value_type = Column(String(20), default="string", comment="值类型: string/number/boolean/json")

    # 来源
    source = Column(String(50), default="system", comment="来源")

    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 唯一约束
    __table_args__ = (
        # 同一用户同一分类同一key唯一
    )

    def __repr__(self):
        return f"<UserPreference(user_id={self.user_id}, {self.category}.{self.key}={self.value[:20]})>"
