"""
情感分析API
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.services.sentiment_service import get_sentiment_service
from app.api.deps import get_current_user
from app.models import User

router = APIRouter(prefix="/sentiment", tags=["情感分析"])


class SentimentRequest(BaseModel):
    """情感分析请求"""
    text: str


class SentimentResponse(BaseModel):
    """情感分析响应"""
    label: str  # 'positive' | 'negative' | 'neutral'
    expression: str  # 表情名称
    motion: str  # 动作名称
    confidence: float  # 置信度


@router.post("/analyze", response_model=SentimentResponse, summary="分析文本情感")
async def analyze_sentiment(
    request: SentimentRequest,
    current_user: User = Depends(get_current_user),
):
    """
    分析文本的情感倾向

    返回的情绪标签用于控制AI虚拟形象的表情和动作:
    - positive: 积极情绪 -> 开心表情
    - negative: 消极情绪 -> 悲伤/生气表情
    - neutral: 中性情绪 -> 微笑表情
    """
    service = get_sentiment_service()
    result = service.analyze(request.text)

    return SentimentResponse(**result)
