"""
WebSocket路由
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.websocket.chat import handle_websocket_chat, manager

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
