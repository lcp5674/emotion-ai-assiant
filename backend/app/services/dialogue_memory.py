"""
对话记忆系统 - 支持对话记忆、话题追踪和实体关系抽取
"""
from typing import List, Dict, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import re
from collections import defaultdict
import loguru


class TopicCategory(Enum):
    """话题类别枚举"""
    GENERAL = "general"
    EMOTIONAL = "emotional"
    PROBLEM_SOLVING = "problem_solving"
    INFORMATION = "information"
    SOCIAL = "social"
    PERSONAL_GROWTH = "personal_growth"


@dataclass
class Entity:
    """实体数据结构"""
    name: str
    entity_type: str
    confidence: float
    mentions: List[str] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    first_mentioned: datetime = field(default_factory=datetime.now)
    last_mentioned: datetime = field(default_factory=datetime.now)


@dataclass
class Relation:
    """关系数据结构"""
    source_entity: str
    target_entity: str
    relation_type: str
    confidence: float
    context: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Topic:
    """话题数据结构"""
    topic_id: str
    name: str
    category: TopicCategory
    keywords: Set[str] = field(default_factory=set)
    start_time: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    message_count: int = 0
    is_active: bool = True
    related_topics: Set[str] = field(default_factory=set)


@dataclass
class DialogueTurn:
    """对话轮次数据结构"""
    turn_id: str
    role: str
    content: str
    timestamp: datetime
    entities: List[Entity] = field(default_factory=list)
    topic_id: Optional[str] = None
    sentiment: Optional[float] = None
    emotion: Optional[str] = None


class DialogueMemory:
    """对话记忆管理类"""

    def __init__(self, max_turns: int = 50, max_topics: int = 10):
        self.logger = loguru.logger
        self.max_turns = max_turns
        self.max_topics = max_topics
        
        self.turns: List[DialogueTurn] = []
        self.topics: Dict[str, Topic] = {}
        self.entities: Dict[str, Entity] = {}
        self.relations: List[Relation] = []
        self.current_topic_id: Optional[str] = None
        self.topic_history: List[str] = []

    def add_turn(self, role: str, content: str) -> DialogueTurn:
        """添加对话轮次
        
        Args:
            role: 角色 (user/assistant)
            content: 对话内容
        
        Returns:
            对话轮次对象
        """
        turn_id = f"turn_{len(self.turns)}"
        turn = DialogueTurn(
            turn_id=turn_id,
            role=role,
            content=content,
            timestamp=datetime.now()
        )
        
        turn.entities = self._extract_entities(content)
        turn.topic_id = self._identify_topic(content)
        turn.sentiment, turn.emotion = self._analyze_sentiment(content)
        
        self.turns.append(turn)
        
        if len(self.turns) > self.max_turns:
            self.turns = self.turns[-self.max_turns:]
        
        self._update_memory(turn)
        
        return turn

    def _extract_entities(self, content: str) -> List[Entity]:
        """从文本中提取实体
        
        Args:
            content: 文本内容
        
        Returns:
            实体列表
        """
        entities = []
        
        patterns = {
            "PERSON": r"([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)",
            "DATE": r"(\d{4}年\d{1,2}月\d{1,2}日|\d{1,2}月\d{1,2}日|今天|明天|后天|昨天|前天)",
            "TIME": r"(\d{1,2}:\d{2}(?::\d{2})?|上午|下午|晚上|早上)",
            "LOCATION": r"(北京|上海|广州|深圳|杭州|南京|成都|武汉|西安|重庆|天津)",
            "EMOTION": r"(开心|高兴|快乐|悲伤|难过|痛苦|愤怒|生气|焦虑|紧张|害怕|恐惧|平静|安心)"
        }
        
        for entity_type, pattern in patterns.items():
            matches = re.findall(pattern, content)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                if match and len(match) > 1:
                    entity = self._get_or_create_entity(match, entity_type)
                    entities.append(entity)
        
        return entities

    def _get_or_create_entity(self, name: str, entity_type: str) -> Entity:
        """获取或创建实体
        
        Args:
            name: 实体名称
            entity_type: 实体类型
        
        Returns:
            实体对象
        """
        key = f"{entity_type}:{name.lower()}"
        
        if key in self.entities:
            entity = self.entities[key]
            entity.last_mentioned = datetime.now()
            if name not in entity.mentions:
                entity.mentions.append(name)
        else:
            entity = Entity(
                name=name,
                entity_type=entity_type,
                confidence=0.8,
                mentions=[name],
                first_mentioned=datetime.now(),
                last_mentioned=datetime.now()
            )
            self.entities[key] = entity
        
        return entity

    def _identify_topic(self, content: str) -> Optional[str]:
        """识别话题
        
        Args:
            content: 文本内容
        
        Returns:
            话题ID
        """
        topic_keywords = {
            TopicCategory.EMOTIONAL: {"心情", "情绪", "感觉", "难过", "开心", "烦恼", "焦虑", "抑郁", "压力"},
            TopicCategory.PROBLEM_SOLVING: {"帮助", "解决", "办法", "建议", "怎么办", "如何", "怎么", "问题"},
            TopicCategory.INFORMATION: {"什么", "知道", "了解", "介绍", "告诉", "查询", "搜索", "资料"},
            TopicCategory.SOCIAL: {"朋友", "家人", "同事", "关系", "聊天", "交流"},
            TopicCategory.PERSONAL_GROWTH: {"学习", "成长", "进步", "目标", "提升", "改变", "习惯"}
        }
        
        content_lower = content.lower()
        matched_category = TopicCategory.GENERAL
        max_matches = 0
        
        for category, keywords in topic_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in content_lower)
            if matches > max_matches:
                max_matches = matches
                matched_category = category
        
        topic_name = self._generate_topic_name(content, matched_category)
        
        existing_topic = self._find_similar_topic(topic_name, content)
        
        if existing_topic:
            topic_id = existing_topic.topic_id
            existing_topic.last_updated = datetime.now()
            existing_topic.message_count += 1
        else:
            topic_id = f"topic_{len(self.topics)}"
            topic = Topic(
                topic_id=topic_id,
                name=topic_name,
                category=matched_category,
                keywords=self._extract_topic_keywords(content),
                start_time=datetime.now(),
                last_updated=datetime.now(),
                message_count=1
            )
            self.topics[topic_id] = topic
            
            if len(self.topics) > self.max_topics:
                oldest_topic = min(self.topics.values(), key=lambda t: t.last_updated)
                del self.topics[oldest_topic.topic_id]
        
        if self.current_topic_id and self.current_topic_id != topic_id:
            self._handle_topic_switch(self.current_topic_id, topic_id)
        
        self.current_topic_id = topic_id
        if topic_id not in self.topic_history:
            self.topic_history.append(topic_id)
        
        return topic_id

    def _generate_topic_name(self, content: str, category: TopicCategory) -> str:
        """生成话题名称
        
        Args:
            content: 文本内容
            category: 话题类别
        
        Returns:
            话题名称
        """
        max_length = 30
        if len(content) <= max_length:
            return content
        return content[:max_length] + "..."

    def _extract_topic_keywords(self, content: str) -> Set[str]:
        """提取话题关键词
        
        Args:
            content: 文本内容
        
        Returns:
            关键词集合
        """
        words = re.findall(r'[\w\u4e00-\u9fa5]+', content)
        stopwords = {"的", "了", "在", "是", "我", "你", "他", "她", "们", "有", "没", "不", "也", "就", "都", "和"}
        keywords = {word for word in words if len(word) >= 2 and word not in stopwords}
        return keywords

    def _find_similar_topic(self, topic_name: str, content: str) -> Optional[Topic]:
        """查找相似话题
        
        Args:
            topic_name: 话题名称
            content: 文本内容
        
        Returns:
            相似话题对象
        """
        content_keywords = self._extract_topic_keywords(content)
        
        for topic in self.topics.values():
            if not topic.is_active:
                continue
            
            overlap = len(topic.keywords & content_keywords)
            if overlap >= 2:
                return topic
        
        return None

    def _handle_topic_switch(self, old_topic_id: str, new_topic_id: str) -> None:
        """处理话题切换
        
        Args:
            old_topic_id: 旧话题ID
            new_topic_id: 新话题ID
        """
        if old_topic_id in self.topics and new_topic_id in self.topics:
            self.topics[old_topic_id].related_topics.add(new_topic_id)
            self.topics[new_topic_id].related_topics.add(old_topic_id)

    def _analyze_sentiment(self, content: str) -> Tuple[Optional[float], Optional[str]]:
        """分析情感
        
        Args:
            content: 文本内容
        
        Returns:
            (情感分数, 情感标签)
        """
        positive_words = {"开心", "高兴", "快乐", "幸福", "满意", "好", "棒", "优秀", "完美", "喜欢", "爱", "温暖", "安慰", "安心", "平静", "放松"}
        negative_words = {"难过", "悲伤", "痛苦", "难过", "烦恼", "焦虑", "紧张", "害怕", "恐惧", "愤怒", "生气", "讨厌", "坏", "差", "糟糕", "担心", "压力"}
        
        positive_count = sum(1 for word in positive_words if word in content)
        negative_count = sum(1 for word in negative_words if word in content)
        
        total = positive_count + negative_count
        if total == 0:
            return 0.0, "neutral"
        
        sentiment_score = (positive_count - negative_count) / total
        
        if sentiment_score > 0.3:
            emotion = "positive"
        elif sentiment_score < -0.3:
            emotion = "negative"
        else:
            emotion = "neutral"
        
        return sentiment_score, emotion

    def _update_memory(self, turn: DialogueTurn) -> None:
        """更新记忆
        
        Args:
            turn: 对话轮次
        """
        for entity in turn.entities:
            for existing_entity in turn.entities:
                if entity != existing_entity:
                    relation = self._extract_relation(turn.content, entity, existing_entity)
                    if relation:
                        self.relations.append(relation)

    def _extract_relation(self, content: str, entity1: Entity, entity2: Entity) -> Optional[Relation]:
        """提取实体关系
        
        Args:
            content: 文本内容
            entity1: 实体1
            entity2: 实体2
        
        Returns:
            关系对象
        """
        relation_patterns = {
            "is": ["是", "就是", "属于"],
            "has": ["有", "拥有", "具备"],
            "likes": ["喜欢", "爱", "感兴趣"],
            "dislikes": ["讨厌", "不喜欢", "厌恶"],
            "talk_about": ["说", "提到", "谈论"],
            "related_to": ["和", "与", "跟", "一起"]
        }
        
        for rel_type, patterns in relation_patterns.items():
            for pattern in patterns:
                if pattern in content:
                    return Relation(
                        source_entity=entity1.name,
                        target_entity=entity2.name,
                        relation_type=rel_type,
                        confidence=0.7,
                        context=content,
                        timestamp=datetime.now()
                    )
        
        return None

    def get_recent_turns(self, n: int = 10) -> List[DialogueTurn]:
        """获取最近的n轮对话
        
        Args:
            n: 轮次数量
        
        Returns:
            对话轮次列表
        """
        return self.turns[-n:]

    def get_current_topic(self) -> Optional[Topic]:
        """获取当前话题
        
        Returns:
            话题对象
        """
        if self.current_topic_id and self.current_topic_id in self.topics:
            return self.topics[self.current_topic_id]
        return None

    def get_topic_history(self) -> List[Topic]:
        """获取话题历史
        
        Returns:
            话题列表
        """
        return [self.topics[topic_id] for topic_id in self.topic_history if topic_id in self.topics]

    def get_entities(self) -> List[Entity]:
        """获取所有实体
        
        Returns:
            实体列表
        """
        return list(self.entities.values())

    def get_relations(self) -> List[Relation]:
        """获取所有关系
        
        Returns:
            关系列表
        """
        return self.relations

    def get_context_summary(self, max_turns: int = 10) -> str:
        """获取上下文摘要
        
        Args:
            max_turns: 最大轮次数
        
        Returns:
            上下文摘要字符串
        """
        recent_turns = self.get_recent_turns(max_turns)
        current_topic = self.get_current_topic()
        
        summary_parts = []
        
        if recent_turns:
            summary_parts.append("最近对话:")
            for turn in recent_turns:
                role_label = "用户" if turn.role == "user" else "AI"
                summary_parts.append(f"{role_label}: {turn.content}")
        
        if current_topic:
            summary_parts.append(f"\n当前话题: {current_topic.name}")
        
        if self.entities:
            summary_parts.append("\n相关实体:")
            for entity in list(self.entities.values())[:5]:
                summary_parts.append(f"- {entity.name} ({entity.entity_type})")
        
        return "\n".join(summary_parts)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典
        
        Returns:
            字典表示
        """
        return {
            "turns": [
                {
                    "turn_id": turn.turn_id,
                    "role": turn.role,
                    "content": turn.content,
                    "timestamp": turn.timestamp.isoformat(),
                    "entities": [
                    {
                        "name": e.name,
                        "type": e.entity_type,
                        "confidence": e.confidence
                    } for e in turn.entities
                ],
                "topic_id": turn.topic_id,
                "sentiment": turn.sentiment,
                "emotion": turn.emotion
            } for turn in self.turns
        ],
        "topics": [
            {
                "topic_id": topic.topic_id,
                "name": topic.name,
                "category": topic.category.value,
                "message_count": topic.message_count
            } for topic in self.topics.values()
        ],
        "entities": [
            {
                "name": entity.name,
                "type": entity.entity_type,
                "mentions": entity.mentions
            } for entity in self.entities.values()
        ],
        "current_topic_id": self.current_topic_id
    }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DialogueMemory':
        """从字典创建对象
        
        Args:
            data: 字典数据
        
        Returns:
            DialogueMemory对象
        """
        memory = cls()
        
        for turn_data in data.get("turns", []):
            turn = DialogueTurn(
                turn_id=turn_data["turn_id"],
                role=turn_data["role"],
                content=turn_data["content"],
                timestamp=datetime.fromisoformat(turn_data["timestamp"]),
                topic_id=turn_data.get("topic_id"),
                sentiment=turn_data.get("sentiment"),
                emotion=turn_data.get("emotion")
            )
            memory.turns.append(turn)
        
        memory.current_topic_id = data.get("current_topic_id")
        
        return memory


class DialogueMemoryManager:
    """对话记忆管理器 - 管理多个用户的对话记忆"""

    def __init__(self):
        self.logger = loguru.logger
        self.user_memories: Dict[int, DialogueMemory] = {}
        self.expiration_hours = 24

    def get_memory(self, user_id: int) -> DialogueMemory:
        """获取用户的对话记忆
        
        Args:
            user_id: 用户ID
        
        Returns:
            对话记忆对象
        """
        if user_id not in self.user_memories:
            self.user_memories[user_id] = DialogueMemory()
        return self.user_memories[user_id]

    def clear_memory(self, user_id: int) -> None:
        """清除用户的对话记忆
        
        Args:
            user_id: 用户ID
        """
        if user_id in self.user_memories:
            del self.user_memories[user_id]

    def cleanup_expired(self) -> None:
        """清理过期的对话记忆"""
        now = datetime.now()
        expired_users = []
        
        for user_id, memory in self.user_memories.items():
            if memory.turns:
                last_turn = memory.turns[-1]
                if now - last_turn.timestamp > timedelta(hours=self.expiration_hours):
                    expired_users.append(user_id)
        
        for user_id in expired_users:
            self.clear_memory(user_id)
            self.logger.info(f"Cleared expired memory for user {user_id}")


_memory_manager: Optional[DialogueMemoryManager] = None


def get_memory_manager() -> DialogueMemoryManager:
    """获取对话记忆管理器实例
    
    Returns:
        DialogueMemoryManager对象
    """
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = DialogueMemoryManager()
    return _memory_manager
