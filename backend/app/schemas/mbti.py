"""
MBTI相关Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class MbtiQuestionSchema(BaseModel):
    """MBTI题目"""
    id: int
    dimension: str
    question_no: int
    question_text: str
    option_a: str
    option_b: str

    class Config:
        from_attributes = True


class MbtiQuestionListResponse(BaseModel):
    """题目列表响应"""
    total: int
    questions: List[MbtiQuestionSchema]


class MbtiAnswerSubmit(BaseModel):
    """提交答案"""
    question_id: int
    answer: str = Field(..., pattern="^[AB]$")


class MbtiTestSubmit(BaseModel):
    """提交测试"""
    answers: List[MbtiAnswerSubmit]


class MbtiDimensionScore(BaseModel):
    """维度得分"""
    dimension: str
    score: int
    tendency: str  # 倾向: E/I, S/N, T/F, J/P


class MbtiResultSchema(BaseModel):
    """MBTI结果"""
    id: int
    mbti_type: str
    ei_score: int
    sn_score: int
    tf_score: int
    jp_score: int
    dimensions: List[MbtiDimensionScore]
    personality: str
    strengths: List[str]
    weaknesses: List[str]
    suitable_jobs: List[str]
    relationship_tips: str
    career_advice: str
    created_at: datetime

    class Config:
        from_attributes = True


class MbtiTestStartResponse(BaseModel):
    """开始测试响应"""
    session_id: str
    total_questions: int
    estimated_time: int  # 分钟


class AiAssistantSchema(BaseModel):
    """AI助手"""
    id: int
    name: str
    avatar: Optional[str] = None
    mbti_type: str
    personality: Optional[str] = None
    speaking_style: Optional[str] = None
    expertise: Optional[str] = None
    greeting: Optional[str] = None
    tags: Optional[str] = None
    is_recommended: bool = False

    class Config:
        from_attributes = True


class AiAssistantListResponse(BaseModel):
    """助手列表响应"""
    total: int
    list: List[AiAssistantSchema]


class RecommendAssistantRequest(BaseModel):
    """推荐助手请求"""
    mbti_type: Optional[str] = None
    tags: Optional[List[str]] = None
    expertise: Optional[List[str]] = None