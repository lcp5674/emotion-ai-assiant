"""
管理员相关接口测试
"""
import pytest


def test_get_system_stats(authorized_admin_client, admin_user):
    """测试获取系统统计信息接口"""
    response = authorized_admin_client.get("/api/v1/admin/system/stats")
    assert response.status_code == 200
    assert response.json()["success"] == True
    data = response.json()["data"]
    assert "total_users" in data
    assert "total_diaries" in data
    assert "total_chats" in data
    assert "active_users_today" in data


def test_get_config(authorized_admin_client, admin_user):
    """测试获取系统配置接口"""
    response = authorized_admin_client.get("/api/v1/admin/config")
    assert response.status_code == 200
    data = response.json()
    assert "llm_provider" in data
    assert "openai_model" in data
    assert "has_openai_key" in data
    assert "has_anthropic_key" in data


def test_update_config(authorized_admin_client, admin_user):
    """测试更新系统配置接口"""
    update_data = {
        "llm_provider": "openai",
        "openai_model": "gpt-3.5-turbo"
    }
    response = authorized_admin_client.post("/api/v1/admin/config", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "changes" in data
    assert "llm_provider" in data["changes"]
    assert "openai_model" in data["changes"]


def test_test_llm(authorized_admin_client, admin_user):
    """测试LLM连接接口"""
    response = authorized_admin_client.post("/api/v1/admin/test")
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "provider" in data


def test_get_assistants(authorized_admin_client, admin_user):
    """获取AI助手列表接口"""
    response = authorized_admin_client.get("/api/v1/admin/assistants")
    assert response.status_code == 200
    data = response.json()
    assert "list" in data
    assert isinstance(data["list"], list)


def test_create_assistant(authorized_admin_client, admin_user):
    """测试创建AI助手接口"""
    create_data = {
        "name": "测试助手",
        "mbti_type": "INTJ",
        "personality": "聪明、理性",
        "speaking_style": "简洁直接",
        "greeting": "你好，我是你的AI助手"
    }
    response = authorized_admin_client.post("/api/v1/admin/assistants", json=create_data)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["name"] == create_data["name"]
    assert data["mbti_type"] == create_data["mbti_type"]


def test_update_assistant(authorized_admin_client, admin_user):
    """测试更新AI助手接口"""
    # 先创建一个助手
    create_data = {
        "name": "待更新助手",
        "mbti_type": "INFJ",
        "personality": "温和",
        "is_recommended": False
    }
    create_resp = authorized_admin_client.post("/api/v1/admin/assistants", json=create_data)
    assistant_id = create_resp.json()["id"]
    
    # 更新助手
    update_data = {
        "name": "已更新助手",
        "is_recommended": True,
        "is_active": False
    }
    response = authorized_admin_client.put(f"/api/v1/admin/assistants/{assistant_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]


def test_delete_assistant(authorized_admin_client, admin_user):
    """测试删除AI助手接口"""
    # 先创建一个助手
    create_data = {
        "name": "待删除助手",
        "mbti_type": "ENTP",
    }
    create_resp = authorized_admin_client.post("/api/v1/admin/assistants", json=create_data)
    assistant_id = create_resp.json()["id"]
    
    # 删除助手
    response = authorized_admin_client.delete(f"/api/v1/admin/assistants/{assistant_id}")
    assert response.status_code == 200
    assert "message" in response.json()


def test_get_dashboard_stats(authorized_admin_client, admin_user):
    """测试获取仪表盘统计接口"""
    response = authorized_admin_client.get("/api/v1/admin/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "user_count" in data
    assert "user_today" in data
    assert "active_users" in data
    assert "paid_users" in data
    assert "conversation_count" in data
    assert "diary_count" in data


def test_list_users(authorized_admin_client, admin_user, test_user):
    """测试获取用户列表接口"""
    response = authorized_admin_client.get("/api/v1/admin/users?page=1&size=10")
    assert response.status_code == 200
    assert response.json()["success"] == True
    data = response.json()["data"]
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "size" in data
    assert len(data["items"]) >= 1


def test_get_conversation_stats(authorized_admin_client, admin_user):
    """测试获取对话统计接口"""
    response = authorized_admin_client.get("/api/v1/admin/conversations/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_conversations" in data
    assert "total_messages" in data
    assert "active_conversations" in data
    assert "avg_messages_per_conversation" in data


def test_get_daily_stats(authorized_admin_client, admin_user):
    """测试获取每日统计接口"""
    response = authorized_admin_client.get("/api/v1/admin/stats/daily?days=7")
    assert response.status_code == 200
    data = response.json()
    assert "dates" in data
    assert "user_counts" in data
    assert "message_counts" in data
    assert "conversation_counts" in data
    assert len(data["dates"]) == 7


def test_get_user_detail(authorized_admin_client, admin_user, test_user):
    """测试获取用户详情接口"""
    response = authorized_admin_client.get(f"/api/v1/admin/users/{test_user.id}")
    assert response.status_code == 200
    assert response.json()["success"] == True
    data = response.json()["data"]
    assert data["id"] == test_user.id
    assert data["phone"] == test_user.phone


def test_update_user_status(authorized_admin_client, admin_user, test_user):
    """测试更新用户状态接口"""
    # 禁用用户
    response = authorized_admin_client.put(
        f"/api/v1/admin/users/{test_user.id}/status",
        json={"is_active": False}
    )
    assert response.status_code == 200
    assert response.json()["success"] == True
    
    # 尝试用禁用用户登录
    from app.models.user import User
    from app.core.database import SessionLocal
    db = SessionLocal()
    user = db_session.query(User).filter(User.id == test_user.id).first()
    assert user.is_active == False
    db.close()
    
    # 恢复用户
    response = authorized_admin_client.put(
        f"/api/v1/admin/users/{test_user.id}/status",
        json={"is_active": True}
    )
    assert response.status_code == 200


def test_delete_user(authorized_admin_client, admin_user, test_user):
    """测试删除用户接口"""
    response = authorized_admin_client.delete(f"/api/v1/admin/users/{test_user.id}")
    assert response.status_code == 200
    assert response.json()["success"] == True


def test_list_diaries(authorized_admin_client, admin_user):
    """测试获取日记列表接口"""
    response = authorized_admin_client.get("/api/v1/admin/diaries?page=1&size=10")
    assert response.status_code == 200
    assert response.json()["success"] == True
    data = response.json()["data"]
    assert "items" in data
    assert "total" in data


def test_get_audit_queue(authorized_admin_client, admin_user):
    """测试获取待审核内容列表接口"""
    response = authorized_admin_client.get("/api/v1/admin/audit-queue?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "list" in data
    assert isinstance(data["list"], list)


def test_review_audit_item(authorized_admin_client, admin_user, db_session):
    """测试审核内容接口"""
    from app.models.content_audit import ContentAuditQueue
    # 创建一个待审核项
    item = ContentAuditQueue(
        user_id=admin_user.id,
        content_type="diary",
        content_id=1,
        content_text="测试内容",
        status="pending"
    )
    db_session.add(item)
    db_session.commit()
    
    response = authorized_admin_client.post(
        f"/api/v1/admin/audit-queue/{item.id}/review",
        json={"status": "approved", "note": "审核通过"}
    )
    assert response.status_code == 200
    assert "message" in response.json()


def test_get_audit_stats(authorized_admin_client, admin_user):
    """测试获取审核统计接口"""
    response = authorized_admin_client.get("/api/v1/admin/audit-queue/stats")
    assert response.status_code == 200
    data = response.json()
    assert "pending" in data
    assert "processing" in data
    assert "approved" in data
    assert "rejected" in data
    assert "total" in data


def test_get_audit_logs(authorized_admin_client, admin_user):
    """测试获取审计日志接口"""
    response = authorized_admin_client.get("/api/v1/admin/audit-logs?page=1&size=10")
    assert response.status_code == 200
    assert response.json()["success"] == True
    data = response.json()["data"]
    assert "items" in data
    assert "total" in data


def test_non_admin_access_forbidden(authorized_client, test_user):
    """测试非管理员访问被拒绝"""
    response = authorized_client.get("/api/v1/admin/system/stats")
    assert response.status_code == 403
    
    response = authorized_client.get("/api/v1/admin/users")
    assert response.status_code == 403
    
    response = authorized_client.get("/api/v1/admin/config")
    assert response.status_code == 403
