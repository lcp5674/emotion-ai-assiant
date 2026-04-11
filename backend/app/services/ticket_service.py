"""
工单服务
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.models.support import SupportTicket, TicketMessage, TicketStatus
from app.models.user import User


class TicketService:
    """工单服务"""

    @staticmethod
    def create_ticket(
        db: Session,
        user_id: int,
        title: str,
        description: str,
        category: Optional[str] = None,
        attachment_url: Optional[str] = None,
        priority: str = "medium"
    ) -> SupportTicket:
        """创建工单"""
        ticket = SupportTicket(
            user_id=user_id,
            title=title,
            description=description,
            category=category,
            attachment_url=attachment_url,
            priority=priority
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        return ticket

    @staticmethod
    def get_ticket(db: Session, ticket_id: int, user_id: int, is_admin: bool = False) -> Optional[SupportTicket]:
        """获取工单"""
        query = db.query(SupportTicket).filter(SupportTicket.id == ticket_id)
        
        # 非管理员只能查看自己的工单
        if not is_admin:
            query = query.filter(SupportTicket.user_id == user_id)
        
        return query.first()

    @staticmethod
    def get_user_tickets(
        db: Session,
        user_id: int,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 100
    ) -> List[SupportTicket]:
        """获取用户的工单列表"""
        query = db.query(SupportTicket).filter(SupportTicket.user_id == user_id)
        
        if status:
            query = query.filter(SupportTicket.status == status)
        if priority:
            query = query.filter(SupportTicket.priority == priority)
        if category:
            query = query.filter(SupportTicket.category == category)
        
        return query.order_by(SupportTicket.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_all_tickets(
        db: Session,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 100
    ) -> List[SupportTicket]:
        """获取所有工单（仅管理员）"""
        query = db.query(SupportTicket)
        
        if status:
            query = query.filter(SupportTicket.status == status)
        if priority:
            query = query.filter(SupportTicket.priority == priority)
        if category:
            query = query.filter(SupportTicket.category == category)
        
        return query.order_by(SupportTicket.created_at.desc()).limit(limit).all()

    @staticmethod
    def update_ticket(
        db: Session,
        ticket_id: int,
        user_id: int,
        is_admin: bool = False,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[TicketStatus] = None,
        priority: Optional[str] = None,
        assigned_to: Optional[int] = None,
        category: Optional[str] = None,
        attachment_url: Optional[str] = None
    ) -> Optional[SupportTicket]:
        """更新工单"""
        ticket = TicketService.get_ticket(db, ticket_id, user_id, is_admin)
        if not ticket:
            return None
        
        # 非管理员只能更新部分字段
        if not is_admin:
            allowed_fields = ["title", "description", "attachment_url"]
            update_data = {}
            if title:
                update_data["title"] = title
            if description:
                update_data["description"] = description
            if attachment_url:
                update_data["attachment_url"] = attachment_url
        else:
            # 管理员可以更新所有字段
            update_data = {}
            if title:
                update_data["title"] = title
            if description:
                update_data["description"] = description
            if status:
                update_data["status"] = status
                # 如果状态更新为已解决，记录解决时间
                if status == TicketStatus.RESOLVED:
                    update_data["resolved_at"] = datetime.now()
            if priority:
                update_data["priority"] = priority
            if assigned_to:
                update_data["assigned_to"] = assigned_to
            if category:
                update_data["category"] = category
            if attachment_url:
                update_data["attachment_url"] = attachment_url
        
        for field, value in update_data.items():
            setattr(ticket, field, value)
        
        db.commit()
        db.refresh(ticket)
        return ticket

    @staticmethod
    def add_ticket_message(
        db: Session,
        ticket_id: int,
        sender_id: int,
        sender_type: str,
        content: str,
        attachment_url: Optional[str] = None
    ) -> Optional[TicketMessage]:
        """添加工单消息"""
        # 验证工单是否存在
        ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
        if not ticket:
            return None
        
        message = TicketMessage(
            ticket_id=ticket_id,
            sender_id=sender_id,
            sender_type=sender_type,
            content=content,
            attachment_url=attachment_url
        )
        db.add(message)
        
        # 如果是管理员回复，自动将工单状态设置为处理中
        if sender_type == "admin" and ticket.status == TicketStatus.PENDING:
            ticket.status = TicketStatus.PROCESSING
        
        db.commit()
        db.refresh(message)
        return message

    @staticmethod
    def get_ticket_messages(
        db: Session,
        ticket_id: int,
        user_id: int,
        is_admin: bool = False
    ) -> List[TicketMessage]:
        """获取工单消息"""
        # 验证工单是否存在且用户有权限
        ticket = TicketService.get_ticket(db, ticket_id, user_id, is_admin)
        if not ticket:
            return []
        
        return db.query(TicketMessage).filter(
            TicketMessage.ticket_id == ticket_id
        ).order_by(TicketMessage.created_at).all()

    @staticmethod
    def get_ticket_stats(db: Session) -> Dict[str, Any]:
        """获取工单统计数据"""
        # 统计不同状态的工单数量
        status_stats = db.query(
            SupportTicket.status,
            func.count(SupportTicket.id).label('count')
        ).group_by(SupportTicket.status).all()
        
        # 统计不同优先级的工单数量
        priority_stats = db.query(
            SupportTicket.priority,
            func.count(SupportTicket.id).label('count')
        ).group_by(SupportTicket.priority).all()
        
        # 统计不同类别的工单数量
        category_stats = db.query(
            SupportTicket.category,
            func.count(SupportTicket.id).label('count')
        ).filter(SupportTicket.category.isnot(None)).group_by(SupportTicket.category).all()
        
        return {
            "status_stats": [
                {"status": stat.status.value, "count": stat.count}
                for stat in status_stats
            ],
            "priority_stats": [
                {"priority": stat.priority.value, "count": stat.count}
                for stat in priority_stats
            ],
            "category_stats": [
                {"category": stat.category, "count": stat.count}
                for stat in category_stats
            ]
        }
