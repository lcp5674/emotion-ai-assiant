"""
统一异常处理模块
"""
from typing import Optional


class AppException(Exception):
    """应用基础异常"""
    code: str = "INTERNAL_ERROR"
    message: str = "系统错误"
    status_code: int = 400

    def __init__(self, message: str = None):
        if message:
            self.message = message
        super().__init__(self.message)

    def to_dict(self):
        """转换为字典格式，用于API响应"""
        return {
            "code": self.code,
            "message": self.message,
        }


class ValidationException(AppException):
    """参数验证异常"""
    code = "VALIDATION_ERROR"
    message = "参数验证失败"
    status_code = 400


class AuthenticationException(AppException):
    """认证异常"""
    code = "AUTHENTICATION_FAILED"
    message = "认证失败"
    status_code = 401


class AuthorizationException(AppException):
    """授权异常"""
    code = "PERMISSION_DENIED"
    message = "权限不足"
    status_code = 403


class NotFoundException(AppException):
    """资源不存在异常"""
    code = "NOT_FOUND"
    message = "资源不存在"
    status_code = 404


class ConflictException(AppException):
    """资源冲突异常"""
    code = "CONFLICT"
    message = "资源冲突"
    status_code = 409


class RateLimitException(AppException):
    """速率限制异常"""
    code = "RATE_LIMIT_EXCEEDED"
    message = "请求过于频繁，请稍后重试"
    status_code = 429


class BusinessLogicException(AppException):
    """业务逻辑异常"""
    code = "BUSINESS_LOGIC_ERROR"
    message = "业务逻辑错误"
    status_code = 400


class ExternalServiceException(AppException):
    """外部服务调用异常"""
    code = "EXTERNAL_SERVICE_ERROR"
    message = "外部服务调用失败"
    status_code = 503


class DatabaseException(AppException):
    """数据库操作异常"""
    code = "DATABASE_ERROR"
    message = "数据库操作失败"
    status_code = 500


class ServiceUnavailableException(AppException):
    """服务不可用异常"""
    code = "SERVICE_UNAVAILABLE"
    message = "服务暂时不可用"
    status_code = 503


class InvalidTokenException(AuthenticationException):
    """无效令牌异常"""
    code = "INVALID_TOKEN"
    message = "令牌无效"
    status_code = 401


class TokenExpiredException(AuthenticationException):
    """令牌过期异常"""
    code = "TOKEN_EXPIRED"
    message = "令牌已过期"
    status_code = 401


class UserNotFoundException(NotFoundException):
    """用户不存在异常"""
    code = "USER_NOT_FOUND"
    message = "用户不存在"
    status_code = 404


class UserAlreadyExistsException(ConflictException):
    """用户已存在异常"""
    code = "USER_ALREADY_EXISTS"
    message = "用户已存在"
    status_code = 409


class PasswordIncorrectException(AuthenticationException):
    """密码不正确异常"""
    code = "PASSWORD_INCORRECT"
    message = "密码不正确"
    status_code = 401


class MemberLevelException(BusinessLogicException):
    """会员等级异常"""
    code = "MEMBER_LEVEL_ERROR"
    message = "会员等级错误"
    status_code = 400


class MessageLimitExceededException(BusinessLogicException):
    """消息数量超限异常"""
    code = "MESSAGE_LIMIT_EXCEEDED"
    message = "每日消息数量已超限"
    status_code = 403


class InvalidMbtiTypeException(ValidationException):
    """MBTI类型无效异常"""
    code = "INVALID_MBTI_TYPE"
    message = "MBTI类型无效"
    status_code = 400


class CrisisDetectionException(BusinessLogicException):
    """危机检测异常"""
    code = "CRISIS_DETECTED"
    message = "检测到危机情况"
    status_code = 400
