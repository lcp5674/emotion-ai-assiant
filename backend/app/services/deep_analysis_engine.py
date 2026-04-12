"""
深度人格分析引擎
实现人格特质与行为模式关联分析和潜在心理需求挖掘
"""
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta
import json
import loguru

from app.models import (
    User,
    MbtiResult,
    SBTIResult,
    AttachmentResult,
    UserActivity,
    UserBehavior,
    EmotionDiary,
    Message,
    PersonaBehaviorPattern,
    PsychologicalNeed,
    DynamicPersonaTag,
)


class DeepAnalysisEngine:
    """深度人格分析引擎"""

    def __init__(self, db: Session):
        self.db = db
        self.logger = loguru.logger

    async def analyze_personality_behavior_correlation(
        self,
        user_id: int,
        days: int = 90
    ) -> List[Dict[str, Any]]:
        """
        分析人格特质与行为模式的关联

        Args:
            user_id: 用户ID
            days: 分析历史天数

        Returns:
            关联分析结果列表
        """
        self.logger.info(f"Starting personality-behavior correlation analysis for user {user_id}")

        results = []

        try:
            mbti_result = self._get_latest_mbti_result(user_id)
            sbti_result = self._get_latest_sbti_result(user_id)
            attachment_result = self._get_latest_attachment_result(user_id)

            behavior_data = await self._collect_behavior_data(user_id, days)

            if mbti_result:
                mbti_correlations = await self._analyze_mbti_behavior_correlation(
                    mbti_result, behavior_data
                )
                results.extend(mbti_correlations)

            if sbti_result:
                sbti_correlations = await self._analyze_sbti_behavior_correlation(
                    sbti_result, behavior_data
                )
                results.extend(sbti_correlations)

            if attachment_result:
                attachment_correlations = await self._analyze_attachment_behavior_correlation(
                    attachment_result, behavior_data
                )
                results.extend(attachment_correlations)

            await self._save_behavior_patterns(user_id, results)

        except Exception as e:
            self.logger.error(f"Error in correlation analysis: {e}")

        return results

    async def mine_psychological_needs(
        self,
        user_id: int,
        days: int = 180
    ) -> List[Dict[str, Any]]:
        """
        挖掘潜在心理需求

        Args:
            user_id: 用户ID
            days: 分析历史天数

        Returns:
            心理需求分析结果列表
        """
        self.logger.info(f"Mining psychological needs for user {user_id}")

        needs = []

        try:
            data_sources = await self._collect_need_evidence(user_id, days)

            need_categories = {
                "autonomy": self._analyze_autonomy_need,
                "competence": self._analyze_competence_need,
                "relatedness": self._analyze_relatedness_need,
                "security": self._analyze_security_need,
                "growth": self._analyze_growth_need,
                "recognition": self._analyze_recognition_need,
            }

            for category, analyzer in need_categories.items():
                need = await analyzer(data_sources, user_id)
                if need:
                    needs.append(need)

            await self._save_psychological_needs(user_id, needs)

        except Exception as e:
            self.logger.error(f"Error in need mining: {e}")

        return needs

    async def extract_dynamic_tags(
        self,
        user_id: int,
        source_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        提取动态画像标签

        Args:
            user_id: 用户ID
            source_type: 标签来源类型

        Returns:
            动态标签列表
        """
        self.logger.info(f"Extracting dynamic tags for user {user_id}")

        tags = []

        try:
            if not source_type or source_type == "chat":
                chat_tags = await self._extract_tags_from_chat(user_id)
                tags.extend(chat_tags)

            if not source_type or source_type == "diary":
                diary_tags = await self._extract_tags_from_diary(user_id)
                tags.extend(diary_tags)

            if not source_type or source_type == "behavior":
                behavior_tags = await self._extract_tags_from_behavior(user_id)
                tags.extend(behavior_tags)

            await self._save_dynamic_tags(user_id, tags)

        except Exception as e:
            self.logger.error(f"Error in tag extraction: {e}")

        return tags

    def _get_latest_mbti_result(self, user_id: int) -> Optional[MbtiResult]:
        """获取最新的MBTI结果"""
        return self.db.query(MbtiResult).filter(
            MbtiResult.user_id == user_id,
            MbtiResult.is_latest == True
        ).first()

    def _get_latest_sbti_result(self, user_id: int) -> Optional[SBTIResult]:
        """获取最新的SBTI结果"""
        return self.db.query(SBTIResult).filter(
            SBTIResult.user_id == user_id,
            SBTIResult.is_latest == True
        ).first()

    def _get_latest_attachment_result(self, user_id: int) -> Optional[AttachmentResult]:
        """获取最新的依恋风格结果"""
        return self.db.query(AttachmentResult).filter(
            AttachmentResult.user_id == user_id,
            AttachmentResult.is_latest == True
        ).first()

    async def _collect_behavior_data(
        self,
        user_id: int,
        days: int
    ) -> Dict[str, Any]:
        """收集行为数据"""
        start_date = datetime.now() - timedelta(days=days)

        activities = self.db.query(UserActivity).filter(
            UserActivity.user_id == user_id,
            UserActivity.created_at >= start_date
        ).all()

        behaviors = self.db.query(UserBehavior).filter(
            UserBehavior.user_id == user_id
        ).all()

        messages = self.db.query(Message).filter(
            Message.user_id == user_id,
            Message.created_at >= start_date
        ).order_by(Message.created_at.desc()).limit(100).all()

        diaries = self.db.query(EmotionDiary).filter(
            EmotionDiary.user_id == user_id,
            EmotionDiary.created_at >= start_date
        ).order_by(EmotionDiary.created_at.desc()).limit(50).all()

        return {
            "activities": activities,
            "behaviors": behaviors,
            "messages": messages,
            "diaries": diaries,
            "date_range": (start_date, datetime.now())
        }

    async def _analyze_mbti_behavior_correlation(
        self,
        mbti_result: MbtiResult,
        behavior_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """分析MBTI与行为的关联"""
        correlations = []

        mbti_type = mbti_result.mbti_type if hasattr(mbti_result, 'mbti_type') else mbti_result.type

        if not mbti_type or len(mbti_type) != 4:
            return correlations

        ei_dimension = mbti_type[0]
        sn_dimension = mbti_type[1]
        tf_dimension = mbti_type[2]
        jp_dimension = mbti_type[3]

        chat_count = len(behavior_data["messages"])
        activity_count = len(behavior_data["activities"])

        if ei_dimension == "E":
            correlations.append({
                "personality_trait": "外向性(E)",
                "trait_source": "mbti",
                "behavior_pattern": "高频社交互动",
                "behavior_category": "social",
                "correlation_strength": min(1.0, chat_count / 50),
                "observation_count": chat_count,
                "sample_size": max(chat_count, 1),
                "is_validated": chat_count > 20,
                "validation_confidence": min(1.0, chat_count / 100)
            })

        if ei_dimension == "I":
            correlations.append({
                "personality_trait": "内向性(I)",
                "trait_source": "mbti",
                "behavior_pattern": "深度思考与独处",
                "behavior_category": "emotion",
                "correlation_strength": 0.7,
                "observation_count": activity_count,
                "sample_size": max(activity_count, 1),
                "is_validated": True,
                "validation_confidence": 0.8
            })

        if tf_dimension == "T":
            correlations.append({
                "personality_trait": "思考型(T)",
                "trait_source": "mbti",
                "behavior_pattern": "逻辑分析决策",
                "behavior_category": "decision",
                "correlation_strength": 0.8,
                "observation_count": activity_count,
                "sample_size": max(activity_count, 1),
                "is_validated": True,
                "validation_confidence": 0.85
            })

        if tf_dimension == "F":
            correlations.append({
                "personality_trait": "情感型(F)",
                "trait_source": "mbti",
                "behavior_pattern": "情感导向沟通",
                "behavior_category": "communication",
                "correlation_strength": 0.85,
                "observation_count": chat_count,
                "sample_size": max(chat_count, 1),
                "is_validated": chat_count > 10,
                "validation_confidence": 0.9
            })

        return correlations

    async def _analyze_sbti_behavior_correlation(
        self,
        sbti_result: SBTIResult,
        behavior_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """分析SBTI与行为的关联"""
        correlations = []

        top_themes = [
            sbti_result.top_theme_1,
            sbti_result.top_theme_2,
            sbti_result.top_theme_3,
            sbti_result.top_theme_4,
            sbti_result.top_theme_5
        ]

        theme_behavior_map = {
            "成就": {"pattern": "追求目标达成", "category": "work"},
            "行动": {"pattern": "快速启动项目", "category": "decision"},
            "适应": {"pattern": "灵活应对变化", "category": "work"},
            "统筹": {"pattern": "组织协调资源", "category": "work"},
            "沟通": {"pattern": "善于表达分享", "category": "communication"},
            "竞争": {"pattern": "追求卓越表现", "category": "work"},
            "完美": {"pattern": "注重品质细节", "category": "work"},
            "自信": {"pattern": "独立决策行动", "category": "decision"},
            "体谅": {"pattern": "共情他人感受", "category": "social"},
            "和谐": {"pattern": "避免冲突矛盾", "category": "social"},
            "包容": {"pattern": "接纳不同观点", "category": "social"},
            "积极": {"pattern": "保持乐观态度", "category": "emotion"},
            "交往": {"pattern": "建立深度关系", "category": "social"},
            "分析": {"pattern": "理性分析问题", "category": "decision"},
            "前瞻": {"pattern": "关注未来趋势", "category": "decision"},
            "理念": {"pattern": "创新思维模式", "category": "work"},
            "学习": {"pattern": "持续学习成长", "category": "work"},
        }

        for theme in top_themes:
            if theme in theme_behavior_map:
                behavior_info = theme_behavior_map[theme]
                correlations.append({
                    "personality_trait": f"{theme}才干",
                    "trait_source": "sbti",
                    "behavior_pattern": behavior_info["pattern"],
                    "behavior_category": behavior_info["category"],
                    "correlation_strength": 0.75,
                    "observation_count": len(behavior_data["activities"]),
                    "sample_size": max(len(behavior_data["activities"]), 1),
                    "is_validated": True,
                    "validation_confidence": 0.7
                })

        return correlations

    async def _analyze_attachment_behavior_correlation(
        self,
        attachment_result: AttachmentResult,
        behavior_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """分析依恋风格与行为的关联"""
        correlations = []

        style = attachment_result.attachment_style.value if hasattr(attachment_result.attachment_style, 'value') else attachment_result.attachment_style

        style_pattern_map = {
            "secure": {
                "pattern": "建立安全稳定的关系",
                "category": "social"
            },
            "anxious": {
                "pattern": "寻求亲密与确认",
                "category": "social"
            },
            "avoidant": {
                "pattern": "保持情感距离",
                "category": "social"
            },
            "disorganized": {
                "pattern": "矛盾的关系行为",
                "category": "emotion"
            }
        }

        if style in style_pattern_map:
            pattern_info = style_pattern_map[style]
            correlations.append({
                "personality_trait": f"{style}依恋风格",
                "trait_source": "attachment",
                "behavior_pattern": pattern_info["pattern"],
                "behavior_category": pattern_info["category"],
                "correlation_strength": 0.85,
                "observation_count": len(behavior_data["diaries"]),
                "sample_size": max(len(behavior_data["diaries"]), 1),
                "is_validated": len(behavior_data["diaries"]) > 5,
                "validation_confidence": 0.8
            })

        return correlations

    async def _save_behavior_patterns(
        self,
        user_id: int,
        patterns: List[Dict[str, Any]]
    ):
        """保存行为模式"""
        for pattern_data in patterns:
            existing = self.db.query(PersonaBehaviorPattern).filter(
                PersonaBehaviorPattern.user_id == user_id,
                PersonaBehaviorPattern.personality_trait == pattern_data["personality_trait"],
                PersonaBehaviorPattern.behavior_pattern == pattern_data["behavior_pattern"]
            ).first()

            if existing:
                existing.correlation_strength = pattern_data["correlation_strength"]
                existing.observation_count = pattern_data["observation_count"]
                existing.is_validated = pattern_data["is_validated"]
                existing.validation_confidence = pattern_data["validation_confidence"]
            else:
                new_pattern = PersonaBehaviorPattern(
                    user_id=user_id,
                    **pattern_data
                )
                self.db.add(new_pattern)

        self.db.commit()

    async def _collect_need_evidence(
        self,
        user_id: int,
        days: int
    ) -> Dict[str, Any]:
        """收集需求证据"""
        start_date = datetime.now() - timedelta(days=days)

        diaries = self.db.query(EmotionDiary).filter(
            EmotionDiary.user_id == user_id,
            EmotionDiary.created_at >= start_date
        ).all()

        messages = self.db.query(Message).filter(
            Message.user_id == user_id,
            Message.created_at >= start_date
        ).all()

        activities = self.db.query(UserActivity).filter(
            UserActivity.user_id == user_id,
            UserActivity.created_at >= start_date
        ).all()

        behaviors = self.db.query(UserBehavior).filter(
            UserBehavior.user_id == user_id
        ).all()

        return {
            "diaries": diaries,
            "messages": messages,
            "activities": activities,
            "behaviors": behaviors
        }

    async def _analyze_autonomy_need(
        self,
        data_sources: Dict[str, Any],
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """分析自主需求"""
        independent_activities = 0
        for activity in data_sources["activities"]:
            if activity.event_type in ["diary_create", "assessment_complete"]:
                independent_activities += 1

        intensity = min(1.0, independent_activities / 20)

        if intensity < 0.3:
            return None

        return {
            "need_name": "自主需求",
            "need_category": "autonomy",
            "need_level": self._get_need_level(intensity),
            "intensity_score": intensity,
            "satisfaction_score": 0.6,
            "priority_score": intensity * 0.8,
            "evidence_sources": ["behavior", "activity"],
            "supporting_behavior": ["独立完成任务", "自我探索"],
            "is_explicit": False
        }

    async def _analyze_competence_need(
        self,
        data_sources: Dict[str, Any],
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """分析能力需求"""
        learning_activities = 0
        for activity in data_sources["activities"]:
            if activity.event_type in ["assessment_complete"]:
                learning_activities += 1

        intensity = min(1.0, learning_activities / 10)

        if intensity < 0.3:
            return None

        return {
            "need_name": "能力需求",
            "need_category": "competence",
            "need_level": self._get_need_level(intensity),
            "intensity_score": intensity,
            "satisfaction_score": 0.5,
            "priority_score": intensity * 0.9,
            "evidence_sources": ["activity"],
            "supporting_behavior": ["参与测评", "技能提升"],
            "is_explicit": False
        }

    async def _analyze_relatedness_need(
        self,
        data_sources: Dict[str, Any],
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """分析关联需求"""
        social_activities = 0
        for activity in data_sources["activities"]:
            if activity.event_type in ["chat_message"]:
                social_activities += 1

        chat_count = len(data_sources["messages"])
        intensity = min(1.0, (social_activities + chat_count) / 50)

        if intensity < 0.3:
            return None

        return {
            "need_name": "关联需求",
            "need_category": "relatedness",
            "need_level": self._get_need_level(intensity),
            "intensity_score": intensity,
            "satisfaction_score": 0.7,
            "priority_score": intensity * 0.85,
            "evidence_sources": ["chat", "activity"],
            "supporting_behavior": ["频繁聊天", "社交互动"],
            "is_explicit": False
        }

    async def _analyze_security_need(
        self,
        data_sources: Dict[str, Any],
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """分析安全需求"""
        routine_behaviors = 0
        for behavior in data_sources["behaviors"]:
            if behavior.frequency > 5:
                routine_behaviors += 1

        intensity = min(1.0, routine_behaviors / 5)

        if intensity < 0.3:
            return None

        return {
            "need_name": "安全需求",
            "need_category": "security",
            "need_level": self._get_need_level(intensity),
            "intensity_score": intensity,
            "satisfaction_score": 0.65,
            "priority_score": intensity * 0.75,
            "evidence_sources": ["behavior"],
            "supporting_behavior": ["规律性行为", "稳定习惯"],
            "is_explicit": False
        }

    async def _analyze_growth_need(
        self,
        data_sources: Dict[str, Any],
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """分析成长需求"""
        growth_activities = 0
        for activity in data_sources["activities"]:
            if activity.event_type in ["assessment_complete", "diary_create"]:
                growth_activities += 1

        diary_count = len(data_sources["diaries"])
        intensity = min(1.0, (growth_activities + diary_count) / 30)

        if intensity < 0.3:
            return None

        return {
            "need_name": "成长需求",
            "need_category": "growth",
            "need_level": self._get_need_level(intensity),
            "intensity_score": intensity,
            "satisfaction_score": 0.55,
            "priority_score": intensity * 0.95,
            "evidence_sources": ["diary", "activity"],
            "supporting_behavior": ["写日记", "自我反思"],
            "is_explicit": False
        }

    async def _analyze_recognition_need(
        self,
        data_sources: Dict[str, Any],
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """分析认可需求"""
        intensity = 0.5

        return {
            "need_name": "认可需求",
            "need_category": "recognition",
            "need_level": self._get_need_level(intensity),
            "intensity_score": intensity,
            "satisfaction_score": 0.5,
            "priority_score": intensity * 0.7,
            "evidence_sources": ["inferred"],
            "supporting_behavior": ["寻求反馈"],
            "is_explicit": False
        }

    def _get_need_level(self, intensity: float) -> str:
        """根据强度获取需求级别"""
        if intensity >= 0.8:
            return "critical"
        elif intensity >= 0.6:
            return "high"
        elif intensity >= 0.4:
            return "medium"
        else:
            return "low"

    async def _save_psychological_needs(
        self,
        user_id: int,
        needs: List[Dict[str, Any]]
    ):
        """保存心理需求"""
        for need_data in needs:
            existing = self.db.query(PsychologicalNeed).filter(
                PsychologicalNeed.user_id == user_id,
                PsychologicalNeed.need_name == need_data["need_name"]
            ).first()

            if existing:
                existing.intensity_score = need_data["intensity_score"]
                existing.satisfaction_score = need_data["satisfaction_score"]
                existing.priority_score = need_data["priority_score"]
                existing.need_level = need_data["need_level"]
            else:
                new_need = PsychologicalNeed(
                    user_id=user_id,
                    **need_data
                )
                self.db.add(new_need)

        self.db.commit()

    async def _extract_tags_from_chat(self, user_id: int) -> List[Dict[str, Any]]:
        """从聊天中提取标签"""
        tags = []
        messages = self.db.query(Message).filter(
            Message.user_id == user_id
        ).order_by(Message.created_at.desc()).limit(50).all()

        if len(messages) > 20:
            tags.append({
                "tag_name": "健谈",
                "tag_category": "behavior",
                "tag_source": "chat",
                "confidence_score": min(1.0, len(messages) / 50),
                "relevance_score": 0.7
            })

        return tags

    async def _extract_tags_from_diary(self, user_id: int) -> List[Dict[str, Any]]:
        """从日记中提取标签"""
        tags = []
        diaries = self.db.query(EmotionDiary).filter(
            EmotionDiary.user_id == user_id
        ).order_by(EmotionDiary.created_at.desc()).limit(30).all()

        if len(diaries) > 10:
            tags.append({
                "tag_name": "善于反思",
                "tag_category": "behavior",
                "tag_source": "diary",
                "confidence_score": min(1.0, len(diaries) / 30),
                "relevance_score": 0.8
            })

        return tags

    async def _extract_tags_from_behavior(self, user_id: int) -> List[Dict[str, Any]]:
        """从行为中提取标签"""
        tags = []
        behaviors = self.db.query(UserBehavior).filter(
            UserBehavior.user_id == user_id
        ).all()

        for behavior in behaviors:
            if behavior.frequency > 10:
                tags.append({
                    "tag_name": f"常{behavior.behavior_type}",
                    "tag_category": "behavior",
                    "tag_source": "behavior",
                    "confidence_score": min(1.0, behavior.frequency / 50),
                    "relevance_score": 0.6
                })

        return tags

    async def _save_dynamic_tags(
        self,
        user_id: int,
        tags: List[Dict[str, Any]]
    ):
        """保存动态标签"""
        for tag_data in tags:
            existing = self.db.query(DynamicPersonaTag).filter(
                DynamicPersonaTag.user_id == user_id,
                DynamicPersonaTag.tag_name == tag_data["tag_name"],
                DynamicPersonaTag.tag_category == tag_data["tag_category"]
            ).first()

            if existing:
                existing.last_observed_at = datetime.now()
                existing.observation_count += 1
                existing.confidence_score = tag_data["confidence_score"]
            else:
                new_tag = DynamicPersonaTag(
                    user_id=user_id,
                    **tag_data
                )
                self.db.add(new_tag)

        self.db.commit()


def get_deep_analysis_engine(db: Session) -> DeepAnalysisEngine:
    """获取深度分析引擎实例"""
    return DeepAnalysisEngine(db)
