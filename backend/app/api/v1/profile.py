
"""
深度画像API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, Tuple
import json
import loguru

from app.core.database import get_db
from app.models import User, MbtiResult, SBTIResult, AttachmentResult, DeepPersonaProfile
from app.schemas.profile import (
    DeepPersonaProfile as DeepPersonaProfileSchema,
    ProfileSummary,
    GenerateProfileRequest,
    CompletionStatus,
    MbtiSection,
    SbtiSection,
    AttachmentSection,
    IntegratedInsights,
    AiCompanionRecommendation,
    AiPartnerListResponse,
    AiPartnerItem,
)
from app.models import AiAssistant
from app.services.profile_service import get_profile_service
from app.api.deps import get_current_user

router = APIRouter(prefix="/profile", tags=["深度画像"])


def _get_user_assessment_results(
    current_user: User,
    db: Session
) -> Tuple[Optional[MbtiResult], Optional[SBTIResult], Optional[AttachmentResult]]:
    """
    获取用户的测评结果（私有辅助函数，消除代码重复）
    
    Args:
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        (mbti_result, sbti_result, attachment_result) 三元组
    """
    mbti_result = None
    sbti_result = None
    attachment_result = None
    
    if hasattr(current_user, 'mbti_result_id') and current_user.mbti_result_id:
        mbti_result = db.query(MbtiResult).filter(
            MbtiResult.id == current_user.mbti_result_id
        ).first()
    
    if hasattr(current_user, 'sbti_result_id') and current_user.sbti_result_id:
        sbti_result = db.query(SBTIResult).filter(
            SBTIResult.user_id == current_user.id,
            SBTIResult.is_latest == True
        ).first()
    
    if hasattr(current_user, 'attachment_result_id') and current_user.attachment_result_id:
        attachment_result = db.query(AttachmentResult).filter(
            AttachmentResult.user_id == current_user.id,
            AttachmentResult.is_latest == True
        ).first()
    
    return mbti_result, sbti_result, attachment_result


def _calculate_completion_status(
    mbti_result: Optional[MbtiResult],
    sbti_result: Optional[SBTIResult],
    attachment_result: Optional[AttachmentResult]
) -> Tuple[CompletionStatus, int]:
    """
    计算测评完成状态和百分比（私有辅助函数）
    
    Args:
        mbti_result: MBTI结果
        sbti_result: SBTI结果
        attachment_result: 依恋风格结果
        
    Returns:
        (completion_status, completion_percentage) 二元组
    """
    completed_count = sum([
        mbti_result is not None,
        sbti_result is not None,
        attachment_result is not None,
    ])
    
    completion_percentage = int(completed_count / 3 * 100)
    
    if completed_count == 0:
        completion_status = CompletionStatus.PENDING
    elif completed_count == 3:
        completion_status = CompletionStatus.COMPLETE
    else:
        completion_status = CompletionStatus.PARTIAL
    
    return completion_status, completion_percentage


@router.get("/deep", summary="获取三位一体深度画像")
async def get_deep_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取MBTI + SBTI + 依恋风格三位一体的深度画像"""
    profile_service = get_profile_service()
    
    # 获取各模块结果（使用重构后的函数）
    mbti_result, sbti_result, attachment_result = _get_user_assessment_results(current_user, db)
    
    # 计算完成状态（使用重构后的函数）
    completion_status, completion_percentage = _calculate_completion_status(
        mbti_result, sbti_result, attachment_result
    )
    
    # 构建画像
    profile = profile_service.build_profile(
        mbti_result=mbti_result,
        sbti_result=sbti_result,
        attachment_result=attachment_result,
        user_id=current_user.id,
    )
    
    return DeepPersonaProfileSchema(
        user_id=current_user.id,
        completion_status=completion_status,
        completion_percentage=completion_percentage,
        mbti=profile.get("mbti"),
        sbti=profile.get("sbti"),
        attachment=profile.get("attachment"),
        integrated_insights=profile.get("integrated_insights"),
        ai_companion_recommendation=profile.get("ai_companion_recommendation"),
        generated_at=datetime.now(),
    )


@router.post("/generate", summary="重新生成深度画像")
async def generate_profile(
    request: Optional[GenerateProfileRequest] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """强制重新生成深度画像"""
    if request and not request.force_regenerate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="如需重新生成，请设置 force_regenerate=true",
        )
    
    profile_service = get_profile_service()
    
    # 获取各模块结果（使用重构后的函数）
    mbti_result, sbti_result, attachment_result = _get_user_assessment_results(current_user, db)
    
    # 检查是否至少有一个测评完成
    if not any([mbti_result, sbti_result, attachment_result]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请至少完成一个测评后再生成画像",
        )
    
    # 计算完成状态（使用重构后的函数）
    completion_status, completion_percentage = _calculate_completion_status(
        mbti_result, sbti_result, attachment_result
    )
    
    # 构建画像
    profile = profile_service.build_profile(
        mbti_result=mbti_result,
        sbti_result=sbti_result,
        attachment_result=attachment_result,
        user_id=current_user.id,
    )
    
    return DeepPersonaProfileSchema(
        user_id=current_user.id,
        completion_status=completion_status,
        completion_percentage=completion_percentage,
        mbti=profile.get("mbti"),
        sbti=profile.get("sbti"),
        attachment=profile.get("attachment"),
        integrated_insights=profile.get("integrated_insights"),
        ai_companion_recommendation=profile.get("ai_companion_recommendation"),
        generated_at=datetime.now(),
    )


@router.get("/summary", summary="获取画像摘要")
async def get_profile_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取简短画像摘要，用于对话上下文"""
    profile_service = get_profile_service()
    
    # 获取各模块结果（使用重构后的函数）
    mbti_result, sbti_result, attachment_result = _get_user_assessment_results(current_user, db)
    
    # 生成摘要
    summary = profile_service.generate_summary(
        mbti_result=mbti_result,
        sbti_result=sbti_result,
        attachment_result=attachment_result,
        user_id=current_user.id,
    )
    
    return ProfileSummary(
        user_id=current_user.id,
        summary=summary.get("summary", ""),
        personality_tags=summary.get("personality_tags", []),
        relationship_style=summary.get("relationship_style", ""),
        communication_tips=summary.get("communication_tips", []),
    )


@router.get("/ai-partners", summary="获取推荐的AI伴侣")
async def get_ai_partners(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """根据用户的人格画像（MBTI + SBTI + 依恋风格）获取推荐的AI伴侣列表"""
    # 使用mbti_service的综合匹配算法获取推荐助手
    from app.services.mbti_service import get_mbti_service
    mbti_service = get_mbti_service()

    # 获取高匹配度助手（85%以上），如果没有会自动创建定制化助手
    scored_assistants = mbti_service.get_high_match_recommended_assistants(
        db=db,
        user_id=current_user.id,
        min_match_score=85.0
    )

    # 限制返回数量
    scored_assistants = scored_assistants[:6]

    # 构建响应
    partners = []
    for item in scored_assistants:
        assistant = item["assistant"]

        # 解析标签
        tags = assistant.tags.split(',') if assistant.tags else []

        partners.append(AiPartnerItem(
            id=assistant.id,
            name=assistant.name,
            avatar=assistant.avatar,
            mbti_type=assistant.mbti_type.value if hasattr(assistant.mbti_type, 'value') else str(assistant.mbti_type),
            personality=assistant.personality,
            attachment_style=None,
            match_reason=item["match_reason"],
            match_score=item["match_score"],
            tags=tags,
        ))

    return AiPartnerListResponse(
        total=len(partners),
        list=partners,
    )

