"""
每日打卡API - 用户留存闭环核心功能
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models import User
from app.schemas.growth import (
    CheckInRequest,
    CheckInResponse,
    CheckInRecordResponse,
    CheckInStatsResponse,
    ReminderCreateRequest,
    ReminderResponse,
    ReminderListResponse,
)
from app.services.checkin_service import get_checkin_service

router = APIRouter(prefix="/checkin", tags=["每日打卡"])


@router.post("", summary="每日打卡", response_model=CheckInResponse)
async def daily_checkin(
    request: CheckInRequest = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """每日打卡接口，连续打卡获得更多奖励"""
    checkin_service = get_checkin_service()

    try:
        result = checkin_service.checkin(db, current_user.id, request.note if request else None)
        return CheckInResponse(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/today", summary="今日打卡状态")
async def get_today_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """检查今日是否已打卡"""
    checkin_service = get_checkin_service()
    status = checkin_service.get_today_status(db, current_user.id)
    return {"checked_in": status["checked_in"], "checkin": status.get("checkin")}


@router.get("/records", summary="打卡记录", response_model=List[CheckInRecordResponse])
async def get_checkin_records(
    limit: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取打卡记录"""
    checkin_service = get_checkin_service()
    records = checkin_service.get_checkin_records(db, current_user.id, limit)

    return [
        CheckInRecordResponse(
            id=r.id,
            check_in_date=r.check_in_date.isoformat(),
            check_in_time=r.check_in_time,
            streak_days=r.streak_days,
            xp_reward=r.xp_reward,
            note=r.note,
        )
        for r in records
    ]


@router.get("/stats", summary="打卡统计", response_model=CheckInStatsResponse)
async def get_checkin_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取打卡统计数据"""
    checkin_service = get_checkin_service()
    stats = checkin_service.get_stats(db, current_user.id)

    return CheckInStatsResponse(
        total_checkins=stats["total_checkins"],
        current_streak=stats["current_streak"],
        max_streak=stats["max_streak"],
        total_xp_earned=stats["total_xp_earned"],
        this_month_checkins=stats["this_month_checkins"],
        last_checkin_date=stats["last_checkin_date"],
        checkin_history=[
            CheckInRecordResponse(
                id=r.id,
                check_in_date=r.check_in_date.isoformat(),
                check_in_time=r.check_in_time,
                streak_days=r.streak_days,
                xp_reward=r.xp_reward,
                note=r.note,
            )
            for r in stats["checkin_history"]
        ],
    )


@router.post("/reminders", summary="创建回访提醒", response_model=ReminderResponse)
async def create_reminder(
    request: ReminderCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建回访提醒"""
    checkin_service = get_checkin_service()
    reminder = checkin_service.create_reminder(
        db,
        current_user.id,
        request.reminder_type,
        request.title,
        request.message,
        request.scheduled_time,
    )

    return ReminderResponse(
        id=reminder.id,
        reminder_type=reminder.reminder_type,
        title=reminder.title,
        message=reminder.message,
        scheduled_time=reminder.scheduled_time,
        is_sent=reminder.is_sent,
        is_cancelled=reminder.is_cancelled,
        sent_at=reminder.sent_at,
    )


@router.get("/reminders", summary="获取提醒列表", response_model=ReminderListResponse)
async def get_reminders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取用户的提醒列表"""
    checkin_service = get_checkin_service()
    result = checkin_service.get_reminders(db, current_user.id)

    return ReminderListResponse(
        pending=[
            ReminderResponse(
                id=r.id,
                reminder_type=r.reminder_type,
                title=r.title,
                message=r.message,
                scheduled_time=r.scheduled_time,
                is_sent=r.is_sent,
                is_cancelled=r.is_cancelled,
                sent_at=r.sent_at,
            )
            for r in result["pending"]
        ],
        sent=[
            ReminderResponse(
                id=r.id,
                reminder_type=r.reminder_type,
                title=r.title,
                message=r.message,
                scheduled_time=r.scheduled_time,
                is_sent=r.is_sent,
                is_cancelled=r.is_cancelled,
                sent_at=r.sent_at,
            )
            for r in result["sent"]
        ],
    )


@router.delete("/reminders/{reminder_id}", summary="取消提醒")
async def cancel_reminder(
    reminder_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """取消提醒"""
    checkin_service = get_checkin_service()
    success = checkin_service.cancel_reminder(db, current_user.id, reminder_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="提醒不存在",
        )

    return {"message": "提醒已取消"}


@router.get("/share/poster", summary="生成打卡分享海报数据")
async def generate_share_poster(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """生成分享海报所需的数据"""
    checkin_service = get_checkin_service()
    stats = checkin_service.get_stats(db, current_user.id)

    return {
        "username": current_user.nickname or "用户",
        "total_checkins": stats["total_checkins"],
        "current_streak": stats["current_streak"],
        "max_streak": stats["max_streak"],
        "total_xp_earned": stats["total_xp_earned"],
        "generated_at": datetime.now().isoformat(),
    }
