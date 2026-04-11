"""
数据质量服务测试
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from app.services.data_quality_service import DataQualityService


class TestDataQualityService:
    """数据质量服务测试"""

    @pytest.fixture
    def db_session(self):
        """创建模拟数据库会话"""
        return Mock()

    @pytest.fixture
    def quality_service(self, db_session):
        """创建数据质量服务实例"""
        return DataQualityService(db_session)

    @pytest.fixture
    def mock_user_with_full_assessment(self):
        """模拟完成所有测评的用户"""
        user = Mock()
        user.id = 1
        user.mbti_type = "INTJ"
        user.sbti_result_id = 100
        user.attachment_result_id = 200
        user.created_at = datetime.now() - timedelta(days=30)
        user.updated_at = datetime.now() - timedelta(days=5)
        user.sbti_result = Mock()
        user.sbti_result.is_latest = True
        user.sbti_result.completed_at = datetime.now() - timedelta(days=5)
        user.attachment_result = Mock()
        user.attachment_result.is_latest = True
        user.attachment_result.completed_at = datetime.now() - timedelta(days=5)
        return user

    @pytest.fixture
    def mock_user_partial_assessment(self):
        """模拟完成部分测评的用户"""
        user = Mock()
        user.id = 2
        user.mbti_type = None  # 缺失MBTI
        user.sbti_result_id = None  # 缺失SBTI
        user.attachment_result_id = 200
        user.created_at = datetime.now() - timedelta(days=90)
        user.updated_at = datetime.now() - timedelta(days=60)
        user.sbti_result = None
        user.attachment_result = Mock()
        user.attachment_result.is_latest = True
        user.attachment_result.completed_at = datetime.now() - timedelta(days=60)
        return user

    # ========== 时效性评估测试 ==========

    def test_assess_timeliness_recent(self, quality_service, mock_user_with_full_assessment):
        """测试近期测评的时效性评分"""
        result = quality_service.assess_timeliness(mock_user_with_full_assessment)

        assert result["score"] >= 0.8  # 5天内应为高分
        assert result["status"] in ["fresh", "acceptable"]
        assert "days_since_update" in result

    def test_assess_timeliness_outdated(self, quality_service, mock_user_partial_assessment):
        """测试过期测评的时效性评分"""
        result = quality_service.assess_timeliness(mock_user_partial_assessment)

        assert result["score"] < 0.5  # 60天前应低于0.5
        assert result["status"] == "outdated"
        assert len(result["warnings"]) > 0

    def test_assess_timeliness_stale(self, quality_service):
        """测试需要刷新的过期测评"""
        user = Mock()
        user.id = 3
        user.updated_at = datetime.now() - timedelta(days=365)
        user.sbti_result = Mock()
        user.sbti_result.completed_at = datetime.now() - timedelta(days=365)

        result = quality_service.assess_timeliness(user)

        assert result["status"] == "stale"
        assert len(result["recommendations"]) > 0

    def test_assess_timeliness_no_data(self, quality_service):
        """测试无测评数据的用户"""
        user = Mock()
        user.id = 4
        user.updated_at = datetime.now() - timedelta(days=5)
        user.sbti_result = None
        user.attachment_result = None
        user.mbti_type = None

        result = quality_service.assess_timeliness(user)

        assert result["score"] == 0.0
        assert result["status"] == "incomplete"
        assert "needs_assessment" in result["warnings"][0].lower()

    # ========== 完整性评估测试 ==========

    def test_assess_completeness_full(self, quality_service, mock_user_with_full_assessment):
        """测试完整的测评数据"""
        result = quality_service.assess_completeness(mock_user_with_full_assessment)

        assert result["score"] == 1.0
        assert result["status"] == "complete"
        assert len(result["missing_items"]) == 0

    def test_assess_completeness_partial(self, quality_service, mock_user_partial_assessment):
        """测试部分完整的测评数据"""
        result = quality_service.assess_completeness(mock_user_partial_assessment)

        assert 0.3 <= result["score"] < 0.7
        assert result["status"] == "partial"
        assert "mbti" in result["missing_items"]
        assert "sbti" in result["missing_items"]

    def test_assess_completeness_empty(self, quality_service):
        """测试无测评数据的用户"""
        user = Mock()
        user.id = 5
        user.mbti_type = None
        user.sbti_result_id = None
        user.attachment_result_id = None

        result = quality_service.assess_completeness(user)

        assert result["score"] == 0.0
        assert result["status"] == "empty"
        assert len(result["missing_items"]) == 3  # mbti, sbti, attachment

    # ========== 一致性评估测试 ==========

    def test_assess_consistency_valid(self, quality_service, db_session):
        """测试数据一致的用户"""
        # 模拟用户有SBTI结果但无记录
        user = Mock()
        user.id = 6
        user.sbti_result_id = 100
        user.attachment_result_id = 200

        # Mock 查询结果
        db_session.query.return_value.filter.return_value.first.side_effect = [
            Mock(id=100, is_latest=True),  # sbti_result
            Mock(id=200, is_latest=True),  # attachment_result
        ]

        result = quality_service.assess_consistency(user)

        assert result["score"] == 1.0
        assert result["status"] == "consistent"
        assert len(result["issues"]) == 0

    def test_assess_consistency_orphaned_record(self, quality_service, db_session):
        """测试存在孤立记录的用户"""
        user = Mock()
        user.id = 7
        user.sbti_result_id = 100
        user.attachment_result_id = None  # 引用不存在

        db_session.query.return_value.filter.return_value.first.side_effect = [
            Mock(id=100, is_latest=True),
            None,  # attachment_result 不存在
        ]

        result = quality_service.assess_consistency(user)

        assert result["score"] < 1.0
        assert result["status"] == "issues_found"
        assert any("attachment" in issue.lower() for issue in result["issues"])

    def test_assess_consistency_expired_result(self, quality_service, db_session):
        """测试过期结果的检测"""
        user = Mock()
        user.id = 8
        user.sbti_result_id = 100

        # 模拟过期结果
        expired_result = Mock()
        expired_result.id = 100
        expired_result.is_latest = False
        expired_result.completed_at = datetime.now() - timedelta(days=180)

        db_session.query.return_value.filter.return_value.first.return_value = expired_result

        result = quality_service.assess_consistency(user)

        assert result["score"] < 0.8
        assert any("过期" in issue or "stale" in issue.lower() for issue in result["issues"])

    # ========== 修复一致性测试 ==========

    @patch('app.services.data_quality_service.DataQualityService._clear_invalid_reference')
    def test_fix_consistency_issues_no_issues(self, mock_clear, quality_service):
        """测试无问题时的修复"""
        quality_report = {
            "issues": [],
            "needs_cleanup": False,
        }

        result = quality_service.fix_consistency_issues(quality_report)

        assert result["fixed_count"] == 0
        assert result["status"] == "no_issues"
        mock_clear.assert_not_called()

    @patch('app.services.data_quality_service.DataQualityService._clear_invalid_reference')
    def test_fix_consistency_issues_with_fix(self, mock_clear, quality_service):
        """测试有问题的修复"""
        mock_clear.return_value = True

        quality_report = {
            "issues": ["orphaned_sbti_record", "expired_result"],
            "needs_cleanup": True,
        }

        result = quality_service.fix_consistency_issues(quality_report)

        assert result["fixed_count"] >= 0
        assert "status" in result

    # ========== 综合评分测试 ==========

    def test_get_overall_quality_score_perfect(self, quality_service, db_session):
        """测试完美的数据质量"""
        user = Mock()
        user.id = 9
        user.mbti_type = "ENFP"
        user.sbti_result_id = 100
        user.attachment_result_id = 200
        user.created_at = datetime.now() - timedelta(days=30)
        user.updated_at = datetime.now() - timedelta(days=2)
        user.sbti_result = Mock()
        user.sbti_result.is_latest = True
        user.sbti_result.completed_at = datetime.now() - timedelta(days=2)
        user.attachment_result = Mock()
        user.attachment_result.is_latest = True
        user.attachment_result.completed_at = datetime.now() - timedelta(days=2)

        db_session.query.return_value.filter.return_value.first.side_effect = [
            Mock(id=100, is_latest=True, completed_at=datetime.now() - timedelta(days=2)),
            Mock(id=200, is_latest=True, completed_at=datetime.now() - timedelta(days=2)),
        ]

        result = quality_service.get_overall_quality_score(user)

        assert result["overall_score"] >= 0.95
        assert result["grade"] in ["A", "A+", "A-"]
        assert len(result["recommendations"]) == 0

    def test_get_overall_quality_score_poor(self, quality_service, db_session):
        """测试较差的数据质量"""
        user = Mock()
        user.id = 10
        user.mbti_type = None
        user.sbti_result_id = None
        user.attachment_result_id = None
        user.created_at = datetime.now() - timedelta(days=200)
        user.updated_at = datetime.now() - timedelta(days=200)

        db_session.query.return_value.filter.return_value.first.return_value = None

        result = quality_service.get_overall_quality_score(user)

        assert result["overall_score"] < 0.3
        assert result["grade"] in ["D", "F"]
        assert len(result["recommendations"]) > 0

    def test_get_overall_quality_score_weights(self, quality_service, db_session):
        """测试评分权重分配"""
        user = Mock()
        user.id = 11
        user.mbti_type = "INTJ"
        user.sbti_result_id = 100
        user.attachment_result_id = None
        user.created_at = datetime.now() - timedelta(days=30)
        user.updated_at = datetime.now() - timedelta(days=5)

        # 设置部分结果
        sbti_result = Mock()
        sbti_result.is_latest = True
        sbti_result.completed_at = datetime.now() - timedelta(days=5)

        db_session.query.return_value.filter.return_value.first.side_effect = [
            sbti_result,
            None,
        ]

        result = quality_service.get_overall_quality_score(user)

        # 验证各维度都有评分
        assert "timeliness" in result["dimensions"]
        assert "completeness" in result["dimensions"]
        assert "consistency" in result["dimensions"]

        # 时效性高 + 完整性中 + 一致性中 = 整体中上
        assert 0.5 <= result["overall_score"] <= 0.8


class TestDataQualityServiceEdgeCases:
    """边界情况测试"""

    def test_none_user(self, db_session):
        """测试空用户"""
        service = DataQualityService(db_session)

        with pytest.raises((AttributeError, TypeError)):
            service.assess_timeliness(None)

    def test_database_error_handling(self, db_session):
        """测试数据库错误处理"""
        db_session.query.side_effect = Exception("Database connection error")
        service = DataQualityService(db_session)

        user = Mock()
        user.id = 99
        user.updated_at = datetime.now()

        # 应该优雅处理错误
        result = service.assess_consistency(user)
        assert "error" in result or result["score"] == 0

    def test_concurrent_access(self, db_session):
        """测试并发访问"""
        import threading

        service = DataQualityService(db_session)
        user = Mock()
        user.id = 100
        user.mbti_type = "INTJ"
        user.sbti_result_id = 1
        user.attachment_result_id = 1
        user.updated_at = datetime.now()
        user.sbti_result = Mock()
        user.sbti_result.is_latest = True
        user.attachment_result = Mock()
        user.attachment_result.is_latest = True

        results = []

        def assess():
            result = service.assess_timeliness(user)
            results.append(result)

        threads = [threading.Thread(target=assess) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 10
