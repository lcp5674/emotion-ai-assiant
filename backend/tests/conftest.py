"""
pytest配置和共享fixture
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings


# 使用SQLite内存数据库进行测试
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db_session():
    """数据库会话fixture - 每个测试函数一个新会话"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """测试客户端fixture - 使用测试数据库"""
    def _get_db_override():
        yield db_session

    app.dependency_overrides[get_db] = _get_db_override
    return TestClient(app)


@pytest.fixture
def test_user(db_session):
    """测试用户fixture - 在测试中可重用"""
    from app.models import User
    from app.core.security import get_password_hash

    user = User(
        phone="13800138000",
        nickname="测试用户",
        password_hash=get_password_hash("Test@123456"),
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_admin_user(db_session):
    """测试管理员用户fixture"""
    from app.models import User
    from app.core.security import get_password_hash

    user = User(
        phone="13900139000",
        nickname="测试管理员",
        password_hash=get_password_hash("Admin@123456"),
        is_active=True,
        is_admin=True,
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def auth_headers(client, test_user):
    """认证headers fixture - 使用测试用户登录"""
    login_resp = client.post("/api/v1/auth/login", json={
        "phone": "13800138000",
        "password": "Test@123456"
    })
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_auth_headers(client, test_admin_user):
    """管理员认证headers fixture"""
    login_resp = client.post("/api/v1/auth/login", json={
        "phone": "13900139000",
        "password": "Admin@123456"
    })
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mbti_questions():
    """MBTI题目fixture - 在内存中存储题目数据"""
    from app.services.mbti_service import MbtiService
    service = MbtiService()

    questions_data = []

    ei_data = service._get_ei_questions()
    sn_data = service._get_sn_questions()
    tf_data = service._get_tf_questions()
    jp_data = service._get_jp_questions()

    for i, q in enumerate(ei_data, 1):
        questions_data.append({
            "dimension": "EI",
            "question_no": i,
            "question_text": q["text"],
            "option_a": q["a"],
            "option_b": q["b"],
            "weight_a": 1,
            "weight_b": 1,
        })

    for i, q in enumerate(sn_data, 1):
        questions_data.append({
            "dimension": "SN",
            "question_no": i,
            "question_text": q["text"],
            "option_a": q["a"],
            "option_b": q["b"],
            "weight_a": 1,
            "weight_b": 1,
        })

    for i, q in enumerate(tf_data, 1):
        questions_data.append({
            "dimension": "TF",
            "question_no": i,
            "question_text": q["text"],
            "option_a": q["a"],
            "option_b": q["b"],
            "weight_a": 1,
            "weight_b": 1,
        })

    for i, q in enumerate(jp_data, 1):
        questions_data.append({
            "dimension": "JP",
            "question_no": i,
            "question_text": q["text"],
            "option_a": q["a"],
            "option_b": q["b"],
            "weight_a": 1,
            "weight_b": 1,
        })

    return questions_data


@pytest.fixture(autouse=True)
def setup_mbti_questions(db_session):
    """自动设置MBTI题目的fixture - 每个测试函数运行前"""
    from app.services.mbti_service import get_mbti_service
    mbti_service = get_mbti_service()
    mbti_service.seed_questions(db_session, force=True)


@pytest.fixture(autouse=True)
def setup_assistants(db_session):
    """自动设置AI助手的fixture"""
    from app.services.mbti_service import seed_assistants
    seed_assistants(db_session)
