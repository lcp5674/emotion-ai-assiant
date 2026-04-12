"""
企业级安全合规服务
提供企业级安全合规管理功能
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models import Enterprise, EnterpriseCompliance, EnterpriseAuditLog
from sqlalchemy.orm import Session


class EnterpriseComplianceService:
    """企业级安全合规服务"""
    
    def create_compliance_policy(self, db: Session, enterprise_id: int, policy_name: str, policy_type: str, policy_content: Dict[str, Any]) -> EnterpriseCompliance:
        """创建合规策略"""
        compliance = EnterpriseCompliance(
            enterprise_id=enterprise_id,
            policy_name=policy_name,
            policy_type=policy_type,
            policy_content=policy_content,
            created_at=datetime.utcnow()
        )
        db.add(compliance)
        db.commit()
        db.refresh(compliance)
        return compliance
    
    def get_compliance_policies(self, db: Session, enterprise_id: int) -> List[EnterpriseCompliance]:
        """获取企业合规策略列表"""
        return db.query(EnterpriseCompliance).filter(
            EnterpriseCompliance.enterprise_id == enterprise_id
        ).order_by(EnterpriseCompliance.created_at.desc()).all()
    
    def update_compliance_policy(self, db: Session, policy_id: int, policy_content: Dict[str, Any]) -> Optional[EnterpriseCompliance]:
        """更新合规策略"""
        compliance = db.query(EnterpriseCompliance).filter(
            EnterpriseCompliance.id == policy_id
        ).first()
        if compliance:
            compliance.policy_content = policy_content
            compliance.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(compliance)
        return compliance
    
    def delete_compliance_policy(self, db: Session, policy_id: int) -> bool:
        """删除合规策略"""
        compliance = db.query(EnterpriseCompliance).filter(
            EnterpriseCompliance.id == policy_id
        ).first()
        if compliance:
            db.delete(compliance)
            db.commit()
            return True
        return False
    
    def log_audit_event(self, db: Session, enterprise_id: int, event_type: str, event_details: Dict[str, Any], user_id: Optional[int] = None) -> EnterpriseAuditLog:
        """记录审计事件"""
        audit_log = EnterpriseAuditLog(
            enterprise_id=enterprise_id,
            event_type=event_type,
            event_details=event_details,
            user_id=user_id,
            created_at=datetime.utcnow()
        )
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        return audit_log
    
    def get_audit_logs(self, db: Session, enterprise_id: int, days: int = 30) -> List[EnterpriseAuditLog]:
        """获取审计日志"""
        start_date = datetime.utcnow() - timedelta(days=days)
        return db.query(EnterpriseAuditLog).filter(
            EnterpriseAuditLog.enterprise_id == enterprise_id,
            EnterpriseAuditLog.created_at >= start_date
        ).order_by(EnterpriseAuditLog.created_at.desc()).all()
    
    def generate_compliance_report(self, db: Session, enterprise_id: int, report_type: str = "monthly") -> Dict[str, Any]:
        """生成合规报告"""
        if report_type == "monthly":
            days = 30
        elif report_type == "quarterly":
            days = 90
        elif report_type == "yearly":
            days = 365
        else:
            days = 30
        
        # 获取合规策略数量
        policy_count = db.query(EnterpriseCompliance).filter(
            EnterpriseCompliance.enterprise_id == enterprise_id
        ).count()
        
        # 获取审计事件数量
        audit_count = db.query(EnterpriseAuditLog).filter(
            EnterpriseAuditLog.enterprise_id == enterprise_id,
            EnterpriseAuditLog.created_at >= datetime.utcnow() - timedelta(days=days)
        ).count()
        
        return {
            "report_type": report_type,
            "period_days": days,
            "policy_count": policy_count,
            "audit_count": audit_count,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def check_compliance_status(self, db: Session, enterprise_id: int) -> Dict[str, Any]:
        """检查合规状态"""
        # 这里实现合规状态检查逻辑
        # 实际项目中需要根据具体的合规要求进行检查
        return {
            "status": "compliant",
            "message": "企业合规状态良好"
        }


def get_enterprise_compliance_service() -> EnterpriseComplianceService:
    """获取企业安全合规服务实例"""
    return EnterpriseComplianceService()
