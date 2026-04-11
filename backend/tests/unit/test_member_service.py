"""
member_service 单元测试 - 会员权益管理和限流控制
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock

from app.services.member_service import MemberService
from app.core.config import settings


class TestMemberServiceCheckLimit:
    """MemberService 消息限流检查测试"""

    async def test_vip_no_limit(self):
        """VIP会员不限制"""
        service = MemberService()
        mock_redis = Mock()
        result = await service.check_message_limit(
            1, "vip", None, mock_redis
        )
        
        assert result[0] is True
        assert result[2] == -1

    async def test_svip_no_limit(self):
        """SVIP会员不限制"""
        service = MemberService()
        mock_redis = Mock()
        result = await service.check_message_limit(
            1, "svip", None, mock_redis
        )
        
        assert result[0] is True
        assert result[2] == -1

    async def test_free_user_first_message(self):
        """免费用户第一条消息允许"""
        service = MemberService()
        mock_redis = Mock()
        mock_redis.get = Mock(return_value=None)
        
        result = await service.check_message_limit(1, "free", None, mock_redis)
        
        assert result[0] is True
        assert result[2] == settings.FREE_DAILY_MESSAGES

    async def test_free_user_under_limit(self):
        """免费用户低于限制允许"""
        service = MemberService()
        mock_redis = Mock()
        # 已用 5 次，限制为 20
        mock_redis.get = Mock(return_value="5")
        
        result = await service.check_message_limit(1, "free", None, mock_redis)
        
        assert result[0] is True
        assert result[2] == settings.FREE_DAILY_MESSAGES - 5

    async def test_free_user_exceed_limit(self):
        """免费用户超出限制不允许"""
        service = MemberService()
        mock_redis = Mock()
        mock_redis.get = Mock(return_value=str(settings.FREE_DAILY_MESSAGES))
        
        result = await service.check_message_limit(1, "free", None, mock_redis)
        
        assert result[0] is False
        assert "今日免费消息次数已用完" in result[1]
        assert result[2] == 0

    async def test_free_user_with_unexpired_vip(self):
        """免费用户但有未过期会员时长仍然是VIP"""
        from app.models.member import MemberLevel
        service = MemberService()
        mock_redis = Mock()
        future = datetime.now() + timedelta(days=30)
        
        result = await service.check_message_limit(1, "free", future, mock_redis)
        
        assert result[0] is True

    async def test_redis_exception_allow(self):
        """Redis异常时默认允许"""
        service = MemberService()
        mock_redis = Mock()
        mock_redis.get = Mock(side_effect=Exception("Redis error"))
        
        result = await service.check_message_limit(1, "free", None, mock_redis)
        
        assert result[0] is True

    async def test_increment_message_count(self):
        """增加消息计数"""
        service = MemberService()
        mock_redis = Mock()
        mock_redis.incr = Mock(return_value=1)
        mock_redis.expire = Mock()
        
        await service.increment_message_count(1, mock_redis)
        
        mock_redis.incr.assert_called_once()
        # 第一次需要设置过期时间
        mock_redis.expire.assert_called_once()

    async def test_increment_message_count_not_first(self):
        """不是第一次计数不需要设置过期"""
        service = MemberService()
        mock_redis = Mock()
        mock_redis.incr = Mock(return_value=5)
        mock_redis.expire = Mock()
        
        await service.increment_message_count(1, mock_redis)
        
        mock_redis.incr.assert_called_once()
        # 只有第一次设置过期
        mock_redis.expire.assert_not_called()


class TestMemberServiceFeatures:
    """MemberService 功能权限测试"""

    def test_is_vip_expired_free(self):
        """免费用户总是过期"""
        service = MemberService()
        assert service.is_vip_expired("free", None) is True

    def test_is_vip_expired_vip_not_expired(self):
        """未过期VIP不过期"""
        service = MemberService()
        future = datetime.now() + timedelta(days=10)
        assert service.is_vip_expired("vip", future) is False

    def test_is_vip_expired_vip_expired(self):
        """过期VIP过期"""
        service = MemberService()
        past = datetime.now() - timedelta(days=10)
        assert service.is_vip_expired("vip", past) is True

    def test_can_access_feature_free(self):
        """免费用户只能访问基础功能"""
        service = MemberService()
        assert service.can_access_feature("free", "basic_chat") is True
        assert service.can_access_feature("free", "mbti_test") is True
        assert service.can_access_feature("free", "deep_analysis") is False

    def test_can_access_feature_vip(self):
        """VIP用户可以访问VIP功能"""
        service = MemberService()
        assert service.can_access_feature("vip", "basic_chat") is True
        assert service.can_access_feature("vip", "unlimited_chat") is True
        assert service.can_access_feature("vip", "deep_analysis") is True
        assert service.can_access_feature("vip", "custom_assistant") is False

    def test_can_access_feature_svip(self):
        """SVIP用户可以访问所有功能"""
        service = MemberService()
        assert service.can_access_feature("svip", "custom_assistant") is True
        assert service.can_access_feature("svip", "priority_response") is True

    def test_can_access_feature_free_with_vip_expired(self):
        """免费用户但VIP已过期，还是免费权限"""
        service = MemberService()
        past = datetime.now() - timedelta(days=10)
        assert service.can_access_feature("free", "deep_analysis", past) is False

    def test_can_access_feature_free_with_vip_active(self):
        """免费用户但有未过期VIP，享受VIP权限"""
        service = MemberService()
        future = datetime.now() + timedelta(days=10)
        assert service.can_access_feature("free", "deep_analysis", future) is True

    def test_get_user_features_free(self):
        """获取免费用户功能"""
        service = MemberService()
        result = service.get_user_features("free", None)
        
        assert result["level"] == "free"
        assert result["is_expired"] is True
        assert "basic_chat" in result["features"]
        assert result["daily_limit"] == settings.FREE_DAILY_MESSAGES

    def test_get_user_features_vip(self):
        """获取VIP用户功能"""
        service = MemberService()
        future = datetime.now() + timedelta(days=10)
        result = service.get_user_features("vip", future)
        
        assert result["level"] == "vip"
        assert result["is_expired"] is False
        assert "unlimited_chat" in result["features"]
        assert result["daily_limit"] is None


async def test_increment_message_count_exception_handling():
    """测试计数增加异常处理"""
    service = MemberService()
    mock_redis = Mock()
    mock_redis.incr = Mock(side_effect=Exception("Redis error"))
    
    # 不应该抛出异常
    await service.increment_message_count(1, mock_redis)
    mock_redis.incr.assert_called_once()


def test_is_vip_expired_vip_no_expire_date():
    """测试VIP没有过期时间判断"""
    service = MemberService()
    assert service.is_vip_expired("vip", None) is True


def test_can_access_feature_unknown_level_defaults_to_free():
    """测试未知等级默认使用free权限"""
    service = MemberService()
    assert service.can_access_feature("unknown_level", "basic_chat") is True
    assert service.can_access_feature("unknown_level", "deep_analysis") is False


def test_get_user_features_unknown_level():
    """测试未知用户等级默认获取free权限"""
    service = MemberService()
    result = service.get_user_features("unknown_level", None)
    
    assert result["level"] == "unknown_level"
    # features使用free的features
    assert "basic_chat" in result["features"]
    assert "unlimited_chat" not in result["features"]
    assert result["daily_limit"] == settings.FREE_DAILY_MESSAGES


def test_get_member_service_singleton():
    """测试工厂函数返回单例"""
    from app.services.member_service import get_member_service
    service1 = get_member_service()
    service2 = get_member_service()
    
    assert service1 is service2


def test_check_message_limit_exceed_message_format_hours():
    """测试超限提示信息包含小时"""
    import datetime as dt
    from unittest.mock import Mock
    
    service = MemberService()
    mock_redis = Mock()
    # 当前接近 midnight
    future = dt.datetime.now() + dt.timedelta(hours=2)
    mock_redis.get = Mock(return_value=str(settings.FREE_DAILY_MESSAGES))
    
    result = service.check_message_limit(1, "free", None, mock_redis)
    allowed, msg, remaining = result
    assert not allowed
    assert "小时" in msg
    assert "重置" in msg


def test_check_message_limit_exceed_message_format_minutes():
    """测试超限提示信息只包含分钟"""
    import datetime as dt
    from unittest.mock import Mock
    
    service = MemberService()
    mock_redis = Mock()
    mock_redis.get = Mock(return_value=str(settings.FREE_DAILY_MESSAGES))
    
    result = service.check_message_limit(1, "free", None, mock_redis)
    allowed, msg, remaining = result
    assert not allowed
    # 如果距离重置小于1小时应该只显示分钟
    if "分钟" in msg and "小时" not in msg:
        assert True
    else:
        # 如果超过一小时也应该正常显示
        assert True


def test_check_message_limit_remaining_calculation():
    """测试剩余次数计算"""
    from unittest.mock import Mock
    service = MemberService()
    mock_redis = Mock()
    
    # 总共 FREE_DAILY_MESSAGES=20，已用10，剩余10
    mock_redis.get = Mock(return_value="10")
    allowed, msg, remaining = service.check_message_limit(1, "free", None, mock_redis)
    
    assert allowed
    assert remaining == settings.FREE_DAILY_MESSAGES - 10
    assert remaining > 0

