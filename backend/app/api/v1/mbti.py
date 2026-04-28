"""
MBTI测试接口
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import loguru
from datetime import datetime

from app.core.database import get_db
from app.models import User, MbtiQuestion, MbtiAnswer, MbtiResult, AiAssistant, AssistantCollection
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
        # 根据MBTI类型更新昵称
        new_nickname = mbti_service.generate_nickname_from_mbti(result["mbti_type"], user.nickname)
        user.nickname = new_nickname
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
        return None

    mbti_result = db.query(MbtiResult).filter(
        MbtiResult.id == current_user.mbti_result_id
    ).first()

    if not mbti_result:
        return None

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
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """获取AI助手列表"""
    mbti_service = get_mbti_service()

    tag_list = tags.split(",") if tags else None

    # 传递user_id以支持三位一体个性化推荐
    user_id = current_user.id if current_user else None
    assistants = mbti_service.get_recommended_assistants(db, mbti_type, tag_list, user_id)

    # 过滤推荐
    if recommended:
        assistants = [a for a in assistants if a.is_recommended]

    # 获取用户收藏列表
    favorited_ids = set()
    if current_user:
        favorites = db.query(AssistantCollection).filter(
            AssistantCollection.user_id == current_user.id
        ).all()
        favorited_ids = {f.assistant_id for f in favorites}

    # 构建返回数据，标记收藏状态
    assistant_list = []
    for a in assistants:
        schema = AiAssistantSchema.model_validate(a)
        schema.is_favorited = a.id in favorited_ids
        assistant_list.append(schema)

    return AiAssistantListResponse(
        total=len(assistant_list),
        list=assistant_list,
    )


@router.get("/assistants/recommended", summary="获取高匹配度AI助手（98%以上，需完成三位一体测评）")
async def get_high_match_assistants(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取高匹配度的AI助手列表（98%以上匹配度），要求完成三位一体测评
    
    如果没有找到98%以上匹配度的助手，会自动为用户创建一个专属定制化助手
    """
    mbti_service = get_mbti_service()

    # 获取高匹配度助手（98%以上）
    scored_assistants = mbti_service.get_high_match_recommended_assistants(
        db, 
        current_user.id,
        min_match_score=98.0
    )

    # 获取用户收藏列表
    favorited_ids = set()
    favorites = db.query(AssistantCollection).filter(
        AssistantCollection.user_id == current_user.id
    ).all()
    favorited_ids = {f.assistant_id for f in favorites}

    # 构建返回数据
    assistant_list = []
    for item in scored_assistants:
        assistant = item["assistant"]
        schema = AiAssistantSchema.model_validate(assistant)
        schema.is_favorited = assistant.id in favorited_ids
        schema.match_reason = item["match_reason"]
        schema.match_score = item["match_score"]
        assistant_list.append(schema)

    return AiAssistantListResponse(
        total=len(assistant_list),
        list=assistant_list,
    )


@router.get("/assistants/recommended/all", summary="获取所有推荐的AI助手（带推荐理由）")
async def get_all_recommended_assistants(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """获取所有推荐的AI助手列表（包含未完成三位一体测评的情况）"""
    mbti_service = get_mbti_service()

    user_id = current_user.id if current_user else None

    # 获取带推荐理由的助手列表
    scored_assistants = mbti_service.get_recommended_assistants_with_reason(db, user_id)

    # 获取用户收藏列表
    favorited_ids = set()
    if current_user:
        favorites = db.query(AssistantCollection).filter(
            AssistantCollection.user_id == current_user.id
        ).all()
        favorited_ids = {f.assistant_id for f in favorites}

    # 构建返回数据
    assistant_list = []
    for item in scored_assistants:
        assistant = item["assistant"]
        schema = AiAssistantSchema.model_validate(assistant)
        schema.is_favorited = assistant.id in favorited_ids
        schema.match_reason = item["match_reason"]
        schema.match_score = item["match_score"]
        assistant_list.append(schema)

    return AiAssistantListResponse(
        total=len(assistant_list),
        list=assistant_list,
    )


@router.post("/assistants/{assistant_id}/favorite", summary="收藏/取消收藏助手")
async def toggle_favorite(
    assistant_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """切换助手收藏状态"""
    # 检查助手是否存在
    assistant = db.query(AiAssistant).filter(AiAssistant.id == assistant_id).first()
    if not assistant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="助手不存在",
        )

    # 检查是否已收藏
    existing = db.query(AssistantCollection).filter(
        AssistantCollection.user_id == current_user.id,
        AssistantCollection.assistant_id == assistant_id,
    ).first()

    if existing:
        # 取消收藏
        db.delete(existing)
        db.commit()
        return {"is_favorited": False, "message": "已取消收藏"}
    else:
        # 添加收藏
        new_favorite = AssistantCollection(
            user_id=current_user.id,
            assistant_id=assistant_id,
        )
        db.add(new_favorite)
        db.commit()
        return {"is_favorited": True, "message": "收藏成功"}


@router.get("/assistants/favorites", summary="获取用户收藏的助手列表")
async def get_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取用户收藏的AI助手列表"""
    favorites = db.query(AssistantCollection).filter(
        AssistantCollection.user_id == current_user.id
    ).all()

    assistant_ids = [f.assistant_id for f in favorites]
    assistants = db.query(AiAssistant).filter(
        AiAssistant.id.in_(assistant_ids)
    ).all() if assistant_ids else []

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


# ==================== 快速版MBTI测试（12题）====================

@router.get("/quick/questions", summary="获取快速版测试题目")
async def get_quick_questions():
    """获取12题快速MBTI测试"""
    from app.services.mbti_service import get_quick_questions
    questions = get_quick_questions()
    return {"total": len(questions), "questions": questions}


@router.post("/quick/submit", summary="提交快速版测试答案")
async def submit_quick_test(
    request: MbtiTestSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """提交快速版MBTI测试答案"""
    from app.services.mbti_service import calculate_quick_result, get_quick_questions
    
    # 验证题目数量
    questions = get_quick_questions()
    if len(request.answers) != len(questions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"请回答所有{len(questions)}道题目"
        )
    
    # 计算结果
    result = calculate_quick_result([a.model_dump() for a in request.answers])
    
    # 保存到数据库（复用完整版逻辑）
    from app.models.mbti import MbtiType
    mbti_result = MbtiResult(
        user_id=current_user.id,
        mbti_type=MbtiType[result["mbti_type"]],
        ei_score=result["scores"]["EI"],
        sn_score=result["scores"]["SN"],
        tf_score=result["scores"]["TF"],
        jp_score=result["scores"]["JP"],
        report_json=str(result),
    )
    db.add(mbti_result)
    db.flush()
    
    user = db.query(User).filter(User.id == current_user.id).first()
    if user:
        user.mbti_type = MbtiType[result["mbti_type"]]
        user.mbti_result_id = mbti_result.id
        # 根据MBTI类型更新昵称
        new_nickname = mbti_service.generate_nickname_from_mbti(result["mbti_type"], user.nickname)
        user.nickname = new_nickname
        db.commit()
        db.refresh(user)
    else:
        db.commit()
    
    db.refresh(mbti_result)
    
    return {"mbti_type": result["mbti_type"], "scores": result["scores"]}