"""
情感日记API
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models import User
from app.schemas.diary import (
    DiaryCreate,
    DiaryUpdate,
    DiaryDetailSchema,
    DiaryListResponse,
    DiarySummarySchema,
    MoodCreate,
    MoodRecordSchema,
    TagCreate,
    TagUpdate,
    DiaryTagSchema,
    DiaryQuery,
    MoodTrendResponse,
    DiaryStatsResponse,
    AnalysisResponse,
)
from app.services.diary_service import get_diary_service

router = APIRouter(prefix="/diary", tags=["情感日记"])


@router.post("/create", summary="创建日记", response_model=DiaryDetailSchema)
async def create_diary(
    request: DiaryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建新的情感日记"""
    diary_service = get_diary_service()

    try:
        diary = diary_service.create_diary(db, current_user.id, request)
        return DiaryDetailSchema.from_orm(diary)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建日记失败: {str(e)}",
        )


@router.get("/{diary_id}", summary="获取日记详情", response_model=DiaryDetailSchema)
async def get_diary(
    diary_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取日记的详细信息"""
    diary_service = get_diary_service()
    diary = diary_service.get_diary(db, current_user.id, diary_id)

    if not diary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="日记不存在",
        )

    return DiaryDetailSchema.from_orm(diary)


@router.get("/date/{diary_date}", summary="根据日期获取日记", response_model=DiaryDetailSchema)
async def get_diary_by_date(
    diary_date: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """根据日期获取日记（YYYY-MM-DD格式）"""
    from datetime import datetime

    try:
        date_obj = datetime.strptime(diary_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="日期格式无效，应使用YYYY-MM-DD格式",
        )

    diary_service = get_diary_service()
    diary = diary_service.get_diary_by_date(db, current_user.id, date_obj)

    if not diary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="该日期没有日记记录",
        )

    return DiaryDetailSchema.from_orm(diary)


@router.get("/list", summary="获取日记列表", response_model=DiaryListResponse)
async def list_diaries(
    query: DiaryQuery = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取用户的日记列表（支持多种筛选条件）"""
    diary_service = get_diary_service()

    # 将字符串日期转换为日期对象
    from datetime import datetime
    start_date = None
    if query.start_date:
        try:
            start_date = datetime.strptime(query.start_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="开始日期格式无效，应使用YYYY-MM-DD格式",
            )

    end_date = None
    if query.end_date:
        try:
            end_date = datetime.strptime(query.end_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="结束日期格式无效，应使用YYYY-MM-DD格式",
            )

    diaries, total = diary_service.list_diaries(
        db,
        current_user.id,
        start_date,
        end_date,
        query.mood_level,
        query.emotion,
        query.category,
        query.tags,
        query.page,
        query.page_size,
    )

    has_next = query.page * query.page_size < total

    return DiaryListResponse(
        total=total,
        page=query.page,
        page_size=query.page_size,
        has_next=has_next,
        data=[DiarySummarySchema.from_orm(d) for d in diaries],
    )


@router.put("/{diary_id}", summary="更新日记", response_model=DiaryDetailSchema)
async def update_diary(
    diary_id: int,
    request: DiaryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新日记内容"""
    diary_service = get_diary_service()

    diary = diary_service.update_diary(db, current_user.id, diary_id, request)

    if not diary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="日记不存在",
        )

    return DiaryDetailSchema.from_orm(diary)


@router.delete("/{diary_id}", summary="删除日记")
async def delete_diary(
    diary_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除日记（软删除）"""
    diary_service = get_diary_service()

    success = diary_service.delete_diary(db, current_user.id, diary_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="日记不存在",
        )

    return {"message": "日记已删除"}


# ============ 心情记录 ============

@router.post("/mood", summary="快速记录心情", response_model=MoodRecordSchema)
async def create_mood_record(
    request: MoodCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """快速记录当前心情"""
    diary_service = get_diary_service()

    try:
        record = diary_service.create_mood_record(db, current_user.id, request)
        return MoodRecordSchema.from_orm(record)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"记录心情失败: {str(e)}",
        )


@router.get("/mood/list", summary="获取心情记录", response_model=List[MoodRecordSchema])
async def list_mood_records(
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    limit: int = Query(100, ge=1, le=1000, description="限制数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取用户的心情记录列表"""
    from datetime import datetime

    start_date_obj = None
    end_date_obj = None

    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="开始日期格式无效，应使用YYYY-MM-DD格式",
            )

    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="结束日期格式无效，应使用YYYY-MM-DD格式",
            )

    diary_service = get_diary_service()
    records = diary_service.list_mood_records(
        db,
        current_user.id,
        start_date_obj,
        end_date_obj,
        limit,
    )

    return [MoodRecordSchema.from_orm(r) for r in records]


# ============ 标签管理 ============

@router.post("/tags", summary="创建标签", response_model=DiaryTagSchema)
async def create_tag(
    request: TagCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建新标签"""
    diary_service = get_diary_service()

    try:
        tag = diary_service.create_tag(db, current_user.id, request)
        return DiaryTagSchema.from_orm(tag)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建标签失败: {str(e)}",
        )


@router.get("/tags", summary="获取标签列表", response_model=List[DiaryTagSchema])
async def list_tags(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取用户的所有标签"""
    diary_service = get_diary_service()
    tags = diary_service.list_tags(db, current_user.id)

    return [DiaryTagSchema.from_orm(t) for t in tags]


@router.put("/tags/{tag_id}", summary="更新标签", response_model=DiaryTagSchema)
async def update_tag(
    tag_id: int,
    request: TagUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新标签信息"""
    diary_service = get_diary_service()

    tag = diary_service.update_tag(db, current_user.id, tag_id, request)

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在",
        )

    return DiaryTagSchema.from_orm(tag)


@router.delete("/tags/{tag_id}", summary="删除标签")
async def delete_tag(
    tag_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除标签"""
    diary_service = get_diary_service()

    success = diary_service.delete_tag(db, current_user.id, tag_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在",
        )

    return {"message": "标签已删除"}


# ============ 统计和分析 ============

@router.get("/stats", summary="获取日记统计", response_model=DiaryStatsResponse)
async def get_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取日记统计数据"""
    diary_service = get_diary_service()

    stats = diary_service.get_stats(db, current_user.id)

    return DiaryStatsResponse(
        total_count=stats["total_count"],
        current_streak=stats["current_streak"],
        max_streak=stats["max_streak"],
        avg_mood=stats["avg_mood"],
        most_common_emotion=stats["most_common_emotion"],
        avg_words_per_day=stats["avg_words_per_day"],
        categories=stats["categories"],
        this_month_count=stats["this_month_count"],
        last_month_count=stats["last_month_count"],
    )


@router.get("/trend", summary="获取心情趋势", response_model=MoodTrendResponse)
async def get_mood_trend(
    time_range: str = Query("week", description="时间范围: week/month/quarter/year"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取心情变化趋势"""
    valid_ranges = {"week", "month", "quarter", "year"}
    if time_range not in valid_ranges:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{time_range} 不是有效的时间范围，应使用 week/month/quarter/year",
        )

    diary_service = get_diary_service()

    trend = diary_service.get_mood_trend(db, current_user.id, time_range)

    return MoodTrendResponse(
        time_range=trend["time_range"],
        start_date=trend["start_date"],
        end_date=trend["end_date"],
        avg_score=trend["avg_score"],
        trend_data=trend["trend_data"],
        emotion_distribution=trend["emotion_distribution"],
        mood_distribution=trend["mood_distribution"],
    )


@router.post("/analyze/{diary_id}", summary="AI分析日记", response_model=AnalysisResponse)
async def analyze_diary(
    diary_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """使用AI分析日记内容"""

    diary_service = get_diary_service()

    # 检查日记是否存在
    diary = diary_service.get_diary(db, current_user.id, diary_id)
    if not diary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="日记不存在",
        )

    # 异步分析
    try:
        result = await diary_service.analyze_diary(db, current_user.id, diary_id)

        return AnalysisResponse(
            status=result["status"],
            analysis=result.get("analysis"),
            suggestion=result.get("suggestion"),
            keywords=result.get("keywords"),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"分析失败: {str(e)}",
        )


# ============ 配置 ============

@router.get("/emotion-config", summary="获取情绪配置")
async def get_emotion_config():
    """获取情绪配置信息"""
    from app.services.diary_service import DiaryService
    return list(DiaryService.EMOTION_CONFIGS.values())


@router.get("/mood-config", summary="获取心情配置")
async def get_mood_config():
    """获取心情等级配置信息"""
    from app.services.diary_service import DiaryService
    return list(DiaryService.MOOD_CONFIGS.values())
