"""
用户行为分析接口
"""
from fastapi import APIRouter, Depends
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
import loguru

from app.api.deps import get_current_user, get_current_user_optional
from app.models import User


router = APIRouter(prefix="/analytics", tags=["数据分析"])


class EventTrackRequest(BaseModel):
    """事件埋点请求"""
    event_type: str
    event_properties: Optional[Dict[str, Any]] = None
    user_properties: Optional[Dict[str, Any]] = None


class PageViewRequest(BaseModel):
    """页面浏览请求"""
    page_name: str
    referrer: Optional[str] = None


@router.post("/track", summary="埋点事件")
async def track_event(
    request: EventTrackRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """记录用户行为事件"""
    from app.services.analytics_service import get_analytics_service
    
    analytics = get_analytics_service()
    
    user_id = current_user.id if current_user else None
    event_properties = request.event_properties or {}
    user_properties = request.user_properties or {}
    
    # 添加用户设备信息
    if not user_properties.get("is_authenticated") and current_user:
        user_properties["is_authenticated"] = True
    
    success = await analytics.track_event(
        event_type=request.event_type,
        user_id=user_id,
        event_properties=event_properties,
        user_properties=user_properties,
    )
    
    return {"success": success}


@router.post("/page_view", summary="页面浏览")
async def track_page_view(
    request: PageViewRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """记录页面浏览"""
    from app.services.analytics_service import get_analytics_service
    
    analytics = get_analytics_service()
    user_id = current_user.id if current_user else None
    
    await analytics.track_page_view(
        page_name=request.page_name,
        user_id=user_id,
        referrer=request.referrer,
    )
    
    return {"success": True}


# ==================== 预定义埋点事件（供前端调用）====================

@router.get("/events", summary="获取支持的事件类型")
async def get_event_types():
    """获取支持的事件类型列表"""
    from app.services.analytics_service import get_analytics_service
    
    analytics = get_analytics_service()
    return {"events": analytics.EVENT_TYPES}


# 用户相关
USER_REGISTER = "user_register"
USER_LOGIN = "user_login"
USER_LOGOUT = "user_logout"

# MBTI测试
MBTI_START = "mbti_start"
MBTI_COMPLETE = "mbti_complete"
MBTI_QUICK_START = "mbti_quick_start"
MBTI_QUICK_COMPLETE = "mbti_quick_complete"

# AI对话
CHAT_START = "chat_start"
CHAT_SEND = "chat_send"
CHAT_RECEIVE = "chat_receive"

# 页面浏览
PAGE_VIEW_HOME = "page_view_home"
PAGE_VIEW_PROFILE = "page_view_profile"
PAGE_VIEW_ASSISTANT = "page_view_assistant"
PAGE_VIEW_DIARY = "page_view_diary"
PAGE_VIEW_PAYMENT = "page_view_payment"

# 支付
PAYMENT_CLICK = "payment_click"
PAYMENT_SUCCESS = "payment_success"