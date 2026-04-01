# 情感日记相关API
from app.schemas.diary import (
    DiaryCreate,
    DiaryUpdate,
    DiaryDetailSchema,
    DiaryListResponse,
    DiarySummarySchema,
    MoodCreate,
    MoodRecordSchema,
    TagCreate,
    TagUpdate,
    DiaryTagSchema,
    DiaryQuery,
    MoodTrendResponse,
    DiaryStatsResponse,
    AnalysisResponse,
)

router = APIRouter(prefix="/diary", tags=["情感日记"])


@pytest.fixture
def mock_diary_service():
    with patch('app.api.v1.diary.get_diary_service') as mock:
        service = MagicMock()
        mock.return_value = service
        yield service


class TestDiaryCRUD:
    """日记CRUD测试"""

    def test_create_diary(self, client, auth_headers, mock_diary_service):
        """测试创建日记"""
        mock_diary_service.create_diary.return_value = MagicMock(
            id=1,
            date="2026-03-31",
            mood_score=7,
            mood_level="愉悦",
            primary_emotion="开心",
            secondary_emotions=[],
            content="今天心情很好",
            category="daily",
            tags="work,life",
            is_shared=False,
            share_public=False,
            created_at="2026-03-31T10:00:00",
            updated_at="2026-03-31T10:00:00",
        )

        response = client.post(
            "/api/v1/diary/create",
            json={
                "date": "2026-03-31",
                "mood_score": 7,
                "mood_level": "愉悦",
                "primary_emotion": "开心",
                "content": "今天心情很好",
            },
            headers=auth_headers,
        )

        assert response.status_code == 200

    def test_list_diaries(self, client, auth_headers, mock_diary_service):
        """测试获取日记列表"""
        mock_diary_service.list_diaries.return_value = (
            [
                MagicMock(
                    id=1,
                    date="2026-03-31",
                    mood_score=7,
                    mood_level="愉悦",
                    primary_emotion="开心",
                    summary="今天心情很好",
                    tags="work",
                    category="daily",
                    created_at="2026-03-31T10:00:00",
                    updated_at="2026-03-31T10:00:00",
                )
            ],
            1,
        )

        response = client.get(
            "/api/v1/diary/list?page=1&page_size=10",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "data" in data

    def test_get_diary_stats(self, client, auth_headers, mock_diary_service):
        """测试获取日记统计"""
        mock_diary_service.get_stats.return_value = {
            "total_count": 10,
            "current_streak": 3,
            "max_streak": 7,
            "avg_mood": 7.5,
            "most_common_emotion": "开心",
            "avg_words_per_day": 150.0,
            "categories": {"daily": 5, "work": 3, "life": 2},
            "this_month_count": 5,
            "last_month_count": 4,
        }

        response = client.get(
            "/api/v1/diary/stats",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 10


class TestMoodRecord:
    """心情记录测试"""

    def test_create_mood_record(self, client, auth_headers, mock_diary_service):
        """测试快速记录心情"""
        mock_diary_service.create_mood_record.return_value = MagicMock(
            id=1,
            mood_score=8,
            mood_level="愉悦",
            emotion="开心",
            note="工作顺利",
            created_at="2026-03-31T10:00:00",
        )

        response = client.post(
            "/api/v1/diary/mood",
            json={
                "mood_score": 8,
                "mood_level": "愉悦",
                "emotion": "开心",
                "note": "工作顺利",
            },
            headers=auth_headers,
        )

        assert response.status_code == 200


class TestDiaryTags:
    """日记标签测试"""

    def test_create_tag(self, client, auth_headers, mock_diary_service):
        """测试创建标签"""
        mock_diary_service.create_tag.return_value = MagicMock(
            id=1,
            name="工作",
            color="#1890ff",
            use_count=0,
            created_at="2026-03-31T10:00:00",
        )

        response = client.post(
            "/api/v1/diary/tags",
            json={"name": "工作", "color": "#1890ff"},
            headers=auth_headers,
        )

        assert response.status_code == 200

    def test_list_tags(self, client, auth_headers, mock_diary_service):
        """测试获取标签列表"""
        mock_diary_service.list_tags.return_value = [
            MagicMock(
                id=1,
                name="工作",
                color="#1890ff",
                use_count=5,
                created_at="2026-03-31T10:00:00",
            )
        ]

        response = client.get(
            "/api/v1/diary/tags",
            headers=auth_headers,
        )

        assert response.status_code == 200


class TestMoodTrend:
    """心情趋势测试"""

    def test_get_mood_trend(self, client, auth_headers, mock_diary_service):
        """测试获取心情趋势"""
        mock_diary_service.get_mood_trend.return_value = {
            "time_range": "week",
            "start_date": "2026-03-24",
            "end_date": "2026-03-31",
            "avg_score": 7.2,
            "trend_data": [
                {"date": "2026-03-24", "mood_score": 7, "mood_level": "愉悦", "count": 1},
                {"date": "2026-03-25", "mood_score": 6, "mood_level": "平静", "count": 1},
            ],
            "emotion_distribution": {"开心": 5, "平静": 2},
            "mood_distribution": {"愉悦": 4, "平静": 3},
        }

        response = client.get(
            "/api/v1/diary/trend?time_range=week",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["avg_score"] == 7.2
