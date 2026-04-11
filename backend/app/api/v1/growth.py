"""
用户成长体系API - 等级经验和成就徽章
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models import User
from app.schemas.growth import (
    BadgeInfo,
    UserBadgeInfo,
    BadgeProgressResponse,
    UserLevelResponse,
    ExpRecordResponse,
    GrowthTaskResponse,
    SetBadgeDisplayRequest,
)
from app.services.growth_service import get_growth_service

router = APIRouter(prefix="/growth", tags=["成长体系"])


# ============ 徽章 ============

@router.get("/badges", summary="获取所有徽章信息")
async def get_all_badges(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取所有徽章定义"""
    growth_service = get_growth_service()
    badges = growth_service.get_all_badges(db)

    return [
        BadgeInfo(
            id=b.id,
            badge_code=b.badge_code,
            name=b.name,
            description=b.description,
            icon=b.icon,
            rarity=b.rarity,
            category=b.category,
            condition_type=b.condition_type,
            condition_value=b.condition_value,
            hint=b.hint,
            is_hidden=b.is_hidden,
        )
        for b in badges
    ]


@router.get("/badges/user", summary="获取用户已获得徽章")
async def get_user_badges(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前用户已获得的徽章"""
    growth_service = get_growth_service()
    result = growth_service.get_user_badges(db, current_user.id)

    return [
        UserBadgeInfo(**item)
        for item in result
    ]


@router.get("/badges/progress", summary="获取徽章解锁进度")
async def get_badge_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取用户徽章解锁进度"""
    growth_service = get_growth_service()
    progress = growth_service.get_badge_progress(db, current_user.id)

    return BadgeProgressResponse(**progress)


@router.post("/badges/{badge_id}/display", summary="设置徽章展示")
async def set_badge_display(
    badge_id: int,
    request: SetBadgeDisplayRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """设置徽章是否在个人资料展示"""
    growth_service = get_growth_service()

    success = growth_service.set_badge_display(
        db=db,
        user_id=current_user.id,
        badge_id=badge_id,
        is_displayed=request.is_displayed,
        display_note=request.display_note,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="徽章不存在或你没有权限修改",
        )

    return {"message": "设置已更新"}


# ============ 等级经验 ============

@router.get("/level", summary="获取用户等级信息")
async def get_user_level(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前用户等级信息"""
    growth_service = get_growth_service()
    info = growth_service.get_user_level_info(db, current_user.id)

    return UserLevelResponse(**info)


@router.get("/exp/records", summary="获取经验获取记录")
async def get_exp_records(
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取经验获取记录"""
    growth_service = get_growth_service()
    records = growth_service.get_exp_records(db, current_user.id, limit)

    return [
        ExpRecordResponse(
            id=r.id,
            action=r.action,
            exp_gained=r.exp_gained,
            description=r.description,
            created_at=r.created_at,
        )
        for r in records
    ]


# ============ 成长任务 ============

@router.get("/tasks", summary="获取成长任务")
async def get_growth_tasks(
    include_completed: bool = Query(False, description="是否包含已完成任务"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取用户成长任务列表"""
    growth_service = get_growth_service()
    tasks = growth_service.get_user_tasks(db, current_user.id, include_completed)

    return [
        GrowthTaskResponse(
            id=t.id,
            task_type=t.task_type,
            task_code=t.task_code,
            title=t.title,
            description=t.description,
            target=t.target,
            current=t.current,
            is_completed=t.is_completed,
            is_rewarded=t.is_rewarded,
            reward_exp=t.reward_exp,
            reward_badge_id=t.reward_badge_id,
            deadline=t.deadline,
            created_at=t.created_at,
            completed_at=t.completed_at,
        )
        for t in tasks
    ]


@router.post("/tasks/{task_id}/claim", summary="领取任务奖励")
async def claim_task_reward(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """完成并领取任务奖励"""
    growth_service = get_growth_service()
    result = growth_service.complete_task(db, current_user.id, task_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在",
        )

    if result.get("already_rewarded"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="奖励已经领取过了",
        )

    return {
        "message": "奖励领取成功",
        "reward_exp": result["reward_exp"],
        "result": result["result"],
    }


@router.get("/overview", summary="获取成长概览")
async def get_growth_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取用户成长体系概览"""
    growth_service = get_growth_service()

    level_info = growth_service.get_user_level_info(db, current_user.id)
    badge_progress = growth_service.get_badge_progress(db, current_user.id)
    tasks = growth_service.get_user_tasks(db, current_user.id, include_completed=False)

    pending_tasks = len([t for t in tasks if not t.is_completed])

    return {
        "level": level_info,
        "badges": {
            "total": badge_progress["total"],
            "unlocked": badge_progress["unlocked_count"],
            "progress_percent": int(badge_progress["unlocked_count"] / badge_progress["total"] * 100) if badge_progress["total"] > 0 else 0,
        },
        "pending_tasks": pending_tasks,
    }
