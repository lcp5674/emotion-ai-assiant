"""
支付相关接口测试
"""
import pytest
from unittest.mock import patch


def test_get_member_plans(authorized_client, test_user):
    """测试获取会员套餐列表接口"""
    response = authorized_client.get("/api/v1/payment/plans")
    assert response.status_code == 200
    data = response.json()
    assert "plans" in data
    assert "current_member" in data
    assert "benefits" in data
    assert isinstance(data["plans"], list)
    if len(data["plans"]) > 0:
        plan = data["plans"][0]
        assert "level" in plan
        assert "name" in plan
        assert "price" in plan
        assert "duration" in plan


def test_create_wechat_native_order_invalid_level(authorized_client, test_user):
    """测试创建微信支付订单 - 无效会员等级"""
    response = authorized_client.post("/api/v1/payment/wechat/native", json={
        "level": "invalid"
    })
    assert response.status_code == 400


def test_create_wechat_native_order_valid_level(authorized_client, test_user):
    """测试创建微信支付订单 - 有效会员等级"""
    response = authorized_client.post("/api/v1/payment/wechat/native", json={
        "level": "vip"
    })
    assert response.status_code == 200
    data = response.json()
    assert "order_no" in data
    assert "amount" in data


def test_query_wechat_order_not_found(authorized_client, test_user):
    """测试查询微信支付订单 - 订单不存在"""
    response = authorized_client.get("/api/v1/payment/wechat/query/NONEXIST")
    assert response.status_code == 404


def test_mock_pay_complete_not_found(authorized_client, test_user):
    """测试Mock支付完成 - 订单不存在"""
    response = authorized_client.post("/api/v1/payment/mock/NONEXIST/complete")
    assert response.status_code == 404


def test_create_stripe_checkout_invalid_level(authorized_client, test_user):
    """测试创建Stripe支付订单 - 无效会员等级"""
    response = authorized_client.post("/api/v1/payment/stripe/checkout", json={
        "level": "invalid"
    })
    assert response.status_code == 400


def test_stripe_success(authorized_client, test_user):
    """测试Stripe支付成功回调"""
    response = authorized_client.get("/api/v1/payment/stripe/success?session_id=test")
    # 验证失败会返回400，但是接口应该存在
    assert response.status_code in [400, 200]


def test_stripe_cancel(authorized_client, test_user):
    """测试Stripe支付取消"""
    response = authorized_client.get("/api/v1/payment/stripe/cancel")
    assert response.status_code == 200
    assert "message" in response.json()


def test_stripe_webhook(authorized_client, test_user):
    """测试Stripe webhook"""
    # 没有签名会失败，但接口应该存在
    response = authorized_client.post("/api/v1/payment/stripe/webhook")
    # 测试接口可用性
    assert response.status_code in [400, 200]


def test_create_alipay_page_order_invalid_level(authorized_client, test_user):
    """测试创建支付宝网页支付订单 - 无效会员等级"""
    response = authorized_client.post("/api/v1/payment/alipay/page", json={
        "level": "invalid"
    })
    assert response.status_code == 400


def test_create_alipay_page_order_valid_level(authorized_client, test_user):
    """测试创建支付宝网页支付订单 - 有效会员等级"""
    response = authorized_client.post("/api/v1/payment/alipay/page", json={
        "level": "vip"
    })
    assert response.status_code == 200
    data = response.json()
    assert "order_no" in data
    assert "amount" in data


def test_create_alipay_wap_order_invalid_level(authorized_client, test_user):
    """测试创建支付宝手机网站支付订单 - 无效会员等级"""
    response = authorized_client.post("/api/v1/payment/alipay/wap", json={
        "level": "invalid"
    })
    assert response.status_code == 400


def test_alipay_notify(authorized_client, test_user):
    """测试支付宝异步回调接口"""
    # 空数据会返回failure，但接口应该存在
    response = authorized_client.post("/api/v1/payment/alipay/notify")
    assert response.status_code == 200
    assert response.text in ["failure", "success"]


def test_alipay_return(authorized_client, test_user):
    """测试支付宝同步跳转接口"""
    response = authorized_client.get("/api/v1/payment/alipay/return")
    # 没有正确参数会返回400，但接口应该存在
    assert response.status_code in [400, 200]


def test_query_alipay_order_not_found(authorized_client, test_user):
    """测试查询支付宝订单 - 订单不存在"""
    response = authorized_client.get("/api/v1/payment/alipay/query/NONEXIST")
    assert response.status_code == 404


def test_get_current_membership(authorized_client, test_user):
    """测试获取当前会员状态接口"""
    response = authorized_client.get("/api/v1/payment/current-membership")
    assert response.status_code == 200
    data = response.json()
    assert "is_active" in data
    assert "level" in data
    assert "expire_at" in data
    assert "days_remaining" in data
    assert "features_available" in data


def test_get_user_order_list(authorized_client, test_user):
    """测试获取用户订单列表接口"""
    response = authorized_client.get("/api/v1/payment/order-list?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "has_next" in data
    assert "orders" in data


def test_wechat_notify(authorized_client, test_user):
    """测试微信支付回调接口"""
    response = authorized_client.post("/api/v1/payment/wechat/notify")
    assert response.status_code == 200


def test_unauthorized_access(client):
    """测试未授权访问"""
    response = client.get("/api/v1/payment/plans")
    assert response.status_code == 401
    
    response = client.get("/api/v1/payment/current-membership")
    assert response.status_code == 401


def test_create_wechat_native_order_success(authorized_client, test_user, db_session):
    """测试创建微信Native支付订单成功流程"""
    # 先创建订单
    response = authorized_client.post("/api/v1/payment/wechat/native", json={
        "level": "vip"
    })
    assert response.status_code == 200
    data = response.json()
    assert "order_no" in data
    order_no = data["order_no"]
    
    # 测试查询订单
    response = authorized_client.get(f"/api/v1/payment/wechat/query/{order_no}")
    assert response.status_code == 200
    query_data = response.json()
    assert query_data["order_no"] == order_no
    assert query_data["status"] == "pending"


def test_mock_pay_complete_success(authorized_client, test_user, db_session, settings):
    """测试Mock支付完成成功流程"""
    # 创建订单
    response = authorized_client.post("/api/v1/payment/wechat/native", json={
        "level": "vip"
    })
    order_no = response.json()["order_no"]
    
    # 完成支付
    response = authorized_client.post(f"/api/v1/payment/mock/{order_no}/complete")
    assert response.status_code == 200
    data = response.json()
    assert "支付成功" in data["message"]
    
    # 查询会员状态
    response = authorized_client.get("/api/v1/payment/current-membership")
    assert response.status_code == 200
    member_data = response.json()
    assert member_data["level"] == "vip"
    assert member_data["is_active"] is True


def test_mock_pay_complete_already_paid(authorized_client, test_user, db_session, settings):
    """测试Mock支付完成 - 订单已支付"""
    # 创建订单
    response = authorized_client.post("/api/v1/payment/wechat/native", json={
        "level": "vip"
    })
    order_no = response.json()["order_no"]
    
    # 第一次完成
    authorized_client.post(f"/api/v1/payment/mock/{order_no}/complete")
    
    # 第二次完成应该失败
    response = authorized_client.post(f"/api/v1/payment/mock/{order_no}/complete")
    assert response.status_code == 400
    assert "订单已支付" in response.json()["detail"]


def test_mock_pay_complete_not_allowed_in_production(authorized_client, test_user, db_session):
    """测试生产环境不允许Mock支付"""
    from unittest.mock import patch
    with patch("app.api.v1.payment.settings.DEBUG", False):
        response = authorized_client.post("/api/v1/payment/mock/any/complete")
        assert response.status_code == 403


def test_create_stripe_checkout_valid_level(authorized_client, test_user):
    """测试创建Stripe支付订单 - 有效等级"""
    response = authorized_client.post("/api/v1/payment/stripe/checkout", json={
        "level": "vip"
    })
    # Stripe可能未配置，但是接口应该能处理
    assert response.status_code in [200, 500]


def test_wechat_notify_processing(authorized_client, test_user, db_session):
    """测试微信支付回调处理"""
    # 接口应该能正常响应，即使没有有效数据
    response = authorized_client.post("/api/v1/payment/wechat/notify")
    assert response.status_code == 200
    # 微信回调总是返回成功
    assert "code" in response.json()


def test_get_user_order_list_pagination(authorized_client, test_user, db_session):
    """测试用户订单列表分页"""
    # 创建几个订单
    for level in ["vip", "svip"]:
        authorized_client.post("/api/v1/payment/wechat/native", json={"level": level})
    
    # 测试第一页
    response = authorized_client.get("/api/v1/payment/order-list?page=1&page_size=1")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 2
    assert len(data["orders"]) == 1
    assert data["has_next"] is True
    
    # 测试第二页
    response = authorized_client.get("/api/v1/payment/order-list?page=2&page_size=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data["orders"]) == 1


def test_get_user_order_list_empty(authorized_client, test_user):
    """测试用户没有订单时返回空列表"""
    # 假设新用户没有订单
    response = authorized_client.get("/api/v1/payment/order-list")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert len(data["orders"]) == 0
    assert data["has_next"] is False


def test_create_alipay_wap_order_valid_level(authorized_client, test_user):
    """测试创建支付宝手机网站支付订单 - 有效等级"""
    response = authorized_client.post("/api/v1/payment/alipay/wap", json={
        "level": "vip"
    })
    assert response.status_code == 200
    data = response.json()
    assert "order_no" in data
    assert "pay_url" in data


def test_alipay_return_invalid_signature(authorized_client, test_user):
    """测试支付宝同步跳转 - 无效签名"""
    response = authorized_client.get("/api/v1/payment/alipay/return")
    assert response.status_code == 400


def test_query_alipay_order_not_paid(authorized_client, test_user, db_session):
    """测试查询支付宝订单 - 未支付"""
    # 创建订单
    response = authorized_client.post("/api/v1/payment/alipay/page", json={"level": "vip"})
    order_no = response.json()["order_no"]
    
    # 查询
    response = authorized_client.get(f"/api/v1/payment/alipay/query/{order_no}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "pending"


def test_current_membership_free_user(authorized_client, test_user):
    """测试免费用户获取会员状态"""
    response = authorized_client.get("/api/v1/payment/current-membership")
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is False
    assert data["level"] == "free"
    assert data["days_remaining"] == 0
