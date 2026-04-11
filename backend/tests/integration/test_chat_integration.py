"""
Chat Service 集成测试
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime
from app.services.chat_service import ChatService


class TestChatServiceIntegration:
    """Chat服务集成测试"""

    @pytest.fixture
    def db_session(self):
        """创建模拟数据库会话"""
        return Mock()

    @pytest.fixture
    def chat_service(self, db_session):
        """创建Chat服务实例"""
        return ChatService(db_session)

    @pytest.fixture
    def mock_user(self):
        """模拟用户"""
        user = Mock()
        user.id = 1
        user.username = "test_user"
        user.mbti_type = "INTJ"
        user.personality_tags = "理性,独立"
        user.relationship_style = "分析型"
        return user

    # ========== 发送消息测试 ==========

    @patch("app.services.chat_service.RAGService")
    @patch("app.services.chat_service.PersonaContextBuilder")
    def test_send_message_success(
        self,
        mock_builder,
        mock_rag,
        chat_service,
        db_session,
        mock_user
    ):
        """测试成功发送消息"""
        # Mock RAG服务
        mock_rag_instance = AsyncMock()
        mock_rag_instance.generate_response.return_value = "这是一个测试回复"
        mock_rag.return_value = mock_rag_instance

        # Mock上下文构建器
        mock_builder_instance = Mock()
        mock_builder_instance.build.return_value = {"context": "测试上下文"}
        mock_builder.return_value = mock_builder_instance

        # Mock用户查询
        db_session.query.return_value.filter.return_value.first.return_value = mock_user

        result = chat_service.send_message(
            user_id=1,
            message="你好",
            conversation_id="conv_123"
        )

        assert result["success"] == True
        assert "message" in result
        assert "ai_response" in result

    @patch("app.services.chat_service.RAGService")
    def test_send_message_empty_content(self, mock_rag, chat_service, db_session, mock_user):
        """测试空消息"""
        db_session.query.return_value.filter.return_value.first.return_value = mock_user

        with pytest.raises(ValueError, match="不能为空"):
            chat_service.send_message(
                user_id=1,
                message="",
                conversation_id="conv_123"
            )

    @patch("app.services.chat_service.RAGService")
    def test_send_message_user_not_found(self, mock_rag, chat_service, db_session):
        """测试用户不存在"""
        db_session.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(ValueError, match="用户不存在"):
            chat_service.send_message(
                user_id=999,
                message="你好",
                conversation_id="conv_123"
            )

    # ========== 危机检测测试 ==========

    @patch("app.services.chat_service.DataSecurityService")
    def test_send_message_crisis_detected(
        self,
        mock_security,
        chat_service,
        db_session,
        mock_user
    ):
        """测试检测到危机内容"""
        # Mock安全服务
        mock_security_instance = Mock()
        mock_security_instance.check_crisis_keywords.return_value = {
            "detected": True,
            "level": "high",
            "keywords": ["想死"]
        }
        mock_security.return_value = mock_security_instance

        # Mock用户
        db_session.query.return_value.filter.return_value.first.return_value = mock_user

        result = chat_service.send_message(
            user_id=1,
            message="我不想活了",
            conversation_id="conv_123"
        )

        assert result["crisis_detected"] == True
        assert result["crisis_response"] is not None

    # ========== 对话历史测试 ==========

    def test_get_conversation_history(self, chat_service, db_session, mock_user):
        """测试获取对话历史"""
        mock_messages = [
            Mock(id=1, content="你好", role="user", created_at=datetime.now()),
            Mock(id=2, content="你好，我是AI助手", role="assistant", created_at=datetime.now()),
        ]

        mock_conversation = Mock()
        mock_conversation.id = "conv_123"
        mock_conversation.messages = mock_messages

        db_session.query.return_value.filter.return_value.first.return_value = mock_conversation

        result = chat_service.get_conversation_history(
            user_id=1,
            conversation_id="conv_123",
            limit=50
        )

        assert len(result) == 2

    def test_get_conversation_history_limit(self, chat_service, db_session, mock_user):
        """测试对话历史限制"""
        mock_conversation = Mock()
        mock_conversation.messages = [
            Mock(id=i, content=f"消息{i}", role="user", created_at=datetime.now())
            for i in range(100)
        ]

        db_session.query.return_value.filter.return_value.first.return_value = mock_conversation

        result = chat_service.get_conversation_history(
            user_id=1,
            conversation_id="conv_123",
            limit=10
        )

        assert len(result) == 10

    # ========== 置信度评估测试 ==========

    @patch("app.services.chat_service.RAGQualityService")
    def test_confidence_assessment(
        self,
        mock_quality,
        chat_service,
        db_session
    ):
        """测试置信度评估"""
        mock_quality_instance = Mock()
        mock_quality_instance.full_quality_assessment.return_value = {
            "overall_score": 0.85,
            "dimension_scores": {
                "relevance": 0.9,
                "accuracy": 0.8,
                "personalization": 0.85,
                "length": 0.9,
                "safety": 1.0
            }
        }
        mock_quality.return_value = mock_quality_instance

        result = chat_service.assess_response_quality(
            query="测试查询",
            answer="测试回答",
            context=[{"content": "上下文"}],
            user=Mock()
        )

        assert "confidence" in result
        assert result["confidence"] >= 0.8


class TestChatServiceEdgeCases:
    """边界情况测试"""

    @pytest.fixture
    def chat_service(self):
        return ChatService(Mock())

    def test_very_long_message(self, chat_service):
        """测试超长消息"""
        # 模拟超长消息
        long_message = "A" * 10000

        with pytest.raises(ValueError, match="过长"):
            chat_service.send_message(
                user_id=1,
                message=long_message,
                conversation_id="conv_123"
            )

    def test_special_characters(self, chat_service, db_session):
        """测试特殊字符"""
        mock_user = Mock()
        mock_user.id = 1
        db_session.query.return_value.filter.return_value.first.return_value = mock_user

        # 应该能处理特殊字符而不抛出异常
        with patch("app.services.chat_service.RAGService"):
            result = chat_service.send_message(
                user_id=1,
                message="你好😀🎉🎊",
                conversation_id="conv_123"
            )
            assert result["success"] == True

    def test_multiple_concurrent_requests(self, chat_service, db_session):
        """测试并发请求"""
        import threading

        mock_user = Mock()
        mock_user.id = 1
        db_session.query.return_value.filter.return_value.first.return_value = mock_user

        results = []
        errors = []

        def send_request():
            try:
                with patch("app.services.chat_service.RAGService"):
                    result = chat_service.send_message(
                        user_id=1,
                        message="测试消息",
                        conversation_id="conv_123"
                    )
                    results.append(result)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=send_request) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 10
        assert len(errors) == 0
