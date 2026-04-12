"""
数据模型包
"""
from app.models.user import User, MemberLevel
from app.models.mbti import MbtiQuestion, MbtiAnswer, MbtiResult, AiAssistant, MbtiDimension, MbtiType
from app.models.chat import Conversation, Message, MessageCollection, MessageType, ConversationStatus
from app.models.knowledge import (
    KnowledgeArticle,
    ArticleCollection,
    Banner,
    Announcement,
    MemberOrder,
    ArticleStatus,
    ArticleCategory,
)
from app.models.system import SystemConfig
from app.models.diary import EmotionDiary, MoodRecord, DiaryTag, MoodLevel, EmotionType
from app.models.user_memory import UserLongTermMemory, UserMemoryInsight, UserPreference, MemoryType, MemoryImportance
from app.models.content_audit import ContentAuditQueue
from app.models.growth import Badge, UserBadge, UserLevel, ExpRecord, GrowthTask, BadgeRarity
from app.models.personality import (
    AttachmentStyle,
    SBTIQuestion,
    SBTIAnswer,
    SBTIResult,
    AttachmentQuestion,
    AttachmentAnswer,
    AttachmentResult,
    DeepPersonaProfile,
    PersonaInsight,
    PersonaTrend,
    DynamicPersonaTag,
    PersonaBehaviorPattern,
    PsychologicalNeed,
    IntegratedPersonaStrategy,
)
from app.models.permission import Role, Permission, PermissionAction, ResourceType
from app.models.analytics import UserActivity, AnalyticsMetric, UserBehavior, EventType
from app.models.support import SupportTicket, TicketMessage, ChatbotConversation, ChatbotMessage, TicketStatus, TicketPriority

__all__ = [
    "User",
    "MemberLevel",
    "MbtiQuestion",
    "MbtiAnswer",
    "MbtiResult",
    "AiAssistant",
    "MbtiDimension",
    "MbtiType",
    "Conversation",
    "Message",
    "MessageCollection",
    "MessageType",
    "ConversationStatus",
    "KnowledgeArticle",
    "ArticleCollection",
    "Banner",
    "Announcement",
    "MemberOrder",
    "ArticleStatus",
    "ArticleCategory",
    "SystemConfig",
    "EmotionDiary",
    "MoodRecord",
    "DiaryTag",
    "MoodLevel",
    "EmotionType",
    "UserLongTermMemory",
    "UserMemoryInsight",
    "UserPreference",
    "MemoryType",
    "MemoryImportance",
    "ContentAuditQueue",
    "Badge",
    "UserBadge",
    "UserLevel",
    "ExpRecord",
    "GrowthTask",
    "BadgeRarity",
    # SBTI和依恋风格模型
    "AttachmentStyle",
    "SBTIQuestion",
    "SBTIAnswer",
    "SBTIResult",
    "AttachmentQuestion",
    "AttachmentAnswer",
    "AttachmentResult",
    "DeepPersonaProfile",
    "PersonaInsight",
    "PersonaTrend",
    "DynamicPersonaTag",
    "PersonaBehaviorPattern",
    "PsychologicalNeed",
    "IntegratedPersonaStrategy",
    # 权限管理模型
    "Role",
    "Permission",
    "PermissionAction",
    "ResourceType",
    # 数据分析模型
    "UserActivity",
    "AnalyticsMetric",
    "UserBehavior",
    "EventType",
    # 客服系统模型
    "SupportTicket",
    "TicketMessage",
    "ChatbotConversation",
    "ChatbotMessage",
    "TicketStatus",
    "TicketPriority",
]