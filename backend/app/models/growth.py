"""
用户成长体系和成就徽章模型
"""
import enum
from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean, Text, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class BadgeRarity(enum.Enum):
    """徽章稀有度"""
    COMMON = "common"     # 普通
    RARE = "rare"         # 稀有
    EPIC = "epic"         # 史诗
    LEGENDARY = "legendary"  # 传说


class Badge(Base):
    """成就徽章定义表"""
    __tablename__ = "badges"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    badge_code = Column(String(50), unique=True, nullable=False, index=True, comment="徽章编码")
    name = Column(String(100), nullable=False, comment="徽章名称")
    description = Column(String(500), nullable=True, comment="徽章描述")
    icon = Column(String(500), nullable=True, comment="图标URL")
    rarity = Column(String(20), nullable=False, default="common", comment="稀有度")
    category = Column(String(50), nullable=True, comment="分类: 入门/活跃/成就/隐藏")

    # 获取条件
    condition_type = Column(String(50), nullable=True, comment="解锁条件类型: login_days/conversation_count/diary_count")
    condition_value = Column(Integer, default=1, comment="条件值")
    hint = Column(String(200), nullable=True, comment="获取提示（对未解锁用户显示）")

    # 是否隐藏（未解锁时不显示）
    is_hidden = Column(Boolean, default=False, comment="是否隐藏")
    is_active = Column(Boolean, default=True, comment="是否启用")

    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    def __repr__(self):
        return f"<Badge(code={self.badge_code}, name={self.name}, rarity={self.rarity})>"


class UserBadge(Base):
    """用户获得的徽章"""
    __tablename__ = "user_badges"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    badge_id = Column(Integer, ForeignKey("badges.id"), nullable=False, index=True, comment="徽章ID")

    # 获取时间
    obtained_at = Column(DateTime, server_default=func.now(), comment="获取时间")
    is_displayed = Column(Boolean, default=True, comment="是否在个人资料展示")

    # 自定义展示语
    display_note = Column(String(200), nullable=True, comment="自定义展示语")

    # 关系
    badge = relationship("Badge")
    user = relationship("User")

    __table_args__ = (
        # 同一用户同一徽章只能获得一次
        # UniqueConstraint('user_id', 'badge_id', name='uix_user_badge'),
    )

    def __repr__(self):
        return f"<UserBadge(user_id={self.user_id}, badge_id={self.badge_id})>"


class UserLevel(Base):
    """用户等级经验"""
    __tablename__ = "user_levels"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, comment="用户ID")

    current_level = Column(Integer, default=1, comment="当前等级")
    current_exp = Column(Integer, default=0, comment="当前经验")

    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    def __repr__(self):
        return f"<UserLevel(user_id={self.user_id}, level={self.current_level}, exp={self.current_exp})>"


class ExpRecord(Base):
    """经验获取记录"""
    __tablename__ = "exp_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")

    action = Column(String(50), nullable=False, comment="获取动作: chat/diary/login/achievement")
    exp_gained = Column(Integer, nullable=False, comment="获得经验")
    description = Column(String(200), nullable=True, comment="描述")
    related_id = Column(Integer, nullable=True, comment="关联ID")

    created_at = Column(DateTime, server_default=func.now(), comment="获取时间")

    def __repr__(self):
        return f"<ExpRecord(user_id={self.user_id}, action={self.action}, exp={self.exp_gained})>"


class CheckIn(Base):
    """每日打卡记录"""
    __tablename__ = "check_ins"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    check_in_date = Column(Date, nullable=False, comment="打卡日期")
    check_in_time = Column(DateTime, server_default=func.now(), comment="打卡时间")
    streak_days = Column(Integer, default=1, comment="连续打卡天数")
    xp_reward = Column(Integer, default=5, comment="获得经验")
    note = Column(String(200), nullable=True, comment="打卡备注")

    # 关系
    user = relationship("User")

    __table_args__ = (
        # 同一用户同一天只能打卡一次
        UniqueConstraint('user_id', 'check_in_date', name='uix_user_check_in_date'),
    )

    def __repr__(self):
        return f"<CheckIn(user_id={self.user_id}, date={self.check_in_date}, streak={self.streak_days})>"


class Reminder(Base):
    """回访提醒"""
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")

    reminder_type = Column(String(50), nullable=False, comment="提醒类型: daily_checkin/diary_reminder/return_visit")
    title = Column(String(100), nullable=False, comment="提醒标题")
    message = Column(String(500), nullable=True, comment="提醒内容")
    scheduled_time = Column(DateTime, nullable=False, comment="计划发送时间")
    is_sent = Column(Boolean, default=False, comment="是否已发送")
    is_cancelled = Column(Boolean, default=False, comment="是否已取消")
    sent_at = Column(DateTime, nullable=True, comment="实际发送时间")

    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    # 关系
    user = relationship("User")

    def __repr__(self):
        return f"<Reminder(user_id={self.user_id}, type={self.reminder_type}, scheduled={self.scheduled_time})>"


class GrowthTask(Base):
    """成长任务"""
    __tablename__ = "growth_tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")

    task_type = Column(String(50), nullable=False, comment="任务类型")
    task_code = Column(String(50), nullable=False, comment="任务编码")
    title = Column(String(100), nullable=False, comment="任务标题")
    description = Column(String(300), nullable=True, comment="任务描述")

    target = Column(Integer, nullable=False, comment="目标值")
    current = Column(Integer, default=0, comment="当前进度")
    is_completed = Column(Boolean, default=False, comment="是否完成")
    is_rewarded = Column(Boolean, default=False, comment="是否已领取奖励")

    reward_exp = Column(Integer, default=0, comment="奖励经验")
    reward_badge_id = Column(Integer, nullable=True, comment="奖励徽章ID")

    deadline = Column(DateTime, nullable=True, comment="截止时间")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    completed_at = Column(DateTime, nullable=True, comment="完成时间")

    def __repr__(self):
        return f"<GrowthTask(user_id={self.user_id}, task={self.task_code}, completed={self.is_completed})>"
