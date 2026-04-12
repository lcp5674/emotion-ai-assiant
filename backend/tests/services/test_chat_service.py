"""
对话服务单元测试
"""
import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from app.models import User, Conversation, Message, AiAssistant
from app.models.chat import MessageType, ConversationStatus
from app.services.chat_service import get_chat_service
from app.services.member_service import get_member_service
from app.services.content_filter import get_content_filter
from app.services.persona_context_builder import get_persona_builder
from app.services.rag.generator import get_generator


class TestChatService:
    """对话服务测试"""

    @pytest.fixture
    def mock_db(self):
        """模拟数据库会话"""
        return Mock(spec=Session)

    @pytest.fixture
    def mock_redis(self):
        """模拟Redis客户端"""
        return Mock()

    @pytest.fixture
    def chat_service(self):
        """对话服务实例"""
        return get_chat_service()

    @pytest.fixture
    def mock_user(self):
        """模拟用户"""
        user = Mock(spec=User)
        user.id = 1
        user.member_level = "FREE"
        user.member_expire_at = None
        user.mbti_type = "INTJ"
        return user

    @pytest.fixture
    def mock_assistant(self):
        """模拟AI助手"""
        assistant = Mock(spec=AiAssistant)
        assistant.id = 1
        assistant.name = "测试助手"
        assistant.personality = "友好"
        assistant.speaking_style = "温和"
        assistant.greeting = "你好！"
        return assistant

    @pytest.fixture
    def mock_conversation(self, mock_user, mock_assistant):
        """模拟对话"""
        conversation = Mock(spec=Conversation)
        conversation.id = 1
        conversation.user_id = mock_user.id
        conversation.session_id = "test_session"
        conversation.assistant_id = mock_assistant.id
        conversation.title = "新对话"
        conversation.message_count = 0
        conversation.updated_at = Mock()
        return conversation

    @pytest.fixture
    def mock_message(self, mock_conversation):
        """模拟消息"""
        message = Mock(spec=Message)
        message.id = 1
        message.conversation_id = mock_conversation.id
        message.role = "user"
        message.content = "测试消息"
        message.message_type = MessageType.TEXT
        message.created_at = Mock()
        return message

    @patch('app.services.chat_service.get_redis')
    @patch('app.services.chat_service.get_member_service')
    @patch('app.services.chat_service.get_content_filter')
    @patch('app.services.chat_service.get_persona_builder')
    @patch('app.services.chat_service.get_generator')
    async def test_create_conversation(self, mock_generator, mock_persona_builder, mock_content_filter, mock_member_service, mock_get_redis, chat_service, mock_db, mock_user, mock_assistant):
        """测试创建对话"""
        # 准备
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock(side_effect=lambda x: setattr(x, 'id', 1))

        # 执行
        conversation = await chat_service.create_conversation(
            db=mock_db,
            user_id=mock_user.id,
            assistant_id=mock_assistant.id,
            title="测试对话"
        )

        # 验证
        assert conversation is not None
        assert conversation.title == "测试对话"
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    @patch('app.services.chat_service.get_redis')
    @patch('app.services.chat_service.get_member_service')
    @patch('app.services.chat_service.get_content_filter')
    @patch('app.services.chat_service.get_persona_builder')
    @patch('app.services.chat_service.get_generator')
    async def test_send_message(self, mock_generator, mock_persona_builder, mock_content_filter, mock_member_service, mock_get_redis, chat_service, mock_db, mock_user, mock_conversation, mock_message):
        """测试发送消息"""
        # 准备
        mock_db.query.side_effect = [
            Mock(filter=lambda *args, **kwargs: Mock(first=lambda: mock_user)),
            Mock(filter=lambda *args, **kwargs: Mock(first=lambda: mock_conversation)),
            Mock(filter=lambda *args, **kwargs: Mock(order_by=lambda x: Mock(limit=lambda x: [mock_message])))
        ]
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()

        mock_redis = Mock()
        mock_get_redis.return_value = mock_redis

        mock_member_service_instance = Mock()
        mock_member_service.return_value = mock_member_service_instance
        mock_member_service_instance.check_message_limit.return_value = (True, "", 10)

        mock_content_filter_instance = Mock()
        mock_content_filter.return_value = mock_content_filter_instance
        mock_content_filter_instance.check_text.return_value = (True, None)

        mock_persona_builder_instance = Mock()
        mock_persona_builder.return_value = mock_persona_builder_instance
        mock_persona_builder_instance.build_user_context.return_value = "测试上下文"

        mock_generator_instance = Mock()
        mock_generator.return_value = mock_generator_instance
        mock_generator_instance.generate.return_value = {"answer": "测试回复", "references": []}

        # 执行
        result = await chat_service.send_message(
            db=mock_db,
            user_id=mock_user.id,
            session_id=mock_conversation.session_id,
            assistant_id=mock_conversation.assistant_id,
            content="测试消息"
        )

        # 验证
        assert result is not None
        assert "session_id" in result
        assert "assistant_message" in result
        assert result["assistant_message"]["content"] == "测试回复"

    def test_get_conversations(self, chat_service, mock_db, mock_conversation):
        """测试获取对话列表"""
        # 准备
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value = [mock_conversation]

        # 执行
        conversations = chat_service.get_conversations(
            db=mock_db,
            user_id=1,
            limit=20,
            offset=0
        )

        # 验证
        assert len(conversations) == 1
        assert conversations[0] == mock_conversation

    def test_get_conversation(self, chat_service, mock_db, mock_conversation):
        """测试获取对话详情"""
        # 准备
        mock_db.query.return_value.filter.return_value.first.return_value = mock_conversation

        # 执行
        conversation = chat_service.get_conversation(
            db=mock_db,
            user_id=1,
            session_id="test_session"
        )

        # 验证
        assert conversation == mock_conversation

    def test_get_messages(self, chat_service, mock_db, mock_message):
        """测试获取对话消息"""
        # 准备
        mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value = [mock_message]

        # 执行
        messages = chat_service.get_messages(
            db=mock_db,
            conversation_id=1,
            limit=50
        )

        # 验证
        assert len(messages) == 1
        assert messages[0] == mock_message

    def test_collect_message(self, chat_service, mock_db, mock_message):
        """测试收藏消息"""
        # 准备
        mock_message.is_collected = False
        mock_db.query.return_value.filter.return_value.first.return_value = mock_message
        mock_db.commit = Mock()

        # 执行
        result = chat_service.collect_message(
            db=mock_db,
            user_id=1,
            message_id=1
        )

        # 验证
        assert result is True
        assert mock_message.is_collected is True
        mock_db.commit.assert_called_once()

    def test_close_conversation(self, chat_service, mock_db, mock_conversation):
        """测试关闭对话"""
        # 准备
        mock_db.query.return_value.filter.return_value.first.return_value = mock_conversation
        mock_db.commit = Mock()

        # 执行
        result = chat_service.close_conversation(
            db=mock_db,
            user_id=1,
            session_id="test_session"
        )

        # 验证
        assert result is True
        assert mock_conversation.status == ConversationStatus.CLOSED
        mock_db.commit.assert_called_once()
