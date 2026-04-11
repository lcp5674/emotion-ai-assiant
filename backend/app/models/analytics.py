"""
数据分析模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class EventType(enum.Enum):
    """事件类型"""
    PAGE_VIEW = "page_view"
    CLICK = "click"
    FORM_SUBMIT = "form_submit"
    API_CALL = "api_call"
    CHAT_MESSAGE = "chat_message"
    DIARY_CREATE = "diary_create"
    ASSESSMENT_COMPLETE = "assessment_complete"
    PAYMENT = "payment"
    LOGIN = "login"
    REGISTER = "register"


class UserActivity(Base):
    """用户活动表"""
    __tablename__ = "user_activities"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="用户ID")
    event_type = Column(Enum(EventType), nullable=False, comment="事件类型")
    event_name = Column(String(100), nullable=False, comment="事件名称")
    event_data = Column(Text, nullable=True, comment="事件数据")
    ip_address = Column(String(50), nullable=True, comment="IP地址")
    user_agent = Column(Text, nullable=True, comment="用户代理")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    # 关系
    user = relationship("User", backref="activities")


class AnalyticsMetric(Base):
    """分析指标表"""
    __tablename__ = "analytics_metrics"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    metric_name = Column(String(100), nullable=False, comment="指标名称")
    metric_value = Column(Float, nullable=False, comment="指标值")
    metric_date = Column(DateTime, nullable=False, comment="指标日期")
    dimension = Column(String(100), nullable=True, comment="维度")
    dimension_value = Column(String(255), nullable=True, comment="维度值")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")


class UserBehavior(Base):
    """用户行为表"""
    __tablename__ = "user_behavior"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    behavior_type = Column(String(100), nullable=False, comment="行为类型")
    behavior_data = Column(Text, nullable=True, comment="行为数据")
    frequency = Column(Integer, default=1, comment="行为频率")
    last_occurred_at = Column(DateTime, server_default=func.now(), comment="最后发生时间")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    user = relationship("User", backref="behaviors")
