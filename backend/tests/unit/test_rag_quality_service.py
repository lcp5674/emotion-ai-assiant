"""
RAG质量评估服务测试
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from app.services.rag.quality_assessment import RAGQualityService


class TestRAGQualityService:
    """RAG质量评估服务测试"""

    @pytest.fixture
    def db_session(self):
        """创建模拟数据库会话"""
        return Mock()

    @pytest.fixture
    def quality_service(self, db_session):
        """创建RAG质量服务实例"""
        return RAGQualityService(db_session)

    @pytest.fixture
    def mock_user_full_profile(self):
        """模拟完整用户画像"""
        user = Mock()
        user.id = 1
        user.mbti_type = "INTJ"
        user.personality_tags = "理性,独立,分析型"
        user.relationship_style = "回避型"
        user.communication_tips = ["喜欢直接沟通", "重视逻辑"]
        return user

    @pytest.fixture
    def mock_relevant_context(self):
        """模拟高度相关的上下文"""
        return [
            {
                "content": "INTJ人格适合深度分析类话题，讨论需要逻辑支撑。",
                "source": "mbti_knowledge",
                "relevance_score": 0.95,
            },
            {
                "content": "回避型依恋的人需要安全型伴侣给予安全感。",
                "source": "attachment_knowledge",
                "relevance_score": 0.90,
            },
        ]

    @pytest.fixture
    def mock_irrelevant_context(self):
        """模拟低相关性的上下文"""
        return [
            {
                "content": "这是一段关于天气的内容。",
                "source": "general",
                "relevance_score": 0.1,
            },
        ]

    # ========== 检索相关性测试 ==========

    def test_assess_retrieval_relevance_high(
        self, quality_service, mock_relevant_context
    ):
        """测试高相关性检索"""
        result = quality_service.assess_retrieval_relevance(
            query="INTJ人格的特点是什么？",
            context=mock_relevant_context
        )

        assert result["score"] >= 0.85
        assert result["status"] == "high"
        assert len(result["top_chunks"]) >= 2

    def test_assess_retrieval_relevance_low(
        self, quality_service, mock_irrelevant_context
    ):
        """测试低相关性检索"""
        result = quality_service.assess_retrieval_relevance(
            query="INTJ人格的特点是什么？",
            context=mock_irrelevant_context
        )

        assert result["score"] < 0.5
        assert result["status"] == "low"
        assert len(result["warnings"]) > 0

    def test_assess_retrieval_relevance_empty_context(self, quality_service):
        """测试空上下文"""
        result = quality_service.assess_retrieval_relevance(
            query="INTJ人格的特点是什么？",
            context=[]
        )

        assert result["score"] == 0.0
        assert result["status"] == "no_context"
        assert "检索不到相关内容" in result["warnings"][0]

    def test_assess_retrieval_relevance_with_scores(
        self, quality_service, mock_relevant_context
    ):
        """测试带分数的相关性评估"""
        result = quality_service.assess_retrieval_relevance(
            query="INTJ人格的特点",
            context=mock_relevant_context,
            min_threshold=0.5
        )

        assert "average_score" in result
        assert "max_score" in result
        assert result["max_score"] >= result["average_score"]

    # ========== 事实准确性测试 ==========

    def test_assess_factual_accuracy_valid(self, quality_service):
        """测试准确的事实检查"""
        answer = "INTJ人格类型约占人口的2%，他们被称为策划者。"
        context = [
            {"content": "INTJ约占人口2%，被称为策划者或建筑师。", "source": "official"},
        ]

        result = quality_service.assess_factual_accuracy(
            answer=answer,
            context=context,
            mbti_type="INTJ"
        )

        assert result["score"] >= 0.8
        assert len(result["inconsistencies"]) == 0

    def test_assess_factual_accuracy_mbti_mismatch(self, quality_service):
        """测试MBTI类型不匹配"""
        answer = "INTJ人格类型的人感情丰富，喜欢社交活动。"
        context = [
            {"content": "INTJ是内向、直觉、思考、判断型，重视逻辑和独立。", "source": "official"},
        ]

        result = quality_service.assess_factual_accuracy(
            answer=answer,
            context=context,
            mbti_type="INTJ"
        )

        assert result["score"] < 0.6
        assert len(result["inconsistencies"]) > 0
        assert any("内向" in str(result["inconsistencies"]) or "逻辑" in str(result["inconsistencies"]))

    def test_assess_factual_accuracy_incomplete_context(self, quality_service):
        """测试上下文不完整时的准确性"""
        answer = "这是一个复杂的问题，需要更多上下文才能准确回答。"
        context = []

        result = quality_service.assess_factual_accuracy(
            answer=answer,
            context=context,
            mbti_type="INTJ"
        )

        # 不完整上下文可能限制准确性评估
        assert "uncertainty_flagged" in result

    # ========== 个性化程度测试 ==========

    def test_assess_personalization_full_profile(
        self, quality_service, mock_user_full_profile
    ):
        """测试完整画像的个性化评估"""
        answer = "作为INTJ类型的你，我建议你可以尝试..."  # 包含MBTI引用
        context = [
            {"content": "INTJ类型特点...", "source": "mbti"},
        ]

        result = quality_service.assess_personalization(
            answer=answer,
            context=context,
            user=mock_user_full_profile
        )

        assert result["score"] >= 0.6
        assert result["level"] in ["high", "medium"]

    def test_assess_personalization_generic_answer(self, quality_service, mock_user_full_profile):
        """测试通用回答的个性化评估"""
        answer = "这是一个常见问题，我给你一些建议..."
        context = []

        result = quality_service.assess_personalization(
            answer=answer,
            context=context,
            user=mock_user_full_profile
        )

        assert result["score"] < 0.4
        assert result["level"] == "low"
        assert len(result["suggestions"]) > 0

    def test_assess_personalization_no_profile(self, quality_service):
        """测试无画像时的个性化评估"""
        answer = "作为INTJ类型的你..."
        context = []
        user = None

        result = quality_service.assess_personalization(
            answer=answer,
            context=context,
            user=user
        )

        assert result["score"] == 0.0
        assert result["level"] == "none"

    # ========== 回答长度质量测试 ==========

    def test_assess_length_quality_optimal(self, quality_service):
        """测试最优长度的回答"""
        answer = "A" * 500  # 500字符
        result = quality_service.assess_length_quality(answer)

        assert result["score"] >= 0.8
        assert result["status"] == "optimal"

    def test_assess_length_quality_too_short(self, quality_service):
        """测试过短的回答"""
        answer = "A" * 30  # 30字符
        result = quality_service.assess_length_quality(answer)

        assert result["score"] < 0.5
        assert result["status"] == "too_short"
        assert "建议" in str(result)

    def test_assess_length_quality_too_long(self, quality_service):
        """测试过长的回答"""
        answer = "A" * 2000  # 2000字符
        result = quality_service.assess_length_quality(answer)

        assert result["score"] < 0.6
        assert result["status"] == "too_long"
        assert "建议" in str(result)

    def test_assess_length_quality_empty(self, quality_service):
        """测试空回答"""
        answer = ""
        result = quality_service.assess_length_quality(answer)

        assert result["score"] == 0.0
        assert result["status"] == "empty"

    # ========== 安全性检查测试 ==========

    def test_assess_safety_normal_content(self, quality_service):
        """测试正常内容"""
        answer = "今天天气很好，心情也很不错！"
        result = quality_service.assess_safety(answer)

        assert result["score"] >= 0.9
        assert result["level"] == "safe"
        assert len(result["concerns"]) == 0

    def test_assess_safety_mild_concern(self, quality_service):
        """测试轻微担忧内容"""
        answer = "最近有点心情低落，不过还好"
        result = quality_service.assess_safety(answer)

        # 轻微情绪不应该是高风险
        assert result["level"] in ["safe", "monitor"]
        assert len(result["concerns"]) == 0 or len(result["concerns"]) == 1

    def test_assess_safety_crisis_detected(self, quality_service):
        """测试检测到危机内容"""
        answer = "我不想活了，觉得活着没意思"
        result = quality_service.assess_safety(answer)

        assert result["level"] == "crisis"
        assert len(result["concerns"]) > 0
        assert any("自杀" in c.lower() or "自残" in c.lower() for c in result["concerns"])

    # ========== 危机内容检测测试 ==========

    def test_check_crisis_content_explicit(self, quality_service):
        """测试显式危机内容"""
        texts = [
            "我不想活了",
            "活着没意思，想死",
            "想结束自己的生命",
            "想用刀割伤自己",
        ]

        for text in texts:
            result = quality_service.check_crisis_content(text)
            assert result["detected"] == True, f"Should detect crisis in: {text}"
            assert result["level"] in ["high", "critical"]

    def test_check_crisis_content_implicit(self, quality_service):
        """测试隐式危机内容"""
        texts = [
            "感觉自己是个负担",
            "没人会在意我消失",
            "一切都没有意义了",
        ]

        for text in texts:
            result = quality_service.check_crisis_content(text)
            # 隐式内容可能检测到也可能检测不到
            assert "level" in result

    def test_check_crisis_content_safe(self, quality_service):
        """测试安全内容"""
        texts = [
            "今天天气真好",
            "工作有点累",
            "想换个发型",
        ]

        for text in texts:
            result = quality_service.check_crisis_content(text)
            assert result["detected"] == False

    # ========== 危机转介响应测试 ==========

    def test_generate_crisis_response(self, quality_service):
        """测试危机转介响应生成"""
        crisis_keywords = ["自杀", "想死"]

        result = quality_service.generate_crisis_response(crisis_keywords)

        assert "empathy" in result
        assert "encourage_contact" in result
        assert "resources" in result
        assert result["should_refer"] == True
        assert any("热线" in str(result["resources"]) or "电话" in str(result))

    def test_generate_crisis_response_specific_keywords(self, quality_service):
        """测试针对特定关键词的响应"""
        crisis_keywords = ["自残", "割腕"]

        result = quality_service.generate_crisis_response(crisis_keywords)

        assert result["should_refer"] == True
        assert len(result["empathy"]) > 0


class TestRAGQualityServiceIntegration:
    """RAG质量服务集成测试"""

    @pytest.fixture
    def quality_service(self):
        """创建服务实例"""
        return RAGQualityService(Mock())

    def test_full_quality_assessment(self, quality_service, mock_user_full_profile):
        """测试完整质量评估流程"""
        # 模拟完整的对话场景
        query = "作为INTJ，我应该如何改善人际关系？"
        answer = """作为INTJ类型的你，拥有出色的分析能力和战略思维。

优势：
- 逻辑清晰，善于发现问题的本质
- 独立自主，不依赖他人认可
- 目标导向，效率很高

建议：
1. 主动表达情感，让他人感受到你的关心
2. 社交时保持耐心，理解不同类型的人
3. 可以寻找同样理性思维的朋友

你的人际关系的改善需要时间，但你的潜力很大！"""

        context = [
            {"content": "INTJ是内向直觉思考判断型，善于分析。", "source": "mbti", "relevance_score": 0.95},
            {"content": "INTJ在人际交往中需要学习表达情感。", "source": "mbti_advice", "relevance_score": 0.90},
        ]

        # 执行完整评估
        result = quality_service.full_quality_assessment(
            query=query,
            answer=answer,
            context=context,
            user=mock_user_full_profile
        )

        # 验证综合评分结构
        assert "overall_score" in result
        assert "dimension_scores" in result
        assert "status" in result
        assert "suggestions" in result

        # 验证权重计算
        dimension_scores = result["dimension_scores"]
        expected_composite = (
            dimension_scores["relevance"] * 0.35 +
            dimension_scores["accuracy"] * 0.30 +
            dimension_scores["personalization"] * 0.15 +
            dimension_scores["length"] * 0.10 +
            dimension_scores["safety"] * 0.10
        )

        # 允许小数精度误差
        assert abs(result["overall_score"] - expected_composite) < 0.01

    def test_quality_assessment_low_scores(self, quality_service):
        """测试低质量回答的评估"""
        query = "MBTI是什么？"
        answer = "MBTI是个性测试。"  # 过于简短
        context = []  # 无上下文
        user = None  # 无用户画像

        result = quality_service.full_quality_assessment(
            query=query,
            answer=answer,
            context=context,
            user=user
        )

        assert result["overall_score"] < 0.4
        assert result["status"] == "poor"
        assert len(result["suggestions"]) > 0


class TestRAGQualityServiceEdgeCases:
    """边界情况测试"""

    def test_unicode_handling(self):
        """测试Unicode字符处理"""
        service = RAGQualityService(Mock())

        answer = "今天心情很好😊，想和人聊天💬"
        result = service.assess_length_quality(answer)

        assert "length" in result
        assert result["length"] == len(answer)

    def test_empty_query(self):
        """测试空查询"""
        service = RAGQualityService(Mock())

        result = service.assess_retrieval_relevance(
            query="",
            context=[]
        )

        assert result["score"] == 0.0

    def test_malformed_context(self):
        """测试格式错误的上下文"""
        service = RAGQualityService(Mock())

        # 缺少必需字段的上下文
        malformed_context = [
            {"source": "test"},  # 缺少content
            "not a dict",  # 甚至不是字典
        ]

        result = service.assess_retrieval_relevance(
            query="test",
            context=malformed_context
        )

        # 应该优雅处理
        assert "score" in result
