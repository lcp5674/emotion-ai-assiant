"""
成长体系Schema定义
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class BadgeInfo(BaseModel):
    """徽章信息"""
    id: int
    badge_code: str
    name: str
    description: Optional[str]
    icon: Optional[str]
    rarity: str
    category: Optional[str]
    condition_type: Optional[str]
    condition_value: Optional[int]
    hint: Optional[str]
    is_hidden: bool

    class Config:
        orm_mode = True


class UserBadgeInfo(BaseModel):
    """用户徽章信息"""
    id: int
    badge_code: str
    name: str
    description: Optional[str]
    icon: Optional[str]
    rarity: str
    category: Optional[str]
    obtained_at: datetime
    is_displayed: bool
    display_note: Optional[str]


class BadgeProgressResponse(BaseModel):
    """徽章进度响应"""
    total: int
    unlocked_count: int
    unlocked: List[BadgeInfo]
    locked: List[BadgeInfo]


class UserLevelResponse(BaseModel):
    """用户等级响应"""
    current_level: int
    current_exp: int
    total_exp_gained: int
    next_level: Optional[int]
    exp_to_next_level: int
    progress_percent: int


class ExpRecordResponse(BaseModel):
    """经验记录响应"""
    id: int
    action: str
    exp_gained: int
    description: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True


class GrowthTaskResponse(BaseModel):
    """成长任务响应"""
    id: int
    task_type: str
    task_code: str
    title: str
    description: Optional[str]
    target: int
    current: int
    is_completed: bool
    is_rewarded: bool
    reward_exp: int
    reward_badge_id: Optional[int]
    deadline: Optional[datetime]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        orm_mode = True


class SetBadgeDisplayRequest(BaseModel):
    """设置徽章展示请求"""
    is_displayed: bool = Field(..., description="是否展示")
    display_note: Optional[str] = Field(None, description="自定义展示语")
