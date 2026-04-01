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


MEMBER_PRICES = [
    {"level": "vip", "name": "VIP会员", "price": 2900, "duration": 30},
    {"level": "svip", "name": "超级会员", "price": 9900, "duration": 90},
    {"level": "enterprise", "name": "企业会员", "price": 39900, "duration": 365},
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
