# -*- coding: utf-8 -*-
"""
SBTI API集成测试
"""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """创建测试客户端"""
    from app.main import app
    return TestClient(app)


@pytest.fixture
def auth_headers(client):
    """获取认证头"""
    # 先注册并登录获取token
    from app.core.database import SessionLocal, Base, engine
    from app.models import User, MemberLevel
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    db = SessionLocal()

    # 创建测试用户
    test_user = db.query(User).filter(User.phone == "13800138000").first()
    if not test_user:
        test_user = User(
            phone="13800138000",
            nickname="测试用户",
            password_hash=pwd_context.hash("test123456"),
            member_level=MemberLevel.FREE
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)

    db.close()

    # 登录获取token
    response = client.post("/api/v1/auth/login", json={
        "phone": "13800138000",
        "password": "test123456"
    })

    if response.status_code == 200:
        token = response.json().get("access_token")
        return {"Authorization": f"Bearer {token}"}

    return {}


class TestSbtiQuestionsAPI:
    """SBTI题目API测试"""

    def test_get_questions_without_auth(self):
        """测试获取题目不需要认证"""
        from app.main import app
        test_client = TestClient(app)

        response = test_client.get("/api/v1/sbti/questions")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 24
        assert len(data["questions"]) == 24

    def test_questions_structure(self):
        """测试题目数据结构"""
        from app.main import app
        test_client = TestClient(app)

        response = test_client.get("/api/v1/sbti/questions")
        data = response.json()

        for q in data["questions"]:
            assert "id" in q
            assert "question_no" in q
            assert "statement_a" in q
            assert "statement_b" in q
            assert "theme_a" in q
            assert "theme_b" in q
            assert "domain" in q


class TestSbtiSubmitAPI:
    """SBTI提交API测试"""

    def test_submit_without_auth(self):
        """测试未认证提交应返回401"""
        from app.main import app
        test_client = TestClient(app)

        answers = [{"question_id": i, "answer": "A"} for i in range(1, 25)]
        response = test_client.post("/api/v1/sbti/submit", json={"answers": answers})

        assert response.status_code in [401, 403]

    def test_submit_invalid_answer_count(self, client, auth_headers):
        """测试答案数量不足"""
        if not auth_headers:
            pytest.skip("无法获取认证token")

        answers = [{"question_id": i, "answer": "A"} for i in range(1, 10)]  # 只有9题
        response = client.post("/api/v1/sbti/submit",
                             json={"answers": answers},
                             headers=auth_headers)

        assert response.status_code == 400
        assert "24道题目" in response.json().get("detail", "")


class TestSbtiResultAPI:
    """SBTI结果API测试"""

    def test_get_result_without_assessment(self, client, auth_headers):
        """测试未测评获取结果"""
        if not auth_headers:
            pytest.skip("无法获取认证token")

        response = client.get("/api/v1/sbti/result", headers=auth_headers)

        assert response.status_code == 404


class TestSbtiThemeDetailAPI:
    """SBTI主题详情API测试"""

    def test_get_theme_detail_valid(self):
        """测试获取有效主题详情"""
        from app.main import app
        test_client = TestClient(app)

        response = test_client.get("/api/v1/sbti/themes/成就")

        assert response.status_code == 200
        data = response.json()
        assert data["theme"] == "成就"
        assert "info" in data

    def test_get_theme_detail_invalid(self):
        """测试获取无效主题"""
        from app.main import app
        test_client = TestClient(app)

        response = test_client.get("/api/v1/sbti/themes/不存在的才干")

        assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
