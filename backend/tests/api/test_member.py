"""
会员相关接口测试
"""
import pytest


def test_get_member_prices(authorized_client, test_user):
    """测试获取会员价格列表接口"""
    response = authorized_client.get("/api/v1/member/prices")
    assert response.status_code == 200
    data = response.json()
    assert "list" in data
    assert isinstance(data["list"], list)
    if len(data["list"]) > 0:
        plan = data["list"][0]
        assert "level" in plan
        assert "name" in plan
        assert "price" in plan
        assert "duration" in plan
        assert "features" in plan


def test_create_order(authorized_client, test_user):
    """测试创建会员订单接口"""
    # 使用有效的会员等级
    response = authorized_client.post("/api/v1/member/order", json={
        "level": "vip"
    })
    assert response.status_code == 200
    data = response.json()
    assert "order_no" in data
    assert "amount" in data
    assert "pay_url" in data


def test_create_order_invalid_level(authorized_client, test_user):
    """测试创建会员订单使用无效等级"""
    response = authorized_client.post("/api/v1/member/order", json={
        "level": "invalid"
    })
    assert response.status_code == 400


def test_pay_order(authorized_client, test_user, db_session):
    """测试支付订单接口"""
    from app.models.user import MemberOrder
    # 创建一个订单
    import uuid
    from datetime import datetime
    order_no = f"TEST{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8]}"
    order = MemberOrder(
        user_id=test_user.id,
        order_no=order_no,
        level="vip",
        amount=2900,
        duration=30,
        status="pending"
    )
    db_session.add(order)
    db_session.commit()
    
    response = authorized_client.post(f"/api/v1/member/order/{order_no}/pay")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "member_level" in data
    
    # 测试已支付订单重复支付
    response = authorized_client.post(f"/api/v1/member/order/{order_no}/pay")
    assert response.status_code == 400


def test_pay_order_not_found(authorized_client, test_user):
    """测试支付不存在的订单"""
    response = authorized_client.post("/api/v1/member/order/NONEXIST/pay")
    assert response.status_code == 404


def test_get_member_status(authorized_client, test_user):
    """测试获取会员状态接口"""
    response = authorized_client.get("/api/v1/member/status")
    assert response.status_code == 200
    data = response.json()
    assert "level" in data
    assert "expire_at" in data
    assert "is_expired" in data


def test_get_member_plans(authorized_client, test_user):
    """测试获取会员套餐列表接口"""
    response = authorized_client.get("/api/v1/member/plans")
    assert response.status_code == 200
    assert response.json()["success"] == True
    data = response.json()["data"]
    assert isinstance(data, list)
    if len(data) > 0:
        plan = data[0]
        assert "id" in plan
        assert "name" in plan
        assert "price" in plan
        assert "duration_days" in plan
        assert "features" in plan


def test_get_current_member_info(authorized_client, test_user):
    """测试获取当前会员信息接口"""
    response = authorized_client.get("/api/v1/member/current")
    assert response.status_code == 200
    assert response.json()["success"] == True
    data = response.json()["data"]
    assert "is_member" in data
    assert "level" in data
    assert "expire_at" in data


def test_check_member_status(authorized_client, test_user):
    """测试检查会员状态接口"""
    response = authorized_client.get("/api/v1/member/status")
    assert response.status_code == 200
    assert response.json()["success"] == True
    data = response.json()["data"]
    assert "is_active" in data
    assert "remaining_days" in data


def test_get_member_benefits(authorized_client, test_user):
    """测试获取会员权益接口"""
    response = authorized_client.get("/api/v1/member/benefits")
    assert response.status_code == 200
    assert response.json()["success"] == True
    data = response.json()["data"]
    assert isinstance(data, list)


def test_unauthorized_access(client):
    """测试未授权访问"""
    response = client.get("/api/v1/member/prices")
    assert response.status_code == 200
    
    response = client.post("/api/v1/member/order", json={"level": "vip"})
    assert response.status_code == 401
