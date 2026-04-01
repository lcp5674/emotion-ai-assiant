"""
知识库接口
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.core.database import get_db
from app.models import User, KnowledgeArticle, Banner, Announcement, ArticleCollection
from app.models.knowledge import ArticleStatus, ArticleCategory
from app.schemas.knowledge import (
    ArticleSchema,
    ArticleDetailResponse,
    ArticleListResponse,
    ArticleSearchRequest,
    BannerSchema,
    AnnouncementSchema,
)
from app.api.deps import get_current_user
from app.services.html_sanitizer import get_html_sanitizer

router = APIRouter(prefix="/knowledge", tags=["知识库"])


@router.get("/articles", summary="获取文章列表")
async def get_articles(
    category: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """获取知识文章列表"""
    query = db.query(KnowledgeArticle).filter(
        KnowledgeArticle.status == ArticleStatus.PUBLISHED
    )

    if category:
        try:
            query = query.filter(KnowledgeArticle.category == ArticleCategory[category.upper()])
        except KeyError:
            pass

    total = query.count()
    articles = query.order_by(KnowledgeArticle.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    return ArticleListResponse(
        total=total,
        list=[ArticleSchema.model_validate(a) for a in articles],
    )


@router.get("/articles/{article_id}", summary="获取文章详情")
async def get_article(
    article_id: int,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取文章详情"""
    article = db.query(KnowledgeArticle).filter(
        KnowledgeArticle.id == article_id,
        KnowledgeArticle.status == ArticleStatus.PUBLISHED,
    ).first()

    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文章不存在",
        )

    # 增加阅读数
    article.view_count += 1
    db.commit()

    # 获取相关文章
    related = []
    if article.tags:
        tags = article.tags.split(",")
        related = db.query(KnowledgeArticle).filter(
            KnowledgeArticle.id != article_id,
            KnowledgeArticle.status == ArticleStatus.PUBLISHED,
            KnowledgeArticle.tags.contains(tags[0]),
        ).limit(5).all()

    # XSS防护：对HTML内容做净化处理
    sanitizer = get_html_sanitizer()
    safe_content = sanitizer.sanitize(article.content_html) if article.content_html else None

    article_data = ArticleSchema.model_validate(article)
    article_data.content_html = safe_content

    return ArticleDetailResponse(
        article=article_data,
        related_articles=[ArticleSchema.model_validate(a) for a in related],
    )


@router.get("/banners", summary="获取Banner列表")
async def get_banners(
    position: str = Query(default="home"),
    db: Session = Depends(get_db),
):
    """获取Banner列表"""
    now = datetime.now()
    banners = db.query(Banner).filter(
        Banner.is_active == True,
        Banner.position == position,
        (Banner.start_time == None) | (Banner.start_time <= now),
        (Banner.end_time == None) | (Banner.end_time >= now),
    ).order_by(Banner.sort_order.desc()).all()

    return {
        "list": [BannerSchema.model_validate(b) for b in banners],
    }


@router.get("/announcements", summary="获取公告列表")
async def get_announcements(
    db: Session = Depends(get_db),
):
    """获取公告列表"""
    now = datetime.now()
    announcements = db.query(Announcement).filter(
        Announcement.is_active == True,
        (Announcement.start_time == None) | (Announcement.start_time <= now),
        (Announcement.end_time == None) | (Announcement.end_time >= now),
    ).order_by(Announcement.is_top.desc(), Announcement.created_at.desc()).all()

    return {
        "list": [AnnouncementSchema.model_validate(a) for a in announcements],
    }


@router.post("/articles/{article_id}/collect", summary="收藏文章")
async def collect_article(
    article_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """收藏/取消收藏文章"""
    # 检查文章是否存在
    article = db.query(KnowledgeArticle).filter(
        KnowledgeArticle.id == article_id
    ).first()

    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文章不存在",
        )

    # 检查是否已收藏
    existing = db.query(ArticleCollection).filter(
        ArticleCollection.user_id == current_user.id,
        ArticleCollection.article_id == article_id,
    ).first()

    if existing:
        # 取消收藏
        db.delete(existing)
        db.commit()
        return {"is_collected": False}
    else:
        # 添加收藏
        collection = ArticleCollection(
            user_id=current_user.id,
            article_id=article_id,
        )
        db.add(collection)
        db.commit()
        return {"is_collected": True}


@router.get("/collections", summary="获取收藏的文章")
async def get_collections(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取用户收藏的文章"""
    total = db.query(ArticleCollection).filter(
        ArticleCollection.user_id == current_user.id
    ).count()

    collections = db.query(ArticleCollection).filter(
        ArticleCollection.user_id == current_user.id
    ).order_by(ArticleCollection.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    articles = []
    for c in collections:
        article = db.query(KnowledgeArticle).filter(
            KnowledgeArticle.id == c.article_id
        ).first()
        if article:
            articles.append(ArticleSchema.model_validate(article))

    return ArticleListResponse(total=total, list=articles)