"""
认证相关接口测试
"""
import pytest
from unittest.mock import patch, AsyncMock


def test_send_verify_code(client):
    """测试发送验证码接口"""
    with patch("app.services.sms_service.get_sms_service") as mock_sms:
        mock_instance = AsyncMock()
        mock_instance.send_verify_code = AsyncMock(return_value=True)
        mock_sms.return_value = mock_instance
        
        response = client.post("/api/v1/auth/send_code", json={
            "phone": "13800138000"
        })
        assert response.status_code == 200
        assert "message" in response.json()


def test_register(client, db_session):
    """测试用户注册接口"""
    from app.core.config import settings
    
    # 在DEBUG模式下不需要验证码
    with patch("app.core.config.settings.DEBUG", new=True):
        response = client.post("/api/v1/auth/register", json={
            "phone": "13800138001",
            "password": "Password123!",
            "nickname": "测试用户",
            "code": "123456",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "user" in data
        assert data["user"]["phone"] == "13800138001"


def test_register_duplicate_phone(client, test_user, db_session):
    """测试重复手机号注册"""
    from app.core.config import settings
    with patch("app.core.config.settings.DEBUG", new=True):
        # 使用已存在的手机号
        response = client.post("/api/v1/auth/register", json={
            "phone": test_user.phone,
            "password": "Password123!",
            "nickname": "重复用户",
            "code": "123456",
        })
        assert response.status_code == 400
        assert "该手机号已注册" in response.json()["detail"]


def test_login(client, test_user, db_session):
    """测试用户登录接口"""
    from app.models.user import User
    from app.core.security import get_password_hash
    
    # 更新密码以便测试
    user = db_session.query(User).filter(User.id == test_user.id).first()
    user.password_hash = get_password_hash("Password123!")
    db_session.commit()
    
    response = client.post("/api/v1/auth/login", json={
        "phone": user.phone,
        "password": "Password123!",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "user" in data


def test_login_wrong_password(client, test_user, db_session):
    """测试密码错误登录"""
    from app.models.user import User
    from app.core.security import get_password_hash
    
    user = db_session.query(User).filter(User.id == test_user.id).first()
    user.password_hash = get_password_hash("Correctpass1!")
    db_session.commit()
    
    response = client.post("/api/v1/auth/login", json={
        "phone": user.phone,
        "password": "Wrongpass1!",
    })
    assert response.status_code == 401
    assert "手机号或密码错误" in response.json()["detail"]


def test_login_inactive_user(client, test_user, db_session):
    """测试禁用用户登录"""
    from app.models.user import User
    from app.core.security import get_password_hash
    
    user = db_session.query(User).filter(User.id == test_user.id).first()
    user.password_hash = get_password_hash("Password123!")
    user.is_active = False
    db_session.commit()
    
    response = client.post("/api/v1/auth/login", json={
        "phone": user.phone,
        "password": "Password123!",
    })
    assert response.status_code == 403
    assert "账号已被禁用" in response.json()["detail"]


def test_refresh_token(client, test_user):
    """测试刷新令牌接口"""
    from app.core.security import create_refresh_token
    
    refresh_token = create_refresh_token(data={"sub": str(test_user.id)})
    
    response = client.post("/api/v1/auth/refresh", json={
        "refresh_token": refresh_token,
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "expires_in" in data


def test_refresh_token_invalid(client):
    """测试使用无效刷新令牌"""
    response = client.post("/api/v1/auth/refresh", json={
        "refresh_token": "invalid_token",
    })
    assert response.status_code == 401


def test_get_current_user_info(authorized_client, test_user):
    """测试获取当前用户信息接口"""
    response = authorized_client.get("/api/v1/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user.id
    assert data["phone"] == test_user.phone


def test_logout(authorized_client, test_user):
    """测试退出登录接口"""
    response = authorized_client.post("/api/v1/auth/logout")
    assert response.status_code == 200
    assert "message" in response.json()


def test_reset_password(client, test_user, db_session):
    """测试重置密码接口"""
    response = client.post("/api/v1/auth/reset_password", json={
        "phone": test_user.phone,
        "code": "123456",
        "new_password": "Newpass1!",
    })
    # 验证码会验证失败，但接口应该可访问（参数验证通过）
    assert response.status_code in [400, 200]


def test_reset_password_user_not_found(client):
    """测试重置不存在用户密码"""
    response = client.post("/api/v1/auth/reset_password", json={
        "phone": "19999999999",
        "code": "123456",
        "new_password": "Newpass1!",
    })
    # 参数验证通过，会返回404
    assert response.status_code == 404


def test_get_crisis_resources(client):
    """测试获取危机干预资源接口 - 公开访问"""
    response = client.get("/api/v1/auth/crisis-resources")
    assert response.status_code == 200
    data = response.json()
    assert "title" in data
    assert "hotlines" in data
    assert "urgent_message" in data
    assert len(data["hotlines"]) > 0


def test_unauthorized_access(client):
    """测试未授权访问需要认证的接口"""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    
    response = client.post("/api/v1/auth/logout")
    assert response.status_code == 401


def test_send_verify_code_sms_failure(client):
    """测试发送验证码 - 短信发送失败仍返回成功"""
    with patch("app.services.sms_service.get_sms_service") as mock_sms:
        mock_instance = AsyncMock()
        mock_instance.send_verify_code = AsyncMock(return_value=False)
        mock_sms.return_value = mock_instance
        
        response = client.post("/api/v1/auth/send_code", json={
            "phone": "13800138000"
        })
        # 即使发送失败，接口仍返回200（不暴露给前端知道发送失败）
        assert response.status_code == 200
        assert "message" in response.json()


def test_register_wrong_verification_code(client, db_session):
    """测试注册 - 验证码错误（非DEBUG模式）"""
    with patch("app.core.config.settings.DEBUG", new=False):
        response = client.post("/api/v1/auth/register", json={
            "phone": "13800138002",
            "password": "Password123!",
            "nickname": "测试用户",
            "code": "wrong",
        })
        assert response.status_code == 400
        assert "验证码错误" in response.json()["detail"]


def test_refresh_token_wrong_type(client, test_user):
    """测试刷新令牌 - 令牌类型不对"""
    from app.core.security import create_access_token
    
    # 使用access token作为refresh token
    wrong_token = create_access_token(data={"sub": str(test_user.id)})  # 类型是access
    
    response = client.post("/api/v1/auth/refresh", json={
        "refresh_token": wrong_token,
    })
    assert response.status_code == 401
    assert "无效的刷新令牌" in response.json()["detail"]


def test_refresh_token_user_inactive(client, test_user, db_session):
    """测试刷新令牌 - 用户已禁用"""
    from app.core.security import create_refresh_token
    
    # 禁用用户
    test_user.is_active = False
    db_session.commit()
    
    refresh_token = create_refresh_token(data={"sub": str(test_user.id)})
    
    response = client.post("/api/v1/auth/refresh", json={
        "refresh_token": refresh_token,
    })
    assert response.status_code == 401
    assert "用户不存在或已被禁用" in response.json()["detail"]


def test_reset_password_wrong_code(client, test_user):
    """测试重置密码 - 验证码错误"""
    response = client.post("/api/v1/auth/reset_password", json={
        "phone": test_user.phone,
        "code": "wrong",
        "new_password": "Newpass1!",
    })
    assert response.status_code == 400
    assert "验证码错误" in response.json()["detail"]


def test_login_user_not_exists(client):
    """测试登录 - 用户不存在"""
    response = client.post("/api/v1/auth/login", json={
        "phone": "19999999999",
        "password": "Password123!",
    })
    assert response.status_code == 401
    assert "手机号或密码错误" in response.json()["detail"]
