"""
虚拟形象模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class AiAvatar(Base):
    """AI助手虚拟形象配置"""
    __tablename__ = "ai_avatars"

    id = Column(Integer, primary_key=True, index=True)
    assistant_id = Column(Integer, ForeignKey("ai_assistants.id"), unique=True, nullable=False)

    # 虚拟形象类型
    model_type = Column(String(20), default="live2d")  # live2d 或 vrm

    # Live2D配置
    live2d_model_url = Column(String(500), nullable=True)
    live2d_texture_urls = Column(JSON, nullable=True)  # 纹理图片列表
    live2d_motion_groups = Column(JSON, nullable=True)  # 动作分组
    live2d_expression_map = Column(JSON, nullable=True)  # 表情映射

    # VRM配置
    vrm_model_url = Column(String(500), nullable=True)

    # 基础配置
    name = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)

    # 位置与缩放
    position_x = Column(Float, default=0.0)
    position_y = Column(Float, default=0.0)
    scale = Column(Float, default=1.0)
    z_index = Column(Integer, default=1)

    # 默认动作
    default_motion = Column(String(50), default="idle")
    speak_motion = Column(String(50), default="speak")

    # 随机待机动作
    idle_motions = Column(JSON, nullable=True)

    # 状态
    is_active = Column(Boolean, default=True)

    # 时间戳
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关联
    assistant = relationship("AiAssistant", back_populates="avatar_info")


class AnimationState(Base):
    """动画状态记录"""
    __tablename__ = "animation_states"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assistant_id = Column(Integer, ForeignKey("ai_assistants.id"), nullable=False)

    # 当前状态
    current_expression = Column(String(50), default="neutral")
    current_motion = Column(String(50), default="idle")

    # 说话状态
    is_speaking = Column(Boolean, default=False)

    # 过渡配置
    transition_duration = Column(Float, default=0.3)

    # 最后更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关联
    user = relationship("User", backref="animation_states")
    assistant = relationship("AiAssistant", backref="animation_states")