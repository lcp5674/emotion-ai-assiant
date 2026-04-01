"""
用户接口
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User
from app.schemas.user import (
    UserInfo,
    UpdateUserRequest,
    ChangePasswordRequest,
)
from app.api.deps import get_current_user
from app.core.security import get_password_hash, verify_password

router = APIRouter(prefix="/user", tags=["用户"])


@router.get("/profile", summary="获取用户资料")
async def get_profile(
    current_user: User = Depends(get_current_user),
):
    """获取当前用户资料"""
    return UserInfo.model_validate(current_user)


@router.put("/profile", summary="更新用户资料")
async def update_profile(
    request: UpdateUserRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新用户资料"""
    if request.nickname is not None:
        current_user.nickname = request.nickname
    if request.avatar is not None:
        current_user.avatar = request.avatar

    db.commit()
    db.refresh(current_user)

    return UserInfo.model_validate(current_user)


@router.post("/password", summary="修改密码")
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """修改密码"""
    # 验证旧密码
    if not verify_password(request.old_password, current_user.password_hash or ""):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="原密码错误",
        )

    # 更新密码
    current_user.password_hash = get_password_hash(request.new_password)
    db.commit()

    return {"message": "密码修改成功"}


@router.get("/stats", summary="获取用户统计")
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取用户统计数据"""
    from app.models import Conversation, MbtiResult

    # 对话数
    conversation_count = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).count()

    # MBTI测试次数
    mbti_test_count = db.query(MbtiResult).filter(
        MbtiResult.user_id == current_user.id
    ).count()

    # 会员状态
    member_info = None
    if current_user.member_level != "free":
        member_info = {
            "level": current_user.member_level.value if hasattr(current_user.member_level, 'value') else current_user.member_level,
            "expire_at": current_user.member_expire_at,
        }

    return {
        "conversation_count": conversation_count,
        "mbti_test_count": mbti_test_count,
        "member": member_info,
    }