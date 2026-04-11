"""
user_memory_service 单元测试
"""
import pytest
from sqlalchemy.orm import Session
import json

from app.services.user_memory_service import UserMemoryService
from app.models.user import User


class TestUserMemoryServiceLongTerm:
    """用户长期记忆服务测试"""

    def test_add_memory(self, db_session):
        """添加用户记忆"""
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()

        service = UserMemoryService()
        memory = service.add_memory(
            db_session,
            user_id=1,
            memory_type="preference",
            content="用户害怕高处",
            importance=4,
            keywords="恐惧,高处"
        )

        assert memory is not None
        assert memory.user_id == 1
        assert memory.content == "用户害怕高处"
        assert memory.memory_type == "preference"
        assert memory.importance == 4
        assert memory.keywords == "恐惧,高处"

    def test_get_memory(self, db_session):
        """获取记忆详情"""
        user = User(id=1, phone="13900000001", password_hash="hash", is_active=True)
        db_session.add(user)
        db_session.commit()

        service = UserMemoryService()
        created = service.add_memory(db_session, 1, "note", "详情测试", 3)
        db_session.commit()

        memory = service.get_memory(db_session, 1, created.id)
        assert memory is not None
        assert memory.id == created.id
        assert memory.content == "详情测试"

    def test_get_memory_wrong_user(self, db_session):
        """获取其他用户的记忆返回None"""
        user1 = User(id=1, phone="13900000001", password_hash="hash", is_active=True)
        user2 = User(id=2, phone="13900000002", password_hash="hash", is_active=True)
        db_session.add(user1)
        db_session.add(user2)
        db_session.commit()

        service = UserMemoryService()
        created = service.add_memory(db_session, 1, "note", "用户1的记忆", 3)
        db_session.commit()

        memory = service.get_memory(db_session, 2, created.id)
        assert memory is None

    def test_get_memory_deleted(self, db_session):
        """获取已删除记忆返回None"""
        user = User(id=1, phone="13900000001", password_hash="hash", is_active=True)
        db_session.add(user)
        db_session.commit()

        service = UserMemoryService()
        created = service.add_memory(db_session, 1, "note", "测试", 3)
        db_session.commit()

        service.delete_memory(db_session, 1, created.id)
        memory = service.get_memory(db_session, 1, created.id)
        assert memory is None

    def test_list_memories(self, db_session):
        """列出用户记忆"""
        user = User(id=1, phone="13900000001", password_hash="hash", is_active=True)
        db_session.add(user)
        db_session.commit()

        service = UserMemoryService()
        service.add_memory(db_session, 1, "preference", "喜欢绿茶", 3, keywords="偏好,茶")
        service.add_memory(db_session, 1, "fear", "害怕黑暗", 4, keywords="恐惧,黑暗")
        service.add_memory(db_session, 1, "preference", "不喝咖啡", 3, keywords="偏好,咖啡")

        memories, total = service.list_memories(db_session, 1)
        assert len(memories) == 3
        assert total == 3

    def test_list_memories_filter_by_type(self, db_session):
        """按类型过滤记忆"""
        user = User(id=1, phone="13900000001", password_hash="hash", is_active=True)
        db_session.add(user)
        db_session.commit()

        service = UserMemoryService()
        service.add_memory(db_session, 1, "preference", "喜欢绿茶", 3)
        service.add_memory(db_session, 1, "fear", "害怕黑暗", 4)
        service.add_memory(db_session, 1, "preference", "不喝咖啡", 3)

        memories, total = service.list_memories(db_session, 1, memory_type="preference")
        assert len(memories) == 2
        assert total == 2
        assert all(m.memory_type == "preference" for m in memories)

    def test_list_memories_filter_by_importance(self, db_session):
        """按重要性过滤记忆"""
        user = User(id=1, phone="13900000001", password_hash="hash", is_active=True)
        db_session.add(user)
        db_session.commit()

        service = UserMemoryService()
        service.add_memory(db_session, 1, "note", "低重要性", 2)
        service.add_memory(db_session, 1, "important", "高重要性", 4)
        service.add_memory(db_session, 1, "normal", "中重要性", 3)

        memories, total = service.list_memories(db_session, 1, min_importance=4)
        assert len(memories) == 1
        assert memories[0].importance == 4

    def test_list_memories_pagination(self, db_session):
        """分页列出记忆"""
        user = User(id=1, phone="13900000001", password_hash="hash", is_active=True)
        db_session.add(user)
        db_session.commit()

        service = UserMemoryService()
        for i in range(25):
            service.add_memory(db_session, 1, "note", f"笔记{i}", 2)

        page1, total1 = service.list_memories(db_session, 1, page=1, page_size=10)
        page2, total2 = service.list_memories(db_session, 1, page=3, page_size=10)
        assert len(page1) == 10
        assert len(page2) == 5
        assert total1 == 25

    def test_update_memory(self, db_session):
        """更新记忆"""
        user = User(id=1, phone="13900000001", password_hash="hash", is_active=True)
        db_session.add(user)
        db_session.commit()

        service = UserMemoryService()
        created = service.add_memory(db_session, 1, "note", "原内容", 2)
        db_session.commit()

        updated = service.update_memory(
            db_session,
            1,
            created.id,
            {"content": "更新后的内容", "memory_type": "preference", "importance": 4}
        )

        assert updated is not None
        assert updated.content == "更新后的内容"
        assert updated.memory_type == "preference"
        assert updated.importance == 4

    def test_update_memory_not_found(self, db_session):
        """更新不存在的记忆返回None"""
        user = User(id=1, phone="13900000001", password_hash="hash", is_active=True)
        db_session.add(user)
        db_session.commit()

        service = UserMemoryService()
        updated = service.update_memory(db_session, 1, 99999, {"content": "测试"})
        assert updated is None

    def test_delete_memory(self, db_session):
        """删除记忆"""
        user = User(id=1, phone="13900000001", password_hash="hash", is_active=True)
        db_session.add(user)
        db_session.commit()

        service = UserMemoryService()
        created = service.add_memory(db_session, 1, "note", "要删除", 2)
        db_session.commit()

        result = service.delete_memory(db_session, 1, created.id)
        assert result is True

        # 验证已删除
        deleted = service.get_memory(db_session, 1, created.id)
        assert deleted is None

    def test_delete_memory_not_found(self, db_session):
        """删除不存在的记忆返回False"""
        service = UserMemoryService()
        result = service.delete_memory(db_session, 1, 99999)
        assert result is False

    def test_search_memories(self, db_session):
        """搜索记忆"""
        user = User(id=1, phone="13900000001", password_hash="hash", is_active=True)
        db_session.add(user)
        db_session.commit()

        service = UserMemoryService()
        service.add_memory(db_session, 1, "preference", "我喜欢喝咖啡", 3, keywords="咖啡,喜欢")
        service.add_memory(db_session, 1, "preference", "我不喜欢喝茶", 3, keywords="茶,不喜欢")
        service.add_memory(db_session, 1, "fear", "害怕黑暗", 4, keywords="恐惧,黑暗")

        results = service.search_memories(db_session, 1, "喜欢")
        assert len(results) == 1
        assert "喜欢喝咖啡" in results[0].content

    def test_search_memories_by_keywords(self, db_session):
        """按关键词搜索"""
        user = User(id=1, phone="13900000001", password_hash="hash", is_active=True)
        db_session.add(user)
        db_session.commit()

        service = UserMemoryService()
        service.add_memory(db_session, 1, "preference", "我喜欢咖啡", 3, keywords="咖啡,喜欢")
        service.add_memory(db_session, 1, "preference", "我喜欢绿茶", 3, keywords="绿茶,喜欢")

        results = service.search_memories(db_session, 1, "咖啡")
        assert len(results) == 1
        assert "咖啡" in results[0].keywords

    def test_get_relevant_memories(self, db_session):
        """根据上下文获取相关记忆"""
        user = User(id=1, phone="13900000001", password_hash="hash", is_active=True)
        db_session.add(user)
        db_session.commit()

        service = UserMemoryService()
        service.add_memory(db_session, 1, "preference", "我喜欢喝咖啡", 3, keywords="咖啡")
        service.add_memory(db_session, 1, "preference", "我害怕黑暗", 4, keywords="恐惧,黑暗")
        service.add_memory(db_session, 1, "preference", "我喜欢绿茶", 3, keywords="绿茶")

        # 当前对话上下文提到咖啡，应该返回咖啡相关记忆
        relevant = service.get_relevant_memories(db_session, 1, "今天想喝咖啡")
        assert len(relevant) > 0
        # 咖啡记忆应该排在前面
        assert any("咖啡" in mem.content for mem in relevant[:2])

    def test_get_formatted_memories_for_prompt(self, db_session):
        """格式化记忆用于prompt"""
        user = User(id=1, phone="13900000001", password_hash="hash", is_active=True)
        db_session.add(user)
        db_session.commit()

        service = UserMemoryService()
        service.add_memory(db_session, 1, "preference", "喜欢绿茶", 4, keywords="绿茶")
        service.add_memory(db_session, 1, "preference", "不喜欢咖啡", 3, keywords="咖啡")

        formatted = service.get_formatted_memories_for_prompt(db_session, 1, "今天喝咖啡吗")
        assert "关于用户的重要信息" in formatted
        assert "喜欢绿茶" in formatted
        assert "不喜欢咖啡" in formatted

    def test_get_formatted_memories_empty(self, db_session):
        """没有记忆返回空字符串"""
        user = User(id=1, phone="13900000001", password_hash="hash", is_active=True)
        db_session.add(user)
        db_session.commit()

        service = UserMemoryService()
        formatted = service.get_formatted_memories_for_prompt(db_session, 1, "测试")
        assert formatted == ""

    def test_get_statistics(self, db_session):
        """获取记忆统计"""
        user = User(id=1, phone="13900000001", password_hash="hash", is_active=True)
        db_session.add(user)
        db_session.commit()

        service = UserMemoryService()
        service.add_memory(db_session, 1, "preference", "喜欢绿茶", 3)
        service.add_memory(db_session, 1, "preference", "不喜欢咖啡", 3)
        service.add_memory(db_session, 1, "fear", "害怕黑暗", 4)

        stats = service.get_statistics(db_session, 1)
        assert stats["total_count"] == 3
        assert stats["by_type"]["preference"] == 2
        assert stats["by_type"]["fear"] == 1
        assert stats["by_importance"][3] == 2
        assert stats["by_importance"][4] == 1


class TestUserMemoryServiceInsights:
    """用户记忆洞察测试"""

    def test_add_insight(self, db_session):
        """添加记忆洞察"""
        user = User(id=1, phone="13900000001", password_hash="hash", is_active=True)
        db_session.add(user)
        db_session.commit()

        service = UserMemoryService()
        insight = service.add_insight(
            db_session, 1, "personality", "用户偏向内向，喜欢独处", [1, 2, 3], 0.8
        )

        assert insight is not None
        assert insight.user_id == 1
        assert insight.insight_type == "personality"
        assert "内向" in insight.insight_content

    def test_list_insights(self, db_session):
        """列出用户洞察"""
        user = User(id=1, phone="13900000001", password_hash="hash", is_active=True)
        db_session.add(user)
        db_session.commit()

        service = UserMemoryService()
        service.add_insight(db_session, 1, "personality", "性格内向", [], 0.8)
        service.add_insight(db_session, 1, "preference", "喜欢咖啡", [], 0.9)
        service.add_insight(db_session, 1, "personality", "敏感细腻", [], 0.7)

        all_insights = service.list_insights(db_session, 1)
        assert len(all_insights) == 3

        personality_insights = service.list_insights(db_session, 1, "personality")
        assert len(personality_insights) == 2


class TestUserMemoryServicePreferences:
    """用户偏好设置测试"""

    def test_set_preference_string(self, db_session):
        """设置字符串偏好"""
        user = User(id=1, phone="13900000001", password_hash="hash", is_active=True)
        db_session.add(user)
        db_session.commit()

        service = UserMemoryService()
        pref = service.set_preference(db_session, 1, "chat", "theme", "dark")

        assert pref is not None
        assert pref.value_type == "string"
        assert pref.value == "dark"

        # 获取验证
        value = service.get_preference(db_session, 1, "chat", "theme")
        assert value == "dark"

    def test_set_preference_boolean(self, db_session):
        """设置布尔偏好"""
        user = User(id=1, phone="13900000001", password_hash="hash", is_active=True)
        db_session.add(user)
        db_session.commit()

        service = UserMemoryService()
        service.set_preference(db_session, 1, "notifications", "enable", True)
        value = service.get_preference(db_session, 1, "notifications", "enable")
        assert value is True

    def test_set_preference_number(self, db_session):
        """设置数字偏好"""
        user = User(id=1, phone="13900000001", password_hash="hash", is_active=True)
        db_session.add(user)
        db_session.commit()

        service = UserMemoryService()
        service.set_preference(db_session, 1, "font", "size", 16)
        value = service.get_preference(db_session, 1, "font", "size")
        assert value == 16
        assert isinstance(value, int)

    def test_set_preference_json(self, db_session):
        """设置JSON偏好"""
        user = User(id=1, phone="13900000001", password_hash="hash", is_active=True)
        db_session.add(user)
        db_session.commit()

        service = UserMemoryService()
        data = {"morning": "coffee", "afternoon": "tea"}
        service.set_preference(db_session, 1, "drinks", "preferences", data)
        value = service.get_preference(db_session, 1, "drinks", "preferences")
        assert value == data
        assert value["morning"] == "coffee"

    def test_update_preference(self, db_session):
        """更新已有偏好"""
        user = User(id=1, phone="13900000001", password_hash="hash", is_active=True)
        db_session.add(user)
        db_session.commit()

        service = UserMemoryService()
        service.set_preference(db_session, 1, "theme", "color", "light")
        service.set_preference(db_session, 1, "theme", "color", "dark")

        value = service.get_preference(db_session, 1, "theme", "color")
        assert value == "dark"

    def test_get_preference_default(self, db_session):
        """获取不存在偏好返回默认值"""
        user = User(id=1, phone="13900000001", password_hash="hash", is_active=True)
        db_session.add(user)
        db_session.commit()

        service = UserMemoryService()
        value = service.get_preference(db_session, 1, "not_exists", "key", "default")
        assert value == "default"

    def test_get_category_preferences(self, db_session):
        """获取分类下所有偏好"""
        user = User(id=1, phone="13900000001", password_hash="hash", is_active=True)
        db_session.add(user)
        db_session.commit()

        service = UserMemoryService()
        service.set_preference(db_session, 1, "ui", "theme", "dark")
        service.set_preference(db_session, 1, "ui", "font_size", 16)
        service.set_preference(db_session, 1, "ui", "notifications", True)

        prefs = service.get_category_preferences(db_session, 1, "ui")
        assert prefs["theme"] == "dark"
        assert prefs["font_size"] == 16
        assert prefs["notifications"] is True
        assert len(prefs) == 3

    def test_delete_preference(self, db_session):
        """删除偏好"""
        user = User(id=1, phone="13900000001", password_hash="hash", is_active=True)
        db_session.add(user)
        db_session.commit()

        service = UserMemoryService()
        service.set_preference(db_session, 1, "theme", "color", "dark")
        result = service.delete_preference(db_session, 1, "theme", "color")
        assert result is True

        value = service.get_preference(db_session, 1, "theme", "color", None)
        assert value is None

    def test_delete_preference_not_found(self, db_session):
        """删除不存在偏好返回False"""
        user = User(id=1, phone="13900000001", password_hash="hash", is_active=True)
        db_session.add(user)
        db_session.commit()

        service = UserMemoryService()
        result = service.delete_preference(db_session, 1, "category", "key")
        assert result is False
