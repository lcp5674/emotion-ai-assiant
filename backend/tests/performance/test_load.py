"""
性能测试脚本
"""
import pytest
import asyncio
import time
from httpx import AsyncClient
import statistics


@pytest.mark.asyncio
async def test_api_concurrent_performance():
    """测试API并发性能"""
    async with AsyncClient(base_url="http://localhost:8000") as client:
        # 先登录获取token
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "phone": "13800138000",
                "password": "Test@123456"
            }
        )
        token = login_response.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 测试并发数
        concurrent_users = [10, 50, 100, 200]
        test_duration = 60  # 每个并发级别测试60秒
        
        for users in concurrent_users:
            print(f"\n=== 测试 {users} 并发用户 ===")
            
            start_time = time.time()
            tasks = []
            
            async def make_request():
                """发送单个请求"""
                try:
                    req_start = time.time()
                    response = await client.get("/api/v1/chat/assistants", headers=headers)
                    req_time = time.time() - req_start
                    return (response.status_code, req_time)
                except Exception as e:
                    return (500, time.time() - req_start)
            
            # 创建并发任务
            for _ in range(users):
                tasks.append(asyncio.create_task(make_request()))
            
            # 等待所有任务完成
            results = await asyncio.gather(*tasks)
            
            total_time = time.time() - start_time
            
            # 统计结果
            success_count = sum(1 for status, _ in results if status == 200)
            error_count = len(results) - success_count
            response_times = [rt for _, rt in results]
            
            print(f"总请求数: {len(results)}")
            print(f"成功请求: {success_count}")
            print(f"失败请求: {error_count}")
            print(f"成功率: {success_count / len(results) * 100:.2f}%")
            print(f"总耗时: {total_time:.2f}s")
            print(f"QPS: {len(results) / total_time:.2f}")
            print(f"平均响应时间: {statistics.mean(response_times) * 1000:.2f}ms")
            print(f"中位数响应时间: {statistics.median(response_times) * 1000:.2f}ms")
            print(f"95分位响应时间: {statistics.quantiles(response_times, n=20)[18] * 1000:.2f}ms")
            print(f"99分位响应时间: {statistics.quantiles(response_times, n=100)[98] * 1000:.2f}ms")
            print(f"最大响应时间: {max(response_times) * 1000:.2f}ms")
            print(f"最小响应时间: {min(response_times) * 1000:.2f}ms")
            
            # 性能断言
            assert success_count / len(results) >= 0.99, f"成功率低于99%，当前: {success_count / len(results) * 100:.2f}%"
            assert statistics.mean(response_times) <= 0.5, f"平均响应时间超过500ms，当前: {statistics.mean(response_times) * 1000:.2f}ms"
            assert statistics.quantiles(response_times, n=100)[98] <= 2, f"99分位响应时间超过2s，当前: {statistics.quantiles(response_times, n=100)[98] * 1000:.2f}ms"


@pytest.mark.asyncio
async def test_chat_api_performance():
    """测试聊天接口性能"""
    async with AsyncClient(base_url="http://localhost:8000") as client:
        # 登录
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "phone": "13800138000",
                "password": "Test@123456"
            }
        )
        token = login_response.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 创建会话
        conv_response = await client.post(
            "/api/v1/chat/conversations",
            json={"assistant_id": 1, "title": "性能测试会话"},
            headers=headers
        )
        conversation_id = conv_response.json()["data"]["id"]
        
        # 测试聊天接口性能
        print("\n=== 测试聊天接口性能 ===")
        
        # 预热
        for _ in range(5):
            await client.post(
                f"/api/v1/chat/conversations/{conversation_id}/messages",
                json={"content": "你好"},
                headers=headers
            )
        
        # 正式测试
        test_cases = [
            {"content": "我今天心情不好", "expected_response_time": 2.0},
            {"content": "可以给我一些建议吗？", "expected_response_time": 2.0},
            {"content": "你觉得我应该怎么做？", "expected_response_time": 2.0},
        ]
        
        for test_case in test_cases:
            start_time = time.time()
            response = await client.post(
                f"/api/v1/chat/conversations/{conversation_id}/messages",
                json={"content": test_case["content"]},
                headers=headers
            )
            response_time = time.time() - start_time
            
            print(f"消息: '{test_case['content']}'")
            print(f"响应时间: {response_time * 1000:.2f}ms")
            print(f"响应状态: {response.status_code}")
            
            assert response.status_code == 200
            assert response_time <= test_case["expected_response_time"], f"响应时间超过预期，当前: {response_time * 1000:.2f}ms，预期: {test_case['expected_response_time'] * 1000:.2f}ms"


def test_database_performance(db_session):
    """测试数据库性能"""
    from app.models.user import User
    from app.services.auth_service import get_password_hash
    
    print("\n=== 测试数据库性能 ===")
    
    # 测试批量插入
    start_time = time.time()
    users = []
    for i in range(1000):
        user = User(
            phone=f"1380000{i:04d}",
            email=f"test{i}@example.com",
            nickname=f"测试用户{i}",
            hashed_password=get_password_hash("Test@123456")
        )
        users.append(user)
    
    db_session.add_all(users)
    db_session.commit()
    insert_time = time.time() - start_time
    print(f"插入1000条用户数据耗时: {insert_time:.2f}s，平均每条: {insert_time / 1000 * 1000:.2f}ms")
    
    # 测试查询性能
    start_time = time.time()
    result = db_session.query(User).filter(User.phone.like("1380000%")).all()
    query_time = time.time() - start_time
    print(f"查询1000条用户数据耗时: {query_time:.2f}s")
    
    # 性能断言
    assert insert_time <= 2.0, "插入1000条数据耗时超过2秒"
    assert query_time <= 0.1, "查询1000条数据耗时超过100毫秒"


def test_redis_performance():
    """测试Redis性能"""
    import redis
    from app.core.config import settings
    
    r = redis.Redis.from_url(settings.REDIS_URL)
    
    print("\n=== 测试Redis性能 ===")
    
    # 测试写入性能
    start_time = time.time()
    for i in range(10000):
        r.set(f"test:key:{i}", f"value:{i}", ex=3600)
    write_time = time.time() - start_time
    print(f"写入10000条KV耗时: {write_time:.2f}s，QPS: {10000 / write_time:.2f}")
    
    # 测试读取性能
    start_time = time.time()
    for i in range(10000):
        r.get(f"test:key:{i}")
    read_time = time.time() - start_time
    print(f"读取10000条KV耗时: {read_time:.2f}s，QPS: {10000 / read_time:.2f}")
    
    # 清理测试数据
    for i in range(10000):
        r.delete(f"test:key:{i}")
    
    # 性能断言
    assert 10000 / write_time >= 5000, "Redis写入QPS低于5000"
    assert 10000 / read_time >= 10000, "Redis读取QPS低于10000"


@pytest.mark.asyncio
async def test_system_stability():
    """测试系统长时间运行稳定性"""
    print("\n=== 测试系统稳定性（10分钟） ===")
    
    async with AsyncClient(base_url="http://localhost:8000") as client:
        # 登录
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "phone": "13800138000",
                "password": "Test@123456"
            }
        )
        token = login_response.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        start_time = time.time()
        duration = 10 * 60  # 10分钟
        request_count = 0
        error_count = 0
        
        while time.time() - start_time < duration:
            try:
                # 混合请求
                await client.get("/health")
                await client.get("/api/v1/chat/assistants", headers=headers)
                await client.get("/api/v1/auth/profile", headers=headers)
                
                request_count += 3
                
                # 每秒发送3个请求
                await asyncio.sleep(1)
            except Exception as e:
                error_count += 1
                print(f"请求错误: {e}")
        
        total_time = time.time() - start_time
        print(f"总运行时间: {total_time:.2f}s")
        print(f"总请求数: {request_count}")
        print(f"错误数: {error_count}")
        print(f"错误率: {error_count / request_count * 100:.4f}%")
        print(f"平均QPS: {request_count / total_time:.2f}")
        
        # 稳定性断言
        assert error_count / request_count <= 0.001, "错误率超过0.1%"
