#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WebSocket聊天服务单元测试 - 完全重写确保正确覆盖所有分支
"""
import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.websocket.chat import ConnectionManager, get_websocket_current_user, handle_websocket_chat
from app.websocket.chat import manager as global_manager


class TestConnectionManager:
    """连接管理器测试"""

    def test_init(self):
        """测试初始化"""
        manager = ConnectionManager()
        assert manager.active_connections == {}
        assert manager.session_users == {}

    async def test_connect(self):
        """测试连接建立"""
        manager = ConnectionManager()
        mock_ws = AsyncMock(spec=WebSocket)
        
        await manager.connect(mock_ws, user_id=1, session_id="test-session")
        
        mock_ws.accept.assert_awaited_once()
        assert 1 in manager.active_connections
        assert manager.active_connections[1] == mock_ws
        assert manager.session_users["test-session"] == 1

    async def test_connect_no_session_id(self):
        """测试连接建立不需要session_id"""
        manager = ConnectionManager()
        mock_ws = AsyncMock(spec=WebSocket)
        
        await manager.connect(mock_ws, user_id=1)
        
        mock_ws.accept.assert_awaited_once()
        assert 1 in manager.active_connections
        assert len(manager.session_users) == 0

    def test_disconnect(self):
        """测试断开连接"""
        manager = ConnectionManager()
        mock_ws = AsyncMock(spec=WebSocket)
        manager.active_connections[1] = mock_ws
        manager.session_users["test-session"] = 1
        
        manager.disconnect(1, "test-session")
        
        assert 1 not in manager.active_connections
        assert "test-session" not in manager.session_users

    def test_disconnect_user_not_exists(self):
        """测试断开不存在用户不报错
        即使user不存在，session仍会被删除（代码逻辑如此）"""
        manager = ConnectionManager()
        manager.active_connections[1] = AsyncMock()
        manager.session_users["test-session"] = 1
        
        # 断开不存在的用户，但session存在会删除session
        manager.disconnect(999, "test-session")
        # user仍然存在（本来就不在）
        assert 1 in manager.active_connections
        # session被删除，因为session存在
        assert "test-session" not in manager.session_users

    def test_disconnect_no_session_id(self):
        """测试断开连接不需要session_id"""
        manager = ConnectionManager()
        mock_ws = AsyncMock(spec=WebSocket)
        manager.active_connections[1] = mock_ws
        
        manager.disconnect(1)
        
        assert 1 not in manager.active_connections

    async def test_send_message(self):
        """测试发送消息"""
        manager = ConnectionManager()
        mock_ws = AsyncMock(spec=WebSocket)
        manager.active_connections[1] = mock_ws
        
        await manager.send_message(1, {"type": "test", "content": "hello"})
        
        mock_ws.send_text.assert_awaited_once()
        # 验证JSON序列化
        sent_json = mock_ws.send_text.call_args[0][0]
        parsed = json.loads(sent_json)
        assert parsed["type"] == "test"
        assert parsed["content"] == "hello"

    async def test_send_message_not_connected(self):
        """测试发送消息给未连接用户不报错"""
        manager = ConnectionManager()
        mock_ws = AsyncMock(spec=WebSocket)
        
        # 不应该抛出异常
        await manager.send_message(999, {"type": "test"})
        mock_ws.send_text.assert_not_called()

    async def test_broadcast(self):
        """测试广播"""
        manager = ConnectionManager()
        mock_ws1 = AsyncMock(spec=WebSocket)
        mock_ws2 = AsyncMock(spec=WebSocket)
        mock_ws3 = AsyncMock(spec=WebSocket)
        
        manager.active_connections[1] = mock_ws1
        manager.active_connections[2] = mock_ws2
        manager.active_connections[3] = mock_ws3
        
        await manager.broadcast({"type": "broadcast", "data": "test"}, exclude=1)
        
        mock_ws1.send_text.assert_not_called()
        mock_ws2.send_text.assert_awaited_once()
        mock_ws3.send_text.assert_awaited_once()

    async def test_broadcast_no_exclude(self):
        """测试广播不排除用户"""
        manager = ConnectionManager()
        mock_ws1 = AsyncMock(spec=WebSocket)
        manager.active_connections[1] = mock_ws1
        
        await manager.broadcast({"type": "test"})
        mock_ws1.send_text.assert_awaited_once()


class TestGetCurrentUser:
    """测试从WebSocket获取当前用户"""

    async def test_no_token_closes_connection(self):
        """测试没有token关闭连接"""
        mock_ws = AsyncMock(spec=WebSocket)
        mock_ws.query_params.get.return_value = None
        
        with pytest.raises(WebSocketDisconnect):
            await get_websocket_current_user(mock_ws)
        
        mock_ws.close.assert_awaited_once()

    async def test_invalid_token_closes_connection(self):
        """测试无效token关闭连接"""
        mock_ws = AsyncMock(spec=WebSocket)
        mock_ws.query_params.get.return_value = "invalid-token"
        
        with patch("app.websocket.chat.decode_token", return_value=None):
            with pytest.raises(WebSocketDisconnect):
                await get_websocket_current_user(mock_ws)
        
        mock_ws.close.assert_awaited_once()

    async def test_user_not_found_closes_connection(self):
        """测试用户不存在关闭连接"""
        from app.core.database import SessionLocal
        mock_ws = AsyncMock(spec=WebSocket)
        mock_ws.query_params.get.return_value = "valid-token"
        
        with patch("app.websocket.chat.decode_token", return_value={"sub": "999"}):
            with patch("app.core.database.SessionLocal") as mock_session:
                mock_db = Mock()
                mock_db.query.return_value.filter.return_value.first.return_value = None
                mock_session.return_value = mock_db
                
                with pytest.raises(WebSocketDisconnect):
                    await get_websocket_current_user(mock_ws)
                
                mock_ws.close.assert_awaited_once()

    async def test_valid_token_returns_user(self):
        """测试有效token返回用户"""
        from app.core.database import SessionLocal
        mock_ws = AsyncMock(spec=WebSocket)
        mock_ws.query_params.get.return_value = "valid-token"
        
        mock_user = Mock()
        mock_user.id = 1
        
        with patch("app.websocket.chat.decode_token", return_value={"sub": "1"}):
            with patch("app.core.database.SessionLocal") as mock_session:
                mock_db = Mock()
                mock_db.query.return_value.filter.return_value.first.return_value = mock_user
                mock_session.return_value = mock_db
                
                result = await get_websocket_current_user(mock_ws)
                
                assert result == mock_user


@pytest.mark.asyncio
async def test_handle_websocket_chat_no_assistant_id():
    """测试没有assistant_id且没有session_id返回错误"""
    mock_ws = AsyncMock(spec=WebSocket)
    mock_ws.query_params.get.side_effect = lambda key: {
        "session_id": None,
        "assistant_id": None
    }.get(key)
    
    mock_user = Mock(id=1)
    mock_db = Mock(spec=Session)
    
    with patch("app.websocket.chat.manager") as mock_manager:
        mock_manager.connect = AsyncMock()
        
        await handle_websocket_chat(mock_ws, mock_user, mock_db)
        
        # 验证发送错误消息
        mock_ws.send_text.assert_awaited_once()
        sent = json.loads(mock_ws.send_text.call_args[0][0])
        assert sent["type"] == "error"
        assert "需要指定助手ID" in sent["message"]
        mock_manager.disconnect.assert_called_once_with(1, None)


@pytest.mark.asyncio
async def test_handle_websocket_chat_empty_message():
    """测试空消息返回错误但不断开连接"""
    mock_ws = AsyncMock(spec=WebSocket)
    mock_ws.query_params.get.side_effect = lambda key: {
        "session_id": "test-session",
        "assistant_id": "1"
    }.get(key)
    
    # 模拟对话已存在
    mock_conversation = Mock()
    mock_conversation.id = 1
    mock_conversation.assistant_id = 1
    mock_conversation.updated_at = None
    mock_conversation.message_count = 0
    
    mock_user = Mock(id=1, mbti_type="INTJ")
    mock_db = Mock(spec=Session)
    
    # 构建正确的链式调用 history: filter -> order_by -> limit -> all
    mock_history = Mock()
    mock_history.all.return_value = []
    mock_history_limit = Mock()
    mock_history_limit.limit.return_value = mock_history
    mock_history_order = Mock()
    mock_history_order.order_by.return_value = mock_history_limit
    mock_history_filter = Mock()
    mock_history_filter.filter.return_value = mock_history_order
    
    mock_conv_filter = Mock()
    mock_conv_filter.first.return_value = mock_conversation
    mock_conv_filter_filter = Mock()
    mock_conv_filter_filter.filter.return_value = mock_conv_filter
    
    mock_ai_filter = Mock()
    mock_ai_filter.first.return_value = None
    mock_ai_filter_filter = Mock()
    mock_ai_filter_filter.filter.return_value = mock_ai_filter
    
    def mock_query(model):
        if model.__name__ == "Conversation":
            return mock_conv_filter_filter
        elif model.__name__ == "AiAssistant":
            return mock_ai_filter_filter
        elif model.__name__ == "Message":
            return mock_history_filter
        return Mock()
    
    mock_db.query = mock_query
    
    with patch("app.websocket.chat.manager") as mock_manager:
        mock_manager.connect = AsyncMock()
        
        # 第一次receive_text返回空内容消息
        mock_ws.receive_text = AsyncMock(side_effect=[
            json.dumps({"content": ""}),
            WebSocketDisconnect()
        ])
        
        try:
            await handle_websocket_chat(mock_ws, mock_user, mock_db)
        except WebSocketDisconnect:
            pass
        
        # 验证发送了错误消息
        error_calls = [
            call for call in mock_ws.send_text.await_args_list
            if "空" in json.loads(call[0][0]).get("message", "")
        ]
        assert len(error_calls) >= 1


@pytest.mark.asyncio
async def test_handle_websocket_chat_invalid_json():
    """测试无效JSON格式返回错误"""
    mock_ws = AsyncMock(spec=WebSocket)
    mock_ws.query_params.get.side_effect = lambda key: {
        "session_id": "test-session",
        "assistant_id": "1"
    }.get(key)
    
    mock_conversation = Mock()
    mock_conversation.id = 1
    mock_conversation.assistant_id = 1
    mock_conversation.updated_at = None
    mock_conversation.message_count = 0
    
    mock_user = Mock(id=1, mbti_type="INTJ")
    mock_db = Mock(spec=Session)
    
    # 构建正确的链式调用 history: filter -> order_by -> limit -> all
    mock_history = Mock()
    mock_history.all.return_value = []
    mock_history_limit = Mock()
    mock_history_limit.limit.return_value = mock_history
    mock_history_order = Mock()
    mock_history_order.order_by.return_value = mock_history_limit
    mock_history_filter = Mock()
    mock_history_filter.filter.return_value = mock_history_order
    
    mock_conv_filter = Mock()
    mock_conv_filter.first.return_value = mock_conversation
    mock_conv_filter_filter = Mock()
    mock_conv_filter_filter.filter.return_value = mock_conv_filter
    
    mock_ai_filter = Mock()
    mock_ai_filter.first.return_value = None
    mock_ai_filter_filter = Mock()
    mock_ai_filter_filter.filter.return_value = mock_ai_filter
    
    def mock_query(model):
        if model.__name__ == "Conversation":
            return mock_conv_filter_filter
        elif model.__name__ == "AiAssistant":
            return mock_ai_filter_filter
        elif model.__name__ == "Message":
            return mock_history_filter
        return Mock()
    
    mock_db.query = mock_query
    
    with patch("app.websocket.chat.manager") as mock_manager:
        mock_manager.connect = AsyncMock()
        
        mock_ws.receive_text = AsyncMock(side_effect=[
            "not valid json{{",
            WebSocketDisconnect()
        ])
        
        try:
            await handle_websocket_chat(mock_ws, mock_user, mock_db)
        except WebSocketDisconnect:
            pass
        
        # 验证发送了JSON格式错误
        error_found = False
        for call in mock_ws.send_text.await_args_list:
            msg = json.loads(call[0][0])
            if msg.get("type") == "error" and "无效的消息格式" in msg.get("message", ""):
                error_found = True
                break
        assert error_found


@pytest.mark.asyncio
async def test_handle_websocket_chat_content_filter_rejected():
    """测试内容过滤拒绝"""
    mock_ws = AsyncMock(spec=WebSocket)
    mock_ws.query_params.get.side_effect = lambda key: {
        "session_id": "test-session",
        "assistant_id": "1"
    }.get(key)
    
    mock_conversation = Mock()
    mock_conversation.id = 1
    mock_conversation.assistant_id = 1
    mock_conversation.updated_at = None
    mock_conversation.message_count = 0
    
    mock_user = Mock(id=1, mbti_type="INTJ")
    mock_db = Mock(spec=Session)
    
    # 构建正确的链式调用 history: filter -> order_by -> limit -> all
    mock_history = Mock()
    mock_history.all.return_value = []
    mock_history_limit = Mock()
    mock_history_limit.limit.return_value = mock_history
    mock_history_order = Mock()
    mock_history_order.order_by.return_value = mock_history_limit
    mock_history_filter = Mock()
    mock_history_filter.filter.return_value = mock_history_order
    
    mock_conv_filter = Mock()
    mock_conv_filter.first.return_value = mock_conversation
    mock_conv_filter_filter = Mock()
    mock_conv_filter_filter.filter.return_value = mock_conv_filter
    
    mock_ai_filter = Mock()
    mock_ai_filter.first.return_value = None
    mock_ai_filter_filter = Mock()
    mock_ai_filter_filter.filter.return_value = mock_ai_filter
    
    def mock_query(model):
        if model.__name__ == "Conversation":
            return mock_conv_filter_filter
        elif model.__name__ == "AiAssistant":
            return mock_ai_filter_filter
        elif model.__name__ == "Message":
            return mock_history_filter
        return Mock()
    
    mock_db.query = mock_query
    
    with patch("app.websocket.chat.manager") as mock_manager:
        mock_manager.connect = AsyncMock()
        
        mock_content_filter = AsyncMock()
        mock_content_filter.check_text = AsyncMock(return_value=(False, "内容不当"))
        
        with patch("app.websocket.chat.get_content_filter", return_value=mock_content_filter):
                mock_ws.receive_text = AsyncMock(side_effect=[
                    json.dumps({"content": "违禁内容"}),
                    WebSocketDisconnect()
                ])
                
                try:
                    await handle_websocket_chat(mock_ws, mock_user, mock_db)
                except WebSocketDisconnect:
                    pass
                
                # 验证发送了内容拒绝错误
                error_found = False
                for call in mock_ws.send_text.await_args_list:
                    msg = json.loads(call[0][0])
                    if msg.get("type") == "error" and "内容包含不当信息" in msg.get("message", ""):
                        error_found = True
                        break
                assert error_found


@pytest.mark.asyncio
async def test_handle_websocket_chat_crisis_detected():
    """测试危机检测触发干预"""
    mock_ws = AsyncMock(spec=WebSocket)
    mock_ws.query_params.get.side_effect = lambda key: {
        "session_id": "test-session",
        "assistant_id": "1"
    }.get(key)
    
    mock_conversation = Mock()
    mock_conversation.id = 1
    mock_conversation.assistant_id = 1
    mock_conversation.updated_at = None
    mock_conversation.message_count = 0
    
    mock_user = Mock(id=1, mbti_type="INTJ")
    mock_db = Mock(spec=Session)
    
    # 构建正确的链式调用 history: filter -> order_by -> limit -> all
    mock_history = Mock()
    mock_history.all.return_value = []
    mock_history_limit = Mock()
    mock_history_limit.limit.return_value = mock_history
    mock_history_order = Mock()
    mock_history_order.order_by.return_value = mock_history_limit
    mock_history_filter = Mock()
    mock_history_filter.filter.return_value = mock_history_order
    
    mock_conv_filter = Mock()
    mock_conv_filter.first.return_value = mock_conversation
    mock_conv_filter_filter = Mock()
    mock_conv_filter_filter.filter.return_value = mock_conv_filter
    
    mock_ai_filter = Mock()
    mock_ai_filter.first.return_value = None
    mock_ai_filter_filter = Mock()
    mock_ai_filter_filter.filter.return_value = mock_ai_filter
    
    def mock_query(model):
        if model.__name__ == "Conversation":
            return mock_conv_filter_filter
        elif model.__name__ == "AiAssistant":
            return mock_ai_filter_filter
        elif model.__name__ == "Message":
            return mock_history_filter
        return Mock()
    
    mock_db.query = mock_query
    
    with patch("app.websocket.chat.manager") as mock_manager:
        mock_manager.connect = AsyncMock()
        
        mock_content_filter = AsyncMock()
        mock_content_filter.check_text = AsyncMock(return_value=(True, None))
        
        from app.services.crisis_service import CrisisLevel
        mock_crisis_result = Mock()
        mock_crisis_result.intervention_required = True
        mock_crisis_result.level = CrisisLevel.HIGH
        
        mock_crisis_detector = AsyncMock()
        mock_crisis_detector.detect = AsyncMock(return_value=mock_crisis_result)
        mock_crisis_detector.get_intervention_response = AsyncMock(return_value="这是危机干预回复")
        
        with patch("app.websocket.chat.get_content_filter", return_value=mock_content_filter):
            with patch("app.websocket.chat.get_crisis_detector", return_value=mock_crisis_detector):
                mock_ws.receive_text = AsyncMock(side_effect=[
                    json.dumps({"content": "我想自杀"}),
                    WebSocketDisconnect()
                ])
                
                try:
                    await handle_websocket_chat(mock_ws, mock_user, mock_db)
                except WebSocketDisconnect:
                    pass
                
                # 验证发送了危机检测消息
                crisis_found = False
                for call in mock_ws.send_text.await_args_list:
                    msg = json.loads(call[0][0])
                    if msg.get("type") == "crisis_detected":
                        crisis_found = True
                        assert msg.get("level") == "high"
                        break
                assert crisis_found


@pytest.mark.asyncio
async def test_handle_websocket_chat_general_exception_handling():
    """测试一般异常处理"""
    mock_ws = AsyncMock(spec=WebSocket)
    mock_ws.query_params.get.side_effect = lambda key: {
        "session_id": "test-session",
        "assistant_id": "1"
    }.get(key)
    
    mock_conversation = Mock()
    mock_conversation.id = 1
    mock_conversation.assistant_id = 1
    mock_conversation.updated_at = None
    mock_conversation.message_count = 0
    
    mock_user = Mock(id=1, mbti_type="INTJ")
    mock_db = Mock(spec=Session)
    
    # 构建正确的链式调用 history: filter -> order_by -> limit -> all
    mock_history = Mock()
    mock_history.all.return_value = []
    mock_history_limit = Mock()
    mock_history_limit.limit.return_value = mock_history
    mock_history_order = Mock()
    mock_history_order.order_by.return_value = mock_history_limit
    mock_history_filter = Mock()
    mock_history_filter.filter.return_value = mock_history_order
    
    mock_conv_filter = Mock()
    mock_conv_filter.first.return_value = mock_conversation
    mock_conv_filter_filter = Mock()
    mock_conv_filter_filter.filter.return_value = mock_conv_filter
    
    mock_ai_filter = Mock()
    mock_ai_filter.first.return_value = None
    mock_ai_filter_filter = Mock()
    mock_ai_filter_filter.filter.return_value = mock_ai_filter
    
    def mock_query(model):
        if model.__name__ == "Conversation":
            return mock_conv_filter_filter
        elif model.__name__ == "AiAssistant":
            return mock_ai_filter_filter
        elif model.__name__ == "Message":
            return mock_history_filter
        return Mock()
    
    mock_db.query = mock_query
    
    with patch("app.websocket.chat.manager") as mock_manager:
        mock_manager.connect = AsyncMock()
        
        mock_content_filter = AsyncMock()
        mock_content_filter.check_text = AsyncMock(side_effect=Exception("测试异常"))
        
        with patch("app.websocket.chat.get_content_filter", return_value=mock_content_filter):
            with patch("app.websocket.chat.loguru.logger.error") as mock_logger:
                mock_ws.receive_text = AsyncMock(side_effect=[
                    json.dumps({"content": "测试消息"}),
                    WebSocketDisconnect()
                ])
                
                try:
                    await handle_websocket_chat(mock_ws, mock_user, mock_db)
                except WebSocketDisconnect:
                    pass
                
                # 验证日志记录了错误
                mock_logger.assert_called()
                # 验证发送了错误消息给客户端
                error_found = False
                for call in mock_ws.send_text.await_args_list:
                    msg = json.loads(call[0][0])
                    if msg.get("type") == "error" and "服务器错误" in msg.get("message", ""):
                        error_found = True
                        break
                assert error_found


@pytest.mark.asyncio
async def test_handle_websocket_chat_retrieval_exception():
    """测试检索失败不中断流程，使用空文档"""
    mock_ws = AsyncMock(spec=WebSocket)
    mock_ws.query_params.get.side_effect = lambda key: {
        "session_id": "test-session",
        "assistant_id": "1"
    }.get(key)
    
    mock_conversation = Mock()
    mock_conversation.id = 1
    mock_conversation.assistant_id = 1
    mock_conversation.updated_at = None
    mock_conversation.message_count = 0
    
    mock_ai = Mock()
    mock_ai.name = "Test"
    mock_ai.personality = "Friendly"
    mock_ai.speaking_style = "Casual"
    mock_ai.greeting = "Hello"
    
    mock_user = Mock(id=1, mbti_type="INTJ")
    mock_db = Mock(spec=Session)
    
    # 第一次查询返回conversation
    # 第二次查询返回ai assistant
    # 第三次查询返回history
    mock_history = Mock()
    mock_history.all.return_value = []
    mock_history_limit = Mock()
    mock_history_limit.limit.return_value = mock_history
    mock_history_order = Mock()
    mock_history_order.order_by.return_value = mock_history_limit
    mock_history_filter = Mock()
    mock_history_filter.filter.return_value = mock_history_order
    
    mock_ai_query = Mock()
    mock_ai_query.first.return_value = mock_ai
    mock_ai_filter = Mock()
    mock_ai_filter.filter.return_value = mock_ai_query
    
    mock_conv_query = Mock()
    mock_conv_query.first.return_value = mock_conversation
    mock_conv_filter = Mock()
    mock_conv_filter.filter.return_value = mock_conv_query
    
    def mock_query(model):
        if model.__name__ == "Conversation":
            return mock_conv_filter
        elif model.__name__ == "AiAssistant":
            return mock_ai_filter
        elif model.__name__ == "Message":
            return mock_history_filter
        return Mock()
    
    mock_db.query = mock_query
    
    with patch("app.websocket.chat.manager") as mock_manager:
        mock_manager.connect = AsyncMock()
        
        mock_content_filter = AsyncMock()
        mock_content_filter.check_text = AsyncMock(return_value=(True, None))
        
        mock_crisis_detector = AsyncMock()
        mock_crisis_detector.detect = AsyncMock(return_value=Mock(intervention_required=False))
        
        mock_retriever = AsyncMock()
        mock_retriever.retrieve_with_expand = AsyncMock(side_effect=Exception("检索失败"))
        
        mock_generator = Mock()
        mock_generator._build_system_prompt = Mock(return_value="system prompt")
        mock_generator._build_user_prompt = Mock(return_value="user prompt")
        
        # 模拟chat_stream
        async def mock_stream(messages, **kwargs):
            yield "Hello"
            yield " World"
        
        # 模拟历史查询返回空列表
        mock_history_query2 = Mock()
        mock_history_query2.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
        
        with patch("app.websocket.chat.get_content_filter", return_value=mock_content_filter):
            with patch("app.websocket.chat.get_crisis_detector", return_value=mock_crisis_detector):
                with patch("app.websocket.chat.get_retriever", return_value=mock_retriever):
                    with patch("app.websocket.chat.get_generator", return_value=mock_generator):
                        with patch("app.websocket.chat.chat_stream", new=mock_stream):
                            mock_ws.receive_text = AsyncMock(side_effect=[
                                json.dumps({"content": "测试消息"}),
                                WebSocketDisconnect()
                            ])
                            
                            # 不应该抛出异常，检索失败后使用空文档继续
                            try:
                                await handle_websocket_chat(mock_ws, mock_user, mock_db)
                            except WebSocketDisconnect:
                                pass
                            
                            # 验证仍然发送了内容
                            content_chunks = []
                            for call in mock_ws.send_text.await_args_list:
                                msg = json.loads(call[0][0])
                                if msg.get("type") == "content":
                                    content_chunks.append(msg.get("content"))
                            
                            assert "Hello" in content_chunks
                            assert " World" in content_chunks


@pytest.mark.asyncio
async def test_handle_websocket_chat_create_conversation_success():
    """测试创建新对话成功"""
    mock_ws = AsyncMock(spec=WebSocket)
    mock_ws.query_params.get.side_effect = lambda key: {
        "session_id": None,
        "assistant_id": "1"
    }.get(key)
    
    mock_user = Mock(id=1)
    mock_db = Mock(spec=Session)
    
    # 对话不存在
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    mock_conversation = Mock(
        session_id="new-session-id",
        id=123,
        assistant_id=1
    )
    
    mock_chat_service = AsyncMock()
    mock_chat_service.create_conversation = AsyncMock(return_value=mock_conversation)
    
    # 模拟历史查询返回空列表
    mock_history_query = Mock()
    mock_history_query.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
    
    def mock_query(model):
        if model.__name__ == "AiAssistant":
            return mock_history_query
        elif model.__name__ == "Message":
            return mock_history_query
        return mock_db.query.return_value
    
    mock_db.query = mock_query
    
    with patch("app.services.chat_service.get_chat_service", return_value=mock_chat_service):
        with patch("app.websocket.chat.manager") as mock_manager:
            mock_manager.connect = AsyncMock()
            
            await handle_websocket_chat(mock_ws, mock_user, mock_db)
            
            # 验证发送对话创建消息
            created_sent = False
            for call in mock_ws.send_text.await_args_list:
                msg = json.loads(call[0][0])
                if msg.get("type") == "conversation_created":
                    assert msg.get("session_id") == "new-session-id"
                    assert msg.get("conversation_id") == 123
                    created_sent = True
                    break
            assert created_sent
            mock_manager.disconnect.assert_called_once_with(1, None)


@pytest.mark.asyncio
async def test_global_manager_exists():
    """测试全局管理器存在"""
    assert global_manager is not None
    assert isinstance(global_manager, ConnectionManager)
