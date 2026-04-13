"""
深度画像上下文构建器 - 根据用户画像构建AI个性化上下文
"""
from typing import Dict, Any, Optional, List
import json
import loguru

from app.models import User, MbtiResult
from app.services.rag.knowledge_data import (
    get_sbti_theme,
    get_mbti_sbti_insight,
    get_attachment_style,
    get_mbti_attachment_tip,
    get_integrated_insight,
    get_all_sbti_themes,
)


class PersonaContextBuilder:
    """深度画像上下文构建器"""

    def __init__(self):
        self.logger = loguru.logger

    async def build_user_context(self, user: User) -> Dict[str, Any]:
        """构建用户深度画像上下文

        Args:
            user: 用户对象

        Returns:
            包含MBTI、SBTI、依恋风格等画像信息的字典
        """
        if not user:
            return {}

        context = {
            "has_profile": False,
            "mbti": {},
            "sbti": {},
            "attachment": {},
            "integrated": {},
            "raw_data": {},
        }

        try:
            # 获取MBTI信息
            mbti_context = await self._build_mbti_context(user)
            context["mbti"] = mbti_context

            # 获取SBTI才干信息
            sbti_context = await self._build_sbti_context(user)
            context["sbti"] = sbti_context

            # 获取依恋风格信息
            attachment_context = await self._build_attachment_context(user)
            context["attachment"] = attachment_context

            # 构建综合洞察
            integrated_context = await self._build_integrated_context(context)
            context["integrated"] = integrated_context

            # 检查是否有画像数据
            context["has_profile"] = bool(
                mbti_context.get("type") or
                sbti_context.get("top_themes") or
                attachment_context.get("style")
            )

            self.logger.debug(f"Built persona context for user {user.id}: has_profile={context['has_profile']}")

        except Exception as e:
            self.logger.error(f"Error building persona context: {e}")
            # 发生错误时返回空上下文，确保系统仍可运行
            return {"has_profile": False}

        return context

    async def _build_mbti_context(self, user: User) -> Dict[str, Any]:
        """构建MBTI上下文"""
        mbti_context = {
            "type": None,
            "dimensions": {},
            "summary": None,
            "description": None,
        }

        if not user.mbti_type:
            return mbti_context

        mbti_type = user.mbti_type.upper()
        mbti_context["type"] = mbti_type

        # 解析MBTI四个维度
        if len(mbti_type) == 4:
            dimensions = {
                "EI": mbti_type[0],  # E或I
                "SN": mbti_type[1],  # S或N
                "TF": mbti_type[2],  # T或F
                "JP": mbti_type[3],  # J或P
            }
            mbti_context["dimensions"] = dimensions

        # 获取MBTI描述
        mbti_context["summary"] = self._get_mbti_summary(mbti_type)

        return mbti_context

    async def _build_sbti_context(self, user: User) -> Dict[str, Any]:
        """构建SBTI才干上下文"""
        sbti_context = {
            "top_themes": [],
            "themes_detail": {},
            "summary": None,
        }

        try:
            from app.models import SbtiResult
            from app.core.database import SessionLocal

            db = SessionLocal()
            try:
                # 从数据库获取用户的SBTI才干结果
                sbti = db.query(SbtiResult).filter(
                    SbtiResult.user_id == user.id
                ).order_by(SbtiResult.created_at.desc()).first()

                if sbti and sbti.top_themes:
                    # top_themes 应该是逗号分隔的字符串，如 "战略、思维、学习"
                    themes = [t.strip() for t in sbti.top_themes.split(",") if t.strip()]
                    sbti_context["top_themes"] = themes[:5]  # 最多取5个

                    # 获取每个才干的详细信息
                    for theme in themes[:5]:
                        theme_info = get_sbti_theme(theme)
                        if theme_info:
                            sbti_context["themes_detail"][theme] = theme_info

                    sbti_context["summary"] = f"用户的核心才干包括：{', '.join(themes[:3])}"
            finally:
                db.close()
        except Exception as e:
            self.logger.error(f"获取SBTI上下文失败: {e}")

        return sbti_context

    async def _build_attachment_context(self, user: User) -> Dict[str, Any]:
        """构建依恋风格上下文"""
        attachment_context = {
            "style": None,
            "characteristics": [],
            "growth": [],
            "communication_tips": None,
        }

        try:
            from app.models import AttachmentStyle
            from app.core.database import SessionLocal

            db = SessionLocal()
            try:
                # 从数据库获取用户的依恋风格评估结果
                attachment = db.query(AttachmentStyle).filter(
                    AttachmentStyle.user_id == user.id
                ).order_by(AttachmentStyle.created_at.desc()).first()

                if attachment:
                    attachment_context["style"] = attachment.style
                    attachment_context["characteristics"] = attachment.characteristics or []
                    attachment_context["growth"] = attachment.growth_suggestions or []
                    attachment_context["communication_tips"] = attachment.communication_tips
            finally:
                db.close()
        except Exception as e:
            self.logger.error(f"获取依恋风格上下文失败: {e}")

        return attachment_context

    async def _build_integrated_context(self, profile_context: Dict[str, Any]) -> Dict[str, Any]:
        """构建综合洞察上下文"""
        integrated = {
            "insights": [],
            "combined_summary": None,
        }

        mbti = profile_context.get("mbti", {}).get("type")
        sbti = profile_context.get("sbti", {})
        attachment = profile_context.get("attachment", {}).get("style")

        # 如果有MBTI+依恋风格组合洞察
        if mbti and attachment:
            tip = get_mbti_attachment_tip(mbti, attachment)
            if tip:
                integrated["insights"].append(tip)

        # 如果有MBTI+SBTI组合洞察
        if mbti and sbti.get("top_themes"):
            for theme in sbti["top_themes"][:2]:  # 取前两个才干
                insight = get_mbti_sbti_insight(mbti, theme)
                if insight:
                    integrated["insights"].append(insight)

        # 构建综合摘要
        if integrated["insights"]:
            integrated["combined_summary"] = " | ".join(integrated["insights"])

        return integrated

    def _get_mbti_summary(self, mbti_type: str) -> str:
        """获取MBTI类型描述"""
        mbti_descriptions = {
            "INTJ": "富有想象力和战略性的思想家，一切都在脑海中构建。",
            "INTP": "具有深刻逻辑分析能力的创新发明家。",
            "ENTJ": "大胆、富有想象力的领导者，具有驱动力的决策者。",
            "ENTP": "聪明好奇的思想者，喜欢智力挑战。",
            "INFJ": "安静而有神秘感的理想主义者，渴望为他人创造美好。",
            "INFP": "富有诗意的理想主义者，渴望内心的和谐与意义。",
            "ENFJ": "富有魅力的领导者，能够启发他人，有责任感。",
            "ENFP": "热情洋溢的创意者，喜欢可能性和新奇。",
            "ISTJ": "安静而可靠的务实者，负责任且值得信赖。",
            "ISFJ": "安静而友好的守护者，重视忠诚和责任感。",
            "ESTJ": "出色的管理者，善于组织，有执行能力。",
            "ESFJ": "热情而尽职的照顾者，喜欢帮助他人。",
            "ISTP": "灵活而理性的问题解决者，善于分析。",
            "ISFP": "灵活而魅力的艺术家，随时准备探索新事物。",
            "ESTP": "聪明且活跃的观察者，喜欢即时体验。",
            "ESFP": "自发的活动家，享受当下的体验。",
        }
        return mbti_descriptions.get(mbti_type, "")

    def get_persona_prompt(self, profile: Dict[str, Any]) -> str:
        """生成基于画像的AI人格提示

        Args:
            profile: 用户画像上下文

        Returns:
            格式化的系统提示字符串
        """
        if not profile.get("has_profile"):
            return ""

        prompt_parts = []

        # MBTI相关提示
        mbti = profile.get("mbti", {})
        if mbti.get("type"):
            prompt_parts.append(f"用户的人格类型是MBTI-{mbti['type']}：{mbti.get('summary', '')}")

            # 根据MBTI调整沟通风格
            if mbti["type"].startswith("I"):
                prompt_parts.append("用户倾向于内向，可能需要更多独处时间和独立思考的空间。")
            elif mbti["type"].startswith("E"):
                prompt_parts.append("用户倾向于外向，喜欢交流和社交互动。")

            if mbti["type"][2] == "T":
                prompt_parts.append("用户决策时更注重逻辑和分析。")
            elif mbti["type"][2] == "F":
                prompt_parts.append("用户决策时更注重情感和人文因素。")

        # SBTI才干相关提示
        sbti = profile.get("sbti", {})
        if sbti.get("top_themes"):
            themes_str = "、".join(sbti["top_themes"])
            prompt_parts.append(f"用户的核心才干包括：{themes_str}。")

            # 获取才干详细信息
            for theme in sbti["top_themes"][:3]:
                theme_info = get_sbti_theme(theme)
                if theme_info:
                    comm_style = theme_info.get("communication", "")
                    if comm_style:
                        prompt_parts.append(f"关于'{theme}'才干：{comm_style}")

        # 依恋风格相关提示
        attachment = profile.get("attachment", {})
        if attachment.get("style"):
            style = attachment["style"]
            prompt_parts.append(f"用户的依恋风格是：{style}。")

            if attachment.get("communication_tips"):
                prompt_parts.append(f"沟通建议：{attachment['communication_tips']}")

        # 综合洞察
        integrated = profile.get("integrated", {})
        if integrated.get("combined_summary"):
            prompt_parts.append(f"综合洞察：{integrated['combined_summary']}")

        if prompt_parts:
            return "\n".join([
                "",
                "【用户画像参考】",
                *prompt_parts,
                "【提示】以上画像信息仅供参考，AI助手应根据用户的实际问题给出回应，不要直接套用理论。",
            ])

        return ""

    def get_context_for_rag(
        self,
        user: User,
        query: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取RAG增强上下文

        用于在RAG检索和生成时提供用户画像上下文

        Args:
            user: 用户对象
            query: 当前查询（可选，用于上下文增强）

        Returns:
            包含用户画像上下文字典
        """
        import asyncio

        # 在同步上下文中调用异步方法
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        profile = loop.run_until_complete(self.build_user_context(user))

        return {
            "profile": profile,
            "persona_prompt": self.get_persona_prompt(profile),
            "has_detailed_profile": profile.get("has_profile", False) and (
                profile.get("mbti", {}).get("type") or
                profile.get("sbti", {}).get("top_themes") or
                profile.get("attachment", {}).get("style")
            ),
        }


# 全局实例
_persona_builder: Optional[PersonaContextBuilder] = None


def get_persona_builder() -> PersonaContextBuilder:
    """获取上下文构建器实例"""
    global _persona_builder
    if _persona_builder is None:
        _persona_builder = PersonaContextBuilder()
    return _persona_builder
