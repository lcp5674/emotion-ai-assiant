"""
用户管理相关接口测试
"""
import pytest
from app.core.security import get_password_hash


def test_get_profile(authorized_client, test_user):
    """测试获取用户资料接口"""
    response = authorized_client.get("/api/v1/user/profile")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user.id
    assert data["phone"] == test_user.phone
    assert data["nickname"] == test_user.nickname


def test_update_profile(authorized_client, test_user):
    """测试更新用户资料接口"""
    update_data = {
        "nickname": "新昵称",
        "avatar": "https://example.com/new-avatar.jpg"
    }
    response = authorized_client.put("/api/v1/user/profile", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["nickname"] == update_data["nickname"]
    assert data["avatar"] == update_data["avatar"]


def test_change_password(authorized_client, test_user, db_session):
    """测试修改密码接口"""
    from app.models.user import User
    # 更新用户密码以便测试
    user = db_session.query(User).filter(User.id == test_user.id).first()
    user.password_hash = get_password_hash("oldpassword")
    db_session.commit()
    
    # 错误的旧密码
    response = authorized_client.post("/api/v1/user/password", json={
        "old_password": "wrongpassword",
        "new_password": "newpassword123"
    })
    assert response.status_code == 400
    
    # 正确的旧密码
    response = authorized_client.post("/api/v1/user/password", json={
        "old_password": "oldpassword",
        "new_password": "newpassword123"
    })
    assert response.status_code == 200
    assert "message" in response.json()


def test_get_user_stats(authorized_client, test_user):
    """测试获取用户统计接口"""
    response = authorized_client.get("/api/v1/user/stats")
    assert response.status_code == 200
    data = response.json()
    assert "conversation_count" in data
    assert "mbti_test_count" in data
    assert "member" in data


def test_get_onboarding_status(authorized_client, test_user):
    """测试获取首次使用引导状态接口"""
    response = authorized_client.get("/api/v1/user/onboarding-status")
    assert response.status_code == 200
    data = response.json()
    assert "has_completed_onboarding" in data
    assert "steps" in data
    assert "current_step" in data
    assert "complete_mbti" in data["steps"]
    assert "create_first_diary" in data["steps"]
    assert "start_first_chat" in data["steps"]


def test_mark_onboarding_step(authorized_client, test_user):
    """测试标记引导步骤已完成接口"""
    response = authorized_client.post("/api/v1/user/mark-onboarding-step?step=complete_mbti")
    assert response.status_code == 200
    assert response.json()["success"] == True


def test_get_privacy_info(authorized_client, test_user):
    """测试获取用户数据隐私说明接口"""
    response = authorized_client.get("/api/v1/user/privacy-info")
    assert response.status_code == 200
    data = response.json()
    assert "title" in data
    assert "points" in data
    assert "data_controls" in data


def test_request_data_export(authorized_client, test_user):
    """测试请求数据导出接口"""
    response = authorized_client.post("/api/v1/user/request-data-export")
    assert response.status_code == 200
    assert response.json()["success"] == True
    assert "message" in response.json()


def test_request_account_deletion(authorized_client, test_user):
    """测试请求删除账户接口"""
    response = authorized_client.post("/api/v1/user/request-account-deletion")
    assert response.status_code == 200
    assert response.json()["success"] == True
    assert "message" in response.json()


def test_get_current_user_info(authorized_client, test_user):
    """测试获取当前用户信息接口"""
    response = authorized_client.get("/api/v1/user/me")
    assert response.status_code == 200
    assert response.json()["success"] == True
    data = response.json()["data"]
    assert data["id"] == test_user.id
    assert data["phone"] == test_user.phone
    assert data["nickname"] == test_user.nickname


def test_update_current_user_info(authorized_client, test_user):
    """测试更新当前用户信息接口"""
    update_data = {
        "nickname": "新昵称",
        "avatar": "https://example.com/new-avatar.jpg",
        "gender": "male",
        "birthday": "1995-05-15",
        "bio": "这是我的个人简介"
    }
    response = authorized_client.put("/api/v1/user/me", json=update_data)
    assert response.status_code == 200
    assert response.json()["success"] == True
    data = response.json()["data"]
    assert data["nickname"] == update_data["nickname"]
    assert data["avatar"] == update_data["avatar"]
    assert data["gender"] == update_data["gender"]
    assert data["bio"] == update_data["bio"]


def test_get_user_by_id(authorized_client, test_user):
    """测试根据ID获取用户信息接口"""
    response = authorized_client.get(f"/api/v1/user/{test_user.id}")
    assert response.status_code == 200
    assert response.json()["success"] == True
    data = response.json()["data"]
    assert data["id"] == test_user.id
    assert data["nickname"] == test_user.nickname
    # 不应该返回敏感信息
    assert "password_hash" not in data


def test_get_user_by_id_not_found(authorized_client):
    """测试用户不存在的情况"""
    response = authorized_client.get("/api/v1/user/99999")
    assert response.status_code == 404
    assert response.json()["code"] == "USER_NOT_FOUND"


def test_unauthorized_access(client):
    """测试未授权访问用户接口"""
    response = client.get("/api/v1/user/profile")
    assert response.status_code == 401
    
    response = client.put("/api/v1/user/profile", json={"nickname": "测试"})
    assert response.status_code == 401
    
    response = client.get("/api/v1/user/me")
    assert response.status_code == 401
