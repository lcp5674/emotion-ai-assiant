"""
情感日记相关接口测试
"""
import pytest


def test_create_diary(authorized_client, test_user):
    """测试创建日记接口"""
    diary_data = {
        "title": "今天心情不错",
        "content": "今天发生了很多开心的事情，工作顺利，和朋友聚会很愉快。",
        "mood_level": 4,
        "emotion": "happy",
        "category": "daily",
        "tags": ["开心", "朋友", "工作"],
        "is_private": False,
    }
    response = authorized_client.post("/api/v1/diary/create", json=diary_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == diary_data["title"]
    assert data["content"] == diary_data["content"]
    assert "id" in data


def test_get_diary(authorized_client, test_user):
    """测试获取日记详情接口"""
    # 创建日记
    create_resp = authorized_client.post("/api/v1/diary/create", json={
        "title": "测试日记",
        "content": "这是测试日记内容",
        "mood_level": 3,
    })
    diary_id = create_resp.json()["id"]
    
    # 获取详情
    response = authorized_client.get(f"/api/v1/diary/{diary_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == diary_id
    assert data["title"] == "测试日记"


def test_get_diary_not_found(authorized_client):
    """测试获取不存在日记"""
    response = authorized_client.get("/api/v1/diary/99999")
    assert response.status_code == 404


def test_get_diary_by_date(authorized_client, test_user):
    """测试根据日期获取日记接口"""
    from datetime import date
    today = date.today().strftime("%Y-%m-%d")
    
    # 创建今天的日记
    authorized_client.post("/api/v1/diary/create", json={
        "title": "今日日记",
        "content": "今天的内容",
        "mood_level": 4,
    })
    
    response = authorized_client.get(f"/api/v1/diary/date/{today}")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["title"] == "今日日记"


def test_get_diary_by_date_invalid_format(authorized_client):
    """测试日期格式错误"""
    response = authorized_client.get("/api/v1/diary/date/2024/01/01")
    assert response.status_code == 400


def test_list_diaries(authorized_client, test_user):
    """测试获取日记列表接口"""
    # 创建几条日记
    for i in range(3):
        authorized_client.post("/api/v1/diary/create", json={
            "title": f"日记{i}",
            "content": f"内容{i}",
            "mood_level": i + 1,
        })
    
    response = authorized_client.get("/api/v1/diary/list?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "has_next" in data
    assert "data" in data
    assert len(data["data"]) >= 3


def test_list_diaries_with_filter(authorized_client, test_user):
    """测试筛选日记列表"""
    response = authorized_client.get(
        "/api/v1/diary/list?page=1&page_size=10&mood_level=3&emotion=happy"
    )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_update_diary(authorized_client, test_user):
    """测试更新日记接口"""
    # 创建日记
    create_resp = authorized_client.post("/api/v1/diary/create", json={
        "title": "原标题",
        "content": "原内容",
        "mood_level": 2,
    })
    diary_id = create_resp.json()["id"]
    
    # 更新日记
    update_data = {
        "title": "更新后标题",
        "content": "更新后内容",
        "mood_level": 4,
    }
    response = authorized_client.put(f"/api/v1/diary/{diary_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "更新后标题"
    assert data["content"] == "更新后内容"
    assert data["mood_level"] == 4


def test_update_diary_not_found(authorized_client, test_user):
    """测试更新不存在日记"""
    response = authorized_client.put("/api/v1/diary/99999", json={
        "title": "测试",
        "content": "测试",
    })
    assert response.status_code == 404


def test_delete_diary(authorized_client, test_user):
    """测试删除日记接口"""
    # 创建日记
    create_resp = authorized_client.post("/api/v1/diary/create", json={
        "title": "要删除的日记",
        "content": "删除内容",
        "mood_level": 1,
    })
    diary_id = create_resp.json()["id"]
    
    # 删除
    response = authorized_client.delete(f"/api/v1/diary/{diary_id}")
    assert response.status_code == 200
    assert "message" in response.json()
    
    # 验证删除
    get_resp = authorized_client.get(f"/api/v1/diary/{diary_id}")
    assert get_resp.status_code == 404


def test_delete_diary_not_found(authorized_client, test_user):
    """测试删除不存在日记"""
    response = authorized_client.delete("/api/v1/diary/99999")
    assert response.status_code == 404


def test_create_mood_record(authorized_client, test_user):
    """测试快速记录心情接口"""
    response = authorized_client.post("/api/v1/diary/mood", json={
        "mood_level": 4,
        "note": "今天心情很好",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["mood_level"] == 4
    assert data["note"] == "今天心情很好"


def test_list_mood_records(authorized_client, test_user):
    """测试获取心情记录列表接口"""
    # 创建几条心情记录
    for i in range(3):
        authorized_client.post("/api/v1/diary/mood", json={
            "mood_level": i + 1,
        })
    
    response = authorized_client.get("/api/v1/diary/mood/list?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3


def test_list_mood_records_invalid_date(authorized_client):
    """测试无效日期格式"""
    response = authorized_client.get("/api/v1/diary/mood/list?start_date=2024/01/01")
    assert response.status_code == 400


def test_create_tag(authorized_client, test_user):
    """测试创建标签接口"""
    response = authorized_client.post("/api/v1/diary/tags", json={
        "name": "工作",
        "color": "#ff0000",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "工作"
    assert data["color"] == "#ff0000"
    assert "id" in data


def test_list_tags(authorized_client, test_user):
    """测试获取标签列表接口"""
    # 创建标签
    authorized_client.post("/api/v1/diary/tags", json={
        "name": "生活",
        "color": "#00ff00",
    })
    
    response = authorized_client.get("/api/v1/diary/tags")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_update_tag(authorized_client, test_user):
    """测试更新标签接口"""
    # 创建标签
    create_resp = authorized_client.post("/api/v1/diary/tags", json={
        "name": "原标签",
        "color": "#000000",
    })
    tag_id = create_resp.json()["id"]
    
    # 更新标签
    response = authorized_client.put(f"/api/v1/diary/tags/{tag_id}", json={
        "name": "更新后标签",
        "color": "#ffffff",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "更新后标签"
    assert data["color"] == "#ffffff"


def test_delete_tag(authorized_client, test_user):
    """测试删除标签接口"""
    # 创建标签
    create_resp = authorized_client.post("/api/v1/diary/tags", json={
        "name": "要删除的标签",
        "color": "#cccccc",
    })
    tag_id = create_resp.json()["id"]
    
    # 删除
    response = authorized_client.delete(f"/api/v1/diary/tags/{tag_id}")
    assert response.status_code == 200


def test_get_stats(authorized_client, test_user):
    """测试获取日记统计接口"""
    # 创建一条日记确保有数据
    authorized_client.post("/api/v1/diary/create", json={
        "title": "统计测试",
        "content": "统计测试内容",
        "mood_level": 3,
    })
    
    response = authorized_client.get("/api/v1/diary/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_count" in data
    assert "current_streak" in data
    assert "max_streak" in data
    assert "avg_mood" in data
    assert "most_common_emotion" in data


def test_get_mood_trend(authorized_client, test_user):
    """测试获取心情趋势接口"""
    response = authorized_client.get("/api/v1/diary/trend?time_range=week")
    assert response.status_code == 200
    data = response.json()
    assert "time_range" in data
    assert "start_date" in data
    assert "end_date" in data
    assert "avg_score" in data
    assert "trend_data" in data


def test_get_mood_trend_invalid_range(authorized_client):
    """测试无效时间范围"""
    response = authorized_client.get("/api/v1/diary/trend?time_range=invalid")
    assert response.status_code == 400


def test_analyze_diary(authorized_client, test_user):
    """测试AI分析日记接口"""
    # 创建日记
    create_resp = authorized_client.post("/api/v1/diary/create", json={
        "title": "分析测试",
        "content": "今天我感到有些焦虑，因为工作压力很大，但是晚上和朋友聊天后感觉好多了。",
        "mood_level": 3,
    })
    diary_id = create_resp.json()["id"]
    
    response = authorized_client.post(f"/api/v1/diary/analyze/{diary_id}")
    # 即使LLM不可用，测试接口存在性
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        data = response.json()
        assert "status" in data


def test_analyze_diary_not_found(authorized_client, test_user):
    """测试分析不存在日记"""
    response = authorized_client.post("/api/v1/diary/analyze/99999")
    assert response.status_code == 404


def test_get_emotion_config(authorized_client):
    """测试获取情绪配置接口"""
    response = authorized_client.get("/api/v1/diary/emotion-config")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_get_mood_config(authorized_client):
    """测试获取心情配置接口"""
    response = authorized_client.get("/api/v1/diary/mood-config")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_generate_mood_trend_share_image(authorized_client, test_user):
    """测试生成情绪趋势分享图片接口"""
    response = authorized_client.get("/api/v1/diary/trend/share-image?time_range=week")
    assert response.status_code == 200
    data = response.json()
    assert "username" in data
    assert "time_range" in data
    assert "avg_score" in data


def test_get_privacy_policy(client):
    """测试获取隐私政策接口 - 公开访问"""
    response = client.get("/api/v1/diary/privacy-policy")
    assert response.status_code == 200
    data = response.json()
    assert "title" in data
    assert "content" in data


def test_get_terms_of_service(client):
    """测试获取用户服务条款接口 - 公开访问"""
    response = client.get("/api/v1/diary/terms-of-service")
    assert response.status_code == 200
    data = response.json()
    assert "title" in data


def test_unauthorized_access(client):
    """测试未授权访问"""
    response = client.post("/api/v1/diary/create", json={
        "title": "测试",
        "content": "测试",
        "mood_level": 3,
    })
    assert response.status_code == 401
    
    response = client.get("/api/v1/diary/list")
    assert response.status_code == 401
