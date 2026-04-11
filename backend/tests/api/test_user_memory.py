"""
用户长期记忆相关接口测试
"""
import pytest


def test_add_memory(authorized_client, test_user):
    """测试添加长期记忆接口"""
    memory_data = {
        "memory_type": "preference",
        "content": "我喜欢绿茶，不喜欢喝咖啡",
        "importance": 3,
        "summary": "用户饮料偏好",
        "keywords": ["绿茶", "咖啡", "偏好"],
        "source": "conversation"
    }
    response = authorized_client.post("/api/v1/user-memory/", json=memory_data)
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == memory_data["content"]
    assert data["memory_type"] == memory_data["memory_type"]
    assert "id" in data


def test_get_memory(authorized_client, test_user):
    """测试获取记忆详情接口"""
    # 创建一条记忆
    create_resp = authorized_client.post("/api/v1/user-memory/", json={
        "memory_type": "fact",
        "content": "用户生日是1995年5月15日",
        "importance": 4,
    })
    memory_id = create_resp.json()["id"]
    
    response = authorized_client.get(f"/api/v1/user-memory/{memory_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == memory_id
    assert data["content"] == "用户生日是1995年5月15日"


def test_get_memory_not_found(authorized_client, test_user):
    """测试获取不存在记忆"""
    response = authorized_client.get("/api/v1/user-memory/99999")
    assert response.status_code == 404


def test_list_memories(authorized_client, test_user):
    """测试获取记忆列表接口"""
    # 创建几条记忆
    for i in range(3):
        authorized_client.post("/api/v1/user-memory/", json={
            "memory_type": "note",
            "content": f"测试记忆{i}",
            "importance": i + 1,
        })
    
    response = authorized_client.get("/api/v1/user-memory/list?page=1&page_size=10&memory_type=note&min_importance=2")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "has_next" in data
    assert "data" in data
    assert isinstance(data["data"], list)


def test_update_memory(authorized_client, test_user):
    """测试更新记忆接口"""
    # 创建记忆
    create_resp = authorized_client.post("/api/v1/user-memory/", json={
        "memory_type": "fact",
        "content": "原始内容",
        "importance": 2,
    })
    memory_id = create_resp.json()["id"]
    
    # 更新记忆
    response = authorized_client.put(f"/api/v1/user-memory/{memory_id}", json={
        "content": "更新后的内容",
        "importance": 4,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "更新后的内容"
    assert data["importance"] == 4


def test_update_memory_not_found(authorized_client, test_user):
    """测试更新不存在记忆"""
    response = authorized_client.put("/api/v1/user-memory/99999", json={
        "content": "测试",
    })
    assert response.status_code == 404


def test_delete_memory(authorized_client, test_user):
    """测试删除记忆接口"""
    # 创建记忆
    create_resp = authorized_client.post("/api/v1/user-memory/", json={
        "memory_type": "temp",
        "content": "要删除的记忆",
        "importance": 1,
    })
    memory_id = create_resp.json()["id"]
    
    # 删除
    response = authorized_client.delete(f"/api/v1/user-memory/{memory_id}")
    assert response.status_code == 200
    assert "message" in response.json()
    
    # 验证删除
    get_resp = authorized_client.get(f"/api/v1/user-memory/{memory_id}")
    assert get_resp.status_code == 404


def test_delete_memory_not_found(authorized_client, test_user):
    """测试删除不存在记忆"""
    response = authorized_client.delete("/api/v1/user-memory/99999")
    assert response.status_code == 404


def test_search_memories(authorized_client, test_user):
    """测试搜索记忆接口"""
    # 创建一条包含特定关键词的记忆
    authorized_client.post("/api/v1/user-memory/", json={
        "memory_type": "preference",
        "content": "我喜欢吃苹果和香蕉",
        "keywords": ["水果", "苹果", "香蕉"],
        "importance": 2,
    })
    
    response = authorized_client.get("/api/v1/user-memory/search?query=苹果&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_memory_stats(authorized_client, test_user):
    """测试获取记忆统计接口"""
    response = authorized_client.get("/api/v1/user-memory/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_count" in data
    assert "by_type" in data
    assert "by_importance" in data


def test_add_insight(authorized_client, test_user):
    """测试添加记忆洞察接口"""
    # 先创建一条记忆
    create_resp = authorized_client.post("/api/v1/user-memory/", json={
        "memory_type": "emotion_pattern",
        "content": "用户每周一情绪较低落",
        "importance": 3,
    })
    memory_id = create_resp.json()["id"]
    
    response = authorized_client.post("/api/v1/user-memory/insights", json={
        "insight_type": "pattern",
        "content": "用户在周一工作压力较大，建议提前做好情绪准备",
        "supporting_memory_ids": [memory_id],
        "confidence": 0.8,
    })
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["insight_type"] == "pattern"


def test_list_insights(authorized_client, test_user):
    """测试获取洞察列表接口"""
    response = authorized_client.get("/api/v1/user-memory/insights")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_set_preference(authorized_client, test_user):
    """测试设置用户偏好接口"""
    response = authorized_client.post("/api/v1/user-memory/preferences", json={
        "category": "chat",
        "key": "response_length",
        "value": "medium",
        "source": "user",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "chat"
    assert data["key"] == "response_length"
    assert data["value"] == "medium"


def test_get_preference(authorized_client, test_user):
    """测试获取用户偏好接口"""
    # 设置偏好
    authorized_client.post("/api/v1/user-memory/preferences", json={
        "category": "ui",
        "key": "theme",
        "value": "dark",
    })
    
    response = authorized_client.get("/api/v1/user-memory/preferences/ui/theme")
    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "ui"
    assert data["key"] == "theme"
    assert data["value"] == "dark"


def test_get_category_preferences(authorized_client, test_user):
    """测试获取分类下所有偏好接口"""
    # 设置多个偏好
    authorized_client.post("/api/v1/user-memory/preferences", json={
        "category": "notification",
        "key": "email",
        "value": "true",
    })
    authorized_client.post("/api/v1/user-memory/preferences", json={
        "category": "notification",
        "key": "push",
        "value": "false",
    })
    
    response = authorized_client.get("/api/v1/user-memory/preferences/notification")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "email" in data
    assert "push" in data


def test_delete_preference(authorized_client, test_user):
    """测试删除用户偏好接口"""
    # 设置偏好
    authorized_client.post("/api/v1/user-memory/preferences", json={
        "category": "temp",
        "key": "test",
        "value": "value",
    })
    
    # 删除偏好
    response = authorized_client.delete("/api/v1/user-memory/preferences/temp/test")
    assert response.status_code == 200


def test_delete_preference_not_found(authorized_client, test_user):
    """测试删除不存在偏好"""
    response = authorized_client.delete("/api/v1/user-memory/preferences/nonexistent/key")
    assert response.status_code == 404


def test_get_relevant_memories(authorized_client, test_user):
    """测试获取相关记忆接口"""
    # 创建一条记忆
    authorized_client.post("/api/v1/user-memory/", json={
        "memory_type": "preference",
        "content": "用户喜欢谈论旅行相关话题",
        "importance": 3,
    })
    
    response = authorized_client.get("/api/v1/user-memory/relevant?context=我想去旅行&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_unauthorized_access(client):
    """测试未授权访问"""
    response = client.get("/api/v1/user-memory/list")
    assert response.status_code == 401
    
    response = client.post("/api/v1/user-memory/", json={
        "memory_type": "test",
        "content": "测试",
    })
    assert response.status_code == 401
