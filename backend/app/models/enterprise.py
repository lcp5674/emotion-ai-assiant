"""
企业级数据模型
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import enum


class EnterpriseStatus(str, enum.Enum):
    """企业状态"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class EnterpriseUserRole(str, enum.Enum):
    """企业用户角色"""
    ADMIN = "admin"
    MEMBER = "member"
    GUEST = "guest"


class Enterprise(Base):
    """企业模型"""
    __tablename__ = "enterprises"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    domain = Column(String(255), unique=True, nullable=False, index=True)
    admin_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(SQLEnum(EnterpriseStatus), default=EnterpriseStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    admin_user = relationship("User", foreign_keys=[admin_user_id])
    users = relationship("EnterpriseUser", back_populates="enterprise")
    compliance_policies = relationship("EnterpriseCompliance", back_populates="enterprise")
    audit_logs = relationship("EnterpriseAuditLog", back_populates="enterprise")


class EnterpriseUser(Base):
    """企业用户关系模型"""
    __tablename__ = "enterprise_users"
    
    id = Column(Integer, primary_key=True, index=True)
    enterprise_id = Column(Integer, ForeignKey("enterprises.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(SQLEnum(EnterpriseUserRole), default=EnterpriseUserRole.MEMBER)
    joined_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    enterprise = relationship("Enterprise", back_populates="users")
    user = relationship("User")


class EnterpriseCompliance(Base):
    """企业合规策略模型"""
    __tablename__ = "enterprise_compliance"
    
    id = Column(Integer, primary_key=True, index=True)
    enterprise_id = Column(Integer, ForeignKey("enterprises.id"), nullable=False)
    policy_name = Column(String(255), nullable=False)
    policy_type = Column(String(100), nullable=False)
    policy_content = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    enterprise = relationship("Enterprise", back_populates="compliance_policies")


class EnterpriseAuditLog(Base):
    """企业审计日志模型"""
    __tablename__ = "enterprise_audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    enterprise_id = Column(Integer, ForeignKey("enterprises.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    event_type = Column(String(100), nullable=False)
    event_details = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    enterprise = relationship("Enterprise", back_populates="audit_logs")
    user = relationship("User")
