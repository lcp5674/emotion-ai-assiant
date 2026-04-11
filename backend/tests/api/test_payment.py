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
