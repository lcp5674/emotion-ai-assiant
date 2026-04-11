"""
WebSocket聊天服务单元测试
"""
import pytest
import json
from unittest.mock import Mock, MagicMock, patch, AsyncMock
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


@pytest.mark.asyncio
async def test_global_manager_exists():
    """测试全局管理器存在"""
    assert global_manager is not None
    assert isinstance(global_manager, ConnectionManager)
