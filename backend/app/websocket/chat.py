"""
WebSocket实时对话服务
"""
import json
from typing import Optional, Dict, Any
from fastapi import WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
import asyncio
import loguru

from app.core.database import get_db, get_redis
from app.models import User, Conversation, Message, AiAssistant
from app.services.rag.generator import get_generator
from app.services.rag.retriever import get_retriever
from app.services.llm.factory import chat_stream
from app.services.member_service import get_member_service
from app.services.content_filter import get_content_filter
from app.services.crisis_service import get_crisis_detector
from app.services.user_memory_service import get_user_memory_service
from app.services.memory_service import get_memory_service
from app.api.deps import get_current_user_ws
from app.core.security import decode_token


class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # user_id -> WebSocket
        self.active_connections: Dict[int, WebSocket] = {}
        # session_id -> user_id
        self.session_users: Dict[str, int] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int, session_id: Optional[str] = None):
        """建立连接"""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        if session_id:
            self.session_users[session_id] = user_id
        loguru.logger.info(f"WebSocket连接建立: user_id={user_id}, session_id={session_id}")
    
    def disconnect(self, user_id: int, session_id: Optional[str] = None):
        """断开连接"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if session_id and session_id in self.session_users:
            del self.session_users[session_id]
        loguru.logger.info(f"WebSocket连接断开: user_id={user_id}")
    
    async def send_message(self, user_id: int, message: Dict[str, Any]):
        """发送消息到客户端"""
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(json.dumps(message))
    
    async def broadcast(self, message: Dict[str, Any], exclude: Optional[int] = None):
        """广播消息"""
        for user_id, websocket in self.active_connections.items():
            if user_id != exclude:
                await websocket.send_text(json.dumps(message))


# 全局连接管理器
manager = ConnectionManager()


async def get_websocket_current_user(websocket: WebSocket) -> User:
    """从WebSocket获取当前用户"""
    # 从查询参数获取token
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001, reason="未提供认证令牌")
        raise WebSocketDisconnect(code=4001)
    
    # 解析token
    payload = decode_token(token)
    if not payload:
        await websocket.close(code=4001, reason="无效的认证令牌")
        raise WebSocketDisconnect(code=4001)
    
    # 获取用户
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == payload.get("sub")).first()
        if not user:
            await websocket.close(code=4001, reason="用户不存在")
            raise WebSocketDisconnect(code=4001)
        return user
    finally:
        db.close()


async def handle_websocket_chat(
    websocket: WebSocket,
    db: Session = Depends(get_db),
):
    """处理WebSocket聊天"""
    # 获取当前用户
    current_user = await get_websocket_current_user(websocket)

    session_id = websocket.query_params.get("session_id")
    assistant_id = websocket.query_params.get("assistant_id")

    # 建立连接
    await manager.connect(websocket, current_user.id, session_id)
    
    try:
        # 如果没有session_id，创建一个新对话
        conversation = None
        if session_id:
            conversation = db.query(Conversation).filter(
                Conversation.session_id == session_id,
                Conversation.user_id == current_user.id,
            ).first()
        
        if not conversation:
            if not assistant_id:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "需要指定助手ID"
                }))
                return
            
            from app.services.chat_service import get_chat_service
            chat_svc = get_chat_service()
            conversation = await chat_svc.create_conversation(
                db=db,
                user_id=current_user.id,
                assistant_id=int(assistant_id),
            )
            # 发送对话创建成功消息
            await websocket.send_text(json.dumps({
                "type": "conversation_created",
                "session_id": conversation.session_id,
                "conversation_id": conversation.id,
            }))
        
        # 获取助手信息
        assistant_info = None
        if conversation.assistant_id:
            ai_asst = db.query(AiAssistant).filter(AiAssistant.id == conversation.assistant_id).first()
            if ai_asst:
                assistant_info = {
                    "name": ai_asst.name,
                    "personality": ai_asst.personality,
                    "speaking_style": ai_asst.speaking_style,
                    "greeting": ai_asst.greeting,
                }
        
                # 获取最近的消息历史（增加上下文窗口以保留更多对话记录）
                history = db.query(Message).filter(
                    Message.conversation_id == conversation.id,
                ).order_by(Message.created_at.desc()).limit(50).all()
                ctx = "\n".join([f"{m.role}: {m.content}" for m in reversed(history)])
        
        # 接收并处理消息
        while True:
            try:
                # 接收客户端消息
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                query = message_data.get("content", "")
                if not query:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "消息内容不能为空"
                    }))
                    continue
                
                # 内容过滤
                content_filter = get_content_filter()
                passed, _ = await content_filter.check_text(query)
                if not passed:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "内容包含不当信息，请修改后再试。"
                    }))
                    continue
                
                # 危机检测
                crisis_detector = get_crisis_detector()
                crisis_result = await crisis_detector.detect(query)
                
                if crisis_result.intervention_required:
                    intervention_response = await crisis_detector.get_intervention_response(crisis_result.level)
                    await websocket.send_text(json.dumps({
                        "type": "crisis_detected",
                        "level": crisis_result.level.value,
                        "content": intervention_response,
                    }))
                    continue
                
                # 保存用户消息
                user_message = Message(
                    conversation_id=conversation.id,
                    role="user",
                    content=query,
                    message_type="text",
                )
                db.add(user_message)
                db.commit()
                db.refresh(user_message)
                
                # 发送消息ID给客户端
                await websocket.send_text(json.dumps({
                    "type": "message_sent",
                    "message_id": user_message.id,
                }))
                
                # 获取用户MBTI
                user_mbti = current_user.mbti_type
                
                # 检索相关文档
                retriever = get_retriever()
                generator = get_generator()
                
                try:
                    docs = await retriever.retrieve_with_expand(
                        query=query,
                        user_mbti=user_mbti,
                        conversation_context=ctx,
                    )
                except Exception as e:
                    loguru.logger.warning(f"检索失败: {e}")
                    docs = []
                
                # 获取用户记忆上下文
                memory_service = get_user_memory_service()
                full_context = f"{ctx}\n{query}" if ctx else query
                memory_context = memory_service.get_formatted_memories_for_prompt(
                    db, current_user.id, full_context, limit=5
                )
                
                # 构建提示词
                system_prompt = generator._build_system_prompt(assistant_info, user_mbti)
                user_prompt = generator._build_user_prompt(query, docs)
                
                # 如果有相关记忆，添加到用户提示词中
                if memory_context:
                    user_prompt = f"{user_prompt}\n\n{memory_context}"
                
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ]
                
                # 流式生成回复
                full_content = ""
                message_id = None
                
                async for chunk in chat_stream(messages, temperature=0.8, max_tokens=1500):
                    full_content += chunk
                    await websocket.send_text(json.dumps({
                        "type": "chunk",
                        "content": chunk,
                    }))
                
                # 保存助手消息
                assistant_message = Message(
                    conversation_id=conversation.id,
                    role="assistant",
                    content=full_content,
                    message_type="text",
                )
                db.add(assistant_message)
                db.commit()
                db.refresh(assistant_message)
                message_id = assistant_message.id

                # 发送完成消息（包含完整内容）
                await websocket.send_text(json.dumps({
                    "type": "done",
                    "message_id": message_id,
                    "content": full_content,
                }))
                
                # 更新对话时间
                conversation.updated_at = __import__('datetime').datetime.now()
                conversation.message_count += 2  # 用户消息 + 助手消息
                db.commit()
                
                # 异步提取用户偏好（不阻塞响应）
                try:
                    vector_memory_service = get_memory_service()
                    asyncio.create_task(
                        vector_memory_service.extract_preference(
                            user_id=current_user.id,
                            message=query,
                            assistant_response=full_content
                        )
                    )
                except Exception as e:
                    loguru.logger.warning(f"提取用户偏好失败: {e}")
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "无效的消息格式"
                }))
            except Exception as e:
                loguru.logger.error(f"WebSocket错误: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": f"服务器错误: {str(e)}"
                }))
    
    finally:
        manager.disconnect(current_user.id, session_id)
