# -*- coding: utf-8 -*-
"""
SBTI服务单元测试
"""
import pytest
from unittest.mock import MagicMock, patch
from app.services.sbti_service import SbtiService, THEME_34, DOMAINS, SBTI_QUESTIONS_DATA


class TestSbtiService:
    """SBTI服务测试"""

    def setup_method(self):
        """测试前准备"""
        self.service = SbtiService()

    def test_theme_34_count(self):
        """测试34项才干主题"""
        assert len(THEME_34) == 34, f"应该有34个才干主题，实际有{len(THEME_34)}个"

    def test_domains(self):
        """测试四大领域"""
        assert len(DOMAINS) == 4
        assert set(DOMAINS) == {"executing", "influencing", "relationship", "strategic"}

    def test_questions_count(self):
        """测试题目数量"""
        assert len(SBTI_QUESTIONS_DATA) == 24

    def test_calculate_result_all_a(self):
        """测试全部选择A的计算结果"""
        mock_db = MagicMock()

        # 模拟24道题全部选A
        answers = []
        for i, q in enumerate(SBTI_QUESTIONS_DATA, 1):
            answers.append({
                "question_id": i,
                "answer": "A"
            })

        result = self.service.calculate_result(mock_db, user_id=1, answers=answers)

        # 验证返回结构
        assert "top5_themes" in result
        assert "top5_scores" in result
        assert "domain_scores" in result
        assert "dominant_domain" in result
        assert "relationship_insights" in result

        # 验证TOP5
        assert len(result["top5_themes"]) == 5
        assert len(result["top5_scores"]) == 5

        # 验证领域得分
        assert set(result["domain_scores"].keys()) == set(DOMAINS)

    def test_calculate_result_all_b(self):
        """测试全部选择B的计算结果"""
        mock_db = MagicMock()

        answers = []
        for i, q in enumerate(SBTI_QUESTIONS_DATA, 1):
            answers.append({
                "question_id": i,
                "answer": "B"
            })

        result = self.service.calculate_result(mock_db, user_id=1, answers=answers)

        assert len(result["top5_themes"]) == 5
        assert result["dominant_domain"] in DOMAINS

    def test_calculate_result_mixed(self):
        """测试混合选择的计算结果"""
        mock_db = MagicMock()

        answers = [
            {"question_id": 1, "answer": "A"},
            {"question_id": 2, "answer": "B"},
            {"question_id": 3, "answer": "A"},
            {"question_id": 4, "answer": "B"},
        ]

        result = self.service.calculate_result(mock_db, user_id=1, answers=answers)

        assert "top5_themes" in result
        assert len(result["top5_themes"]) == 5

    def test_calculate_result_invalid_answer(self):
        """测试无效答案处理"""
        mock_db = MagicMock()

        answers = [
            {"question_id": 1, "answer": "C"},  # 无效选项
            {"question_id": 2, "answer": ""},   # 空选项
            {"question_id": 3, "answer": "A"},
        ]

        result = self.service.calculate_result(mock_db, user_id=1, answers=answers)

        # 应该正常返回，只是无效答案被忽略
        assert "top5_themes" in result

    def test_calculate_result_missing_question_id(self):
        """测试缺少题目ID的处理"""
        mock_db = MagicMock()

        answers = [
            {"answer": "A"},  # 缺少question_id
            {"question_id": 2, "answer": "B"},
        ]

        result = self.service.calculate_result(mock_db, user_id=1, answers=answers)

        assert "top5_themes" in result

    def test_relationship_insights(self):
        """测试关系洞察生成"""
        mock_db = MagicMock()

        # 全部选A
        answers = [{"question_id": i, "answer": "A"} for i in range(1, 25)]

        result = self.service.calculate_result(mock_db, user_id=1, answers=answers)

        insights = result.get("relationship_insights", {})
        assert "communication_style" in insights
        assert isinstance(insights["communication_style"], str)

    def test_theme_scores_sum(self):
        """测试才干得分总和"""
        mock_db = MagicMock()

        answers = [{"question_id": i, "answer": "A"} for i in range(1, 25)]

        result = self.service.calculate_result(mock_db, user_id=1, answers=answers)

        # 检查domain_scores的合理性
        for domain, score in result["domain_scores"].items():
            assert 0 <= score <= 100, f"领域{domain}得分应在0-100之间，实际为{score}"

    def test_dominant_domain_determination(self):
        """测试主导领域判定"""
        mock_db = MagicMock()

        answers = [{"question_id": i, "answer": "A"} for i in range(1, 25)]

        result = self.service.calculate_result(mock_db, user_id=1, answers=answers)

        # 主导领域应该是得分最高的领域
        dominant = result["dominant_domain"]
        max_score = max(result["domain_scores"].values())

        assert result["domain_scores"][dominant] == max_score


class TestSbtiServiceThemeMapping:
    """才干主题映射测试"""

    def test_all_themes_in_34(self):
        """验证所有题目中的主题都在34项中"""
        for q in SBTI_QUESTIONS_DATA:
            assert q["theme_a"] in THEME_34, f"主题{q['theme_a']}不在34项中"
            assert q["theme_b"] in THEME_34, f"主题{q['theme_b']}不在34项中"

    def test_theme_domain_mapping(self):
        """验证主题到领域的映射"""
        for theme, info in THEME_34.items():
            assert "domain" in info
            assert info["domain"] in DOMAINS

    def test_questions_cover_all_domains(self):
        """验证题目覆盖所有领域"""
        domains_in_questions = set(q["domain"] for q in SBTI_QUESTIONS_DATA)
        assert domains_in_questions == set(DOMAINS)


class TestSbtiServiceSingleton:
    """单例模式测试"""

    def test_get_sbti_service_returns_same_instance(self):
        """测试获取单例"""
        from app.services.sbti_service import get_sbti_service

        service1 = get_sbti_service()
        service2 = get_sbti_service()

        assert service1 is service2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
