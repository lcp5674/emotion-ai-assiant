"""
MBTI服务单元测试
"""
import pytest

from app.services.mbti_service import MbtiService, seed_assistants
from app.models.mbti import MbtiType, MbtiDimension


class TestMbtiQuestionSeeding:
    """MBTI题目初始化测试"""

    def test_seed_questions_creates_48_questions(self, db_session):
        """测试创建48道题目"""
        service = MbtiService()
        service.seed_questions(db_session, force=True)

        questions = service.get_questions(db_session)
        assert len(questions) == 48

    def test_seed_questions_creates_correct_dimensions(self, db_session):
        """测试创建正确维度的题目"""
        service = MbtiService()
        service.seed_questions(db_session, force=True)

        ei_questions = service.get_questions(db_session, dimension="EI")
        sn_questions = service.get_questions(db_session, dimension="SN")
        tf_questions = service.get_questions(db_session, dimension="TF")
        jp_questions = service.get_questions(db_session, dimension="JP")

        assert len(ei_questions) == 12
        assert len(sn_questions) == 12
        assert len(tf_questions) == 12
        assert len(jp_questions) == 12

    def test_seed_questions_idempotent(self, db_session):
        """测试多次执行幂等"""
        service = MbtiService()

        # 第一次
        service.seed_questions(db_session, force=False)
        count1 = len(service.get_questions(db_session))

        # 第二次 (force=False 不重新创建)
        service.seed_questions(db_session, force=False)
        count2 = len(service.get_questions(db_session))

        assert count1 == count2

    def test_seed_questions_force_reseeds(self, db_session):
        """测试force=True重新创建"""
        service = MbtiService()
        service.seed_questions(db_session, force=True)

        # 修改一道题目
        questions = service.get_questions(db_session)
        q1 = questions[0]
        original_text = q1.question_text
        q1.question_text = "Modified text"
        db_session.commit()

        # 强制重新创建
        service.seed_questions(db_session, force=True)
        questions = service.get_questions(db_session)
        assert questions[0].question_text == original_text


class TestMbtiResultCalculation:
    """MBTI结果计算测试"""

    def test_calculate_result_returns_valid_type(self, db_session):
        """测试计算返回有效MBTI类型"""
        service = MbtiService()
        service.seed_questions(db_session, force=True)

        questions = service.get_questions(db_session)
        answers = [
            {"question_id": q.id, "answer": "A"}
            for q in questions
        ]

        result = service.calculate_result(db_session, user_id=1, answers=answers)

        assert "mbti_type" in result
        assert result["mbti_type"] in [t.value for t in MbtiType]

    def test_calculate_result_includes_scores(self, db_session):
        """测试计算包含各维度得分"""
        service = MbtiService()
        service.seed_questions(db_session, force=True)

        questions = service.get_questions(db_session)
        answers = [
            {"question_id": q.id, "answer": "A"}
            for q in questions
        ]

        result = service.calculate_result(db_session, user_id=1, answers=answers)

        assert "ei_score" in result
        assert "sn_score" in result
        assert "tf_score" in result
        assert "jp_score" in result

    def test_calculate_result_includes_personality(self, db_session):
        """测试计算包含性格描述"""
        service = MbtiService()
        service.seed_questions(db_session, force=True)

        questions = service.get_questions(db_session)
        answers = [
            {"question_id": q.id, "answer": "A"}
            for q in questions
        ]

        result = service.calculate_result(db_session, user_id=1, answers=answers)

        assert "personality" in result
        assert len(result["personality"]) > 0

    def test_calculate_result_includes_strengths_weaknesses(self, db_session):
        """测试计算包含优势劣势"""
        service = MbtiService()
        service.seed_questions(db_session, force=True)

        questions = service.get_questions(db_session)
        answers = [
            {"question_id": q.id, "answer": "A"}
            for q in questions
        ]

        result = service.calculate_result(db_session, user_id=1, answers=answers)

        assert "strengths" in result
        assert "weaknesses" in result
        assert isinstance(result["strengths"], list)
        assert isinstance(result["weaknesses"], list)

    def test_calculate_result_includes_suitable_jobs(self, db_session):
        """测试计算包含合适工作"""
        service = MbtiService()
        service.seed_questions(db_session, force=True)

        questions = service.get_questions(db_session)
        answers = [
            {"question_id": q.id, "answer": "A"}
            for q in questions
        ]

        result = service.calculate_result(db_session, user_id=1, answers=answers)

        assert "suitable_jobs" in result
        assert isinstance(result["suitable_jobs"], list)

    def test_calculate_result_includes_dimensions(self, db_session):
        """测试计算包含各维度详情"""
        service = MbtiService()
        service.seed_questions(db_session, force=True)

        questions = service.get_questions(db_session)
        answers = [
            {"question_id": q.id, "answer": "A"}
            for q in questions
        ]

        result = service.calculate_result(db_session, user_id=1, answers=answers)

        assert "dimensions" in result
        assert len(result["dimensions"]) == 4

        for dim in result["dimensions"]:
            assert "dimension" in dim
            assert "score" in dim
            assert "tendency" in dim


class TestAssistantSeeding:
    """AI助手初始化测试"""

    def test_seed_assistants_creates_assistants(self, db_session):
        """测试创建AI助手"""
        from app.models import AiAssistant

        seed_assistants(db_session)

        assistants = db_session.query(AiAssistant).all()
        assert len(assistants) >= 8

    def test_seed_assistants_idempotent(self, db_session):
        """测试多次执行幂等"""
        from app.models import AiAssistant

        seed_assistants(db_session)
        count1 = db_session.query(AiAssistant).count()

        seed_assistants(db_session)
        count2 = db_session.query(AiAssistant).count()

        assert count1 == count2

    def test_assistants_have_correct_fields(self, db_session):
        """测试助手有正确字段"""
        from app.models import AiAssistant

        seed_assistants(db_session)
        assistant = db_session.query(AiAssistant).first()

        assert assistant.name is not None
        assert assistant.mbti_type is not None
        assert assistant.personality is not None
        assert assistant.speaking_style is not None
        assert assistant.greeting is not None


class TestRecommendedAssistants:
    """推荐助手获取测试"""

    def test_get_recommended_assistants(self, db_session):
        """测试获取推荐助手"""
        from app.models import AiAssistant

        seed_assistants(db_session)
        service = MbtiService()

        assistants = service.get_recommended_assistants(db_session)
        assert len(assistants) > 0

    def test_get_recommended_assistants_by_mbti(self, db_session):
        """测试按MBTI类型筛选"""
        from app.models import AiAssistant

        seed_assistants(db_session)
        service = MbtiService()

        intj_assistants = service.get_recommended_assistants(
            db_session, mbti_type="INTJ"
        )

        for a in intj_assistants:
            assert a.mbti_type.value == "INTJ"


class TestTypeDescriptions:
    """类型描述测试"""

    def test_all_16_types_have_descriptions(self):
        """测试所有16种类型都有描述"""
        service = MbtiService()

        for mbti_type in MbtiType:
            assert mbti_type.value in service.TYPE_DESCRIPTIONS

    def test_type_description_has_required_fields(self):
        """测试类型描述有必要字段"""
        service = MbtiService()

        intj_desc = service.TYPE_DESCRIPTIONS["INTJ"]
        assert "personality" in intj_desc
        assert "strengths" in intj_desc
        assert "weaknesses" in intj_desc
        assert "suitable_jobs" in intj_desc

    def test_get_relationship_tips(self):
        """测试获取关系建议"""
        service = MbtiService()

        tips = service._get_relationship_tips("INTJ")
        assert isinstance(tips, str)
        assert len(tips) > 0

    def test_get_career_advice(self):
        """测试获取职业建议"""
        service = MbtiService()

        advice = service._get_career_advice("INTJ")
        assert isinstance(advice, str)
        assert len(advice) > 0
