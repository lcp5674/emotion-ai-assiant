"""
chat_service 单元测试
"""
import pytest
from sqlalchemy.orm import Session

from app.services.chat_service import ChatService
from app.models.chat import Conversation, Message, ConversationStatus
from app.models.user import User
from app.models.mbti import AiAssistant, MbtiType


class TestChatService:
    """ChatService单元测试"""

    def test_get_conversations(self, db_session):
        """获取用户会话列表"""
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        assistant = AiAssistant(
            id=1,
            name="test",
            mbti_type=MbtiType.INTJ,
            personality="test description",
            speaking_style="friendly",
            expertise="testing",
            greeting="Hello",
            is_active=True,
        )
        db_session.add(assistant)
        conv1 = Conversation(
            user_id=1,
            assistant_id=1,
            session_id="session-1",
            title="会话1",
        )
        conv2 = Conversation(
            user_id=1,
            assistant_id=1,
            session_id="session-2",
            title="会话2",
        )
        db_session.add(conv1)
        db_session.add(conv2)
        db_session.commit()

        service = ChatService()
        sessions = service.get_conversations(db_session, 1)
        
        assert len(sessions) == 2

    def test_get_conversation_exists(self, db_session):
        """获取存在的会话"""
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        assistant = AiAssistant(
            id=1,
            name="test",
            mbti_type=MbtiType.INTJ,
            personality="test description",
            speaking_style="friendly",
            expertise="testing",
            greeting="Hello",
            is_active=True,
        )
        db_session.add(assistant)
        conv = Conversation(
            user_id=1,
            assistant_id=1,
            session_id="session-1",
            title="测试会话",
        )
        db_session.add(conv)
        db_session.commit()

        service = ChatService()
        result = service.get_conversation(db_session, 1, "session-1")
        
        assert result is not None
        assert result.title == "测试会话"

    def test_get_conversation_not_exists(self, db_session):
        """获取不存在的会话返回None"""
        service = ChatService()
        result = service.get_conversation(db_session, 1, "not-exists")
        
        assert result is None

    def test_get_conversation_wrong_user(self, db_session):
        """获取其他用户的会话返回None"""
        user1 = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        user2 = User(
            id=2,
            phone="13900000002",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user1)
        db_session.add(user2)
        assistant = AiAssistant(
            id=1,
            name="test",
            mbti_type=MbtiType.INTJ,
            personality="test description",
            speaking_style="friendly",
            expertise="testing",
            greeting="Hello",
            is_active=True,
        )
        db_session.add(assistant)
        conv = Conversation(
            user_id=1,
            assistant_id=1,
            session_id="session-1",
            title="用户1的会话",
        )
        db_session.add(conv)
        db_session.commit()

        service = ChatService()
        result = service.get_conversation(db_session, 2, "session-1")
        
        assert result is None

    async def test_create_conversation(self, db_session):
        """创建新会话"""
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        assistant = AiAssistant(
            id=1,
            name="test",
            mbti_type=MbtiType.INTJ,
            personality="test description",
            speaking_style="friendly",
            expertise="testing",
            greeting="Hello",
            is_active=True,
        )
        db_session.add(assistant)
        db_session.commit()

        service = ChatService()
        conv = await service.create_conversation(db_session, 1, 1, "新会话")
        
        assert conv is not None
        assert conv.user_id == 1
        assert conv.assistant_id == 1
        assert conv.title == "新会话"

    def test_get_messages(self, db_session):
        """获取会话消息列表"""
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        assistant = AiAssistant(
            id=1,
            name="test",
            mbti_type=MbtiType.INTJ,
            personality="test description",
            speaking_style="friendly",
            expertise="testing",
            greeting="Hello",
            is_active=True,
        )
        db_session.add(assistant)
        conv = Conversation(
            user_id=1,
            assistant_id=1,
            session_id="session-1",
            title="会话",
        )
        db_session.add(conv)
        db_session.commit()

        msg1 = Message(conversation_id=conv.id, role="user", content="你好")
        msg2 = Message(conversation_id=conv.id, role="assistant", content="你好呀")
        db_session.add(msg1)
        db_session.add(msg2)
        db_session.commit()

        service = ChatService()
        messages = service.get_messages(db_session, conv.id)
        
        assert len(messages) == 2

    def test_collect_message(self, db_session):
        """收藏消息 - toggle"""
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        assistant = AiAssistant(
            id=1,
            name="test",
            mbti_type=MbtiType.INTJ,
            personality="test description",
            speaking_style="friendly",
            expertise="testing",
            greeting="Hello",
            is_active=True,
        )
        db_session.add(assistant)
        conv = Conversation(
            user_id=1,
            assistant_id=1,
            session_id="session-1",
            title="会话",
        )
        db_session.add(conv)
        db_session.commit()
        msg = Message(conversation_id=conv.id, role="assistant", content="test", is_collected=False)
        db_session.add(msg)
        db_session.commit()

        service = ChatService()
        result = service.collect_message(db_session, 1, msg.id)
        
        assert result is True
        # 重新查询确认状态改变
        updated = db_session.query(Message).filter(Message.id == msg.id).first()
        assert updated.is_collected is True

        # 再次收藏会取消
        result2 = service.collect_message(db_session, 1, msg.id)
        assert result2 is False
        updated2 = db_session.query(Message).filter(Message.id == msg.id).first()
        assert updated2.is_collected is False

    def test_collect_message_not_found(self, db_session):
        """收藏不存在的消息返回False"""
        service = ChatService()
        result = service.collect_message(db_session, 1, 99999)
        assert result is False

    def test_close_conversation(self, db_session):
        """关闭对话"""
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        assistant = AiAssistant(
            id=1,
            name="test",
            mbti_type=MbtiType.INTJ,
            personality="test description",
            speaking_style="friendly",
            expertise="testing",
            greeting="Hello",
            is_active=True,
        )
        db_session.add(assistant)
        conv = Conversation(
            user_id=1,
            assistant_id=1,
            session_id="session-1",
            title="要关闭",
            status=ConversationStatus.ACTIVE,
        )
        db_session.add(conv)
        db_session.commit()

        service = ChatService()
        result = service.close_conversation(db_session, 1, "session-1")
        
        assert result is True
        updated = service.get_conversation(db_session, 1, "session-1")
        assert updated.status == ConversationStatus.CLOSED

    def test_close_conversation_not_found(self, db_session):
        """关闭不存在的对话返回False"""
        service = ChatService()
        result = service.close_conversation(db_session, 1, "not-exists")
        assert result is False


class TestChatServiceSendMessage:
    """send_message 方法测试"""

    async def test_send_message_success_new_conversation(self, db_session):
        """发送消息成功 - 创建新对话"""
        from unittest.mock import Mock, patch, AsyncMock
        from app.models.member import MemberLevel

        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
            member_level=MemberLevel.FREE,
            member_expire_at=None,
        )
        db_session.add(user)
        assistant = AiAssistant(
            id=1,
            name="test",
            mbti_type=MbtiType.INTJ,
            personality="test description",
            speaking_style="friendly",
            expertise="testing",
            greeting="Hello",
            is_active=True,
        )
        db_session.add(assistant)
        db_session.commit()

        mock_member_svc = Mock()
        mock_member_svc.check_message_limit = AsyncMock(return_value=(True, "", 10))
        mock_member_svc.increment_message_count = AsyncMock()
        
        mock_content_filter = Mock()
        mock_content_filter.check_text = AsyncMock(return_value=(True, None))
        mock_content_filter.get_blocked_response = Mock(return_value="内容不符合社区规范")
        
        mock_generator = Mock()
        mock_generator.generate = AsyncMock(return_value={
            "answer": "这是AI的回复",
            "references": []
        })

        mock_redis = Mock()

        with patch("app.services.chat_service.get_member_service", return_value=mock_member_svc), \
             patch("app.services.chat_service.get_content_filter", return_value=mock_content_filter), \
             patch("app.services.chat_service.get_generator", return_value=mock_generator), \
             patch("app.services.chat_service.get_redis", return_value=AsyncMock(return_value=mock_redis)):

            service = ChatService()
            result = await service.send_message(
                db=db_session,
                user_id=1,
                session_id=None,
                assistant_id=1,
                content="你好，这是一条测试消息",
            )

        assert result is not None
        assert result["session_id"] is not None
        assert result["conversation_id"] is not None
        assert result["user_message"] is not None
        assert result["assistant_message"] is not None
        assert result["assistant_message"]["content"] == "这是AI的回复"
        mock_member_svc.check_message_limit.assert_called_once()
        mock_content_filter.check_text.assert_called_once()
        mock_generator.generate.assert_called_once()
        mock_member_svc.increment_message_count.assert_called_once()

    async def test_send_message_content_blocked(self, db_session):
        """发送消息被内容过滤拦截"""
        from unittest.mock import Mock, patch, AsyncMock
        from app.models.member import MemberLevel

        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
            member_level=MemberLevel.FREE,
            member_expire_at=None,
        )
        db_session.add(user)
        db_session.commit()

        mock_member_svc = Mock()
        mock_member_svc.check_message_limit = AsyncMock(return_value=(True, "", 10))
        
        mock_content_filter = Mock()
        mock_content_filter.check_text = AsyncMock(return_value=(False, "违规内容"))
        mock_content_filter.get_blocked_response = Mock(return_value="内容不符合社区规范")

        mock_redis = Mock()

        with patch("app.services.chat_service.get_member_service", return_value=mock_member_svc), \
             patch("app.services.chat_service.get_content_filter", return_value=mock_content_filter), \
             patch("app.services.chat_service.get_redis", return_value=AsyncMock(return_value=mock_redis)):

            service = ChatService()
            result = await service.send_message(
                db=db_session,
                user_id=1,
                session_id=None,
                assistant_id=1,
                content="违规内容",
            )

        assert result["content_blocked"] is True
        assert result["assistant_message"]["content"] == "内容不符合社区规范"

    async def test_send_message_exceed_limit(self, db_session):
        """发送消息超出限制抛出异常"""
        from unittest.mock import Mock, patch, AsyncMock
        from app.models.member import MemberLevel

        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
            member_level=MemberLevel.FREE,
            member_expire_at=None,
        )
        db_session.add(user)
        db_session.commit()

        mock_member_svc = Mock()
        mock_member_svc.check_message_limit = AsyncMock(return_value=(False, "今日消息限额已用完", 0))
        mock_redis = Mock()

        with patch("app.services.chat_service.get_member_service", return_value=mock_member_svc), \
             patch("app.services.chat_service.get_redis", return_value=AsyncMock(return_value=mock_redis)):

            service = ChatService()
            with pytest.raises(ValueError) as exc_info:
                await service.send_message(
                    db=db_session,
                    user_id=1,
                    session_id=None,
                    assistant_id=1,
                    content="你好",
                )

        assert "今日消息限额已用完" in str(exc_info.value)

    async def test_send_message_user_not_exists(self, db_session):
        """用户不存在抛出异常"""
        from unittest.mock import Mock, patch

        service = ChatService()
        with pytest.raises(ValueError) as exc_info:
            await service.send_message(
                db=db_session,
                user_id=9999,
                session_id=None,
                assistant_id=1,
                content="你好",
            )

        assert "用户不存在" in str(exc_info.value)

    async def test_send_message_no_assistant_id(self, db_session):
        """没有session_id也没有assistant_id抛出异常"""
        from unittest.mock import Mock, patch, AsyncMock
        from app.models.member import MemberLevel

        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
            member_level=MemberLevel.FREE,
            member_expire_at=None,
        )
        db_session.add(user)
        db_session.commit()

        mock_member_svc = Mock()
        mock_member_svc.check_message_limit = AsyncMock(return_value=(True, "", 10))
        mock_redis = Mock()

        with patch("app.services.chat_service.get_member_service", return_value=mock_member_svc), \
             patch("app.services.chat_service.get_redis", return_value=AsyncMock(return_value=mock_redis)):

            service = ChatService()
            with pytest.raises(ValueError) as exc_info:
                await service.send_message(
                    db=db_session,
                    user_id=1,
                    session_id="not-exists",
                    assistant_id=None,
                    content="你好",
                )

        assert "需要指定助手ID" in str(exc_info.value)
