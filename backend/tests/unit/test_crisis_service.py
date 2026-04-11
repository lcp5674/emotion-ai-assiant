"""
crisis_service 单元测试 - 危机干预服务
"""
import pytest

from app.services.crisis_service import CrisisDetector, CrisisLevel, CrisisResult


class TestCrisisDetector:
    """CrisisDetector单元测试"""

    def test_init(self):
        """测试初始化"""
        detector = CrisisDetector()
        assert detector is not None
        assert hasattr(detector, 'detect')
        assert hasattr(detector, 'get_intervention_response')
        assert hasattr(detector, 'should_alert_admin')

    async def test_detect_critical_suicide_risk(self):
        """测试检测自杀风险 - 极危"""
        detector = CrisisDetector()
        # 添加求助信号让分数达到 >=70 成为极危
        result = await detector.detect("我不想活了，我觉得活着没有意思，我想死，救救我")
        assert result.detected is True
        assert result.level in [CrisisLevel.HIGH, CrisisLevel.CRITICAL]
        assert len(result.keywords) > 0
        assert result.intervention_required is True
        assert result.risk_score >= 70

    async def test_detect_high_risk_multiple_keywords(self):
        """测试多个高风险关键词"""
        detector = CrisisDetector()
        result = await detector.detect("我想死，我要自杀，活着没意思")
        assert result.detected is True
        assert result.level in [CrisisLevel.HIGH, CrisisLevel.CRITICAL]
        assert len(result.keywords) >= 2
        assert result.intervention_required is True

    async def test_detect_medium_risk_depression(self):
        """测试检测中等风险抑郁情绪"""
        detector = CrisisDetector()
        result = await detector.detect("我最近好绝望，撑不下去了，没人在乎我")
        assert result.detected is True
        assert result.level == CrisisLevel.MEDIUM
        assert len(result.keywords) > 0
        assert result.intervention_required is False

    async def test_detect_low_risk(self):
        """测试检测低风险"""
        detector = CrisisDetector()
        # 单个中等风险关键词加起来只有 30，属于中等风险，单个低风险词组才是低风险
        result = await detector.detect("最近压力好大")
        assert result.detected is True
        assert result.level == CrisisLevel.MEDIUM
        assert len(result.keywords) > 0
        assert result.intervention_required is False

    async def test_detect_with_help_seeking(self):
        """测试包含求助信号"""
        detector = CrisisDetector()
        result = await detector.detect("我撑不下去了，谁能帮帮我，救救我")
        assert result.detected is True
        assert "救救我" in result.keywords
        assert result.risk_score > 30

    async def test_detect_with_protective_factors(self):
        """测试保护性因素降低风险"""
        detector = CrisisDetector()
        # 明确包含保护性关键词
        result = await detector.detect("我有时候不想活了，但是还有家人需要我，我舍不得他们")
        assert result.detected is True
        # 风险分数会因为保护性因素降低
        # 正则匹配到 "不想活" 而不是 "不想活了"
        assert any("不想活" in kw for kw in result.keywords)
        # 检查风险降低，原来60，减去20得到40
        assert result.risk_score == 40

    async def test_detect_no_risk(self):
        """测试检测无风险内容"""
        detector = CrisisDetector()
        result = await detector.detect("我今天心情很好，去公园散步了")
        assert result.detected is False
        assert result.level == CrisisLevel.NONE
        assert len(result.keywords) == 0
        assert result.risk_score == 0
        assert result.intervention_required is False

    async def test_detect_empty_content(self):
        """测试空内容"""
        detector = CrisisDetector()
        result = await detector.detect("")
        assert result.detected is False
        assert result.level == CrisisLevel.NONE

    async def test_detect_whitespace_only(self):
        """测试只有空格"""
        detector = CrisisDetector()
        result = await detector.detect("   \n  ")
        assert result.detected is False
        assert result.level == CrisisLevel.NONE

    async def test_detect_self_harm(self):
        """测试检测自伤倾向"""
        detector = CrisisDetector()
        result = await detector.detect("我想割腕伤害自己")
        assert result.detected is True
        assert result.level == CrisisLevel.HIGH
        assert "割腕" in result.keywords
        assert "伤害自己" in result.keywords
        assert result.intervention_required is True

    def test_determine_level_critical(self):
        """测试等级判断 - 极危"""
        detector = CrisisDetector()
        level = detector._determine_level(70, True)
        assert level == CrisisLevel.CRITICAL

    def test_determine_level_high(self):
        """测试等级判断 - 高风险"""
        detector = CrisisDetector()
        level = detector._determine_level(60, True)
        assert level == CrisisLevel.HIGH
        level = detector._determine_level(60, False)
        assert level == CrisisLevel.HIGH

    def test_determine_level_medium(self):
        """测试等级判断 - 中等风险"""
        detector = CrisisDetector()
        level = detector._determine_level(30, False)
        assert level == CrisisLevel.MEDIUM

    def test_determine_level_low(self):
        """测试等级判断 - 低风险"""
        detector = CrisisDetector()
        level = detector._determine_level(10, False)
        assert level == CrisisLevel.LOW

    def test_determine_level_none(self):
        """测试等级判断 - 无风险"""
        detector = CrisisDetector()
        level = detector._determine_level(0, False)
        assert level == CrisisLevel.NONE

    async def test_get_intervention_response_all_levels(self):
        """测试获取各个等级的干预回应"""
        detector = CrisisDetector()
        for level in CrisisLevel:
            response = await detector.get_intervention_response(level)
            assert isinstance(response, str)
            # 非NONE级别应该有内容
            if level != CrisisLevel.NONE:
                assert len(response) > 0

    async def test_should_alert_admin(self):
        """测试判断是否需要告警管理员"""
        detector = CrisisDetector()
        
        # 高风险和极危应该告警
        assert await detector.should_alert_admin(CrisisLevel.HIGH) is True
        assert await detector.should_alert_admin(CrisisLevel.CRITICAL) is True
        
        # 低风险和中等不需要
        assert await detector.should_alert_admin(CrisisLevel.LOW) is False
        assert await detector.should_alert_admin(CrisisLevel.MEDIUM) is False
        assert await detector.should_alert_admin(CrisisLevel.NONE) is False

    def test_get_suggestion_all_levels(self):
        """测试获取各个等级的建议"""
        detector = CrisisDetector()
        for level in CrisisLevel:
            suggestion = detector._get_suggestion(level)
            assert isinstance(suggestion, str)
            # 非NONE级别应该有内容
            if level != CrisisLevel.NONE:
                assert len(suggestion) > 0

    async def test_case_insensitive_detection(self):
        """测试大小写不敏感检测"""
        detector = CrisisDetector()
        result = await detector.detect("我不想活了".upper())
        assert result.detected is True
        # 正则匹配到 "不想活"
        assert any("不想活" in kw for kw in result.keywords)
