"""
MBTI测试接口
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import loguru
from datetime import datetime

from app.core.database import get_db
from app.models import User, MbtiQuestion, MbtiAnswer, MbtiResult, AiAssistant
from app.models.mbti import MbtiType
from app.schemas.mbti import (
    MbtiQuestionSchema,
    MbtiQuestionListResponse,
    MbtiTestSubmit,
    MbtiResultSchema,
    MbtiTestStartResponse,
    AiAssistantSchema,
    AiAssistantListResponse,
)
from app.services.mbti_service import get_mbti_service
from app.api.deps import get_current_user, get_current_user_optional

router = APIRouter(prefix="/mbti", tags=["MBTI测试"])


@router.get("/questions", summary="获取测试题目")
async def get_questions(
    dimension: Optional[str] = None,
    force_refresh: bool = False,
    db: Session = Depends(get_db),
):
    """获取MBTI测试题目"""
    mbti_service = get_mbti_service()

    mbti_service.seed_questions(db, force=force_refresh)

    questions = mbti_service.get_questions(db, dimension)

    return MbtiQuestionListResponse(
        total=len(questions),
        questions=[MbtiQuestionSchema.model_validate(q) for q in questions],
    )


@router.post("/start", summary="开始测试")
async def start_test(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """开始MBTI测试"""
    import uuid
    if current_user:
        session_id = f"mbti_{current_user.id}_{int(datetime.now().timestamp())}"
    else:
        session_id = f"mbti_visitor_{uuid.uuid4().hex[:12]}"

    return MbtiTestStartResponse(
        session_id=session_id,
        total_questions=48,
        estimated_time=15,
    )


@router.post("/submit", summary="提交测试答案")
async def submit_test(
    request: MbtiTestSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """提交MBTI测试答案"""
    mbti_service = get_mbti_service()

    answers = [answer.model_dump() for answer in request.answers]

    result = mbti_service.calculate_result(db, current_user.id, answers)

    for answer in answers:
        db.add(MbtiAnswer(
            user_id=current_user.id,
            question_id=answer["question_id"],
            answer=answer["answer"],
            score=1 if answer["answer"] == "A" else 2,
        ))

    # 保存结果
    import json
    mbti_result = MbtiResult(
        user_id=current_user.id,
        mbti_type=MbtiType[result["mbti_type"]],
        ei_score=result["ei_score"],
        sn_score=result["sn_score"],
        tf_score=result["tf_score"],
        jp_score=result["jp_score"],
        report_json=json.dumps(result),
    )
    db.add(mbti_result)
    db.flush()

    user = db.query(User).filter(User.id == current_user.id).first()
    if user:
        user.mbti_type = result["mbti_type"]
        user.mbti_result_id = mbti_result.id
        db.commit()
        db.refresh(user)
    else:
        db.commit()

    db.refresh(mbti_result)

    # 返回结果
    return MbtiResultSchema(
        id=mbti_result.id,
        mbti_type=mbti_result.mbti_type.value,
        ei_score=mbti_result.ei_score,
        sn_score=mbti_result.sn_score,
        tf_score=mbti_result.tf_score,
        jp_score=mbti_result.jp_score,
        dimensions=result["dimensions"],
        personality=result["personality"],
        strengths=result["strengths"],
        weaknesses=result["weaknesses"],
        suitable_jobs=result["suitable_jobs"],
        relationship_tips=result["relationship_tips"],
        career_advice=result["career_advice"],
        created_at=mbti_result.created_at,
    )


@router.get("/result", summary="获取测试结果")
async def get_result(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取用户的MBTI测试结果"""
    if not current_user.mbti_result_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="尚未完成MBTI测试",
        )

    mbti_result = db.query(MbtiResult).filter(
        MbtiResult.id == current_user.mbti_result_id
    ).first()

    if not mbti_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="测试结果不存在",
        )

    # 解析report_json
    import ast
    try:
        report = ast.literal_eval(mbti_result.report_json)
    except:
        report = {}

    return MbtiResultSchema(
        id=mbti_result.id,
        mbti_type=mbti_result.mbti_type.value,
        ei_score=mbti_result.ei_score,
        sn_score=mbti_result.sn_score,
        tf_score=mbti_result.tf_score,
        jp_score=mbti_result.jp_score,
        dimensions=report.get("dimensions", []),
        personality=report.get("personality", ""),
        strengths=report.get("strengths", []),
        weaknesses=report.get("weaknesses", []),
        suitable_jobs=report.get("suitable_jobs", []),
        relationship_tips=report.get("relationship_tips", ""),
        career_advice=report.get("career_advice", ""),
        created_at=mbti_result.created_at,
    )


@router.get("/assistants", summary="获取AI助手列表")
async def get_assistants(
    mbti_type: Optional[str] = None,
    tags: Optional[str] = None,
    recommended: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    """获取AI助手列表"""
    mbti_service = get_mbti_service()

    tag_list = tags.split(",") if tags else None

    assistants = mbti_service.get_recommended_assistants(db, mbti_type, tag_list)

    # 过滤推荐
    if recommended:
        assistants = [a for a in assistants if a.is_recommended]

    return AiAssistantListResponse(
        total=len(assistants),
        list=[AiAssistantSchema.model_validate(a) for a in assistants],
    )


@router.get("/assistants/{assistant_id}", summary="获取助手详情")
async def get_assistant(
    assistant_id: int,
    db: Session = Depends(get_db),
):
    """获取AI助手详情"""
    assistant = db.query(AiAssistant).filter(AiAssistant.id == assistant_id).first()

    if not assistant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="助手不存在",
        )

    return AiAssistantSchema.model_validate(assistant)