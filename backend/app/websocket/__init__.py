"""
WebSocket路由
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.orm import Session
import json
import asyncio

from app.core.database import get_db
from app.websocket.chat import handle_websocket_chat, manager
from app.services.animation_service import get_animation_service

router = APIRouter(prefix="/ws", tags=["WebSocket"])


@router.websocket("/chat")
async def websocket_chat(
    websocket: WebSocket,
    db: Session = Depends(get_db),
):
    """WebSocket实时对话端点"""
    await handle_websocket_chat(websocket, db=db)


@router.websocket("/connect")
async def websocket_connect(websocket: WebSocket):
    """简单的WebSocket连接测试"""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        pass


@router.websocket("/avatar/{assistant_id}")
async def websocket_avatar(
    websocket: WebSocket,
    assistant_id: int,
    token: str = Query(...),
):
    """WebSocket虚拟形象动画端点"""
    from app.core.security import decode_token
    from app.models import User

    # 验证token
    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub"))
    except Exception:
        await websocket.close(code=4001, reason="无效的认证令牌")
        return

    # 获取用户
    db = next(get_db())
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        await websocket.close(code=4001, reason="用户不存在")
        return

    await websocket.accept()

    # 加入avatar房间
    room_key = f"avatar_{user_id}_{assistant_id}"
    if not hasattr(manager, 'avatar_connections'):
        manager.avatar_connections = {}

    manager.avatar_connections[room_key] = websocket

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            msg_type = message.get("type")

            if msg_type == "animate":
                # 获取动画指令
                emotion = message.get("emotion")
                message_text = message.get("message")
                response_text = message.get("response")

                service = get_animation_service()
                animation = service.get_animation(
                    emotion=emotion,
                    message=message_text,
                    response=response_text,
                    assistant_id=assistant_id,
                )

                await websocket.send_text(json.dumps({
                    "type": "animation",
                    "data": animation,
                }))

            elif msg_type == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))

    except WebSocketDisconnect:
        if room_key in getattr(manager, 'avatar_connections', {}):
            del manager.avatar_connections[room_key]
    except Exception as e:
        if room_key in getattr(manager, 'avatar_connections', {}):
            del manager.avatar_connections[room_key]
