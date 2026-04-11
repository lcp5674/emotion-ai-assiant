"""
diary_service 单元测试
"""
import pytest
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta

from app.services.diary_service import DiaryService
from app.models.diary import EmotionDiary, EmotionType, MoodLevel
from app.models.user import User
from app.schemas.diary import DiaryCreate, DiaryUpdate


class TestDiaryService:
    """DiaryService单元测试"""

    def test_list_diaries(self, db_session):
        """获取用户日记列表"""
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        for i in range(5):
            diary = EmotionDiary(
                user_id=1,
                date=date.today() - timedelta(days=i),
                content=f"日记{i} 内容{i}",
                mood_score=8 - i,
                is_deleted=False,
            )
            db_session.add(diary)
        db_session.commit()

        service = DiaryService()
        diaries, total = service.list_diaries(db_session, 1)
        
        assert len(diaries) == 5
        assert total == 5

    def test_list_diaries_pagination(self, db_session):
        """分页获取用户日记"""
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        for i in range(25):
            diary = EmotionDiary(
                user_id=1,
                date=date.today() - timedelta(days=i),
                content=f"日记{i} 内容{i}",
                mood_score=i % 10,
                is_deleted=False,
            )
            db_session.add(diary)
        db_session.commit()

        service = DiaryService()
        page1, total1 = service.list_diaries(db_session, 1, page=1, page_size=10)
        page2, total2 = service.list_diaries(db_session, 1, page=3, page_size=10)
        
        assert len(page1) == 10
        assert len(page2) == 5
        assert total1 == 25
        assert total2 == 25

    def test_get_diary_exists(self, db_session):
        """获取存在的日记"""
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        diary = EmotionDiary(
            user_id=1,
            date=date.today(),
            content="测试日记 测试内容",
            mood_score=7,
            is_deleted=False,
        )
        db_session.add(diary)
        db_session.commit()

        service = DiaryService()
        result = service.get_diary(db_session, 1, diary.id)
        
        assert result is not None
        assert result.content == "测试日记 测试内容"
        assert result.mood_score == 7

    def test_get_diary_not_exists(self, db_session):
        """获取不存在的日记返回None"""
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()

        service = DiaryService()
        result = service.get_diary(db_session, 1, 99999)
        
        assert result is None

    def test_get_diary_deleted(self, db_session):
        """获取已删除日记返回None"""
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        diary = EmotionDiary(
            user_id=1,
            date=date.today(),
            content="已删除内容",
            mood_score=5,
            is_deleted=True,
        )
        db_session.add(diary)
        db_session.commit()

        service = DiaryService()
        result = service.get_diary(db_session, 1, diary.id)
        
        assert result is None

    def test_get_diary_wrong_user(self, db_session):
        """获取其他用户的日记返回None"""
        user1 = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        user2 = User(
            id=2,
            phone="13900000002",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user1)
        db_session.add(user2)
        diary = EmotionDiary(
            user_id=1,
            date=date.today(),
            content="用户1的日记内容",
            mood_score=7,
            is_deleted=False,
        )
        db_session.add(diary)
        db_session.commit()

        service = DiaryService()
        result = service.get_diary(db_session, 2, diary.id)
        
        assert result is None

    def test_get_diary_by_date(self, db_session):
        """根据日期获取日记"""
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        today = date.today()
        diary = EmotionDiary(
            user_id=1,
            date=today,
            content="今日日记内容",
            mood_score=5,
            is_deleted=False,
        )
        db_session.add(diary)
        db_session.commit()

        service = DiaryService()
        result = service.get_diary_by_date(db_session, 1, today)
        
        assert result is not None
        assert result.date == today

    async def test_create_diary(self, db_session):
        """创建日记"""
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()

        req = DiaryCreate(
            date=date.today().isoformat(),
            content="这是新建日记的内容",
            mood_score=9,
            mood_level=None,
            primary_emotion=EmotionType.HAPPY,
        )

        service = DiaryService()
        diary = await service.create_diary(db_session, 1, req)
        
        assert diary is not None
        assert diary.user_id == 1
        assert diary.content == "这是新建日记的内容"
        assert diary.mood_score == 9
        assert diary.primary_emotion == EmotionType.HAPPY

    async def test_create_diary_duplicate_date(self, db_session):
        """同一天重复创建日记抛出异常"""
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        today = date.today()
        diary = EmotionDiary(
            user_id=1,
            date=today,
            content="已有日记内容",
            mood_score=5,
            mood_level=MoodLevel.NEUTRAL,
            is_deleted=False,
        )
        db_session.add(diary)
        db_session.commit()

        req = DiaryCreate(
            date=today.isoformat(),
            content="这是新建日记的内容",
            mood_score=9,
        )

        service = DiaryService()
        with pytest.raises(ValueError) as exc_info:
            await service.create_diary(db_session, 1, req)
        
        assert "已经有日记记录" in str(exc_info.value)

    async def test_update_diary(self, db_session):
        """更新日记"""
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        diary = EmotionDiary(
            user_id=1,
            date=date.today(),
            content="旧内容",
            mood_score=5,
            mood_level=MoodLevel.NEUTRAL,
            is_deleted=False,
        )
        db_session.add(diary)
        db_session.commit()

        req = DiaryUpdate(
            content="新内容",
            mood_score=8,
        )

        service = DiaryService()
        result = await service.update_diary(db_session, 1, diary.id, req)
        
        assert result is not None
        assert result.content == "新内容"
        assert result.mood_score == 8

    async def test_update_diary_not_found(self, db_session):
        """更新不存在的日记返回None"""
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()

        req = DiaryUpdate(
            content="内容",
            mood_score=5,
        )

        service = DiaryService()
        result = await service.update_diary(db_session, 1, 99999, req)
        
        assert result is None

    def test_delete_diary(self, db_session):
        """删除日记（软删除）"""
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        diary = EmotionDiary(
            user_id=1,
            date=date.today(),
            content="要删除内容",
            mood_score=5,
            mood_level=MoodLevel.NEUTRAL,
            is_deleted=False,
        )
        db_session.add(diary)
        db_session.commit()

        service = DiaryService()
        result = service.delete_diary(db_session, 1, diary.id)
        
        assert result is True
        check = service.get_diary(db_session, 1, diary.id)
        assert check is None

    def test_delete_diary_not_found(self, db_session):
        """删除不存在的日记返回False"""
        service = DiaryService()
        result = service.delete_diary(db_session, 1, 99999)
        assert result is False

    def test_get_stats(self, db_session):
        """获取统计数据"""
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        # 添加10条记录
        today = date.today()
        for i in range(10):
            diary = EmotionDiary(
                user_id=1,
                date=today - timedelta(days=i),
                content=f"日记 {i} content word count {i}",
                mood_score=i + 1,
                is_deleted=False,
            )
            db_session.add(diary)
        db_session.commit()

        service = DiaryService()
        stats = service.get_stats(db_session, 1)
        
        assert stats is not None
        assert stats["total_count"] == 10
        assert 0 < stats["avg_mood"] < 10
        assert stats["this_month_count"] == 10

    def test_get_mood_trend(self, db_session):
        """获取心情趋势"""
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        today = date.today()
        for i in range(10):
            diary = EmotionDiary(
                user_id=1,
                date=today - timedelta(days=i),
                content=f"日记{i}",
                mood_score=i + 1,
                primary_emotion=EmotionType.HAPPY if i % 2 == 0 else EmotionType.SAD,
                is_deleted=False,
            )
            db_session.add(diary)
        db_session.commit()

        service = DiaryService()
        trend = service.get_mood_trend(db_session, 1, "week")
        
        assert trend is not None
        assert "trend_data" in trend
        assert "emotion_distribution" in trend
        assert "mood_distribution" in trend
        # 最近一周最多包含8天数据（开始今天是周三，一周内就是上周四到本周三共8天）
        data = trend["trend_data"]
        assert data is not None
        assert len(data) > 0
        assert len(data) <= 8

    def test__get_mood_level(self, db_session):
        """测试根据分数获取心情等级"""
        service = DiaryService()
        assert service._get_mood_level(1) == "terrible"
        assert service._get_mood_level(3) == "bad"
        assert service._get_mood_level(5) == "neutral"
        assert service._get_mood_level(7) == "good"
        assert service._get_mood_level(9) == "excellent"


class TestDiaryServiceTags:
    """DiaryService 标签操作测试"""

    def test_create_tag(self, db_session):
        """创建标签"""
        from app.schemas.diary import TagCreate
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()

        req = TagCreate(name="工作", color="#FF0000")
        service = DiaryService()
        tag = service.create_tag(db_session, 1, req)
        
        assert tag is not None
        assert tag.name == "工作"
        assert tag.color == "#FF0000"
        assert tag.user_id == 1

    def test_create_tag_duplicate_name(self, db_session):
        """创建重复名称标签抛出异常"""
        from app.schemas.diary import TagCreate
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()

        req = TagCreate(name="工作", color="#FF0000")
        service = DiaryService()
        service.create_tag(db_session, 1, req)
        
        with pytest.raises(ValueError) as exc_info:
            service.create_tag(db_session, 1, req)
        
        assert "该标签已存在" in str(exc_info.value)

    def test_list_tags_ordered_by_usage(self, db_session):
        """获取标签列表按使用次数排序"""
        from app.models.diary import DiaryTag
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        tag1 = DiaryTag(user_id=1, name="高频", use_count=10)
        tag2 = DiaryTag(user_id=1, name="中频", use_count=5)
        tag3 = DiaryTag(user_id=1, name="低频", use_count=1)
        db_session.add_all([tag1, tag2, tag3])
        db_session.commit()

        service = DiaryService()
        tags = service.list_tags(db_session, 1)
        
        assert len(tags) == 3
        assert tags[0].name == "高频"
        assert tags[1].name == "中频"
        assert tags[2].name == "低频"

    def test_update_tag(self, db_session):
        """更新标签"""
        from app.models.diary import DiaryTag
        from app.schemas.diary import TagUpdate
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        tag = DiaryTag(user_id=1, name="旧名称", color="#000000", use_count=5)
        db_session.add(tag)
        db_session.commit()

        req = TagUpdate(name="新名称", color="#FFFFFF")
        service = DiaryService()
        result = service.update_tag(db_session, 1, tag.id, req)
        
        assert result is not None
        assert result.name == "新名称"
        assert result.color == "#FFFFFF"

    def test_update_tag_not_found(self, db_session):
        """更新不存在的标签返回None"""
        from app.schemas.diary import TagUpdate
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()

        req = TagUpdate(name="新名称")
        service = DiaryService()
        result = service.update_tag(db_session, 1, 99999, req)
        
        assert result is None

    def test_delete_tag(self, db_session):
        """删除标签"""
        from app.models.diary import DiaryTag
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        tag = DiaryTag(user_id=1, name="要删除", color="#000000")
        db_session.add(tag)
        db_session.commit()

        service = DiaryService()
        result = service.delete_tag(db_session, 1, tag.id)
        
        assert result is True
        check = db_session.query(DiaryTag).filter(DiaryTag.id == tag.id).first()
        assert check is None

    def test_delete_tag_not_found(self, db_session):
        """删除不存在的标签返回False"""
        service = DiaryService()
        result = service.delete_tag(db_session, 1, 99999)
        assert result is False


class TestDiaryServiceMoodRecords:
    """DiaryService 心情快速记录测试"""

    def test_create_mood_record(self, db_session):
        """创建心情记录"""
        from app.schemas.diary import MoodCreate
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()

        req = MoodCreate(
            mood_score=8,
            emotion="happy",
            note="今天心情不错",
            location="家里",
            activity="看书",
        )

        service = DiaryService()
        record = service.create_mood_record(db_session, 1, req)
        
        assert record is not None
        assert record.user_id == 1
        assert record.mood_score == 8
        assert record.note == "今天心情不错"

    def test_list_mood_records(self, db_session):
        """获取心情记录列表"""
        from app.models.diary import MoodRecord
        from datetime import datetime
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        for i in range(5):
            record = MoodRecord(
                user_id=1,
                mood_score=5 + i,
                note=f"记录{i}",
            )
            db_session.add(record)
        db_session.commit()

        service = DiaryService()
        records = service.list_mood_records(db_session, 1, limit=10)
        
        assert len(records) == 5


class TestDiaryServiceAiAnalysis:
    """DiaryService AI分析测试"""

    async def test_analyze_diary_success(self, db_session):
        """成功分析日记"""
        from unittest.mock import patch, AsyncMock
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        diary = EmotionDiary(
            user_id=1,
            date=date.today(),
            content="今天我有点焦虑，因为工作压力很大，但晚上和朋友聊天后感觉好多了。",
            mood_score=6,
            is_deleted=False,
            analysis_status="pending",
        )
        db_session.add(diary)
        db_session.commit()

        mock_chat = AsyncMock(return_value='''
{
    "analysis": "用户感受到工作压力带来的焦虑，但通过社交得到了缓解。",
    "suggestion": "继续保持社交支持，可以尝试深呼吸放松。",
    "keywords": ["焦虑", "工作压力", "朋友"]
}
''')

        service = DiaryService()
        with patch("app.services.llm.factory.chat", mock_chat):
            result = await service.analyze_diary(db_session, 1, diary.id)
        
        assert result is not None
        assert result["status"] == "completed"
        assert "analysis" in result
        assert "suggestion" in result
        # 验证状态更新
        updated = service.get_diary(db_session, 1, diary.id)
        assert updated.analysis_status == "completed"

    async def test_analyze_diary_not_found(self, db_session):
        """分析不存在的日记返回None"""
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()

        service = DiaryService()
        result = await service.analyze_diary(db_session, 1, 99999)
        
        assert result is None

    async def test_analyze_diary_empty_content(self, db_session):
        """分析空内容日记"""
        user = User(
            id=1,
            phone="13900000001",
            password_hash="hash",
            is_active=True,
        )
        db_session.add(user)
        diary = EmotionDiary(
            user_id=1,
            date=date.today(),
            content="",
            mood_score=5,
            is_deleted=False,
        )
        db_session.add(diary)
        db_session.commit()

        service = DiaryService()
        result = await service.analyze_diary(db_session, 1, diary.id)
        
        assert result["status"] == "no_content"
