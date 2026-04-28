"""
知识库同步服务
支持联网获取最新心理知识文章
"""
import loguru
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import httpx
import asyncio
import json

from app.models.knowledge import KnowledgeArticle, ArticleStatus, ArticleCategory


class KnowledgeSyncService:
    """知识库同步服务"""

    # 默认知识库API端点（真实公开免费API）
    DEFAULT_SOURCES = {
        # ZenQuotes API - 励志名言/心理健康语录
        "zenquotes": "https://zenquotes.io/api/random",
        # Advice Slip API - 生活建议
        "advice_slip": "https://api.adviceslip.com/advice",
        # Affirmations API - 正能量语录
        "affirmations": "https://www.affirmations.cool/",
    }

    # 分类映射：将API来源映射到文章分类
    SOURCE_CATEGORY_MAP = {
        "zenquotes": ArticleCategory.SELF_GROWTH,      # 个人成长
        "advice_slip": ArticleCategory.PSYCHOLOGY,      # 心理知识
        "affirmations": ArticleCategory.EMOTION,        # 情绪管理
    }

    def __init__(self, source_url: Optional[str] = None):
        """
        初始化知识库同步服务

        Args:
            source_url: 可选的自定义数据源URL。如果为None，则使用DEFAULT_SOURCES中的所有源
        """
        self.source_url = source_url
        self.last_sync_time = None

    def set_source_url(self, source_url: str) -> None:
        """设置自定义数据源URL"""
        self.source_url = source_url

    async def fetch_from_zenquotes(self) -> List[Dict[str, Any]]:
        """从ZenQuotes API获取励志名言"""
        articles = []
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.DEFAULT_SOURCES["zenquotes"])
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        for item in data:
                            articles.append({
                                "title": f"每日名言：{item.get('q', '智慧名言')}",
                                "summary": f"出自 {item.get('a', '未知作者')}",
                                "content": f"""
**名言内容**

"{item.get('q', '')}"

**作者简介**

{item.get('a', '未知作者')}

**心灵感悟**

这句名言提醒我们，生活的意义不仅在于追求成功，更在于保持内心的平静与智慧。
当我们面对困难和挑战时，这些智慧的言语能够给我们力量和勇气。
                                """.strip(),
                                "category": "self_growth",
                                "tags": "励志,心理健康,名言警句,自我成长",
                                "mbti_types": "ENFP,INFP,ENFJ,INFJ",  # 适合理想主义者
                                "author": "ZenQuotes",
                            })
            loguru.logger.info(f"从ZenQuotes获取到 {len(articles)} 条名言")
        except Exception as e:
            loguru.logger.warning(f"从ZenQuotes获取名言失败: {e}")
        return articles

    async def fetch_from_advice_slip(self) -> List[Dict[str, Any]]:
        """从Advice Slip API获取生活建议"""
        articles = []
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.DEFAULT_SOURCES["advice_slip"])
                if response.status_code == 200:
                    data = response.json()
                    slip = data.get("slip", {})
                    if slip:
                        advice_text = slip.get("advice", "")
                        articles.append({
                            "title": f"生活建议：{advice_text[:30]}..." if len(advice_text) > 30 else f"生活建议：{advice_text}",
                            "summary": advice_text[:100] + "..." if len(advice_text) > 100 else advice_text,
                            "content": f"""
**建议内容**

{advice_text}

**应用场景**

这条建议可以帮助你在日常生活中更好地处理情绪和人际关系。
当我们学会倾听内心的声音，就能更好地理解自己和他人的需求。

**心理学解读**

从心理学的角度来看，这条建议涉及到自我认知和情绪管理的范畴。
它提醒我们要关注内心的感受，学会在适当的时候给自己一些空间和时间。
                            """.strip(),
                            "category": "psychology",
                            "tags": "生活建议,心理健康,自我成长,情绪管理",
                            "mbti_types": "INTJ,INTP,ENTP,ENFP",  # 适合思考者和直觉者
                            "author": "Advice Slip",
                        })
            loguru.logger.info(f"从Advice Slip获取到 {len(articles)} 条建议")
        except Exception as e:
            loguru.logger.warning(f"从Advice Slip获取建议失败: {e}")
        return articles

    async def fetch_from_affirmations(self) -> List[Dict[str, Any]]:
        """从Affirmations API获取正能量语录"""
        articles = []
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.DEFAULT_SOURCES["affirmations"])
                if response.status_code == 200:
                    data = response.json()
                    affirmation = data.get("affirmation", "")
                    if affirmation:
                        articles.append({
                            "title": f"正能量语录",
                            "summary": affirmation[:100] + "..." if len(affirmation) > 100 else affirmation,
                            "content": f"""
**正能量语录**

{affirmation}

**自我肯定的意义**

自我肯定是一种强大的心理技巧，它可以帮助我们建立积极的自我形象。
每天对自己说一些积极的话语，可以显著提升我们的心理健康和幸福感。

**实践方法**

1. 每天早晨对着镜子告诉自己："我很有价值"
2. 遇到困难时，深呼吸并默念："我有能力克服这个挑战"
3. 睡前感恩今天发生的美好事物

**适用人群**

适合所有需要情绪调节和心理支持的人群，
特别是正在经历焦虑、压力大或情绪低落的时期。
                            """.strip(),
                            "category": "emotion",
                            "tags": "正能量,自我肯定,情绪调节,心理健康",
                            "mbti_types": "ESFJ,ISFJ,ENFJ,INFJ",  # 适合情感型人格
                            "author": "Affirmations API",
                        })
            loguru.logger.info(f"从Affirmations获取到 {len(articles)} 条语录")
        except Exception as e:
            loguru.logger.warning(f"从Affirmations获取语录失败: {e}")
        return articles

    async def fetch_online_articles(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """从在线源获取文章

        如果配置了自定义source_url，则使用该单一源；
        否则从所有默认源（ZenQuotes, Advice Slip, Affirmations）获取文章。

        Args:
            category: 可选的分类过滤

        Returns:
            文章列表
        """
        all_articles = []

        if self.source_url:
            # 使用自定义单一数据源
            return await self._fetch_from_custom_source(self.source_url, category)

        # 从所有默认源获取
        try:
            results = await asyncio.gather(
                self.fetch_from_zenquotes(),
                self.fetch_from_advice_slip(),
                self.fetch_from_affirmations(),
                return_exceptions=True
            )

            for result in results:
                if isinstance(result, list):
                    all_articles.extend(result)
                elif isinstance(result, Exception):
                    loguru.logger.warning(f"获取在线文章时出错: {result}")

        except Exception as e:
            loguru.logger.warning(f"获取在线文章失败: {e}")

        # 按分类过滤
        if category:
            cat_enum = None
            try:
                cat_enum = ArticleCategory[category.upper()]
            except KeyError:
                pass
            if cat_enum:
                all_articles = [
                    a for a in all_articles
                    if a.get("category", "").upper() == category.upper()
                ]

        return all_articles

    async def _fetch_from_custom_source(self, source_url: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """从自定义数据源获取文章"""
        articles = []
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(source_url)

                if response.status_code == 200:
                    data = response.json()

                    # 尝试多种数据格式
                    items = []
                    if isinstance(data, list):
                        items = data
                    elif isinstance(data, dict):
                        if "articles" in data:
                            items = data["articles"]
                        elif "data" in data:
                            items = data["data"]
                        elif "results" in data:
                            items = data["results"]
                        else:
                            items = [data]

                    for item in items:
                        # 通用字段映射
                        title = item.get("title") or item.get("name") or item.get("quote") or item.get("advice") or item.get("affirmation", "无标题")
                        content = item.get("content") or item.get("description") or item.get("text") or item.get("body", "")
                        summary = item.get("summary") or item.get("excerpt") or (content[:100] + "..." if content else "")
                        tags = item.get("tags", "")
                        mbti_types = item.get("mbti_types", "")

                        if title and content:
                            cat_str = item.get("category", category or "psychology")
                            try:
                                cat_enum = ArticleCategory[cat_str.upper()]
                            except KeyError:
                                cat_enum = ArticleCategory.PSYCHOLOGY

                            articles.append({
                                "title": str(title),
                                "summary": str(summary)[:200],
                                "content": str(content),
                                "category": cat_str.lower(),
                                "tags": str(tags) if tags else "心理健康",
                                "mbti_types": str(mbti_types) if mbti_types else "",
                                "author": item.get("author") or item.get("source", "在线知识库"),
                            })

        except Exception as e:
            loguru.logger.warning(f"从自定义源 {source_url} 获取文章失败: {e}")

        return articles

    def sync_articles_to_db(self, db: Session, articles: List[Dict[str, Any]]) -> int:
        """将在线文章同步到数据库

        Args:
            db: 数据库会话
            articles: 文章列表

        Returns:
            同步的文章数量
        """
        synced_count = 0

        for article_data in articles:
            title = article_data.get("title", "")
            if not title:
                continue

            # 检查文章是否已存在（根据标题）
            existing = db.query(KnowledgeArticle).filter(
                KnowledgeArticle.title == title
            ).first()

            if existing:
                # 更新现有文章
                existing.summary = article_data.get("summary", existing.summary)
                existing.content = article_data.get("content", existing.content)
                existing.tags = article_data.get("tags", existing.tags)
                loguru.logger.debug(f"更新文章: {existing.title}")
            else:
                # 创建新文章
                category_str = article_data.get("category", "psychology")
                try:
                    category = ArticleCategory[category_str.upper()]
                except KeyError:
                    category = ArticleCategory.PSYCHOLOGY

                new_article = KnowledgeArticle(
                    title=title,
                    summary=article_data.get("summary", ""),
                    content=article_data["content"] if article_data.get("content") else article_data.get("summary", ""),
                    category=category,
                    tags=article_data.get("tags", ""),
                    mbti_types=article_data.get("mbti_types", ""),
                    author=article_data.get("author", "心灵伴侣AI"),
                    status=ArticleStatus.PUBLISHED,
                )
                db.add(new_article)
                loguru.logger.debug(f"新增文章: {new_article.title}")
                synced_count += 1

        db.commit()
        return synced_count

    async def sync_from_online(self, db: Session) -> Dict[str, Any]:
        """从在线源同步知识库

        Args:
            db: 数据库会话

        Returns:
            同步结果统计
        """
        result = {
            "success": False,
            "synced_count": 0,
            "total_online": 0,
            "message": "",
        }

        loguru.logger.info("开始从在线源同步知识库...")

        # 获取在线文章
        online_articles = await self.fetch_online_articles()

        if not online_articles:
            result["message"] = "没有找到在线文章或连接失败"
            return result

        result["total_online"] = len(online_articles)

        # 同步到数据库
        synced_count = self.sync_articles_to_db(db, online_articles)
        result["synced_count"] = synced_count
        result["success"] = True
        result["message"] = f"成功同步 {synced_count} 篇新文章"

        loguru.logger.info(f"知识库同步完成: {synced_count} 篇新文章")

        return result

    def get_local_articles_count(self, db: Session) -> int:
        """获取本地文章数量

        Args:
            db: 数据库会话

        Returns:
            文章总数
        """
        return db.query(KnowledgeArticle).count()

    def get_articles_by_category_from_db(self, db: Session, category: str) -> List[KnowledgeArticle]:
        """从数据库获取指定分类的文章

        Args:
            db: 数据库会话
            category: 分类名称

        Returns:
            文章列表
        """
        try:
            cat_enum = ArticleCategory[category.upper()]
            return db.query(KnowledgeArticle).filter(
                KnowledgeArticle.category == cat_enum,
                KnowledgeArticle.status == ArticleStatus.PUBLISHED
            ).all()
        except KeyError:
            return []

    def get_recommendations_for_user(
        self,
        db: Session,
        mbti_type: Optional[str] = None,
        attachment_style: Optional[str] = None,
        limit: int = 5
    ) -> List[KnowledgeArticle]:
        """根据用户画像推荐相关文章

        Args:
            db: 数据库会话
            mbti_type: MBTI类型
            attachment_style: 依恋风格
            limit: 返回数量

        Returns:
            推荐的文章列表
        """
        query = db.query(KnowledgeArticle).filter(
            KnowledgeArticle.status == ArticleStatus.PUBLISHED
        )

        # 如果有MBTI类型，优先返回相关的
        if mbti_type:
            mbti_articles = query.filter(
                KnowledgeArticle.mbti_types.contains(mbti_type.upper())
            ).limit(limit).all()

            if mbti_articles:
                return mbti_articles

        # 否则返回最新的文章
        return query.order_by(
            KnowledgeArticle.created_at.desc()
        ).limit(limit).all()


# 全局服务实例
_knowledge_sync_service: Optional[KnowledgeSyncService] = None


def get_knowledge_sync_service() -> KnowledgeSyncService:
    """获取知识库同步服务实例"""
    global _knowledge_sync_service
    if _knowledge_sync_service is None:
        _knowledge_sync_service = KnowledgeSyncService()
    return _knowledge_sync_service
