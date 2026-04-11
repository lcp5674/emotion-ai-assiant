"""
认证服务
"""
from typing import Optional
from sqlalchemy.orm import Session
from datetime import timedelta
import loguru

from app.core.config import settings
from app.core.security import verify_password, create_access_token, create_refresh_token, get_password_hash
from app.models import User
from app.schemas.user import RegisterRequest as UserCreate, LoginResponse
from app.services.sms_service import get_sms_service


class AuthService:
    def __init__(self, db: Session):
        self.db = db
    
    async def register(self, user_create: UserCreate) -> User:
        """用户注册"""
        # 检查手机号是否已存在
        existing_user = self.db.query(User).filter(User.phone == user_create.phone).first()
        if existing_user:
            raise ValueError("手机号已被注册")
        
        # 验证验证码
        if settings.DEBUG:
            # 开发环境跳过验证码验证
            pass
        else:
            sms_service = get_sms_service()
            if not await sms_service.verify_code(user_create.phone, user_create.code):
                raise ValueError("验证码错误或已过期")
        
        # 创建用户
        hashed_password = get_password_hash(user_create.password)
        user = User(
            phone=user_create.phone,
            password_hash=hashed_password,
            nickname=f"用户{user_create.phone[-4:]}",
            is_active=True,
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        loguru.logger.info(f"用户注册成功: {user.id} - {user.phone}")
        return user
    
    async def login(self, phone: str, password: str) -> Optional[LoginResponse]:
        """用户登录"""
        user = self.db.query(User).filter(User.phone == phone).first()
        if not user or not verify_password(password, user.password_hash):
            return None
        
        if not user.is_active:
            raise ValueError("用户已被禁用")
        
        # 生成令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user,
        )
    
    async def login_with_sms(self, phone: str, code: str) -> Optional[LoginResponse]:
        """短信验证码登录"""
        # 验证验证码
        if settings.DEBUG:
            # 开发环境跳过验证码验证
            pass
        else:
            sms_service = get_sms_service()
            if not await sms_service.verify_code(phone, code):
                raise ValueError("验证码错误或已过期")
        
        # 查找用户，不存在则自动注册
        user = self.db.query(User).filter(User.phone == phone).first()
        if not user:
            # 自动创建用户
            user = User(
                phone=phone,
                nickname=f"用户{phone[-4:]}",
                is_active=True,
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            loguru.logger.info(f"短信登录自动创建用户: {user.id} - {phone}")
        
        if not user.is_active:
            raise ValueError("用户已被禁用")
        
        # 生成令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user,
        )
    
    async def refresh_token(self, refresh_token: str) -> Optional[LoginResponse]:
        """刷新令牌"""
        from app.core.security import decode_token
        
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                return None
            
            user_id = payload.get("sub")
            if not user_id:
                return None
            
            user = self.db.query(User).filter(User.id == int(user_id)).first()
            if not user or not user.is_active:
                return None
            
            # 生成新令牌
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            new_access_token = create_access_token(
                data={"sub": str(user.id)},
                expires_delta=access_token_expires
            )
            new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
            
            return LoginResponse(
                access_token=new_access_token,
                refresh_token=new_refresh_token,
                token_type="bearer",
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                user=user,
            )
        except Exception:
            return None


def get_auth_service(db: Session) -> AuthService:
    """获取认证服务实例"""
    return AuthService(db)
