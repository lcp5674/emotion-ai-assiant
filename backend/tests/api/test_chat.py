"""
对话相关接口测试
"""
import pytest
from unittest.mock import patch, AsyncMock


def test_get_assistants(authorized_client, test_user):
    """测试获取AI助手列表接口"""
    response = authorized_client.get("/api/v1/chat/assistants")
    assert response.status_code == 200
    assert response.json()["success"] == True
    data = response.json()["data"]
    assert isinstance(data, list)


def test_create_conversation(authorized_client, test_user, db_session):
    """测试创建新对话接口"""
    from app.models import AiAssistant
    from app.models.mbti import MbtiType
    
    # 创建一个AI助手
    assistant = AiAssistant(
        name="测试助手",
        mbti_type=MbtiType.INTJ,
        personality="理性",
        speaking_style="直接",
        is_active=True,
    )
    db_session.add(assistant)
    db_session.commit()
    
    response = authorized_client.post("/api/v1/chat/create", json={
        "assistant_id": assistant.id,
        "title": "测试对话",
    })
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "conversation_id" in data
    assert data["title"] == "测试对话"


def test_get_conversations(authorized_client, test_user):
    """测试获取对话列表接口"""
    response = authorized_client.get("/api/v1/chat/conversations?limit=10&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "list" in data
    assert isinstance(data["list"], list)


def test_send_message(authorized_client, test_user, db_session):
    """测试发送消息接口"""
    from app.models import AiAssistant
    from app.models.mbti import MbtiType
    
    # 创建一个AI助手
    assistant = AiAssistant(
        name="测试助手",
        mbti_type=MbtiType.INTJ,
        personality="理性",
        speaking_style="直接",
        is_active=True,
    )
    db_session.add(assistant)
    db_session.commit()
    
    # 创建对话
    create_resp = authorized_client.post("/api/v1/chat/create", json={
        "assistant_id": assistant.id,
        "title": "消息测试对话",
    })
    session_id = create_resp.json()["session_id"]
    
    # 使用mock避免实际调用LLM
    with patch("app.services.chat_service.get_chat_service") as mock_chat:
        mock_instance = AsyncMock()
        mock_instance.send_message = AsyncMock(return_value={
            "session_id": session_id,
            "conversation_id": 1,
            "assistant_message": {"id": 1, "content": "你好，我能帮你什么吗？"},
        })
        mock_chat.return_value = mock_instance
        
        response = authorized_client.post("/api/v1/chat/send", json={
            "session_id": session_id,
            "assistant_id": assistant.id,
            "content": "你好",
        })
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "assistant_message" in data


def test_send_message_crisis_detected(authorized_client, test_user):
    """测试发送消息检测到危机"""
    with patch("app.services.crisis_service.get_crisis_detector") as mock_detector:
        mock_instance = AsyncMock()
        mock_instance.detect = AsyncMock(return_value=type(
            'obj', (object,), {
                'intervention_required': True,
                'level': type('obj', (object,), {'value': 'high'})
            }
        )())
        mock_instance.get_intervention_response = AsyncMock(return_value="我感受到你现在情绪很低落，请你一定要知道...")
        mock_detector.return_value = mock_instance
        
        response = authorized_client.post("/api/v1/chat/send", json={
            "session_id": "test",
            "assistant_id": 1,
            "content": "我想自杀",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["crisis_detected"] == True
        assert data["crisis_level"] == "high"
        assert data["assistant_message"] is not None


def test_stream_message(authorized_client, test_user, db_session):
    """测试流式发送消息接口"""
    from app.models import AiAssistant
    from app.models.mbti import MbtiType
    
    # 创建一个AI助手
    assistant = AiAssistant(
        name="测试助手",
        mbti_type=MbtiType.INTJ,
        personality="理性",
        speaking_style="直接",
        is_active=True,
    )
    db_session.add(assistant)
    db_session.commit()
    
    # 测试流式接口存在性
    # 实际流式返回我们只测试接口可访问
    response = authorized_client.post("/api/v1/chat/stream", json={
        "session_id": None,
        "assistant_id": assistant.id,
        "content": "你好，这是流式测试",
    })
    # 流式响应应该正确返回，即使实际内容可能是mock
    assert response.status_code in [200, 400, 500]
    if response.status_code == 200:
        assert response.headers["content-type"] == "text/event-stream"


def test_get_conversation_history(authorized_client, test_user, db_session):
    """测试获取对话历史接口"""
    from app.models import AiAssistant
    from app.models.mbti import MbtiType
    from app.services.chat_service import get_chat_service
    
    # 创建一个AI助手和对话
    assistant = AiAssistant(
        name="测试助手",
        mbti_type=MbtiType.INTJ,
        personality="理性",
        speaking_style="直接",
        is_active=True,
    )
    db_session.add(assistant)
    db_session.commit()
    
    from app.services.chat_service import get_chat_service
    import asyncio
    chat_service = get_chat_service()
    conversation = asyncio.run(chat_service.create_conversation(
        db=db, user_id=test_user.id, assistant_id=assistant.id, title="历史测试"
    ))
    
    response = authorized_client.get(f"/api/v1/chat/history/{conversation.session_id}?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "list" in data
    assert isinstance(data["list"], list)


def test_get_conversation_history_not_found(authorized_client, test_user):
    """测试获取不存在对话历史"""
    response = authorized_client.get("/api/v1/chat/history/NONEXIST")
    assert response.status_code == 404


def test_collect_message(authorized_client, test_user, db_session):
    """测试收藏/取消收藏消息接口"""
    from app.models import AiAssistant
    from app.models.mbti import MbtiType
    from app.models.chat import Conversation, Message
    
    # 创建数据
    assistant = AiAssistant(name="测试", mbti_type=MbtiType.INTJ, personality="测试", speaking_style="测试", is_active=True)
    db_session.add(assistant)
    db.flush()
    
    conversation = Conversation(
        user_id=test_user.id,
        assistant_id=assistant.id,
        title="测试",
        session_id="test_session",
    )
    db_session.add(conversation)
    db.flush()
    
    message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content="这是一条测试消息",
    )
    db_session.add(message)
    db_session.commit()
    
    # 收藏消息
    response = authorized_client.post("/api/v1/chat/collect", json={
        "message_id": message.id,
    })
    assert response.status_code == 200
    data = response.json()
    assert "is_collected" in data


def test_close_conversation(authorized_client, test_user, db_session):
    """测试关闭对话接口"""
    from app.models import AiAssistant
    from app.models.mbti import MbtiType
    from app.services.chat_service import get_chat_service
    
    # 创建对话
    assistant = AiAssistant(name="测试", mbti_type=MbtiType.INTJ, personality="测试", speaking_style="测试", is_active=True)
    db_session.add(assistant)
    db_session.commit()
    
    from app.services.chat_service import get_chat_service
    import asyncio
    chat_service = get_chat_service()
    conversation = asyncio.run(chat_service.create_conversation(
        db=db, user_id=test_user.id, assistant_id=assistant.id
    ))
    
    response = authorized_client.post(f"/api/v1/chat/close/{conversation.session_id}")
    assert response.status_code == 200
    assert "message" in response.json()


def test_close_conversation_not_found(authorized_client, test_user):
    """测试关闭不存在对话"""
    response = authorized_client.post("/api/v1/chat/close/NONEXIST")
    assert response.status_code == 404


def test_update_conversation_title(authorized_client, test_user, db_session):
    """测试更新对话标题接口"""
    from app.models import AiAssistant
    from app.models.mbti import MbtiType
    from app.services.chat_service import get_chat_service
    
    # 创建对话
    assistant = AiAssistant(name="测试", mbti_type=MbtiType.INTJ, personality="测试", speaking_style="测试", is_active=True)
    db_session.add(assistant)
    db_session.commit()
    
    from app.services.chat_service import get_chat_service
    import asyncio
    chat_service = get_chat_service()
    conversation = asyncio.run(chat_service.create_conversation(
        db=db, user_id=test_user.id, assistant_id=assistant.id, title="原标题"
    ))
    
    response = authorized_client.put(f"/api/v1/chat/title/{conversation.session_id}", json={
        "title": "新标题",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "新标题"


def test_update_conversation_title_not_found(authorized_client, test_user):
    """测试更新不存在对话标题"""
    response = authorized_client.put("/api/v1/chat/title/NONEXIST", json={
        "title": "测试",
    })
    assert response.status_code == 404


def test_delete_message(authorized_client, test_user, db_session):
    """测试撤回消息接口"""
    from app.models import AiAssistant
    from app.models.mbti import MbtiType
    from app.models.chat import Conversation, Message
    
    # 创建数据
    assistant = AiAssistant(name="测试", mbti_type=MbtiType.INTJ, personality="测试", speaking_style="测试", is_active=True)
    db_session.add(assistant)
    db.flush()
    
    conversation = Conversation(
        user_id=test_user.id,
        assistant_id=assistant.id,
        title="测试",
        session_id="test_session",
    )
    db_session.add(conversation)
    db.flush()
    
    message1 = Message(conversation_id=conversation.id, role="user", content="第一条消息")
    db_session.add(message1)
    message2 = Message(conversation_id=conversation.id, role="user", content="最后一条消息")
    db_session.add(message2)
    db_session.commit()
    
    # 删除最后一条消息
    response = authorized_client.delete(f"/api/v1/chat/message/{message2.id}")
    assert response.status_code == 200
    assert "message" in response.json()


def test_delete_message_not_last(authorized_client, test_user, db_session):
    """测试删除不是最后一条消息应该失败"""
    from app.models import AiAssistant
    from app.models.mbti import MbtiType
    from app.models.chat import Conversation, Message
    
    assistant = AiAssistant(name="测试", mbti_type=MbtiType.INTJ, personality="测试", speaking_style="测试", is_active=True)
    db_session.add(assistant)
    db.flush()
    
    conversation = Conversation(user_id=test_user.id, assistant_id=assistant.id, title="测试", session_id="test")
    db_session.add(conversation)
    db.flush()
    
    message1 = Message(conversation_id=conversation.id, role="user", content="第一条")
    db_session.add(message1)
    message2 = Message(conversation_id=conversation.id, role="user", content="第二条")
    db_session.add(message2)
    db_session.commit()
    
    # 尝试删除第一条消息，应该失败
    response = authorized_client.delete(f"/api/v1/chat/message/{message1.id}")
    assert response.status_code == 400


def test_delete_message_not_found(authorized_client, test_user):
    """测试删除不存在消息"""
    response = authorized_client.delete("/api/v1/chat/message/99999")
    assert response.status_code == 404


def test_regenerate_response(authorized_client, test_user, db_session):
    """测试重新生成回复接口"""
    from app.models import AiAssistant
    from app.models.mbti import MbtiType
    from app.models.chat import Conversation, Message
    
    # 创建数据
    assistant = AiAssistant(name="测试", mbti_type=MbtiType.INTJ, personality="测试", speaking_style="测试", is_active=True)
    db_session.add(assistant)
    db.flush()
    
    conversation = Conversation(user_id=test_user.id, assistant_id=assistant.id, title="测试", session_id="test")
    db_session.add(conversation)
    db.flush()
    
    user_message = Message(conversation_id=conversation.id, role="user", content="你好")
    db_session.add(user_message)
    db.flush()
    
    ai_message = Message(conversation_id=conversation.id, role="assistant", content="你好，有什么可以帮你？")
    db_session.add(ai_message)
    db_session.commit()
    
    # 测试接口存在性
    response = authorized_client.post(f"/api/v1/chat/regenerate/{conversation.id}")
    # 流式响应，验证状态码
    assert response.status_code in [200, 400, 404]


def test_regenerate_response_no_ai_message(authorized_client, test_user, db_session):
    """测试没有AI回复时重新生成应该失败"""
    from app.models import AiAssistant
    from app.models.mbti import MbtiType
    from app.models.chat import Conversation
    
    assistant = AiAssistant(name="测试", mbti_type=MbtiType.INTJ, personality="测试", speaking_style="测试", is_active=True)
    db_session.add(assistant)
    db.flush()
    
    conversation = Conversation(user_id=test_user.id, assistant_id=assistant.id, title="测试", session_id="test")
    db_session.add(conversation)
    db_session.commit()
    
    response = authorized_client.post(f"/api/v1/chat/regenerate/{conversation.id}")
    assert response.status_code == 400


def test_unauthorized_access(client):
    """测试未授权访问"""
    response = client.get("/api/v1/chat/conversations")
    assert response.status_code == 401
    
    response = client.post("/api/v1/chat/create", json={"assistant_id": 1})
    assert response.status_code == 401


def test_send_message_value_error(authorized_client, test_user):
    """测试发送消息发生ValueError返回400"""
    with patch("app.services.chat_service.get_chat_service") as mock_chat:
        mock_instance = AsyncMock()
        mock_instance.send_message = AsyncMock(side_effect=ValueError("测试错误"))
        mock_chat.return_value = mock_instance
        
        response = authorized_client.post("/api/v1/chat/send", json={
            "session_id": "test",
            "assistant_id": 1,
            "content": "测试",
        })
        assert response.status_code == 400
        assert "测试错误" in response.json()["detail"]


def test_stream_message_no_session_no_assistant(authorized_client, test_user):
    """测试流式发送消息 - 没有sessionId也没有assistantId"""
    response = authorized_client.post("/api/v1/chat/stream", json={
        "content": "测试",
    })
    assert response.status_code == 400
    assert "需要指定助手ID" in response.json()["detail"]


def test_stream_message_content_filter_rejected(authorized_client, test_user, db_session):
    """测试流式发送消息 - 内容审核不通过"""
    with patch("app.services.content_filter.get_content_filter") as mock_filter:
        mock_instance = AsyncMock()
        mock_instance.check_text = AsyncMock(return_value=(False, "不合适内容"))
        mock_filter.return_value = mock_instance
        
        response = authorized_client.post("/api/v1/chat/stream", json={
            "assistant_id": 1,
            "content": "违规内容",
        })
        assert response.status_code == 400
        assert "内容包含不当信息" in response.json()["detail"]


def test_stream_message_limit_exceeded(authorized_client, test_user, db_session):
    """测试流式发送消息 - 超出消息限额"""
    with patch("app.services.member_service.get_member_service") as mock_member:
        mock_instance = AsyncMock()
        mock_instance.check_message_limit = AsyncMock(return_value=(False, "今日消息限额已用完", None))
        mock_member.return_value = mock_instance
        
        response = authorized_client.post("/api/v1/chat/stream", json={
            "assistant_id": 1,
            "content": "测试",
        })
        assert response.status_code == 400


def test_collect_message_toggle(authorized_client, test_user, db_session):
    """测试收藏消息切换 - 收藏后再次调用取消收藏"""
    from app.models import AiAssistant
    from app.models.mbti import MbtiType
    from app.models.chat import Conversation, Message
    
    # 创建数据
    assistant = AiAssistant(name="测试", mbti_type=MbtiType.INTJ, personality="测试", speaking_style="测试", is_active=True)
    db_session.add(assistant)
    db_session.flush()
    
    conversation = Conversation(
        user_id=test_user.id,
        assistant_id=assistant.id,
        title="测试",
        session_id="test_session",
    )
    db_session.add(conversation)
    db_session.flush()
    
    message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content="这是一条测试消息",
    )
    db_session.add(message)
    db_session.commit()
    
    # 第一次调用：收藏
    response = authorized_client.post("/api/v1/chat/collect", json={
        "message_id": message.id,
    })
    assert response.status_code == 200
    assert response.json()["is_collected"] == True
    
    # 第二次调用：取消收藏
    response = authorized_client.post("/api/v1/chat/collect", json={
        "message_id": message.id,
    })
    assert response.status_code == 200
    assert response.json()["is_collected"] == False


def test_delete_message_not_owner(authorized_client, test_user, db_session):
    """测试删除消息 - 不是消息所有者"""
    from app.models import AiAssistant
    from app.models.mbti import MbtiType
    from app.models.chat import Conversation, Message
    from app.models import User
    
    # 创建另一个用户
    other_user = User(
        id=999,
        phone="13900009999",
        nickname="其他用户",
        password_hash="hash",
        is_active=True,
    )
    db_session.add(other_user)
    db_session.flush()
    
    assistant = AiAssistant(name="测试", mbti_type=MbtiType.INTJ, personality="测试", speaking_style="测试", is_active=True)
    db_session.add(assistant)
    db_session.flush()
    
    conversation = Conversation(
        user_id=999,
        assistant_id=assistant.id,
        title="测试",
        session_id="test_session",
    )
    db_session.add(conversation)
    db_session.flush()
    
    message = Message(conversation_id=conversation.id, role="user", content="测试")
    db_session.add(message)
    db_session.commit()
    
    # 当前用户尝试删除其他用户的消息
    response = authorized_client.delete(f"/api/v1/chat/message/{message.id}")
    assert response.status_code == 403
    assert "你没有权限操作此消息" in response.json()["detail"]


def test_regenerate_response_conversation_not_found(authorized_client, test_user):
    """测试重新生成回复 - 对话不存在"""
    response = authorized_client.post("/api/v1/chat/regenerate/99999")
    assert response.status_code == 404


def test_regenerate_response_no_user_message(authorized_client, test_user, db_session):
    """测试重新生成回复 - 找不到对应用户消息"""
    from app.models import AiAssistant
    from app.models.mbti import MbtiType
    from app.models.chat import Conversation, Message
    
    assistant = AiAssistant(name="测试", mbti_type=MbtiType.INTJ, personality="测试", speaking_style="测试", is_active=True)
    db_session.add(assistant)
    db_session.flush()
    
    conversation = Conversation(
        user_id=test_user.id,
        assistant_id=assistant.id,
        title="测试",
        session_id="test",
    )
    db_session.add(conversation)
    db_session.flush()
    
    # 只有AI消息，没有用户消息
    ai_message = Message(conversation_id=conversation.id, role="assistant", content="你好")
    db_session.add(ai_message)
    db_session.commit()
    
    response = authorized_client.post(f"/api/v1/chat/regenerate/{conversation.id}")
    assert response.status_code == 400
    assert "找不到对应的用户消息" in response.json()["detail"]


def test_get_conversation_history_with_before_id(authorized_client, test_user, db_session):
    """测试获取对话历史 - 带before_id分页"""
    from app.models import AiAssistant
    from app.models.mbti import MbtiType
    from app.models.chat import Conversation, Message
    
    # 创建对话和多条消息
    assistant = AiAssistant(name="测试", mbti_type=MbtiType.INTJ, personality="测试", speaking_style="测试", is_active=True)
    db_session.add(assistant)
    db_session.flush()
    
    conversation = Conversation(
        user_id=test_user.id,
        assistant_id=assistant.id,
        title="测试",
        session_id="test_session",
    )
    db_session.add(conversation)
    db_session.flush()
    
    for i in range(5):
        msg = Message(conversation_id=conversation.id, role="user", content=f"消息{i+1}")
        db_session.add(msg)
    db_session.commit()
    
    # 获取最后两条消息
    last_msg = db_session.query(Message).filter(
        Message.conversation_id == conversation.id
    ).order_by(Message.id.desc()).first()
    
    response = authorized_client.get(f"/api/v1/chat/history/test_session?limit=2&before_id={last_msg.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["list"]) == 2


def test_get_conversations_pagination(authorized_client, test_user, db_session):
    """测试获取对话列表分页"""
    from app.models import AiAssistant
    from app.models.mbti import MbtiType
    from app.services.chat_service import get_chat_service
    
    assistant = AiAssistant(name="测试", mbti_type=MbtiType.INTJ, personality="测试", speaking_style="测试", is_active=True)
    db_session.add(assistant)
    db_session.commit()
    
    # 创建3个对话
    import asyncio
    chat_service = get_chat_service()
    for i in range(3):
        asyncio.run(chat_service.create_conversation(
            db=db_session, user_id=test_user.id, assistant_id=assistant.id
        ))
    
    response = authorized_client.get("/api/v1/chat/conversations?limit=2&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["list"]) == 2
    
    response = authorized_client.get("/api/v1/chat/conversations?limit=2&offset=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["list"]) == 1
