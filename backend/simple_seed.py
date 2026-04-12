#!/usr/bin/env python3
"""
简单的知识库数据种子脚本
"""
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import enum

# 创建SQLite引擎
engine = create_engine('sqlite:///./emotion_ai.db', connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 枚举类
class ArticleStatus(enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class ArticleCategory(enum.Enum):
    EMOTION = "emotion"
    RELATIONSHIP = "relationship"
    SELF_GROWTH = "self_growth"
    PSYCHOLOGY = "psychology"
    LOVE = "love"
    FAMILY = "family"
    CAREER = "career"

# 模型定义
class KnowledgeArticle(Base):
    __tablename__ = "knowledge_articles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    summary = Column(String(500), nullable=True)
    content = Column(Text, nullable=False)
    content_html = Column(Text, nullable=True)
    category = Column(Enum(ArticleCategory), nullable=False)
    tags = Column(String(500), nullable=True)
    mbti_types = Column(String(100), nullable=True)
    vector_id = Column(String(100), nullable=True)
    status = Column(Enum(ArticleStatus), default=ArticleStatus.DRAFT)
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    cover_image = Column(String(500), nullable=True)
    author = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    published_at = Column(DateTime, nullable=True)

class Banner(Base):
    __tablename__ = "banners"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    image_url = Column(String(500), nullable=False)
    link_url = Column(String(500), nullable=True)
    link_type = Column(String(20), nullable=True)
    position = Column(String(20), default="home")
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    content_type = Column(String(20), default="text")
    is_active = Column(Boolean, default=True)
    is_top = Column(Boolean, default=False)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

# 创建表结构
def create_tables():
    Base.metadata.create_all(bind=engine)
    print("表结构创建完成")

# 添加测试数据
def seed_data():
    db = SessionLocal()
    
    # 检查是否已有数据
    existing_article = db.query(KnowledgeArticle).first()
    if existing_article:
        print("知识库文章已存在，跳过添加")
        return
    
    # 添加文章
    articles = [
        KnowledgeArticle(
            title="如何管理负面情绪",
            summary="学习如何识别和管理负面情绪，保持心理健康",
            content="# 如何管理负面情绪\n\n负面情绪是每个人都会经历的，重要的是学会如何管理它们。\n\n## 识别情绪\n首先要学会识别自己的情绪，了解情绪的来源。\n\n## 接受情绪\n不要压抑情绪，而是接受它们的存在。\n\n## 应对策略\n- 深呼吸\n- 运动\n- 写日记\n- 寻求支持\n",
            content_html="<h1>如何管理负面情绪</h1><p>负面情绪是每个人都会经历的，重要的是学会如何管理它们。</p><h2>识别情绪</h2><p>首先要学会识别自己的情绪，了解情绪的来源。</p><h2>接受情绪</h2><p>不要压抑情绪，而是接受它们的存在。</p><h2>应对策略</h2><ul><li>深呼吸</li><li>运动</li><li>写日记</li><li>寻求支持</li></ul>",
            category=ArticleCategory.EMOTION,
            tags="情绪管理,心理健康",
            status=ArticleStatus.PUBLISHED,
            cover_image="https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=person%20meditating%20calm%20peaceful%20mindfulness&image_size=landscape_16_9",
            author="心理专家"
        ),
        KnowledgeArticle(
            title="建立健康的人际关系",
            summary="学习如何建立和维护健康的人际关系",
            content="# 建立健康的人际关系\n\n良好的人际关系对心理健康至关重要。\n\n## 沟通技巧\n- 积极倾听\n- 表达感受\n- 尊重他人\n\n## 边界设置\n学会设置健康的边界，保护自己的心理空间。\n\n## 冲突解决\n有效解决冲突，维护关系的和谐。\n",
            content_html="<h1>建立健康的人际关系</h1><p>良好的人际关系对心理健康至关重要。</p><h2>沟通技巧</h2><ul><li>积极倾听</li><li>表达感受</li><li>尊重他人</li></ul><h2>边界设置</h2><p>学会设置健康的边界，保护自己的心理空间。</p><h2>冲突解决</h2><p>有效解决冲突，维护关系的和谐。</p>",
            category=ArticleCategory.RELATIONSHIP,
            tags="人际关系,沟通技巧",
            status=ArticleStatus.PUBLISHED,
            cover_image="https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=group%20of%20friends%20talking%20happily%20social%20connection&image_size=landscape_16_9",
            author="人际关系专家"
        ),
        KnowledgeArticle(
            title="MBTI人格类型与职业选择",
            summary="了解不同MBTI类型适合的职业方向",
            content="# MBTI人格类型与职业选择\n\nMBTI可以帮助你了解自己的优势和适合的职业方向。\n\n## ISTJ\n适合：会计、审计、行政管理\n\n## ENFP\n适合：营销、创意、教育\n\n## INTJ\n适合：战略规划、科研、技术开发\n\n## ESFJ\n适合：教育、护理、人力资源\n",
            content_html="<h1>MBTI人格类型与职业选择</h1><p>MBTI可以帮助你了解自己的优势和适合的职业方向。</p><h2>ISTJ</h2><p>适合：会计、审计、行政管理</p><h2>ENFP</h2><p>适合：营销、创意、教育</p><h2>INTJ</h2><p>适合：战略规划、科研、技术开发</p><h2>ESFJ</h2><p>适合：教育、护理、人力资源</p>",
            category=ArticleCategory.PSYCHOLOGY,
            tags="MBTI,职业规划",
            status=ArticleStatus.PUBLISHED,
            cover_image="https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=professional%20person%20working%20career%20success&image_size=landscape_16_9",
            author="职业顾问"
        ),
        KnowledgeArticle(
            title="恋爱中的沟通技巧",
            summary="学习如何在恋爱关系中有效沟通",
            content="# 恋爱中的沟通技巧\n\n良好的沟通是健康恋爱关系的基础。\n\n## 表达需求\n学会清晰表达自己的需求和感受。\n\n## 倾听技巧\n积极倾听伴侣的想法和感受。\n\n## 处理冲突\n以建设性的方式处理分歧和冲突。\n",
            content_html="<h1>恋爱中的沟通技巧</h1><p>良好的沟通是健康恋爱关系的基础。</p><h2>表达需求</h2><p>学会清晰表达自己的需求和感受。</p><h2>倾听技巧</h2><p>积极倾听伴侣的想法和感受。</p><h2>处理冲突</h2><p>以建设性的方式处理分歧和冲突。</p>",
            category=ArticleCategory.LOVE,
            tags="恋爱,沟通",
            status=ArticleStatus.PUBLISHED,
            cover_image="https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=couple%20talking%20intimately%20relationship%20communication&image_size=landscape_16_9",
            author="情感专家"
        ),
        KnowledgeArticle(
            title="个人成长的五个步骤",
            summary="踏上个人成长之旅的实用指南",
            content="# 个人成长的五个步骤\n\n个人成长是一个持续的过程，需要有意识的努力。\n\n## 自我觉察\n了解自己的优势、劣势和价值观。\n\n## 设定目标\n制定明确、可实现的个人目标。\n\n## 学习与成长\n持续学习新技能和知识。\n\n## 行动与实践\n将所学应用到实际生活中。\n\n## 反思与调整\n定期反思进展，调整方向。\n",
            content_html="<h1>个人成长的五个步骤</h1><p>个人成长是一个持续的过程，需要有意识的努力。</p><h2>自我觉察</h2><p>了解自己的优势、劣势和价值观。</p><h2>设定目标</h2><p>制定明确、可实现的个人目标。</p><h2>学习与成长</h2><p>持续学习新技能和知识。</p><h2>行动与实践</h2><p>将所学应用到实际生活中。</p><h2>反思与调整</h2><p>定期反思进展，调整方向。</p>",
            category=ArticleCategory.SELF_GROWTH,
            tags="个人成长,自我提升",
            status=ArticleStatus.PUBLISHED,
            cover_image="https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=person%20climbing%20mountain%20growth%20journey&image_size=landscape_16_9",
            author="个人成长教练"
        )
    ]
    
    for article in articles:
        db.add(article)
    
    # 添加Banner
    banners = [
        Banner(
            title="MBTI测试",
            image_url="https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=MBTI%20personality%20test%20psychology%20infographic&image_size=landscape_16_9",
            link_url="/mbti",
            link_type="internal",
            position="home",
            is_active=True,
            sort_order=10
        ),
        Banner(
            title="情感日记",
            image_url="https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=person%20writing%20diary%20emotion%20journal&image_size=landscape_16_9",
            link_url="/diary",
            link_type="internal",
            position="home",
            is_active=True,
            sort_order=9
        ),
        Banner(
            title="AI助手",
            image_url="https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=AI%20assistant%20robot%20helpful%20friendly&image_size=landscape_16_9",
            link_url="/assistants",
            link_type="internal",
            position="home",
            is_active=True,
            sort_order=8
        )
    ]
    
    for banner in banners:
        db.add(banner)
    
    # 添加公告
    announcements = [
        Announcement(
            title="系统更新通知",
            content="尊敬的用户，我们已于近期完成系统更新，新增了情感日记功能，欢迎体验！",
            content_type="text",
            is_active=True,
            is_top=True
        )
    ]
    
    for announcement in announcements:
        db.add(announcement)
    
    db.commit()
    print(f"添加了 {len(articles)} 篇知识库文章")
    print(f"添加了 {len(banners)} 个Banner")
    print(f"添加了 {len(announcements)} 条公告")

if __name__ == "__main__":
    print("开始添加知识库测试数据...")
    create_tables()
    seed_data()
    print("知识库测试数据添加完成！")
