"""
内容审核队列模型 - 存储需要人工复审的内容
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float
from sqlalchemy.sql import func

from app.core.database import Base


class ContentAuditQueue(Base):
    """内容人工审核队列"""
    __tablename__ = "content_audit_queue"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="提交用户ID")

    # 内容信息
    content_type = Column(String(20), nullable=False, comment="内容类型: chat/diary/comment")
    content_id = Column(Integer, nullable=True, comment="内容ID")
    content_text = Column(Text, nullable=False, comment="内容文本")

    # 检测结果
    risk_level = Column(String(20), nullable=False, comment="风险等级")
    categories = Column(String(200), nullable=True, comment="违规分类，逗号分隔")
    detected_keywords = Column(String(200), nullable=True, comment="检测到的关键词")
    confidence = Column(Float, default=0.5, comment="检测置信度")

    # 审核状态
    status = Column(String(20), default="pending", comment="状态: pending/processing/approved/rejected")
    reviewed_by = Column(Integer, nullable=True, comment="审核管理员ID")
    reviewed_at = Column(DateTime, nullable=True, comment="审核时间")
    review_note = Column(String(500), nullable=True, comment="审核备注")

    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<ContentAuditQueue(id={self.id}, status={self.status}, risk={self.risk_level})>"
