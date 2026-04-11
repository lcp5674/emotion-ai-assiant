"""
知识库初始化
"""
import loguru
from sqlalchemy.orm import Session
from app.models.knowledge import KnowledgeArticle, ArticleStatus, ArticleCategory
from app.services.rag.knowledge_data import get_knowledge_articles


def init_knowledge_articles(db: Session) -> None:
    """初始化知识库文章"""
    # 检查是否已有文章
    existing_count = db.query(KnowledgeArticle).count()
    if existing_count > 0:
        loguru.logger.info(f"知识库已有 {existing_count} 篇文章，跳过初始化")
        return

    articles_data = get_knowledge_articles()
    loguru.logger.info(f"开始初始化 {len(articles_data)} 篇知识库文章")

    for article_data in articles_data:
        # 转换分类
        category_str = article_data.get("category", "psychology")
        try:
            category = ArticleCategory[category_str.upper()]
        except KeyError:
            category = ArticleCategory.PSYCHOLOGY

        # 创建文章
        article = KnowledgeArticle(
            title=article_data["title"],
            summary=article_data.get("summary", ""),
            content=article_data["content"],
            category=category,
            tags=article_data.get("tags", ""),
            mbti_types=article_data.get("mbti_types", ""),
            author=article_data.get("author", "心灵伴侣AI"),
            cover_image=article_data.get("cover_image"),
            status=ArticleStatus.PUBLISHED,
            view_count=0,
            like_count=0,
        )
        db.add(article)

    db.commit()
    loguru.logger.info(f"知识库初始化完成，共 {len(articles_data)} 篇文章")