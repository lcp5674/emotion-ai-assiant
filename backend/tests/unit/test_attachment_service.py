# -*- coding: utf-8 -*-
"""
依恋风格服务单元测试
"""
import pytest
from unittest.mock import MagicMock
from app.services.attachment_service import AttachmentService


class TestAttachmentService:
    """依恋风格服务测试"""

    def setup_method(self):
        """测试前准备"""
        self.service = AttachmentService()

    def test_styles_exist(self):
        """测试四种依恋风格定义"""
        assert len(self.service.STYLES) == 4
        assert "安全型" in self.service.STYLES
        assert "焦虑型" in self.service.STYLES
        assert "回避型" in self.service.STYLES
        assert "混乱型" in self.service.STYLES

    def test_determine_style_secure(self):
        """测试安全型判定"""
        # 低焦虑 + 低回避 = 安全型
        style = self.service._determine_style(2.0, 2.0)
        assert style == "安全型"

    def test_determine_style_anxious(self):
        """测试焦虑型判定"""
        # 高焦虑 + 低回避 = 焦虑型
        style = self.service._determine_style(5.0, 2.0)
        assert style == "焦虑型"

    def test_determine_style_avoidant(self):
        """测试回避型判定"""
        # 低焦虑 + 高回避 = 回避型
        style = self.service._determine_style(2.0, 5.0)
        assert style == "回避型"

    def test_determine_style_disorganized(self):
        """测试混乱型判定"""
        # 高焦虑 + 高回避 = 混乱型
        style = self.service._determine_style(5.0, 5.0)
        assert style == "混乱型"

    def test_determine_style_boundary_low(self):
        """测试边界值：刚好3.5"""
        style = self.service._determine_style(3.5, 3.5)
        assert style == "混乱型"  # 3.5 > 3.5 为 false，所以是 <=3.5


class TestAttachmentServiceCalculation:
    """依恋风格计算测试"""

    def setup_method(self):
        """测试前准备"""
        self.service = AttachmentService()

    def test_calculate_result_all_low_scores(self):
        """测试全部低分（安全型）"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = MagicMock(
            anxiety_weight=1.0, avoidance_weight=0.0
        )

        # 模拟10道题答案
        answers = [{"question_id": i, "score": 2} for i in range(1, 11)]

        result = self.service.calculate_result(mock_db, user_id=1, answers=answers)

        assert result["style"] in ["安全型", "焦虑型", "回避型", "混乱型"]
        assert "anxiety_score" in result
        assert "avoidance_score" in result

    def test_calculate_result_all_high_scores(self):
        """测试全部高分"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = MagicMock(
            anxiety_weight=1.0, avoidance_weight=0.0
        )

        answers = [{"question_id": i, "score": 6} for i in range(1, 11)]

        result = self.service.calculate_result(mock_db, user_id=1, answers=answers)

        assert result["anxiety_score"] > 0
        assert result["avoidance_score"] > 0

    def test_calculate_result_with_missing_question(self):
        """测试题目缺失处理"""
        mock_db = MagicMock()
        # 返回None表示题目不存在
        mock_db.query.return_value.filter.return_value.first.return_value = None

        answers = [
            {"question_id": 999, "score": 5},  # 不存在的题目
            {"question_id": 2, "score": 3},
        ]

        result = self.service.calculate_result(mock_db, user_id=1, answers=answers)

        # 应该正常返回
        assert "style" in result

    def test_calculate_result_string_score(self):
        """测试字符串分数处理"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = MagicMock(
            anxiety_weight=1.0, avoidance_weight=0.0
        )

        answers = [{"question_id": 1, "score": "5"}]  # 字符串分数

        result = self.service.calculate_result(mock_db, user_id=1, answers=answers)

        assert "style" in result


class TestAttachmentServiceQuestions:
    """依恋风格题目测试"""

    def setup_method(self):
        """测试前准备"""
        self.service = AttachmentService()

    def test_questions_data_count(self):
        """测试题目数量"""
        questions = self.service._get_questions_data()
        assert len(questions) == 10

    def test_questions_structure(self):
        """测试题目结构"""
        questions = self.service._get_questions_data()

        for q in questions:
            assert "question_no" in q
            assert "question_text" in q
            assert "anxiety_weight" in q
            assert "avoidance_weight" in q

    def test_anxiety_dimensions(self):
        """测试焦虑维度题目"""
        questions = self.service._get_questions_data()
        anxiety_questions = [q for q in questions if q["anxiety_weight"] > 0]
        assert len(anxiety_questions) == 5

    def test_avoidance_dimensions(self):
        """测试回避维度题目"""
        questions = self.service._get_questions_data()
        avoidance_questions = [q for q in questions if q["avoidance_weight"] > 0]
        assert len(avoidance_questions) == 5


class TestAttachmentServiceSingleton:
    """单例模式测试"""

    def test_get_attachment_service_returns_same_instance(self):
        """测试获取单例"""
        from app.services.attachment_service import get_attachment_service

        service1 = get_attachment_service()
        service2 = get_attachment_service()

        assert service1 is service2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
