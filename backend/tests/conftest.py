"""
测试配置
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import Mock, patch

from app.main import app
from app.core.config import settings
from app.core.database import Base, get_db
from app.services.auth_service import create_access_token

# 使用SQLite内存数据库进行测试
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """测试用数据库依赖"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def event_loop():
    """创建会话级别的事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session():
    """数据库会话fixture"""
    # 创建表
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    # 回滚并删除表
    db.rollback()
    Base.metadata.drop_all(bind=engine)
    db.close()


@pytest.fixture(scope="function")
def client(db_session):
    """测试客户端fixture"""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db_session):
    """测试用户fixture"""
    from app.models.user import User
    from app.services.auth_service import get_password_hash
    
    user = User(
        phone="13800138000",
        email="test@example.com",
        nickname="测试用户",
        password_hash=get_password_hash("Test@123456"),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def authorized_client(client, test_user):
    """带认证的测试客户端fixture"""
    access_token = create_access_token(data={"sub": str(test_user.id)})
    client.headers["Authorization"] = f"Bearer {access_token}"
    return client


@pytest.fixture(scope="function")
def mock_llm_service():
    """Mock LLM服务fixture"""
    with patch("app.services.llm_service.get_llm_response") as mock:
        mock.return_value = "这是一个测试回复"
        yield mock


@pytest.fixture(scope="function")
def mock_sms_service():
    """Mock SMS服务fixture"""
    with patch("app.services.sms_service.send_verification_code") as mock:
        mock.return_value = True
        yield mock


@pytest.fixture(scope="function")
def admin_user(db_session):
    """管理员用户fixture"""
    from app.models.user import User
    from app.services.auth_service import get_password_hash
    
    user = User(
        phone="13800138001",
        email="admin@example.com",
        nickname="管理员",
        password_hash=get_password_hash("Admin@123456"),
        is_active=True,
        is_admin=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def authorized_admin_client(client, admin_user):
    """带管理员认证的测试客户端fixture"""
    access_token = create_access_token(data={"sub": str(admin_user.id)})
    client.headers["Authorization"] = f"Bearer {access_token}"
    return client
