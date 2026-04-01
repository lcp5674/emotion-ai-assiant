"""
知识库相关Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ArticleSchema(BaseModel):
    """知识文章"""
    id: int
    title: str
    summary: Optional[str] = None
    content: Optional[str] = None
    category: str
    tags: Optional[str] = None
    mbti_types: Optional[str] = None
    cover_image: Optional[str] = None
    author: Optional[str] = None
    view_count: int = 0
    like_count: int = 0
    created_at: datetime
    published_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ArticleDetailResponse(BaseModel):
    """文章详情响应"""
    article: ArticleSchema
    related_articles: List[ArticleSchema] = []


class ArticleListResponse(BaseModel):
    """文章列表响应"""
    total: int
    list: List[ArticleSchema]


class ArticleSearchRequest(BaseModel):
    """文章搜索请求"""
    keyword: str = Field(..., min_length=1)
    category: Optional[str] = None
    mbti_types: Optional[List[str]] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=50)


class BannerSchema(BaseModel):
    """Banner"""
    id: int
    title: str
    image_url: str
    link_url: Optional[str] = None
    link_type: Optional[str] = None
    position: str = "home"

    class Config:
        from_attributes = True


class AnnouncementSchema(BaseModel):
    """公告"""
    id: int
    title: str
    content: str
    content_type: str = "text"
    is_top: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class ArticleCollectionRequest(BaseModel):
    """收藏文章请求"""
    article_id: int


class ArticleLikeRequest(BaseModel):
    """点赞文章请求"""
    article_id: int