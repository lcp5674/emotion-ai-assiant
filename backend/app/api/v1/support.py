"""
客服系统API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from app.core.database import get_db
from app.models.support import SupportTicket, TicketMessage, ChatbotConversation, ChatbotMessage, TicketStatus
from app.schemas.support import (
    SupportTicketCreate, SupportTicketResponse, SupportTicketUpdate,
    TicketMessageCreate, TicketMessageResponse,
    ChatbotMessageCreate, ChatbotMessageResponse,
    ChatbotConversationResponse
)
from app.api.deps import get_current_user, get_current_admin
from app.models.user import User
from app.services.chatbot_service import ChatbotService
from app.services.ticket_service import TicketService

router = APIRouter()


@router.post("/tickets", response_model=SupportTicketResponse, summary="创建工单")
def create_support_ticket(
    ticket: SupportTicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建工单"""
    db_ticket = TicketService.create_ticket(
        db=db,
        user_id=current_user.id,
        title=ticket.title,
        description=ticket.description,
        category=ticket.category,
        attachment_url=ticket.attachment_url,
        priority=ticket.priority
    )
    return db_ticket


@router.get("/tickets", response_model=List[SupportTicketResponse], summary="获取工单列表")
def get_support_tickets(
    status: Optional[str] = Query(None, description="工单状态"),
    priority: Optional[str] = Query(None, description="工单优先级"),
    category: Optional[str] = Query(None, description="工单类别"),
    limit: int = Query(100, ge=1, le=1000, description="限制数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取工单列表"""
    if current_user.is_admin:
        # 管理员可以查看所有工单
        tickets = TicketService.get_all_tickets(
            db=db,
            status=status,
            priority=priority,
            category=category,
            limit=limit
        )
    else:
        # 普通用户只能查看自己的工单
        tickets = TicketService.get_user_tickets(
            db=db,
            user_id=current_user.id,
            status=status,
            priority=priority,
            category=category,
            limit=limit
        )
    return tickets


@router.get("/tickets/{ticket_id}", response_model=SupportTicketResponse, summary="获取工单详情")
def get_support_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取工单详情"""
    ticket = TicketService.get_ticket(
        db=db,
        ticket_id=ticket_id,
        user_id=current_user.id,
        is_admin=current_user.is_admin
    )
    if not ticket:
        raise HTTPException(status_code=404, detail="工单不存在")
    
    return ticket


@router.put("/tickets/{ticket_id}", response_model=SupportTicketResponse, summary="更新工单")
def update_support_ticket(
    ticket_id: int,
    ticket_update: SupportTicketUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新工单"""
    ticket = TicketService.update_ticket(
        db=db,
        ticket_id=ticket_id,
        user_id=current_user.id,
        is_admin=current_user.is_admin,
        title=ticket_update.title,
        description=ticket_update.description,
        status=ticket_update.status,
        priority=ticket_update.priority,
        assigned_to=ticket_update.assigned_to,
        category=ticket_update.category,
        attachment_url=ticket_update.attachment_url
    )
    
    if not ticket:
        raise HTTPException(status_code=404, detail="工单不存在")
    
    return ticket


@router.post("/tickets/{ticket_id}/messages", response_model=TicketMessageResponse, summary="添加工单消息")
def create_ticket_message(
    ticket_id: int,
    message: TicketMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """添加工单消息"""
    sender_type = "admin" if current_user.is_admin else "user"
    
    db_message = TicketService.add_ticket_message(
        db=db,
        ticket_id=ticket_id,
        sender_id=current_user.id,
        sender_type=sender_type,
        content=message.content,
        attachment_url=message.attachment_url
    )
    
    if not db_message:
        raise HTTPException(status_code=404, detail="工单不存在")
    
    return db_message


@router.get("/tickets/{ticket_id}/messages", response_model=List[TicketMessageResponse], summary="获取工单消息")
def get_ticket_messages(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取工单消息"""
    messages = TicketService.get_ticket_messages(
        db=db,
        ticket_id=ticket_id,
        user_id=current_user.id,
        is_admin=current_user.is_admin
    )
    
    if not messages:
        # 检查工单是否存在
        ticket = TicketService.get_ticket(
            db=db,
            ticket_id=ticket_id,
            user_id=current_user.id,
            is_admin=current_user.is_admin
        )
        if not ticket:
            raise HTTPException(status_code=404, detail="工单不存在")
    
    return messages


@router.post("/chatbot/conversations", response_model=ChatbotConversationResponse, summary="创建智能客服对话")
def create_chatbot_conversation(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建智能客服对话"""
    conversation = ChatbotService.create_conversation(
        db=db,
        user_id=current_user.id
    )
    return conversation


@router.post("/chatbot/conversations/{conversation_id}/messages", response_model=ChatbotMessageResponse, summary="发送智能客服消息")
async def send_chatbot_message(
    conversation_id: int,
    message: ChatbotMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """发送智能客服消息"""
    try:
        result = await ChatbotService.send_message(
            db=db,
            conversation_id=conversation_id,
            user_id=current_user.id,
            content=message.content,
            message_type=message.message_type
        )
        return result["bot_message"]
    except ValueError as e:
        if "对话不存在" in str(e):
            raise HTTPException(status_code=404, detail="对话不存在")
        elif "对话已结束" in str(e):
            raise HTTPException(status_code=400, detail="对话已结束")
        else:
            raise HTTPException(status_code=403, detail="无权操作此对话")
    except Exception as e:
        raise HTTPException(status_code=500, detail="发送消息失败")


@router.get("/chatbot/conversations", response_model=List[ChatbotConversationResponse], summary="获取智能客服对话列表")
def get_chatbot_conversations(
    limit: int = Query(100, ge=1, le=1000, description="限制数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取智能客服对话列表"""
    conversations = ChatbotService.get_user_conversations(
        db=db,
        user_id=current_user.id,
        limit=limit
    )
    
    return conversations


@router.get("/chatbot/conversations/{conversation_id}/messages", response_model=List[ChatbotMessageResponse], summary="获取智能客服对话消息")
def get_chatbot_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取智能客服对话消息"""
    try:
        messages = ChatbotService.get_conversation_messages(
            db=db,
            conversation_id=conversation_id,
            user_id=current_user.id
        )
        return messages
    except ValueError as e:
        if "对话不存在" in str(e):
            raise HTTPException(status_code=404, detail="对话不存在")
        else:
            raise HTTPException(status_code=403, detail="无权查看此对话")
    except Exception as e:
        raise HTTPException(status_code=500, detail="获取消息失败")


@router.put("/chatbot/conversations/{conversation_id}/end", response_model=ChatbotConversationResponse, summary="结束智能客服对话")
def end_chatbot_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """结束智能客服对话"""
    conversation = ChatbotService.end_conversation(
        db=db,
        conversation_id=conversation_id,
        user_id=current_user.id
    )
    
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    return conversation


@router.get("/tickets/stats", response_model=Dict[str, Any], summary="获取工单统计数据")
def get_ticket_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """获取工单统计数据（仅管理员）"""
    stats = TicketService.get_ticket_stats(db=db)
    return stats
