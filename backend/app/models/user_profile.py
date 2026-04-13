"""
用户资料模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class UserProfile(Base):
    """用户资料表"""
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True, comment="用户ID")

    # 基本资料
    nickname = Column(String(50), nullable=True, comment="昵称")
    avatar = Column(String(500), nullable=True, comment="头像URL")
    bio = Column(Text, nullable=True, comment="个人简介")
    gender = Column(String(10), nullable=True, comment="性别")
    birthday = Column(String(20), nullable=True, comment="生日")

    # 位置信息
    city = Column(String(50), nullable=True, comment="城市")
    country = Column(String(50), nullable=True, comment="国家")

    # 职业信息
    occupation = Column(String(100), nullable=True, comment="职业")
    company = Column(String(200), nullable=True, comment="公司")
    school = Column(String(200), nullable=True, comment="学校")

    # 社交信息
    website = Column(String(500), nullable=True, comment="个人网站")
    wechat = Column(String(100), nullable=True, comment="微信号")

    # 隐私设置
    is_public = Column(Boolean, default=True, comment="资料是否公开")

    # 时间
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    user = relationship("User", back_populates="profile")

    def __repr__(self):
        return f"<UserProfile(user_id={self.user_id}, nickname={self.nickname})>"
