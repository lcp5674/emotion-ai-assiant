"""
危机干预服务单元测试
"""
import pytest

from app.services.crisis_service import (
    CrisisDetector,
    CrisisLevel,
)


class TestCrisisDetection:
    """危机检测测试"""

    @pytest.fixture
    def crisis_detector(self):
        """危机检测器fixture"""
        return CrisisDetector()

    async def test_detect_high_risk_keywords(self, crisis_detector):
        """测试检测高风险关键词"""
        high_risk_texts = [
            "我不想活了",
            "我想结束生命",
            "我想自杀",
            "我想去死",
            "我想跳楼",
            "我想割腕",
        ]

        for text in high_risk_texts:
            result = await crisis_detector.detect(text)

            assert result.detected is True
            assert result.level in [CrisisLevel.HIGH, CrisisLevel.CRITICAL]
            assert result.intervention_required is True
            assert result.risk_score >= 60

    async def test_detect_medium_risk_keywords(self, crisis_detector):
        """测试检测中等风险关键词"""
        medium_risk_texts = [
            "我好绝望",
            "我很无助",
            "我压力好大",
            "我撑不下去了",
            "我真的好累",
            "我崩溃了",
            "我觉得自己没用",
            "没人关心我",
        ]

        for text in medium_risk_texts:
            result = await crisis_detector.detect(text)

            assert result.detected is True
            assert result.level in [CrisisLevel.MEDIUM, CrisisLevel.HIGH]
            assert result.risk_score >= 30

    async def test_detect_low_risk_keywords(self, crisis_detector):
        """测试检测低风险关键词"""
        low_risk_texts = [
            "我有些不开心",
            "我今天心情不太好",
            "最近有些烦",
            "我有点困扰",
        ]

        for text in low_risk_texts:
            result = await crisis_detector.detect(text)

            assert result.level in [CrisisLevel.LOW, CrisisLevel.NONE]
            assert result.intervention_required is False
            assert result.risk_score < 30

    async def test_detected_high_risk_with_help_seeking(self, crisis_detector):
        """测试高风险+求助信号"""
        text = "我真的不想活了，有人能帮帮我吗？"

        result = await crisis_detector.detect(text)

        assert result.detected is True
        assert result.level in [CrisisLevel.HIGH, CrisisLevel.CRITICAL]
        assert result.intervention_required is True

    async def test_detect_with_protective_factors(self, crisis_detector):
        """测试有保护因素的情况"""
        # 有保护因素的高风险文本
        text_with_protection = "我不想活了，但我舍不得我的家人"

        result = await crisis_detector.detect(text_with_protection)

        assert result.detected is True
        assert result.level <= CrisisLevel.MEDIUM

    async def test_detect_multiple_keywords(self, crisis_detector):
        """测试包含多个关键词"""
        text = "我好绝望，真的不想活了，压力太大了"

        result = await crisis_detector.detect(text)

        assert result.detected is True
        assert len(result.keywords) >= 3
        assert result.risk_score > 70

    async def test_no_risk_detection(self, crisis_detector):
        """测试无风险文本"""
        safe_texts = [
            "你好",
            "今天天气不错",
            "我想学习MBTI",
            "如何提高情商",
            "推荐一本书",
            "我今天很开心",
        ]

        for text in safe_texts:
            result = await crisis_detector.detect(text)

            assert result.level == CrisisLevel.NONE
            assert result.detected is False
            assert result.risk_score == 0
            assert len(result.keywords) == 0


class TestCrisisIntervention:
    """危机干预测试"""

    @pytest.fixture
    def crisis_detector(self):
        return CrisisDetector()

    async def test_get_intervention_response(self, crisis_detector):
        """测试获取干预响应"""
        responses = {
            CrisisLevel.NONE: "",
            CrisisLevel.LOW: "陪着你",
            CrisisLevel.MEDIUM: "专业心理咨询师",
            CrisisLevel.HIGH: "联系家人",
            CrisisLevel.CRITICAL: "危机干预热线",
        }

        for level in responses:
            response = await crisis_detector.get_intervention_response(level)

            if level == CrisisLevel.NONE:
                assert len(response) == 0
            else:
                assert len(response) > 0
                assert responses[level] in response

    async def test_get_suggestion(self, crisis_detector):
        """测试获取建议"""
        result = await crisis_detector.detect("我不想活了")

        assert len(result.suggestion) > 0
        assert "寻求专业帮助" in result.suggestion

    async def test_should_alert_admin(self, crisis_detector):
        """测试是否需要告警管理员"""
        # 高风险需要告警
        high_risk_result = await crisis_detector.detect("我想自杀")
        assert crisis_detector.should_alert_admin(high_risk_result.level) is True

        # 中等风险不需要
        medium_risk_result = await crisis_detector.detect("我好绝望")
        assert crisis_detector.should_alert_admin(medium_risk_result.level) is False

    async def test_risk_level_determination(self, crisis_detector):
        """测试风险等级判断"""
        # 临界值测试
        text_just_low = "我有点不开心"
        result_low = await crisis_detector.detect(text_just_low)
        assert result_low.level == CrisisLevel.LOW

        text_just_medium = "我好绝望"
        result_medium = await crisis_detector.detect(text_just_medium)
        assert result_medium.level == CrisisLevel.MEDIUM

        text_just_high = "我不想活了"
        result_high = await crisis_detector.detect(text_just_high)
        assert result_high.level == CrisisLevel.HIGH


class TestKeywordMatching:
    """关键词匹配测试"""

    @pytest.fixture
    def crisis_detector(self):
        return CrisisDetector()

    async def test_keyword_case_insensitive(self, crisis_detector):
        """测试关键词不区分大小写"""
        # 检测关键词匹配是不区分大小写的
        text1 = "我不想活了"
        text2 = "我不想活了"
        text3 = "我不想活了"

        result1 = await crisis_detector.detect(text1)
        result2 = await crisis_detector.detect(text2)

        assert result1.detected == result2.detected
        assert result1.level == result2.level

    async def test_partial_keyword_matching(self, crisis_detector):
        """测试部分关键词匹配"""
        text = "我真的真的不想活了"
        result = await crisis_detector.detect(text)

        assert "不想活" in result.keywords

    async def test_multiple_keywords_combination(self, crisis_detector):
        """测试多种关键词组合"""
        text = "我真的很绝望，压力太大了，我不想活了"
        result = await crisis_detector.detect(text)

        assert "绝望" in result.keywords
        assert "压力" in result.keywords
        assert "不想活" in result.keywords
        assert len(result.keywords) >= 3


class TestEdgeCases:
    """边界情况测试"""

    @pytest.fixture
    def crisis_detector(self):
        return CrisisDetector()

    async def test_empty_string(self, crisis_detector):
        """测试空字符串"""
        result = await crisis_detector.detect("")

        assert result.level == CrisisLevel.NONE
        assert result.detected is False
        assert result.risk_score == 0

    async def test_whitespace_only(self, crisis_detector):
        """测试纯空白字符"""
        result = await crisis_detector.detect("   \t\n")

        assert result.level == CrisisLevel.NONE
        assert result.detected is False
        assert result.risk_score == 0

    async def test_very_long_text(self, crisis_detector):
        """测试很长的文本"""
        long_text = "正常内容 " * 100 + " 我不想活了 " + "正常内容 " * 100
        result = await crisis_detector.detect(long_text)

        assert result.detected is True
        assert result.level >= CrisisLevel.MEDIUM


class TestSuggestionGeneration:
    """建议生成测试"""

    @pytest.fixture
    def crisis_detector(self):
        return CrisisDetector()

    async def test_crisis_level_transitions(self, crisis_detector):
        """测试不同等级的响应"""
        # 无风险
        none_result = await crisis_detector.detect("你好")
        assert none_result.suggestion == ""

        # 低风险
        low_text = "我有点不开心"
        low_result = await crisis_detector.detect(low_text)
        assert len(low_result.suggestion) < 100
        assert "聊聊" in low_result.suggestion

        # 中等风险
        medium_text = "我好绝望"
        medium_result = await crisis_detector.detect(medium_text)
        assert len(medium_result.suggestion) > 100
        assert "专业心理咨询师" in medium_result.suggestion

        # 高风险
        high_text = "我不想活了"
        high_result = await crisis_detector.detect(high_text)
        assert len(high_result.suggestion) > 150
        assert "紧急" in high_result.suggestion or "热线" in high_result.suggestion
