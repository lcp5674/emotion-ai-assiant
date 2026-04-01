"""
用户模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class MemberLevel(enum.Enum):
    """会员等级"""
    FREE = "free"        # 免费用户
    VIP = "vip"          # VIP会员
    SVIP = "svip"        # 超级会员
    ENTERPRISE = "enterprise"  # 企业用户


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    phone = Column(String(20), unique=True, index=True, nullable=True, comment="手机号")
    email = Column(String(255), unique=True, index=True, nullable=True, comment="邮箱")
    nickname = Column(String(50), nullable=True, comment="昵称")
    avatar = Column(String(500), nullable=True, comment="头像URL")
    password_hash = Column(String(255), nullable=True, comment="密码哈希")

    # MBTI相关
    mbti_type = Column(String(4), nullable=True, comment="MBTI类型")
    mbti_result_id = Column(Integer, nullable=True, comment="MBTI结果ID")

    # 会员相关
    member_level = Column(Enum(MemberLevel), default=MemberLevel.FREE, comment="会员等级")
    member_expire_at = Column(DateTime, nullable=True, comment="会员过期时间")

    # 状态
    is_active = Column(Boolean, default=True, comment="是否激活")
    is_verified = Column(Boolean, default=False, comment="是否验证")
    is_deleted = Column(Boolean, default=False, comment="是否删除")
    is_admin = Column(Boolean, default=False, comment="是否为管理员")

    # 时间戳
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    last_login_at = Column(DateTime, nullable=True, comment="最后登录时间")

    # 关系
    mbti_answers = relationship("MbtiAnswer", back_populates="user", cascade="all, delete-orphan")
    mbti_results = relationship("MbtiResult", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    members = relationship("MemberOrder", back_populates="user", cascade="all, delete-orphan")
    diaries = relationship("EmotionDiary", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, nickname={self.nickname}, mbti={self.mbti_type})>"