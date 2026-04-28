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
    "LLM_FAILOVER_CHAIN",
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
    "VOLCENGINE_API_KEY", "VOLCENGINE_MODEL", "VOLCENGINE_BASE_URL",
    "SENSETIME_API_KEY", "SENSETIME_MODEL",
    "BAICHUAN_API_KEY", "BAICHUAN_MODEL",
    "MOONSHOT_API_KEY", "MOONSHOT_MODEL",
    "LINGYI_API_KEY", "LINGYI_MODEL",
]

# 知识库配置键
KNOWLEDGE_CONFIG_KEYS = [
    "EMBEDDING_MODEL",
    "EMBEDDING_DIM",
    "CHUNK_SIZE",
    "CHUNK_OVERLAP",
    "VECTOR_DB_TYPE",
    "MILVUS_HOST",
    "MILVUS_PORT",
    "MILVUS_COLLECTION",
    "QDRANT_HOST",
    "QDRANT_PORT",
    "QDRANT_COLLECTION",
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
    llm_failover_chain: Optional[str] = None
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
    volcengine_api_key: Optional[str] = None
    volcengine_model: Optional[str] = None
    volcengine_base_url: Optional[str] = None
    sensetime_api_key: Optional[str] = None
    sensetime_model: Optional[str] = None
    baichuan_api_key: Optional[str] = None
    baichuan_model: Optional[str] = None
    moonshot_api_key: Optional[str] = None
    moonshot_model: Optional[str] = None
    lingyi_api_key: Optional[str] = None
    lingyi_model: Optional[str] = None


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

    # 获取failover chain配置
    failover_config = db.query(SystemConfig).filter(
        SystemConfig.config_key == "LLM_FAILOVER_CHAIN"
    ).first()

    # 辅助函数：掩码API Key，只显示前4位和后4位
    def mask_api_key(key: str) -> str:
        if not key:
            return ""
        if len(key) <= 8:
            return "*" * len(key)
        return f"{key[:4]}...{key[-4:]}"

    return {
        "llm_provider": settings.LLM_PROVIDER,
        "llm_failover_chain": failover_config.config_value if failover_config else "volcengine,doubao,glm,qwen,siliconflow,ernie,hunyuan",
        "openai_model": settings.OPENAI_MODEL,
        "openai_base_url": settings.OPENAI_BASE_URL,
        "openai_api_key": mask_api_key(settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else "",
        "anthropic_model": settings.ANTHROPIC_MODEL,
        "anthropic_base_url": settings.ANTHROPIC_BASE_URL,
        "anthropic_api_key": mask_api_key(settings.ANTHROPIC_API_KEY) if settings.ANTHROPIC_API_KEY else "",
        "glm_model": settings.GLM_MODEL,
        "glm_base_url": settings.GLM_BASE_URL,
        "glm_api_key": mask_api_key(settings.GLM_API_KEY) if settings.GLM_API_KEY else "",
        "qwen_model": settings.QWEN_MODEL,
        "qwen_base_url": settings.QWEN_BASE_URL,
        "qwen_api_key": mask_api_key(settings.QWEN_API_KEY) if settings.QWEN_API_KEY else "",
        "minimax_model": settings.MINIMAX_MODEL,
        "minimax_base_url": settings.MINIMAX_BASE_URL,
        "minimax_api_key": mask_api_key(settings.MINIMAX_API_KEY) if settings.MINIMAX_API_KEY else "",
        "ernie_model": settings.ERNIE_MODEL,
        "ernie_base_url": settings.ERNIE_BASE_URL,
        "ernie_api_key": mask_api_key(settings.ERNIE_API_KEY) if settings.ERNIE_API_KEY else "",
        "hunyuan_model": settings.HUNYUAN_MODEL,
        "hunyuan_base_url": settings.HUNYUAN_BASE_URL,
        "hunyuan_api_key": mask_api_key(settings.HUNYUAN_API_KEY) if settings.HUNYUAN_API_KEY else "",
        "spark_model": settings.SPARK_MODEL,
        "spark_base_url": settings.SPARK_BASE_URL,
        "spark_api_key": mask_api_key(settings.SPARK_API_KEY) if settings.SPARK_API_KEY else "",
        "doubao_model": settings.DOUBAO_MODEL,
        "doubao_base_url": settings.DOUBAO_BASE_URL,
        "doubao_api_key": mask_api_key(settings.DOUBAO_API_KEY) if settings.DOUBAO_API_KEY else "",
        "siliconflow_model": settings.SILICONFLOW_MODEL,
        "siliconflow_base_url": settings.SILICONFLOW_BASE_URL,
        "siliconflow_api_key": mask_api_key(settings.SILICONFLOW_API_KEY) if settings.SILICONFLOW_API_KEY else "",
        "volcengine_model": getattr(settings, 'VOLCENGINE_MODEL', 'doubao-pro-32k'),
        "volcengine_base_url": getattr(settings, 'VOLCENGINE_BASE_URL', 'https://ark.cn-beijing.volces.com/api/v3'),
        "volcengine_api_key": mask_api_key(getattr(settings, 'VOLCENGINE_API_KEY', None)) if getattr(settings, 'VOLCENGINE_API_KEY', None) else "",
        "sensetime_model": getattr(settings, 'SENSETIME_MODEL', 'sensechat-5'),
        "sensetime_api_key": mask_api_key(getattr(settings, 'SENSETIME_API_KEY', None)) if getattr(settings, 'SENSETIME_API_KEY', None) else "",
        "baichuan_model": getattr(settings, 'BAICHUAN_MODEL', 'baichuan4'),
        "baichuan_api_key": mask_api_key(getattr(settings, 'BAICHUAN_API_KEY', None)) if getattr(settings, 'BAICHUAN_API_KEY', None) else "",
        "moonshot_model": getattr(settings, 'MOONSHOT_MODEL', 'moonshot-v1-8k'),
        "moonshot_api_key": mask_api_key(getattr(settings, 'MOONSHOT_API_KEY', None)) if getattr(settings, 'MOONSHOT_API_KEY', None) else "",
        "lingyi_model": getattr(settings, 'LINGYI_MODEL', 'yi-medium'),
        "lingyi_api_key": mask_api_key(getattr(settings, 'LINGYI_API_KEY', None)) if getattr(settings, 'LINGYI_API_KEY', None) else "",
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
        "has_volcengine_key": bool(getattr(settings, 'VOLCENGINE_API_KEY', None)),
        "has_sensetime_key": bool(getattr(settings, 'SENSETIME_API_KEY', None)),
        "has_baichuan_key": bool(getattr(settings, 'BAICHUAN_API_KEY', None)),
        "has_moonshot_key": bool(getattr(settings, 'MOONSHOT_API_KEY', None)),
        "has_lingyi_key": bool(getattr(settings, 'LINGYI_API_KEY', None)),
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
        "llm_failover_chain": "LLM_FAILOVER_CHAIN",
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
        "volcengine_api_key": "VOLCENGINE_API_KEY",
        "volcengine_model": "VOLCENGINE_MODEL",
        "volcengine_base_url": "VOLCENGINE_BASE_URL",
        "sensetime_api_key": "SENSETIME_API_KEY",
        "sensetime_model": "SENSETIME_MODEL",
        "baichuan_api_key": "BAICHUAN_API_KEY",
        "baichuan_model": "BAICHUAN_MODEL",
        "moonshot_api_key": "MOONSHOT_API_KEY",
        "moonshot_model": "MOONSHOT_MODEL",
        "lingyi_api_key": "LINGYI_API_KEY",
        "lingyi_model": "LINGYI_MODEL",
    }

    # API Key字段列表 - 这些字段需要特殊处理，空字符串不覆盖已有值
    api_key_fields = {
        "openai_api_key": "OPENAI_API_KEY",
        "anthropic_api_key": "ANTHROPIC_API_KEY",
        "glm_api_key": "GLM_API_KEY",
        "qwen_api_key": "QWEN_API_KEY",
        "minimax_api_key": "MINIMAX_API_KEY",
        "ernie_api_key": "ERNIE_API_KEY",
        "hunyuan_api_key": "HUNYUAN_API_KEY",
        "spark_api_key": "SPARK_API_KEY",
        "doubao_api_key": "DOUBAO_API_KEY",
        "siliconflow_api_key": "SILICONFLOW_API_KEY",
        "volcengine_api_key": "VOLCENGINE_API_KEY",
        "sensetime_api_key": "SENSETIME_API_KEY",
        "baichuan_api_key": "BAICHUAN_API_KEY",
        "moonshot_api_key": "MOONSHOT_API_KEY",
        "lingyi_api_key": "LINGYI_API_KEY",
    }

    for frontend_key, backend_key in config_map.items():
        value = getattr(config, frontend_key, None)
        # API Key字段：只有非空字符串才更新，None或空字符串保留原有值
        if backend_key in api_key_fields.values():
            if value is not None and value != '':
                updates[backend_key] = value
        else:
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


@router.post("/test_provider", summary="测试单个Provider")
async def test_provider(
    provider: str = Query(..., description="Provider名称"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """测试降级链中单个Provider的可用性"""
    from app.core.config import settings

    load_llm_config_to_memory(db)

    # 获取provider配置
    config_key_map = {
        "openai": ("OPENAI_API_KEY", "OPENAI_MODEL", "OPENAI_BASE_URL"),
        "anthropic": ("ANTHROPIC_API_KEY", "ANTHROPIC_MODEL", "ANTHROPIC_BASE_URL"),
        "volcengine": ("VOLCENGINE_API_KEY", "VOLCENGINE_MODEL", "VOLCENGINE_BASE_URL"),
        "doubao": ("DOUBAO_API_KEY", "DOUBAO_MODEL", "DOUBAO_BASE_URL"),
        "glm": ("GLM_API_KEY", "GLM_MODEL", "GLM_BASE_URL"),
        "qwen": ("QWEN_API_KEY", "QWEN_MODEL", "QWEN_BASE_URL"),
        "minimax": ("MINIMAX_API_KEY", "MINIMAX_MODEL", "MINIMAX_BASE_URL"),
        "ernie": ("ERNIE_API_KEY", "ERNIE_MODEL", "ERNIE_BASE_URL"),
        "hunyuan": ("HUNYUAN_API_KEY", "HUNYUAN_MODEL", "HUNYUAN_BASE_URL"),
        "spark": ("SPARK_API_KEY", "SPARK_MODEL", "SPARK_BASE_URL"),
        "siliconflow": ("SILICONFLOW_API_KEY", "SILICONFLOW_MODEL", "SILICONFLOW_BASE_URL"),
        "sensetime": ("SENSETIME_API_KEY", "SENSETIME_MODEL", None),
        "baichuan": ("BAICHUAN_API_KEY", "BAICHUAN_MODEL", None),
        "moonshot": ("MOONSHOT_API_KEY", "MOONSHOT_MODEL", None),
        "lingyi": ("LINGYI_API_KEY", "LINGYI_MODEL", None),
    }

    if provider not in config_key_map:
        return {"success": False, "provider": provider, "error": f"不支持的Provider: {provider}"}

    api_key_key, model_key, base_url_key = config_key_map[provider]
    api_key = getattr(settings, api_key_key, None)
    model = getattr(settings, model_key, None)
    base_url = getattr(settings, base_url_key, None) if base_url_key else None

    if not api_key:
        return {"success": False, "provider": provider, "error": "未配置API Key"}

    # 临时切换provider进行测试
    original_provider = settings.LLM_PROVIDER
    try:
        settings.LLM_PROVIDER = provider

        # 调用LLM
        from app.services.llm import chat
        result = await chat(
            messages=[{"role": "user", "content": "测试"}],
            temperature=0.7,
            max_tokens=100,
        )
        return {
            "success": True,
            "provider": provider,
            "model": model,
            "response": result[:200] if result else ""
        }
    except Exception as e:
        return {"success": False, "provider": provider, "model": model, "error": str(e)}
    finally:
        settings.LLM_PROVIDER = original_provider


@router.get("/provider_status", summary="获取降级链Provider状态")
async def get_provider_status(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """获取降级链中所有Provider的配置状态"""
    from app.core.config import settings

    load_llm_config_to_memory(db)

    # Provider配置映射
    provider_configs = {
        "openai": {"api_key": settings.OPENAI_API_KEY, "model": settings.OPENAI_MODEL, "base_url": settings.OPENAI_BASE_URL},
        "anthropic": {"api_key": settings.ANTHROPIC_API_KEY, "model": settings.ANTHROPIC_MODEL, "base_url": settings.ANTHROPIC_BASE_URL},
        "volcengine": {"api_key": getattr(settings, 'VOLCENGINE_API_KEY', None), "model": getattr(settings, 'VOLCENGINE_MODEL', 'doubao-pro-32k'), "base_url": getattr(settings, 'VOLCENGINE_BASE_URL', 'https://ark.cn-beijing.volces.com/api/v3')},
        "doubao": {"api_key": settings.DOUBAO_API_KEY, "model": settings.DOUBAO_MODEL, "base_url": settings.DOUBAO_BASE_URL},
        "glm": {"api_key": settings.GLM_API_KEY, "model": settings.GLM_MODEL, "base_url": settings.GLM_BASE_URL},
        "qwen": {"api_key": settings.QWEN_API_KEY, "model": settings.QWEN_MODEL, "base_url": settings.QWEN_BASE_URL},
        "minimax": {"api_key": settings.MINIMAX_API_KEY, "model": settings.MINIMAX_MODEL, "base_url": settings.MINIMAX_BASE_URL},
        "ernie": {"api_key": settings.ERNIE_API_KEY, "model": settings.ERNIE_MODEL, "base_url": settings.ERNIE_BASE_URL},
        "hunyuan": {"api_key": settings.HUNYUAN_API_KEY, "model": settings.HUNYUAN_MODEL, "base_url": settings.HUNYUAN_BASE_URL},
        "spark": {"api_key": settings.SPARK_API_KEY, "model": settings.SPARK_MODEL, "base_url": settings.SPARK_BASE_URL},
        "siliconflow": {"api_key": settings.SILICONFLOW_API_KEY, "model": settings.SILICONFLOW_MODEL, "base_url": settings.SILICONFLOW_BASE_URL},
        "sensetime": {"api_key": getattr(settings, 'SENSETIME_API_KEY', None), "model": getattr(settings, 'SENSETIME_MODEL', 'sensechat-5'), "base_url": None},
        "baichuan": {"api_key": getattr(settings, 'BAICHUAN_API_KEY', None), "model": getattr(settings, 'BAICHUAN_MODEL', 'baichuan4'), "base_url": None},
        "moonshot": {"api_key": getattr(settings, 'MOONSHOT_API_KEY', None), "model": getattr(settings, 'MOONSHOT_MODEL', 'moonshot-v1-8k'), "base_url": None},
        "lingyi": {"api_key": getattr(settings, 'LINGYI_API_KEY', None), "model": getattr(settings, 'LINGYI_MODEL', 'yi-medium'), "base_url": None},
    }

    # 获取当前failover chain
    failover_config = db.query(SystemConfig).filter(
        SystemConfig.config_key == "LLM_FAILOVER_CHAIN"
    ).first()
    failover_chain = failover_config.config_value.split(',') if failover_config and failover_config.config_value else []

    # 构建状态列表
    status_list = []
    for provider in failover_chain:
        provider = provider.strip()
        if provider in provider_configs:
            config = provider_configs[provider]
            status_list.append({
                "provider": provider,
                "has_api_key": bool(config["api_key"]),
                "model": config["model"] or "未设置",
                "base_url": config["base_url"] or "默认",
            })

    return {
        "failover_chain": failover_chain,
        "providers": status_list,
        "current_provider": settings.LLM_PROVIDER,
    }


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

    return DateRangeStatsResponse(
        dates=dates,
        user_counts=user_counts,
        message_counts=message_counts,
        conversation_counts=conversation_counts,
    )


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


# ============ 知识库同步管理 ============

from app.schemas.knowledge import KnowledgeSyncConfig, KnowledgeSyncStatus, KnowledgeSyncResult
from app.services.rag.knowledge_sync import get_knowledge_sync_service


@router.get("/knowledge-sync/config", summary="获取知识库同步配置")
async def get_knowledge_sync_config(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """获取当前知识库同步配置"""
    # 从数据库读取配置
    source_config = db.query(SystemConfig).filter(
        SystemConfig.config_key == "KNOWLEDGE_SYNC_SOURCE_URL"
    ).first()
    enabled_config = db.query(SystemConfig).filter(
        SystemConfig.config_key == "KNOWLEDGE_SYNC_ENABLED"
    ).first()
    auto_sync_config = db.query(SystemConfig).filter(
        SystemConfig.config_key == "KNOWLEDGE_SYNC_AUTO"
    ).first()
    interval_config = db.query(SystemConfig).filter(
        SystemConfig.config_key == "KNOWLEDGE_SYNC_INTERVAL"
    ).first()

    service = get_knowledge_sync_service()

    return {
        "source_url": source_config.config_value if source_config else None,
        "enabled": enabled_config.config_value == "true" if enabled_config else True,
        "auto_sync": auto_sync_config.config_value == "true" if auto_sync_config else False,
        "sync_interval_hours": int(interval_config.config_value) if interval_config else 24,
        "last_sync_time": service.last_sync_time,
        "default_sources": service.DEFAULT_SOURCES,
    }


class KnowledgeSyncConfigUpdate(BaseModel):
    source_url: Optional[str] = None
    enabled: Optional[bool] = None
    auto_sync: Optional[bool] = None
    sync_interval_hours: Optional[int] = None


@router.put("/knowledge-sync/config", summary="更新知识库同步配置")
async def update_knowledge_sync_config(
    config: KnowledgeSyncConfigUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """更新知识库同步配置"""
    updates = {}

    if config.source_url is not None:
        updates["KNOWLEDGE_SYNC_SOURCE_URL"] = config.source_url
    if config.enabled is not None:
        updates["KNOWLEDGE_SYNC_ENABLED"] = "true" if config.enabled else "false"
    if config.auto_sync is not None:
        updates["KNOWLEDGE_SYNC_AUTO"] = "true" if config.auto_sync else "false"
    if config.sync_interval_hours is not None:
        updates["KNOWLEDGE_SYNC_INTERVAL"] = str(config.sync_interval_hours)

    for key, value in updates.items():
        existing = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
        if existing:
            existing.config_value = value
        else:
            new_config = SystemConfig(config_key=key, config_value=value)
            db.add(new_config)

    db.commit()

    # 更新服务实例
    service = get_knowledge_sync_service()
    if config.source_url is not None:
        service.set_source_url(config.source_url)

    return {"message": "配置已更新", "changes": list(updates.keys())}


@router.post("/knowledge-sync/trigger", summary="手动触发知识库同步")
async def trigger_knowledge_sync(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """手动触发一次知识库同步"""
    import asyncio
    from datetime import datetime

    service = get_knowledge_sync_service()

    # 获取在线文章
    online_articles = await service.fetch_online_articles()

    result = {
        "success": False,
        "synced_count": 0,
        "total_online": len(online_articles),
        "message": "",
    }

    if not online_articles:
        result["message"] = "没有找到在线文章或连接失败"
        return result

    # 同步到数据库
    synced_count = service.sync_articles_to_db(db, online_articles)
    result["synced_count"] = synced_count
    result["success"] = True
    result["message"] = f"成功同步 {synced_count} 篇新文章，共获取 {len(online_articles)} 篇"

    # 更新最后同步时间
    service.last_sync_time = datetime.now()

    loguru.logger.info(f"管理员手动触发知识库同步: {result}")

    return result


@router.get("/knowledge-sync/status", summary="获取知识库同步状态")
async def get_knowledge_sync_status(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """获取知识库同步状态"""
    service = get_knowledge_sync_service()
    local_count = service.get_local_articles_count(db)

    source_config = db.query(SystemConfig).filter(
        SystemConfig.config_key == "KNOWLEDGE_SYNC_SOURCE_URL"
    ).first()
    enabled_config = db.query(SystemConfig).filter(
        SystemConfig.config_key == "KNOWLEDGE_SYNC_ENABLED"
    ).first()
    auto_sync_config = db.query(SystemConfig).filter(
        SystemConfig.config_key == "KNOWLEDGE_SYNC_AUTO"
    ).first()
    interval_config = db.query(SystemConfig).filter(
        SystemConfig.config_key == "KNOWLEDGE_SYNC_INTERVAL"
    ).first()

    return KnowledgeSyncStatus(
        configured=source_config is not None,
        enabled=enabled_config.config_value == "true" if enabled_config else True,
        auto_sync=auto_sync_config.config_value == "true" if auto_sync_config else False,
        sync_interval_hours=int(interval_config.config_value) if interval_config else 24,
        last_sync_time=service.last_sync_time,
        local_articles_count=local_count,
        sources=service.DEFAULT_SOURCES,
    )


# ============ 知识库Embedding和分块配置 ============

class KnowledgeBaseConfigUpdate(BaseModel):
    embedding_model: Optional[str] = None
    embedding_dim: Optional[int] = None
    chunk_size: Optional[int] = None
    chunk_overlap: Optional[int] = None
    vector_db_type: Optional[str] = None
    milvus_host: Optional[str] = None
    milvus_port: Optional[int] = None
    milvus_collection: Optional[str] = None
    qdrant_host: Optional[str] = None
    qdrant_port: Optional[int] = None
    qdrant_collection: Optional[str] = None


@router.get("/knowledge-base/config", summary="获取知识库Embedding和分块配置")
async def get_knowledge_base_config(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """获取知识库Embedding和分块配置"""
    from app.core.config import settings

    # 从数据库读取配置
    def get_config(key: str, default: str = None) -> Optional[str]:
        config = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
        return config.config_value if config else default

    def get_config_int(key: str, default: int = None) -> Optional[int]:
        config = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
        return int(config.config_value) if config else default

    return {
        # Embedding配置
        "embedding_model": get_config("EMBEDDING_MODEL", settings.EMBEDDING_MODEL),
        "embedding_dim": get_config_int("EMBEDDING_DIM", settings.EMBEDDING_DIM),
        # 分块配置
        "chunk_size": get_config_int("CHUNK_SIZE", 500),
        "chunk_overlap": get_config_int("CHUNK_OVERLAP", 50),
        # 向量数据库配置
        "vector_db_type": get_config("VECTOR_DB_TYPE", settings.VECTOR_DB_TYPE),
        "milvus_host": get_config("MILVUS_HOST", settings.MILVUS_HOST),
        "milvus_port": get_config_int("MILVUS_PORT", settings.MILVUS_PORT),
        "milvus_collection": get_config("MILVUS_COLLECTION", settings.MILVUS_COLLECTION),
        "qdrant_host": get_config("QDRANT_HOST", settings.QDRANT_HOST),
        "qdrant_port": get_config_int("QDRANT_PORT", settings.QDRANT_PORT),
        "qdrant_collection": get_config("QDRANT_COLLECTION", settings.QDRANT_COLLECTION),
    }


@router.put("/knowledge-base/config", summary="更新知识库Embedding和分块配置")
async def update_knowledge_base_config(
    config: KnowledgeBaseConfigUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """更新知识库Embedding和分块配置"""
    updates = {}

    if config.embedding_model is not None:
        updates["EMBEDDING_MODEL"] = config.embedding_model
    if config.embedding_dim is not None:
        updates["EMBEDDING_DIM"] = str(config.embedding_dim)
    if config.chunk_size is not None:
        updates["CHUNK_SIZE"] = str(config.chunk_size)
    if config.chunk_overlap is not None:
        updates["CHUNK_OVERLAP"] = str(config.chunk_overlap)
    if config.vector_db_type is not None:
        updates["VECTOR_DB_TYPE"] = config.vector_db_type
    if config.milvus_host is not None:
        updates["MILVUS_HOST"] = config.milvus_host
    if config.milvus_port is not None:
        updates["MILVUS_PORT"] = str(config.milvus_port)
    if config.milvus_collection is not None:
        updates["MILVUS_COLLECTION"] = config.milvus_collection
    if config.qdrant_host is not None:
        updates["QDRANT_HOST"] = config.qdrant_host
    if config.qdrant_port is not None:
        updates["QDRANT_PORT"] = str(config.qdrant_port)
    if config.qdrant_collection is not None:
        updates["QDRANT_COLLECTION"] = config.qdrant_collection

    for key, value in updates.items():
        existing = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
        if existing:
            existing.config_value = value
        else:
            new_config = SystemConfig(config_key=key, config_value=value)
            db.add(new_config)

    db.commit()

    # 更新settings内存
    from app.core.config import settings
    for key, value in updates.items():
        if hasattr(settings, key):
            # 类型转换
            if key in ["EMBEDDING_DIM", "CHUNK_SIZE", "CHUNK_OVERLAP", "MILVUS_PORT", "QDRANT_PORT"]:
                value = int(value)
            setattr(settings, key, value)
        os.environ[key] = str(value)

    # 重置向量存储实例（下次使用时重新初始化）
    import app.services.rag.vectorstore as vectorstore_module
    vectorstore_module._vector_store = None

    return {"message": "知识库配置已更新", "changes": list(updates.keys())}

