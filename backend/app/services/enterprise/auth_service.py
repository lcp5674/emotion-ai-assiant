"""
企业认证服务
支持SSO、SAML、OAuth等企业级认证方式
"""
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.core.config import settings
from app.core.database import get_db
from app.models import User, Enterprise, EnterpriseUser
from sqlalchemy.orm import Session


class EnterpriseAuthService:
    """企业认证服务"""
    
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
    
    def create_enterprise_token(self, enterprise_id: int, user_id: int) -> str:
        """创建企业级JWT令牌"""
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {
            "sub": str(user_id),
            "enterprise_id": enterprise_id,
            "type": "enterprise",
            "exp": expire
        }
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_enterprise_token(self, token: str) -> Optional[Dict[str, Any]]:
        """验证企业级JWT令牌"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != "enterprise":
                return None
            return payload
        except JWTError:
            return None
    
    def get_enterprise_user(self, db: Session, enterprise_id: int, user_id: int) -> Optional[EnterpriseUser]:
        """获取企业用户关系"""
        return db.query(EnterpriseUser).filter(
            EnterpriseUser.enterprise_id == enterprise_id,
            EnterpriseUser.user_id == user_id
        ).first()
    
    def create_enterprise(self, db: Session, name: str, domain: str, admin_user_id: int) -> Enterprise:
        """创建企业"""
        enterprise = Enterprise(
            name=name,
            domain=domain,
            admin_user_id=admin_user_id
        )
        db.add(enterprise)
        db.commit()
        db.refresh(enterprise)
        
        # 创建企业管理员关系
        enterprise_user = EnterpriseUser(
            enterprise_id=enterprise.id,
            user_id=admin_user_id,
            role="admin"
        )
        db.add(enterprise_user)
        db.commit()
        
        return enterprise
    
    def add_enterprise_user(self, db: Session, enterprise_id: int, user_id: int, role: str = "member") -> EnterpriseUser:
        """添加企业用户"""
        enterprise_user = EnterpriseUser(
            enterprise_id=enterprise_id,
            user_id=user_id,
            role=role
        )
        db.add(enterprise_user)
        db.commit()
        db.refresh(enterprise_user)
        return enterprise_user
    
    def sso_login(self, domain: str, email: str, password: str) -> Optional[Dict[str, Any]]:
        """SSO登录"""
        # 这里实现SSO登录逻辑
        # 实际项目中需要集成企业的SSO系统
        pass
    
    def saml_login(self, saml_response: str) -> Optional[Dict[str, Any]]:
        """SAML登录"""
        # 这里实现SAML登录逻辑
        pass
    
    def oauth_login(self, provider: str, code: str) -> Optional[Dict[str, Any]]:
        """OAuth登录"""
        # 这里实现OAuth登录逻辑
        pass


def get_enterprise_auth_service() -> EnterpriseAuthService:
    """获取企业认证服务实例"""
    return EnterpriseAuthService()
