"""
用户长期记忆API
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models import User
from app.schemas.user_memory import (
    UserMemoryCreate,
    UserMemoryUpdate,
    UserMemoryResponse,
    UserMemoryListResponse,
    MemoryInsightCreate,
    MemoryInsightResponse,
    UserPreferenceSet,
    UserPreferenceResponse,
    MemoryStatisticsResponse,
)
from app.services.user_memory_service import get_user_memory_service

router = APIRouter(prefix="/user-memory", tags=["用户长期记忆"])


# ============ 长期记忆 ============

@router.post("/", summary="添加长期记忆", response_model=UserMemoryResponse)
async def add_memory(
    request: UserMemoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """添加新的用户长期记忆"""
    memory_service = get_user_memory_service()

    memory = memory_service.add_memory(
        db=db,
        user_id=current_user.id,
        memory_type=request.memory_type,
        content=request.content,
        importance=request.importance or 2,
        summary=request.summary,
        keywords=request.keywords,
        source=request.source or "conversation",
        source_conversation_id=request.source_conversation_id,
        source_message_id=request.source_message_id,
        confidence=request.confidence or 1.0,
    )

    return UserMemoryResponse.model_validate(memory)


@router.get("/{memory_id}", summary="获取记忆详情", response_model=UserMemoryResponse)
async def get_memory(
    memory_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取记忆详情"""
    memory_service = get_user_memory_service()
    memory = memory_service.get_memory(db, current_user.id, memory_id)

    if not memory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="记忆不存在",
        )

    return UserMemoryResponse.model_validate(memory)


@router.get("/list", summary="获取记忆列表", response_model=UserMemoryListResponse)
async def list_memories(
    memory_type: Optional[str] = Query(None, description="记忆类型筛选"),
    min_importance: Optional[int] = Query(None, description="最低重要程度"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取用户记忆列表"""
    memory_service = get_user_memory_service()
    memories, total = memory_service.list_memories(
        db=db,
        user_id=current_user.id,
        memory_type=memory_type,
        min_importance=min_importance,
        keyword=keyword,
        page=page,
        page_size=page_size,
    )

    has_next = page * page_size < total

    return UserMemoryListResponse(
        total=total,
        page=page,
        page_size=page_size,
        has_next=has_next,
        data=[UserMemoryResponse.model_validate(m) for m in memories],
    )


@router.put("/{memory_id}", summary="更新记忆", response_model=UserMemoryResponse)
async def update_memory(
    memory_id: int,
    request: UserMemoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新记忆信息"""
    memory_service = get_user_memory_service()
    updates = request.model_dump(exclude_unset=True)

    memory = memory_service.update_memory(db, current_user.id, memory_id, updates)
    if not memory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="记忆不存在",
        )

    return UserMemoryResponse.model_validate(memory)


@router.delete("/{memory_id}", summary="删除记忆")
async def delete_memory(
    memory_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除记忆（软删除）"""
    memory_service = get_user_memory_service()
    success = memory_service.delete_memory(db, current_user.id, memory_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="记忆不存在",
        )

    return {"message": "记忆已删除"}


@router.get("/search", summary="搜索记忆", response_model=List[UserMemoryResponse])
async def search_memories(
    query: str = Query(..., description="搜索关键词"),
    limit: int = Query(10, ge=1, le=50, description="返回数量限制"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """搜索用户记忆"""
    memory_service = get_user_memory_service()
    results = memory_service.search_memories(
        db=db,
        user_id=current_user.id,
        query=query,
        limit=limit,
    )

    return [UserMemoryResponse.model_validate(r) for r in results]


@router.get("/stats", summary="获取记忆统计", response_model=MemoryStatisticsResponse)
async def get_memory_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取用户记忆统计信息"""
    memory_service = get_user_memory_service()
    stats = memory_service.get_statistics(db, current_user.id)

    return MemoryStatisticsResponse(
        total_count=stats["total_count"],
        by_type=stats["by_type"],
        by_importance=stats["by_importance"],
    )


# ============ 记忆洞察 ============

@router.post("/insights", summary="添加记忆洞察", response_model=MemoryInsightResponse)
async def add_insight(
    request: MemoryInsightCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """添加AI生成的记忆洞察"""
    memory_service = get_user_memory_service()

    insight = memory_service.add_insight(
        db=db,
        user_id=current_user.id,
        insight_type=request.insight_type,
        content=request.content,
        supporting_memory_ids=request.supporting_memory_ids,
        confidence=request.confidence or 0.5,
    )

    return MemoryInsightResponse.model_validate(insight)


@router.get("/insights", summary="获取洞察列表", response_model=List[MemoryInsightResponse])
async def list_insights(
    insight_type: Optional[str] = Query(None, description="洞察类型"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取用户记忆洞察列表"""
    memory_service = get_user_memory_service()
    insights = memory_service.list_insights(db, current_user.id, insight_type)

    return [MemoryInsightResponse.model_validate(i) for i in insights]


# ============ 用户偏好 ============

@router.post("/preferences", summary="设置用户偏好", response_model=UserPreferenceResponse)
async def set_preference(
    request: UserPreferenceSet,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """设置用户偏好"""
    memory_service = get_user_memory_service()

    pref = memory_service.set_preference(
        db=db,
        user_id=current_user.id,
        category=request.category,
        key=request.key,
        value=request.value,
        source=request.source or "user",
    )

    return UserPreferenceResponse(
        id=pref.id,
        category=pref.category,
        key=pref.key,
        value=pref.value,
        value_type=pref.value_type,
        source=pref.source,
        created_at=pref.created_at,
        updated_at=pref.updated_at,
    )


@router.get("/preferences/{category}/{key}", summary="获取用户偏好")
async def get_preference(
    category: str,
    key: str,
    default: Optional[str] = Query(None, description="默认值"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取用户偏好"""
    memory_service = get_user_memory_service()
    value = memory_service.get_preference(db, current_user.id, category, key, default)

    return {"category": category, "key": key, "value": value}


@router.get("/preferences/{category}", summary="获取分类下所有偏好", response_model=Dict[str, Any])
async def get_category_preferences(
    category: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取某个分类下的所有用户偏好"""
    memory_service = get_user_memory_service()
    prefs = memory_service.get_category_preferences(db, current_user.id, category)

    return prefs


@router.delete("/preferences/{category}/{key}", summary="删除用户偏好")
async def delete_preference(
    category: str,
    key: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除用户偏好"""
    memory_service = get_user_memory_service()
    success = memory_service.delete_preference(db, current_user.id, category, key)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="偏好不存在",
        )

    return {"message": "偏好已删除"}


@router.get("/relevant", summary="获取相关记忆", response_model=List[UserMemoryResponse])
async def get_relevant_memories(
    context: str = Query(..., description="当前对话上下文"),
    limit: int = Query(5, ge=1, le=20, description="返回数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """根据上下文获取相关的记忆"""
    memory_service = get_user_memory_service()
    results = memory_service.get_relevant_memories(
        db=db,
        user_id=current_user.id,
        conversation_context=context,
        limit=limit,
    )

    return [UserMemoryResponse.model_validate(r) for r in results]
