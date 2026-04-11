"""
数据分析API测试
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.core.database import get_db
from app.models.user import User
from app.models.analytics import UserActivity, AnalyticsMetric, UserBehavior, EventType
from app.schemas.analytics import UserActivityCreate

client = TestClient(app)


@pytest.fixture
def db_session():
    """获取数据库会话"""
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_user(db_session: Session):
    """创建测试用户"""
    user = User(
        phone="13800138000",
        email="test@example.com",
        nickname="测试用户",
        password_hash="test_hash",
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_token(test_user: User):
    """获取认证令牌"""
    response = client.post(
        "/api/v1/auth/login",
        json={"phone": "13800138000", "password": "test_password"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def test_create_user_activity(auth_token: str):
    """测试创建用户活动"""
    response = client.post(
        "/api/v1/analytics/activities",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "event_type": "page_view",
            "event_name": "首页访问",
            "event_data": "{\"url\": \"/home\"}",
            "ip_address": "127.0.0.1",
            "user_agent": "Mozilla/5.0"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["event_type"] == "page_view"
    assert data["event_name"] == "首页访问"


def test_get_user_activities(auth_token: str, db_session: Session, test_user: User):
    """测试获取用户活动列表"""
    # 创建测试活动
    activity = UserActivity(
        user_id=test_user.id,
        event_type=EventType.PAGE_VIEW,
        event_name="测试活动",
        event_data="{\"test\": \"data\"}"
    )
    db_session.add(activity)
    db_session.commit()
    
    response = client.get(
        "/api/v1/analytics/activities",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0


def test_get_user_behavior_stats(auth_token: str):
    """测试获取用户行为统计"""
    response = client.get(
        "/api/v1/analytics/user-behavior-stats",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "activity_count" in data
    assert "activity_types" in data
    assert "top_behaviors" in data
