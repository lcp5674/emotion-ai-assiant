"""
信任与安全服务
提供数据隐私、安全合规、心理咨询师审核等功能
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import User, Message, Conversation
from app.core.security import get_password_hash
import json


class TrustSecurityService:
    """信任与安全服务"""
    
    def __init__(self):
        self.data_retention_days = 365  # 数据保留天数
        self.auto_delete_days = 730  # 自动删除天数
    
    def get_privacy_settings(
        self,
        db: Session,
        user_id: int
    ) -> Dict[str, Any]:
        """
        获取用户隐私设置
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            
        Returns:
            隐私设置
        """
        # 这里应该从数据库获取用户隐私设置
        # 目前返回默认设置
        return {
            "user_id": user_id,
            "data_collection": {
                "chat_history": True,
                "voice_data": False,
                "location_data": False,
                "usage_statistics": True
            },
            "data_sharing": {
                "with_ai_partners": False,
                "for_research": False,
                "anonymous": True
            },
            "data_retention": {
                "chat_history_days": 365,
                "voice_data_days": 90
            },
            "security": {
                "two_factor_enabled": False,
                "login_alerts": True,
                "session_timeout": 30
            },
            "updated_at": datetime.utcnow().isoformat()
        }
    
    def update_privacy_settings(
        self,
        db: Session,
        user_id: int,
        privacy_settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        更新用户隐私设置
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            privacy_settings: 隐私设置
            
        Returns:
            更新后的隐私设置
        """
        # 这里应该保存到数据库
        # 目前返回更新后的设置
        return {
            "user_id": user_id,
            **privacy_settings,
            "updated_at": datetime.utcnow().isoformat()
        }
    
    def export_user_data(
        self,
        db: Session,
        user_id: int
    ) -> Dict[str, Any]:
        """
        导出用户数据
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            
        Returns:
            用户数据包
        """
        # 获取用户信息
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return {"success": False, "error": "用户不存在"}
        
        # 获取对话数据
        conversations = db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).all()
        
        # 获取消息数据
        messages = db.query(Message).join(
            Conversation, Message.conversation_id == Conversation.id
        ).filter(
            Conversation.user_id == user_id
        ).all()
        
        # 构建数据包
        data_package = {
            "success": True,
            "exported_at": datetime.utcnow().isoformat(),
            "user": {
                "id": user.id,
                "nickname": user.nickname,
                "mbti_type": user.mbti_type,
                "created_at": user.created_at.isoformat() if user.created_at else None
            },
            "conversations": [
                {
                    "id": conv.id,
                    "session_id": conv.session_id,
                    "title": conv.title,
                    "created_at": conv.created_at.isoformat() if conv.created_at else None,
                    "message_count": conv.message_count
                }
                for conv in conversations
            ],
            "messages": [
                {
                    "id": msg.id,
                    "conversation_id": msg.conversation_id,
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat() if msg.created_at else None
                }
                for msg in messages
            ],
            "data_summary": {
                "total_conversations": len(conversations),
                "total_messages": len(messages),
                "data_size_estimate": f"{len(json.dumps(messages, default=str)) // 1024}KB"
            }
        }
        
        return data_package
    
    def delete_user_data(
        self,
        db: Session,
        user_id: int,
        data_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        删除用户数据
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            data_types: 要删除的数据类型
            
        Returns:
            删除结果
        """
        if data_types is None:
            data_types = ["all"]
        
        deleted_counts = {}
        
        if "all" in data_types or "messages" in data_types:
            # 删除消息
            message_count = db.query(Message).join(
                Conversation, Message.conversation_id == Conversation.id
            ).filter(Conversation.user_id == user_id).delete()
            deleted_counts["messages"] = message_count
        
        if "all" in data_types or "conversations" in data_types:
            # 删除对话
            conv_count = db.query(Conversation).filter(
                Conversation.user_id == user_id
            ).delete()
            deleted_counts["conversations"] = conv_count
        
        if "all" in data_types or "account" in data_types:
            # 标记用户为已删除（软删除）
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.is_active = 0
                deleted_counts["account"] = 1
        
        db.commit()
        
        return {
            "success": True,
            "deleted_counts": deleted_counts,
            "deleted_at": datetime.utcnow().isoformat()
        }
    
    def get_data_retention_info(
        self,
        db: Session,
        user_id: int
    ) -> Dict[str, Any]:
        """
        获取数据保留信息
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            
        Returns:
            数据保留信息
        """
        # 统计用户数据
        message_count = db.query(func.count(Message.id)).join(
            Conversation, Message.conversation_id == Conversation.id
        ).filter(Conversation.user_id == user_id).scalar()
        
        conversation_count = db.query(func.count(Conversation.id)).filter(
            Conversation.user_id == user_id
        ).scalar()
        
        # 计算最早和最新数据日期
        earliest_message = db.query(Message.created_at).join(
            Conversation, Message.conversation_id == Conversation.id
        ).filter(Conversation.user_id == user_id).order_by(
            Message.created_at
        ).first()
        
        latest_message = db.query(Message.created_at).join(
            Conversation, Message.conversation_id == Conversation.id
        ).filter(Conversation.user_id == user_id).order_by(
            Message.created_at.desc()
        ).first()
        
        return {
            "user_id": user_id,
            "data_summary": {
                "total_messages": message_count or 0,
                "total_conversations": conversation_count or 0
            },
            "data_age": {
                "earliest_data": earliest_message[0].isoformat() if earliest_message else None,
                "latest_data": latest_message[0].isoformat() if latest_message else None,
                "retention_days": self.data_retention_days,
                "auto_delete_days": self.auto_delete_days
            },
            "upcoming_deletions": self._get_upcoming_deletions(db, user_id),
            "export_available": True
        }
    
    def _get_upcoming_deletions(
        self,
        db: Session,
        user_id: int
    ) -> List[Dict[str, Any]]:
        """
        获取即将删除的数据
        """
        threshold_date = datetime.utcnow() - timedelta(days=self.data_retention_days)
        
        # 获取即将过期的消息
        expiring_messages = db.query(Message.id, Message.created_at).join(
            Conversation, Message.conversation_id == Conversation.id
        ).filter(
            Conversation.user_id == user_id,
            Message.created_at < threshold_date
        ).limit(10).all()
        
        return [
            {
                "type": "message",
                "id": msg.id,
                "created_at": msg.created_at.isoformat(),
                "days_until_deletion": max(0, (threshold_date - msg.created_at).days)
            }
            for msg in expiring_messages
        ]
    
    def verify_ai_response(
        self,
        response_content: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        验证AI回复
        
        Args:
            response_content: AI回复内容
            context: 上下文
            
        Returns:
            验证结果
        """
        # 这里实现AI回复验证逻辑
        # 实际项目中可能需要心理咨询师审核机制
        
        verification_result = {
            "verified": True,
            "risk_level": "low",
            "flags": [],
            "suggestions": [],
            "verified_at": datetime.utcnow().isoformat()
        }
        
        # 检查是否有敏感内容
        sensitive_keywords = ["自杀", "自残", "暴力", "伤害"]
        for keyword in sensitive_keywords:
            if keyword in response_content:
                verification_result["risk_level"] = "high"
                verification_result["flags"].append(f"包含敏感关键词: {keyword}")
                verification_result["suggestions"].append("建议转接专业心理咨询师")
        
        return verification_result
    
    def get_security_audit_log(
        self,
        db: Session,
        user_id: int,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        获取安全审计日志
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            limit: 限制数量
            
        Returns:
            安全审计日志
        """
        # 这里应该从数据库获取安全审计日志
        # 目前返回模拟数据
        return [
            {
                "id": 1,
                "event_type": "login",
                "ip_address": "192.168.1.1",
                "user_agent": "Mozilla/5.0...",
                "location": "北京",
                "result": "success",
                "created_at": datetime.utcnow().isoformat()
            }
        ]
    
    def request_data_deletion(
        self,
        db: Session,
        user_id: int,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        申请数据删除
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            reason: 删除原因
            
        Returns:
            申请结果
        """
        # 这里应该创建删除申请记录
        return {
            "success": True,
            "request_id": f"delete_req_{user_id}_{datetime.utcnow().timestamp()}",
            "status": "pending",
            "review_deadline": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            "reason": reason
        }


def get_trust_security_service() -> TrustSecurityService:
    """获取信任与安全服务实例"""
    return TrustSecurityService()
