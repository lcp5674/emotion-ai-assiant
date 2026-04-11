"""
数据安全服务测试
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from app.services.data_security_service import DataSecurityService


class TestDataSecurityService:
    """数据安全服务测试"""

    @pytest.fixture
    def db_session(self):
        """创建模拟数据库会话"""
        return Mock()

    @pytest.fixture
    def security_service(self, db_session):
        """创建安全服务实例"""
        return DataSecurityService(db_session)

    # ========== 手机号脱敏测试 ==========

    def test_mask_phone_standard(self, security_service):
        """测试标准手机号脱敏"""
        phone = "13812345678"
        result = security_service.mask_phone(phone)

        assert result == "138****5678"
        assert result[3] == "*"
        assert result[7] == "*"

    def test_mask_phone_international(self, security_service):
        """测试国际格式手机号脱敏"""
        phone = "+86 13812345678"
        result = security_service.mask_phone(phone)

        assert "***" in result
        assert "138" in result  # 保留区号

    def test_mask_phone_invalid(self, security_service):
        """测试无效手机号"""
        phone = "12345"
        result = security_service.mask_phone(phone)

        # 无效手机号应该返回原值或特定标记
        assert len(result) < len(phone)  # 至少部分脱敏

    def test_mask_phone_none(self, security_service):
        """测试空手机号"""
        result = security_service.mask_phone(None)
        assert result == ""

    # ========== 邮箱脱敏测试 ==========

    def test_mask_email_standard(self, security_service):
        """测试标准邮箱脱敏"""
        email = "test@example.com"
        result = security_service.mask_email(email)

        assert result == "t**t@example.com"
        assert "@" in result
        assert "example.com" in result

    def test_mask_email_short_username(self, security_service):
        """测试短用户名的邮箱脱敏"""
        email = "ab@example.com"
        result = security_service.mask_email(email)

        assert "@" in result
        assert "a**b@example.com" in result

    def test_mask_email_no_at_symbol(self, security_service):
        """测试无@符号的邮箱脱敏"""
        email = "invalid-email"
        result = security_service.mask_email(email)

        # 应该安全处理
        assert "***" in result or result == ""

    def test_mask_email_none(self, security_service):
        """测试空邮箱"""
        result = security_service.mask_email(None)
        assert result == ""

    # ========== 审计日志测试 ==========

    def test_generate_audit_log(self, security_service):
        """测试审计日志生成"""
        result = security_service.generate_audit_log(
            user_id=1,
            action="view_profile",
            resource="profile",
            resource_id=100
        )

        assert result["user_id"] == 1
        assert result["action"] == "view_profile"
        assert result["resource"] == "profile"
        assert result["resource_id"] == 100
        assert "timestamp" in result
        assert "ip_address" in result
        assert "user_agent" in result

    def test_generate_audit_log_with_details(self, security_service):
        """测试带详细信息的审计日志"""
        result = security_service.generate_audit_log(
            user_id=1,
            action="update_profile",
            resource="profile",
            resource_id=100,
            details={"field": "mbti_type", "old_value": "INTJ", "new_value": "ENFP"}
        )

        assert "details" in result
        assert result["details"]["field"] == "mbti_type"

    def test_generate_audit_log_read_action(self, security_service):
        """测试读操作的审计日志"""
        result = security_service.generate_audit_log(
            user_id=1,
            action="read",
            resource="chat_messages",
            resource_id=200
        )

        assert result["action"] == "read"
        assert result["resource"] == "chat_messages"

    # ========== 危机关键词检测测试 ==========

    def test_check_crisis_keywords_critical(self, security_service):
        """测试关键危机关键词"""
        texts = [
            "我想自杀",
            "我要杀了我自己",
            "活着有什么意义，不如死了算了",
        ]

        for text in texts:
            result = security_service.check_crisis_keywords(text)
            assert result["level"] in ["critical", "high"], f"Failed for: {text}"
            assert result["detected"] == True

    def test_check_crisis_keywords_high(self, security_service):
        """测试高风险危机关键词"""
        texts = [
            "活着真累",
            "不想活了",
            "轻生",
        ]

        for text in texts:
            result = security_service.check_crisis_keywords(text)
            assert result["detected"] == True
            assert result["level"] in ["high", "medium"]

    def test_check_crisis_keywords_safe(self, security_service):
        """测试安全内容"""
        texts = [
            "今天天气很好",
            "工作有点累",
            "学习压力",
        ]

        for text in texts:
            result = security_service.check_crisis_keywords(text)
            assert result["level"] == "safe"
            assert result["detected"] == False

    def test_check_crisis_keywords_empty(self, security_service):
        """测试空文本"""
        result = security_service.check_crisis_keywords("")
        assert result["detected"] == False
        assert result["level"] == "safe"

    # ========== 数据导出测试 ==========

    def test_export_user_data(self, security_service, db_session):
        """测试用户数据导出"""
        # Mock用户数据
        mock_user = Mock()
        mock_user.id = 1
        mock_user.username = "test_user"
        mock_user.email = "test@example.com"
        mock_user.phone = "13812345678"
        mock_user.mbti_type = "INTJ"
        mock_user.created_at = datetime(2024, 1, 1)

        # Mock评估结果
        mock_assessments = [
            Mock(id=1, type="sbti", data={"score": 85}),
            Mock(id=2, type="mbti", data={"type": "INTJ"}),
        ]

        db_session.query.return_value.filter.return_value.all.side_effect = [
            [mock_user],  # user query
            mock_assessments,  # assessments query
        ]

        result = security_service.export_user_data(user_id=1)

        assert "user_profile" in result
        assert "assessments" in result
        assert "export_date" in result
        # 验证脱敏
        assert result["user_profile"]["email"] == "t**t@example.com"
        assert result["user_profile"]["phone"] == "138****5678"

    # ========== 数据删除测试 ==========

    def test_delete_user_data(self, security_service, db_session):
        """测试用户数据删除"""
        result = security_service.delete_user_data(user_id=1)

        assert result["success"] == True
        assert result["deleted_records"] > 0
        assert "cascade_deletes" in result

    def test_delete_user_data_with_audit(self, security_service, db_session):
        """测试带审计的数据删除"""
        result = security_service.delete_user_data(
            user_id=1,
            reason="user_request",
            requester_id=1
        )

        assert result["success"] == True
        assert "audit_logged" in result

    # ========== 敏感数据检测测试 ==========

    def test_detect_sensitive_fields(self, security_service):
        """测试敏感字段检测"""
        data = {
            "username": "test",
            "email": "test@example.com",
            "password": "secret123",
            "credit_card": "4111111111111111",
            "mbti_type": "INTJ",
        }

        result = security_service.detect_sensitive_fields(data)

        assert "sensitive_fields" in result
        assert "password" in result["sensitive_fields"]
        assert "credit_card" in result["sensitive_fields"]
        assert "username" not in result["sensitive_fields"]  # 非敏感字段

    def test_detect_sensitive_fields_nested(self, security_service):
        """测试嵌套数据结构检测"""
        data = {
            "user": {
                "name": "张三",
                "id_card": "110101199001011234",
                "bank_account": "6222021234567890"
            }
        }

        result = security_service.detect_sensitive_fields(data)

        assert len(result["sensitive_fields"]) >= 2


class TestDataSecurityServiceEdgeCases:
    """边界情况测试"""

    def test_concurrent_data_access(self):
        """测试并发数据访问"""
        from app.services.data_security_service import DataSecurityService
        import threading

        service = DataSecurityService(Mock())
        results = []

        def mask_phone_task():
            result = service.mask_phone("13812345678")
            results.append(result)

        threads = [threading.Thread(target=mask_phone_task) for _ in range(100)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # 所有结果应该一致
        assert all(r == "138****5678" for r in results)

    def test_large_text_processing(self):
        """测试大文本处理"""
        service = DataSecurityService(Mock())

        # 模拟大文本
        large_text = "内容" * 10000

        result = service.check_crisis_keywords(large_text)
        assert "processing_time" in result or "level" in result

    def test_special_characters(self):
        """测试特殊字符处理"""
        service = DataSecurityService(Mock())

        emails = [
            "test@example.com",
            "test+tag@example.com",
            "test_test@example.com",
        ]

        for email in emails:
            result = service.mask_email(email)
            assert "@" in result
            assert "example.com" in result

    def test_sql_injection_prevention(self):
        """测试SQL注入防护"""
        service = DataSecurityService(Mock())

        malicious_input = "'; DROP TABLE users; --"

        result = service.mask_phone(malicious_input)
        # 不应该执行任何SQL
        assert "DROP" not in result

    def test_xss_prevention(self):
        """测试XSS防护"""
        service = DataSecurityService(Mock())

        malicious_input = "<script>alert('xss')</script>"

        result = service.mask_phone(malicious_input)
        # 应该安全处理或脱敏
        assert "<script>" not in result
