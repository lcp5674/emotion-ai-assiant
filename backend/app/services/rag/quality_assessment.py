"""
RAG回答质量评估服务 - 评估和控制LLM+RAG回答的精准度和质量
"""
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import re
import loguru

from app.services.rag.knowledge_data import (
    get_sbti_theme,
    get_attachment_style,
    KNOWLEDGE_ARTICLES,
)


class ConfidenceLevel(str, Enum):
    """回答置信度等级"""
    HIGH = "high"      # 高置信度 (>=0.8)
    MEDIUM = "medium"  # 中置信度 (>=0.5)
    LOW = "low"       # 低置信度 (<0.5)


class AnswerQualityMetrics:
    """回答质量指标"""
    def __init__(
        self,
        relevance_score: float,      # 检索相关性得分 (0-1)
        factual_accuracy: float,     # 事实准确性得分 (0-1)
        personalization_score: float, # 个性化程度得分 (0-1)
        length_score: float,         # 回答长度合理性得分 (0-1)
        safety_score: float,         # 安全性得分 (0-1)
    ):
        self.relevance_score = relevance_score
        self.factual_accuracy = factual_accuracy
        self.personalization_score = personalization_score
        self.length_score = length_score
        self.safety_score = safety_score

        # 计算综合置信度
        self.overall_confidence = (
            relevance_score * 0.35 +
            factual_accuracy * 0.30 +
            personalization_score * 0.15 +
            length_score * 0.10 +
            safety_score * 0.10
        )

        # 确定置信度等级
        if self.overall_confidence >= 0.8:
            self.level = ConfidenceLevel.HIGH
        elif self.overall_confidence >= 0.5:
            self.level = ConfidenceLevel.MEDIUM
        else:
            self.level = ConfidenceLevel.LOW

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_confidence": round(self.overall_confidence, 3),
            "level": self.level.value,
            "components": {
                "relevance_score": round(self.relevance_score, 3),
                "factual_accuracy": round(self.factual_accuracy, 3),
                "personalization_score": round(self.personalization_score, 3),
                "length_score": round(self.length_score, 3),
                "safety_score": round(self.safety_score, 3),
            },
        }


class RAGQualityService:
    """RAG回答质量评估服务"""

    # 最优回答长度范围 (字符数)
    OPTIMAL_LENGTH_MIN = 100
    OPTIMAL_LENGTH_MAX = 800

    # 敏感话题关键词
    SENSITIVE_TOPICS = [
        "自杀", "自残", "药物", "毒品", "暴力", "虐待",
        "儿童性侵", "恐怖主义", "犯罪", "违法行为"
    ]

    # 心理咨询转介关键词
    CRISIS_KEYWORDS = [
        "不想活了", "活着没意思", "想死", "轻生", "自杀念头",
        "自残", "割腕", "跳楼", "安眠药"
    ]

    def __init__(self):
        self._sbti_themes_cache = None
        self._attachment_styles_cache = None

    def _get_sbti_themes(self) -> List[str]:
        """获取所有SBTI主题"""
        if self._sbti_themes_cache is None:
            from app.services.rag.knowledge_data import get_all_sbti_themes
            themes = get_all_sbti_themes()
            self._sbti_themes_cache = list(themes.keys())
        return self._sbti_themes_cache

    def _get_attachment_styles(self) -> List[str]:
        """获取所有依恋风格"""
        if self._attachment_styles_cache is None:
            self._attachment_styles_cache = ["安全型", "焦虑型", "回避型", "混乱型"]
        return self._attachment_styles_cache

    def assess_retrieval_relevance(
        self,
        query: str,
        retrieved_docs: List[Dict[str, Any]],
    ) -> float:
        """评估检索相关性"""
        if not retrieved_docs:
            return 0.0

        # 关键词匹配分析
        query_keywords = self._extract_keywords(query)
        relevance_scores = []

        for doc in retrieved_docs:
            doc_text = doc.get("text", "")
            doc_keywords = self._extract_keywords(doc_text)

            # 计算关键词重叠度
            if query_keywords:
                overlap = len(set(query_keywords) & set(doc_keywords))
                keyword_score = overlap / len(query_keywords)
            else:
                keyword_score = 0.5  # 默认分数

            # 文本长度惩罚
            length_score = 1.0
            if len(doc_text) < 50:
                length_score = 0.5
            elif len(doc_text) > 2000:
                length_score = 0.8

            doc_relevance = keyword_score * 0.7 + length_score * 0.3
            relevance_scores.append(doc_relevance)

        # 取最高分的文档作为参考
        return max(relevance_scores) if relevance_scores else 0.0

    def assess_factual_accuracy(
        self,
        answer: str,
        retrieved_docs: List[Dict[str, Any]],
        query: str,
    ) -> float:
        """评估事实准确性"""
        score = 1.0

        # 1. 检查MBTI类型准确性
        mbti_types = ["INTJ", "INTP", "ENTJ", "ENTP", "INFJ", "INFP",
                       "ENFJ", "ENFP", "ISTJ", "ISFJ", "ESTJ", "ESFJ",
                       "ISTP", "ISFP", "ESTP", "ESFP"]

        for mbti in mbti_types:
            if mbti in answer:
                # 检查是否与知识库一致
                consistent = False
                for doc in retrieved_docs:
                    if mbti in doc.get("text", ""):
                        consistent = True
                        break
                if not consistent and retrieved_docs:
                    score -= 0.1

        # 2. 检查SBTI主题准确性
        sbti_themes = self._get_sbti_themes()
        mentioned_themes = [t for t in sbti_themes if t in answer]
        if mentioned_themes:
            for theme in mentioned_themes:
                theme_info = get_sbti_theme(theme)
                if not theme_info and retrieved_docs:
                    # 知识库中没有该主题
                    score -= 0.05

        # 3. 检查依恋风格准确性
        attachment_styles = self._get_attachment_styles()
        mentioned_styles = [s for s in attachment_styles if s in answer]
        if mentioned_styles:
            for style in mentioned_styles:
                style_info = get_attachment_style(style)
                if not style_info and retrieved_docs:
                    score -= 0.05

        # 4. 检查自我矛盾
        positive_words = ["总是", "永远", "一定", "绝对"]
        for word in positive_words:
            if word in answer:
                score -= 0.05  # 过度绝对的表述可能不准确

        # 5. 检查不确定性表达
        uncertain_words = ["可能", "也许", "大概", "不确定"]
        uncertain_count = sum(1 for w in uncertain_words if w in answer)
        if uncertain_count > 3:
            score -= 0.1

        return max(0.0, min(1.0, score))

    def assess_personalization(
        self,
        answer: str,
        user_mbti: Optional[str],
        user_sbti: Optional[List[str]],
        user_attachment_style: Optional[str],
        persona_context: Optional[Dict[str, Any]],
    ) -> float:
        """评估个性化程度"""
        score = 0.0
        max_score = 1.0

        if not persona_context and not any([user_mbti, user_sbti, user_attachment_style]):
            return 0.5  # 无画像信息时的默认分数

        personalization_indicators = 0
        total_indicators = 0

        # 1. MBTI个性化
        total_indicators += 1
        if user_mbti and user_mbti in answer:
            personalization_indicators += 1
        elif persona_context and persona_context.get("mbti"):
            personalization_indicators += 0.5

        # 2. SBTI才干个性化
        total_indicators += 1
        if user_sbti:
            for theme in user_sbti[:3]:  # 只检查Top3
                if theme and theme in answer:
                    personalization_indicators += 0.5
                    break
        elif persona_context and persona_context.get("sbti"):
            personalization_indicators += 0.5

        # 3. 依恋风格个性化
        total_indicators += 1
        if user_attachment_style and user_attachment_style in answer:
            personalization_indicators += 1
        elif persona_context and persona_context.get("attachment"):
            personalization_indicators += 0.5

        # 4. 检查个性化建议
        personalization_phrases = [
            "根据你的", "针对你", "因为你", "对你来说",
            "基于你的", "结合你的"
        ]
        for phrase in personalization_phrases:
            if phrase in answer:
                personalization_indicators += 0.3
                break

        score = personalization_indicators / total_indicators if total_indicators > 0 else 0.5
        return max(0.0, min(1.0, score))

    def assess_length_quality(self, answer: str) -> float:
        """评估回答长度合理性"""
        length = len(answer)

        # 字符数评分
        if self.OPTIMAL_LENGTH_MIN <= length <= self.OPTIMAL_LENGTH_MAX:
            return 1.0
        elif length < self.OPTIMAL_LENGTH_MIN:
            # 太短，按比例递减
            return max(0.3, length / self.OPTIMAL_LENGTH_MIN)
        else:
            # 太长，按比例递减
            excess_ratio = length / self.OPTIMAL_LENGTH_MAX
            if excess_ratio > 3:
                return 0.3
            elif excess_ratio > 2:
                return 0.5
            elif excess_ratio > 1.5:
                return 0.7
            else:
                return 0.9

    def assess_safety(self, answer: str) -> float:
        """评估回答安全性"""
        score = 1.0

        # 1. 检查敏感话题
        for topic in self.SENSITIVE_TOPICS:
            if topic in answer:
                # 如果涉及敏感话题，需要专业处理的暗示
                score -= 0.1

        # 2. 检查危机关键词
        for keyword in self.CRISIS_KEYWORDS:
            if keyword in answer:
                # 如果涉及危机内容，需要转介建议
                score -= 0.2

        # 3. 检查是否提供专业医疗建议
        medical_keywords = ["药物治疗", "精神科", "处方药", "诊断"]
        for keyword in medical_keywords:
            if keyword in answer:
                score -= 0.1

        # 4. 检查是否有免责声明
        disclaimer_phrases = ["我不是", "不能替代", "如有需要请咨询"]
        has_disclaimer = any(p in answer for p in disclaimer_phrases)
        if not has_disclaimer:
            score -= 0.05  # 建议添加免责声明

        return max(0.0, min(1.0, score))

    def assess_answer_quality(
        self,
        answer: str,
        query: str,
        retrieved_docs: List[Dict[str, Any]],
        user_mbti: Optional[str] = None,
        user_sbti: Optional[List[str]] = None,
        user_attachment_style: Optional[str] = None,
        persona_context: Optional[Dict[str, Any]] = None,
    ) -> AnswerQualityMetrics:
        """综合评估回答质量"""
        return AnswerQualityMetrics(
            relevance_score=self.assess_retrieval_relevance(query, retrieved_docs),
            factual_accuracy=self.assess_factual_accuracy(answer, retrieved_docs, query),
            personalization_score=self.assess_personalization(
                answer, user_mbti, user_sbti, user_attachment_style, persona_context
            ),
            length_score=self.assess_length_quality(answer),
            safety_score=self.assess_safety(answer),
        )

    def generate_quality_feedback(
        self,
        metrics: AnswerQualityMetrics,
    ) -> Tuple[str, List[str]]:
        """生成质量反馈和改进建议"""
        suggestions = []
        level_desc = ""

        if metrics.level == ConfidenceLevel.HIGH:
            level_desc = "回答质量优秀"
        elif metrics.level == ConfidenceLevel.MEDIUM:
            level_desc = "回答质量一般，可进一步优化"
        else:
            level_desc = "回答质量较低，建议改进"

        # 各维度分析
        if metrics.relevance_score < 0.5:
            suggestions.append("检索相关性较低，建议优化检索策略或扩展知识库")

        if metrics.factual_accuracy < 0.7:
            suggestions.append("存在事实准确性风险，建议核实关键信息")

        if metrics.personalization_score < 0.5:
            suggestions.append("个性化程度不足，建议结合用户画像提供更定制化的回答")

        if metrics.length_score < 0.6:
            suggestions.append("回答长度不太合适，建议调整到合适的篇幅")

        if metrics.safety_score < 0.8:
            suggestions.append("存在安全风险，建议添加专业转介建议或免责声明")

        return level_desc, suggestions

    def _extract_keywords(self, text: str) -> List[str]:
        """提取文本关键词"""
        # 移除标点符号
        text = re.sub(r'[^\w\s]', ' ', text)
        # 分词并过滤停用词
        stopwords = {'的', '了', '是', '在', '我', '有', '和', '就', '不', '人',
                     '都', '一', '这', '上', '也', '很', '到', '说', '要', '去',
                     '你', '会', '着', '没有', '看', '好', '自己', '什么', '吗',
                     '啊', '呢', '吧', '嗯', '哦', '呀', '嘿', '喂'}
        words = [w for w in text.split() if len(w) >= 2 and w not in stopwords]
        return words

    def check_crisis_content(self, query: str) -> Tuple[bool, str]:
        """检查是否包含危机内容"""
        for keyword in self.CRISIS_KEYWORDS:
            if keyword in query:
                return True, f"检测到危机关键词: {keyword}"
        return False, ""

    def generate_crisis_response(self) -> str:
        """生成危机转介回复"""
        return """感谢你分享了你的感受。我注意到你提到了可能表示自己有困难的想法。

我想让你知道，你的感受真的很重要。

如果你现在感到痛苦或绝望，请记住：
1. **你并不孤单** - 很多人都会经历困难的时刻
2. **帮助是存在的** - 专业的心理咨询师可以提供你需要的支持
3. **寻求帮助是勇敢的** - 这是一个重要的第一步

**紧急帮助资源**：
- 全国心理援助热线：400-161-9995
- 北京心理危机研究与干预中心：010-82951332
- 生命热线：400-821-1215

如果你现在处于紧急危险中，请立即拨打120或前往最近的医院急诊。

记住，无论你现在感觉如何，总有人愿意倾听和支持你。"""
