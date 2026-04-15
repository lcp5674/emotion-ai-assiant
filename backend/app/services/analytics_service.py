"""
用户行为埋点服务
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
import loguru


class AnalyticsService:
    """用户行为分析服务"""
    
    # 事件类型定义
    EVENT_TYPES = {
        # 用户行为
        "user_register": "用户注册",
        "user_login": "用户登录",
        "user_logout": "用户登出",
        
        # MBTI测试
        "mbti_start": "开始MBTI测试",
        "mbti_complete": "完成MBTI测试",
        "mbti_quick_start": "开始快速MBTI测试",
        "mbti_quick_complete": "完成快速MBTI测试",
        
        # SBTI测试
        "sbti_start": "开始SBTI测试",
        "sbti_complete": "完成SBTI测试",
        
        # 依恋风格测试
        "attachment_start": "开始依恋测试",
        "attachment_complete": "完成依恋测试",
        
        # AI对话
        "chat_start": "开始AI对话",
        "chat_send": "发送消息",
        "chat_receive": "接收回复",
        
        # 页面浏览
        "page_view_home": "首页浏览",
        "page_view_profile": "画像页浏览",
        "page_view_assistant": "助手页浏览",
        "page_view_diary": "日记页浏览",
        "page_view_payment": "支付页浏览",
        
        # 分享
        "share_result": "分享结果",
        
        # 支付
        "payment_click": "点击支付",
        "payment_success": "支付成功",
    }
    
    async def track_event(
        self,
        event_type: str,
        user_id: Optional[int] = None,
        event_properties: Optional[Dict[str, Any]] = None,
        user_properties: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """记录用户行为事件
        
        Args:
            event_type: 事件类型
            user_id: 用户ID（可选）
            event_properties: 事件属性
            user_properties: 用户属性
            
        Returns:
            是否记录成功
        """
        # 验证事件类型
        if event_type not in self.EVENT_TYPES:
            loguru.logger.warning(f"未知事件类型: {event_type}")
            return False
        
        event_data = {
            "event_type": event_type,
            "event_name": self.EVENT_TYPES.get(event_type, event_type),
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "event_properties": event_properties or {},
            "user_properties": user_properties or {},
        }
        
        # 打印日志（实际项目中发送到分析服务）
        loguru.logger.info(f"[埋点] {event_data}")
        
        return True
    
    async def track_page_view(
        self,
        page_name: str,
        user_id: Optional[int] = None,
        referrer: Optional[str] = None,
    ) -> bool:
        """记录页面浏览"""
        return await self.track_event(
            event_type=f"page_view_{page_name}",
            user_id=user_id,
            event_properties={
                "page": page_name,
                "referrer": referrer,
            }
        )


_analytics_service: Optional[AnalyticsService] = None


def get_analytics_service() -> AnalyticsService:
    """获取分析服务实例"""
    global _analytics_service
    if _analytics_service is None:
        _analytics_service = AnalyticsService()
    return _analytics_service