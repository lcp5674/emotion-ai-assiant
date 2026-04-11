"""
Attachment Service 集成测试
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from app.services.attachment_service import AttachmentService


class TestAttachmentServiceIntegration:
    """Attachment服务集成测试"""

    @pytest.fixture
    def db_session(self):
        """创建模拟数据库会话"""
        session = Mock()
        return session

    @pytest.fixture
    def attachment_service(self, db_session):
        """创建Attachment服务实例"""
        return AttachmentService(db_session)

    # ========== 获取题目测试 ==========

    def test_get_questions_success(self, attachment_service):
        """测试成功获取题目"""
        result = attachment_service.get_questions()

        assert "questions" in result
        assert "total" in result
        assert len(result["questions"]) == 10  # 应该10题
        assert result["total"] == 10

    def test_questions_structure(self, attachment_service):
        """测试题目结构"""
        result = attachment_service.get_questions()

        for q in result["questions"]:
            assert "id" in q
            assert "text" in q
            assert "options" in q
            assert len(q["options"]) >= 3

    # ========== 提交答案测试 ==========

    @patch("app.services.attachment_service.AttachmentService._calculate_style")
    def test_submit_success(
        self,
        mock_calculate,
        attachment_service,
        db_session
    ):
        """测试成功提交答案"""
        # Mock 用户
        mock_user = Mock()
        mock_user.id = 1
        mock_user.attachment_result_id = None

        # Mock 分数计算
        mock_calculate.return_value = {
            "attachment_style": "secure",
            "attachment_score": 75,
            "dimension_scores": {
                "anxiety": 30,
                "avoidance": 25
            }
        }

        db_session.query.return_value.filter.return_value.first.return_value = mock_user

        # 提交完整答案
        answers = {f"q{i}": 4 for i in range(1, 11)}

        result = attachment_service.submit(
            user_id=1,
            answers=answers
        )

        assert result["success"] == True
        assert "attachment_style" in result

    def test_submit_incomplete_answers(self, attachment_service, db_session):
        """测试答案不完整"""
        mock_user = Mock()
        mock_user.id = 1
        db_session.query.return_value.filter.return_value.first.return_value = mock_user

        # 只提交部分答案
        answers = {"q1": 4, "q2": 3}

        with pytest.raises(ValueError, match="答案不完整"):
            attachment_service.submit(user_id=1, answers=answers)

    def test_submit_invalid_answer_format(self, attachment_service, db_session):
        """测试无效答案格式"""
        mock_user = Mock()
        mock_user.id = 1
        db_session.query.return_value.filter.return_value.first.return_value = mock_user

        # 无效分数
        answers = {f"q{i}": 10 for i in range(1, 11)}  # 超过有效范围

        with pytest.raises(ValueError, match="无效"):
            attachment_service.submit(user_id=1, answers=answers)

    # ========== 获取结果测试 ==========

    def test_get_result_success(self, attachment_service, db_session):
        """测试成功获取结果"""
        mock_result = Mock()
        mock_result.id = 1
        mock_result.attachment_style = "secure"
        mock_result.attachment_score = 80
        mock_result.dimension_scores = {"anxiety": 20, "avoidance": 15}
        mock_result.is_latest = True
        mock_result.completed_at = datetime.now()

        mock_user = Mock()
        mock_user.attachment_result_id = 1

        db_session.query.return_value.filter.return_value.first.side_effect = [
            mock_user,
            mock_result
        ]

        result = attachment_service.get_result(user_id=1)

        assert "attachment_style" in result
        assert result["attachment_score"] == 80

    def test_get_result_no_result(self, attachment_service, db_session):
        """测试无结果"""
        mock_user = Mock()
        mock_user.attachment_result_id = None

        db_session.query.return_value.filter.return_value.first.return_value = mock_user

        result = attachment_service.get_result(user_id=1)

        assert result is None

    # ========== 依恋风格分析测试 ==========

    def test_calculate_style_secure(self, attachment_service):
        """测试安全型计算"""
        scores = {"anxiety": 20, "avoidance": 15}

        result = attachment_service._calculate_style(scores)

        assert result["attachment_style"] == "secure"
        assert result["attachment_score"] > 70

    def test_calculate_style_anxious(self, attachment_service):
        """测试焦虑型计算"""
        scores = {"anxiety": 80, "avoidance": 20}

        result = attachment_service._calculate_style(scores)

        assert result["attachment_style"] == "anxious"

    def test_calculate_style_avoidant(self, attachment_service):
        """测试回避型计算"""
        scores = {"anxiety": 20, "avoidance": 80}

        result = attachment_service._calculate_style(scores)

        assert result["attachment_style"] == "avoidant"

    def test_calculate_style_fearful(self, attachment_service):
        """测试恐惧型计算"""
        scores = {"anxiety": 75, "avoidance": 75}

        result = attachment_service._calculate_style(scores)

        assert result["attachment_style"] == "fearful"
