"""
成长与激励增强模块 - 增强数据模型
包含多维度成长指标、专家称号、稀有徽章、限定成就、特殊纪念日奖励等
"""
import enum
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON, Float, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class GrowthDimension(enum.Enum):
    """成长维度类型"""
    EMOTIONAL_HEALTH = "emotional_health"      # 情感健康
    SELF_AWARENESS = "self_awareness"            # 自我认知
    SOCIAL_SKILLS = "social_skills"              # 社交能力
    RESILIENCE = "resilience"                    # 心理韧性
    CREATIVITY = "creativity"                    # 创造力
    MINDFULNESS = "mindfulness"                  # 正念觉察


class TitleTier(enum.Enum):
    """称号等级"""
    NOVICE = "novice"            # 新手
    APPRENTICE = "apprentice"    # 学徒
    JOURNEYMAN = "journeyman"    # 熟练工
    EXPERT = "expert"            # 专家
    MASTER = "master"            # 大师
    GRANDMASTER = "grandmaster"  # 宗师


class BadgeTimeType(enum.Enum):
    """限定徽章时间类型"""
    NONE = "none"                 # 不限定
    SEASONAL = "seasonal"         # 季节性
    HOLIDAY = "holiday"           # 节日
    ANNIVERSARY = "anniversary"   # 周年纪念
    LIMITED = "limited"           # 限时活动


class UserGrowthDimension(Base):
    """用户多维度成长指标"""
    __tablename__ = "user_growth_dimensions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    dimension = Column(String(50), nullable=False, comment="成长维度")
    level = Column(Integer, default=1, comment="维度等级")
    experience = Column(Integer, default=0, comment="维度经验")
    score = Column(Float, default=0.0, comment="综合评分 (0-100)")
    
    # 历史记录
    score_history = Column(JSON, default=list, comment="评分历史")
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        UniqueConstraint('user_id', 'dimension', name='uix_user_dimension'),
    )


class ExpertTitle(Base):
    """专家称号定义"""
    __tablename__ = "expert_titles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title_code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    tier = Column(String(20), nullable=False)
    dimension = Column(String(50), nullable=False)
    
    # 解锁条件
    required_level = Column(Integer, default=1)
    required_score = Column(Float, default=0.0)
    required_badges = Column(JSON, default=list, comment="所需徽章编码列表")
    
    icon = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class UserTitle(Base):
    """用户获得的称号"""
    __tablename__ = "user_titles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title_id = Column(Integer, ForeignKey("expert_titles.id"), nullable=False, index=True)
    
    obtained_at = Column(DateTime, server_default=func.now())
    is_equipped = Column(Boolean, default=False)
    
    title = relationship("ExpertTitle")
    user = relationship("User")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'title_id', name='uix_user_title'),
    )


class EnhancedBadge(Base):
    """增强徽章定义（稀有徽章、限定成就）"""
    __tablename__ = "enhanced_badges"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    badge_code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    icon = Column(String(500), nullable=True)
    
    # 稀有度（增加更多等级）
    rarity = Column(String(20), nullable=False, default="common")
    time_type = Column(String(20), nullable=False, default="none")
    time_value = Column(String(100), nullable=True, comment="时间限定值")
    
    # 限定信息
    is_limited = Column(Boolean, default=False)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    max_holders = Column(Integer, nullable=True, comment="最大持有者数量")
    current_holders = Column(Integer, default=0)
    
    category = Column(String(50), nullable=True)
    condition_type = Column(String(50), nullable=True)
    condition_value = Column(Integer, default=1)
    condition_meta = Column(JSON, default=dict, comment="复杂条件配置")
    
    hint = Column(String(200), nullable=True)
    is_hidden = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class UserEnhancedBadge(Base):
    """用户获得的增强徽章"""
    __tablename__ = "user_enhanced_badges"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    badge_id = Column(Integer, ForeignKey("enhanced_badges.id"), nullable=False, index=True)
    
    obtained_at = Column(DateTime, server_default=func.now())
    is_displayed = Column(Boolean, default=True)
    display_note = Column(String(200), nullable=True)
    
    # 获得时的序号（用于稀有编号）
    obtain_number = Column(Integer, nullable=True)
    
    badge = relationship("EnhancedBadge")
    user = relationship("User")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'badge_id', name='uix_user_enhanced_badge'),
    )


class LoginStreak(Base):
    """连续打卡记录"""
    __tablename__ = "login_streaks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    
    current_streak = Column(Integer, default=0, comment="当前连续天数")
    max_streak = Column(Integer, default=0, comment="历史最大连续天数")
    last_login_date = Column(DateTime, nullable=True)
    total_logins = Column(Integer, default=0, comment="总登录次数")
    
    # 连续打卡奖励记录
    streak_rewards = Column(JSON, default=dict, comment="已领取的连续奖励")
    
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class SpecialAnniversary(Base):
    """特殊纪念日定义"""
    __tablename__ = "special_anniversaries"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    anniversary_code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    
    # 纪念日类型
    anniversary_type = Column(String(50), nullable=False, comment="registration/usage/milestone")
    days_required = Column(Integer, nullable=True, comment="需要的天数")
    
    # 奖励
    reward_exp = Column(Integer, default=0)
    reward_badge_id = Column(Integer, ForeignKey("enhanced_badges.id"), nullable=True)
    reward_title_id = Column(Integer, ForeignKey("expert_titles.id"), nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class UserAnniversary(Base):
    """用户纪念日记录"""
    __tablename__ = "user_anniversaries"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    anniversary_id = Column(Integer, ForeignKey("special_anniversaries.id"), nullable=False, index=True)
    
    achieved_at = Column(DateTime, server_default=func.now())
    is_rewarded = Column(Boolean, default=False)
    
    anniversary = relationship("SpecialAnniversary")
    user = relationship("User")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'anniversary_id', name='uix_user_anniversary'),
    )


class SmartTask(Base):
    """智能任务"""
    __tablename__ = "smart_tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    task_code = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # AI生成相关
    ai_generated = Column(Boolean, default=True)
    generation_prompt = Column(Text, nullable=True)
    user_profile = Column(JSON, default=dict, comment="生成时的用户画像")
    
    # 任务属性
    difficulty = Column(String(20), nullable=False, default="easy")
    dimension = Column(String(50), nullable=True)
    estimated_time_minutes = Column(Integer, nullable=True)
    
    # 进度
    target = Column(Integer, default=1)
    current = Column(Integer, default=0)
    is_completed = Column(Boolean, default=False)
    is_rewarded = Column(Boolean, default=False)
    
    # 奖励
    reward_exp = Column(Integer, default=0)
    reward_dimension_exp = Column(JSON, default=dict, comment="各维度经验奖励")
    
    # 自适应调整
    difficulty_adjustment = Column(JSON, default=dict, comment="难度调整记录")
    success_rate = Column(Float, default=0.0, comment="历史成功率")
    
    deadline = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)


class TaskDifficultyHistory(Base):
    """任务难度历史记录（用于自适应调整）"""
    __tablename__ = "task_difficulty_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    task_id = Column(Integer, ForeignKey("smart_tasks.id"), nullable=True)
    
    dimension = Column(String(50), nullable=False)
    difficulty = Column(String(20), nullable=False)
    completion_time_minutes = Column(Integer, nullable=True)
    was_successful = Column(Boolean, nullable=False)
    
    feedback_score = Column(Float, nullable=True, comment="用户反馈评分 (1-5)")
    created_at = Column(DateTime, server_default=func.now())
