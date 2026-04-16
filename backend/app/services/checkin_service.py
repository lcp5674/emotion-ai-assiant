"""
每日打卡服务 - 用户留存闭环核心功能
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
import loguru

from app.models import CheckIn, Reminder, UserLevel, ExpRecord
from app.models.growth import BadgeRarity


class CheckInService:
    """每日打卡服务"""

    # 打卡连续奖励配置
    STREAK_REWARDS = {
        1: 5,    # 第1天 5 XP
        3: 8,    # 第3天 8 XP
        7: 15,   # 第7天 15 XP
        14: 25,  # 第14天 25 XP
        30: 50,  # 第30天 50 XP
        60: 80,  # 第60天 80 XP
        90: 120, # 第90天 120 XP
    }

    # 打卡徽章定义
    CHECKIN_BADGES = [
        {
            "badge_code": "checkin_7",
            "name": "连续打卡7天",
            "description": "连续打卡7天",
            "rarity": BadgeRarity.RARE.value,
            "category": "活跃",
            "condition_type": "checkin_streak",
            "condition_value": 7,
            "hint": "连续打卡7天即可解锁",
            "is_hidden": False,
        },
        {
            "badge_code": "checkin_30",
            "name": "连续打卡30天",
            "description": "连续打卡30天",
            "rarity": BadgeRarity.EPIC.value,
            "category": "成就",
            "condition_type": "checkin_streak",
            "condition_value": 30,
            "hint": "连续打卡30天即可解锁",
            "is_hidden": False,
        },
        {
            "badge_code": "checkin_100",
            "name": "连续打卡100天",
            "description": "连续打卡100天",
            "rarity": BadgeRarity.LEGENDARY.value,
            "category": "成就",
            "condition_type": "checkin_streak",
            "condition_value": 100,
            "hint": "连续打卡100天即可解锁",
            "is_hidden": False,
        },
    ]

    def __init__(self):
        pass

    def checkin(self, db: Session, user_id: int, note: Optional[str] = None) -> Dict[str, Any]:
        """
        执行每日打卡

        Returns:
            打卡结果，包含 streak_days, xp_reward, is_new_record 等
        """
        today = date.today()

        # 检查今日是否已打卡
        existing = db.query(CheckIn).filter(
            and_(
                CheckIn.user_id == user_id,
                CheckIn.check_in_date == today,
            )
        ).first()

        if existing:
            raise ValueError("今日已打卡")

        # 计算连续打卡天数
        yesterday = today - timedelta(days=1)
        last_checkin = db.query(CheckIn).filter(
            and_(
                CheckIn.user_id == user_id,
                CheckIn.check_in_date == yesterday,
            )
        ).first()

        if last_checkin:
            streak_days = last_checkin.streak_days + 1
        else:
            streak_days = 1

        # 计算奖励
        xp_reward = self._calculate_reward(streak_days)

        # 创建打卡记录
        checkin = CheckIn(
            user_id=user_id,
            check_in_date=today,
            streak_days=streak_days,
            xp_reward=xp_reward,
            note=note,
        )
        db.add(checkin)

        # 添加经验
        self._add_exp(db, user_id, xp_reward, f"每日打卡: 连续{streak_days}天")

        # 检查打卡徽章
        self._check_and_unlock_badges(db, user_id, streak_days)

        db.commit()
        db.refresh(checkin)

        loguru.logger.info(f"用户 {user_id} 打卡成功: 连续{streak_days}天, 获得{xp_reward}XP")

        return {
            "id": checkin.id,
            "check_in_date": today.isoformat(),
            "streak_days": streak_days,
            "xp_reward": xp_reward,
            "is_new_record": streak_days > 1,
            "consecutive_checkins": streak_days,
        }

    def get_today_status(self, db: Session, user_id: int) -> Dict[str, Any]:
        """获取今日打卡状态"""
        today = date.today()

        checkin = db.query(CheckIn).filter(
            and_(
                CheckIn.user_id == user_id,
                CheckIn.check_in_date == today,
            )
        ).first()

        return {
            "checked_in": checkin is not None,
            "checkin": {
                "id": checkin.id,
                "check_in_date": checkin.check_in_date.isoformat(),
                "streak_days": checkin.streak_days,
                "xp_reward": checkin.xp_reward,
                "note": checkin.note,
            } if checkin else None,
        }

    def get_checkin_records(self, db: Session, user_id: int, limit: int = 30) -> List[CheckIn]:
        """获取打卡记录"""
        return db.query(CheckIn).filter(
            CheckIn.user_id == user_id
        ).order_by(desc(CheckIn.check_in_date)).limit(limit).all()

    def get_stats(self, db: Session, user_id: int) -> Dict[str, Any]:
        """获取打卡统计"""
        # 总打卡次数
        total_checkins = db.query(func.count(CheckIn.id)).filter(
            CheckIn.user_id == user_id
        ).scalar() or 0

        # 获取所有打卡记录用于计算
        all_checkins = db.query(CheckIn).filter(
            CheckIn.user_id == user_id
        ).order_by(desc(CheckIn.check_in_date)).all()

        # 计算当前连续天数
        current_streak = 0
        max_streak = 0
        last_checkin_date = None
        temp_streak = 0
        prev_date = None

        for checkin in all_checkins:
            if last_checkin_date is None:
                last_checkin_date = checkin.check_in_date
                temp_streak = 1
                # 检查是否昨天
                if checkin.check_in_date == date.today() - timedelta(days=1):
                    current_streak = checkin.streak_days
            else:
                if prev_date and checkin.check_in_date == prev_date - timedelta(days=1):
                    temp_streak += 1
                else:
                    temp_streak = 1
            max_streak = max(max_streak, checkin.streak_days)
            prev_date = checkin.check_in_date

        # 如果今天已打卡且昨天也打卡了，当前连续天数应该用今天的
        today = date.today()
        today_checkin = db.query(CheckIn).filter(
            and_(
                CheckIn.user_id == user_id,
                CheckIn.check_in_date == today,
            )
        ).first()
        if today_checkin:
            current_streak = today_checkin.streak_days

        # 本月打卡次数
        first_day_of_month = today.replace(day=1)
        this_month_checkins = db.query(func.count(CheckIn.id)).filter(
            and_(
                CheckIn.user_id == user_id,
                CheckIn.check_in_date >= first_day_of_month,
            )
        ).scalar() or 0

        # 总获得经验
        total_xp_earned = db.query(func.sum(CheckIn.xp_reward)).filter(
            CheckIn.user_id == user_id
        ).scalar() or 0

        # 最近打卡历史
        checkin_history = self.get_checkin_records(db, user_id, 30)

        return {
            "total_checkins": total_checkins,
            "current_streak": current_streak,
            "max_streak": max_streak,
            "total_xp_earned": int(total_xp_earned),
            "this_month_checkins": this_month_checkins,
            "last_checkin_date": last_checkin_date.isoformat() if last_checkin_date else None,
            "checkin_history": checkin_history,
        }

    def _calculate_reward(self, streak_days: int) -> int:
        """根据连续天数计算奖励"""
        # 找到最高的满足条件的奖励
        reward = self.STREAK_REWARDS.get(1)
        for days, xp in sorted(self.STREAK_REWARDS.items(), key=lambda x: x[0], reverse=True):
            if streak_days >= days:
                reward = xp
                break
        return reward

    def _add_exp(self, db: Session, user_id: int, exp: int, description: str):
        """添加经验"""
        # 获取或创建用户等级
        user_level = db.query(UserLevel).filter(
            UserLevel.user_id == user_id
        ).first()

        if not user_level:
            user_level = UserLevel(
                user_id=user_id,
                current_level=1,
                current_exp=0,
            )
            db.add(user_level)

        # 更新经验
        user_level.current_exp += exp

        # 检查升级
        LEVEL_EXP = {
            1: 0, 2: 100, 3: 300, 4: 600, 5: 1000,
            6: 1500, 7: 2100, 8: 2800, 9: 3600, 10: 4500,
            11: 5500, 12: 6600, 13: 7800, 14: 9100, 15: 10500,
            16: 12000, 17: 13600, 18: 15300, 19: 17100, 20: 19000,
        }

        while True:
            next_level = user_level.current_level + 1
            required_exp = LEVEL_EXP.get(next_level)
            if required_exp is not None and user_level.current_exp >= required_exp:
                user_level.current_level = next_level
            else:
                break

        # 记录经验获取
        record = ExpRecord(
            user_id=user_id,
            action="checkin",
            exp_gained=exp,
            description=description,
        )
        db.add(record)

    def _check_and_unlock_badges(self, db: Session, user_id: int, streak_days: int):
        """检查并解锁打卡徽章"""
        from app.models import Badge, UserBadge

        for badge_data in self.CHECKIN_BADGES:
            badge = db.query(Badge).filter(
                Badge.badge_code == badge_data["badge_code"]
            ).first()

            if not badge:
                continue

            # 检查是否已解锁
            existing = db.query(UserBadge).filter(
                and_(
                    UserBadge.user_id == user_id,
                    UserBadge.badge_id == badge.id,
                )
            ).first()

            if existing:
                continue

            # 检查是否满足条件
            if streak_days >= badge.condition_value:
                user_badge = UserBadge(
                    user_id=user_id,
                    badge_id=badge.id,
                    is_displayed=True,
                )
                db.add(user_badge)
                loguru.logger.info(f"用户 {user_id} 解锁打卡徽章: {badge.name}")

    # ============ 提醒管理 ============

    def create_reminder(
        self,
        db: Session,
        user_id: int,
        reminder_type: str,
        title: str,
        message: Optional[str],
        scheduled_time: datetime,
    ) -> Reminder:
        """创建提醒"""
        reminder = Reminder(
            user_id=user_id,
            reminder_type=reminder_type,
            title=title,
            message=message,
            scheduled_time=scheduled_time,
        )
        db.add(reminder)
        db.commit()
        db.refresh(reminder)
        return reminder

    def get_reminders(self, db: Session, user_id: int) -> Dict[str, List[Reminder]]:
        """获取用户的提醒列表"""
        pending = db.query(Reminder).filter(
            and_(
                Reminder.user_id == user_id,
                Reminder.is_sent == False,
                Reminder.is_cancelled == False,
            )
        ).order_by(Reminder.scheduled_time).all()

        sent = db.query(Reminder).filter(
            and_(
                Reminder.user_id == user_id,
                Reminder.is_sent == True,
            )
        ).order_by(desc(Reminder.sent_at)).limit(20).all()

        return {
            "pending": pending,
            "sent": sent,
        }

    def cancel_reminder(self, db: Session, user_id: int, reminder_id: int) -> bool:
        """取消提醒"""
        reminder = db.query(Reminder).filter(
            and_(
                Reminder.id == reminder_id,
                Reminder.user_id == user_id,
                Reminder.is_sent == False,
            )
        ).first()

        if not reminder:
            return False

        reminder.is_cancelled = True
        db.commit()
        return True


# 全局实例
_checkin_service: Optional[CheckInService] = None


def get_checkin_service() -> CheckInService:
    """获取打卡服务实例"""
    global _checkin_service
    if _checkin_service is None:
        _checkin_service = CheckInService()
    return _checkin_service
