"""
用户相关Schema
"""

from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum
import re


class MemberLevelEnum(str, Enum):
    """会员等级"""

    FREE = "free"
    VIP = "vip"
    SVIP = "svip"
    ENTERPRISE = "enterprise"


# ========== 认证 ==========
class SmsSendRequest(BaseModel):
    """发送验证码请求"""

    phone: str = Field(..., pattern=r"^1[3-9]\d{9}$")


class SmsVerifyRequest(BaseModel):
    """验证验证码请求"""

    phone: str = Field(..., pattern=r"^1[3-9]\d{9}$")
    code: str = Field(..., min_length=6, max_length=6)


class RegisterRequest(BaseModel):
    """注册请求 - 支持多种注册方式"""

    # 手机号注册（需要验证码）
    phone: Optional[str] = Field(None, pattern=r"^1[3-9]\d{9}$")
    code: Optional[str] = Field(None, min_length=6, max_length=6)  # 短信验证码

    # 邮箱注册
    email: Optional[str] = None

    # 用户名注册
    username: Optional[str] = Field(None, min_length=3, max_length=20)

    password: str = Field(..., min_length=6, max_length=50)
    nickname: Optional[str] = None

    @field_validator('email')
    def validate_email_format(cls, v):
        if v is not None and not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', v):
            raise ValueError('邮箱格式不正确')
        return v

    @field_validator('username')
    def validate_username_format(cls, v):
        if v is not None:
            if not re.match(r'^[a-zA-Z0-9_]+$', v):
                raise ValueError('用户名只能包含字母、数字和下划线')
            if len(v) < 3:
                raise ValueError('用户名至少3个字符')
        return v

    def model_post_init(self, ctx):
        # 至少需要一种标识符
        if not any([self.phone, self.email, self.username]):
            raise ValueError('请提供手机号、邮箱或用户名')


class LoginRequest(BaseModel):
    """登录请求 - 支持手机号、邮箱、用户名登录"""

    identifier: str = Field(..., min_length=1, description="手机号、邮箱或用户名")
    password: str = Field(..., min_length=6, max_length=50)


class LoginResponse(BaseModel):
    """登录响应"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserInfo"


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求"""

    refresh_token: str


# ========== 用户信息 ==========
class UserInfo(BaseModel):
    """用户信息"""

    id: int
    phone: Optional[str] = None
    email: Optional[str] = None
    username: Optional[str] = None
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    mbti_type: Optional[str] = None
    member_level: Optional[str] = "free"
    member_expire_at: Optional[datetime] = None
    is_verified: bool = False
    is_admin: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class UpdateUserRequest(BaseModel):
    """更新用户信息请求"""

    nickname: Optional[str] = Field(None, max_length=50)
    avatar: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""

    old_password: str
    new_password: str = Field(..., min_length=8, max_length=20)

    @field_validator("new_password")
    def validate_new_password(cls, v):
        """验证新密码强度"""
        if len(v) < 8:
            raise ValueError("密码长度至少8位")
        if not re.search(r"[A-Z]", v):
            raise ValueError("密码必须包含大写字母")
        if not re.search(r"[a-z]", v):
            raise ValueError("密码必须包含小写字母")
        if not re.search(r"\d", v):
            raise ValueError("密码必须包含数字")
        if not re.search(r"[!@#$%^&*()_+{}[\]:;<>,.?~\\-]", v):
            raise ValueError("密码必须包含特殊字符")
        return v


class ResetPasswordRequest(BaseModel):
    """重置密码请求（通过手机验证码）"""

    phone: str = Field(..., pattern=r"^1[3-9]\d{9}$")
    code: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=8, max_length=20)

    @field_validator("new_password")
    def validate_reset_password(cls, v):
        """验证重置密码强度"""
        if len(v) < 8:
            raise ValueError("密码长度至少8位")
        if not re.search(r"[A-Z]", v):
            raise ValueError("密码必须包含大写字母")
        if not re.search(r"[a-z]", v):
            raise ValueError("密码必须包含小写字母")
        if not re.search(r"\d", v):
            raise ValueError("密码必须包含数字")
        if not re.search(r"[!@#$%^&*()_+{}[\]:;<>,.?~\\-]", v):
            raise ValueError("密码必须包含特殊字符")
        return v


# ========== 会员 ==========
class MemberPrice(BaseModel):
    """会员价格"""

    level: str
    name: str
    price: int  # 分
    duration: int  # 天
    features: list[str]


class MemberOrderCreate(BaseModel):
    """创建会员订单"""

    level: MemberLevelEnum


class MemberOrderResponse(BaseModel):
    """会员订单响应"""

    order_no: str
    amount: int
    pay_url: Optional[str] = None


# 更新 forward ref
LoginResponse.model_rebuild()
