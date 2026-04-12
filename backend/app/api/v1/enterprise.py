"""
企业级API端点
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.core.database import get_db
from app.models import User, Enterprise, EnterpriseUser, EnterpriseCompliance, EnterpriseAuditLog
from app.schemas.enterprise import (
    EnterpriseCreate,
    EnterpriseResponse,
    EnterpriseUserCreate,
    EnterpriseUserResponse,
    EnterpriseComplianceCreate,
    EnterpriseComplianceResponse,
    EnterpriseReportResponse,
    EnterpriseWebhookCreate,
    EnterpriseWebhookResponse,
)
from app.services.enterprise import (
    get_enterprise_auth_service,
    get_enterprise_analytics_service,
    get_enterprise_api_integration_service,
    get_enterprise_compliance_service,
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/enterprise", tags=["企业管理"])


@router.post("/create", summary="创建企业", response_model=EnterpriseResponse)
async def create_enterprise(
    request: EnterpriseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建新企业"""
    auth_service = get_enterprise_auth_service()
    enterprise = auth_service.create_enterprise(
        db=db,
        name=request.name,
        domain=request.domain,
        admin_user_id=current_user.id
    )
    return enterprise


@router.get("/list", summary="获取企业列表", response_model=List[EnterpriseResponse])
async def get_enterprises(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取用户所属的企业列表"""
    enterprises = db.query(Enterprise).join(
        EnterpriseUser
    ).filter(
        EnterpriseUser.user_id == current_user.id
    ).all()
    return enterprises


@router.post("/add-user", summary="添加企业用户", response_model=EnterpriseUserResponse)
async def add_enterprise_user(
    request: EnterpriseUserCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """添加用户到企业"""
    # 验证当前用户是否是企业管理员
    enterprise_user = db.query(EnterpriseUser).filter(
        EnterpriseUser.enterprise_id == request.enterprise_id,
        EnterpriseUser.user_id == current_user.id,
        EnterpriseUser.role == "admin"
    ).first()
    
    if not enterprise_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有企业管理员可以添加用户"
        )
    
    auth_service = get_enterprise_auth_service()
    enterprise_user = auth_service.add_enterprise_user(
        db=db,
        enterprise_id=request.enterprise_id,
        user_id=request.user_id,
        role=request.role
    )
    return enterprise_user


@router.get("/analytics/summary/{enterprise_id}", summary="获取企业概览")
async def get_enterprise_summary(
    enterprise_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取企业概览数据"""
    # 验证用户是否属于企业
    enterprise_user = db.query(EnterpriseUser).filter(
        EnterpriseUser.enterprise_id == enterprise_id,
        EnterpriseUser.user_id == current_user.id
    ).first()
    
    if not enterprise_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="你不属于该企业"
        )
    
    analytics_service = get_enterprise_analytics_service()
    summary = analytics_service.get_enterprise_summary(db, enterprise_id)
    return summary


@router.get("/analytics/activity/{enterprise_id}", summary="获取用户活动数据")
async def get_user_activity(
    enterprise_id: int,
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取用户活动数据"""
    # 验证用户是否属于企业
    enterprise_user = db.query(EnterpriseUser).filter(
        EnterpriseUser.enterprise_id == enterprise_id,
        EnterpriseUser.user_id == current_user.id
    ).first()
    
    if not enterprise_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="你不属于该企业"
        )
    
    analytics_service = get_enterprise_analytics_service()
    activity = analytics_service.get_user_activity(db, enterprise_id, days)
    return activity


@router.get("/analytics/report/{enterprise_id}", summary="生成企业报表", response_model=EnterpriseReportResponse)
async def generate_enterprise_report(
    enterprise_id: int,
    report_type: str = "monthly",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """生成企业报表"""
    # 验证用户是否是企业管理员
    enterprise_user = db.query(EnterpriseUser).filter(
        EnterpriseUser.enterprise_id == enterprise_id,
        EnterpriseUser.user_id == current_user.id,
        EnterpriseUser.role == "admin"
    ).first()
    
    if not enterprise_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有企业管理员可以生成报表"
        )
    
    analytics_service = get_enterprise_analytics_service()
    report = analytics_service.generate_enterprise_report(db, enterprise_id, report_type)
    return report


@router.post("/compliance/policy", summary="创建合规策略", response_model=EnterpriseComplianceResponse)
async def create_compliance_policy(
    request: EnterpriseComplianceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建企业合规策略"""
    # 验证用户是否是企业管理员
    enterprise_user = db.query(EnterpriseUser).filter(
        EnterpriseUser.enterprise_id == request.enterprise_id,
        EnterpriseUser.user_id == current_user.id,
        EnterpriseUser.role == "admin"
    ).first()
    
    if not enterprise_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有企业管理员可以创建合规策略"
        )
    
    compliance_service = get_enterprise_compliance_service()
    policy = compliance_service.create_compliance_policy(
        db=db,
        enterprise_id=request.enterprise_id,
        policy_name=request.policy_name,
        policy_type=request.policy_type,
        policy_content=request.policy_content
    )
    return policy


@router.get("/compliance/policies/{enterprise_id}", summary="获取合规策略列表")
async def get_compliance_policies(
    enterprise_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取企业合规策略列表"""
    # 验证用户是否属于企业
    enterprise_user = db.query(EnterpriseUser).filter(
        EnterpriseUser.enterprise_id == enterprise_id,
        EnterpriseUser.user_id == current_user.id
    ).first()
    
    if not enterprise_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="你不属于该企业"
        )
    
    compliance_service = get_enterprise_compliance_service()
    policies = compliance_service.get_compliance_policies(db, enterprise_id)
    return policies


@router.post("/api-integration/webhook", summary="创建webhook", response_model=EnterpriseWebhookResponse)
async def create_webhook(
    request: EnterpriseWebhookCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建企业webhook"""
    # 验证用户是否是企业管理员
    enterprise_user = db.query(EnterpriseUser).filter(
        EnterpriseUser.enterprise_id == request.enterprise_id,
        EnterpriseUser.user_id == current_user.id,
        EnterpriseUser.role == "admin"
    ).first()
    
    if not enterprise_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有企业管理员可以创建webhook"
        )
    
    api_service = get_enterprise_api_integration_service()
    webhook = api_service.create_webhook(
        enterprise_id=request.enterprise_id,
        url=request.url,
        events=request.events
    )
    return webhook


@router.post("/sso/login", summary="企业SSO登录")
async def sso_login(
    domain: str,
    email: str,
    password: str,
    db: Session = Depends(get_db),
):
    """企业SSO登录"""
    auth_service = get_enterprise_auth_service()
    result = auth_service.sso_login(domain, email, password)
    return result
