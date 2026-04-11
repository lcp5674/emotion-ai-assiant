"""
支付接口 - 微信支付
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
import loguru

from app.core.database import get_db, get_redis
from app.models import User, MemberOrder
from app.models.user import MemberLevel
from app.schemas.user import MemberOrderCreate, MemberOrderResponse
from app.api.deps import get_current_user
from app.services.payment_service import get_wechat_pay_service

router = APIRouter(prefix="/payment", tags=["支付"])


@router.get("/plans", summary="获取会员套餐列表")
async def get_member_plans(
    current_user: User = Depends(get_current_user),
):
    """获取所有可用会员套餐列表"""
    from app.models.user import User
    current_info = None
    if current_user.member_level and current_user.member_level != MemberLevel.FREE:
        current_info = {
            "level": current_user.member_level.value,
            "expire_at": current_user.member_expire_at,
        }
    
    return {
        "plans": MEMBER_PRICES,
        "current_member": current_info,
        "benefits": [
            {
                "name": "无限AI对话",
                "description": "不再限制每日聊天次数，随时倾诉你的心情"
            },
            {
                "name": "深度情绪分析",
                "description": "AI分析你的情绪变化趋势，生成专业报告"
            },
            {
                "name": "情绪趋势图表",
                "description": "可视化展示你的情绪变化，助你成长"
            },
            {
                "name": "MBTI深度解析",
                "description": "更详细的人格特点分析和成长建议"
            },
            {
                "name": "优先客服支持",
                "description": "更快的问题响应和问题解决"
            }
        ]
    }


MEMBER_PRICES = [
    {"level": "vip", "name": "月度VIP", "price": 2900, "duration": 30, 
     "description": "解锁所有AI对话功能，无限聊天次数", 
     "features": ["无限AI对话", "优先AI处理", "基础情绪分析", "MBTI完整报告"]},
    {"level": "svip", "name": "季度超级VIP", "price": 9900, "duration": 90, 
     "description": "全部功能开放，享受最佳体验", 
     "features": ["无限AI对话", "专属AI助手", "完整情绪分析报告", "情绪趋势图表", 
                 "MBTI深度解析", "无限制成长记录", "优先客服支持"]},
    {"level": "yearly", "name": "年度会员", "price": 29900, "duration": 365, 
     "description": "最划算选择，年度优惠", 
     "features": ["全部SVIP功能", "享受7折优惠", "专属功能优先体验", "一对一顾问咨询"]},
]


@router.post("/wechat/native", summary="创建微信Native支付订单")
async def create_wechat_native_order(
    request: MemberOrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    price_info = next((p for p in MEMBER_PRICES if p["level"] == request.level), None)
    if not price_info:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无效的会员等级")

    order_no = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8]}"

    order = MemberOrder(
        user_id=current_user.id,
        order_no=order_no,
        level=request.level,
        amount=price_info["price"],
        duration=price_info["duration"],
        status="pending",
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    pay_service = get_wechat_pay_service()
    description = f"心灵伴侣AI-{price_info['name']}"
    result = await pay_service.create_native_order(order_no, price_info["price"], description)

    if result.get("mode") == "wechat":
        return {
            "order_no": order_no,
            "code_url": result.get("code_url"),
            "amount": price_info["price"],
        }
    elif result.get("mode") == "mock":
        return {
            "mode": "mock",
            "order_no": order_no,
            "pay_url": result.get("pay_url"),
            "amount": price_info["price"],
        }
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="支付创建失败")


@router.post("/wechat/notify", summary="微信支付回调通知")
async def wechat_notify(
    request: Request,
    db: Session = Depends(get_db),
):
    body = await request.body()
    headers = dict(request.headers)

    pay_service = get_wechat_pay_service()
    notify_data = await pay_service.parse_notify(body, headers)

    if not notify_data:
        return {"code": "SUCCESS", "message": "OK"}

    if notify_data.get("status") == "paid":
        order_no = notify_data["order_no"]
        order = db.query(MemberOrder).filter(MemberOrder.order_no == order_no).first()

        if order and order.status != "paid":
            order.status = "paid"
            order.paid_at = datetime.now()

            user = db.query(User).filter(User.id == order.user_id).first()
            if user:
                user.member_level = MemberLevel[order.level.upper()]

                from datetime import timedelta
                if user.member_expire_at and user.member_expire_at > datetime.now():
                    user.member_expire_at = user.member_expire_at + timedelta(days=order.duration)
                else:
                    user.member_expire_at = datetime.now() + timedelta(days=order.duration)

            db.commit()
            loguru.logger.info(f"订单 {order_no} 支付成功")

    return {"code": "SUCCESS", "message": "OK"}


@router.get("/wechat/query/{order_no}", summary="查询支付状态")
async def query_wechat_order(
    order_no: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = db.query(MemberOrder).filter(
        MemberOrder.order_no == order_no,
        MemberOrder.user_id == current_user.id,
    ).first()

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单不存在")

    return {
        "order_no": order.order_no,
        "status": order.status,
        "level": order.level,
        "amount": order.amount,
        "paid_at": order.paid_at,
    }


@router.post("/mock/{order_no}/complete", summary="Mock支付完成（仅开发测试用）")
async def mock_pay_complete(
    order_no: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.core.config import settings
    if not settings.DEBUG:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="仅开发环境可用")

    order = db.query(MemberOrder).filter(
        MemberOrder.order_no == order_no,
        MemberOrder.user_id == current_user.id,
    ).first()

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单不存在")
    if order.status == "paid":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="订单已支付")

    order.status = "paid"
    order.paid_at = datetime.now()

    current_user.member_level = MemberLevel[order.level.upper()]

    from datetime import timedelta as td
    if current_user.member_expire_at and current_user.member_expire_at > datetime.now():
        current_user.member_expire_at = current_user.member_expire_at + td(days=order.duration)
    else:
        current_user.member_expire_at = datetime.now() + td(days=order.duration)

    db.commit()

    return {"message": "支付成功", "level": order.level}


@router.post("/stripe/checkout", summary="创建Stripe支付订单")
async def create_stripe_checkout(
    request: MemberOrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    price_info = next((p for p in MEMBER_PRICES if p["level"] == request.level), None)
    if not price_info:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无效的会员等级")

    order_no = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8]}"

    order = MemberOrder(
        user_id=current_user.id,
        order_no=order_no,
        level=request.level,
        amount=price_info["price"],
        duration=price_info["duration"],
        status="pending",
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    from app.services.stripe_service import get_stripe_pay_service
    stripe_service = get_stripe_pay_service()
    description = f"心灵伴侣AI-{price_info['name']}"
    
    success_url = f"{settings.API_BASE_URL}/api/v1/payment/stripe/success?session_id={{session_id}}"
    cancel_url = f"{settings.API_BASE_URL}/api/v1/payment/stripe/cancel"
    
    result = await stripe_service.create_checkout_session(
        order_no=order_no,
        amount=price_info["price"],
        description=description,
        success_url=success_url,
        cancel_url=cancel_url,
    )

    return result


@router.get("/stripe/success", summary="Stripe支付成功回调")
async def stripe_success(
    session_id: str,
    db: Session = Depends(get_db),
):
    from app.services.stripe_service import get_stripe_pay_service
    stripe_service = get_stripe_pay_service()
    
    result = await stripe_service.verify_payment(session_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="支付验证失败")

    order_no = result.get("order_no")
    order = db.query(MemberOrder).filter(MemberOrder.order_no == order_no).first()

    if order and order.status != "paid":
        order.status = "paid"
        order.paid_at = datetime.now()

        user = db.query(User).filter(User.id == order.user_id).first()
        if user:
            user.member_level = MemberLevel[order.level.upper()]

            from datetime import timedelta
            if user.member_expire_at and user.member_expire_at > datetime.now():
                user.member_expire_at = user.member_expire_at + timedelta(days=order.duration)
            else:
                user.member_expire_at = datetime.now() + timedelta(days=order.duration)

        db.commit()
        loguru.logger.info(f"Stripe订单 {order_no} 支付成功")

    return {"message": "支付成功", "redirect_url": "/payment/success"}


@router.get("/stripe/cancel", summary="Stripe支付取消")
async def stripe_cancel():
    return {"message": "支付已取消", "redirect_url": "/payment"}


@router.post("/stripe/webhook", summary="Stripe webhook")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    payload = await request.body()
    signature = request.headers.get("stripe-signature", "")

    from app.services.stripe_service import get_stripe_pay_service
    stripe_service = get_stripe_pay_service()
    
    result = await stripe_service.handle_webhook(payload, signature)
    if result and result.get("status") == "paid":
        order_no = result.get("order_no")
        order = db.query(MemberOrder).filter(MemberOrder.order_no == order_no).first()

        if order and order.status != "paid":
            order.status = "paid"
            order.paid_at = datetime.now()

            user = db.query(User).filter(User.id == order.user_id).first()
            if user:
                user.member_level = MemberLevel[order.level.upper()]

                from datetime import timedelta
                if user.member_expire_at and user.member_expire_at > datetime.now():
                    user.member_expire_at = user.member_expire_at + timedelta(days=order.duration)
                else:
                    user.member_expire_at = datetime.now() + timedelta(days=order.duration)

            db.commit()
            loguru.logger.info(f"Stripe webhook订单 {order_no} 支付成功")

    return {"received": True}


@router.post("/alipay/page", summary="创建支付宝网页支付订单")
async def create_alipay_page_order(
    request: MemberOrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    price_info = next((p for p in MEMBER_PRICES if p["level"] == request.level), None)
    if not price_info:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无效的会员等级")

    order_no = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8]}"

    order = MemberOrder(
        user_id=current_user.id,
        order_no=order_no,
        level=request.level,
        amount=price_info["price"],
        duration=price_info["duration"],
        status="pending",
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    from app.services.alipay_service import get_alipay_service
    alipay_service = get_alipay_service()
    description = f"心灵伴侣AI-{price_info['name']}"
    # 分转元
    amount = price_info["price"] / 100
    
    result = await alipay_service.create_page_pay_order(
        order_no=order_no,
        amount=amount,
        subject=description,
    )

    if result.get("mode") in ["alipay", "mock"]:
        return {
            "order_no": order_no,
            "pay_url": result.get("pay_url"),
            "amount": price_info["price"],
            "mode": result.get("mode"),
        }
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="支付创建失败")


@router.post("/alipay/wap", summary="创建支付宝手机网站支付订单")
async def create_alipay_wap_order(
    request: MemberOrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    price_info = next((p for p in MEMBER_PRICES if p["level"] == request.level), None)
    if not price_info:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无效的会员等级")

    order_no = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8]}"

    order = MemberOrder(
        user_id=current_user.id,
        order_no=order_no,
        level=request.level,
        amount=price_info["price"],
        duration=price_info["duration"],
        status="pending",
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    from app.services.alipay_service import get_alipay_service
    alipay_service = get_alipay_service()
    description = f"心灵伴侣AI-{price_info['name']}"
    # 分转元
    amount = price_info["price"] / 100
    
    result = await alipay_service.create_wap_pay_order(
        order_no=order_no,
        amount=amount,
        subject=description,
    )

    if result.get("mode") in ["alipay", "mock"]:
        return {
            "order_no": order_no,
            "pay_url": result.get("pay_url"),
            "amount": price_info["price"],
            "mode": result.get("mode"),
        }
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="支付创建失败")


@router.post("/alipay/notify", summary="支付宝支付异步回调")
async def alipay_notify(
    request: Request,
    db: Session = Depends(get_db),
):
    form_data = await request.form()
    params = dict(form_data)

    from app.services.alipay_service import get_alipay_service
    alipay_service = get_alipay_service()
    
    if not alipay_service.verify_notify(params):
        return "failure"

    trade_status = params.get("trade_status")
    order_no = params.get("out_trade_no")
    
    if trade_status == "TRADE_SUCCESS" or trade_status == "TRADE_FINISHED":
        order = db.query(MemberOrder).filter(MemberOrder.order_no == order_no).first()

        if order and order.status != "paid":
            order.status = "paid"
            order.paid_at = datetime.now()
            order.transaction_id = params.get("trade_no")

            user = db.query(User).filter(User.id == order.user_id).first()
            if user:
                user.member_level = MemberLevel[order.level.upper()]

                from datetime import timedelta
                if user.member_expire_at and user.member_expire_at > datetime.now():
                    user.member_expire_at = user.member_expire_at + timedelta(days=order.duration)
                else:
                    user.member_expire_at = datetime.now() + timedelta(days=order.duration)

            db.commit()
            loguru.logger.info(f"支付宝订单 {order_no} 支付成功")

    return "success"


@router.get("/alipay/return", summary="支付宝支付同步跳转")
async def alipay_return(
    request: Request,
    db: Session = Depends(get_db),
):
    params = dict(request.query_params)

    from app.services.alipay_service import get_alipay_service
    alipay_service = get_alipay_service()
    
    if not alipay_service.verify_return(params):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="支付验证失败")

    order_no = params.get("out_trade_no")
    order = db.query(MemberOrder).filter(MemberOrder.order_no == order_no).first()

    if order and order.status != "paid":
        # 同步跳转可能延迟，主动查询订单状态
        order_result = await alipay_service.query_order(order_no)
        if order_result and order_result.get("status") in ["TRADE_SUCCESS", "TRADE_FINISHED"]:
            order.status = "paid"
            order.paid_at = datetime.now()
            order.transaction_id = order_result.get("trade_no")

            user = db.query(User).filter(User.id == order.user_id).first()
            if user:
                user.member_level = MemberLevel[order.level.upper()]

                from datetime import timedelta
                if user.member_expire_at and user.member_expire_at > datetime.now():
                    user.member_expire_at = user.member_expire_at + timedelta(days=order.duration)
                else:
                    user.member_expire_at = datetime.now() + timedelta(days=order.duration)

            db.commit()
            loguru.logger.info(f"支付宝订单 {order_no} 支付成功（同步跳转）")

    return {"message": "支付成功", "redirect_url": "/payment/success"}


@router.get("/alipay/query/{order_no}", summary="查询支付宝订单状态")
async def query_alipay_order(
    order_no: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = db.query(MemberOrder).filter(
        MemberOrder.order_no == order_no,
        MemberOrder.user_id == current_user.id,
    ).first()

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单不存在")

    from app.services.alipay_service import get_alipay_service
    alipay_service = get_alipay_service()
    
    # 如果本地状态已支付，直接返回
    if order.status == "paid":
        return {
            "order_no": order.order_no,
            "status": order.status,
            "level": order.level,
            "amount": order.amount,
            "paid_at": order.paid_at,
            "transaction_id": order.transaction_id,
        }
    
    # 否则主动查询支付宝
    result = await alipay_service.query_order(order_no)
    if result and result.get("status") in ["TRADE_SUCCESS", "TRADE_FINISHED"]:
        # 更新订单状态
        order.status = "paid"
        order.paid_at = datetime.now()
        order.transaction_id = result.get("trade_no")
        
        user = db.query(User).filter(User.id == order.user_id).first()
        if user:
            user.member_level = MemberLevel[order.level.upper()]

            from datetime import timedelta
            if user.member_expire_at and user.member_expire_at > datetime.now():
                user.member_expire_at = user.member_expire_at + timedelta(days=order.duration)
            else:
                user.member_expire_at = datetime.now() + timedelta(days=order.duration)
        
        db.commit()
        loguru.logger.info(f"支付宝订单 {order_no} 支付成功（主动查询）")
        
        return {
            "order_no": order.order_no,
            "status": "paid",
            "level": order.level,
            "amount": order.amount,
            "paid_at": order.paid_at,
            "transaction_id": order.transaction_id,
        }
    
    return {
        "order_no": order.order_no,
        "status": order.status,
        "level": order.level,
        "amount": order.amount,
        "paid_at": order.paid_at,
        "transaction_id": order.transaction_id,
    }


@router.get("/current-membership", summary="获取当前会员状态")
async def get_current_membership(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前用户会员状态"""
    from datetime import datetime
    
    is_active = False
    days_remaining = 0
    
    if (current_user.member_level != MemberLevel.FREE 
        and current_user.member_expire_at 
        and current_user.member_expire_at > datetime.now()):
        is_active = True
        days_remaining = (current_user.member_expire_at - datetime.now()).days
    
    return {
        "is_active": is_active,
        "level": current_user.member_level.value if current_user.member_level else "free",
        "expire_at": current_user.member_expire_at,
        "days_remaining": days_remaining,
        "features_available": {
            "unlimited_chat": is_active or current_user.member_level != MemberLevel.FREE,
            "mood_charts": is_active,
            "advanced_analysis": is_active,
            "full_mbti_report": is_active,
        }
    }


@router.get("/order-list", summary="获取用户订单列表")
async def get_user_order_list(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = 1,
    page_size: int = 10,
):
    """获取用户的订单列表"""
    from sqlalchemy import desc
    
    query = db.query(MemberOrder).filter(
        MemberOrder.user_id == current_user.id
    ).order_by(desc(MemberOrder.created_at))
    
    total = query.count()
    offset = (page - 1) * page_size
    orders = query.offset(offset).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "has_next": page * page_size < total,
        "orders": [
            {
                "order_no": o.order_no,
                "level": o.level,
                "amount": o.amount,
                "duration": o.duration,
                "status": o.status,
                "created_at": o.created_at,
                "paid_at": o.paid_at,
            }
            for o in orders
        ]
    }
