"""
成长体系相关接口测试
"""
import pytest


def test_get_all_badges(authorized_client, test_user):
    """测试获取所有徽章信息接口"""
    response = authorized_client.get("/api/v1/growth/badges")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_user_badges(authorized_client, test_user):
    """测试获取用户已获得徽章接口"""
    response = authorized_client.get("/api/v1/growth/badges/user")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_badge_progress(authorized_client, test_user):
    """测试获取徽章解锁进度接口"""
    response = authorized_client.get("/api/v1/growth/badges/progress")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "unlocked_count" in data


def test_set_badge_display(authorized_client, test_user, db_session):
    """测试设置徽章展示接口"""
    from app.models.growth import Badge, UserBadge
    # 创建一个徽章
    badge = Badge(
        badge_code="test_badge",
        name="测试徽章",
        description="测试徽章描述",
        rarity="common",
        category="test"
    )
    db_session.add(badge)
    db_session.commit()
    
    # 用户获得这个徽章
    user_badge = UserBadge(
        user_id=test_user.id,
        badge_id=badge.id,
        is_displayed=False
    )
    db_session.add(user_badge)
    db_session.commit()
    
    # 设置展示
    response = authorized_client.post(
        f"/api/v1/growth/badges/{badge.id}/display",
        json={"is_displayed": True, "display_note": "这是我的测试徽章"}
    )
    assert response.status_code == 200
    assert "message" in response.json()


def test_set_badge_display_not_found(authorized_client, test_user):
    """测试设置不存在徽章展示"""
    response = authorized_client.post(
        "/api/v1/growth/badges/99999/display",
        json={"is_displayed": True}
    )
    assert response.status_code == 404


def test_get_user_level(authorized_client, test_user):
    """测试获取用户等级信息接口"""
    response = authorized_client.get("/api/v1/growth/level")
    assert response.status_code == 200
    data = response.json()
    assert "current_level" in data
    assert "current_exp" in data
    assert "exp_to_next" in data


def test_get_exp_records(authorized_client, test_user):
    """测试获取经验获取记录接口"""
    response = authorized_client.get("/api/v1/growth/exp/records?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_growth_tasks(authorized_client, test_user):
    """测试获取成长任务列表接口"""
    response = authorized_client.get("/api/v1/growth/tasks?include_completed=false")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_claim_task_reward_not_found(authorized_client, test_user):
    """测试领取不存在任务奖励"""
    response = authorized_client.post("/api/v1/growth/tasks/99999/claim")
    assert response.status_code == 404


def test_get_growth_overview(authorized_client, test_user):
    """测试获取成长概览接口"""
    response = authorized_client.get("/api/v1/growth/overview")
    assert response.status_code == 200
    data = response.json()
    assert "level" in data
    assert "badges" in data
    assert "pending_tasks" in data


def test_unauthorized_access(client):
    """测试未授权访问"""
    response = client.get("/api/v1/growth/badges")
    assert response.status_code == 401
    
    response = client.get("/api/v1/growth/level")
    assert response.status_code == 401
