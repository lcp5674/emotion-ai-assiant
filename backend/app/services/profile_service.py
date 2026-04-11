"""
深度画像服务
"""
from typing import List, Dict, Optional, Any
from datetime import datetime
import json
import loguru

from sqlalchemy.orm import Session


class ProfileService:
    """深度画像服务"""

    # AI伴侣推荐配置
    AI_COMPANION_TYPES = {
        "温暖治愈型": {
            "tags": ["温暖", "治愈", "倾听", "共情"],
            "mbti_preference": ["INFJ", "ENFJ", "ISFJ"],
            "description": "擅长情绪支持和深度共情",
        },
        "理性分析型": {
            "tags": ["理性", "分析", "逻辑", "智慧"],
            "mbti_preference": ["INTJ", "INTP", "ISTP"],
            "description": "擅长问题分析和逻辑思考",
        },
        "阳光能量型": {
            "tags": ["阳光", "正能量", "创意", "幽默"],
            "mbti_preference": ["ENFP", "ESFP", "ENTP"],
            "description": "充满活力，能够带来积极能量",
        },
        "知心导师型": {
            "tags": ["知心", "指引", "成长", "智慧"],
            "mbti_preference": ["INTJ", "INFJ", "ENTJ"],
            "description": "擅长引导成长和提供建议",
        },
        "陪伴守护型": {
            "tags": ["陪伴", "守护", "稳定", "耐心"],
            "mbti_preference": ["ISFJ", "ISTJ", "ESFJ"],
            "description": "稳定可靠，擅长长期陪伴",
        },
    }

    def build_profile(
        self,
        mbti_result: Optional[Any] = None,
        sbti_result: Optional[Any] = None,
        attachment_result: Optional[Any] = None,
        user_id: int = 0,
    ) -> Dict[str, Any]:
        """构建三位一体深度画像"""
        profile = {}
        
        # MBTI部分
        if mbti_result:
            profile["mbti"] = self._build_mbti_section(mbti_result)
        
        # SBTI部分
        if sbti_result:
            profile["sbti"] = self._build_sbti_section(sbti_result)
        
        # 依恋风格部分
        if attachment_result:
            profile["attachment"] = self._build_attachment_section(attachment_result)
        
        # 整合洞察
        if any([mbti_result, sbti_result, attachment_result]):
            profile["integrated_insights"] = self._build_integrated_insights(
                mbti_result, sbti_result, attachment_result
            )
        
        # AI伴侣推荐
        if any([mbti_result, sbti_result, attachment_result]):
            profile["ai_companion_recommendation"] = self._build_ai_recommendation(
                mbti_result, sbti_result, attachment_result
            )
        
        return profile

    def _build_mbti_section(self, mbti_result: Any) -> Dict[str, Any]:
        """构建MBTI部分"""
        mbti_type = mbti_result.mbti_type.value if hasattr(mbti_result.mbti_type, 'value') else mbti_result.mbti_type
        
        # MBTI沟通风格映射
        communication_styles = {
            "INTJ": "直接、逻辑性强",
            "INTP": "理性、善于解释",
            "ENTJ": "果断、目标导向",
            "ENTP": "辩论式、充满创意",
            "INFJ": "温柔、富有洞察力",
            "INFP": "理想主义、真诚",
            "ENFJ": "热情、善于激励",
            "ENFP": "热情洋溢、充满灵感",
            "ISTJ": "稳重、注重事实",
            "ISFJ": "体贴、细心周到",
            "ESTJ": "直接、注重效率",
            "ESFJ": "热情、善于社交",
            "ISTP": "冷静、善于分析",
            "ISFP": "温和、富有艺术感",
            "ESTP": "活泼、善于社交",
            "ESFP": "开朗、注重当下",
        }
        
        # 情绪模式映射
        emotional_patterns = {
            "INTJ": "倾向于内敛处理情绪",
            "INTP": "用逻辑分析情绪",
            "ENTJ": "将情绪转化为动力",
            "ENTP": "用幽默化解情绪",
            "INFJ": "深刻体验情绪，善于共情",
            "INFP": "情绪丰富，内在世界深刻",
            "ENFJ": "情绪外放，善于感染他人",
            "ENFP": "情绪波动大，创造力强",
            "ISTJ": "情绪稳定，不轻易外露",
            "ISFJ": "在意他人情绪，容易感同身受",
            "ESTJ": "理性对待情绪，注重事实",
            "ESFJ": "通过社交调节情绪",
            "ISTP": "情绪反应较慢，冷静观察",
            "ISFP": "情绪敏感，富有艺术感受",
            "ESTP": "活在当下，享受情绪",
            "ESFP": "情绪外放，容易感染他人",
        }
        
        return {
            "type": mbti_type,
            "communication_style": communication_styles.get(mbti_type, "真诚直接"),
            "emotional_pattern": emotional_patterns.get(mbti_type, "情绪稳定"),
        }

    def _build_sbti_section(self, sbti_result: Any) -> Dict[str, Any]:
        """构建SBTI部分"""
        top_themes = [
            sbti_result.top_theme_1,
            sbti_result.top_theme_2,
            sbti_result.top_theme_3,
            sbti_result.top_theme_4,
            sbti_result.top_theme_5,
        ]
        # 过滤空值
        top_themes = [t for t in top_themes if t]
        
        return {
            "top5_themes": top_themes,
            "relationship_advantages": self._get_relationship_advantages(sbti_result),
        }

    def _get_relationship_advantages(self, sbti_result: Any) -> List[str]:
        """从SBTI结果中提取关系优势"""
        advantages = []
        
        top_themes = [
            sbti_result.top_theme_1,
            sbti_result.top_theme_2,
            sbti_result.top_theme_3,
            sbti_result.top_theme_4,
            sbti_result.top_theme_5,
        ]
        
        theme_advantages = {
            "关联": ["善于建立深度关系"],
            "体谅": ["共情能力强"],
            "沟通": ["善于表达情感"],
            "包容": ["接纳差异"],
            "和谐": ["善于处理冲突"],
            "伯乐": ["善于培养他人"],
            "交往": ["善于维护友谊"],
        }
        
        for theme in top_themes:
            if theme and theme in theme_advantages:
                advantages.extend(theme_advantages[theme])
        
        return list(set(advantages))[:3]  # 最多返回3个

    def _build_attachment_section(self, attachment_result: Any) -> Dict[str, Any]:
        """构建依恋风格部分"""
        style_value = attachment_result.attachment_style.value if hasattr(attachment_result.attachment_style, 'value') else str(attachment_result.attachment_style)
        characteristics = attachment_result.characteristics if isinstance(attachment_result.characteristics, list) else []
        
        return {
            "style": style_value,
            "triggers": self._get_triggers(style_value),
            "needs": self._get_needs(style_value),
            "characteristics": characteristics,
        }

    def _get_triggers(self, style: str) -> List[str]:
        """获取触发因素"""
        triggers_map = {
            "安全型": ["长期的关系不稳定", "持续的忽视"],
            "焦虑型": ["伴侣没有及时回复", "感觉到被忽视", "关系中的不确定性"],
            "回避型": ["过度的亲密要求", "情绪化的交流", "失去个人空间"],
            "混乱型": ["关系中的任何压力", "被抛弃的恐惧", "对亲密的抗拒"],
        }
        return triggers_map.get(style, [])

    def _get_needs(self, style: str) -> List[str]:
        """获取核心需求"""
        needs_map = {
            "安全型": ["需要定期的亲密互动", "需要开放的沟通"],
            "焦虑型": ["需要定期确认关系", "需要大量的关注和回应", "需要安全感"],
            "回避型": ["需要个人空间", "需要独立的兴趣爱好", "需要慢慢建立信任"],
            "混乱型": ["需要稳定的关系环境", "需要专业的支持", "需要建立安全感"],
        }
        return needs_map.get(style, [])

    def _build_integrated_insights(
        self,
        mbti_result: Optional[Any],
        sbti_result: Optional[Any],
        attachment_result: Optional[Any],
    ) -> Dict[str, Any]:
        """构建整合洞察"""
        insights = {
            "relationship_pattern": "",
            "effective_communication": "",
            "avoid_topics": [],
        }
        
        # 分析关系模式
        patterns = []
        
        if mbti_result:
            mbti_type = mbti_result.mbti_type.value if hasattr(mbti_result.mbti_type, 'value') else mbti_result.mbti_type
            if mbti_type in ["INFJ", "INFP", "ENFJ", "ENFP"]:
                patterns.append("深度连接型")
            elif mbti_type in ["INTJ", "INTP", "ISTP", "ESTP"]:
                patterns.append("独立思考型")
            elif mbti_type in ["ESFJ", "ISFJ", "ESTJ", "ISTJ"]:
                patterns.append("稳定支持型")
            else:
                patterns.append("平衡发展型")
        
        if attachment_result:
            style_value = attachment_result.attachment_style.value if hasattr(attachment_result.attachment_style, 'value') else str(attachment_result.attachment_style)
            if style_value == "安全型":
                patterns.append("安全依恋型")
            elif style_value == "焦虑型":
                patterns.append("渴望亲密型")
            elif style_value == "回避型":
                patterns.append("独立自主型")
            else:
                patterns.append("成长探索型")
        
        insights["relationship_pattern"] = " + ".join(patterns) if patterns else "待完善"
        
        # 有效沟通方式
        if mbti_result:
            mbti_type = mbti_result.mbti_type.value if hasattr(mbti_result.mbti_type, 'value') else mbti_result.mbti_type
            if mbti_type in ["INTJ", "INTP", "ISTP"]:
                insights["effective_communication"] = "先逻辑分析再情感交流"
            elif mbti_type in ["ENFJ", "ENFP", "ESFJ"]:
                insights["effective_communication"] = "先情感共鸣再理性讨论"
            else:
                insights["effective_communication"] = "真诚、开放的沟通"
        
        # 需要避免的话题
        avoid_topics = []
        if attachment_result:
            style_value = attachment_result.attachment_style.value if hasattr(attachment_result.attachment_style, 'value') else str(attachment_result.attachment_style)
            if style_value == "焦虑型":
                avoid_topics.extend(["过度理性分析情感问题", "长时间不回复消息"])
            elif style_value == "回避型":
                avoid_topics.extend(["过于情绪化的表达", "强迫分享感受"])
        
        insights["avoid_topics"] = avoid_topics if avoid_topics else ["避免触及对方的敏感点"]
        
        return insights

    def _build_ai_recommendation(
        self,
        mbti_result: Optional[Any],
        sbti_result: Optional[Any],
        attachment_result: Optional[Any],
    ) -> Dict[str, Any]:
        """构建AI伴侣推荐"""
        recommendation = {
            "companion_type": "温暖治愈型",
            "matching_reason": "",
            "suggested_topics": [],
            "interaction_tips": [],
        }
        
        # 基于MBTI选择伴侣类型
        if mbti_result:
            mbti_type = mbti_result.mbti_type.value if hasattr(mbti_result.mbti_type, 'value') else mbti_result.mbti_type
            
            if mbti_type in ["INTJ", "INTP"]:
                recommendation["companion_type"] = "温暖治愈型"
                recommendation["matching_reason"] = "你的MBTI偏理性，可能需要一个能够共情理解你的伴侣。"
                recommendation["interaction_tips"] = ["多分享感受", "接受对方的关心"]
            elif mbti_type in ["ENFJ", "ENFP"]:
                recommendation["companion_type"] = "知心导师型"
                recommendation["matching_reason"] = "你的MBTI富有同理心，适合与能够引导深度思考的伴侣交流。"
                recommendation["interaction_tips"] = ["倾听为主", "深入探讨话题"]
            elif mbti_type in ["INFJ", "INFP"]:
                recommendation["companion_type"] = "阳光能量型"
                recommendation["matching_reason"] = "你的MBTI偏内向深刻，有时需要一些积极能量来平衡。"
                recommendation["interaction_tips"] = ["接受正能量的感染", "一起参与活动"]
            elif mbti_type in ["ESFJ", "ISFJ"]:
                recommendation["companion_type"] = "理性分析型"
                recommendation["matching_reason"] = "你善于照顾他人，也可以尝试与理性型的伴侣互补成长。"
                recommendation["interaction_tips"] = ["尊重对方的独立空间", "共同解决问题"]
            else:
                recommendation["companion_type"] = "陪伴守护型"
                recommendation["matching_reason"] = "稳定可靠的陪伴是最适合你的方式。"
                recommendation["interaction_tips"] = ["建立稳定的互动习惯", "互相支持"]
        
        # 基于依恋风格调整
        if attachment_result:
            style_value = attachment_result.attachment_style.value if hasattr(attachment_result.attachment_style, 'value') else str(attachment_result.attachment_style)
            if style_value == "焦虑型":
                recommendation["suggested_topics"] = ["安全感建立", "情绪管理", "自我成长"]
                recommendation["interaction_tips"].append("需要定期确认关系")
            elif style_value == "回避型":
                recommendation["suggested_topics"] = ["个人成长", "兴趣爱好", "独立发展"]
                recommendation["interaction_tips"].append("尊重个人空间很重要")
            elif style_value == "安全型":
                recommendation["suggested_topics"] = ["人际关系", "情感交流", "生活分享"]
        
        return recommendation

    def generate_summary(
        self,
        mbti_result: Optional[Any] = None,
        sbti_result: Optional[Any] = None,
        attachment_result: Optional[Any] = None,
        user_id: int = 0,
    ) -> Dict[str, Any]:
        """生成画像摘要"""
        summary_parts = []
        personality_tags = []
        relationship_style = ""
        communication_tips = []
        
        # MBTI摘要
        if mbti_result:
            mbti_type = mbti_result.mbti_type.value if hasattr(mbti_result.mbti_type, 'value') else mbti_result.mbti_type
            summary_parts.append(f"MBTI类型为{mbti_type}型")
            personality_tags.append(f"{mbti_type}型")
            
            type_tips = {
                "INTJ": "给你独立思考的空间",
                "INTP": "尊重你的逻辑分析",
                "ENTJ": "欣赏你的决断力",
                "ENTP": "与你一起探索新想法",
                "INFJ": "理解你深刻的内心世界",
                "INFP": "欣赏你的理想主义",
                "ENFJ": "支持你的人际影响力",
                "ENFP": "激发你的创造力",
                "ISTJ": "尊重你的可靠和稳定",
                "ISFJ": "感激你的细心照顾",
                "ESTJ": "欣赏你的组织能力",
                "ESFJ": "喜欢你的热情社交",
                "ISTP": "给你动手探索的空间",
                "ISFP": "欣赏你的艺术气质",
                "ESTP": "与你一起享受当下",
                "ESFP": "喜欢你的活泼开朗",
            }
            if mbti_type in type_tips:
                communication_tips.append(type_tips[mbti_type])
        
        # SBTI摘要
        if sbti_result:
            top_themes = [
                sbti_result.top_theme_1,
                sbti_result.top_theme_2,
                sbti_result.top_theme_3,
            ]
            top_themes = [t for t in top_themes if t]
            if top_themes:
                summary_parts.append(f"核心才干包括{'、'.join(top_themes)}")
                personality_tags.extend(top_themes)
        
        # 依恋风格摘要
        if attachment_result:
            style_value = attachment_result.attachment_style.value if hasattr(attachment_result.attachment_style, 'value') else str(attachment_result.attachment_style)
            summary_parts.append(f"依恋风格为{style_value}")
            personality_tags.append(style_value)
            
            style_relationship = {
                "安全型": "能够健康地建立亲密关系",
                "焦虑型": "渴望被关注和确认",
                "回避型": "需要个人空间和独立",
                "混乱型": "在亲密和独立间寻找平衡",
            }
            relationship_style = style_relationship.get(style_value, "")
        
        # 整合摘要
        summary = "，".join(summary_parts) if summary_parts else "请完成测评以获取完整画像"
        
        return {
            "summary": summary,
            "personality_tags": personality_tags,
            "relationship_style": relationship_style,
            "communication_tips": communication_tips,
        }


# 全局服务实例
_profile_service: Optional[ProfileService] = None


def get_profile_service() -> ProfileService:
    """获取深度画像服务实例"""
    global _profile_service
    if _profile_service is None:
        _profile_service = ProfileService()
    return _profile_service
