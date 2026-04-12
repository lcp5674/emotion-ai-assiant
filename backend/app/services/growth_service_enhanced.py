"""
成长与激励增强模块 - 增强服务
实现丰富成长体系、多样化激励机制
"""
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func, or_
import loguru
import random

from app.models import UserLevel, ExpRecord
from app.models.growth import BadgeRarity
from app.models.growth_models_enhanced import (
    GrowthDimension,
    TitleTier,
    BadgeTimeType,
    UserGrowthDimension,
    ExpertTitle,
    UserTitle,
    EnhancedBadge,
    UserEnhancedBadge,
    LoginStreak,
    SpecialAnniversary,
    UserAnniversary,
)
from app.services.growth_service import get_growth_service


class GrowthServiceEnhanced:
    """成长服务增强版"""

    # 扩展等级配置 - 更多等级
    EXTENDED_LEVEL_EXP = {
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
        21: 21000,
        22: 23200,
        23: 25500,
        24: 27900,
        25: 30400,
        26: 33000,
        27: 35700,
        28: 38500,
        29: 41400,
        30: 44400,
        31: 47500,
        32: 50700,
        33: 54000,
        34: 57400,
        35: 60900,
        36: 64500,
        37: 68200,
        38: 72000,
        39: 75900,
        40: 80000,
        41: 84200,
        42: 88500,
        43: 92900,
        44: 97400,
        45: 102000,
        46: 106700,
        47: 111500,
        48: 116400,
        49: 121400,
        50: 126500,
    }

    # 维度等级经验配置
    DIMENSION_LEVEL_EXP = {
        1: 0,
        2: 50,
        3: 150,
        4: 300,
        5: 500,
        6: 750,
        7: 1050,
        8: 1400,
        9: 1800,
        10: 2250,
    }

    # 连续打卡奖励倍增配置
    STREAK_MULTIPLIERS = {
        1: 1.0,
        3: 1.5,
        7: 2.0,
        14: 2.5,
        30: 3.0,
        60: 3.5,
        90: 4.0,
        180: 5.0,
        365: 10.0,
    }

    # 默认专家称号数据
    DEFAULT_TITLES = [
        {
            "title_code": "emotional_novice",
            "name": "情感探索者",
            "description": "开始探索内心世界的旅程",
            "tier": TitleTier.NOVICE.value,
            "dimension": GrowthDimension.EMOTIONAL_HEALTH.value,
            "required_level": 1,
            "required_score": 10.0,
            "required_badges": [],
        },
        {
            "title_code": "emotional_apprentice",
            "name": "情绪觉察者",
            "description": "能够识别和理解自己的情绪",
            "tier": TitleTier.APPRENTICE.value,
            "dimension": GrowthDimension.EMOTIONAL_HEALTH.value,
            "required_level": 3,
            "required_score": 30.0,
            "required_badges": [],
        },
        {
            "title_code": "emotional_expert",
            "name": "情绪管理大师",
            "description": "精通情绪调节和管理技巧",
            "tier": TitleTier.EXPERT.value,
            "dimension": GrowthDimension.EMOTIONAL_HEALTH.value,
            "required_level": 5,
            "required_score": 60.0,
            "required_badges": [],
        },
        {
            "title_code": "self_aware_novice",
            "name": "自我发现者",
            "description": "开始认识真实的自己",
            "tier": TitleTier.NOVICE.value,
            "dimension": GrowthDimension.SELF_AWARENESS.value,
            "required_level": 1,
            "required_score": 10.0,
            "required_badges": [],
        },
        {
            "title_code": "social_novice",
            "name": "社交探索者",
            "description": "开始建立健康的社交关系",
            "tier": TitleTier.NOVICE.value,
            "dimension": GrowthDimension.SOCIAL_SKILLS.value,
            "required_level": 1,
            "required_score": 10.0,
            "required_badges": [],
        },
        {
            "title_code": "resilient_novice",
            "name": "坚韧初学者",
            "description": "在困难中学习成长",
            "tier": TitleTier.NOVICE.value,
            "dimension": GrowthDimension.RESILIENCE.value,
            "required_level": 1,
            "required_score": 10.0,
            "required_badges": [],
        },
    ]

    # 增强徽章数据（稀有徽章、限定成就）
    DEFAULT_ENHANCED_BADGES = [
        {
            "badge_code": "first_100_days",
            "name": "百日坚持",
            "description": "连续100天不放弃",
            "rarity": "epic",
            "time_type": BadgeTimeType.NONE.value,
            "category": "坚持",
            "condition_type": "login_streak",
            "condition_value": 100,
            "is_limited": False,
        },
        {
            "badge_code": "spring_2025",
            "name": "春日探索者",
            "description": "2025年春季限定徽章",
            "rarity": "rare",
            "time_type": BadgeTimeType.SEASONAL.value,
            "time_value": "spring_2025",
            "category": "季节限定",
            "condition_type": "seasonal_activity",
            "condition_value": 1,
            "is_limited": True,
        },
        {
            "badge_code": "new_year_2026",
            "name": "新年先锋",
            "description": "2026新年限定徽章",
            "rarity": "legendary",
            "time_type": BadgeTimeType.HOLIDAY.value,
            "time_value": "new_year_2026",
            "category": "节日限定",
            "condition_type": "holiday_login",
            "condition_value": 1,
            "is_limited": True,
            "max_holders": 1000,
        },
        {
            "badge_code": "first_anniversary",
            "name": "一路同行",
            "description": "陪伴一周年",
            "rarity": "legendary",
            "time_type": BadgeTimeType.ANNIVERSARY.value,
            "category": "周年纪念",
            "condition_type": "registration_days",
            "condition_value": 365,
            "is_limited": False,
        },
        {
            "badge_code": "perfect_month",
            "name": "完美月度",
            "description": "整月每天都打卡",
            "rarity": "epic",
            "time_type": BadgeTimeType.NONE.value,
            "category": "坚持",
            "condition_type": "perfect_month",
            "condition_value": 1,
            "is_limited": False,
        },
        {
            "badge_code": "early_bird",
            "name": "早起的鸟儿",
            "description": "连续30天在6点前打卡",
            "rarity": "rare",
            "time_type": BadgeTimeType.NONE.value,
            "category": "生活习惯",
            "condition_type": "early_login",
            "condition_value": 30,
            "is_limited": False,
        },
    ]

    # 默认纪念日数据
    DEFAULT_ANNIVERSARIES = [
        {
            "anniversary_code": "first_week",
            "name": "第一周",
            "description": "使用第一周纪念",
            "anniversary_type": "registration",
            "days_required": 7,
            "reward_exp": 100,
        },
        {
            "anniversary_code": "first_month",
            "name": "第一个月",
            "description": "使用一个月纪念",
            "anniversary_type": "registration",
            "days_required": 30,
            "reward_exp": 300,
        },
        {
            "anniversary_code": "first_100_days",
            "name": "百日纪念",
            "description": "使用100天纪念",
            "anniversary_type": "registration",
            "days_required": 100,
            "reward_exp": 500,
        },
        {
            "anniversary_code": "first_year",
            "name": "一周年",
            "description": "使用一周年纪念",
            "anniversary_type": "registration",
            "days_required": 365,
            "reward_exp": 2000,
        },
    ]

    def __init__(self):
        self.growth_service = get_growth_service()

    # ============ 初始化数据 ============

    def init_default_data(self, db: Session):
        """初始化所有默认数据"""
        self.init_default_titles(db)
        self.init_default_enhanced_badges(db)
        self.init_default_anniversaries(db)
        loguru.logger.info("增强成长体系默认数据初始化完成")

    def init_default_titles(self, db: Session):
        """初始化默认称号数据"""
        for title_data in self.DEFAULT_TITLES:
            existing = db.query(ExpertTitle).filter(ExpertTitle.title_code == title_data["title_code"]).first()
            if not existing:
                title = ExpertTitle(**title_data)
                db.add(title)
        db.commit()
        loguru.logger.info("默认称号数据初始化完成")

    def init_default_enhanced_badges(self, db: Session):
        """初始化默认增强徽章数据"""
        for badge_data in self.DEFAULT_ENHANCED_BADGES:
            existing = db.query(EnhancedBadge).filter(EnhancedBadge.badge_code == badge_data["badge_code"]).first()
            if not existing:
                badge = EnhancedBadge(**badge_data)
                db.add(badge)
        db.commit()
        loguru.logger.info("默认增强徽章数据初始化完成")

    def init_default_anniversaries(self, db: Session):
        """初始化默认纪念日数据"""
        for anniv_data in self.DEFAULT_ANNIVERSARIES:
            existing = db.query(SpecialAnniversary).filter(SpecialAnniversary.anniversary_code == anniv_data["anniversary_code"]).first()
            if not existing:
                anniv = SpecialAnniversary(**anniv_data)
                db.add(anniv)
        db.commit()
        loguru.logger.info("默认纪念日数据初始化完成")

    # ============ 多维度成长指标 ============

    def get_or_create_user_dimensions(self, db: Session, user_id: int) -> List[UserGrowthDimension]:
        """获取或创建用户的所有成长维度"""
        dimensions = []
        for dim in GrowthDimension:
            dimension = db.query(UserGrowthDimension).filter(
                and_(UserGrowthDimension.user_id == user_id, UserGrowthDimension.dimension == dim.value)
            ).first()
            if not dimension:
                dimension = UserGrowthDimension(
                    user_id=user_id,
                    dimension=dim.value,
                    level=1,
                    experience=0,
                    score=0.0,
                )
                db.add(dimension)
            dimensions.append(dimension)
        db.commit()
        return dimensions

    def add_dimension_exp(
        self,
        db: Session,
        user_id: int,
        dimension: str,
        exp: int,
        score_delta: Optional[float] = 0.0,
    ) -> Dict[str, Any]:
        """为特定维度添加经验和评分"""
        dim_obj = db.query(UserGrowthDimension).filter(
            and_(UserGrowthDimension.user_id == user_id, UserGrowthDimension.dimension == dimension)
        ).first()
        if not dim_obj:
            return {"added": 0, "level_up": False}
        
        old_level = dim_obj.level
        dim_obj.experience += exp
        dim_obj.score = min(100.0, max(0.0, dim_obj.score + score_delta))
        
        now = datetime.now()
        dim_obj.score_history.append({
            "date": now.isoformat(),
            "score": dim_obj.score,
        })
        
        leveled_up = False
        while True:
            next_level = dim_obj.level + 1
            required_exp = self.DIMENSION_LEVEL_EXP.get(next_level)
            if required_exp is not None and dim_obj.experience >= required_exp:
                dim_obj.level = next_level
                leveled_up = True
            else:
                break
        
        db.commit()
        
        new_titles = self.check_and_unlock_titles(db, user_id)
        
        return {
            "added": exp,
            "old_level": old_level,
            "new_level": dim_obj.level,
            "level_up": leveled_up,
            "new_titles": new_titles,
        }

    def get_user_dimensions(self, db: Session, user_id: int) -> List[UserGrowthDimension]:
        """获取用户的所有成长维度"""
        return db.query(UserGrowthDimension).filter(UserGrowthDimension.user_id == user_id).all()

    # ============ 专家称号系统 ============

    def get_all_titles(self, db: Session) -> List[ExpertTitle]:
        """获取所有称号"""
        return db.query(ExpertTitle).filter(ExpertTitle.is_active == True).all()

    def get_user_titles(self, db: Session, user_id: int) -> List[Dict[str, Any]]:
        """获取用户已获得的称号"""
        query = db.query(ExpertTitle, UserTitle).join(
            UserTitle,
            and_(
                UserTitle.title_id == ExpertTitle.id,
                UserTitle.user_id == user_id,
            )
        ).filter(ExpertTitle.is_active == True)

        result = []
        for title, user_title in query.all():
            result.append({
                "id": user_title.id,
                "title_id": title.id,
                "title": title,
                "obtained_at": user_title.obtained_at,
                "is_equipped": user_title.is_equipped,
            })
        return result

    def check_and_unlock_titles(self, db: Session, user_id: int) -> List[ExpertTitle]:
        """检查并解锁新称号"""
        existing_title_ids = [
            ut.title_id for ut in
            db.query(UserTitle).filter(UserTitle.user_id == user_id).all()
        ]

        candidates = db.query(ExpertTitle).filter(
            ExpertTitle.is_active == True,
            ~ExpertTitle.id.in_(existing_title_ids),
        ).all()

        newly_unlocked = []
        user_dimensions = {d.dimension: d for d in self.get_user_dimensions(db, user_id)}

        for title in candidates:
            dim_obj = user_dimensions.get(title.dimension)
            if not dim_obj:
                continue
                
            if (dim_obj.level >= title.required_level and 
                dim_obj.score >= title.required_score):
                user_title = UserTitle(
                    user_id=user_id,
                    title_id=title.id,
                    is_equipped=False,
                )
                db.add(user_title)
                newly_unlocked.append(title)
                loguru.logger.info(f"用户 {user_id} 解锁称号: {title.name}")

        if newly_unlocked:
            db.commit()

        return newly_unlocked

    def equip_title(
        self,
        db: Session,
        user_id: int,
        user_title_id: int,
        is_equipped: bool,
    ) -> bool:
        """装备或卸下称号"""
        user_title = db.query(UserTitle).filter(
            and_(UserTitle.user_id == user_id, UserTitle.id == user_title_id)
        ).first()
        if not user_title:
            return False

        if is_equipped:
            db.query(UserTitle).filter(
                and_(UserTitle.user_id == user_id, UserTitle.is_equipped == True)
            ).update({"is_equipped": False})

        user_title.is_equipped = is_equipped
        db.commit()
        return True

    # ============ 稀有徽章和限定成就 ============

    def get_all_enhanced_badges(self, db: Session) -> List[EnhancedBadge]:
        """获取所有增强徽章"""
        return db.query(EnhancedBadge).filter(EnhancedBadge.is_active == True).order_by(
            EnhancedBadge.rarity, EnhancedBadge.category
        ).all()

    def get_user_enhanced_badges(self, db: Session, user_id: int) -> List[Dict[str, Any]]:
        """获取用户已获得的增强徽章"""
        query = db.query(EnhancedBadge, UserEnhancedBadge).join(
            UserEnhancedBadge,
            and_(
                UserEnhancedBadge.badge_id == EnhancedBadge.id,
                UserEnhancedBadge.user_id == user_id,
            )
        ).filter(EnhancedBadge.is_active == True)

        result = []
        for badge, user_badge in query.all():
            result.append({
                "id": user_badge.id,
                "badge_id": badge.id,
                "badge": badge,
                "obtained_at": user_badge.obtained_at,
                "is_displayed": user_badge.is_displayed,
                "display_note": user_badge.display_note,
                "obtain_number": user_badge.obtain_number,
            })
        return result

    def check_and_unlock_enhanced_badges(self, db: Session, user_id: int) -> List[EnhancedBadge]:
        """检查并解锁新的增强徽章"""
        existing_badge_ids = [
            ub.badge_id for ub in
            db.query(UserEnhancedBadge).filter(UserEnhancedBadge.user_id == user_id).all()
        ]

        now = datetime.now()
        candidates = db.query(EnhancedBadge).filter(
            EnhancedBadge.is_active == True,
            ~EnhancedBadge.id.in_(existing_badge_ids),
            or_(
                EnhancedBadge.is_limited == False,
                and_(
                    EnhancedBadge.start_time <= now,
                    EnhancedBadge.end_time >= now,
                )
            )
        ).all()

        newly_unlocked = []

        for badge in candidates:
            if self._check_enhanced_badge_condition(db, user_id, badge):
                if badge.is_limited and badge.max_holders and badge.current_holders >= badge.max_holders:
                    continue

                user_badge = UserEnhancedBadge(
                    user_id=user_id,
                    badge_id=badge.id,
                    is_displayed=True,
                    obtain_number=badge.current_holders + 1 if badge.is_limited else None,
                )
                db.add(user_badge)
                
                if badge.is_limited:
                    badge.current_holders += 1

                newly_unlocked.append(badge)
                loguru.logger.info(f"用户 {user_id} 解锁增强徽章: {badge.name}")

        if newly_unlocked:
            db.commit()

        return newly_unlocked

    def _check_enhanced_badge_condition(self, db: Session, user_id: int, badge: EnhancedBadge) -> bool:
        """检查增强徽章解锁条件"""
        condition_type = badge.condition_type
        target = badge.condition_value

        if condition_type == "login_streak":
            streak = db.query(LoginStreak).filter(LoginStreak.user_id == user_id).first()
            return streak and streak.current_streak >= target

        elif condition_type == "registration_days":
            from app.models import User
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                days = (datetime.now() - user.created_at).days
                return days >= target
            return False

        return False

    def set_enhanced_badge_display(
        self,
        db: Session,
        user_id: int,
        user_badge_id: int,
        is_displayed: bool,
        display_note: Optional[str] = None,
    ) -> bool:
        """设置增强徽章展示"""
        user_badge = db.query(UserEnhancedBadge).filter(
            and_(
                UserEnhancedBadge.user_id == user_id,
                UserEnhancedBadge.id == user_badge_id,
            )
        ).first()
        if not user_badge:
            return False

        user_badge.is_displayed = is_displayed
        if display_note is not None:
            user_badge.display_note = display_note

        db.commit()
        return True

    # ============ 连续打卡奖励倍增 ============

    def get_or_create_login_streak(self, db: Session, user_id: int) -> LoginStreak:
        """获取或创建用户连续打卡记录"""
        streak = db.query(LoginStreak).filter(LoginStreak.user_id == user_id).first()
        if not streak:
            streak = LoginStreak(
                user_id=user_id,
                current_streak=0,
                max_streak=0,
                total_logins=0,
            )
            db.add(streak)
            db.commit()
            db.refresh(streak)
        return streak

    def record_login(self, db: Session, user_id: int) -> Dict[str, Any]:
        """记录登录，计算连续打卡，发放奖励"""
        streak = self.get_or_create_login_streak(db, user_id)
        now = datetime.now()
        today = now.date()

        yesterday = None
        if streak.last_login_date:
            yesterday = streak.last_login_date.date()

        if yesterday == today:
            return {
                "streak": streak,
                "bonus_exp": 0,
                "multiplier": 1.0,
                "new_badges": [],
                "new_titles": [],
                "anniversaries": [],
            }

        if yesterday and (today - yesterday).days == 1:
            streak.current_streak += 1
        else:
            streak.current_streak = 1

        streak.max_streak = max(streak.max_streak, streak.current_streak)
        streak.total_logins += 1
        streak.last_login_date = now

        multiplier = self._get_streak_multiplier(streak.current_streak)
        base_exp = 2
        bonus_exp = int(base_exp * multiplier)

        reward_result = self.growth_service.add_exp(
            db, user_id, "login_daily", None,
            f"连续打卡 x{multiplier}"
        )

        new_badges = self.check_and_unlock_enhanced_badges(db, user_id)
        new_titles = self.check_and_unlock_titles(db, user_id)
        anniversaries = self.check_and_award_anniversaries(db, user_id)

        db.commit()

        return {
            "streak": streak,
            "bonus_exp": bonus_exp,
            "multiplier": multiplier,
            "new_badges": [
                {"id": b.id, "name": b.name, "badge_code": b.badge_code}
                for b in new_badges
            ],
            "new_titles": [
                {"id": t.id, "name": t.name, "title_code": t.title_code}
                for t in new_titles
            ],
            "anniversaries": anniversaries,
        }

    def _get_streak_multiplier(self, streak_days: int) -> float:
        """获取连续打卡倍数"""
        multiplier = 1.0
        for days, mult in sorted(self.STREAK_MULTIPLIERS.items()):
            if streak_days >= days:
                multiplier = mult
        return multiplier

    # ============ 特殊纪念日奖励 ============

    def get_all_anniversaries(self, db: Session) -> List[SpecialAnniversary]:
        """获取所有纪念日"""
        return db.query(SpecialAnniversary).filter(SpecialAnniversary.is_active == True).all()

    def check_and_award_anniversaries(self, db: Session, user_id: int) -> List[Dict[str, Any]]:
        """检查并发放纪念日奖励"""
        from app.models import User
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return []

        days_since_registration = (datetime.now() - user.created_at).days

        existing_anniv_ids = [
            ua.anniversary_id for ua in
            db.query(UserAnniversary).filter(UserAnniversary.user_id == user_id).all()
        ]

        candidates = db.query(SpecialAnniversary).filter(
            SpecialAnniversary.is_active == True,
            ~SpecialAnniversary.id.in_(existing_anniv_ids),
        ).all()

        awarded = []

        for anniv in candidates:
            if anniv.anniversary_type == "registration":
                if anniv.days_required and days_since_registration >= anniv.days_required:
                    user_anniv = UserAnniversary(
                        user_id=user_id,
                        anniversary_id=anniv.id,
                        is_rewarded=False,
                    )
                    db.add(user_anniv)

                    if anniv.reward_exp > 0:
                        self.growth_service.add_exp(
                            db, user_id, "anniversary", anniv.id,
                            f"纪念日奖励: {anniv.name}"
                        )

                    user_anniv.is_rewarded = True

                    awarded.append({
                        "id": anniv.id,
                        "name": anniv.name,
                        "reward_exp": anniv.reward_exp,
                    })
                    loguru.logger.info(f"用户 {user_id} 获得纪念日: {anniv.name}")

        if awarded:
            db.commit()

        return awarded

    def get_user_anniversaries(self, db: Session, user_id: int) -> List[Dict[str, Any]]:
        """获取用户纪念日记录"""
        query = db.query(SpecialAnniversary, UserAnniversary).join(
            UserAnniversary,
            and_(
                UserAnniversary.anniversary_id == SpecialAnniversary.id,
                UserAnniversary.user_id == user_id,
            )
        )

        result = []
        for anniv, user_anniv in query.all():
            result.append({
                "id": user_anniv.id,
                "anniversary_id": anniv.id,
                "anniversary": anniv,
                "achieved_at": user_anniv.achieved_at,
                "is_rewarded": user_anniv.is_rewarded,
            })
        return result

    # ============ 综合成长概览 ============

    def get_growth_overview(self, db: Session, user_id: int) -> Dict[str, Any]:
        """获取完整的成长体系概览"""
        self.get_or_create_user_dimensions(db, user_id)
        
        level_info = self.growth_service.get_user_level_info(db, user_id)
        dimensions = self.get_user_dimensions(db, user_id)
        titles = self.get_user_titles(db, user_id)
        streak = self.get_or_create_login_streak(db, user_id)
        anniversaries = self.get_user_anniversaries(db, user_id)
        
        all_badges = self.get_all_enhanced_badges(db)
        user_badge_ids = [
            ub.badge_id for ub in
            db.query(UserEnhancedBadge).filter(UserEnhancedBadge.user_id == user_id).all()
        ]
        
        return {
            "level_info": level_info,
            "dimensions": dimensions,
            "titles": titles,
            "badges": {
                "total": len(all_badges),
                "unlocked_count": len(user_badge_ids),
            },
            "streak": streak,
            "anniversaries": anniversaries,
            "smart_tasks": [],
        }


_growth_service_enhanced: Optional[GrowthServiceEnhanced] = None


def get_growth_service_enhanced() -> GrowthServiceEnhanced:
    """获取增强成长服务实例"""
    global _growth_service_enhanced
    if _growth_service_enhanced is None:
        _growth_service_enhanced = GrowthServiceEnhanced()
    return _growth_service_enhanced
