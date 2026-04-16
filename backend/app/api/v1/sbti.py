"""
SBTI测评API
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import json
import loguru

from app.core.database import get_db
from app.models import User, SBTIQuestion, SBTIAnswer, SBTIResult
from app.schemas.sbti import (
    SbtiQuestionSchema,
    SbtiQuestionListResponse,
    SbtiTestSubmit,
    SbtiResultResponse,
    SbtiThemeDetailResponse,
    ThemeInfo,
)
from app.services.sbti_service import get_sbti_service, SBTIService
from app.api.deps import get_current_user

router = APIRouter(prefix="/sbti", tags=["SBTI测评"])


# 才干主题详细信息
THEME_DETAILS = {
    "成就": {
        "name": "成就",
        "domain": "执行力",
        "description": "你是一个追求卓越的人，享受完成任务和达成目标的成就感。",
        "strengths": ["勤奋努力", "目标导向", "自我驱动", "高效执行"],
        "weaknesses": ["可能过度工作", "难以放松", "对低效缺乏耐心"],
        "relationships": ["欣赏同样努力的伴侣", "需要对方的理解和支持"],
        "career_paths": ["项目管理", "企业管理者", "创业者"],
        "growth_tips": ["学会欣赏过程中的美好", "适当休息和放松"],
    },
    "行动": {
        "name": "行动",
        "domain": "执行力",
        "description": "你喜欢立即行动，快速将想法付诸实践，不喜欢拖延。",
        "strengths": ["执行力强", "果断勇敢", "善于把握机会", "不怕失败"],
        "weaknesses": ["可能冲动", "考虑不够周全", "缺乏耐心"],
        "relationships": ["欣赏行动力强的伴侣", "需要学会倾听"],
        "career_paths": ["企业家", "销售", "应急响应"],
        "growth_tips": ["三思而后行", "多考虑他人感受"],
    },
    "适应": {
        "name": "适应",
        "domain": "执行力",
        "description": "你灵活变通，能够快速适应变化的环境和情况。",
        "strengths": ["灵活", "务实", "善于应变", "活在当下"],
        "weaknesses": ["可能缺乏长期规划", "原则性不强"],
        "relationships": ["善于处理冲突", "适应力强"],
        "career_paths": ["咨询", "外交", "项目管理"],
        "growth_tips": ["培养长期视角", "学会坚持"],
    },
    "关联": {
        "name": "关联",
        "domain": "关系建立",
        "description": "你相信万事皆有关联，重视人际之间的联系和共同点。",
        "strengths": ["善于建立关系", "共情能力强", "团队精神", "包容开放"],
        "weaknesses": ["可能过度在意他人", "难以拒绝"],
        "relationships": ["善于维护关系", "重视深层连接"],
        "career_paths": ["咨询", "社会工作", "人力资源"],
        "growth_tips": ["设立边界", "学会说不"],
    },
    "体谅": {
        "name": "体谅",
        "domain": "关系建立",
        "description": "你善于理解他人，能够设身处地为别人着想。",
        "strengths": ["共情能力强", "善解人意", "支持他人", "敏感细腻"],
        "weaknesses": ["可能过度承担他人情绪", "难以保持客观"],
        "relationships": ["非常体贴的伴侣", "需要学会保护自己"],
        "career_paths": ["心理咨询", "护理", "教师"],
        "growth_tips": ["设立情绪边界", "学会自我关怀"],
    },
    "沟通": {
        "name": "沟通",
        "domain": "影响力",
        "description": "你善于表达和交流，能够激发他人的热情和想法。",
        "strengths": ["表达能力强", "富有感染力", "善于激励", "社交能力好"],
        "weaknesses": ["可能话多", "深度不够"],
        "relationships": ["善于表达爱意", "需要学会倾听"],
        "career_paths": ["销售", "教师", "主持人", "营销"],
        "growth_tips": ["多倾听少说", "注重深度交流"],
    },
    "分析": {
        "name": "分析",
        "domain": "战略思维",
        "description": "你善于深入分析问题，寻找事物背后的逻辑和规律。",
        "strengths": ["分析能力强", "理性客观", "逻辑清晰", "善于研究"],
        "weaknesses": ["可能过于理性", "忽视情感因素"],
        "relationships": ["理性的讨论伙伴", "需要学会情感表达"],
        "career_paths": ["研究", "技术", "咨询", "金融分析"],
        "growth_tips": ["平衡理性与情感", "学会接纳不确定性"],
    },
    "专注": {
        "name": "专注",
        "domain": "执行力",
        "description": "你能够排除干扰，全身心投入重要的事情。",
        "strengths": ["专注", "有毅力", "有条理", "高效"],
        "weaknesses": ["可能过于狭隘", "忽视其他重要事项"],
        "relationships": ["专一的伴侣", "需要平衡工作与生活"],
        "career_paths": ["研究", "技术", "财务"],
        "growth_tips": ["拓宽关注范围", "学会放松"],
    },
    "战略": {
        "name": "战略",
        "domain": "战略思维",
        "description": "你善于制定长远计划，能够看到全局和可能性。",
        "strengths": ["全局视角", "善于规划", "预见未来", "创新思维"],
        "weaknesses": ["可能忽视执行细节", "过于理想化"],
        "relationships": ["有远见的伴侣", "需要关注当下感受"],
        "career_paths": ["战略规划", "创业", "投资", "管理咨询"],
        "growth_tips": ["关注执行细节", "学以致用"],
    },
    "学习": {
        "name": "学习",
        "domain": "战略思维",
        "description": "你热爱学习，享受获取新知识和技能的过程。",
        "strengths": ["学习能力强", "好奇心强", "适应力强", "谦虚好学"],
        "weaknesses": ["可能学而不用", "容易分心"],
        "relationships": ["共同成长的伴侣", "需要将学习转化为行动"],
        "career_paths": ["教育", "研究", "技术"],
        "growth_tips": ["专注深度学习", "将知识转化为能力"],
    },
}


@router.get("/questions", summary="获取SBTI题目")
async def get_questions(
    force_refresh: bool = False,
    db: Session = Depends(get_db),
):
    """获取48道SBTI测评题目"""
    sbti_service = get_sbti_service()

    sbti_service.seed_questions(db, force=force_refresh)

    questions = sbti_service.get_questions(db)

    return SbtiQuestionListResponse(
        total=len(questions),
        questions=[SbtiQuestionSchema.model_validate(q) for q in questions],
    )


@router.post("/submit", summary="提交SBTI测试答案")
async def submit_test(
    request: SbtiTestSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """提交48道SBTI测评答案，计算并返回结果"""
    if len(request.answers) != 48:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="必须回答全部48道题目",
        )

    sbti_service = get_sbti_service()

    answers = [answer.model_dump() for answer in request.answers]
    result = sbti_service.calculate_result(db, current_user.id, answers)

    # 保存答案并计算得分
    for answer_data in answers:
        question = (
            db.query(SBTIQuestion)
            .filter(SBTIQuestion.id == answer_data["question_id"])
            .first()
        )

        if question:
            selected_theme = (
                question.theme_a if answer_data["answer"] == "A" else question.theme_b
            )
            weight = (
                question.weight_a if answer_data["answer"] == "A" else question.weight_b
            )

            db.add(
                SBTIAnswer(
                    user_id=current_user.id,
                    question_id=answer_data["question_id"],
                    answer=answer_data["answer"],
                    selected_theme=selected_theme,
                    score=weight,
                )
            )

    # 标记旧结果为非最新
    db.query(SBTIResult).filter(
        SBTIResult.user_id == current_user.id, SBTIResult.is_latest == True
    ).update({"is_latest": False})

    # 保存结果
    sbti_result = SBTIResult(
        user_id=current_user.id,
        all_themes_scores=result["all_themes_scores"],
        top_theme_1=result["top5_themes"][0] if len(result["top5_themes"]) > 0 else "",
        top_theme_2=result["top5_themes"][1] if len(result["top5_themes"]) > 1 else "",
        top_theme_3=result["top5_themes"][2] if len(result["top5_themes"]) > 2 else "",
        top_theme_4=result["top5_themes"][3] if len(result["top5_themes"]) > 3 else "",
        top_theme_5=result["top5_themes"][4] if len(result["top5_themes"]) > 4 else "",
        executing_score=result["domain_scores"].get("执行力", 0),
        influencing_score=result["domain_scores"].get("影响力", 0),
        relationship_score=result["domain_scores"].get("关系建立", 0),
        strategic_score=result["domain_scores"].get("战略思维", 0),
        dominant_domain=result["dominant_domain"],
        report_json=json.dumps(result, ensure_ascii=False),
        version=1,
        is_latest=True,
    )
    db.add(sbti_result)
    db.commit()
    db.refresh(sbti_result)

    # 更新用户的SBTI结果关联
    user = db.query(User).filter(User.id == current_user.id).first()
    if user and hasattr(user, "sbti_result_id"):
        user.sbti_result_id = sbti_result.id
        db.commit()

    # 返回结果
    return SbtiResultResponse(
        id=sbti_result.id,
        top5_themes=result["top5_themes"],
        top5_scores=result["top5_scores"],
        domain_scores=result["domain_scores"],
        dominant_domain=result["dominant_domain"],
        report=result,
        created_at=sbti_result.created_at,
    )


@router.get("/result", summary="获取SBTI结果")
async def get_result(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前用户的SBTI测评结果"""
    if not hasattr(current_user, "sbti_result_id") or not current_user.sbti_result_id:
        return None

    sbti_result = (
        db.query(SBTIResult)
        .filter(SBTIResult.user_id == current_user.id, SBTIResult.is_latest == True)
        .first()
    )

    if not sbti_result:
        return None

    # 解析report_json
    report = {}
    if sbti_result.report_json:
        try:
            report = json.loads(sbti_result.report_json)
        except:
            report = {}

    return SbtiResultResponse(
        id=sbti_result.id,
        top5_themes=[
            sbti_result.top_theme_1,
            sbti_result.top_theme_2,
            sbti_result.top_theme_3,
            sbti_result.top_theme_4,
            sbti_result.top_theme_5,
        ],
        top5_scores=report.get("top5_scores", []),
        domain_scores={
            "执行力": sbti_result.executing_score,
            "影响力": sbti_result.influencing_score,
            "关系建立": sbti_result.relationship_score,
            "战略思维": sbti_result.strategic_score,
        },
        dominant_domain=sbti_result.dominant_domain,
        report=report,
        created_at=sbti_result.created_at,
    )


@router.get("/themes/{theme}", summary="获取才干主题详情")
async def get_theme_detail(
    theme: str,
    db: Session = Depends(get_db),
):
    """获取特定才干主题的详细信息"""
    theme_info = THEME_DETAILS.get(theme)

    if not theme_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到主题: {theme}",
        )

    return SbtiThemeDetailResponse(
        theme=theme,
        info=ThemeInfo(**theme_info),
    )
