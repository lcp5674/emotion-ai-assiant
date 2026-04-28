"""
情感日记API
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

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
        diary = await diary_service.create_diary(db, current_user.id, request)
        db.commit()  # 显式提交事务
        return DiaryDetailSchema.model_validate(diary)

    except ValueError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建日记失败: {str(e)}",
        )


# ============ 统计和分析 ============

@router.get("/stats", summary="获取日记统计", response_model=DiaryStatsResponse)
async def get_stats(
    time_range: str = Query("month", description="时间范围: week/month/quarter/year"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取日记统计数据"""
    diary_service = get_diary_service()

    stats = diary_service.get_stats(db, current_user.id, time_range)

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
        period_count=stats["period_count"],
    )


@router.get("/trend", summary="获取心情趋势", response_model=MoodTrendResponse)
async def get_mood_trend(
    time_range: str = Query("week", description="时间范围: week/month/quarter/year/all"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取心情变化趋势"""
    valid_ranges = {"week", "month", "quarter", "year", "all"}
    if time_range not in valid_ranges:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{time_range} 不是有效的时间范围，应使用 week/month/quarter/year/all",
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


# ============ 日记操作 ============

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

    return DiaryDetailSchema.model_validate(diary)


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
        data=[DiarySummarySchema.model_validate(d) for d in diaries],
    )


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
        return MoodRecordSchema.model_validate(record)

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

    return [MoodRecordSchema.model_validate(r) for r in records]


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
        return DiaryTagSchema.model_validate(tag)

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

    return [DiaryTagSchema.model_validate(t) for t in tags]


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

    return DiaryTagSchema.model_validate(tag)


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


# ============ AI分析 ============

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


@router.get("/trend/share-image", summary="生成情绪趋势分享图片")
async def generate_mood_trend_share_image(
    time_range: str = Query("week", description="时间范围: week/month/quarter/year"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """生成情绪趋势分享图片"""
    from app.services.diary_service import get_diary_service
    
    diary_service = get_diary_service()
    trend = diary_service.get_mood_trend(db, current_user.id, time_range)
    
    # 生成分享图片数据
    share_data = {
        "username": current_user.nickname or "用户",
        "time_range": trend["time_range"],
        "avg_score": trend["avg_score"],
        "trend_data": trend["trend_data"],
        "emotion_distribution": trend["emotion_distribution"],
        "mood_distribution": trend["mood_distribution"],
        "generated_at": datetime.now().isoformat(),
    }
    
    return share_data


@router.get("/privacy-policy", summary="获取隐私政策")
async def get_privacy_policy():
    """获取数据隐私说明"""
    return {
        "title": "数据隐私保护说明",
        "content": """
<h2>数据隐私保护说明</h2>
<p>我们非常重视您的数据隐私保护：</p>
<ul>
  <li><strong>数据所有权：</strong>您记录的所有数据（日记、心情、MBTI结果）都完全属于您</li>
  <li><strong>加密存储：</strong>您的个人数据采用加密方式存储，只有您本人可以访问</li>
  <li><strong>AI处理说明：</strong>当您使用AI功能时，内容会被发送给AI服务商处理，我们不会将您的数据用于其他用途</li>
  <li><strong>第三方分享：</strong>我们绝不会将您的个人数据出售或分享给第三方用于广告或营销目的</li>
  <li><strong>数据导出：</strong>您可以随时导出或删除您的所有个人数据</li>
  <li><strong>本地优先：</strong>在技术允许的范围内，我们优先采用本地处理的方式保护您的隐私</li>
</ul>
<h3>数据使用范围</h3>
<p>我们仅在以下情况使用您的数据：</p>
<ul>
  <li>为您提供AI情感陪伴服务</li>
  <li>生成您的情绪统计和成长报告</li>
  <li>改进和优化服务质量</li>
  <li>遵循法律法规要求</li>
</ul>
        """.strip(),
        "last_updated": "2024-01-01",
        "version": "1.0"
    }


@router.get("/terms-of-service", summary="获取用户服务条款")
async def get_terms_of_service():
    """获取用户服务条款"""
    return {
        "title": "用户服务条款",
        "last_updated": "2024-01-01",
        "version": "1.0"
    }


# ============ 日记详情（放在最后，避免拦截其他路由）============

# PUT和DELETE路由也放在最后，避免拦截隐私政策等服务条款路由
@router.put("/{diary_id}", summary="更新日记", response_model=DiaryDetailSchema)
async def update_diary(
    diary_id: int,
    request: DiaryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新日记内容"""
    diary_service = get_diary_service()

    diary = await diary_service.update_diary(db, current_user.id, diary_id, request)

    if not diary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="日记不存在",
        )

    return DiaryDetailSchema.model_validate(diary)


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

    return DiaryDetailSchema.model_validate(diary)
