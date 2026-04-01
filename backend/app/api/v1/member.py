"""
会员接口
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid

from app.core.database import get_db
from app.models import User, MemberOrder
from app.schemas.user import MemberOrderCreate, MemberOrderResponse, MemberPrice
from app.api.deps import get_current_user

router = APIRouter(prefix="/member", tags=["会员"])


MEMBER_PRICES = [
    MemberPrice(level="vip", name="VIP会员", price=2900, duration=30, features=[
        "无限次AI对话",
        "无限次MBTI测试",
        "专属AI助手",
        "情感日记",
        "知识库VIP内容",
    ]),
    MemberPrice(level="svip", name="超级会员", price=9900, duration=90, features=[
        "VIP全部权益",
        "优先响应",
        "专属情感顾问",
        "线下活动资格",
        "会员专属折扣",
    ]),
    MemberPrice(level="enterprise", name="企业会员", price=39900, duration=365, features=[
        "SVIP全部权益",
        "企业API接口",
        "定制AI助手",
        "专属客服",
        "数据报告",
    ]),
]


@router.get("/prices", summary="获取会员价格")
async def get_member_prices():
    return {"list": MEMBER_PRICES}


@router.post("/order", summary="创建会员订单")
async def create_order(
    request: MemberOrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 获取价格
    price_info = next((p for p in MEMBER_PRICES if p.level == request.level), None)
    if not price_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的会员等级",
        )

    # 生成订单号
    order_no = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8]}"

    # 创建订单
    order = MemberOrder(
        user_id=current_user.id,
        order_no=order_no,
        level=request.level,
        amount=price_info.price,
        duration=price_info.duration,
        status="pending",
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    pay_url = f"/payment/{order_no}"

    return MemberOrderResponse(
        order_no=order.order_no,
        amount=order.amount,
        pay_url=pay_url,
    )


@router.post("/order/{order_no}/pay", summary="支付订单")
async def pay_order(
    order_no: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = db.query(MemberOrder).filter(
        MemberOrder.order_no == order_no,
        MemberOrder.user_id == current_user.id,
    ).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在",
        )

    if order.status == "paid":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="订单已支付",
        )

    order.status = "paid"
    order.paid_at = datetime.now()

    current_user.member_level = request_level_to_enum(order.level)

    if current_user.member_expire_at and current_user.member_expire_at > datetime.now():
        current_user.member_expire_at = current_user.member_expire_at + timedelta(days=order.duration)
    else:
        current_user.member_expire_at = datetime.now() + timedelta(days=order.duration)

    db.commit()

    return {
        "message": "支付成功",
        "member_level": order.level,
        "expire_at": current_user.member_expire_at,
    }


@router.get("/status", summary="获取会员状态")
async def get_member_status(
    current_user: User = Depends(get_current_user),
):
    is_expired = False
    if current_user.member_expire_at:
        is_expired = current_user.member_expire_at < datetime.now()

    level = current_user.member_level.value if hasattr(current_user.member_level, 'value') else current_user.member_level

    return {
        "level": level,
        "expire_at": current_user.member_expire_at,
        "is_expired": is_expired,
    }


def request_level_to_enum(level: str):
    from app.models.user import MemberLevel
    return MemberLevel[level.upper()]