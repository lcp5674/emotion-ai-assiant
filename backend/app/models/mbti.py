"""
MBTI测试模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class MbtiDimension(enum.Enum):
    """MBTI维度"""
    EI = "EI"  # 内向-外向
    SN = "SN"  # 感觉-直觉
    TF = "TF"  # 思维-情感
    JP = "JP"  # 判断-知觉


class MbtiType(enum.Enum):
    """MBTI 16种类型"""
    ISTJ = "ISTJ"
    ISFJ = "ISFJ"
    INFJ = "INFJ"
    INTJ = "INTJ"
    ISTP = "ISTP"
    ISFP = "ISFP"
    INFP = "INFP"
    INTP = "INTP"
    ESTP = "ESTP"
    ESFP = "ESFP"
    ENFP = "ENFP"
    ENTP = "ENTP"
    ESTJ = "ESTJ"
    ESFJ = "ESFJ"
    ENFJ = "ENFJ"
    ENTJ = "ENTJ"


class MbtiQuestion(Base):
    """MBTI测试题目表"""
    __tablename__ = "mbti_questions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    dimension = Column(Enum(MbtiDimension), nullable=False, comment="所属维度")
    question_no = Column(Integer, nullable=False, comment="题目序号(1-48)")
    question_text = Column(Text, nullable=False, comment="题目内容")
    option_a = Column(String(500), nullable=False, comment="选项A")
    option_b = Column(String(500), nullable=False, comment="选项B")
    weight_a = Column(Integer, default=1, comment="选项A权重")
    weight_b = Column(Integer, default=1, comment="选项B权重")

    # 状态
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    def __repr__(self):
        return f"<MbtiQuestion(id={self.id}, dimension={self.dimension}, no={self.question_no})>"


class MbtiAnswer(Base):
    """用户答题记录"""
    __tablename__ = "mbti_answers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    question_id = Column(Integer, ForeignKey("mbti_questions.id"), nullable=False, comment="题目ID")
    answer = Column(String(1), nullable=False, comment="答案(A/B)")
    score = Column(Integer, nullable=False, comment="得分")

    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    # 关系
    user = relationship("User", back_populates="mbti_answers")
    question = relationship("MbtiQuestion")

    def __repr__(self):
        return f"<MbtiAnswer(user_id={self.user_id}, question_id={self.question_id})>"


class MbtiResult(Base):
    """MBTI测试结果"""
    __tablename__ = "mbti_results"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    mbti_type = Column(Enum(MbtiType), nullable=False, comment="MBTI类型")

    # 维度得分
    ei_score = Column(Integer, nullable=False, comment="E-I得分(正数偏E)")
    sn_score = Column(Integer, nullable=False, comment="S-N得分(正数偏S)")
    tf_score = Column(Integer, nullable=False, comment="T-F得分(正数偏T)")
    jp_score = Column(Integer, nullable=False, comment="J-P得分(正数偏J)")

    # 报告JSON
    report_json = Column(Text, nullable=True, comment="详细报告JSON")

    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    # 关系
    user = relationship("User", back_populates="mbti_results")

    def __repr__(self):
        return f"<MbtiResult(user_id={self.user_id}, type={self.mbti_type})>"


class AiAssistant(Base):
    """AI助手表"""
    __tablename__ = "ai_assistants"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False, comment="助手名称")
    avatar = Column(String(500), nullable=True, comment="头像URL")
    mbti_type = Column(Enum(MbtiType), nullable=False, comment="MBTI类型")

    # 个性化配置
    personality = Column(Text, nullable=True, comment="性格描述")
    speaking_style = Column(Text, nullable=True, comment="说话风格")
    expertise = Column(String(500), nullable=True, comment="专长领域")
    greeting = Column(Text, nullable=True, comment="开场白")

    # 标签
    tags = Column(String(500), nullable=True, comment="标签,逗号分隔")

    # 状态
    is_recommended = Column(Boolean, default=False, comment="是否推荐")
    is_active = Column(Boolean, default=True, comment="是否启用")
    sort_order = Column(Integer, default=0, comment="排序")

    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<AiAssistant(id={self.id}, name={self.name}, mbti={self.mbti_type})>"