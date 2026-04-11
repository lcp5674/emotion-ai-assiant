"""
RAG生成服务 - 结合检索结果生成回答
支持深度画像（MBTI + SBTI + 依恋风格）
"""
from typing import List, Dict, Any, Optional
import json
import loguru

from app.services.llm.factory import chat
from app.services.rag.retriever import get_retriever


class Generator:
    """RAG生成器"""

    def __init__(self):
        self.retriever = get_retriever()

    async def generate(
        self,
        query: str,
        user_mbti: Optional[str] = None,
        conversation_context: Optional[str] = None,
        assistant_info: Optional[Dict[str, Any]] = None,
        persona_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """生成回答

        Args:
            query: 用户问题
            user_mbti: 用户MBTI类型
            conversation_context: 对话上下文
            assistant_info: 助手信息
            persona_context: 用户画像上下文（MBTI+SBTI+依恋风格）

        Returns:
            生成的回答和引用
        """
        # 1. 检索相关知识
        docs = await self.retriever.retrieve_with_expand(
            query=query,
            user_mbti=user_mbti,
            conversation_context=conversation_context,
        )

        # 2. 构建增强上下文（包含画像信息）
        enhanced_context = self._build_enhanced_context(
            docs,
            user_mbti,
            persona_context
        )

        # 3. 构建提示词
        system_prompt = self._build_system_prompt(
            assistant_info,
            user_mbti,
            persona_context
        )
        user_prompt = self._build_user_prompt(
            query,
            enhanced_context,
            persona_context
        )

        # 4. 调用LLM生成
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            answer = await chat(messages, temperature=0.8, max_tokens=1500)
        except Exception as e:
            loguru.logger.error(f"LLM generate error: {e}")
            answer = "抱歉，我现在有点累，让我休息一下再和你聊天好吗？"

        # 5. 返回结果
        return {
            "answer": answer,
            "references": [
                {
                    "text": doc.get("text", "")[:200] + "...",
                    "category": doc.get("category", ""),
                }
                for doc in docs[:3]
            ],
            "has_reference": len(docs) > 0,
            "persona_context_used": persona_context.get("has_profile", False) if persona_context else False,
        }

    def _build_enhanced_context(
        self,
        docs: List[Dict[str, Any]],
        user_mbti: Optional[str],
        persona_context: Optional[Dict[str, Any]],
    ) -> str:
        """构建增强的上下文，包含画像知识"""
        context_parts = []

        # 添加检索到的知识
        if docs:
            context_parts.append("【相关知识】")
            for doc in docs[:3]:
                text = doc.get("text", "")[:500]
                category = doc.get("category", "")
                context_parts.append(f"[{category}] {text}")

        # 添加用户画像相关知识
        if persona_context and persona_context.get("has_profile"):
            profile_knowledge = self._get_profile_knowledge(persona_context)
            if profile_knowledge:
                context_parts.append("\n【用户画像相关知识】")
                context_parts.append(profile_knowledge)

        return "\n\n".join(context_parts)

    def _get_profile_knowledge(self, persona_context: Dict[str, Any]) -> str:
        """获取与画像相关的知识"""
        knowledge_parts = []

        # MBTI相关知识
        mbti = persona_context.get("mbti", {})
        if mbti.get("type"):
            mbti_type = mbti["type"]
            # 添加MBTI类型描述
            mbti_descriptions = {
                "INTJ": "INTJ型用户善于独立思考，有战略眼光，喜欢深入分析问题。他们需要时间和空间来处理信息，可能不善于表达情感。",
                "INTP": "INTP型用户逻辑性强，好奇心重，喜欢理论探讨。他们重视智力挑战，可能在情感表达上较为内敛。",
                "ENTJ": "ENTJ型用户果断有主见，喜欢掌控局面。他们善于规划和组织，但可能有时过于强势。",
                "ENTP": "ENTP型用户思维敏捷，善于辩论和创新。他们喜欢可能性，但可能难以坚持到底。",
                "INFJ": "INFJ型用户敏感而有洞察力，关注他人感受。他们有理想主义倾向，善于帮助他人。",
                "INFP": "INFP型用户理想主义，重视内心价值观。他们忠诚而敏感，善于理解他人。",
                "ENFJ": "ENFJ型用户热情有感染力，善于激励他人。他们关注他人成长，但可能过度在意他人看法。",
                "ENFP": "ENFP型用户热情洋溢，充满创意。他们喜欢可能性，但可能难以专注细节。",
                "ISTJ": "ISTJ型用户务实可靠，重视责任和承诺。他们做事有条理，但可能不善于变通。",
                "ISFJ": "ISFJ型用户温柔体贴，重视人际关系。他们善于照顾他人，但可能过度承担责任。",
                "ESTJ": "ESTJ型用户务实高效，重视组织和秩序。他们执行力强，但可能不够灵活。",
                "ESFJ": "ESFJ型用户热情友好，重视和谐。他们善于社交，但可能过于在意他人评价。",
                "ISTP": "ISTP型用户冷静务实，善于分析问题。他们动手能力强，但可能不善于表达情感。",
                "ISFP": "ISFP型用户敏感细腻，追求美感。他们活在当下，但可能回避冲突。",
                "ESTP": "ESTP型用户活跃实际，喜欢即时体验。他们善于应对当前问题，但可能缺乏长远规划。",
                "ESFP": "ESFP型用户活泼开朗，喜欢社交。他们活在当下，但可能难以忍受无聊。",
            }
            if mbti_type in mbti_descriptions:
                knowledge_parts.append(f"MBTI-{mbti_type}特征：{mbti_descriptions[mbti_type]}")

        # SBTI才干知识
        sbti = persona_context.get("sbti", {})
        if sbti.get("top_themes"):
            from app.services.rag.knowledge_data import get_sbti_theme
            themes = sbti["top_themes"][:3]
            knowledge_parts.append(f"用户的核心才干：{', '.join(themes)}")
            for theme in themes:
                theme_info = get_sbti_theme(theme)
                if theme_info:
                    knowledge_parts.append(
                        f"- {theme}才干：{theme_info.get('definition', '')} "
                        f"沟通特点：{theme_info.get('communication', '')}"
                    )

        # 依恋风格知识
        attachment = persona_context.get("attachment", {})
        if attachment.get("style"):
            from app.services.rag.knowledge_data import get_attachment_style
            style = attachment["style"]
            style_info = get_attachment_style(style)
            if style_info:
                knowledge_parts.append(
                    f"依恋风格-{style}："
                    f"特点包括{'、'.join(style_info.get('characteristics', [])[:3])}。"
                    f"沟通建议：{style_info.get('communication_tips', '')}"
                )

        # 综合洞察
        integrated = persona_context.get("integrated", {})
        if integrated.get("combined_summary"):
            knowledge_parts.append(f"综合洞察：{integrated['combined_summary']}")

        return "\n".join(knowledge_parts)

    def _build_system_prompt(
        self,
        assistant_info: Optional[Dict] = None,
        user_mbti: Optional[str] = None,
        persona_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """构建系统提示词"""
        base_prompt = """你是一个温暖、有同理心的AI情感助手"心灵伴侣"。你的职责是：
1. 倾听用户的情感和困惑
2. 提供情绪支持和心理疏导
3. 用专业但易懂的方式解释心理学知识
4. 给出积极、正向的建议

重要原则：
- 始终保持温暖、理解的语气
- 不评判、不批评用户
- 尊重用户的感受和选择
- 必要时建议寻求专业帮助
- 回答要简洁、有重点，不要过长"""

        # 添加助手个性化信息
        if assistant_info:
            personality = assistant_info.get("personality", "")
            speaking_style = assistant_info.get("speaking_style", "")
            if personality:
                base_prompt += f"\n\n你的性格特点：{personality}"
            if speaking_style:
                base_prompt += f"\n你的说话风格：{speaking_style}"

        # 添加用户MBTI信息
        if user_mbti:
            base_prompt += f"\n\n当前用户的MBTI类型是：{user_mbti}"

        # 添加深度画像提示（基于MBTI+SBTI+依恋风格）
        if persona_context and persona_context.get("has_profile"):
            persona_prompt = self._build_persona_prompt(persona_context)
            if persona_prompt:
                base_prompt += f"\n\n{persona_prompt}"

        return base_prompt

    def _build_persona_prompt(self, persona_context: Dict[str, Any]) -> str:
        """构建基于画像的提示"""
        prompt_parts = []

        mbti = persona_context.get("mbti", {})
        sbti = persona_context.get("sbti", {})
        attachment = persona_context.get("attachment", {})

        # MBTI类型调整
        if mbti.get("type"):
            mbti_type = mbti["type"]

            # 根据MBTI类型调整沟通风格
            if mbti_type[0] == "I":  # 内向型
                prompt_parts.append("- 用户倾向于内向，给他/她更多思考和回应的空间，不要催促。")
            elif mbti_type[0] == "E":  # 外向型
                prompt_parts.append("- 用户倾向于外向，可以适当多提问，引导他/她表达。")

            # 决策风格
            if mbti_type[2] == "T":  # 思维型
                prompt_parts.append("- 用户决策时更注重逻辑，可以适当提供分析和事实。")
            elif mbti_type[2] == "F":  # 情感型
                prompt_parts.append("- 用户决策时更注重情感和价值观，多关注他/她的感受。")

        # SBTI才干调整
        if sbti.get("top_themes"):
            themes = sbti["top_themes"][:2]
            prompt_parts.append(f"- 用户的核心才干：{', '.join(themes)}，沟通时可适当呼应这些特点。")

        # 依恋风格调整
        if attachment.get("style"):
            style = attachment["style"]
            if style == "焦虑型":
                prompt_parts.append("- 用户属于焦虑型依恋，需要给予更多的安全感和确认。")
            elif style == "回避型":
                prompt_parts.append("- 用户属于回避型依恋，需要尊重他/她的空间，避免过于逼迫。")
            elif style == "安全型":
                prompt_parts.append("- 用户属于安全型依恋，可以建立稳定温暖的互动关系。")

        if prompt_parts:
            return "【个性化沟通提示】\n" + "\n".join(prompt_parts)

        return ""

    def _build_user_prompt(
        self,
        query: str,
        enhanced_context: str,
        persona_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """构建用户提示词"""
        prompt_parts = []

        # 添加上下文
        if enhanced_context:
            prompt_parts.append(f"【上下文信息】\n{enhanced_context}\n")

        # 添加对话历史
        # 如果需要可以添加conversation_context

        # 添加用户问题
        prompt_parts.append(f"用户的问题是：{query}")

        # 添加画像引导（如果有详细画像）
        if persona_context and persona_context.get("has_profile"):
            guidance = self._get_response_guidance(persona_context)
            if guidance:
                prompt_parts.append(f"\n\n【回答引导】\n{guidance}")

        prompt_parts.append("\n\n请根据以上信息，用温暖理解的方式回答用户的问题。")

        return "\n".join(prompt_parts)

    def _get_response_guidance(self, persona_context: Dict[str, Any]) -> str:
        """获取回答引导建议"""
        guidance_parts = []

        # 根据MBTI给出回应建议
        mbti = persona_context.get("mbti", {})
        if mbti.get("type"):
            # 针对不同MBTI的回应风格建议
            mbti_guidance = {
                "INTJ": "回应风格建议：简洁直接，提供深度分析，但注意表达理解和支持。",
                "INTP": "回应风格建议：可以分享一些有趣的分析，但不要过于学术化。",
                "INFJ": "回应风格建议：温和深入，关注用户的内心世界，给予情感支持。",
                "INFP": "回应风格建议：关注价值观和意义，给予理解和认可。",
                "ENFJ": "回应风格建议：热情支持，鼓励用户表达，但不要过于主导对话。",
                "ENFP": "回应风格建议：灵活有趣，多提问引导，但帮助他/她聚焦。",
                "ISTJ": "回应风格建议：务实可靠，提供具体建议，尊重用户的责任感和可靠性。",
                "ISFJ": "回应风格建议：温和体贴，关注用户照顾他人的需求，提醒他/她也值得被照顾。",
                "ESTJ": "回应风格建议：务实直接，提供实际的解决方案。",
                "ESFJ": "回应风格建议：温暖友好，关注人际关系方面的困惑。",
            }
            if mbti["type"] in mbti_guidance:
                guidance_parts.append(mbti_guidance[mbti["type"]])

        # 根据依恋风格给出回应建议
        attachment = persona_context.get("attachment", {})
        if attachment.get("style"):
            attachment_guidance = {
                "焦虑型": "在回答中给予理解和确认，帮助用户感到被理解。",
                "回避型": "保持温和但不过于亲密的语调，尊重用户的边界。",
                "安全型": "建立稳定的支持关系，鼓励用户继续成长。",
                "混乱型": "提供稳定和清晰的回应，可能需要建议专业帮助。",
            }
            if attachment["style"] in attachment_guidance:
                guidance_parts.append(attachment_guidance[attachment["style"]])

        return " ".join(guidance_parts)


# 全局生成器实例
_generator: Optional[Generator] = None


def get_generator() -> Generator:
    """获取生成器实例"""
    global _generator
    if _generator is None:
        _generator = Generator()
    return _generator