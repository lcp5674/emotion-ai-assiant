"""
Analytics Service Unit Tests
"""
import pytest
from app.services.analytics_service import AnalyticsService


class TestAnalyticsService:
    """Analytics service test cases"""
    
    @pytest.fixture
    def service(self):
        """Create analytics service instance"""
        return AnalyticsService()
    
    @pytest.mark.asyncio
    async def test_track_event_user_register(self, service):
        """Test user register event tracking"""
        result = await service.track_event(
            event_type="user_register",
            user_id=123,
            event_properties={"source": "wechat"}
        )
        assert result is True
    
    @pytest.mark.asyncio
    async def test_track_event_mbti_complete(self, service):
        """Test MBTI complete event"""
        result = await service.track_event(
            event_type="mbti_complete",
            user_id=456,
            event_properties={"mbti_type": "INTJ", "duration": 300}
        )
        assert result is True
    
    @pytest.mark.asyncio
    async def test_track_event_unknown_type(self, service):
        """Test unknown event type returns False"""
        result = await service.track_event(
            event_type="unknown_event",
            user_id=789
        )
        assert result is False
    
    @pytest.mark.asyncio
    async def test_track_page_view(self, service):
        """Test page view tracking"""
        result = await service.track_page_view(
            page_name="home",
            user_id=111,
            referrer="/"
        )
        assert result is True
    
    @pytest.mark.asyncio
    async def test_event_types_defined(self, service):
        """Test all expected event types are defined"""
        expected_types = [
            "user_register",
            "user_login",
            "mbti_start",
            "mbti_complete",
            "mbti_quick_start",
            "mbti_quick_complete",
            "sbti_start",
            "sbti_complete",
            "attachment_start",
            "attachment_complete",
            "chat_start",
            "chat_send",
            "share_result",
            "payment_click",
            "payment_success",
        ]
        
        for event_type in expected_types:
            assert event_type in service.EVENT_TYPES, f"Missing event type: {event_type}"