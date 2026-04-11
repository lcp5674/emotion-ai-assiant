"""
Admin API - 系统管理
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta, date
import os
import loguru

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models import User, SystemConfig, Conversation, Message, EmotionDiary, MbtiResult, ContentAuditQueue
from app.models.user import MemberLevel
from app.models.chat import ConversationStatus

router = APIRouter(prefix="/admin", tags=["管理"])

LLM_CONFIG_KEYS = [
    "LLM_PROVIDER",
    "OPENAI_API_KEY", "OPENAI_MODEL", "OPENAI_BASE_URL",
    "ANTHROPIC_API_KEY", "ANTHROPIC_MODEL", "ANTHROPIC_BASE_URL",
    "GLM_API_KEY", "GLM_MODEL", "GLM_BASE_URL",
    "QWEN_API_KEY", "QWEN_MODEL", "QWEN_BASE_URL",
    "MINIMAX_API_KEY", "MINIMAX_MODEL", "MINIMAX_BASE_URL",
    "ERNIE_API_KEY", "ERNIE_MODEL", "ERNIE_BASE_URL",
    "HUNYUAN_API_KEY", "HUNYUAN_MODEL", "HUNYUAN_BASE_URL",
    "SPARK_API_KEY", "SPARK_MODEL", "SPARK_BASE_URL",
    "DOUBAO_API_KEY", "DOUBAO_MODEL", "DOUBAO_BASE_URL",
    "SILICONFLOW_API_KEY", "SILICONFLOW_MODEL", "SILICONFLOW_BASE_URL",
]


class DashboardStatsResponse(BaseModel):
    """仪表盘统计响应"""
    user_count: int
    user_today: int
    active_users: int
    paid_users: int

    conversation_count: int
    conversation_today: int
    message_count: int
    message_today: int

    mbti_tested: int
    mbti_today: int
    diary_count: int
    diary_today: int


class UserListResponse(BaseModel):
    """用户列表响应"""
    total: int
    list: List[dict]


class ConversationStatsResponse(BaseModel):
    """对话统计响应"""
    total_conversations: int
    total_messages: int
    active_conversations: int
    avg_messages_per_conversation: float


class DateRangeStatsResponse(BaseModel):
    """日期范围统计响应"""
    dates: List[str]
    user_counts: List[int]
    message_counts: List[int]
    conversation_counts: List[int]


def load_llm_config_to_memory(db: Session):
    from app.core.config import settings
    
    configs = db.query(SystemConfig).filter(SystemConfig.config_key.in_(LLM_CONFIG_KEYS)).all()
    for config in configs:
        setattr(settings, config.config_key, config.config_value)
        os.environ[config.config_key] = config.config_value or ""


class SystemConfigUpdate(BaseModel):
    llm_provider: Optional[str] = None
    openai_api_key: Optional[str] = None
    openai_model: Optional[str] = None
    openai_base_url: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    anthropic_model: Optional[str] = None
    anthropic_base_url: Optional[str] = None
    glm_api_key: Optional[str] = None
    glm_model: Optional[str] = None
    glm_base_url: Optional[str] = None
    qwen_api_key: Optional[str] = None
    qwen_model: Optional[str] = None
    qwen_base_url: Optional[str] = None
    minimax_api_key: Optional[str] = None
    minimax_model: Optional[str] = None
    minimax_base_url: Optional[str] = None
    ernie_api_key: Optional[str] = None
    ernie_model: Optional[str] = None
    ernie_base_url: Optional[str] = None
    hunyuan_api_key: Optional[str] = None
    hunyuan_model: Optional[str] = None
    hunyuan_base_url: Optional[str] = None
    spark_api_key: Optional[str] = None
    spark_model: Optional[str] = None
    spark_base_url: Optional[str] = None
    doubao_api_key: Optional[str] = None
    doubao_model: Optional[str] = None
    doubao_base_url: Optional[str] = None
    siliconflow_api_key: Optional[str] = None
    siliconflow_model: Optional[str] = None
    siliconflow_base_url: Optional[str] = None


class AssistantUpdate(BaseModel):
    name: Optional[str] = None
    personality: Optional[str] = None
    speaking_style: Optional[str] = None
    expertise: Optional[str] = None
    greeting: Optional[str] = None
    tags: Optional[str] = None
    is_recommended: Optional[bool] = None
    is_active: Optional[bool] = None


class AssistantCreate(BaseModel):
    name: str
    mbti_type: str
    personality: Optional[str] = None
    speaking_style: Optional[str] = None
    expertise: Optional[str] = None
    greeting: Optional[str] = None
    tags: Optional[str] = None
    is_recommended: bool = False


def require_admin(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user


@router.get("/config", summary="获取系统配置")
async def get_config(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    from app.core.config import settings
    
    load_llm_config_to_memory(db)
    
    return {
        "llm_provider": settings.LLM_PROVIDER,
        "openai_model": settings.OPENAI_MODEL,
        "openai_base_url": settings.OPENAI_BASE_URL,
        "anthropic_model": settings.ANTHROPIC_MODEL,
        "anthropic_base_url": settings.ANTHROPIC_BASE_URL,
        "glm_model": settings.GLM_MODEL,
        "glm_base_url": settings.GLM_BASE_URL,
        "qwen_model": settings.QWEN_MODEL,
        "qwen_base_url": settings.QWEN_BASE_URL,
        "minimax_model": settings.MINIMAX_MODEL,
        "minimax_base_url": settings.MINIMAX_BASE_URL,
        "ernie_model": settings.ERNIE_MODEL,
        "ernie_base_url": settings.ERNIE_BASE_URL,
        "hunyuan_model": settings.HUNYUAN_MODEL,
        "hunyuan_base_url": settings.HUNYUAN_BASE_URL,
        "spark_model": settings.SPARK_MODEL,
        "spark_base_url": settings.SPARK_BASE_URL,
        "doubao_model": settings.DOUBAO_MODEL,
        "doubao_base_url": settings.DOUBAO_BASE_URL,
        "siliconflow_model": settings.SILICONFLOW_MODEL,
        "siliconflow_base_url": settings.SILICONFLOW_BASE_URL,
        "has_openai_key": bool(settings.OPENAI_API_KEY),
        "has_anthropic_key": bool(settings.ANTHROPIC_API_KEY),
        "has_glm_key": bool(settings.GLM_API_KEY),
        "has_qwen_key": bool(settings.QWEN_API_KEY),
        "has_minimax_key": bool(settings.MINIMAX_API_KEY),
        "has_ernie_key": bool(settings.ERNIE_API_KEY),
        "has_hunyuan_key": bool(settings.HUNYUAN_API_KEY),
        "has_spark_key": bool(settings.SPARK_API_KEY),
        "has_doubao_key": bool(settings.DOUBAO_API_KEY),
        "has_siliconflow_key": bool(settings.SILICONFLOW_API_KEY),
    }


@router.post("/config", summary="更新系统配置")
async def update_config(
    config: SystemConfigUpdate,
    validate: bool = False,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    updates = {}
    
    config_map = {
        "llm_provider": "LLM_PROVIDER",
        "openai_api_key": "OPENAI_API_KEY",
        "openai_model": "OPENAI_MODEL",
        "openai_base_url": "OPENAI_BASE_URL",
        "anthropic_api_key": "ANTHROPIC_API_KEY",
        "anthropic_model": "ANTHROPIC_MODEL",
        "anthropic_base_url": "ANTHROPIC_BASE_URL",
        "glm_api_key": "GLM_API_KEY",
        "glm_model": "GLM_MODEL",
        "glm_base_url": "GLM_BASE_URL",
        "qwen_api_key": "QWEN_API_KEY",
        "qwen_model": "QWEN_MODEL",
        "qwen_base_url": "QWEN_BASE_URL",
        "minimax_api_key": "MINIMAX_API_KEY",
        "minimax_model": "MINIMAX_MODEL",
        "minimax_base_url": "MINIMAX_BASE_URL",
        "ernie_api_key": "ERNIE_API_KEY",
        "ernie_model": "ERNIE_MODEL",
        "ernie_base_url": "ERNIE_BASE_URL",
        "hunyuan_api_key": "HUNYUAN_API_KEY",
        "hunyuan_model": "HUNYUAN_MODEL",
        "hunyuan_base_url": "HUNYUAN_BASE_URL",
        "spark_api_key": "SPARK_API_KEY",
        "spark_model": "SPARK_MODEL",
        "spark_base_url": "SPARK_BASE_URL",
        "doubao_api_key": "DOUBAO_API_KEY",
        "doubao_model": "DOUBAO_MODEL",
        "doubao_base_url": "DOUBAO_BASE_URL",
        "siliconflow_api_key": "SILICONFLOW_API_KEY",
        "siliconflow_model": "SILICONFLOW_MODEL",
        "siliconflow_base_url": "SILICONFLOW_BASE_URL",
    }
    
    for frontend_key, backend_key in config_map.items():
        value = getattr(config, frontend_key, None)
        if value is not None:
            updates[backend_key] = value
    
    temp_settings = {}
    for key, value in updates.items():
        temp_settings[key] = value
        os.environ[key] = str(value)
    
    for key, value in temp_settings.items():
        existing = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
        if existing:
            existing.config_value = str(value)
        else:
            new_config = SystemConfig(config_key=key, config_value=str(value))
            db.add(new_config)
    
    db.commit()
    
    load_llm_config_to_memory(db)
    
    import app.services.llm.factory as llm_factory
    llm_factory._llm_provider = None
    
    if validate:
        try:
            from app.services.llm import chat
            result = await chat(
                messages=[{"role": "user", "content": "Hi"}],
                temperature=0.7,
                max_tokens=100,
            )
            return {
                "message": "配置已更新并验证成功",
                "changes": list(updates.keys()),
                "validation": {"success": True, "response": result[:100] if result else ""}
            }
        except Exception as e:
            return {
                "message": "配置已保存，但连接测试失败",
                "changes": list(updates.keys()),
                "validation": {"success": False, "error": str(e)}
            }
    
    return {"message": "配置已更新", "changes": list(updates.keys())}


@router.post("/test", summary="测试LLM连接")
async def test_llm(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    from app.services.llm import chat
    from app.core.config import settings
    
    load_llm_config_to_memory(db)
    import app.services.llm.factory as llm_factory
    llm_factory._llm_provider = None
    
    try:
        result = await chat(
            messages=[{"role": "user", "content": "你好"}],
            temperature=0.7,
            max_tokens=500,
        )
        return {"success": True, "provider": settings.LLM_PROVIDER, "response": result}
    except Exception as e:
        return {"success": False, "provider": settings.LLM_PROVIDER, "error": str(e)}


@router.get("/assistants", summary="获取AI助手列表")
async def get_assistants(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """获取所有AI助手"""
    from app.models import AiAssistant
    assistants = db.query(AiAssistant).all()
    return {
        "list": [
            {
                "id": a.id,
                "name": a.name,
                "mbti_type": a.mbti_type,
                "personality": a.personality,
                "speaking_style": a.speaking_style,
                "expertise": a.expertise,
                "greeting": a.greeting,
                "tags": a.tags,
                "is_recommended": a.is_recommended,
                "is_active": a.is_active,
            }
            for a in assistants
        ]
    }


@router.post("/assistants", summary="创建AI助手")
async def create_assistant(
    assistant: AssistantCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """创建新的AI助手"""
    from app.models import AiAssistant
    from app.models.mbti import MbtiType
    
    new_assistant = AiAssistant(
        name=assistant.name,
        mbti_type=MbtiType[assistant.mbti_type],
        personality=assistant.personality or "",
        speaking_style=assistant.speaking_style or "",
        expertise=assistant.expertise or "",
        greeting=assistant.greeting or "",
        tags=assistant.tags or "",
        is_recommended=assistant.is_recommended,
        is_active=True,
    )
    db.add(new_assistant)
    db.commit()
    db.refresh(new_assistant)
    
    return {
        "id": new_assistant.id,
        "name": new_assistant.name,
        "mbti_type": new_assistant.mbti_type.value,
    }


@router.put("/assistants/{assistant_id}", summary="更新AI助手")
async def update_assistant(
    assistant_id: int,
    updates: AssistantUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """更新AI助手信息"""
    from app.models import AiAssistant
    
    assistant = db.query(AiAssistant).filter(AiAssistant.id == assistant_id).first()
    if not assistant:
        raise HTTPException(status_code=404, detail="助手不存在")
    
    if updates.name is not None:
        assistant.name = updates.name
    if updates.personality is not None:
        assistant.personality = updates.personality
    if updates.speaking_style is not None:
        assistant.speaking_style = updates.speaking_style
    if updates.expertise is not None:
        assistant.expertise = updates.expertise
    if updates.greeting is not None:
        assistant.greeting = updates.greeting
    if updates.tags is not None:
        assistant.tags = updates.tags
    if updates.is_recommended is not None:
        assistant.is_recommended = updates.is_recommended
    if updates.is_active is not None:
        assistant.is_active = updates.is_active
    
    db.commit()
    db.refresh(assistant)
    
    return {
        "id": assistant.id,
        "name": assistant.name,
        "mbti_type": assistant.mbti_type.value,
    }


@router.delete("/assistants/{assistant_id}", summary="删除AI助手")
async def delete_assistant(
    assistant_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """删除AI助手"""
    from app.models import AiAssistant

    assistant = db.query(AiAssistant).filter(AiAssistant.id == assistant_id).first()
    if not assistant:
        raise HTTPException(status_code=404, detail="助手不存在")

    db.delete(assistant)
    db.commit()

    return {"message": "删除成功"}


@router.get("/dashboard", summary="获取仪表盘统计")
async def get_dashboard_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """获取系统整体统计"""
    from datetime import date, timedelta

    today = date.today()
    week_ago = today - timedelta(days=7)

    # 用户统计
    user_count = db.query(User).count()
    user_today = db.query(User).filter(
        func.date(User.created_at) == today
    ).count()

    active_users = db.query(User).filter(
        func.date(User.last_login_at) >= week_ago
    ).count()

    paid_users = db.query(User).filter(
        User.member_level != MemberLevel.FREE
    ).count()

    # 对话统计
    conversation_count = db.query(Conversation).count()
    conversation_today = db.query(Conversation).filter(
        func.date(Conversation.created_at) == today
    ).count()

    message_count = db.query(Message).count()
    message_today = db.query(Message).filter(
        func.date(Message.created_at) == today
    ).count()

    # MBTI测试统计
    mbti_tested = db.query(MbtiResult).count()
    mbti_today = db.query(MbtiResult).filter(
        func.date(MbtiResult.created_at) == today
    ).count()

    # 日记统计
    diary_count = db.query(EmotionDiary).count()
    diary_today = db.query(EmotionDiary).filter(
        func.date(EmotionDiary.created_at) == today
    ).count()

    return DashboardStatsResponse(
        user_count=user_count,
        user_today=user_today,
        active_users=active_users,
        paid_users=paid_users,
        conversation_count=conversation_count,
        conversation_today=conversation_today,
        message_count=message_count,
        message_today=message_today,
        mbti_tested=mbti_tested,
        mbti_today=mbti_today,
        diary_count=diary_count,
        diary_today=diary_today,
    )


@router.get("/users", summary="获取用户列表")
async def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    level: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """获取用户列表（支持搜索和筛选）"""
    query = db.query(User)

    if keyword:
        query = query.filter(
            User.nickname.contains(keyword) |
            User.phone.contains(keyword)
        )

    if level:
        from app.models.user import MemberLevel
        query = query.filter(User.member_level == MemberLevel[level.upper()])

    total = query.count()

    offset = (page - 1) * page_size
    users = query.order_by(User.created_at.desc()).offset(offset).limit(page_size).all()

    user_list = []
    for u in users:
        user_list.append({
            "id": u.id,
            "phone": u.phone,
            "nickname": u.nickname,
            "mbti_type": u.mbti_type,
            "level": u.member_level.value if hasattr(u.member_level, 'value') else u.member_level,
            "is_active": u.is_active,
            "is_verified": u.is_verified,
            "is_admin": u.is_admin,
            "created_at": u.created_at,
            "last_login_at": u.last_login_at,
        })

    return {"total": total, "page": page, "page_size": page_size, "data": user_list}


class UserUpdateRequest(BaseModel):
    """用户更新请求"""
    nickname: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    member_level: Optional[str] = None


@router.get("/users/{user_id}", summary="获取用户详情")
async def get_user_detail(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """获取用户详细信息"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 获取用户相关统计数据
    from app.models import Conversation, Message, EmotionDiary, MbtiResult
    
    conversation_count = db.query(Conversation).filter(Conversation.user_id == user_id).count()
    message_count = db.query(Message).join(Conversation).filter(Conversation.user_id == user_id).count()
    diary_count = db.query(EmotionDiary).filter(EmotionDiary.user_id == user_id).count()
    mbti_count = db.query(MbtiResult).filter(MbtiResult.user_id == user_id).count()
    
    return {
        "id": user.id,
        "phone": user.phone,
        "nickname": user.nickname,
        "mbti_type": user.mbti_type,
        "level": user.member_level.value if hasattr(user.member_level, 'value') else user.member_level,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "is_admin": user.is_admin,
        "created_at": user.created_at,
        "last_login_at": user.last_login_at,
        "stats": {
            "conversation_count": conversation_count,
            "message_count": message_count,
            "diary_count": diary_count,
            "mbti_count": mbti_count,
        },
    }


@router.put("/users/{user_id}", summary="更新用户信息")
async def update_user(
    user_id: int,
    request: UserUpdateRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """更新用户信息（状态、权限等）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    if request.nickname is not None:
        user.nickname = request.nickname
    if request.is_active is not None:
        user.is_active = request.is_active
    if request.is_admin is not None:
        user.is_admin = request.is_admin
    if request.member_level is not None:
        from app.models.user import MemberLevel
        user.member_level = MemberLevel[request.member_level.upper()]
    
    db.commit()
    db.refresh(user)
    
    return {
        "message": "用户信息更新成功",
        "user": {
            "id": user.id,
            "nickname": user.nickname,
            "is_active": user.is_active,
            "is_admin": user.is_admin,
            "level": user.member_level.value if hasattr(user.member_level, 'value') else user.member_level,
        },
    }


@router.delete("/users/{user_id}", summary="删除用户")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """删除用户（软删除）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 软删除
    user.is_active = False
    user.deletion_requested = True
    user.deletionRequestedAt = datetime.now()
    
    db.commit()
    
    return {"message": "用户已删除"}


@router.get("/conversations/stats", summary="获取对话统计")
async def get_conversation_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """获取对话详细统计"""
    from sqlalchemy import func

    total_conversations = db.query(Conversation).count()
    total_messages = db.query(Message).count()

    active_conversations = db.query(Conversation).filter(
        Conversation.status == ConversationStatus.ACTIVE
    ).count()

    avg_messages = 0
    if total_conversations > 0:
        avg_messages = total_messages / total_conversations

    return ConversationStatsResponse(
        total_conversations=total_conversations,
        total_messages=total_messages,
        active_conversations=active_conversations,
        avg_messages_per_conversation=round(avg_messages, 1),
    )


@router.get("/stats/daily", summary="每日统计")
async def get_daily_stats(
    days: int = Query(30, ge=1, le=90),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """获取每日统计数据"""
    from datetime import date, timedelta

    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)

    # 生成日期范围
    dates = []
    date_obj = start_date
    while date_obj <= end_date:
        dates.append(date_obj.strftime("%Y-%m-%d"))
        date_obj += timedelta(days=1)

    user_counts = []
    message_counts = []
    conversation_counts = []
    diary_counts = []
    mbti_counts = []

    for d_str in dates:
        d = datetime.strptime(d_str, "%Y-%m-%d").date()

        # 用户统计
        user_count = db.query(User).filter(
            func.date(User.created_at) == d
        ).count()
        user_counts.append(user_count)

        # 消息统计
        message_count = db.query(Message).filter(
            func.date(Message.created_at) == d
        ).count()
        message_counts.append(message_count)

        # 对话统计
        conversation_count = db.query(Conversation).filter(
            func.date(Conversation.created_at) == d
        ).count()
        conversation_counts.append(conversation_count)

        # 日记统计
        from app.models.diary import EmotionDiary
        diary_count = db.query(EmotionDiary).filter(
            func.date(EmotionDiary.created_at) == d
        ).count()
        diary_counts.append(diary_count)

        # MBTI测试统计
        mbti_count = db.query(MbtiResult).filter(
            func.date(MbtiResult.created_at) == d
        ).count()
        mbti_counts.append(mbti_count)

    return {
        "dates": dates,
        "user_counts": user_counts,
        "message_counts": message_counts,
        "conversation_counts": conversation_counts,
        "diary_counts": diary_counts,
        "mbti_counts": mbti_counts,
    }


@router.get("/stats/user-growth", summary="用户增长统计")
async def get_user_growth_stats(
    period: str = Query("month", description="统计周期: day, week, month"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """获取用户增长统计"""
    from datetime import date, timedelta
    
    end_date = date.today()
    if period == "day":
        start_date = end_date - timedelta(days=30)
        interval = timedelta(days=1)
    elif period == "week":
        start_date = end_date - timedelta(weeks=12)
        interval = timedelta(weeks=1)
    else:  # month
        start_date = end_date - timedelta(days=365)
        interval = timedelta(days=30)
    
    dates = []
    counts = []
    date_obj = start_date
    
    while date_obj <= end_date:
        if period == "day":
            dates.append(date_obj.strftime("%Y-%m-%d"))
            count = db.query(User).filter(
                func.date(User.created_at) == date_obj
            ).count()
        elif period == "week":
            week_end = date_obj + timedelta(days=6)
            dates.append(f"{date_obj.strftime('%Y-%m-%d')} ~ {week_end.strftime('%Y-%m-%d')}")
            count = db.query(User).filter(
                User.created_at >= date_obj,
                User.created_at <= week_end
            ).count()
        else:  # month
            dates.append(date_obj.strftime("%Y-%m"))
            next_month = date_obj + timedelta(days=30)
            count = db.query(User).filter(
                User.created_at >= date_obj,
                User.created_at < next_month
            ).count()
        counts.append(count)
        date_obj += interval
    
    return {
        "period": period,
        "labels": dates,
        "data": counts,
    }


@router.get("/stats/activity", summary="用户活跃度统计")
async def get_activity_stats(
    days: int = Query(30, ge=1, le=90),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """获取用户活跃度统计"""
    from datetime import date, timedelta
    
    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)
    
    dates = []
    active_users = []
    new_users = []
    
    date_obj = start_date
    while date_obj <= end_date:
        dates.append(date_obj.strftime("%Y-%m-%d"))
        
        # 活跃用户数（有登录或操作的用户）
        active_count = db.query(User).filter(
            func.date(User.last_login_at) == date_obj
        ).count()
        active_users.append(active_count)
        
        # 新用户数
        new_count = db.query(User).filter(
            func.date(User.created_at) == date_obj
        ).count()
        new_users.append(new_count)
        
        date_obj += timedelta(days=1)
    
    return {
        "dates": dates,
        "active_users": active_users,
        "new_users": new_users,
    }


@router.get("/stats/content", summary="内容统计")
async def get_content_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """获取内容统计"""
    from app.models import KnowledgeArticle, Banner, Announcement
    from app.models.knowledge import ArticleStatus
    from app.models.diary import EmotionDiary
    
    # 文章统计
    total_articles = db.query(KnowledgeArticle).count()
    published_articles = db.query(KnowledgeArticle).filter(
        KnowledgeArticle.status == ArticleStatus.PUBLISHED
    ).count()
    draft_articles = db.query(KnowledgeArticle).filter(
        KnowledgeArticle.status == ArticleStatus.DRAFT
    ).count()
    
    # 总阅读量
    total_views = db.query(func.sum(KnowledgeArticle.view_count)).scalar() or 0
    
    # 其他内容统计
    total_banners = db.query(Banner).count()
    active_banners = db.query(Banner).filter(Banner.is_active == True).count()
    
    total_announcements = db.query(Announcement).count()
    active_announcements = db.query(Announcement).filter(Announcement.is_active == True).count()
    
    total_diaries = db.query(EmotionDiary).count()
    
    return {
        "articles": {
            "total": total_articles,
            "published": published_articles,
            "draft": draft_articles,
            "total_views": total_views,
        },
        "banners": {
            "total": total_banners,
            "active": active_banners,
        },
        "announcements": {
            "total": total_announcements,
            "active": active_announcements,
        },
        "diaries": {
            "total": total_diaries,
        },
    }


@router.get("/stats/membership", summary="会员统计")
async def get_membership_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """获取会员统计"""
    from app.models.user import MemberLevel
    
    total_users = db.query(User).count()
    
    # 各等级会员数量
    free_users = db.query(User).filter(
        User.member_level == MemberLevel.FREE
    ).count()
    
    pro_users = db.query(User).filter(
        User.member_level == MemberLevel.PRO
    ).count()
    
    premium_users = db.query(User).filter(
        User.member_level == MemberLevel.PREMIUM
    ).count()
    
    # 会员占比
    pro_ratio = (pro_users / total_users * 100) if total_users > 0 else 0
    premium_ratio = (premium_users / total_users * 100) if total_users > 0 else 0
    
    return {
        "total_users": total_users,
        "membership_distribution": {
            "free": free_users,
            "pro": pro_users,
            "premium": premium_users,
        },
        "membership_ratio": {
            "pro": round(pro_ratio, 2),
            "premium": round(premium_ratio, 2),
        },
    }


@router.get("/stats/system", summary="系统统计")
async def get_system_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """获取系统统计"""
    from app.models import Conversation, Message, ContentAuditQueue
    
    # 系统概览
    total_users = db.query(User).count()
    total_conversations = db.query(Conversation).count()
    total_messages = db.query(Message).count()
    
    # 审核队列统计
    pending_audit = db.query(ContentAuditQueue).filter(
        ContentAuditQueue.status == "pending"
    ).count()
    
    # 平均消息数 per 对话
    avg_messages_per_conversation = 0
    if total_conversations > 0:
        avg_messages_per_conversation = total_messages / total_conversations
    
    return {
        "overview": {
            "total_users": total_users,
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "avg_messages_per_conversation": round(avg_messages_per_conversation, 1),
        },
        "audit_queue": {
            "pending": pending_audit,
        },
    }


# ============ 内容审核 ============

class AuditQueueListResponse(BaseModel):
    total: int
    list: List[dict]


@router.get("/audit-queue", summary="获取待审核内容列表")
async def get_audit_queue(
    status: Optional[str] = Query("pending", description="状态筛选: pending/processing/approved/rejected"),
    risk_level: Optional[str] = Query(None, description="风险等级筛选"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """获取内容审核队列"""
    query = db.query(ContentAuditQueue)

    if status:
        query = query.filter(ContentAuditQueue.status == status)
    if risk_level:
        query = query.filter(ContentAuditQueue.risk_level == risk_level)

    total = query.count()
    items = query.order_by(desc(ContentAuditQueue.created_at)).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    result = []
    for item in items:
        result.append({
            "id": item.id,
            "user_id": item.user_id,
            "content_type": item.content_type,
            "content_id": item.content_id,
            "content_text": item.content_text[:200] + ("..." if len(item.content_text) > 200 else ""),
            "risk_level": item.risk_level,
            "categories": item.categories,
            "detected_keywords": item.detected_keywords,
            "confidence": item.confidence,
            "status": item.status,
            "reviewed_by": item.reviewed_by,
            "reviewed_at": item.reviewed_at,
            "review_note": item.review_note,
            "created_at": item.created_at,
        })

    return AuditQueueListResponse(total=total, list=result)


class AuditReviewRequest(BaseModel):
    status: str
    note: Optional[str] = None


@router.post("/audit-queue/{item_id}/review", summary="审核内容")
async def review_audit_item(
    item_id: int,
    request: AuditReviewRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """审核内容项"""
    item = db.query(ContentAuditQueue).filter(ContentAuditQueue.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="审核项不存在")

    item.status = request.status
    item.reviewed_by = current_user.id
    item.reviewed_at = datetime.now()
    item.review_note = request.note

    db.commit()

    return {
        "message": f"已审核，状态更新为: {request.status}",
        "id": item_id,
    }


@router.get("/audit-queue/stats", summary="获取审核统计")
async def get_audit_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """获取审核队列统计"""
    pending = db.query(ContentAuditQueue).filter(
        ContentAuditQueue.status == "pending"
    ).count()
    processing = db.query(ContentAuditQueue).filter(
        ContentAuditQueue.status == "processing"
    ).count()
    approved = db.query(ContentAuditQueue).filter(
        ContentAuditQueue.status == "approved"
    ).count()
    rejected = db.query(ContentAuditQueue).filter(
        ContentAuditQueue.status == "rejected"
    ).count()

    return {
        "pending": pending,
        "processing": processing,
        "approved": approved,
        "rejected": rejected,
        "total": pending + processing + approved + rejected,
    }


# ============ 内容管理 ============

class ArticleCreateRequest(BaseModel):
    """创建文章请求"""
    title: str
    content_html: str
    category: str
    tags: Optional[str] = None
    cover_image: Optional[str] = None
    is_featured: bool = False
    status: str = "DRAFT"


class ArticleUpdateRequest(BaseModel):
    """更新文章请求"""
    title: Optional[str] = None
    content_html: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    cover_image: Optional[str] = None
    is_featured: Optional[bool] = None
    status: Optional[str] = None


@router.get("/articles", summary="获取文章列表（管理）")
async def get_admin_articles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    category: Optional[str] = None,
    keyword: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """获取所有文章（包括草稿）"""
    from app.models import KnowledgeArticle
    from app.models.knowledge import ArticleStatus, ArticleCategory
    
    query = db.query(KnowledgeArticle)
    
    if status:
        query = query.filter(KnowledgeArticle.status == ArticleStatus[status.upper()])
    if category:
        query = query.filter(KnowledgeArticle.category == ArticleCategory[category.upper()])
    if keyword:
        query = query.filter(KnowledgeArticle.title.contains(keyword) | KnowledgeArticle.content_html.contains(keyword))
    
    total = query.count()
    articles = query.order_by(KnowledgeArticle.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "data": [
            {
                "id": a.id,
                "title": a.title,
                "category": a.category.value if hasattr(a.category, 'value') else a.category,
                "status": a.status.value if hasattr(a.status, 'value') else a.status,
                "view_count": a.view_count,
                "is_featured": a.is_featured,
                "created_at": a.created_at,
                "updated_at": a.updated_at,
            }
            for a in articles
        ],
    }


@router.post("/articles", summary="创建文章")
async def create_article(
    request: ArticleCreateRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """创建新文章"""
    from app.models import KnowledgeArticle
    from app.models.knowledge import ArticleStatus, ArticleCategory
    
    new_article = KnowledgeArticle(
        title=request.title,
        content_html=request.content_html,
        category=ArticleCategory[request.category.upper()],
        tags=request.tags,
        cover_image=request.cover_image,
        is_featured=request.is_featured,
        status=ArticleStatus[request.status.upper()],
        author_id=current_user.id,
    )
    db.add(new_article)
    db.commit()
    db.refresh(new_article)
    
    return {
        "id": new_article.id,
        "title": new_article.title,
        "status": new_article.status.value if hasattr(new_article.status, 'value') else new_article.status,
    }


@router.put("/articles/{article_id}", summary="更新文章")
async def update_article(
    article_id: int,
    request: ArticleUpdateRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """更新文章"""
    from app.models import KnowledgeArticle
    from app.models.knowledge import ArticleStatus, ArticleCategory
    
    article = db.query(KnowledgeArticle).filter(KnowledgeArticle.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    if request.title is not None:
        article.title = request.title
    if request.content_html is not None:
        article.content_html = request.content_html
    if request.category is not None:
        article.category = ArticleCategory[request.category.upper()]
    if request.tags is not None:
        article.tags = request.tags
    if request.cover_image is not None:
        article.cover_image = request.cover_image
    if request.is_featured is not None:
        article.is_featured = request.is_featured
    if request.status is not None:
        article.status = ArticleStatus[request.status.upper()]
    
    db.commit()
    db.refresh(article)
    
    return {
        "message": "文章更新成功",
        "article": {
            "id": article.id,
            "title": article.title,
            "status": article.status.value if hasattr(article.status, 'value') else article.status,
        },
    }


@router.delete("/articles/{article_id}", summary="删除文章")
async def delete_article(
    article_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """删除文章"""
    from app.models import KnowledgeArticle
    
    article = db.query(KnowledgeArticle).filter(KnowledgeArticle.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    db.delete(article)
    db.commit()
    
    return {"message": "文章已删除"}


class BannerCreateRequest(BaseModel):
    """创建Banner请求"""
    title: str
    image_url: str
    link_url: str
    position: str
    is_active: bool = True
    sort_order: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class BannerUpdateRequest(BaseModel):
    """更新Banner请求"""
    title: Optional[str] = None
    image_url: Optional[str] = None
    link_url: Optional[str] = None
    position: Optional[str] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


@router.get("/banners", summary="获取Banner列表（管理）")
async def get_admin_banners(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """获取所有Banner"""
    from app.models import Banner
    
    banners = db.query(Banner).order_by(Banner.sort_order.desc(), Banner.created_at.desc()).all()
    
    return {
        "list": [
            {
                "id": b.id,
                "title": b.title,
                "image_url": b.image_url,
                "link_url": b.link_url,
                "position": b.position,
                "is_active": b.is_active,
                "sort_order": b.sort_order,
                "start_time": b.start_time,
                "end_time": b.end_time,
                "created_at": b.created_at,
            }
            for b in banners
        ],
    }


@router.post("/banners", summary="创建Banner")
async def create_banner(
    request: BannerCreateRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """创建新Banner"""
    from app.models import Banner
    
    new_banner = Banner(**request.model_dump())
    db.add(new_banner)
    db.commit()
    db.refresh(new_banner)
    
    return {
        "id": new_banner.id,
        "title": new_banner.title,
        "is_active": new_banner.is_active,
    }


@router.put("/banners/{banner_id}", summary="更新Banner")
async def update_banner(
    banner_id: int,
    request: BannerUpdateRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """更新Banner"""
    from app.models import Banner
    
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    if not banner:
        raise HTTPException(status_code=404, detail="Banner不存在")
    
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(banner, field, value)
    
    db.commit()
    db.refresh(banner)
    
    return {
        "message": "Banner更新成功",
        "banner": {
            "id": banner.id,
            "title": banner.title,
            "is_active": banner.is_active,
        },
    }


@router.delete("/banners/{banner_id}", summary="删除Banner")
async def delete_banner(
    banner_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """删除Banner"""
    from app.models import Banner
    
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    if not banner:
        raise HTTPException(status_code=404, detail="Banner不存在")
    
    db.delete(banner)
    db.commit()
    
    return {"message": "Banner已删除"}


class AnnouncementCreateRequest(BaseModel):
    """创建公告请求"""
    title: str
    content: str
    is_top: bool = False
    is_active: bool = True
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class AnnouncementUpdateRequest(BaseModel):
    """更新公告请求"""
    title: Optional[str] = None
    content: Optional[str] = None
    is_top: Optional[bool] = None
    is_active: Optional[bool] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


@router.get("/announcements", summary="获取公告列表（管理）")
async def get_admin_announcements(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """获取所有公告"""
    from app.models import Announcement
    
    announcements = db.query(Announcement).order_by(Announcement.is_top.desc(), Announcement.created_at.desc()).all()
    
    return {
        "list": [
            {
                "id": a.id,
                "title": a.title,
                "content": a.content,
                "is_top": a.is_top,
                "is_active": a.is_active,
                "start_time": a.start_time,
                "end_time": a.end_time,
                "created_at": a.created_at,
            }
            for a in announcements
        ],
    }


@router.post("/announcements", summary="创建公告")
async def create_announcement(
    request: AnnouncementCreateRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """创建新公告"""
    from app.models import Announcement
    
    new_announcement = Announcement(**request.model_dump())
    db.add(new_announcement)
    db.commit()
    db.refresh(new_announcement)
    
    return {
        "id": new_announcement.id,
        "title": new_announcement.title,
        "is_active": new_announcement.is_active,
    }


@router.put("/announcements/{announcement_id}", summary="更新公告")
async def update_announcement(
    announcement_id: int,
    request: AnnouncementUpdateRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """更新公告"""
    from app.models import Announcement
    
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not announcement:
        raise HTTPException(status_code=404, detail="公告不存在")
    
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(announcement, field, value)
    
    db.commit()
    db.refresh(announcement)
    
    return {
        "message": "公告更新成功",
        "announcement": {
            "id": announcement.id,
            "title": announcement.title,
            "is_active": announcement.is_active,
        },
    }


@router.delete("/announcements/{announcement_id}", summary="删除公告")
async def delete_announcement(
    announcement_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """删除公告"""
    from app.models import Announcement
    
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not announcement:
        raise HTTPException(status_code=404, detail="公告不存在")
    
    db.delete(announcement)
    db.commit()
    
    return {"message": "公告已删除"}


# ============ 权限管理 ============

class RoleCreateRequest(BaseModel):
    """创建角色请求"""
    name: str
    code: str
    description: Optional[str] = None
    is_system: bool = False


class RoleUpdateRequest(BaseModel):
    """更新角色请求"""
    name: Optional[str] = None
    description: Optional[str] = None
    is_system: Optional[bool] = None


class RoleAssignPermissionRequest(BaseModel):
    """角色分配权限请求"""
    permission_ids: List[int]


class UserAssignRoleRequest(BaseModel):
    """用户分配角色请求"""
    role_ids: List[int]


@router.get("/roles", summary="获取角色列表")
async def get_roles(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """获取所有角色"""
    from app.models import Role
    
    roles = db.query(Role).all()
    
    return {
        "list": [
            {
                "id": r.id,
                "name": r.name,
                "code": r.code,
                "description": r.description,
                "is_system": r.is_system,
                "permission_count": len(r.permissions),
                "user_count": len(r.users),
                "created_at": r.created_at,
            }
            for r in roles
        ],
    }


@router.post("/roles", summary="创建角色")
async def create_role(
    request: RoleCreateRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """创建新角色"""
    from app.models import Role
    
    # 检查角色代码是否已存在
    existing = db.query(Role).filter(Role.code == request.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="角色代码已存在")
    
    new_role = Role(**request.model_dump())
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    
    return {
        "id": new_role.id,
        "name": new_role.name,
        "code": new_role.code,
    }


@router.put("/roles/{role_id}", summary="更新角色")
async def update_role(
    role_id: int,
    request: RoleUpdateRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """更新角色"""
    from app.models import Role
    
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    # 系统角色不允许修改
    if role.is_system:
        raise HTTPException(status_code=400, detail="系统角色不允许修改")
    
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(role, field, value)
    
    db.commit()
    db.refresh(role)
    
    return {
        "message": "角色更新成功",
        "role": {
            "id": role.id,
            "name": role.name,
            "code": role.code,
        },
    }


@router.delete("/roles/{role_id}", summary="删除角色")
async def delete_role(
    role_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """删除角色"""
    from app.models import Role
    
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    # 系统角色不允许删除
    if role.is_system:
        raise HTTPException(status_code=400, detail="系统角色不允许删除")
    
    # 检查是否有用户关联此角色
    if role.users:
        raise HTTPException(status_code=400, detail="该角色下还有用户，无法删除")
    
    db.delete(role)
    db.commit()
    
    return {"message": "角色已删除"}


@router.get("/permissions", summary="获取权限列表")
async def get_permissions(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """获取所有权限"""
    from app.models import Permission
    
    permissions = db.query(Permission).all()
    
    return {
        "list": [
            {
                "id": p.id,
                "name": p.name,
                "code": p.code,
                "description": p.description,
                "resource_type": p.resource_type.value,
                "action": p.action.value,
                "created_at": p.created_at,
            }
            for p in permissions
        ],
    }


@router.post("/roles/{role_id}/permissions", summary="分配权限给角色")
async def assign_permissions_to_role(
    role_id: int,
    request: RoleAssignPermissionRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """分配权限给角色"""
    from app.models import Role, Permission
    
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    # 系统角色不允许修改权限
    if role.is_system:
        raise HTTPException(status_code=400, detail="系统角色不允许修改权限")
    
    # 验证权限是否存在
    permissions = db.query(Permission).filter(Permission.id.in_(request.permission_ids)).all()
    if len(permissions) != len(request.permission_ids):
        raise HTTPException(status_code=400, detail="部分权限不存在")
    
    # 分配权限
    role.permissions = permissions
    db.commit()
    
    return {
        "message": "权限分配成功",
        "role_id": role_id,
        "permission_count": len(permissions),
    }


@router.post("/users/{user_id}/roles", summary="分配角色给用户")
async def assign_roles_to_user(
    user_id: int,
    request: UserAssignRoleRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """分配角色给用户"""
    from app.models import User, Role
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 验证角色是否存在
    roles = db.query(Role).filter(Role.id.in_(request.role_ids)).all()
    if len(roles) != len(request.role_ids):
        raise HTTPException(status_code=400, detail="部分角色不存在")
    
    # 分配角色
    user.roles = roles
    db.commit()
    
    return {
        "message": "角色分配成功",
        "user_id": user_id,
        "role_count": len(roles),
    }


@router.get("/users/{user_id}/roles", summary="获取用户角色")
async def get_user_roles(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """获取用户的角色"""
    from app.models import User
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return {
        "user_id": user_id,
        "roles": [
            {
                "id": r.id,
                "name": r.name,
                "code": r.code,
                "is_system": r.is_system,
            }
            for r in user.roles
        ],
    }

