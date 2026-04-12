"""
企业级数据模型schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.models.enterprise import EnterpriseStatus, EnterpriseUserRole


class EnterpriseBase(BaseModel):
    """企业基础模型"""
    name: str = Field(..., description="企业名称")
    domain: str = Field(..., description="企业域名")


class EnterpriseCreate(EnterpriseBase):
    """创建企业请求模型"""
    pass


class EnterpriseResponse(EnterpriseBase):
    """企业响应模型"""
    id: int
    admin_user_id: int
    status: EnterpriseStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class EnterpriseUserBase(BaseModel):
    """企业用户基础模型"""
    enterprise_id: int
    user_id: int
    role: EnterpriseUserRole = EnterpriseUserRole.MEMBER


class EnterpriseUserCreate(EnterpriseUserBase):
    """创建企业用户请求模型"""
    pass


class EnterpriseUserResponse(EnterpriseUserBase):
    """企业用户响应模型"""
    id: int
    joined_at: datetime
    
    class Config:
        from_attributes = True


class EnterpriseComplianceBase(BaseModel):
    """企业合规策略基础模型"""
    enterprise_id: int
    policy_name: str
    policy_type: str
    policy_content: Dict[str, Any]


class EnterpriseComplianceCreate(EnterpriseComplianceBase):
    """创建企业合规策略请求模型"""
    pass


class EnterpriseComplianceResponse(EnterpriseComplianceBase):
    """企业合规策略响应模型"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class EnterpriseReportResponse(BaseModel):
    """企业报表响应模型"""
    report_type: str
    period_days: int
    summary: Dict[str, Any]
    user_activity: List[Dict[str, Any]]
    usage_metrics: Dict[str, Any]
    generated_at: str


class EnterpriseWebhookBase(BaseModel):
    """企业webhook基础模型"""
    enterprise_id: int
    url: str
    events: List[str]


class EnterpriseWebhookCreate(EnterpriseWebhookBase):
    """创建企业webhook请求模型"""
    pass


class EnterpriseWebhookResponse(BaseModel):
    """企业webhook响应模型"""
    webhook_id: str
    url: str
    events: List[str]
