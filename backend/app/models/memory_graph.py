"""
知识图谱模型 - 存储用户实体和关系
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class KnowledgeGraph(Base):
    """用户知识图谱表 - 存储实体和关系"""
    __tablename__ = "knowledge_graph"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")

    # 图谱类型: entity(实体) / relation(关系)
    graph_type = Column(String(20), nullable=False, index=True, comment="图谱类型")

    # 实体信息
    entity_type = Column(String(50), nullable=True, comment="实体类型")
    entity_name = Column(String(200), nullable=True, comment="实体名称")

    # 内容
    content = Column(Text, nullable=False, comment="内容")

    # 元数据
    metadata = Column(Text, nullable=True, comment="元数据JSON")

    # 状态
    is_deleted = Column(Boolean, default=False, comment="是否删除")

    # 时间
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    user = relationship("User")

    def __repr__(self):
        return f"<KnowledgeGraph(user_id={self.user_id}, type={self.graph_type}, name={self.entity_name})>"
