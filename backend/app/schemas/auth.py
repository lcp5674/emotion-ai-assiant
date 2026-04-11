"""
认证相关schema
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

from app.schemas.user import UserInfo as UserResponse


class UserCreate(BaseModel):
    """用户注册请求"""
    phone: str = Field(..., description="手机号", min_length=11, max_length=11)
    password: str = Field(..., description="密码", min_length=6, max_length=32)
    code: str = Field(..., description="验证码", min_length=6, max_length=6)
    
    @field_validator("phone")
    def validate_phone(cls, v):
        if not v.isdigit() or len(v) != 11:
            raise ValueError("手机号格式不正确")
        return v


class UserLogin(BaseModel):
    """用户登录请求"""
    phone: str = Field(..., description="手机号")
    password: str = Field(..., description="密码")


class SmsLogin(BaseModel):
    """短信登录请求"""
    phone: str = Field(..., description="手机号")
    code: str = Field(..., description="验证码")


class SmsSendRequest(BaseModel):
    """发送验证码请求"""
    phone: str = Field(..., description="手机号")
    
    @field_validator("phone")
    def validate_phone(cls, v):
        if not v.isdigit() or len(v) != 11:
            raise ValueError("手机号格式不正确")
        return v


class TokenRefreshRequest(BaseModel):
    """刷新令牌请求"""
    refresh_token: str = Field(..., description="刷新令牌")


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="有效期（秒）")
    user: UserResponse = Field(..., description="用户信息")
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """令牌响应"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="有效期（秒）")


class SmsSendResponse(BaseModel):
    """发送验证码响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="消息")
    expire_seconds: int = Field(default=300, description="有效期（秒）")
