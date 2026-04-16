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
        from_attributes = True


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
        from_attributes = True


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
        from_attributes = True


class SetBadgeDisplayRequest(BaseModel):
    """设置徽章展示请求"""
    is_displayed: bool = Field(..., description="是否展示")
    display_note: Optional[str] = Field(None, description="自定义展示语")


# ============ 打卡相关Schema ============

class CheckInRequest(BaseModel):
    """打卡请求"""
    note: Optional[str] = Field(None, description="打卡备注")


class CheckInResponse(BaseModel):
    """打卡响应"""
    id: int
    check_in_date: str
    streak_days: int
    xp_reward: int
    is_new_record: bool
    consecutive_checkins: int

    class Config:
        from_attributes = True


class CheckInRecordResponse(BaseModel):
    """打卡记录响应"""
    id: int
    check_in_date: str
    check_in_time: datetime
    streak_days: int
    xp_reward: int
    note: Optional[str]

    class Config:
        from_attributes = True


class CheckInStatsResponse(BaseModel):
    """打卡统计响应"""
    total_checkins: int
    current_streak: int
    max_streak: int
    total_xp_earned: int
    this_month_checkins: int
    last_checkin_date: Optional[str]
    checkin_history: List[CheckInRecordResponse]


# ============ 提醒相关Schema ============

class ReminderCreateRequest(BaseModel):
    """创建提醒请求"""
    reminder_type: str = Field(..., description="提醒类型: daily_checkin/diary_reminder/return_visit")
    title: str = Field(..., description="提醒标题")
    message: Optional[str] = Field(None, description="提醒内容")
    scheduled_time: datetime = Field(..., description="计划发送时间")


class ReminderResponse(BaseModel):
    """提醒响应"""
    id: int
    reminder_type: str
    title: str
    message: Optional[str]
    scheduled_time: datetime
    is_sent: bool
    is_cancelled: bool
    sent_at: Optional[datetime]

    class Config:
        from_attributes = True


class ReminderListResponse(BaseModel):
    """提醒列表响应"""
    pending: List[ReminderResponse]
    sent: List[ReminderResponse]
