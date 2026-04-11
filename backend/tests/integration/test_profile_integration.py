"""
Profile Service 集成测试
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from app.services.profile_service import ProfileService


class TestProfileServiceIntegration:
    """Profile服务集成测试"""

    @pytest.fixture
    def db_session(self):
        """创建模拟数据库会话"""
        session = Mock()
        return session

    @pytest.fixture
    def profile_service(self, db_session):
        """创建Profile服务实例"""
        return ProfileService(db_session)

    @pytest.fixture
    def mock_user_complete(self):
        """完整的用户数据"""
        user = Mock()
        user.id = 1
        user.username = "test_user"
        user.mbti_type = "INTJ"
        user.attachment_result_id = 100
        user.sbti_result_id = 200
        user.created_at = datetime.now() - timedelta(days=30)
        user.updated_at = datetime.now() - timedelta(days=5)
        return user

    @pytest.fixture
    def mock_mbti_result(self):
        """MBTI结果"""
        return Mock(
            id=200,
            mbti_type="INTJ",
            is_latest=True,
            completed_at=datetime.now() - timedelta(days=10),
            scores={
                "EI": 20,
                "SN": 80,
                "TF": 30,
                "JP": 70
            }
        )

    @pytest.fixture
    def mock_sbti_result(self):
        """SBTI结果"""
        return Mock(
            id=200,
            top5_themes=["independence", "logical", "strategic"],
            domain_scores={"emotional": 85, "social": 60},
            is_latest=True,
            completed_at=datetime.now() - timedelta(days=10)
        )

    @pytest.fixture
    def mock_attachment_result(self):
        """依恋风格结果"""
        return Mock(
            id=100,
            attachment_style="anxious",  # 焦虑型
            attachment_score=72,
            is_latest=True,
            completed_at=datetime.now() - timedelta(days=10)
        )

    # ========== 获取深度画像测试 ==========

    def test_get_deep_profile_success(
        self,
        profile_service,
        db_session,
        mock_user_complete,
        mock_mbti_result,
        mock_sbti_result,
        mock_attachment_result
    ):
        """测试成功获取深度画像"""
        # Mock 用户查询
        db_session.query.return_value.filter.return_value.first.side_effect = [
            mock_user_complete,  # get_user_by_id
            mock_mbti_result,     # mbti_result
            mock_sbti_result,     # sbti_result
            mock_attachment_result,  # attachment_result
        ]

        result = profile_service.get_deep_profile(user_id=1)

        assert result is not None
        assert "user_id" in result
        assert "mbti_section" in result
        assert "sbti_section" in result
        assert "attachment_section" in result
        assert "integrated_insights" in result

    def test_get_deep_profile_missing_mbti(self, profile_service, db_session, mock_user_complete):
        """测试MBTI缺失时的处理"""
        mock_user_complete.mbti_type = None
        mock_user_complete.mbti_result_id = None

        db_session.query.return_value.filter.return_value.first.return_value = mock_user_complete

        result = profile_service.get_deep_profile(user_id=1)

        # 应该返回部分画像
        assert result["mbti_section"]["status"] == "incomplete"

    def test_get_deep_profile_user_not_found(self, profile_service, db_session):
        """测试用户不存在"""
        db_session.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(ValueError, match="用户不存在"):
            profile_service.get_deep_profile(user_id=999)

    # ========== 生成画像测试 ==========

    @patch("app.services.profile_service.LLMClient")
    def test_generate_profile_success(
        self,
        mock_llm,
        profile_service,
        db_session,
        mock_user_complete,
        mock_mbti_result,
        mock_sbti_result,
        mock_attachment_result
    ):
        """测试成功生成画像"""
        # Mock LLM响应
        mock_llm_instance = Mock()
        mock_llm_instance.generate.return_value = '{"summary": "测试摘要", "personality_tags": ["理性"], "relationship_style": "独立型"}'
        mock_llm.return_value = mock_llm_instance

        # Mock数据库查询
        db_session.query.return_value.filter.return_value.first.side_effect = [
            mock_user_complete,
            mock_mbti_result,
            mock_sbti_result,
            mock_attachment_result,
        ]

        result = profile_service.generate_profile(user_id=1)

        assert "profile_data" in result
        assert result["success"] == True

    # ========== 获取摘要测试 ==========

    def test_get_profile_summary_with_data(self, profile_service, db_session, mock_user_complete):
        """测试有数据时的摘要"""
        mock_user_complete.deep_profile = {
            "summary": "测试摘要内容",
            "personality_tags": ["理性", "独立"],
            "relationship_style": "分析型",
            "communication_tips": ["直接沟通", "逻辑支持"]
        }

        db_session.query.return_value.filter.return_value.first.return_value = mock_user_complete

        result = profile_service.get_profile_summary(user_id=1)

        assert "summary" in result
        assert len(result["personality_tags"]) > 0

    def test_get_profile_summary_no_data(self, profile_service, db_session, mock_user_complete):
        """测试无数据时的摘要"""
        mock_user_complete.deep_profile = None

        db_session.query.return_value.filter.return_value.first.return_value = mock_user_complete

        result = profile_service.get_profile_summary(user_id=1)

        assert result["summary"] == ""
        assert len(result["personality_tags"]) == 0
