"""
日记服务单元测试
"""
import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from app.models import User, EmotionDiary, MoodRecord, DiaryTag
from app.services.diary_service import get_diary_service


class TestDiaryService:
    """日记服务测试"""

    @pytest.fixture
    def mock_db(self):
        """模拟数据库会话"""
        return Mock(spec=Session)

    @pytest.fixture
    def diary_service(self):
        """日记服务实例"""
        return get_diary_service()

    @pytest.fixture
    def mock_user(self):
        """模拟用户"""
        user = Mock(spec=User)
        user.id = 1
        return user

    @pytest.fixture
    def mock_diary(self, mock_user):
        """模拟日记"""
        diary = Mock(spec=EmotionDiary)
        diary.id = 1
        diary.user_id = mock_user.id
        diary.content = "测试日记内容"
        diary.emotion = "happy"
        diary.created_at = Mock()
        return diary

    @pytest.fixture
    def mock_mood(self, mock_user):
        """模拟心情记录"""
        mood = Mock(spec=MoodRecord)
        mood.id = 1
        mood.user_id = mock_user.id
        mood.mood = 8
        mood.note = "测试心情"
        mood.recorded_at = Mock()
        return mood

    @pytest.fixture
    def mock_tag(self, mock_user):
        """模拟标签"""
        tag = Mock(spec=DiaryTag)
        tag.id = 1
        tag.user_id = mock_user.id
        tag.name = "测试标签"
        tag.color = "#ff0000"
        return tag

    def test_create_diary(self, diary_service, mock_db, mock_user, mock_diary):
        """测试创建日记"""
        # 准备
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock(side_effect=lambda x: setattr(x, 'id', 1))

        # 执行
        diary = diary_service.create_diary(
            db=mock_db,
            user_id=mock_user.id,
            content="测试内容",
            emotion="happy",
            tags=[1, 2]
        )

        # 验证
        assert diary is not None
        assert diary.content == "测试内容"
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_get_diary(self, diary_service, mock_db, mock_diary):
        """测试获取日记"""
        # 准备
        mock_db.query.return_value.filter.return_value.first.return_value = mock_diary

        # 执行
        diary = diary_service.get_diary(mock_db, 1, 1)

        # 验证
        assert diary == mock_diary

    def test_list_diaries(self, diary_service, mock_db, mock_diary):
        """测试获取日记列表"""
        # 准备
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value = [mock_diary]

        # 执行
        diaries, total = diary_service.list_diaries(
            db=mock_db,
            user_id=1,
            page=1,
            page_size=10
        )

        # 验证
        assert len(diaries) == 1
        assert diaries[0] == mock_diary

    def test_update_diary(self, diary_service, mock_db, mock_diary):
        """测试更新日记"""
        # 准备
        mock_db.query.return_value.filter.return_value.first.return_value = mock_diary
        mock_db.commit = Mock()

        # 执行
        updated_diary = diary_service.update_diary(
            db=mock_db,
            diary_id=1,
            user_id=1,
            content="更新内容",
            emotion="sad"
        )

        # 验证
        assert updated_diary == mock_diary
        mock_db.commit.assert_called_once()

    def test_delete_diary(self, diary_service, mock_db, mock_diary):
        """测试删除日记"""
        # 准备
        mock_db.query.return_value.filter.return_value.first.return_value = mock_diary
        mock_db.delete = Mock()
        mock_db.commit = Mock()

        # 执行
        result = diary_service.delete_diary(mock_db, 1, 1)

        # 验证
        assert result is True
        mock_db.delete.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_create_mood(self, diary_service, mock_db, mock_user, mock_mood):
        """测试创建心情记录"""
        # 准备
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock(side_effect=lambda x: setattr(x, 'id', 1))

        # 执行
        mood = diary_service.create_mood(
            db=mock_db,
            user_id=mock_user.id,
            mood=8,
            note="测试心情"
        )

        # 验证
        assert mood is not None
        assert mood.mood == 8
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_list_moods(self, diary_service, mock_db, mock_mood):
        """测试获取心情记录列表"""
        # 准备
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value = [mock_mood]

        # 执行
        moods, total = diary_service.list_moods(
            db=mock_db,
            user_id=1,
            page=1,
            page_size=10
        )

        # 验证
        assert len(moods) == 1
        assert moods[0] == mock_mood

    def test_create_tag(self, diary_service, mock_db, mock_user, mock_tag):
        """测试创建标签"""
        # 准备
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock(side_effect=lambda x: setattr(x, 'id', 1))

        # 执行
        tag = diary_service.create_tag(
            db=mock_db,
            user_id=mock_user.id,
            name="测试标签",
            color="#ff0000"
        )

        # 验证
        assert tag is not None
        assert tag.name == "测试标签"
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_list_tags(self, diary_service, mock_db, mock_tag):
        """测试获取标签列表"""
        # 准备
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_tag]

        # 执行
        tags = diary_service.list_tags(mock_db, 1)

        # 验证
        assert len(tags) == 1
        assert tags[0] == mock_tag

    def test_get_diary_stats(self, diary_service, mock_db):
        """测试获取日记统计"""
        # 准备
        mock_db.query.return_value.filter.return_value.count.return_value = 10

        # 执行
        stats = diary_service.get_diary_stats(mock_db, 1)

        # 验证
        assert stats is not None
        assert "total_diaries" in stats
