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
from app.models.memory_graph import KnowledgeGraph
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
)
from app.models.enterprise import (
    Enterprise,
    EnterpriseUser,
    EnterpriseCompliance,
    EnterpriseAuditLog,
    EnterpriseStatus,
    EnterpriseUserRole,
)
from app.models.recommendation import (
    ContentType,
    RecommendationReason,
    UserContentInteraction,
    UserContentPreference,
    ContentTag,
    ContentTagRelation,
    RecommendationHistory,
)
from app.models.feedback import (
    FeedbackType,
    FeedbackStatus,
    MessageFeedback,
    AssistantFeedback,
    AppFeedback,
    UserGrowthGoal,
    GrowthMilestone,
    AIAdviceHistory,
    UserReflection,
)
from app.models.user_login import UserLogin
from app.models.user_profile import UserProfile

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
    "KnowledgeGraph",
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
    # enterprise
    "Enterprise",
    "EnterpriseUser",
    "EnterpriseCompliance",
    "EnterpriseAuditLog",
    "EnterpriseStatus",
    "EnterpriseUserRole",
    # recommendation
    "ContentType",
    "RecommendationReason",
    "UserContentInteraction",
    "UserContentPreference",
    "ContentTag",
    "ContentTagRelation",
    "RecommendationHistory",
    # feedback
    "FeedbackType",
    "FeedbackStatus",
    "MessageFeedback",
    "AssistantFeedback",
    "AppFeedback",
    "UserGrowthGoal",
    "GrowthMilestone",
    "AIAdviceHistory",
    "UserReflection",
    # user
    "UserLogin",
    "UserProfile",
]