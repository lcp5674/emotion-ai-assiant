"""
权限管理模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class PermissionAction(enum.Enum):
    """权限操作类型"""
    READ = "read"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    MANAGE = "manage"


class ResourceType(enum.Enum):
    """资源类型"""
    USER = "user"
    ARTICLE = "article"
    BANNER = "banner"
    ANNOUNCEMENT = "announcement"
    CONFIG = "config"
    STATISTICS = "statistics"
    AUDIT = "audit"
    ASSISTANT = "assistant"


# 角色-权限关联表
role_permission = Table('role_permission', Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)

# 用户-角色关联表
user_role = Table('user_role', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)


class Permission(Base):
    """权限表"""
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False, comment="权限名称")
    code = Column(String(50), unique=True, nullable=False, comment="权限代码")
    description = Column(String(200), nullable=True, comment="权限描述")
    resource_type = Column(Enum(ResourceType), nullable=False, comment="资源类型")
    action = Column(Enum(PermissionAction), nullable=False, comment="操作类型")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    roles = relationship("Role", secondary=role_permission, back_populates="permissions")

    def __repr__(self):
        return f"<Permission(id={self.id}, code={self.code}, resource={self.resource_type.value}, action={self.action.value})>"


class Role(Base):
    """角色表"""
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False, comment="角色名称")
    code = Column(String(50), unique=True, nullable=False, comment="角色代码")
    description = Column(String(200), nullable=True, comment="角色描述")
    is_system = Column(Boolean, default=False, comment="是否系统角色")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    permissions = relationship("Permission", secondary=role_permission, back_populates="roles")
    users = relationship("User", secondary=user_role, back_populates="roles")

    def __repr__(self):
        return f"<Role(id={self.id}, code={self.code}, name={self.name})>"


# 在User模型中添加角色关系
from app.models.user import User
User.roles = relationship("Role", secondary=user_role, back_populates="users")
