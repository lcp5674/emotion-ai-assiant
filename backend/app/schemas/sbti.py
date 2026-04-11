"""
SBTI相关Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class SbtiQuestionSchema(BaseModel):
    """SBTI题目"""
    id: int
    question_no: int
    statement_a: str
    theme_a: str
    statement_b: str
    theme_b: str
    domain: str

    class Config:
        from_attributes = True


class SbtiQuestionListResponse(BaseModel):
    """SBTI题目列表响应"""
    total: int
    questions: List[SbtiQuestionSchema]


class SbtiAnswerSubmit(BaseModel):
    """提交答案"""
    question_id: int
    answer: str = Field(..., pattern="^[AB]$", description="选项A或B")


class SbtiTestSubmit(BaseModel):
    """提交SBTI测试"""
    answers: List[SbtiAnswerSubmit]


class ThemeDetail(BaseModel):
    """才干主题详情"""
    rank: int
    score: int
    description: str
    strengths: List[str] = []
    growth_suggestions: List[str] = []


class DomainDistribution(BaseModel):
    """领域分布"""
    执行力: float = 0
    影响力: float = 0
    关系建立: float = 0
    战略思维: float = 0


class RelationshipInsights(BaseModel):
    """关系洞察"""
    strengths: List[str] = []
    communication_style: str = ""
    growth_areas: List[str] = []


class SbtiResultResponse(BaseModel):
    """SBTI结果响应"""
    id: int
    top5_themes: List[str]
    top5_scores: List[int]
    domain_scores: Dict[str, float]
    dominant_domain: str
    report: Dict[str, Any] = {}
    created_at: datetime

    class Config:
        from_attributes = True


class ThemeInfo(BaseModel):
    """才干主题信息"""
    name: str
    description: str
    domain: str
    strengths: List[str]
    weaknesses: List[str]
    relationships: List[str]
    career_paths: List[str]
    growth_tips: List[str]


class SbtiThemeDetailResponse(BaseModel):
    """SBTI才干主题详情响应"""
    theme: str
    info: ThemeInfo
