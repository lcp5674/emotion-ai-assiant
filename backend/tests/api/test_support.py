"""
客服系统API测试
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.user import User
from app.models.support import SupportTicket, TicketMessage, ChatbotConversation, ChatbotMessage, TicketStatus

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


def test_create_support_ticket(auth_token: str):
    """测试创建工单"""
    response = client.post(
        "/api/v1/support/tickets",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "title": "测试工单",
            "description": "这是一个测试工单",
            "category": "技术支持",
            "priority": "medium"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "测试工单"
    assert data["description"] == "这是一个测试工单"


def test_get_support_tickets(auth_token: str, db_session: Session, test_user: User):
    """测试获取工单列表"""
    # 创建测试工单
    ticket = SupportTicket(
        user_id=test_user.id,
        title="测试工单",
        description="这是一个测试工单",
        status=TicketStatus.PENDING
    )
    db_session.add(ticket)
    db_session.commit()
    
    response = client.get(
        "/api/v1/support/tickets",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0


def test_create_chatbot_conversation(auth_token: str):
    """测试创建智能客服对话"""
    response = client.post(
        "/api/v1/support/chatbot/conversations",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data


def test_send_chatbot_message(auth_token: str):
    """测试发送智能客服消息"""
    # 先创建对话
    create_response = client.post(
        "/api/v1/support/chatbot/conversations",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    conversation_id = create_response.json()["id"]
    
    # 发送消息
    response = client.post(
        f"/api/v1/support/chatbot/conversations/{conversation_id}/messages",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"content": "你好，我有一个问题"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["sender_type"] == "bot"
