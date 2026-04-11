"""
冒烟测试用例 - 上线前执行
"""
import pytest
import subprocess
import time


def test_system_health():
    """测试系统健康状态"""
    print("=== 冒烟测试: 系统健康检查 ===")
    
    # 测试后端服务是否启动
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    print("✓ 后端服务正常")
    
    # 测试数据库连接
    from app.core.database import SessionLocal
    db = SessionLocal()
    result = db.execute("SELECT 1")
    assert result.scalar() == 1
    db.close()
    print("✓ 数据库连接正常")
    
    # 测试Redis连接
    import redis
    from app.core.config import settings
    r = redis.Redis.from_url(settings.REDIS_URL)
    assert r.ping() == True
    print("✓ Redis连接正常")
    
    # 测试LLM服务连接
    from app.services.llm_service import get_llm_response
    response = get_llm_response("你好", [], "INTJ")
    assert response != ""
    print("✓ LLM服务正常")


def test_core_functionality():
    """测试核心功能"""
    print("\n=== 冒烟测试: 核心功能 ===")
    
    # 1. 用户注册登录
    print("测试用户注册登录...")
    # 发送验证码
    response = client.post(
        "/api/v1/auth/send-code",
        json={"phone": "13900000001"}
    )
    assert response.status_code == 200
    
    # 注册
    with patch("app.services.auth_service.verify_verification_code") as mock_verify:
        mock_verify.return_value = True
        response = client.post(
            "/api/v1/auth/register",
            json={
                "phone": "13900000001",
                "code": "123456",
                "password": "Test@123456",
                "nickname": "冒烟测试用户"
            }
        )
        assert response.status_code == 200
        assert "access_token" in response.json()["data"]
        token = response.json()["data"]["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    print("✓ 用户注册登录正常")
    
    # 2. 获取助手列表
    print("测试获取助手列表...")
    response = client.get("/api/v1/chat/assistants", headers=headers)
    assert response.status_code == 200
    assert len(response.json()["data"]) > 0
    assistant_id = response.json()["data"][0]["id"]
    print("✓ 助手列表获取正常")
    
    # 3. 创建会话
    print("测试创建会话...")
    response = client.post(
        "/api/v1/chat/conversations",
        json={"assistant_id": assistant_id, "title": "冒烟测试会话"},
        headers=headers
    )
    assert response.status_code == 200
    conversation_id = response.json()["data"]["id"]
    print("✓ 会话创建正常")
    
    # 4. 发送消息
    print("测试发送消息...")
    response = client.post(
        f"/api/v1/chat/conversations/{conversation_id}/messages",
        json={"content": "你好，我最近心情不好"},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["data"]["content"] != ""
    print("✓ 聊天功能正常")
    
    # 5. MBTI测试
    print("测试MBTI功能...")
    response = client.get("/api/v1/mbti/questions", headers=headers)
    assert response.status_code == 200
    assert len(response.json()["data"]) > 0
    print("✓ MBTI测试功能正常")
    
    # 6. 个人信息管理
    print("测试个人信息管理...")
    response = client.get("/api/v1/auth/profile", headers=headers)
    assert response.status_code == 200
    assert response.json()["data"]["phone"] == "13900000001"
    
    # 更新信息
    response = client.put(
        "/api/v1/auth/profile",
        json={"nickname": "更新后的昵称"},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["data"]["nickname"] == "更新后的昵称"
    print("✓ 个人信息管理正常")


def test_api_performance_smoke():
    """API性能冒烟测试"""
    print("\n=== 冒烟测试: API性能 ===")
    
    # 测试健康检查接口性能
    start_time = time.time()
    for _ in range(100):
        response = client.get("/health")
        assert response.status_code == 200
    total_time = time.time() - start_time
    avg_time = total_time / 100 * 1000
    print(f"健康检查接口平均响应时间: {avg_time:.2f}ms")
    assert avg_time < 50, "健康检查接口响应时间超过50ms"
    
    # 测试登录接口性能
    start_time = time.time()
    for _ in range(10):
        response = client.post(
            "/api/v1/auth/login",
            json={
                "phone": "13900000001",
                "password": "Test@123456"
            }
        )
        assert response.status_code == 200
    total_time = time.time() - start_time
    avg_time = total_time / 10 * 1000
    print(f"登录接口平均响应时间: {avg_time:.2f}ms")
    assert avg_time < 200, "登录接口响应时间超过200ms"
    
    # 测试聊天接口性能
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "phone": "13900000001",
            "password": "Test@123456"
        }
    )
    token = login_response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 创建会话
    conv_response = client.post(
        "/api/v1/chat/conversations",
        json={"assistant_id": 1, "title": "性能测试会话"},
        headers=headers
    )
    conversation_id = conv_response.json()["data"]["id"]
    
    start_time = time.time()
    response = client.post(
        f"/api/v1/chat/conversations/{conversation_id}/messages",
        json={"content": "你好"},
        headers=headers
    )
    assert response.status_code == 200
    response_time = (time.time() - start_time) * 1000
    print(f"聊天接口响应时间: {response_time:.2f}ms")
    assert response_time < 3000, "聊天接口响应时间超过3秒"


def test_security_smoke():
    """安全性冒烟测试"""
    print("\n=== 冒烟测试: 安全性 ===")
    
    # 测试未授权访问
    print("测试未授权访问...")
    response = client.get("/api/v1/auth/profile")
    assert response.status_code == 401
    print("✓ 未授权访问拦截正常")
    
    # 测试SQL注入防护
    print("测试SQL注入防护...")
    response = client.post(
        "/api/v1/auth/login",
        json={
            "phone": "' OR 1=1 --",
            "password": "anypassword"
        }
    )
    assert response.status_code in [401, 404, 422]  # 不返回200即可
    print("✓ SQL注入防护正常")
    
    # 测试XSS防护
    print("测试XSS防护...")
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "phone": "13900000001",
            "password": "Test@123456"
        }
    )
    token = login_response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 更新昵称包含XSS代码
    response = client.put(
        "/api/v1/auth/profile",
        json={"nickname": "<script>alert('xss')</script>"},
        headers=headers
    )
    assert response.status_code == 200
    # 获取个人信息，验证XSS代码被转义
    profile_response = client.get("/api/v1/auth/profile", headers=headers)
    assert "<script>" not in profile_response.text, "XSS代码未被转义"
    print("✓ XSS防护正常")
    
    # 测试内容安全过滤
    print("测试内容安全过滤...")
    conv_response = client.post(
        "/api/v1/chat/conversations",
        json={"assistant_id": 1, "title": "测试会话"},
        headers=headers
    )
    conversation_id = conv_response.json()["data"]["id"]
    
    response = client.post(
        f"/api/v1/chat/conversations/{conversation_id}/messages",
        json={"content": "我想自杀"},
        headers=headers
    )
    assert response.status_code == 400
    assert response.json()["code"] == "CONTENT_VIOLATION"
    print("✓ 内容安全过滤正常")


def test_error_handling():
    """错误处理冒烟测试"""
    print("\n=== 冒烟测试: 错误处理 ===")
    
    # 测试404错误
    response = client.get("/api/v1/nonexistent-endpoint")
    assert response.status_code == 404
    assert response.json()["success"] == False
    assert "code" in response.json()
    print("✓ 404错误处理正常")
    
    # 测试参数校验错误
    response = client.post(
        "/api/v1/auth/send-code",
        json={"phone": "invalid-phone-number"}
    )
    assert response.status_code == 422
    assert "detail" in response.json()
    print("✓ 参数校验错误处理正常")
    
    # 测试业务错误
    response = client.post(
        "/api/v1/auth/login",
        json={
            "phone": "13900000001",
            "password": "wrong-password"
        }
    )
    assert response.status_code == 401
    assert response.json()["code"] == "INVALID_CREDENTIALS"
    print("✓ 业务错误处理正常")


def main():
    """冒烟测试主函数"""
    print("🚀 开始执行上线前冒烟测试...")
    print("=" * 60)
    
    try:
        test_system_health()
        test_core_functionality()
        test_api_performance_smoke()
        test_security_smoke()
        test_error_handling()
        
        print("\n" + "=" * 60)
        print("✅ 所有冒烟测试用例通过！系统可以上线！")
        return 0
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ 冒烟测试失败: {e}")
        print("系统不满足上线条件，请修复问题后重新测试！")
        return 1


if __name__ == "__main__":
    exit(main())
