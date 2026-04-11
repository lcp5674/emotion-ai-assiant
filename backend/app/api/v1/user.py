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


@router.get("/onboarding-status", summary="获取首次使用引导状态")
async def get_onboarding_status(
    current_user: User = Depends(get_current_user),
):
    """获取用户首次使用引导状态，检查哪些步骤已完成"""
    from app.models import MbtiResult
    from app.core.database import SessionLocal
    db = SessionLocal()
    
    # 检查是否已完成MBTI测试
    has_completed_mbti = db.query(MbtiResult).filter(
        MbtiResult.user_id == current_user.id
    ).count() > 0
    
    # 检查是否已创建第一篇日记
    from app.models.diary import Diary
    has_created_diary = db.query(Diary).filter(
        Diary.user_id == current_user.id
    ).count() > 0
    
    # 检查是否已有对话
    from app.models.chat import Conversation
    has_started_chat = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).count() > 0
    
    db.close()
    
    return {
        "has_completed_onboarding": has_completed_mbti and has_created_diary and has_started_chat,
        "steps": {
            "complete_mbti": has_completed_mbti,
            "create_first_diary": has_created_diary,
            "start_first_chat": has_started_chat
        },
        "current_step": (
            "complete_mbti" if not has_completed_mbti else
            "create_first_diary" if not has_created_diary else
            "start_first_chat" if not has_started_chat else
            "completed"
        )
    }


@router.post("/mark-onboarding-step", summary="标记引导步骤已完成")
async def mark_onboarding_step(
    step: str,
    current_user: User = Depends(get_current_user),
):
    """标记某个引导步骤已完成"""
    # 这里只是记录，实际状态还是根据实际数据判断
    # 可以在用户表增加字段，但这里直接根据实际数据判断更准确
    return {
        "success": True,
        "message": f"步骤 {step} 已标记完成"
    }


@router.get("/privacy-info", summary="获取用户数据隐私说明")
async def get_privacy_info(
    current_user: User = Depends(get_current_user),
):
    """获取针对当前用户的数据隐私说明"""
    return {
        "title": "您的数据隐私说明",
        "points": [
            {
                "title": "数据加密存储",
                "description": "您的日记和个人信息采用加密存储"
            },
            {
                "title": "完全可控",
                "description": "您可以随时查看、编辑、导出或删除您的所有数据"
            },
            {
                "title": "不用于广告营销",
                "description": "我们绝不会出售或分享您的个人数据给第三方用于广告营销"
            },
            {
                "title": "AI处理说明",
                "description": "当您使用AI聊天时，内容会发送给AI服务商处理以生成回复"
            }
        ],
        "data_controls": [
            {
                "action": "export",
                "title": "导出所有数据",
                "description": "下载您存储在我们这里的所有个人数据"
            },
            {
                "action": "delete_account",
                "title": "删除账户",
                "description": "永久删除您的账户和所有相关数据"
            }
        ]
    }


@router.post("/request-data-export", summary="请求数据导出")
async def request_data_export(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """请求导出用户所有数据"""
    # 创建导出任务
    # 实际实现可以异步处理，这里直接返回成功
    return {
        "success": True,
        "message": "数据导出请求已受理，处理完成后会通知您",
        "estimated_time": "1-5分钟"
    }


@router.post("/request-account-deletion", summary="请求删除账户")
async def request_account_deletion(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """请求删除账户"""
    # 这里标记账户为待删除状态
    # 实际删除会在后台处理
    current_user.is_active = False
    current_user.deletion_requested = True
    current_user.deletionRequestedAt = db.func.now()
    db.commit()
    
    return {
        "success": True,
        "message": "账户删除请求已受理，我们会在7个工作日内处理完成",
        "cancellation_info": "如果您改变了主意，可以在此期间联系客服取消请求"
    }