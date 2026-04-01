"""
知识库模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class ArticleStatus(enum.Enum):
    """文章状态"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ArticleCategory(enum.Enum):
    """文章分类"""
    EMOTION = "emotion"           # 情绪管理
    RELATIONSHIP = "relationship" # 人际关系
    SELF_GROWTH = "self_growth"   # 个人成长
    PSYCHOLOGY = "psychology"     # 心理知识
    LOVE = "love"                 # 恋爱心理
    FAMILY = "family"             # 家庭关系
    CAREER = "career"             # 职场心理


class KnowledgeArticle(Base):
    """知识文章表"""
    __tablename__ = "knowledge_articles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False, comment="标题")
    summary = Column(String(500), nullable=True, comment="摘要")

    # 内容
    content = Column(Text, nullable=False, comment="文章内容(Markdown)")
    content_html = Column(Text, nullable=True, comment="HTML内容")

    # 分类
    category = Column(Enum(ArticleCategory), nullable=False, comment="分类")
    tags = Column(String(500), nullable=True, comment="标签,逗号分隔")
    mbti_types = Column(String(100), nullable=True, comment="相关MBTI类型,逗号分隔")

    # 向量
    vector_id = Column(String(100), nullable=True, comment="向量ID")

    # 状态
    status = Column(Enum(ArticleStatus), default=ArticleStatus.DRAFT, comment="状态")
    view_count = Column(Integer, default=0, comment="阅读数")
    like_count = Column(Integer, default=0, comment="点赞数")

    # 封面
    cover_image = Column(String(500), nullable=True, comment="封面图")

    # 作者
    author = Column(String(100), nullable=True, comment="作者")

    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    published_at = Column(DateTime, nullable=True, comment="发布时间")

    # 关系
    collections = relationship("ArticleCollection", back_populates="article", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<KnowledgeArticle(id={self.id}, title={self.title})>"


class ArticleCollection(Base):
    """文章收藏表"""
    __tablename__ = "article_collections"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    article_id = Column(Integer, ForeignKey("knowledge_articles.id"), nullable=False, comment="文章ID")

    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    # 关系
    user = relationship("User")
    article = relationship("KnowledgeArticle", back_populates="collections")

    def __repr__(self):
        return f"<ArticleCollection(user_id={self.user_id}, article_id={self.article_id})>"


class Banner(Base):
    """Banner表"""
    __tablename__ = "banners"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(100), nullable=False, comment="标题")
    image_url = Column(String(500), nullable=False, comment="图片URL")
    link_url = Column(String(500), nullable=True, comment="跳转链接")
    link_type = Column(String(20), nullable=True, comment="跳转类型(internal/external)")

    # 位置
    position = Column(String(20), default="home", comment="位置(home/mbti/chat)")

    # 状态
    is_active = Column(Boolean, default=True, comment="是否启用")
    sort_order = Column(Integer, default=0, comment="排序")
    start_time = Column(DateTime, nullable=True, comment="开始时间")
    end_time = Column(DateTime, nullable=True, comment="结束时间")

    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    def __repr__(self):
        return f"<Banner(id={self.id}, title={self.title})>"


class Announcement(Base):
    """公告表"""
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False, comment="标题")
    content = Column(Text, nullable=False, comment="内容")
    content_type = Column(String(20), default="text", comment="内容类型(text/markdown)")

    # 状态
    is_active = Column(Boolean, default=True, comment="是否启用")
    is_top = Column(Boolean, default=False, comment="是否置顶")

    # 时间
    start_time = Column(DateTime, nullable=True, comment="开始时间")
    end_time = Column(DateTime, nullable=True, comment="结束时间")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    def __repr__(self):
        return f"<Announcement(id={self.id}, title={self.title})>"


class MemberOrder(Base):
    """会员订单表"""
    __tablename__ = "member_orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    order_no = Column(String(64), unique=True, nullable=False, comment="订单号")

    # 会员信息
    level = Column(String(20), nullable=False, comment="会员等级")
    amount = Column(Integer, nullable=False, comment="金额(分)")
    duration = Column(Integer, nullable=False, comment="时长(天)")

    # 支付
    payment_method = Column(String(20), nullable=True, comment="支付方式")
    paid_at = Column(DateTime, nullable=True, comment="支付时间")

    # 状态
    status = Column(String(20), default="pending", comment="状态(pending/paid/cancelled/refunded)")

    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    # 关系
    user = relationship("User", back_populates="members")

    def __repr__(self):
        return f"<MemberOrder(id={self.id}, order_no={self.order_no}, level={self.level})>"