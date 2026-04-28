"""
知识库初始化
"""
import loguru
from sqlalchemy.orm import Session
from app.models.knowledge import KnowledgeArticle, ArticleStatus, ArticleCategory
from app.services.rag.knowledge_data import get_knowledge_articles


def init_knowledge_articles(db: Session) -> None:
    """初始化知识库文章（增量更新）

    如果已有文章，检查是否有新文章需要添加
    如果没有文章，则批量初始化所有文章
    """
    existing_titles = set(
        article[0] for article in
        db.query(KnowledgeArticle.title).all()
    )

    articles_data = get_knowledge_articles()

    if not existing_titles:
        # 首次初始化，添加所有文章
        loguru.logger.info(f"首次初始化知识库，开始添加 {len(articles_data)} 篇文章")
        for article_data in articles_data:
            _add_article(db, article_data)
        db.commit()
        loguru.logger.info(f"知识库初始化完成，共 {len(articles_data)} 篇文章")
    else:
        # 增量更新，只添加新文章
        new_articles = [
            a for a in articles_data
            if a["title"] not in existing_titles
        ]

        if new_articles:
            loguru.logger.info(f"发现 {len(new_articles)} 篇新文章，开始增量更新")
            for article_data in new_articles:
                _add_article(db, article_data)
            db.commit()
            loguru.logger.info(f"知识库增量更新完成，新增 {len(new_articles)} 篇文章")
        else:
            loguru.logger.info("知识库已是最新，无需更新")


def _add_article(db: Session, article_data: dict) -> None:
    """添加单篇文章到数据库"""
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