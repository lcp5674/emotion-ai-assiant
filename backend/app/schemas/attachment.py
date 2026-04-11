"""
依恋风格相关Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class AttachmentQuestionSchema(BaseModel):
    """依恋风格题目"""
    id: int
    question_no: int
    question_text: str
    scale_min: int = 1
    scale_max: int = 7
    scale_min_label: str = "完全不符合"
    scale_max_label: str = "完全符合"

    class Config:
        from_attributes = True


class AttachmentQuestionListResponse(BaseModel):
    """依恋风格题目列表响应"""
    total: int
    questions: List[AttachmentQuestionSchema]


class AttachmentAnswerSubmit(BaseModel):
    """提交答案"""
    question_id: int
    score: int = Field(..., ge=1, le=7, description="得分(1-7)")


class AttachmentTestSubmit(BaseModel):
    """提交依恋风格测试"""
    answers: List[AttachmentAnswerSubmit]


class AttachmentStyleInfo(BaseModel):
    """依恋风格信息"""
    name: str
    description: str
    characteristics: List[str]
    strengths: List[str]
    challenges: List[str]
    relationship_patterns: List[str]
    growth_areas: List[str]


class AttachmentResultResponse(BaseModel):
    """依恋风格结果响应"""
    id: int
    style: str
    anxiety_score: float
    avoidance_score: float
    characteristics: List[str] = []
    relationship_tips: str = ""
    self_growth_tips: str = ""
    created_at: datetime

    class Config:
        from_attributes = True
