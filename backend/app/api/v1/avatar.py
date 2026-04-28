"""
虚拟形象API
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User, AiAssistant, AiAvatar
from app.schemas.avatar import (
    AiAvatarCreate,
    AiAvatarUpdate,
    AiAvatarResponse,
    AnimationRequest,
    AnimationResponse,
    AvatarConfigResponse,
    BuiltInExpression,
    BuiltInMotion,
)
from app.services.animation_service import get_animation_service
from app.api.deps import get_current_user

router = APIRouter(prefix="/avatar", tags=["虚拟形象"])


@router.get("/config", summary="获取虚拟形象配置")
async def get_avatar_config():
    """获取内置的表情和动作列表"""
    service = get_animation_service()

    expressions = [BuiltInExpression(**e) for e in service.get_built_in_expressions()]
    motions = [BuiltInMotion(**m) for m in service.get_built_in_motions()]

    return AvatarConfigResponse(
        expressions=expressions,
        motions=motions,
    )


@router.get("/{assistant_id}", summary="获取助手虚拟形象")
async def get_avatar(
    assistant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取指定AI助手的虚拟形象配置"""
    # 检查助手是否存在
    assistant = db.query(AiAssistant).filter(AiAssistant.id == assistant_id).first()
    if not assistant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI助手不存在",
        )

    # 获取虚拟形象
    avatar = db.query(AiAvatar).filter(AiAvatar.assistant_id == assistant_id).first()

    if not avatar:
        # 如果没有配置，返回预设信息
        service = get_animation_service()
        preset = service.get_preset_config(assistant_id)

        if preset:
            return {
                "id": None,
                "assistant_id": assistant_id,
                "model_type": "live2d",
                "name": preset["name"],
                "description": preset["personality"],
                "preset": True,
                "default_expression": preset["default_expression"],
                "expressions": preset["expressions"],
                "default_motion": preset["default_motion"],
                "motions": preset["motions"],
                "position_x": 0.0,
                "position_y": 0.0,
                "scale": 1.0,
                "z_index": 1,
                "is_active": True,
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="该助手暂无虚拟形象配置",
            )

    return avatar


@router.post("/", summary="创建虚拟形象")
async def create_avatar(
    avatar_data: AiAvatarCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """为AI助手创建虚拟形象配置"""
    # 检查助手是否存在
    assistant = db.query(AiAssistant).filter(AiAssistant.id == avatar_data.assistant_id).first()
    if not assistant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI助手不存在",
        )

    # 检查是否已存在
    existing = db.query(AiAvatar).filter(AiAvatar.assistant_id == avatar_data.assistant_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该助手已有虚拟形象配置，请使用更新接口",
        )

    # 创建虚拟形象
    avatar = AiAvatar(
        assistant_id=avatar_data.assistant_id,
        model_type=avatar_data.model_type,
        name=avatar_data.name,
        description=avatar_data.description,
        position_x=avatar_data.position_x,
        position_y=avatar_data.position_y,
        scale=avatar_data.scale,
        z_index=avatar_data.z_index,
        default_motion=avatar_data.default_motion,
        speak_motion=avatar_data.speak_motion,
        idle_motions=avatar_data.idle_motions,
        is_active=True,
    )
    db.add(avatar)
    db.commit()
    db.refresh(avatar)

    return avatar


@router.put("/{avatar_id}", summary="更新虚拟形象")
async def update_avatar(
    avatar_id: int,
    avatar_data: AiAvatarUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新虚拟形象配置"""
    avatar = db.query(AiAvatar).filter(AiAvatar.id == avatar_id).first()
    if not avatar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="虚拟形象不存在",
        )

    # 更新字段
    update_data = avatar_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(avatar, key, value)

    db.commit()
    db.refresh(avatar)

    return avatar


@router.delete("/{avatar_id}", summary="删除虚拟形象")
async def delete_avatar(
    avatar_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除虚拟形象配置"""
    avatar = db.query(AiAvatar).filter(AiAvatar.id == avatar_id).first()
    if not avatar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="虚拟形象不存在",
        )

    # 软删除
    avatar.is_active = False
    db.commit()

    return {"message": "虚拟形象已删除"}


@router.post("/animate", summary="获取动画指令")
async def get_animation(
    request: AnimationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """根据内容获取动画指令"""
    service = get_animation_service()

    # 确定assistant_id
    assistant_id = request.assistant_id if hasattr(request, 'assistant_id') else None

    # 获取动画
    animation = service.get_animation(
        emotion=request.emotion,
        message=request.message,
        response=request.response,
        assistant_id=assistant_id,
    )

    return AnimationResponse(
        expressions=animation.get("expressions", []),
        motions=animation.get("motions", []),
        sound=animation.get("sound"),
        duration=animation.get("duration"),
        transition_duration=animation.get("transition_duration", 0.3),
    )


@router.post("/animate/{assistant_id}", summary="获取指定助手的动画指令")
async def get_animation_for_assistant(
    assistant_id: int,
    request: AnimationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """根据内容获取指定AI助手的动画指令"""
    # 检查助手是否存在
    assistant = db.query(AiAssistant).filter(AiAssistant.id == assistant_id).first()
    if not assistant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI助手不存在",
        )

    service = get_animation_service()

    # 强制使用指定的表情/动作（如果提供）
    if request.force_expression:
        animation = {
            "expressions": [request.force_expression],
            "motions": [],
            "sound": None,
            "transition_duration": 0.3,
            "emotion": request.force_expression,
        }
    elif request.force_motion:
        animation = {
            "expressions": [],
            "motions": [request.force_motion],
            "sound": None,
            "transition_duration": 0.3,
            "emotion": request.force_motion,
        }
    else:
        animation = service.get_animation(
            emotion=request.emotion,
            message=request.message,
            response=request.response,
            assistant_id=assistant_id,
        )

    return AnimationResponse(
        expressions=animation.get("expressions", []),
        motions=animation.get("motions", []),
        sound=animation.get("sound"),
        duration=animation.get("duration"),
        transition_duration=animation.get("transition_duration", 0.3),
    )