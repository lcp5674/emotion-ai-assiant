"""
危机干预服务 - 检测和处理自伤/自杀倾向等危机情况
"""
import re
from typing import Tuple, List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import loguru


class CrisisLevel(Enum):
    """危机等级"""
    NONE = "none"              # 无风险
    LOW = "low"                # 低风险 - 需要关注
    MEDIUM = "medium"          # 中等风险 - 需要干预
    HIGH = "high"              # 高风险 - 立即干预
    CRITICAL = "critical"      # 极危 - 紧急处理


@dataclass
class CrisisResult:
    """危机检测结果"""
    level: CrisisLevel
    detected: bool
    keywords: List[str]
    risk_score: int  # 0-100
    suggestion: str
    intervention_required: bool


class CrisisDetector:
    """危机检测服务"""

    # 高风险关键词 - 自杀/自伤倾向
    HIGH_RISK_KEYWORDS = [
        "自杀", "不想活", "不想活了", "不想再活", "活着没意思",
        "活着没意义", "结束生命", "结束自己", "不想活下去",
        "想结束", "想离开这个世界", "离开这个世界", "离开人世",
        "想离开人世", "去死", "我想死", "想自杀",
        "不想继续", "不想继续了", "一死了之", "了断",
        "自我了断", "割腕", "跳楼", "喝药",
        "吃安眠药", "上吊", "烧炭",
        "自伤", "自残", "伤害自己", "伤害自己身体",
    ]

    # 中等风险关键词 - 抑郁/绝望情绪
    MEDIUM_RISK_KEYWORDS = [
        "绝望", "好绝望", "很绝望", "太绝望",
        "无助", "好无助", "很无助", "太无助",
        "没有希望", "没有任何希望", "看不到希望",
        "人生没有意义", "人生没意义", "生活没意义",
        "我没用", "我没用了", "我是个废物",
        "都是我的错", "我什么都做不好",
        "没有人在乎我", "没人在乎我",
        "没有人关心我", "没人关心我",
        "没有人懂我", "没人懂我",
        "压力好大", "压力太大了",
        "撑不下去了", "快撑不住了", "撑不住了",
        "快坚持不住了", "坚持不住了",
        "想消失", "想要消失", "消失就好了",
        "好累", "好累好累", "真的好累",
        "好痛苦", "太痛苦了", "很痛苦",
        "崩溃", "快要崩溃", "快崩溃了",
    ]

    # 求助信号
    HELP_SEEKING_KEYWORDS = [
        "有人能帮我吗", "谁能帮帮我", "能帮帮我吗",
        "需要帮助", "我需要帮助", "需要人帮助",
        "救救我", "救我",
    ]

    # 保护性因素关键词
    PROTECTIVE_KEYWORDS = [
        "家人", "朋友", "孩子", "父母",
        "不想让", "舍不得", "放不下",
        "还有", "还有希望",
        "会好的", "会好起来",
        "想活下去", "要活下去",
        "坚持", "努力",
    ]

    def __init__(self):
        # 预编译正则表达式，提高匹配效率
        self._high_risk_pattern = self._compile_pattern(self.HIGH_RISK_KEYWORDS)
        self._medium_risk_pattern = self._compile_pattern(self.MEDIUM_RISK_KEYWORDS)
        self._help_seeking_pattern = self._compile_pattern(self.HELP_SEEKING_KEYWORDS)
        self._protective_pattern = self._compile_pattern(self.PROTECTIVE_KEYWORDS)

    def _compile_pattern(self, keywords: List[str]) -> re.Pattern:
        """编译关键词正则表达式"""
        if not keywords:
            return None
        # 使用word boundary和大小写不敏感
        pattern_str = "|".join(re.escape(kw) for kw in keywords)
        return re.compile(pattern_str, re.IGNORECASE)

    async def detect(self, text: str) -> CrisisResult:
        """
        检测文本中的危机信号

        Args:
            text: 用户输入的文本

        Returns:
            CrisisResult: 危机检测结果
        """
        if not text or not text.strip():
            return CrisisResult(
                level=CrisisLevel.NONE,
                detected=False,
                keywords=[],
                risk_score=0,
                suggestion=self._get_suggestion(CrisisLevel.NONE),
                intervention_required=False,
            )

        detected_keywords = []
        risk_score = 0

        # 检测高风险关键词
        high_risk_matches = self._find_matches(self._high_risk_pattern, text)
        if high_risk_matches:
            risk_score += 60
            detected_keywords.extend(high_risk_matches)

        # 检测中等风险关键词
        medium_risk_matches = self._find_matches(self._medium_risk_pattern, text)
        if medium_risk_matches:
            risk_score += 30
            detected_keywords.extend(medium_risk_matches)

        # 检测求助信号
        help_seeking_matches = self._find_matches(self._help_seeking_pattern, text)
        if help_seeking_matches:
            risk_score += 10
            detected_keywords.extend(help_seeking_matches)

        # 检测保护性因素，降低风险分数
        protective_matches = self._find_matches(self._protective_pattern, text)
        if protective_matches:
            risk_score = max(0, risk_score - 20)

        # 去重关键词
        detected_keywords = list(set(detected_keywords))

        # 判断危机等级
        level = self._determine_level(risk_score, len(high_risk_matches) > 0)

        # 记录日志
        if level != CrisisLevel.NONE:
            loguru.logger.warning(
                f"危机检测: level={level.value}, score={risk_score}, keywords={detected_keywords}"
            )

        return CrisisResult(
            level=level,
            detected=level != CrisisLevel.NONE,
            keywords=detected_keywords,
            risk_score=risk_score,
            suggestion=self._get_suggestion(level),
            intervention_required=level in [CrisisLevel.HIGH, CrisisLevel.CRITICAL],
        )

    def _find_matches(self, pattern: Optional[re.Pattern], text: str) -> List[str]:
        """查找匹配的关键词"""
        if not pattern:
            return []
        return pattern.findall(text)

    def _determine_level(self, score: int, has_high_risk: bool) -> CrisisLevel:
        """确定危机等级"""
        if has_high_risk and score >= 70:
            return CrisisLevel.CRITICAL
        if has_high_risk:
            return CrisisLevel.HIGH
        if score >= 60:
            return CrisisLevel.HIGH
        if score >= 30:
            return CrisisLevel.MEDIUM
        if score >= 10:
            return CrisisLevel.LOW
        return CrisisLevel.NONE

    def _get_suggestion(self, level: CrisisLevel) -> str:
        """获取干预建议"""
        suggestions = {
            CrisisLevel.NONE: "",
            CrisisLevel.LOW: (
                "我注意到你最近可能有些困扰。"
                "如果愿意的话，可以和我多聊聊发生了什么。"
            ),
            CrisisLevel.MEDIUM: (
                "我能感受到你正在经历一些困难。"
                "请记住，你不是一个人在面对这些。"
                "如果情况没有好转，建议寻求专业心理咨询师的帮助。"
            ),
            CrisisLevel.HIGH: (
                "我非常关心你现在的状态。"
                "请相信，无论遇到什么困难，都会有解决的办法。"
                "请立即联系你信任的家人或朋友，"
                "或者拨打心理援助热线寻求专业帮助。"
            ),
            CrisisLevel.CRITICAL: (
                "我非常担心你现在的安全。"
                "请立即停止任何可能伤害自己的想法。"
                "你值得被爱和被关心。"
                "请立即拨打危机干预热线寻求紧急帮助：\n"
                "全国心理援助热线：400-161-9995\n"
                "北京心理危机研究与干预中心：010-82951332\n"
                "生命热线：400-821-1215"
            ),
        }
        return suggestions.get(level, "")

    async def get_intervention_response(self, level: CrisisLevel) -> str:
        """
        获取危机干预响应

        Args:
            level: 危机等级

        Returns:
            str: 干预响应文本
        """
        responses = {
            CrisisLevel.NONE: "",
            CrisisLevel.LOW: (
                "我在这里陪着你。能和我说说发生了什么吗？"
                "有时候把心里的话说出来，会感觉好一些。"
            ),
            CrisisLevel.MEDIUM: (
                "我能感受到你现在的痛苦和挣扎。"
                "你不需要独自承担这一切。"
                "让我陪你一起度过这个难关，好吗？"
            ),
            CrisisLevel.HIGH: (
                "我非常、非常担心你。"
                "请答应我，不要做任何伤害自己的事情。"
                "你的生命很重要，值得被珍惜。"
                "请现在就给家人或朋友打个电话，让他们陪着你。"
            ),
            CrisisLevel.CRITICAL: (
                "我必须告诉你，我现在非常担心你的安全。"
                "无论你正在经历什么，都不值得用生命来解决。"
                "请立即拨打以下热线寻求专业帮助：\n\n"
                "📞 全国心理援助热线：400-161-9995\n"
                "📞 北京心理危机干预中心：010-82951332\n"
                "📞 生命热线：400-821-1215\n\n"
                "请现在就拨打，专业的人员会帮助你的。"
                "你不是一个人，我们都关心你。"
            ),
        }
        return responses.get(level, "")

    async def should_alert_admin(self, level: CrisisLevel) -> bool:
        """是否需要告警管理员"""
        return level in [CrisisLevel.HIGH, CrisisLevel.CRITICAL]


# 全局服务实例
_crisis_detector: Optional[CrisisDetector] = None


def get_crisis_detector() -> CrisisDetector:
    """获取危机检测服务实例"""
    global _crisis_detector
    if _crisis_detector is None:
        _crisis_detector = CrisisDetector()
    return _crisis_detector


# 危机干预资源配置
CRISIS_RESOURCES = {
    "hotlines": [
        {
            "name": "全国心理援助热线",
            "phone": "400-161-9995",
            "service_time": "24小时",
        },
        {
            "name": "北京心理危机研究与干预中心",
            "phone": "010-82951332",
            "service_time": "24小时",
        },
        {
            "name": "生命热线",
            "phone": "400-821-1215",
            "service_time": "24小时",
        },
        {
            "name": "希望24热线",
            "phone": "400-161-9995",
            "service_time": "24小时",
        },
    ],
    "emergency": "110/120",
    "message": "如果你或身边的人正在经历危机，请立即寻求专业帮助。",
}
