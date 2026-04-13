"""
用户登录记录模型
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship

from app.core.database import Base


class UserLogin(Base):
    """用户登录记录表"""
    __tablename__ = "user_logins"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")

    # 登录日期
    login_date = Column(Date, nullable=False, index=True, comment="登录日期")

    # 登录时间
    login_time = Column(DateTime, nullable=True, comment="登录时间")

    # 登录方式
    login_method = Column(String(50), default="password", comment="登录方式")

    # IP地址
    ip_address = Column(String(50), nullable=True, comment="IP地址")

    # 设备信息
    device_info = Column(String(500), nullable=True, comment="设备信息")

    # 关系
    user = relationship("User")

    def __repr__(self):
        return f"<UserLogin(user_id={self.user_id}, date={self.login_date})>"
