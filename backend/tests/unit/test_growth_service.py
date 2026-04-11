"""
growth_service 单元测试 - 用户成长体系
"""
import pytest
from sqlalchemy.orm import Session

from app.services.growth_service import GrowthService
from app.models.growth import GrowthTask, UserLevel, Badge, UserBadge, BadgeRarity
from app.models.user import User
from app.models.chat import Conversation
from app.models.diary import EmotionDiary


class TestGrowthServiceBadges:
    """GrowthService 徽章管理测试"""

    def test_init_default_badges(self, db_session):
        """初始化默认徽章数据"""
        service = GrowthService()
        service.init_default_badges(db_session)
        
        # 检查默认徽章是否创建
        badges = db_session.query(Badge).filter(Badge.is_active == True).all()
        assert len(badges) >= 8  # 默认有8个徽章

    def test_get_all_badges(self, db_session):
        """获取所有徽章"""
        service = GrowthService()
        service.init_default_badges(db_session)
        
        badges = service.get_all_badges(db_session)
        assert len(badges) > 0
        assert all(b.is_active for b in badges)

    def test_get_user_badges_empty(self, db_session):
        """新用户没有徽章"""
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()

        service = GrowthService()
        service.init_default_badges(db_session)
        result = service.get_user_badges(db_session, 1)
        
        assert len(result) == 0

    def test_get_badge_progress(self, db_session):
        """获取徽章解锁进度"""
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()

        service = GrowthService()
        service.init_default_badges(db_session)
        progress = service.get_badge_progress(db_session, 1)
        
        assert "total" in progress
        assert "unlocked_count" in progress
        assert "unlocked" in progress
        assert "locked" in progress
        assert progress["unlocked_count"] == 0

    def test_check_and_unlock_first_chat(self, db_session):
        """满足条件自动解锁徽章 - 第一次对话"""
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        # 创建一个对话
        conv = Conversation(user_id=1, session_id="test", assistant_id=1)
        db_session.add(conv)
        db_session.commit()

        service = GrowthService()
        service.init_default_badges(db_session)
        
        newly_unlocked = service.check_and_unlock_badges(db_session, 1)
        # 应该解锁 first_chat
        assert len(newly_unlocked) >= 1
        unlocked_codes = [b.badge_code for b in newly_unlocked]
        assert "first_chat" in unlocked_codes

    def test_check_and_unlock_first_diary(self, db_session):
        """满足条件自动解锁徽章 - 第一篇日记"""
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        # 创建一篇日记
        diary = EmotionDiary(
            user_id=1,
            date="2024-01-01",
            content="test",
            mood_score=5,
            is_deleted=False,
        )
        db_session.add(diary)
        db_session.commit()

        service = GrowthService()
        service.init_default_badges(db_session)
        
        newly_unlocked = service.check_and_unlock_badges(db_session, 1)
        # 应该解锁 first_diary
        assert len(newly_unlocked) >= 1
        unlocked_codes = [b.badge_code for b in newly_unlocked]
        assert "first_diary" in unlocked_codes

    def test_check_and_unlock_vip_badge(self, db_session):
        """VIP用户解锁VIP徽章"""
        from app.models.member import MemberLevel
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
            member_level=MemberLevel.VIP,
        )
        db_session.add(user)
        db_session.commit()

        service = GrowthService()
        service.init_default_badges(db_session)
        
        newly_unlocked = service.check_and_unlock_badges(db_session, 1)
        unlocked_codes = [b.badge_code for b in newly_unlocked]
        assert "vip_member" in unlocked_codes

    def test_set_badge_display(self, db_session):
        """设置徽章是否展示"""
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        badge = Badge(
            badge_code="test",
            name="测试徽章",
            description="测试",
            rarity=BadgeRarity.COMMON.value,
            is_active=True,
        )
        db_session.add(badge)
        db_session.commit()

        service = GrowthService()
        # 让用户获得徽章
        service.check_and_unlock_badges(db_session, 1)
        # 添加用户徽章
        user_badge = UserBadge(user_id=1, badge_id=badge.id, is_displayed=False)
        db_session.add(user_badge)
        db_session.commit()

        result = service.set_badge_display(db_session, 1, badge.id, True, "我的备注")
        assert result is True
        
        # 验证更新
        updated = db_session.query(UserBadge).filter(
            UserBadge.user_id == 1, UserBadge.badge_id == badge.id
        ).first()
        assert updated.is_displayed is True
        assert updated.display_note == "我的备注"

    def test_set_badge_display_not_found(self, db_session):
        """设置不存在的徽章返回False"""
        service = GrowthService()
        result = service.set_badge_display(db_session, 1, 99999, True)
        assert result is False


class TestGrowthServiceLevelExp:
    """GrowthService 等级经验测试"""

    def test_get_or_create_user_level_new(self, db_session):
        """新用户创建等级信息"""
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()

        service = GrowthService()
        user_level = service.get_or_create_user_level(db_session, 1)
        
        assert user_level is not None
        assert user_level.current_level == 1
        assert user_level.current_exp == 0

    def test_get_user_level_info_new(self, db_session):
        """获取新用户等级信息"""
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()

        service = GrowthService()
        info = service.get_user_level_info(db_session, 1)
        
        assert info["current_level"] == 1
        assert info["current_exp"] == 0
        assert info["progress_percent"] == 0
        assert info["next_level"] == 2

    def test_add_exp_chat(self, db_session):
        """对话添加经验"""
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()

        service = GrowthService()
        result = service.add_exp(db_session, 1, "chat")
        
        assert result["added"] == 5
        assert result["level_up"] is False

    def test_add_exp_diary(self, db_session):
        """写日记添加经验"""
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()

        service = GrowthService()
        result = service.add_exp(db_session, 1, "diary")
        
        assert result["added"] == 10

    def test_add_exp_level_up_multiple(self, db_session):
        """一次性升多级"""
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()

        service = GrowthService()
        # 添加足够经验直接升几级
        result = service.add_exp(db_session, 1, "badge_unlock")  # 50经验
        
        assert result["added"] == 50
        # 从0开始，到50，需要100经验升2级，所以现在是1级50经验
        assert result["new_level"] == 1
        assert result["level_up"] is False

        # 再加60经验到110，就升到2级
        result2 = service.add_exp(db_session, 1, "chat")  # +5 = 115
        # 现在current_level = 2
        level_info = service.get_user_level_info(db_session, 1)
        assert level_info["current_level"] == 2

    def test_get_exp_records(self, db_session):
        """获取经验记录"""
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()

        service = GrowthService()
        # 添加几次经验
        service.add_exp(db_session, 1, "chat")
        service.add_exp(db_session, 1, "diary")
        service.add_exp(db_session, 1, "login_daily")
        
        records = service.get_exp_records(db_session, 1, limit=10)
        assert len(records) == 3

    def test_add_exp_unknown_action(self, db_session):
        """未知动作不添加经验"""
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()

        service = GrowthService()
        result = service.add_exp(db_session, 1, "unknown_action")
        
        assert result["added"] == 0
        assert result["level_up"] is False


class TestGrowthServiceTasks:
    """GrowthService 成长任务测试"""

    def test_get_user_tasks_empty(self, db_session):
        """用户没有任务返回空列表"""
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()

        service = GrowthService()
        tasks = service.get_user_tasks(db_session, 1)
        
        assert len(tasks) == 0

    def test_get_user_tasks_include_completed(self, db_session):
        """获取用户任务包含已完成"""
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        task1 = GrowthTask(user_id=1, title="任务1", is_completed=False, reward_exp=10)
        task2 = GrowthTask(user_id=1, title="任务2", is_completed=True, reward_exp=20)
        db_session.add_all([task1, task2])
        db_session.commit()

        service = GrowthService()
        tasks = service.get_user_tasks(db_session, 1, include_completed=True)
        assert len(tasks) == 2
        
        tasks_incomplete = service.get_user_tasks(db_session, 1, include_completed=False)
        assert len(tasks_incomplete) == 1

    def test_complete_task(self, db_session):
        """完成任务并获得奖励"""
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        task = GrowthTask(
            user_id=1,
            title="完成第一次对话",
            is_completed=False,
            is_rewarded=False,
            reward_exp=30,
        )
        db_session.add(task)
        db_session.commit()

        service = GrowthService()
        result = service.complete_task(db_session, 1, task.id)
        
        assert result is not None
        assert result["task"].is_completed is True
        assert result["task"].is_rewarded is True
        assert result["reward_exp"] == 30
        # 验证经验增加
        level_info = service.get_user_level_info(db_session, 1)
        assert level_info["current_exp"] == 30

    def test_complete_task_already_rewarded(self, db_session):
        """重复领取奖励"""
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        task = GrowthTask(
            user_id=1,
            title="已完成任务",
            is_completed=True,
            is_rewarded=True,
            reward_exp=10,
        )
        db_session.add(task)
        db_session.commit()

        service = GrowthService()
        result = service.complete_task(db_session, 1, task.id)
        
        assert result["already_rewarded"] is True

    def test_complete_task_not_found(self, db_session):
        """完成不存在的任务返回None"""
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()

        service = GrowthService()
        result = service.complete_task(db_session, 1, 99999)
        
        assert result is None
