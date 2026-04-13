"""
对话满意度评价API
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.models import User
from app.schemas.feedback import (
    MessageFeedbackCreate,
    MessageFeedbackResponse,
    ConversationFeedbackCreate,
    ConversationFeedbackResponse,
    FeedbackStatsResponse,
)
from app.services.feedback_service import get_feedback_service
from app.api.deps import get_current_user
from app.core.i18n import _

router = APIRouter(prefix="/feedback", tags=["反馈评价"])


@router.post("/message", summary="评价消息")
async def create_message_feedback(
    request: MessageFeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    对AI消息进行评价
    - rating: 评分 1-5星
    - helpful: 是否有帮助 0-否 1-是
    - comment: 评价内容（可选）
    """
    feedback_service = get_feedback_service()
    feedback = feedback_service.create_message_feedback(
        db=db,
        user_id=current_user.id,
        message_id=request.message_id,
        rating=request.rating,
        helpful=request.helpful,
        comment=request.comment
    )

    return MessageFeedbackResponse(
        id=feedback.id,
        message_id=feedback.message_id,
        rating=feedback.rating,
        helpful=feedback.helpful,
        comment=feedback.comment,
        created_at=feedback.created_at
    )


@router.get("/message/{message_id}", summary="获取消息评价")
async def get_message_feedback(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取指定消息的评价"""
    feedback_service = get_feedback_service()
    feedback = feedback_service.get_message_feedback(
        db=db,
        user_id=current_user.id,
        message_id=message_id
    )

    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_("暂无评价")
        )

    return MessageFeedbackResponse(
        id=feedback.id,
        message_id=feedback.message_id,
        rating=feedback.rating,
        helpful=feedback.helpful,
        comment=feedback.comment,
        created_at=feedback.created_at
    )


@router.post("/conversation", summary="评价对话")
async def create_conversation_feedback(
    request: ConversationFeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    对整个对话进行满意度评价
    - overall_rating: 整体评分 1-5星
    - empathy_rating: 共情能力评分 1-5星
    - helpfulness_rating: 帮助程度评分 1-5星
    - tags: 标签列表，如：温暖、专业、有用、耐心等
    - improvement_suggestion: 改进建议（可选）
    - is_satisfied: 是否满意
    """
    feedback_service = get_feedback_service()
    feedback = feedback_service.create_conversation_feedback(
        db=db,
        user_id=current_user.id,
        conversation_id=request.conversation_id,
        overall_rating=request.overall_rating,
        empathy_rating=request.empathy_rating,
        helpfulness_rating=request.helpfulness_rating,
        tags=request.tags,
        improvement_suggestion=request.improvement_suggestion,
        is_satisfied=request.is_satisfied
    )

    return feedback


@router.get("/conversation/{conversation_id}", summary="获取对话评价")
async def get_conversation_feedback(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取指定对话的评价"""
    feedback_service = get_feedback_service()
    feedback = feedback_service.get_conversation_feedback(
        db=db,
        user_id=current_user.id,
        conversation_id=conversation_id
    )

    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_("暂无评价")
        )

    return feedback


@router.get("/stats/me", summary="获取我的反馈统计")
async def get_my_feedback_stats(
    days: int = Query(default=30, ge=7, le=365, description="统计周期（天）"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    获取当前用户的反馈统计
    - total_conversations: 评价的对话总数
    - avg_overall_rating: 平均整体评分
    - avg_empathy_rating: 平均共情评分
    - avg_helpfulness_rating: 平均帮助程度评分
    - satisfaction_rate: 满意度百分比
    - top_tags: 热门标签
    """
    feedback_service = get_feedback_service()
    stats = feedback_service.get_user_feedback_stats(
        db=db,
        user_id=current_user.id,
        days=days
    )

    return stats


@router.get("/stats/system", summary="获取系统反馈统计")
async def get_system_feedback_stats(
    days: int = Query(default=7, ge=1, le=90, description="统计周期（天）"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    获取系统反馈统计（管理员用）
    """
    # TODO: 添加管理员权限验证
    feedback_service = get_feedback_service()
    stats = feedback_service.get_system_feedback_stats(
        db=db,
        days=days
    )

    return stats
