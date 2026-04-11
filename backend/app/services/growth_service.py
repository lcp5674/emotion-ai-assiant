"""
用户成长体系服务 - 等级经验和成就徽章
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
import loguru

from app.models import Badge, UserBadge, UserLevel, ExpRecord, GrowthTask
from app.models.growth import BadgeRarity


class GrowthService:
    """用户成长服务"""

    # 等级经验配置 - 每一级需要的经验
    LEVEL_EXP = {
        1: 0,
        2: 100,
        3: 300,
        4: 600,
        5: 1000,
        6: 1500,
        7: 2100,
        8: 2800,
        9: 3600,
        10: 4500,
        11: 5500,
        12: 6600,
        13: 7800,
        14: 9100,
        15: 10500,
        16: 12000,
        17: 13600,
        18: 15300,
        19: 17100,
        20: 19000,
    }

    # 经验获取配置
    EXP_CONFIG = {
        "chat": 5,           # 每次对话获得5经验
        "diary": 10,         # 写日记获得10经验
        "login_daily": 2,    # 每日登录获得2经验
        "badge_unlock": 50,  # 解锁徽章获得50经验
        "task_complete": 30, # 完成任务获得30经验
    }

    # 默认徽章数据
    DEFAULT_BADGES = [
        {
            "badge_code": "first_chat",
            "name": "第一次倾诉",
            "description": "完成第一次对话",
            "rarity": BadgeRarity.COMMON.value,
            "category": "入门",
            "condition_type": "conversation_count",
            "condition_value": 1,
            "hint": "完成第一次对话即可解锁",
            "is_hidden": False,
        },
        {
            "badge_code": "first_diary",
            "name": "心情记录者",
            "description": "写下第一篇情感日记",
            "rarity": BadgeRarity.COMMON.value,
            "category": "入门",
            "condition_type": "diary_count",
            "condition_value": 1,
            "hint": "写下第一篇情感日记即可解锁",
            "is_hidden": False,
        },
        {
            "badge_code": "seven_days",
            "name": "坚持一周",
            "description": "连续七天记录心情",
            "rarity": BadgeRarity.RARE.value,
            "category": "活跃",
            "condition_type": "login_streak",
            "condition_value": 7,
            "hint": "连续七天访问即可解锁",
            "is_hidden": False,
        },
        {
            "badge_code": "chat_10",
            "name": "倾诉达人",
            "description": "完成10次对话",
            "rarity": BadgeRarity.RARE.value,
            "category": "活跃",
            "condition_type": "conversation_count",
            "condition_value": 10,
            "hint": "完成10次对话即可解锁",
            "is_hidden": False,
        },
        {
            "badge_code": "diary_10",
            "name": "日记爱好者",
            "description": "写下10篇情感日记",
            "rarity": BadgeRarity.RARE.value,
            "category": "活跃",
            "condition_type": "diary_count",
            "condition_value": 10,
            "hint": "写下10篇情感日记即可解锁",
            "is_hidden": False,
        },
        {
            "badge_code": "chat_100",
            "name": "深度交流",
            "description": "完成100次对话",
            "rarity": BadgeRarity.EPIC.value,
            "category": "成就",
            "condition_type": "conversation_count",
            "condition_value": 100,
            "hint": "完成100次对话即可解锁",
            "is_hidden": False,
        },
        {
            "badge_code": "thirty_days",
            "name": "一月坚持",
            "description": "连续三十天记录心情",
            "rarity": BadgeRarity.EPIC.value,
            "category": "成就",
            "condition_type": "login_streak",
            "condition_value": 30,
            "hint": "连续三十天访问即可解锁",
            "is_hidden": False,
        },
        {
            "badge_code": "vip_member",
            "name": "VIP会员",
            "description": "成为VIP会员支持我们",
            "rarity": BadgeRarity.LEGENDARY.value,
            "category": "会员",
            "condition_type": "member_level",
            "condition_value": 1,
            "hint": "成为VIP会员即可解锁",
            "is_hidden": False,
        },
    ]

    def __init__(self):
        pass

    # ============ 徽章管理 ============

    def init_default_badges(self, db: Session):
        """初始化默认徽章数据"""
        for badge_data in self.DEFAULT_BADGES:
            existing = db.query(Badge).filter(Badge.badge_code == badge_data["badge_code"]).first()
            if not existing:
                badge = Badge(**badge_data)
                db.add(badge)

        db.commit()
        loguru.logger.info("默认徽章数据初始化完成")

    def get_all_badges(self, db: Session) -> List[Badge]:
        """获取所有徽章"""
        return db.query(Badge).filter(Badge.is_active == True).order_by(Badge.rarity, Badge.category).all()

    def get_user_badges(self, db: Session, user_id: int) -> List[dict]:
        """获取用户已获得的徽章"""
        query = db.query(Badge, UserBadge).join(
            UserBadge,
            and_(
                UserBadge.badge_id == Badge.id,
                UserBadge.user_id == user_id,
            )
        ).filter(Badge.is_active == True)

        result = []
        for badge, user_badge in query.all():
            result.append({
                "id": badge.id,
                "badge_code": badge.badge_code,
                "name": badge.name,
                "description": badge.description,
                "icon": badge.icon,
                "rarity": badge.rarity,
                "category": badge.category,
                "obtained_at": user_badge.obtained_at,
                "is_displayed": user_badge.is_displayed,
                "display_note": user_badge.display_note,
            })

        return result

    def get_badge_progress(self, db: Session, user_id: int) -> Dict[str, Any]:
        """获取徽章解锁进度"""
        all_badges = self.get_all_badges(db)
        user_badge_ids = [
            ub.badge_id for ub in
            db.query(UserBadge).filter(UserBadge.user_id == user_id).all()
        ]

        unlocked = []
        locked = []

        for badge in all_badges:
            if badge.id in user_badge_ids:
                unlocked.append({
                    "id": badge.id,
                    "badge_code": badge.badge_code,
                    "name": badge.name,
                    "description": badge.description,
                    "icon": badge.icon,
                    "rarity": badge.rarity,
                    "category": badge.category,
                })
            else:
                if not badge.is_hidden:
                    locked.append({
                        "id": badge.id,
                        "badge_code": badge.badge_code,
                        "name": badge.name,
                        "description": badge.hint or "？？？",
                        "icon": badge.icon,
                        "rarity": badge.rarity,
                        "category": badge.category,
                        "condition_type": badge.condition_type,
                        "condition_value": badge.condition_value,
                        "is_locked": True,
                    })

        return {
            "total": len(all_badges),
            "unlocked_count": len(unlocked),
            "unlocked": unlocked,
            "locked": locked,
        }

    def check_and_unlock_badges(self, db: Session, user_id: int) -> List[Badge]:
        """检查并解锁新徽章"""
        # 获取用户已有的徽章ID
        existing_badge_ids = [
            ub.badge_id for ub in
            db.query(UserBadge).filter(UserBadge.user_id == user_id).all()
        ]

        # 获取所有未获得且激活的徽章
        candidates = db.query(Badge).filter(
            Badge.is_active == True,
            ~Badge.id.in_(existing_badge_ids),
        ).all()

        newly_unlocked = []

        for badge in candidates:
            if self._check_badge_condition(db, user_id, badge):
                # 解锁徽章
                user_badge = UserBadge(
                    user_id=user_id,
                    badge_id=badge.id,
                    is_displayed=True,
                )
                db.add(user_badge)

                # 奖励经验
                self.add_exp(db, user_id, "badge_unlock", badge.id)
                newly_unlocked.append(badge)
                loguru.logger.info(f"用户 {user_id} 解锁徽章: {badge.name}")

        if newly_unlocked:
            db.commit()

        return newly_unlocked

    def _check_badge_condition(self, db: Session, user_id: int, badge: Badge) -> bool:
        """检查是否满足徽章解锁条件"""
        from app.models import Conversation, EmotionDiary, User

        condition_type = badge.condition_type
        target = badge.condition_value

        if condition_type == "conversation_count":
            count = db.query(Conversation).filter(
                Conversation.user_id == user_id
            ).count()
            return count >= target

        elif condition_type == "diary_count":
            count = db.query(EmotionDiary).filter(
                EmotionDiary.user_id == user_id,
                EmotionDiary.is_deleted == False,
            ).count()
            return count >= target

        elif condition_type == "member_level":
            user = db.query(User).filter(User.id == user_id).first()
            if user and user.member_level.value != "free":
                return True
            return False

        # TODO: 其他条件后续实现
        return False

    def set_badge_display(
        self,
        db: Session,
        user_id: int,
        badge_id: int,
        is_displayed: bool,
        display_note: Optional[str] = None,
    ) -> bool:
        """设置徽章是否展示"""
        user_badge = db.query(UserBadge).filter(
            and_(
                UserBadge.user_id == user_id,
                UserBadge.badge_id == badge_id,
            )
        ).first()

        if not user_badge:
            return False

        user_badge.is_displayed = is_displayed
        if display_note is not None:
            user_badge.display_note = display_note

        db.commit()
        return True

    # ============ 等级经验 ============

    def get_or_create_user_level(self, db: Session, user_id: int) -> UserLevel:
        """获取或创建用户等级信息"""
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
            db.commit()
            db.refresh(user_level)

        return user_level

    def get_user_level_info(self, db: Session, user_id: int) -> Dict[str, Any]:
        """获取用户等级信息"""
        user_level = self.get_or_create_user_level(db, user_id)

        # 计算下一等级需要的经验
        next_level = user_level.current_level + 1
        exp_needed = self.LEVEL_EXP.get(next_level, None)
        current_level_exp_needed = self.LEVEL_EXP.get(user_level.current_level, 0)

        if exp_needed is None:
            # 已经是最高级
            exp_to_next = 0
            progress = 100
        else:
            exp_to_next = exp_needed - user_level.current_exp
            progress = int((user_level.current_exp - current_level_exp_needed) / (exp_needed - current_level_exp_needed) * 100)

        # 统计经验记录
        total_exp_gained = db.query(func.sum(ExpRecord.exp_gained)).filter(
            ExpRecord.user_id == user_id
        ).scalar() or 0

        return {
            "current_level": user_level.current_level,
            "current_exp": user_level.current_exp,
            "total_exp_gained": total_exp_gained,
            "next_level": next_level if exp_needed else None,
            "exp_to_next_level": exp_to_next,
            "progress_percent": progress,
        }

    def add_exp(
        self,
        db: Session,
        user_id: int,
        action: str,
        related_id: Optional[int] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        添加经验

        Args:
            db: 数据库会话
            user_id: 用户ID
            action: 动作类型
            related_id: 关联ID
            description: 描述

        Returns:
            经验添加结果，包含是否升级
        """
        exp_gained = self.EXP_CONFIG.get(action, 0)
        if exp_gained <= 0:
            return {"added": 0, "level_up": False}

        # 获取用户当前等级
        user_level = self.get_or_create_user_level(db, user_id)

        # 记录经验获取
        record = ExpRecord(
            user_id=user_id,
            action=action,
            exp_gained=exp_gained,
            description=description,
            related_id=related_id,
        )
        db.add(record)

        # 更新经验
        old_level = user_level.current_level
        user_level.current_exp += exp_gained

        # 检查是否升级
        leveled_up = False
        while True:
            next_level = user_level.current_level + 1
            required_exp = self.LEVEL_EXP.get(next_level)
            if required_exp is not None and user_level.current_exp >= required_exp:
                user_level.current_level = next_level
                leveled_up = True
            else:
                break

        db.commit()

        # 检查是否有新徽章解锁
        new_badges = self.check_and_unlock_badges(db, user_id)

        return {
            "added": exp_gained,
            "old_level": old_level,
            "new_level": user_level.current_level,
            "level_up": leveled_up,
            "new_badges": [
                {"id": b.id, "name": b.name, "badge_code": b.badge_code}
                for b in new_badges
            ],
        }

    def get_exp_records(
        self,
        db: Session,
        user_id: int,
        limit: int = 20,
    ) -> List[ExpRecord]:
        """获取经验获取记录"""
        return db.query(ExpRecord).filter(
            ExpRecord.user_id == user_id
        ).order_by(desc(ExpRecord.created_at)).limit(limit).all()

    # ============ 成长任务 ============

    def get_user_tasks(
        self,
        db: Session,
        user_id: int,
        include_completed: bool = False,
    ) -> List[GrowthTask]:
        """获取用户成长任务"""
        query = db.query(GrowthTask).filter(GrowthTask.user_id == user_id)

        if not include_completed:
            query = query.filter(GrowthTask.is_completed == False)

        return query.order_by(GrowthTask.created_at.desc()).all()

    def complete_task(
        self,
        db: Session,
        user_id: int,
        task_id: int,
    ) -> Optional[Dict[str, Any]]:
        """完成任务并领取奖励"""
        task = db.query(GrowthTask).filter(
            and_(
                GrowthTask.id == task_id,
                GrowthTask.user_id == user_id,
            )
        ).first()

        if not task:
            return None

        if task.is_completed and task.is_rewarded:
            return {"task": task, "already_rewarded": True}

        task.is_completed = True
        task.is_rewarded = True
        task.completed_at = datetime.now()

        # 发放奖励
        reward_result = None
        if task.reward_exp > 0:
            reward_result = self.add_exp(
                db, user_id, "task_complete", task.id,
                f"完成任务: {task.title}"
            )

        db.commit()

        return {
            "task": task,
            "reward_exp": task.reward_exp,
            "reward_badge_id": task.reward_badge_id,
            "result": reward_result,
        }


# 全局实例
_growth_service: Optional[GrowthService] = None


def get_growth_service() -> GrowthService:
    """获取成长服务实例"""
    global _growth_service
    if _growth_service is None:
        _growth_service = GrowthService()
    return _growth_service
