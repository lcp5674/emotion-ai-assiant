"""
依恋风格API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import json
import loguru

from app.core.database import get_db
from app.models import User, AttachmentQuestion, AttachmentAnswer, AttachmentResult
from app.schemas.attachment import (
    AttachmentQuestionSchema,
    AttachmentQuestionListResponse,
    AttachmentTestSubmit,
    AttachmentResultResponse,
)
from app.services.attachment_service import get_attachment_service
from app.api.deps import get_current_user

router = APIRouter(prefix="/attachment", tags=["依恋风格"])


@router.get("/questions", summary="获取依恋风格题目")
async def get_questions(
    force_refresh: bool = False,
    db: Session = Depends(get_db),
):
    """获取10道依恋风格测评题目"""
    attachment_service = get_attachment_service()
    
    # 确保题目已初始化
    attachment_service.seed_questions(db, force=force_refresh)
    
    questions = attachment_service.get_questions(db)
    
    return AttachmentQuestionListResponse(
        total=len(questions),
        questions=[AttachmentQuestionSchema.model_validate(q) for q in questions],
    )


@router.post("/submit", summary="提交依恋风格测试答案")
async def submit_test(
    request: AttachmentTestSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """提交10道依恋风格测评答案，计算并返回结果"""
    if len(request.answers) != 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="必须回答全部10道题目",
        )
    
    attachment_service = get_attachment_service()
    
    # 计算结果
    answers = [answer.model_dump() for answer in request.answers]
    result = await attachment_service.calculate_result(db, current_user.id, answers)
    
    # 保存答案
    for answer_data in answers:
        db.add(AttachmentAnswer(
            user_id=current_user.id,
            question_id=answer_data["question_id"],
            score=answer_data["score"],
        ))
    
    # 标记旧结果为非最新
    db.query(AttachmentResult).filter(
        AttachmentResult.user_id == current_user.id,
        AttachmentResult.is_latest == True
    ).update({"is_latest": False})
    
    # 保存结果
    attachment_result = AttachmentResult(
        user_id=current_user.id,
        anxiety_score=result["anxiety_score"],
        avoidance_score=result["avoidance_score"],
        attachment_style=result["attachment_style"],
        characteristics=result["characteristics"],
        relationship_tips=result["relationship_tips"],
        self_growth_tips=result["self_growth_tips"],
        report_json=json.dumps(result, ensure_ascii=False),
        version=1,
        is_latest=True,
    )
    db.add(attachment_result)
    db.commit()
    db.refresh(attachment_result)
    
    # 更新用户的依恋风格结果关联
    user = db.query(User).filter(User.id == current_user.id).first()
    if user and hasattr(user, 'attachment_result_id'):
        user.attachment_result_id = attachment_result.id
        db.commit()
    
    # 返回结果
    return AttachmentResultResponse(
        id=attachment_result.id,
        style=result["style"],
        anxiety_score=result["anxiety_score"],
        avoidance_score=result["avoidance_score"],
        characteristics=result["characteristics"],
        relationship_tips=result["relationship_tips"],
        self_growth_tips=result["self_growth_tips"],
        created_at=attachment_result.created_at,
    )


@router.get("/result", summary="获取依恋风格结果")
async def get_result(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前用户的依恋风格测评结果"""
    if not hasattr(current_user, 'attachment_result_id') or not current_user.attachment_result_id:
        return None

    attachment_result = db.query(AttachmentResult).filter(
        AttachmentResult.user_id == current_user.id,
        AttachmentResult.is_latest == True
    ).first()

    if not attachment_result:
        return None
    
    # 获取风格 - 从枚举值映射回中文名称
    ENUM_TO_CHINESE = {
        "secure": "安全型",
        "anxious": "焦虑型",
        "avoidant": "回避型",
        "disorganized": "混乱型",
    }
    style_value = attachment_result.attachment_style.value if hasattr(attachment_result.attachment_style, 'value') else str(attachment_result.attachment_style)
    style_name = ENUM_TO_CHINESE.get(style_value, style_value)

    # 获取特征列表
    characteristics = attachment_result.characteristics if isinstance(attachment_result.characteristics, list) else []

    return AttachmentResultResponse(
        id=attachment_result.id,
        style=style_name,
        anxiety_score=attachment_result.anxiety_score,
        avoidance_score=attachment_result.avoidance_score,
        characteristics=characteristics,
        relationship_tips=attachment_result.relationship_tips or "",
        self_growth_tips=attachment_result.self_growth_tips or "",
        created_at=attachment_result.created_at,
    )
