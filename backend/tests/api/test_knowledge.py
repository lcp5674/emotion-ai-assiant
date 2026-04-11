"""
知识库相关接口测试
"""
import pytest


def test_get_articles(authorized_client, test_user, db_session):
    """测试获取文章列表接口"""
    from app.models.knowledge import KnowledgeArticle, ArticleStatus, ArticleCategory
    # 创建一篇测试文章
    article = KnowledgeArticle(
        title="测试文章",
        summary="这是一篇测试文章",
        content_html="<p>测试内容</p>",
        category=ArticleCategory.EMOTION,
        status=ArticleStatus.PUBLISHED,
        tags="测试,情绪"
    )
    db_session.add(article)
    db_session.commit()
    
    response = authorized_client.get("/api/v1/knowledge/articles?page=1&page_size=10&category=emotion")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "list" in data
    assert isinstance(data["list"], list)
    assert len(data["list"]) >= 1


def test_get_article_detail(authorized_client, test_user, db_session):
    """测试获取文章详情接口"""
    from app.models.knowledge import KnowledgeArticle, ArticleStatus, ArticleCategory
    article = KnowledgeArticle(
        title="详情测试",
        summary="测试摘要",
        content_html="<p>测试详情内容</p>",
        category=ArticleCategory.EMOTION,
        status=ArticleStatus.PUBLISHED,
    )
    db_session.add(article)
    db_session.commit()
    
    response = authorized_client.get(f"/api/v1/knowledge/articles/{article.id}")
    assert response.status_code == 200
    data = response.json()
    assert "article" in data
    assert "related_articles" in data
    assert data["article"]["id"] == article.id
    assert data["article"]["title"] == "详情测试"


def test_get_article_not_found(authorized_client):
    """测试文章不存在"""
    response = authorized_client.get("/api/v1/knowledge/articles/99999")
    assert response.status_code == 404


def test_get_banners(authorized_client):
    """测试获取Banner列表接口"""
    response = authorized_client.get("/api/v1/knowledge/banners?position=home")
    assert response.status_code == 200
    data = response.json()
    assert "list" in data
    assert isinstance(data["list"], list)


def test_get_announcements(authorized_client):
    """测试获取公告列表接口"""
    response = authorized_client.get("/api/v1/knowledge/announcements")
    assert response.status_code == 200
    data = response.json()
    assert "list" in data
    assert isinstance(data["list"], list)


def test_collect_article(authorized_client, test_user, db_session):
    """测试收藏/取消收藏文章接口"""
    from app.models.knowledge import KnowledgeArticle, ArticleStatus, ArticleCategory
    article = KnowledgeArticle(
        title="收藏测试",
        summary="测试摘要",
        category=ArticleCategory.EMOTION,
        status=ArticleStatus.PUBLISHED,
    )
    db_session.add(article)
    db_session.commit()
    
    # 收藏文章
    response = authorized_client.post(f"/api/v1/knowledge/articles/{article.id}/collect")
    assert response.status_code == 200
    data = response.json()
    assert data["is_collected"] == True
    
    # 取消收藏
    response = authorized_client.post(f"/api/v1/knowledge/articles/{article.id}/collect")
    assert response.status_code == 200
    data = response.json()
    assert data["is_collected"] == False


def test_collect_article_not_found(authorized_client, test_user):
    """测试收藏不存在文章"""
    response = authorized_client.post("/api/v1/knowledge/articles/99999/collect")
    assert response.status_code == 404


def test_get_collections(authorized_client, test_user, db_session):
    """测试获取收藏文章列表接口"""
    response = authorized_client.get("/api/v1/knowledge/collections?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "list" in data
    assert isinstance(data["list"], list)


def test_public_access(client):
    """测试公开接口访问"""
    # 知识库文章列表应该允许公开访问
    response = client.get("/api/v1/knowledge/articles")
    assert response.status_code == 200
    
    response = client.get("/api/v1/knowledge/banners")
    assert response.status_code == 200
    
    response = client.get("/api/v1/knowledge/announcements")
    assert response.status_code == 200
