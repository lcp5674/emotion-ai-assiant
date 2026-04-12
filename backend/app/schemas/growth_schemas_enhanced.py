"""
成长与激励增强模块 - Schema 定义
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class GrowthDimensionInfo(BaseModel):
    """成长维度信息"""
    id: int
    user_id: int
    dimension: str
    level: int
    experience: int
    score: float
    last_updated: datetime
    
    class Config:
        orm_mode = True


class ExpertTitleInfo(BaseModel):
    """专家称号信息"""
    id: int
    title_code: str
    name: str
    description: Optional[str]
    tier: str
    dimension: str
    required_level: int
    required_score: float
    required_badges: List[str]
    icon: Optional[str]
    
    class Config:
        orm_mode = True


class UserTitleInfo(BaseModel):
    """用户称号信息"""
    id: int
    title_id: int
    title: ExpertTitleInfo
    obtained_at: datetime
    is_equipped: bool
    
    class Config:
        orm_mode = True


class EnhancedBadgeInfo(BaseModel):
    """增强徽章信息"""
    id: int
    badge_code: str
    name: str
    description: Optional[str]
    icon: Optional[str]
    rarity: str
    time_type: str
    time_value: Optional[str]
    is_limited: bool
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    max_holders: Optional[int]
    current_holders: int
    category: Optional[str]
    condition_type: Optional[str]
    condition_value: int
    condition_meta: Dict[str, Any]
    hint: Optional[str]
    is_hidden: bool
    
    class Config:
        orm_mode = True


class UserEnhancedBadgeInfo(BaseModel):
    """用户增强徽章信息"""
    id: int
    badge_id: int
    badge: EnhancedBadgeInfo
    obtained_at: datetime
    is_displayed: bool
    display_note: Optional[str]
    obtain_number: Optional[int]
    
    class Config:
        orm_mode = True


class LoginStreakInfo(BaseModel):
    """连续打卡信息"""
    id: int
    user_id: int
    current_streak: int
    max_streak: int
    last_login_date: Optional[datetime]
    total_logins: int
    streak_rewards: Dict[str, Any]
    updated_at: datetime
    
    class Config:
        orm_mode = True


class SpecialAnniversaryInfo(BaseModel):
    """特殊纪念日信息"""
    id: int
    anniversary_code: str
    name: str
    description: Optional[str]
    anniversary_type: str
    days_required: Optional[int]
    reward_exp: int
    reward_badge_id: Optional[int]
    reward_title_id: Optional[int]
    
    class Config:
        orm_mode = True


class UserAnniversaryInfo(BaseModel):
    """用户纪念日信息"""
    id: int
    anniversary_id: int
    anniversary: SpecialAnniversaryInfo
    achieved_at: datetime
    is_rewarded: bool
    
    class Config:
        orm_mode = True


class SmartTaskInfo(BaseModel):
    """智能任务信息"""
    id: int
    user_id: int
    task_code: str
    title: str
    description: Optional[str]
    ai_generated: bool
    difficulty: str
    dimension: Optional[str]
    estimated_time_minutes: Optional[int]
    target: int
    current: int
    is_completed: bool
    is_rewarded: bool
    reward_exp: int
    reward_dimension_exp: Dict[str, int]
    deadline: Optional[datetime]
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        orm_mode = True


class GrowthOverviewResponse(BaseModel):
    """成长体系概览响应"""
    level_info: Dict[str, Any]
    dimensions: List[GrowthDimensionInfo]
    titles: List[UserTitleInfo]
    badges: Dict[str, Any]
    streak: Optional[LoginStreakInfo]
    anniversaries: List[UserAnniversaryInfo]
    smart_tasks: List[SmartTaskInfo]


class GenerateTaskRequest(BaseModel):
    """生成智能任务请求"""
    dimension: Optional[str] = Field(None, description="目标维度，如：emotional_health")
    difficulty: Optional[str] = Field(None, description="难度：easy/medium/hard")
    count: int = Field(1, ge=1, le=5, description="生成任务数量")


class CompleteSmartTaskRequest(BaseModel):
    """完成智能任务请求"""
    feedback_score: Optional[float] = Field(None, ge=1, le=5, description="用户反馈评分")
    completion_time_minutes: Optional[int] = Field(None, description="实际完成时间(分钟)")


class EquipTitleRequest(BaseModel):
    """装备称号请求"""
    is_equipped: bool = Field(..., description="是否装备")


class SetEnhancedBadgeDisplayRequest(BaseModel):
    """设置增强徽章展示请求"""
    is_displayed: bool = Field(..., description="是否展示")
    display_note: Optional[str] = Field(None, description="自定义展示语")


class RecordLoginResponse(BaseModel):
    """记录登录响应"""
    streak: LoginStreakInfo
    bonus_exp: int
    multiplier: float
    new_badges: List[Dict[str, Any]]
    new_titles: List[Dict[str, Any]]
    anniversaries: List[Dict[str, Any]]
