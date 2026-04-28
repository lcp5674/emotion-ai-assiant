"""
对话接口
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db, get_redis
from app.models import User, Conversation, Message, AiAssistant
from app.schemas.chat import (
    ChatSendRequest,
    ConversationListResponse,
    MessageListResponse,
    ConversationCreateRequest,
    ConversationTitleUpdate,
    MessageCollectRequest,
)
from app.services.chat_service import get_chat_service
from app.services.stream_service import get_stream_service
from app.services.member_service import get_member_service
from app.services.content_filter import get_content_filter
from app.services.crisis_service import get_crisis_detector, CrisisLevel
from app.api.deps import get_current_user
from app.core.i18n import _

router = APIRouter(prefix="/chat", tags=["对话"])


@router.post("/send", summary="发送消息")
async def send_message(
    request: ChatSendRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 危机检测
    crisis_detector = get_crisis_detector()
    crisis_result = await crisis_detector.detect(request.content)

    if crisis_result.intervention_required:
        intervention_response = await crisis_detector.get_intervention_response(crisis_result.level)
        return {
            "session_id": request.session_id,
            "conversation_id": None,
            "user_message": None,
            "assistant_message": {
                "id": None,
                "role": "assistant",
                "content": intervention_response,
                "created_at": None,
            },
            "crisis_detected": True,
            "crisis_level": crisis_result.level.value,
        }

    chat_service = get_chat_service()

    try:
        result = await chat_service.send_message(
            db=db,
            user_id=current_user.id,
            session_id=request.session_id,
            assistant_id=request.assistant_id,
            content=request.content,
        )

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/stream", summary="流式发送消息")
async def stream_message(
    request: ChatSendRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    member_level = current_user.member_level.value if hasattr(current_user.member_level, 'value') else current_user.member_level
    redis_client = await get_redis()
    member_svc = get_member_service()
    allowed, msg, _ = await member_svc.check_message_limit(
        current_user.id, member_level, current_user.member_expire_at, redis_client
    )
    if not allowed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

    content_filter = get_content_filter()
    passed, _ = await content_filter.check_text(request.content)
    if not passed:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=_("内容包含不当信息，请修改后再试。"),
            )

    conversation = None
    if request.session_id:
        conversation = db.query(Conversation).filter(
            Conversation.session_id == request.session_id,
            Conversation.user_id == current_user.id,
        ).first()

    if not conversation:
        if not request.assistant_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=_("需要指定助手ID"))
        chat_svc = get_chat_service()
        conversation = await chat_svc.create_conversation(
            db=db, user_id=current_user.id, assistant_id=request.assistant_id
        )

    ai_asst = db.query(AiAssistant).filter(AiAssistant.id == conversation.assistant_id).first() if conversation.assistant_id else None
    assistant_info = None
    if ai_asst:
        assistant_info = {
            "name": ai_asst.name,
            "personality": ai_asst.personality,
            "speaking_style": ai_asst.speaking_style,
            "greeting": ai_asst.greeting,
        }

    user_mbti = current_user.mbti_type

    history = db.query(Message).filter(
        Message.conversation_id == conversation.id,
    ).order_by(Message.created_at.desc()).limit(50).all()
    ctx = "\n".join([f"{m.role}: {m.content}" for m in reversed(history)])

    stream_svc = get_stream_service()

    async def event_generator():
        if member_level == "free":
            await member_svc.increment_message_count(current_user.id, redis_client)
        async for chunk in stream_svc.stream_generate(
            query=request.content,
            user_mbti=user_mbti,
            conversation_context=ctx,
            assistant_info=assistant_info,
        ):
            yield chunk

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "X-Accel-Buffering": "no",
            "Cache-Control": "no-cache",
        },
    )


@router.post("/create", summary="创建对话")
async def create_conversation(
    request: ConversationCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建新对话"""
    chat_service = get_chat_service()

    conversation = await chat_service.create_conversation(
        db=db,
        user_id=current_user.id,
        assistant_id=request.assistant_id,
        title=request.title,
    )

    return {
        "session_id": conversation.session_id,
        "conversation_id": conversation.id,
        "title": conversation.title,
    }


@router.get("/conversations", summary="获取对话列表")
async def get_conversations(
    limit: int = Query(default=20, le=50),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取用户的对话列表"""
    chat_service = get_chat_service()
    conversations = chat_service.get_conversations(db, current_user.id, limit, offset)

    return ConversationListResponse(
        total=len(conversations),
        list=[
            {
                "id": c.id,
                "session_id": c.session_id,
                "title": c.title,
                "assistant_id": c.assistant_id,
                "assistant_name": c.assistant.name if c.assistant else None,
                "message_count": c.message_count,
                "status": c.status.value if hasattr(c.status, 'value') else c.status,
                "created_at": c.created_at,
                "updated_at": c.updated_at,
            }
            for c in conversations
        ],
    )


@router.get("/history/{session_id}", summary="获取对话历史")
async def get_conversation_history(
    session_id: str,
    limit: int = Query(default=50, le=100),
    before_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    ):
    chat_service = get_chat_service()

    conversation = chat_service.get_conversation(db, current_user.id, session_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_("对话不存在"),
        )

    messages = chat_service.get_messages(db, conversation.id, limit, before_id)

    return MessageListResponse(
        total=len(messages),
        list=[
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "message_type": m.message_type.value if hasattr(m.message_type, 'value') else m.message_type,
                "emotion": m.emotion,
                "sentiment_score": m.sentiment_score,
                "is_collected": m.is_collected,
                "created_at": m.created_at,
            }
            for m in messages
        ],
    )


@router.post("/collect", summary="收藏消息")
async def collect_message(
    request: MessageCollectRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """收藏/取消收藏消息"""
    chat_service = get_chat_service()
    is_collected = chat_service.collect_message(db, current_user.id, request.message_id)

    return {"is_collected": is_collected}


@router.post("/close/{session_id}", summary="关闭对话")
async def close_conversation(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """关闭对话"""
    chat_service = get_chat_service()
    success = chat_service.close_conversation(db, current_user.id, session_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_("对话不存在"),
        )

    return {"message": "对话已关闭"}


@router.delete("/conversations/{session_id}", summary="删除对话")
async def delete_conversation(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除对话及其所有消息"""
    chat_service = get_chat_service()
    success = chat_service.delete_conversation(db, current_user.id, session_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_("对话不存在"),
        )

    return {"message": "对话已删除"}


@router.put("/title/{session_id}", summary="更新对话标题")
async def update_conversation_title(
    session_id: str,
    request: ConversationTitleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversation = db.query(Conversation).filter(
        Conversation.session_id == session_id,
        Conversation.user_id == current_user.id,
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_("对话不存在"),
        )

    conversation.title = request.title
    db.commit()

    return {"title": conversation.title}


@router.delete("/message/{message_id}", summary="撤回消息")
async def delete_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    撤回最后一条消息
    - 只能撤回对话中最后一条消息
    - 只能撤回用户自己发送的消息
    """
    # 查找消息
    message = db.query(Message).filter(
        Message.id == message_id,
    ).first()

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_("消息不存在"),
        )

    # 验证对话属于当前用户
    conversation = db.query(Conversation).filter(
        Conversation.id == message.conversation_id,
        Conversation.user_id == current_user.id,
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=_("你没有权限操作此消息"),
        )

    # 检查是否是最后一条消息
    last_message = db.query(Message).filter(
        Message.conversation_id == conversation.id
    ).order_by(Message.id.desc()).first()

    if not last_message or last_message.id != message_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_("只能撤回对话中的最后一条消息"),
        )

    # 删除消息
    db.delete(message)
    # 更新对话消息计数
    conversation.message_count = max(0, conversation.message_count - 1)
    db.commit()

    return {
        "message": _("消息已撤回"),
        "conversation_id": conversation.id,
        "message_count": conversation.message_count,
    }


@router.post("/regenerate/{conversation_id}", summary="重新生成回复")
async def regenerate_response(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    重新生成AI最后一次回复
    - 删除最后一条AI回复，重新生成
    """
    # 验证对话属于当前用户
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id,
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_("对话不存在"),
        )

    # 找到最后一条AI回复
    last_assistant_message = db.query(Message).filter(
        Message.conversation_id == conversation.id,
        Message.role == "assistant",
    ).order_by(Message.id.desc()).first()

    if not last_assistant_message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_("没有可重新生成的AI回复"),
        )

    # 找到对应用户消息
    previous_user_message = db.query(Message).filter(
        Message.conversation_id == conversation.id,
        Message.role == "user",
        Message.id < last_assistant_message.id
    ).order_by(Message.id.desc()).first()

    if not previous_user_message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_("找不到对应的用户消息"),
        )

    # 删除旧的AI回复
    db.delete(last_assistant_message)
    conversation.message_count = max(0, conversation.message_count - 1)
    db.commit()

    # 获取助手信息
    ai_asst = db.query(AiAssistant).filter(AiAssistant.id == conversation.assistant_id).first() if conversation.assistant_id else None
    assistant_info = None
    if ai_asst:
        assistant_info = {
            "name": ai_asst.name,
            "personality": ai_asst.personality,
            "speaking_style": ai_asst.speaking_style,
            "greeting": ai_asst.greeting,
        }

    user_mbti = current_user.mbti_type

    # 获取历史上下文（排除刚删除的AI回复）
    history = db.query(Message).filter(
        Message.conversation_id == conversation.id,
    ).order_by(Message.created_at.desc()).limit(50).all()
    ctx = "\n".join([f"{m.role}: {m.content}" for m in reversed(history)])

    from app.services.stream_service import get_stream_service
    from fastapi.responses import StreamingResponse
    from app.services.member_service import get_member_service
    from app.core.database import get_redis
    import asyncio

    # 检查消息限额
    redis_client = await get_redis()
    member_svc = get_member_service()
    member_level = current_user.member_level.value if hasattr(current_user.member_level, 'value') else current_user.member_level
    allowed, msg, _ = await member_svc.check_message_limit(
        current_user.id, member_level, current_user.member_expire_at, redis_client
    )
    if not allowed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

    stream_svc = get_stream_service()

    async def event_generator():
        if member_level == "free":
            await member_svc.increment_message_count(current_user.id, redis_client)
        async for chunk in stream_svc.stream_generate(
            query=previous_user_message.content,
            user_mbti=user_mbti,
            conversation_context=ctx,
            assistant_info=assistant_info,
        ):
            yield chunk

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "X-Accel-Buffering": "no",
            "Cache-Control": "no-cache",
        },
    )