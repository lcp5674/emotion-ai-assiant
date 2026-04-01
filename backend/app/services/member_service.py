"""
会员服务 - 权益管理和限流控制
"""
from datetime import datetime, timedelta
from typing import Optional, Tuple
import loguru

from app.core.config import settings


class MemberService:
    """会员权益服务"""

    FEATURES = {
        "free": ["basic_chat", "mbti_test", "knowledge_view"],
        "vip": ["unlimited_chat", "mbti_test", "knowledge_view", "deep_analysis", "diary"],
        "svip": ["unlimited_chat", "mbti_test", "knowledge_view", "deep_analysis", "diary", "custom_assistant", "priority_response"],
        "enterprise": ["unlimited_chat", "mbti_test", "knowledge_view", "deep_analysis", "diary", "custom_assistant", "priority_response", "api_access", "data_report"],
    }

    FREE_DAILY_LIMIT = settings.FREE_DAILY_MESSAGES

    async def check_message_limit(
        self,
        user_id: int,
        member_level: str,
        member_expire_at: Optional[datetime],
        redis_client,
    ) -> Tuple[bool, str, int]:
        """
        检查用户是否可以发送消息
        
        Returns:
            tuple: (是否允许, 提示信息, 剩余次数)
        """
        if member_level != "free":
            return True, "", -1

        if member_expire_at and member_expire_at > datetime.now():
            return True, "", -1

        today = datetime.now().strftime("%Y%m%d")
        key = f"limit:message:{user_id}:{today}"

        try:
            current_count = await redis_client.get(key)
            if current_count is None:
                return True, "", self.FREE_DAILY_LIMIT

            current_count = int(current_count)
            remaining = max(0, self.FREE_DAILY_LIMIT - current_count)

            if current_count >= self.FREE_DAILY_LIMIT:
                reset_time = (datetime.now() + timedelta(days=1)).replace(hour=0, minute=0, second=0)
                wait_seconds = int((reset_time - datetime.now()).total_seconds())
                hours = wait_seconds // 3600
                minutes = (wait_seconds % 3600) // 60
                if hours > 0:
                    reset_str = f"{hours}小时{minutes}分钟后"
                else:
                    reset_str = f"{minutes}分钟后"
                return False, f"今日免费消息次数已用完（{self.FREE_DAILY_LIMIT}条/天）。{reset_str}将重置。成为VIP会员可解锁无限消息。", remaining

            return True, "", remaining
        except Exception as e:
            loguru.logger.warning(f"限流检查失败: {e}")
            return True, "", self.FREE_DAILY_LIMIT

    async def increment_message_count(self, user_id: int, redis_client) -> None:
        """增加消息计数"""
        today = datetime.now().strftime("%Y%m%d")
        key = f"limit:message:{user_id}:{today}"

        try:
            count = await redis_client.incr(key)
            if count == 1:
                ttl = 86400
                await redis_client.expire(key, ttl)
        except Exception as e:
            loguru.logger.warning(f"限流计数失败: {e}")

    def is_vip_expired(self, member_level: str, member_expire_at: Optional[datetime]) -> bool:
        """检查VIP是否过期"""
        if member_level == "free":
            return True
        if member_expire_at is None:
            return member_level != "free"
        return member_expire_at < datetime.now()

    def can_access_feature(self, member_level: str, feature: str, member_expire_at: Optional[datetime] = None) -> bool:
        level = member_level if member_level else "free"
        if level == "free" and member_expire_at and member_expire_at > datetime.now():
            level = "vip"

        allowed_features = self.FEATURES.get(level, self.FEATURES["free"])
        return feature in allowed_features

    def get_user_features(self, member_level: str, member_expire_at: Optional[datetime]) -> dict:
        """获取用户可用的功能列表"""
        level = member_level if member_level else "free"
        if level == "free":
            if member_expire_at and member_expire_at > datetime.now():
                level = "vip"

        features = self.FEATURES.get(level, self.FEATURES["free"])
        is_expired = self.is_vip_expired(member_level, member_expire_at)

        return {
            "level": level,
            "is_expired": is_expired,
            "features": features,
            "daily_limit": None if level != "free" else self.FREE_DAILY_LIMIT,
        }


_member_service: Optional[MemberService] = None


def get_member_service() -> MemberService:
    """获取会员服务实例"""
    global _member_service
    if _member_service is None:
        _member_service = MemberService()
    return _member_service
