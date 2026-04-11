"""
人格测评模型 - SBTI优势测评与依恋风格测评
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum, Float, JSON, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class AttachmentStyle(enum.Enum):
    """依恋风格类型"""
    SECURE = "secure"           # 安全型
    ANXIOUS = "anxious"         # 焦虑型
    AVOIDANT = "avoidant"       # 回避型
    DISORGANIZED = "disorganized"  # 混乱型


class SBTITheme(enum.Enum):
    """SBTI 34项才干主题分类"""
    # 执行力 (Executing)
    ACHIEVEMENT = "成就"        # 成就
    ACTIVATOR = "行动"          # 行动
    ADAPTABILITY = "适应"       # 适应
    ARRANGER = "统筹"           # 统筹
    BELIEF = "信仰"             # 信仰
    CONSISTENCY = "公平"        # 公平
    DELIBERATIVE = "审慎"       # 审慎
    DISCIPLINE = "纪律"         # 纪律
    FOCUS = "专注"              # 专注
    RESPONSIBILITY = "责任"     # 责任
    RESTORATIVE = "排难"        # 排难
    
    # 影响力 (Influencing)
    ACTIVATION = "行动"         # 行动 (注：与上面不同维度)
    COMMAND = "统率"            # 统率
    COMMUNICATION = "沟通"      # 沟通
    COMPETITION = "竞争"        # 竞争
    MAXIMIZER = "完美"          # 完美
    SELF_ASSURANCE = "自信"     # 自信
    SIGNIFICANCE = "追求"       # 追求
    WOO = "取悦"                # 取悦
    
    # 关系建立 (Relationship Building)
    ADAPTIVE = "适应"           # 适应
    CONNECTEDNESS = "关联"      # 关联
    DEVELOPER = "伯乐"          # 伯乐
    EMPATHY = "体谅"            # 体谅
    HARMONY = "和谐"            # 和谐
    INCLUDER = "包容"           # 包容
    INDIVIDUALIZATION = "个别"  # 个别
    POSITIVITY = "积极"         # 积极
    RELATOR = "交往"            # 交往
    
    # 战略思维 (Strategic Thinking)
    ANALYTICAL = "分析"         # 分析
    CONTEXT = "回顾"            # 回顾
    FUTURISTIC = "前瞻"         # 前瞻
    IDEATION = "理念"           # 理念
    INPUT = "搜集"              # 搜集
    INTELLECTION = "思维"       # 思维
    LEARNER = "学习"            # 学习
    STRATEGIC = "战略"          # 战略


class SBTIQuestion(Base):
    """SBTI测评题目表 - 24道二选一题目"""
    __tablename__ = "sbti_questions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    question_no = Column(Integer, nullable=False, unique=True, comment="题目序号(1-24)")
    
    # 选项A
    statement_a = Column(Text, nullable=False, comment="陈述A")
    theme_a = Column(String(50), nullable=False, comment="选项A对应的才干主题")
    weight_a = Column(Integer, default=1, comment="选项A权重")
    
    # 选项B
    statement_b = Column(Text, nullable=False, comment="陈述B")
    theme_b = Column(String(50), nullable=False, comment="选项B对应的才干主题")
    weight_b = Column(Integer, default=1, comment="选项B权重")
    
    # 所属才干领域
    domain = Column(String(50), nullable=False, comment="所属领域(执行力/影响力/关系建立/战略思维)")
    
    # 状态
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    answers = relationship("SBTIAnswer", back_populates="question", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<SBTIQuestion(id={self.id}, no={self.question_no})>"


class SBTIAnswer(Base):
    """SBTI用户答题记录"""
    __tablename__ = "sbti_answers"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    question_id = Column(Integer, ForeignKey("sbti_questions.id"), nullable=False, comment="题目ID")
    answer = Column(String(1), nullable=False, comment="答案(A/B)")
    selected_theme = Column(String(50), nullable=False, comment="选择的才干主题")
    score = Column(Integer, nullable=False, comment="得分")
    
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    
    # 关系
    user = relationship("User", back_populates="sbti_answers")
    question = relationship("SBTIQuestion", back_populates="answers")
    
    # 索引
    __table_args__ = (
        Index('ix_sbti_answers_user_id', 'user_id'),
        Index('ix_sbti_answers_question_id', 'question_id'),
    )
    
    def __repr__(self):
        return f"<SBTIAnswer(user_id={self.user_id}, question_id={self.question_id})>"


class SBTIResult(Base):
    """SBTI优势测评结果"""
    __tablename__ = "sbti_results"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    
    # 34项才干得分 (JSON格式存储)
    all_themes_scores = Column(JSON, nullable=False, comment="34项才干得分详情")
    
    # TOP5 优势才干 (按排序)
    top_theme_1 = Column(String(50), nullable=False, comment="第一优势才干")
    top_theme_2 = Column(String(50), nullable=False, comment="第二优势才干")
    top_theme_3 = Column(String(50), nullable=False, comment="第三优势才干")
    top_theme_4 = Column(String(50), nullable=False, comment="第四优势才干")
    top_theme_5 = Column(String(50), nullable=False, comment="第五优势才干")
    
    # 四大领域得分
    executing_score = Column(Float, nullable=False, comment="执行力领域得分")
    influencing_score = Column(Float, nullable=False, comment="影响力领域得分")
    relationship_score = Column(Float, nullable=False, comment="关系建立领域得分")
    strategic_score = Column(Float, nullable=False, comment="战略思维领域得分")
    
    # 主导领域
    dominant_domain = Column(String(50), nullable=False, comment="主导领域")
    
    # 详细报告
    report_json = Column(Text, nullable=True, comment="详细报告JSON")
    
    # 版本控制
    version = Column(Integer, default=1, comment="测评版本")
    is_latest = Column(Boolean, default=True, comment="是否为最新结果")
    
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    user = relationship("User", back_populates="sbti_results")
    
    # 索引
    __table_args__ = (
        Index('ix_sbti_results_user_id', 'user_id'),
        Index('ix_sbti_results_is_latest', 'is_latest'),
    )
    
    def __repr__(self):
        return f"<SBTIResult(user_id={self.user_id}, top1={self.top_theme_1})>"


class AttachmentQuestion(Base):
    """依恋风格测评题目表 - 10题"""
    __tablename__ = "attachment_questions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    question_no = Column(Integer, nullable=False, unique=True, comment="题目序号(1-10)")
    question_text = Column(Text, nullable=False, comment="题目内容")
    
    # 维度权重
    anxiety_weight = Column(Float, default=0, comment="焦虑维度权重")
    avoidance_weight = Column(Float, default=0, comment="回避维度权重")
    
    # 选项设计 (1-7分李克特量表)
    scale_min = Column(Integer, default=1, comment="量表最小值")
    scale_max = Column(Integer, default=7, comment="量表最大值")
    scale_min_label = Column(String(50), default="完全不符合", comment="最小值标签")
    scale_max_label = Column(String(50), default="完全符合", comment="最大值标签")
    
    # 状态
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    
    # 关系
    answers = relationship("AttachmentAnswer", back_populates="question", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<AttachmentQuestion(id={self.id}, no={self.question_no})>"


class AttachmentAnswer(Base):
    """依恋风格用户答题记录"""
    __tablename__ = "attachment_answers"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    question_id = Column(Integer, ForeignKey("attachment_questions.id"), nullable=False, comment="题目ID")
    score = Column(Integer, nullable=False, comment="得分(1-7)")
    
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    
    # 关系
    user = relationship("User", back_populates="attachment_answers")
    question = relationship("AttachmentQuestion", back_populates="answers")
    
    # 索引
    __table_args__ = (
        Index('ix_attachment_answers_user_id', 'user_id'),
        Index('ix_attachment_answers_question_id', 'question_id'),
    )
    
    def __repr__(self):
        return f"<AttachmentAnswer(user_id={self.user_id}, question_id={self.question_id})>"


class AttachmentResult(Base):
    """依恋风格测评结果"""
    __tablename__ = "attachment_results"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    
    # 维度得分
    anxiety_score = Column(Float, nullable=False, comment="焦虑维度得分")
    avoidance_score = Column(Float, nullable=False, comment="回避维度得分")
    
    # 依恋风格类型
    attachment_style = Column(Enum(AttachmentStyle), nullable=False, comment="依恋风格类型")
    
    # 子类型 (更细分的分类)
    sub_type = Column(String(50), nullable=True, comment="子类型描述")
    
    # 特征描述
    characteristics = Column(JSON, nullable=True, comment="特征标签列表")
    
    # 关系建议
    relationship_tips = Column(Text, nullable=True, comment="关系建议")
    self_growth_tips = Column(Text, nullable=True, comment="自我成长建议")
    
    # 详细报告
    report_json = Column(Text, nullable=True, comment="详细报告JSON")
    
    # 版本控制
    version = Column(Integer, default=1, comment="测评版本")
    is_latest = Column(Boolean, default=True, comment="是否为最新结果")
    
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    user = relationship("User", back_populates="attachment_results")
    
    # 索引
    __table_args__ = (
        Index('ix_attachment_results_user_id', 'user_id'),
        Index('ix_attachment_results_is_latest', 'is_latest'),
    )
    
    def __repr__(self):
        return f"<AttachmentResult(user_id={self.user_id}, style={self.attachment_style})>"


class DeepPersonaProfile(Base):
    """
    三位一体深度人格画像
    整合 MBTI + SBTI + 依恋风格
    """
    __tablename__ = "deep_persona_profiles"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, comment="用户ID")
    
    # 三个测评结果的外键
    mbti_result_id = Column(Integer, ForeignKey("mbti_results.id"), nullable=True, comment="MBTI结果ID")
    sbti_result_id = Column(Integer, ForeignKey("sbti_results.id"), nullable=True, comment="SBTI结果ID")
    attachment_result_id = Column(Integer, ForeignKey("attachment_results.id"), nullable=True, comment="依恋风格结果ID")
    
    # 核心人格标签
    core_tags = Column(JSON, nullable=True, comment="核心人格标签")
    
    # 情感模式分析
    emotion_pattern = Column(Text, nullable=True, comment="情感模式分析")
    
    # 沟通风格
    communication_style = Column(Text, nullable=True, comment="沟通风格描述")
    
    # 关系需求
    relationship_needs = Column(JSON, nullable=True, comment="关系需求列表")
    
    # 成长建议
    growth_suggestions = Column(JSON, nullable=True, comment="个性化成长建议")
    
    # AI匹配建议
    ai_compatibility = Column(JSON, nullable=True, comment="AI助手匹配建议")
    
    # 画像完整度 (0-100)
    completeness = Column(Integer, default=0, comment="画像完整度百分比")
    
    # 是否已生成深度报告
    has_deep_report = Column(Boolean, default=False, comment="是否已生成深度报告")
    deep_report_content = Column(Text, nullable=True, comment="深度报告内容")
    
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    user = relationship("User", back_populates="deep_persona_profile")
    mbti_result = relationship("MbtiResult")
    sbti_result = relationship("SBTIResult")
    attachment_result = relationship("AttachmentResult")
    
    # 索引
    __table_args__ = (
        Index('ix_deep_persona_profiles_user_id', 'user_id'),
        Index('ix_deep_persona_profiles_completeness', 'completeness'),
    )
    
    def __repr__(self):
        return f"<DeepPersonaProfile(user_id={self.user_id}, completeness={self.completeness})>"


class PersonaInsight(Base):
    """
    人格洞察记录 - 基于深度画像生成的个性化洞察
    """
    __tablename__ = "persona_insights"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    
    # 洞察类型
    insight_type = Column(String(50), nullable=False, comment="洞察类型(emotion/relationship/career/growth)")
    
    # 洞察标题和内容
    title = Column(String(200), nullable=False, comment="洞察标题")
    content = Column(Text, nullable=False, comment="洞察内容")
    
    # 相关标签
    tags = Column(JSON, nullable=True, comment="相关标签")
    
    # 用户反馈
    is_helpful = Column(Boolean, nullable=True, comment="用户是否觉得有帮助")
    user_feedback = Column(Text, nullable=True, comment="用户反馈")
    
    # 生成来源
    generated_by = Column(String(50), default="ai", comment="生成来源(ai/system)")
    
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    
    # 关系
    user = relationship("User", back_populates="persona_insights")
    
    # 索引
    __table_args__ = (
        Index('ix_persona_insights_user_id', 'user_id'),
        Index('ix_persona_insights_insight_type', 'insight_type'),
        Index('ix_persona_insights_created_at', 'created_at'),
    )
    
    def __repr__(self):
        return f"<PersonaInsight(user_id={self.user_id}, type={self.insight_type})>"
