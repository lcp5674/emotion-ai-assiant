"""
增强版智能客服服务 - 集成深度上下文理解、个性化对话风格和对话质量提升
"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import uuid
import re

from app.models.support import ChatbotConversation, ChatbotMessage
from app.models.user import User
from app.services.llm.factory import get_llm_provider
from app.core.config import settings
from app.services.dialogue_memory import (
    DialogueMemory,
    DialogueMemoryManager,
    get_memory_manager,
    TopicCategory
)
from app.services.persona_context_builder import (
    PersonaContextBuilder,
    get_persona_builder
)
import loguru


class CredibilityScorer:
    """回答可信度评分器"""

    @staticmethod
    def score_response(content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """评估回答的可信度
        
        Args:
            content: 回答内容
            context: 上下文信息
        
        Returns:
            可信度评分结果
        """
        scores = {
            "overall": 0.0,
            "clarity": 0.0,
            "relevance": 0.0,
            "completeness": 0.0,
            "reasoning": 0.0
        }
        
        content_lower = content.lower()
        
        clarity_score = CredibilityScorer._assess_clarity(content)
        scores["clarity"] = clarity_score
        
        relevance_score = CredibilityScorer._assess_relevance(content, context)
        scores["relevance"] = relevance_score
        
        completeness_score = CredibilityScorer._assess_completeness(content)
        scores["completeness"] = completeness_score
        
        reasoning_score = CredibilityScorer._assess_reasoning(content)
        scores["reasoning"] = reasoning_score
        
        scores["overall"] = (
            clarity_score * 0.25 +
            relevance_score * 0.30 +
            completeness_score * 0.20 +
            reasoning_score * 0.25
        )
        
        return scores

    @staticmethod
    def _assess_clarity(content: str) -> float:
        """评估清晰度"""
        score = 0.5
        
        if len(content) > 20:
            score += 0.1
        
        ambiguous_phrases = ["可能", "大概", "也许", "好像", "不确定", "不太清楚"]
        ambiguous_count = sum(1 for phrase in ambiguous_phrases if phrase in content)
        if ambiguous_count == 0:
            score += 0.2
        else:
            score -= ambiguous_count * 0.05
        
        definite_phrases = ["是的", "当然", "确实", "肯定", "一定", "明确"]
        definite_count = sum(1 for phrase in definite_phrases if phrase in content)
        score += min(definite_count * 0.05, 0.2)
        
        return min(max(score, 0.0), 1.0)

    @staticmethod
    def _assess_relevance(content: str, context: Dict[str, Any]) -> float:
        """评估相关性"""
        score = 0.5
        
        user_query = context.get("user_query", "")
        if user_query:
            query_keywords = set(re.findall(r'[\w\u4e00-\u9fa5]+', user_query.lower()))
            content_keywords = set(re.findall(r'[\w\u4e00-\u9fa5]+', content.lower()))
            overlap = len(query_keywords & content_keywords)
            if overlap > 0:
                score += min(overlap * 0.1, 0.4)
        
        return min(max(score, 0.0), 1.0)

    @staticmethod
    def _assess_completeness(content: str) -> float:
        """评估完整性"""
        score = 0.5
        
        sentence_count = content.count('。') + content.count('！') + content.count('？')
        if sentence_count >= 2:
            score += 0.2
        elif sentence_count == 1:
            score += 0.1
        
        detail_indicators = ["具体", "详细", "包括", "例如", "比如"]
        detail_count = sum(1 for indicator in detail_indicators if indicator in content)
        score += min(detail_count * 0.1, 0.3)
        
        return min(max(score, 0.0), 1.0)

    @staticmethod
    def _assess_reasoning(content: str) -> float:
        """评估推理性"""
        score = 0.5
        
        reasoning_indicators = ["因此", "所以", "因为", "由于", "基于", "根据"]
        reasoning_count = sum(1 for indicator in reasoning_indicators if indicator in content)
        score += min(reasoning_count * 0.1, 0.3)
        
        step_indicators = ["首先", "其次", "然后", "最后", "第一", "第二"]
        step_count = sum(1 for indicator in step_indicators if indicator in content)
        score += min(step_count * 0.1, 0.2)
        
        return min(max(score, 0.0), 1.0)


class DialogueFlowOptimizer:
    """对话流畅度优化器"""

    @staticmethod
    def optimize_response(
        response: str,
        memory: DialogueMemory,
        persona_context: Dict[str, Any]
    ) -> str:
        """优化回复的流畅度
        
        Args:
            response: 原始回复
            memory: 对话记忆
            persona_context: 人格画像上下文
        
        Returns:
            优化后的回复
        """
        optimized = response
        
        optimized = DialogueFlowOptimizer._add_coherence_markers(optimized, memory)
        optimized = DialogueFlowOptimizer._adjust_to_persona(optimized, persona_context)
        optimized = DialogueFlowOptimizer._ensure_natural_flow(optimized)
        
        return optimized

    @staticmethod
    def _add_coherence_markers(response: str, memory: DialogueMemory) -> str:
        """添加连贯标记"""
        current_topic = memory.get_current_topic()
        
        if current_topic and current_topic.message_count > 1:
            if current_topic.category == TopicCategory.EMOTIONAL:
                if "我理解" not in response and "我明白" not in response:
                    return "我理解你的感受。" + response
            elif current_topic.category == TopicCategory.PROBLEM_SOLVING:
                if "让我们" not in response and "我们可以" not in response:
                    if len(response) > 50:
                        return "让我们一起来看看这个问题。" + response
        
        return response

    @staticmethod
    def _adjust_to_persona(response: str, persona_context: Dict[str, Any]) -> str:
        """根据人格画像调整"""
        mbti = persona_context.get("mbti", {})
        mbti_type = mbti.get("type", "")
        
        if mbti_type:
            if mbti_type.startswith("F"):
                empathetic_phrases = ["我理解", "我明白", "我能感受到", "这确实"]
                has_empathetic = any(phrase in response for phrase in empathetic_phrases)
                if not has_empathetic and len(response) > 20:
                    response = "我理解你的想法。" + response
            elif mbti_type.startswith("T"):
                structured_indicators = ["具体来说", "详细来讲", "总结一下"]
                has_structured = any(indicator in response for indicator in structured_indicators)
                if not has_structured and len(response) > 100:
                    response += " 总结一下：" + response[:50] + "..."
        
        return response

    @staticmethod
    def _ensure_natural_flow(response: str) -> str:
        """确保自然流畅"""
        response = re.sub(r'[。！？]{2,}', lambda m: m.group(0)[0], response)
        response = re.sub(r'，，+', '，', response)
        
        if response and not response[-1] in '。！？':
            response += '。'
        
        return response


class EmotionalResponseGenerator:
    """情感化回复生成器"""

    EMOTIONAL_PATTERNS = {
        "positive": [
            "太好了！",
            "真为你高兴！",
            "这是个好消息！",
            "太棒了！",
            "真开心听到这个！"
        ],
        "negative": [
            "我很抱歉听到这个。",
            "这确实很难过。",
            "我理解你的痛苦。",
            "请给自己一些时间。",
            "你并不孤单。"
        ],
        "neutral": [
            "我明白了。",
            "好的，我理解了。",
            "谢谢你告诉我这些。"
        ]
    }

    @staticmethod
    def generate_emotional_prefix(emotion: str, sentiment: Optional[float] = None) -> str:
        """生成情感前缀
        
        Args:
            emotion: 情感标签
            sentiment: 情感分数
        
        Returns:
            情感前缀
        """
        import random
        
        if emotion == "positive":
            return random.choice(EmotionalResponseGenerator.EMOTIONAL_PATTERNS["positive"])
        elif emotion == "negative":
            return random.choice(EmotionalResponseGenerator.EMOTIONAL_PATTERNS["negative"])
        else:
            return random.choice(EmotionalResponseGenerator.EMOTIONAL_PATTERNS["neutral"])

    @staticmethod
    def enhance_with_emotion(
        response: str,
        user_emotion: str,
        user_sentiment: Optional[float] = None
    ) -> str:
        """用情感增强回复
        
        Args:
            response: 原始回复
            user_emotion: 用户情感
            user_sentiment: 用户情感分数
        
        Returns:
            情感增强后的回复
        """
        if user_emotion in ["positive", "negative"]:
            prefix = EmotionalResponseGenerator.generate_emotional_prefix(user_emotion, user_sentiment)
            if prefix not in response:
                response = prefix + " " + response
        
        return response


class ChatbotServiceEnhanced:
    """增强版智能客服服务"""

    def __init__(self):
        self.logger = loguru.logger
        self.memory_manager = get_memory_manager()
        self.persona_builder = get_persona_builder()
        self.credibility_scorer = CredibilityScorer()
        self.flow_optimizer = DialogueFlowOptimizer()
        self.emotional_generator = EmotionalResponseGenerator()

    @staticmethod
    def create_conversation(db: Session, user_id: int) -> ChatbotConversation:
        """创建智能客服对话"""
        session_id = str(uuid.uuid4())
        conversation = ChatbotConversation(
            user_id=user_id,
            session_id=session_id
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation

    @staticmethod
    def get_conversation(db: Session, conversation_id: int, user_id: int) -> Optional[ChatbotConversation]:
        """获取对话"""
        return db.query(ChatbotConversation).filter(
            ChatbotConversation.id == conversation_id,
            ChatbotConversation.user_id == user_id
        ).first()

    @staticmethod
    def get_user_conversations(db: Session, user_id: int, limit: int = 100) -> List[ChatbotConversation]:
        """获取用户的对话列表"""
        return db.query(ChatbotConversation).filter(
            ChatbotConversation.user_id == user_id
        ).order_by(ChatbotConversation.created_at.desc()).limit(limit).all()

    @staticmethod
    def end_conversation(db: Session, conversation_id: int, user_id: int) -> Optional[ChatbotConversation]:
        """结束对话"""
        conversation = ChatbotServiceEnhanced.get_conversation(db, conversation_id, user_id)
        if conversation and conversation.status:
            conversation.status = False
            conversation.ended_at = datetime.now()
            db.commit()
            db.refresh(conversation)
        return conversation

    async def send_message(
        self,
        db: Session,
        conversation_id: int,
        user_id: int,
        content: str,
        message_type: str = "text",
        user: Optional[User] = None
    ) -> Dict[str, Any]:
        """发送消息并获取AI增强回复
        
        Args:
            db: 数据库会话
            conversation_id: 对话ID
            user_id: 用户ID
            content: 消息内容
            message_type: 消息类型
            user: 用户对象（可选，用于人格画像）
        
        Returns:
            包含用户消息、AI消息和增强信息的字典
        """
        conversation = ChatbotServiceEnhanced.get_conversation(db, conversation_id, user_id)
        if not conversation:
            raise ValueError("对话不存在")
        
        if not conversation.status:
            raise ValueError("对话已结束")
        
        memory = self.memory_manager.get_memory(user_id)
        user_turn = memory.add_turn("user", content)
        
        persona_context = {}
        if user:
            persona_context = await self.persona_builder.build_user_context(user)
        
        user_message = ChatbotMessage(
            conversation_id=conversation_id,
            sender_type="user",
            content=content,
            message_type=message_type
        )
        db.add(user_message)
        
        ai_response, enhancement_data = await self.generate_enhanced_ai_response(
            db=db,
            conversation=conversation,
            user_message=content,
            memory=memory,
            persona_context=persona_context,
            user=user
        )
        
        bot_message = ChatbotMessage(
            conversation_id=conversation_id,
            sender_type="bot",
            content=ai_response,
            message_type="text"
        )
        db.add(bot_message)
        
        memory.add_turn("assistant", ai_response)
        
        db.commit()
        db.refresh(bot_message)
        
        return {
            "user_message": user_message,
            "bot_message": bot_message,
            "enhancement_data": enhancement_data
        }

    async def generate_enhanced_ai_response(
        self,
        db: Session,
        conversation: ChatbotConversation,
        user_message: str,
        memory: DialogueMemory,
        persona_context: Dict[str, Any],
        user: Optional[User] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """生成增强的AI回复
        
        Args:
            db: 数据库会话
            conversation: 对话对象
            user_message: 用户消息
            memory: 对话记忆
            persona_context: 人格画像上下文
            user: 用户对象
        
        Returns:
            (增强的回复, 增强数据)
        """
        history_messages = db.query(ChatbotMessage).filter(
            ChatbotMessage.conversation_id == conversation.id
        ).order_by(ChatbotMessage.created_at).all()
        
        history = []
        for msg in history_messages:
            role = "user" if msg.sender_type == "user" else "assistant"
            history.append({
                "role": role,
                "content": msg.content
            })
        
        history.append({
            "role": "user",
            "content": user_message
        })
        
        system_prompt = self._build_enhanced_system_prompt(memory, persona_context)
        
        try:
            llm = get_llm_provider()
            raw_response = await llm.chat(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    }
                ] + history,
                temperature=0.7,
                max_tokens=1000
            )
            
            enhancement_data = self._apply_enhancements(
                raw_response=raw_response,
                user_message=user_message,
                memory=memory,
                persona_context=persona_context
            )
            
            return enhancement_data["final_response"], enhancement_data
            
        except Exception as e:
            self.logger.error(f"Error generating enhanced response: {e}")
            fallback_response = "感谢您的咨询，我会尽力帮助您。"
            return fallback_response, {
                "final_response": fallback_response,
                "raw_response": fallback_response,
                "error": str(e)
            }

    def _build_enhanced_system_prompt(
        self,
        memory: DialogueMemory,
        persona_context: Dict[str, Any]
    ) -> str:
        """构建增强的系统提示
        
        Args:
            memory: 对话记忆
            persona_context: 人格画像上下文
        
        Returns:
            系统提示字符串
        """
        prompt_parts = [
            "你是一个智能、贴心的AI助手，负责回答用户的问题，提供帮助和支持。"
        ]
        
        context_summary = memory.get_context_summary(max_turns=5)
        if context_summary:
            prompt_parts.append("\n【对话上下文】")
            prompt_parts.append(context_summary)
        
        persona_prompt = self.persona_builder.get_persona_prompt(persona_context)
        if persona_prompt:
            prompt_parts.append(persona_prompt)
        
        current_topic = memory.get_current_topic()
        if current_topic:
            prompt_parts.append(f"\n当前对话话题类别：{current_topic.category.value}")
            if current_topic.category == TopicCategory.EMOTIONAL:
                prompt_parts.append("请给予情感支持和共情。")
            elif current_topic.category == TopicCategory.PROBLEM_SOLVING:
                prompt_parts.append("请提供实用的建议和解决方案。")
        
        prompt_parts.append("\n请保持友好、专业的语气，根据用户的情况提供个性化的回应。")
        
        return "\n".join(prompt_parts)

    def _apply_enhancements(
        self,
        raw_response: str,
        user_message: str,
        memory: DialogueMemory,
        persona_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """应用所有增强
        
        Args:
            raw_response: 原始回复
            user_message: 用户消息
            memory: 对话记忆
            persona_context: 人格画像上下文
        
        Returns:
            增强数据字典
        """
        enhancement_data = {
            "raw_response": raw_response,
            "final_response": raw_response,
            "credibility_score": None,
            "flow_optimization": None,
            "emotion_enhancement": None,
            "topic_info": None,
            "entities_extracted": []
        }
        
        current_topic = memory.get_current_topic()
        if current_topic:
            enhancement_data["topic_info"] = {
                "topic_id": current_topic.topic_id,
                "topic_name": current_topic.name,
                "category": current_topic.category.value
            }
        
        entities = memory.get_entities()
        enhancement_data["entities_extracted"] = [
            {"name": e.name, "type": e.entity_type} for e in entities
        ]
        
        recent_turns = memory.get_recent_turns(1)
        user_emotion = "neutral"
        user_sentiment = 0.0
        if recent_turns:
            user_emotion = recent_turns[-1].emotion or "neutral"
            user_sentiment = recent_turns[-1].sentiment or 0.0
        
        emotion_enhanced = self.emotional_generator.enhance_with_emotion(
            raw_response,
            user_emotion,
            user_sentiment
        )
        enhancement_data["emotion_enhancement"] = {
            "applied": emotion_enhanced != raw_response,
            "user_emotion": user_emotion,
            "user_sentiment": user_sentiment
        }
        
        flow_optimized = self.flow_optimizer.optimize_response(
            emotion_enhanced,
            memory,
            persona_context
        )
        enhancement_data["flow_optimization"] = {
            "applied": flow_optimized != emotion_enhanced
        }
        
        credibility_context = {"user_query": user_message}
        credibility_score = self.credibility_scorer.score_response(
            flow_optimized,
            credibility_context
        )
        enhancement_data["credibility_score"] = credibility_score
        
        enhancement_data["final_response"] = flow_optimized
        
        return enhancement_data

    @staticmethod
    def get_conversation_messages(
        db: Session,
        conversation_id: int,
        user_id: int
    ) -> List[ChatbotMessage]:
        """获取对话消息"""
        conversation = ChatbotServiceEnhanced.get_conversation(db, conversation_id, user_id)
        if not conversation:
            raise ValueError("对话不存在")
        
        return db.query(ChatbotMessage).filter(
            ChatbotMessage.conversation_id == conversation_id
        ).order_by(ChatbotMessage.created_at).all()

    def get_enhanced_context(
        self,
        user_id: int,
        user: Optional[User] = None
    ) -> Dict[str, Any]:
        """获取增强的上下文信息
        
        Args:
            user_id: 用户ID
            user: 用户对象
        
        Returns:
            增强上下文字典
        """
        memory = self.memory_manager.get_memory(user_id)
        
        persona_context = {}
        if user:
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            persona_context = loop.run_until_complete(self.persona_builder.build_user_context(user))
        
        current_topic = memory.get_current_topic()
        topic_history = memory.get_topic_history()
        
        return {
            "dialogue_memory": memory.to_dict(),
            "persona_context": persona_context,
            "current_topic": {
                "id": current_topic.topic_id,
                "name": current_topic.name,
                "category": current_topic.category.value
            } if current_topic else None,
            "topic_history": [
                {
                    "id": topic.topic_id,
                    "name": topic.name,
                    "category": topic.category.value
                } for topic in topic_history
            ],
            "recent_sentiment": memory.turns[-1].sentiment if memory.turns else None
        }


_chatbot_service_enhanced: Optional[ChatbotServiceEnhanced] = None


def get_chatbot_service_enhanced() -> ChatbotServiceEnhanced:
    """获取增强版智能客服服务实例
    
    Returns:
        ChatbotServiceEnhanced对象
    """
    global _chatbot_service_enhanced
    if _chatbot_service_enhanced is None:
        _chatbot_service_enhanced = ChatbotServiceEnhanced()
    return _chatbot_service_enhanced
