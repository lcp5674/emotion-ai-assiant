"""
mbti_service 单元测试
"""
import pytest
from sqlalchemy.orm import Session

from app.services.mbti_service import MbtiService
from app.models.user import User
from app.models.mbti import MbtiType, MbtiQuestion, AiAssistant, MbtiDimension


class TestMbtiService:
    """MbtiService单元测试"""

    def test_get_questions_all(self, db_session):
        """获取所有测试问题"""
        # 添加测试问题
        q1 = MbtiQuestion(
            dimension=MbtiDimension.EI,
            question_no=1,
            question_text="周末你通常会怎么安排？",
            option_a="约朋友一起出去玩",
            option_b="一个人在家看书",
            weight_a=1,
            weight_b=1,
            is_active=True,
        )
        q2 = MbtiQuestion(
            dimension=MbtiDimension.SN,
            question_no=1,
            question_text="你看地图时，更关注？",
            option_a="具体的街道名",
            option_b="整体的方向",
            weight_a=1,
            weight_b=1,
            is_active=True,
        )
        db_session.add(q1)
        db_session.add(q2)
        db_session.commit()

        service = MbtiService()
        questions = service.get_questions(db_session)
        assert len(questions) == 2

    def test_get_questions_by_dimension(self, db_session):
        """按维度获取测试问题"""
        q1 = MbtiQuestion(
            dimension=MbtiDimension.EI,
            question_no=1,
            question_text="周末你通常会怎么安排？",
            option_a="约朋友一起出去玩",
            option_b="一个人在家看书",
            weight_a=1,
            weight_b=1,
            is_active=True,
        )
        q2 = MbtiQuestion(
            dimension=MbtiDimension.SN,
            question_no=1,
            question_text="你看地图时，更关注？",
            option_a="具体的街道名",
            option_b="整体的方向",
            weight_a=1,
            weight_b=1,
            is_active=True,
        )
        db_session.add(q1)
        db_session.add(q2)
        db_session.commit()

        service = MbtiService()
        questions = service.get_questions(db_session, dimension="EI")
        assert len(questions) == 1
        assert questions[0].dimension == MbtiDimension.EI

    def test_start_test(self, db_session):
        """开始测试返回会话ID"""
        service = MbtiService()
        session_id = service.start_test(1)
        assert session_id.startswith("mbti_1_")
        assert len(session_id) > 10

    async def test_calculate_result_intj(self, db_session):
        """计算MBTI结果 - INTJ"""
        # 添加测试问题
        # 计分规则：
        # answer A: -weight
        # answer B: +weight
        # 结果判定：
        # EI > 0 → E, else → I
        # SN > 0 → S, else → N
        # TF > 0 → T, else → F
        # JP > 0 → J, else → P
        q1 = MbtiQuestion(id=1, dimension=MbtiDimension.EI, weight_a=1, weight_b=1, is_active=True)
        q2 = MbtiQuestion(id=2, dimension=MbtiDimension.SN, weight_a=1, weight_b=1, is_active=True)
        q3 = MbtiQuestion(id=3, dimension=MbtiDimension.TF, weight_a=1, weight_b=1, is_active=True)
        q4 = MbtiQuestion(id=4, dimension=MbtiDimension.JP, weight_a=1, weight_b=1, is_active=True)
        db_session.add_all([q1, q2, q3, q4])
        db_session.commit()

        # INTJ: I(-) N(-) T(+) J(+)
        answers = [
            {"question_id": 1, "answer": "A"},  # A → -1 → EI = -1 → I ✓
            {"question_id": 2, "answer": "A"},  # A → -1 → SN = -1 → N ✓
            {"question_id": 3, "answer": "B"},  # B → +1 → TF = +1 → T ✓
            {"question_id": 4, "answer": "B"},  # B → +1 → JP = +1 → J ✓
        ]

        service = MbtiService()
        result = service.calculate_result(db_session, 1, answers)
        
        assert result["mbti_type"] == "INTJ"
        assert "personality" in result
        assert "strengths" in result
        assert "weaknesses" in result
        assert "suitable_jobs" in result
        assert "relationship_tips" in result
        assert "career_advice" in result
        assert len(result["dimensions"]) == 4

    async def test_calculate_result_enfp(self, db_session):
        """计算MBTI结果 - ENFP"""
        # 添加测试问题
        q1 = MbtiQuestion(id=1, dimension=MbtiDimension.EI, weight_a=1, weight_b=1, is_active=True)
        q2 = MbtiQuestion(id=2, dimension=MbtiDimension.SN, weight_a=1, weight_b=1, is_active=True)
        q3 = MbtiQuestion(id=3, dimension=MbtiDimension.TF, weight_a=1, weight_b=1, is_active=True)
        q4 = MbtiQuestion(id=4, dimension=MbtiDimension.JP, weight_a=1, weight_b=1, is_active=True)
        db_session.add_all([q1, q2, q3, q4])
        db_session.commit()

        # ENFP: E(+) N(-) F(-) P(-)
        answers = [
            {"question_id": 1, "answer": "B"},  # B → +1 → EI = +1 → E ✓
            {"question_id": 2, "answer": "A"},  # A → -1 → SN = -1 → N ✓
            {"question_id": 3, "answer": "A"},  # A → -1 → TF = -1 → F ✓
            {"question_id": 4, "answer": "A"},  # A → -1 → JP = -1 → P ✓
        ]

        service = MbtiService()
        result = service.calculate_result(db_session, 1, answers)
        
        assert result["mbti_type"] == "ENFP"

    def test_calculate_result_has_all_descriptions(self, db_session):
        """计算结果包含所有描述信息"""
        q1 = MbtiQuestion(id=1, dimension=MbtiDimension.EI, weight_a=1, weight_b=1, is_active=True)
        db_session.add(q1)
        db_session.commit()

        answers = [{"question_id": 1, "answer": "A"}]
        service = MbtiService()
        result = service.calculate_result(db_session, 1, answers)
        
        # 不管是什么类型，都应该有描述信息
        assert "personality" in result
        assert isinstance(result["strengths"], list)
        assert isinstance(result["weaknesses"], list)
        assert isinstance(result["suitable_jobs"], list)

    def test_get_recommended_assistants_by_mbti(self, db_session):
        """根据MBTI类型获取推荐助理"""
        assistant1 = AiAssistant(
            id=1,
            name="INTJ助理",
            mbti_type=MbtiType.INTJ,
            personality="理性分析型",
            speaking_style="直接",
            expertise="策略分析",
            greeting="你好，我是INTJ助理",
            is_active=True,
            sort_order=10,
        )
        assistant2 = AiAssistant(
            id=2,
            name="INFP助理",
            mbti_type=MbtiType.INFP,
            personality="理想主义",
            speaking_style="诗意",
            expertise="创意写作",
            greeting="你好，我是INFP助理",
            is_active=True,
            sort_order=9,
        )
        assistant3 = AiAssistant(
            id=3,
            name="不活跃",
            mbti_type=MbtiType.ENFJ,
            personality="test",
            speaking_style="test",
            expertise="test",
            greeting="test",
            is_active=False,
        )
        db_session.add_all([assistant1, assistant2, assistant3])
        db_session.commit()

        service = MbtiService()
        assistants = service.get_recommended_assistants(db_session, "INTJ")
        
        assert len(assistants) == 1
        assert assistants[0].mbti_type == MbtiType.INTJ
        assert assistants[0].is_active is True

    def test_get_recommended_assistants_all_active(self, db_session):
        """不指定MBTI获取所有活跃助理"""
        assistant1 = AiAssistant(
            id=1,
            name="INTJ助理",
            mbti_type=MbtiType.INTJ,
            personality="test",
            speaking_style="test",
            expertise="test",
            greeting="test",
            is_active=True,
        )
        assistant2 = AiAssistant(
            id=2,
            name="INFP助理",
            mbti_type=MbtiType.INFP,
            personality="test",
            speaking_style="test",
            expertise="test",
            greeting="test",
            is_active=True,
        )
        assistant3 = AiAssistant(
            id=3,
            name="INACTIVE助理",
            mbti_type=MbtiType.ENFJ,
            personality="test",
            speaking_style="test",
            expertise="test",
            greeting="test",
            is_active=False,
        )
        db_session.add_all([assistant1, assistant2, assistant3])
        db_session.commit()

        service = MbtiService()
        assistants = service.get_recommended_assistants(db_session)
        
        assert len(assistants) == 2

    def test_seed_questions(self, db_session):
        """初始化题目数据"""
        service = MbtiService()
        service.seed_questions(db_session, force=False)
        
        # 应该添加了48道题（每个维度12道）
        count = db_session.query(MbtiQuestion).count()
        assert count == 48

        # 再次调用不会重复添加
        service.seed_questions(db_session, force=False)
        count2 = db_session.query(MbtiQuestion).count()
        assert count2 == 48

    def test_seed_questions_force(self, db_session):
        """强制重新初始化题目"""
        service = MbtiService()
        service.seed_questions(db_session, force=True)
        
        count = db_session.query(MbtiQuestion).count()
        assert count == 48

    def test_relationship_tips_exists_for_all_types(self, db_session):
        """所有类型都有人际关系建议"""
        service = MbtiService()
        # 测试几个类型
        for mbti_type in ["ISTJ", "INFJ", "ENFP", "ENTJ"]:
            tips = service._get_relationship_tips(mbti_type)
            assert isinstance(tips, str)
            assert len(tips) > 0

    def test_career_advice_exists_for_all_types(self, db_session):
        """所有类型都有职业建议"""
        service = MbtiService()
        # 测试几个类型
        for mbti_type in ["ISTJ", "INFJ", "ENFP", "ENTJ"]:
            advice = service._get_career_advice(mbti_type)
            assert isinstance(advice, str)
            assert len(advice) > 0

    async def test_calculate_result_question_not_found(self, db_session):
        """问题不存在会被跳过"""
        q1 = MbtiQuestion(id=1, dimension=MbtiDimension.EI, weight_a=1, weight_b=1, is_active=True)
        db_session.add(q1)
        db_session.commit()

        answers = [
            {"question_id": 1, "answer": "A"},
            {"question_id": 999, "answer": "B"},  # 不存在
        ]

        service = MbtiService()
        result = service.calculate_result(db_session, 1, answers)
        
        # 计算仍能完成，只是少了一个维度的得分
        assert "mbti_type" in result
        assert "ei_score" in result
