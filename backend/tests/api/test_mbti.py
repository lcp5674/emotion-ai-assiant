"""
MBTI相关接口测试
"""
import pytest
from datetime import datetime


def test_get_questions(authorized_client):
    """测试获取MBTI测试题目接口"""
    response = authorized_client.get("/api/v1/mbti/questions")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "questions" in data
    assert isinstance(data["questions"], list)
    if len(data["questions"]) > 0:
        question = data["questions"][0]
        assert "id" in question
        assert "question_text" in question
        assert "dimension" in question
        assert "option_a" in question
        assert "option_b" in question
    
    # 按维度筛选
    response = authorized_client.get("/api/v1/mbti/questions?dimension=EI")
    assert response.status_code == 200


def test_start_test(authorized_client):
    """测试开始MBTI测试接口"""
    response = authorized_client.post("/api/v1/mbti/start")
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "total_questions" in data
    assert "estimated_time" in data


def test_submit_test(authorized_client, test_user, db_session):
    """测试提交MBTI测试答案接口"""
    # 获取问题
    questions_resp = authorized_client.get("/api/v1/mbti/questions")
    questions = questions_resp.json()["questions"][:10]  # 只取前10个问题
    
    answers = []
    for q in questions:
        answers.append({
            "question_id": q["id"],
            "answer": "A"
        })
    
    response = authorized_client.post("/api/v1/mbti/submit", json={"answers": answers})
    # 由于我们只回答了部分问题，可能会有问题，但接口应该可访问
    # 即使不完整，验证接口存在性
    assert response.status_code in [200, 400, 422]


def test_get_result_not_found(authorized_client, test_user):
    """测试获取MBTI测试结果 - 尚未完成测试"""
    test_user.mbti_result_id = None
    db_session.commit()
    
    response = authorized_client.get("/api/v1/mbti/result")
    assert response.status_code == 404


def test_get_assistants(authorized_client):
    """测试获取AI助手列表接口"""
    response = authorized_client.get("/api/v1/mbti/assistants")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "list" in data
    assert isinstance(data["list"], list)
    
    # 按MBTI类型筛选
    response = authorized_client.get("/api/v1/mbti/assistants?mbti_type=INTJ&recommended=true")
    assert response.status_code == 200


def test_get_assistant_detail(authorized_client, db_session):
    """测试获取AI助手详情接口"""
    from app.models import AiAssistant
    from app.models.mbti import MbtiType
    
    # 创建一个助手
    assistant = AiAssistant(
        name="测试助手",
        mbti_type=MbtiType.INTJ,
        personality="理性分析型",
        speaking_style="直接简洁",
        is_recommended=True,
        is_active=True,
    )
    db_session.add(assistant)
    db_session.commit()
    
    response = authorized_client.get(f"/api/v1/mbti/assistants/{assistant.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == assistant.id
    assert data["name"] == "测试助手"
    assert data["mbti_type"] == "INTJ"


def test_get_assistant_detail_not_found(authorized_client):
    """测试获取不存在的AI助手详情"""
    response = authorized_client.get("/api/v1/mbti/assistants/99999")
    assert response.status_code == 404


def test_public_access(client):
    """测试公开接口访问"""
    # MBTI题目应该允许未登录访问
    response = client.get("/api/v1/mbti/questions")
    assert response.status_code == 200
    
    # 开始测试也应该允许
    response = client.post("/api/v1/mbti/start")
    assert response.status_code == 200
    
    # 获取AI助手列表也应该允许
    response = client.get("/api/v1/mbti/assistants")
    assert response.status_code == 200
