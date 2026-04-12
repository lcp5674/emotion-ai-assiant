"""
测试配置文件
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models import user, mbti, chat, knowledge, diary, system


@pytest.fixture(scope="session")
def test_db():
    """测试数据库"""
    # 使用SQLite内存数据库
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(test_db):
    """数据库会话"""
    try:
        yield test_db
        test_db.commit()
    except Exception:
        test_db.rollback()
        raise


@pytest.fixture(scope="function")
def test_user(db_session):
    """测试用户"""
    from app.models.user import User
    from app.services.auth_service import get_password_hash

    user = User(
        phone="13800138001",  # 不同的手机号避免冲突
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
def admin_user(db_session):
    """管理员用户"""
    from app.models.user import User
    from app.services.auth_service import get_password_hash

    user = User(
        phone="13800138002",
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
def authorized_client(db_session, test_user):
    """授权客户端"""
    from fastapi.testclient import TestClient
    from app.main import app
    from app.core.security import create_access_token

    client = TestClient(app)
    token = create_access_token(data={"sub": str(test_user.id)})
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


@pytest.fixture(scope="function")
def authorized_admin_client(db_session, admin_user):
    """管理员授权客户端"""
    from fastapi.testclient import TestClient
    from app.main import app
    from app.core.security import create_access_token

    client = TestClient(app)
    token = create_access_token(data={"sub": str(admin_user.id)})
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


@pytest.fixture(scope="function")
def mock_llm_service():
    """模拟LLM服务"""
    from unittest.mock import Mock
    mock = Mock()
    mock.generate.return_value = {"answer": "测试回复", "references": []}
    return mock


@pytest.fixture(scope="function")
def mock_sms_service():
    """模拟短信服务"""
    from unittest.mock import Mock
    mock = Mock()
    mock.send_verify_code.return_value = True
    return mock
