"""
增强的人格画像服务
实现动态人格画像、人格变化趋势追踪和三位一体深度融合
"""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
import json
import loguru

from app.models import (
    User,
    MbtiResult,
    SBTIResult,
    AttachmentResult,
    DeepPersonaProfile,
    PersonaTrend,
    IntegratedPersonaStrategy,
    DynamicPersonaTag,
    PersonaBehaviorPattern,
    PsychologicalNeed,
)
from app.services.deep_analysis_engine import DeepAnalysisEngine, get_deep_analysis_engine


class EnhancedPersonaService:
    """增强的人格画像服务"""

    def __init__(self, db: Session):
        self.db = db
        self.logger = loguru.logger
        self.analysis_engine = get_deep_analysis_engine(db)

    async def update_dynamic_persona(
        self,
        user_id: int,
        behavior_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        实时更新动态人格画像

        Args:
            user_id: 用户ID
            behavior_data: 行为数据（可选）

        Returns:
            更新后的人格画像
        """
        self.logger.info(f"Updating dynamic persona for user {user_id}")

        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError(f"User {user_id} not found")

            if behavior_data:
                await self._process_behavior_data(user_id, behavior_data)

            await self.analysis_engine.extract_dynamic_tags(user_id)
            await self.analysis_engine.analyze_personality_behavior_correlation(user_id)
            await self.analysis_engine.mine_psychological_needs(user_id)

            await self._track_persona_trends(user_id)

            updated_profile = await self._get_complete_persona_profile(user_id)

            return {
                "success": True,
                "user_id": user_id,
                "profile": updated_profile,
                "updated_at": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error updating dynamic persona: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_persona_trends(
        self,
        user_id: int,
        trend_type: Optional[str] = None,
        days: int = 90
    ) -> Dict[str, Any]:
        """
        获取人格变化趋势

        Args:
            user_id: 用户ID
            trend_type: 趋势类型（可选）
            days: 统计天数

        Returns:
            趋势分析结果
        """
        self.logger.info(f"Getting persona trends for user {user_id}")

        try:
            start_date = datetime.now() - timedelta(days=days)

            query = self.db.query(PersonaTrend).filter(
                PersonaTrend.user_id == user_id,
                PersonaTrend.snapshot_date >= start_date
            )

            if trend_type:
                query = query.filter(PersonaTrend.trend_type == trend_type)

            trends = query.order_by(PersonaTrend.snapshot_date.desc()).all()

            trend_summary = self._summarize_trends(trends)

            return {
                "success": True,
                "user_id": user_id,
                "trends": [
                    {
                        "id": t.id,
                        "type": t.trend_type,
                        "snapshot_date": t.snapshot_date.isoformat(),
                        "previous_value": t.previous_value,
                        "current_value": t.current_value,
                        "change_magnitude": t.change_magnitude,
                        "trend_direction": t.trend_direction,
                        "contributing_factors": t.contributing_factors
                    }
                    for t in trends
                ],
                "summary": trend_summary,
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": datetime.now().isoformat()
                }
            }

        except Exception as e:
            self.logger.error(f"Error getting persona trends: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def generate_integrated_strategy(
        self,
        user_id: int
    ) -> Dict[str, Any]:
        """
        生成三位一体融合策略

        Args:
            user_id: 用户ID

        Returns:
            融合策略结果
        """
        self.logger.info(f"Generating integrated strategy for user {user_id}")

        try:
            mbti_result = self._get_latest_mbti_result(user_id)
            sbti_result = self._get_latest_sbti_result(user_id)
            attachment_result = self._get_latest_attachment_result(user_id)

            if not (mbti_result or sbti_result or attachment_result):
                return {
                    "success": False,
                    "error": "No assessment results found for user"
                }

            fusion_insights = self._generate_fusion_insights(mbti_result, sbti_result, attachment_result)
            synergy_effects = self._identify_synergy_effects(mbti_result, sbti_result, attachment_result)
            potential_conflicts = self._identify_potential_conflicts(mbti_result, sbti_result, attachment_result)
            communication_strategy = self._generate_communication_strategy(mbti_result, sbti_result, attachment_result)
            personal_advice = self._generate_personal_advice(mbti_result, sbti_result, attachment_result)

            strategy = await self._save_integrated_strategy(
                user_id,
                mbti_result,
                sbti_result,
                attachment_result,
                fusion_insights,
                synergy_effects,
                potential_conflicts,
                communication_strategy,
                personal_advice
            )

            return {
                "success": True,
                "user_id": user_id,
                "strategy": strategy,
                "generated_at": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error generating integrated strategy: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_multi_dimensional_tags(
        self,
        user_id: int,
        category: Optional[str] = None,
        active_only: bool = True
    ) -> Dict[str, Any]:
        """
        获取多维度画像标签

        Args:
            user_id: 用户ID
            category: 标签类别（可选）
            active_only: 是否只返回活跃标签

        Returns:
            标签体系结果
        """
        self.logger.info(f"Getting multi-dimensional tags for user {user_id}")

        try:
            query = self.db.query(DynamicPersonaTag).filter(
                DynamicPersonaTag.user_id == user_id
            )

            if category:
                query = query.filter(DynamicPersonaTag.tag_category == category)

            if active_only:
                query = query.filter(DynamicPersonaTag.is_active == True)

            tags = query.order_by(
                DynamicPersonaTag.relevance_score.desc(),
                DynamicPersonaTag.confidence_score.desc()
            ).all()

            tags_by_category = {}
            for tag in tags:
                if tag.tag_category not in tags_by_category:
                    tags_by_category[tag.tag_category] = []
                tags_by_category[tag.tag_category].append({
                    "id": tag.id,
                    "name": tag.tag_name,
                    "confidence": tag.confidence_score,
                    "relevance": tag.relevance_score,
                    "source": tag.tag_source,
                    "observation_count": tag.observation_count,
                    "first_observed": tag.first_observed_at.isoformat(),
                    "last_observed": tag.last_observed_at.isoformat(),
                    "is_temporary": tag.is_temporary
                })

            return {
                "success": True,
                "user_id": user_id,
                "tags_by_category": tags_by_category,
                "total_tags": len(tags)
            }

        except Exception as e:
            self.logger.error(f"Error getting multi-dimensional tags: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _process_behavior_data(
        self,
        user_id: int,
        behavior_data: Dict[str, Any]
    ):
        """处理行为数据"""
        behavior_type = behavior_data.get("type", "unknown")
        behavior_content = behavior_data.get("content", {})

        self.logger.debug(f"Processing behavior: {behavior_type} for user {user_id}")

    async def _track_persona_trends(self, user_id: int):
        """追踪人格变化趋势"""
        mbti_result = self._get_latest_mbti_result(user_id)
        sbti_result = self._get_latest_sbti_result(user_id)
        attachment_result = self._get_latest_attachment_result(user_id)

        if mbti_result:
            await self._create_trend_record(user_id, "mbti", mbti_result)

        if sbti_result:
            await self._create_trend_record(user_id, "sbti", sbti_result)

        if attachment_result:
            await self._create_trend_record(user_id, "attachment", attachment_result)

    async def _create_trend_record(
        self,
        user_id: int,
        trend_type: str,
        current_result: Any
    ):
        """创建趋势记录"""
        previous_trend = self.db.query(PersonaTrend).filter(
            PersonaTrend.user_id == user_id,
            PersonaTrend.trend_type == trend_type
        ).order_by(PersonaTrend.snapshot_date.desc()).first()

        current_value = self._extract_trend_value(trend_type, current_result)
        previous_value = None
        change_magnitude = 0.0
        trend_direction = "stable"

        if previous_trend:
            previous_value = previous_trend.current_value
            change_magnitude = self._calculate_change_magnitude(previous_value, current_value)
            trend_direction = self._determine_trend_direction(change_magnitude)

        trend = PersonaTrend(
            user_id=user_id,
            trend_type=trend_type,
            previous_value=previous_value,
            current_value=current_value,
            change_magnitude=change_magnitude,
            trend_direction=trend_direction,
            contributing_factors=["behavior_update"]
        )

        self.db.add(trend)
        self.db.commit()

    def _extract_trend_value(self, trend_type: str, result: Any) -> Dict[str, Any]:
        """提取趋势值"""
        if trend_type == "mbti":
            mbti_type = result.mbti_type if hasattr(result, 'mbti_type') else result.type
            return {"type": mbti_type}
        elif trend_type == "sbti":
            return {
                "top_themes": [
                    result.top_theme_1,
                    result.top_theme_2,
                    result.top_theme_3,
                    result.top_theme_4,
                    result.top_theme_5
                ],
                "domains": {
                    "executing": result.executing_score,
                    "influencing": result.influencing_score,
                    "relationship": result.relationship_score,
                    "strategic": result.strategic_score
                }
            }
        elif trend_type == "attachment":
            style = result.attachment_style.value if hasattr(result.attachment_style, 'value') else result.attachment_style
            return {
                "style": style,
                "anxiety_score": result.anxiety_score,
                "avoidance_score": result.avoidance_score
            }
        return {}

    def _calculate_change_magnitude(self, previous: Any, current: Any) -> float:
        """计算变化幅度"""
        if not previous or not current:
            return 0.0

        if isinstance(previous, dict) and isinstance(current, dict):
            if previous.get("type") != current.get("type"):
                return 1.0

        return 0.0

    def _determine_trend_direction(self, magnitude: float) -> str:
        """确定趋势方向"""
        if magnitude > 0.1:
            return "increase"
        elif magnitude < -0.1:
            return "decrease"
        return "stable"

    def _summarize_trends(self, trends: List[PersonaTrend]) -> Dict[str, Any]:
        """总结趋势"""
        summary = {
            "total_changes": 0,
            "stable_types": [],
            "changing_types": [],
            "recent_changes": []
        }

        type_changes = {}
        for trend in trends:
            if trend.trend_type not in type_changes:
                type_changes[trend.trend_type] = {"changes": 0, "last_change": None}

            if trend.change_magnitude > 0:
                type_changes[trend.trend_type]["changes"] += 1
                type_changes[trend.trend_type]["last_change"] = trend.snapshot_date

        for trend_type, data in type_changes.items():
            if data["changes"] == 0:
                summary["stable_types"].append(trend_type)
            else:
                summary["changing_types"].append(trend_type)
                summary["total_changes"] += data["changes"]

        summary["recent_changes"] = [
            t.trend_type for t in trends[:5] if t.change_magnitude > 0
        ]

        return summary

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

    def _generate_fusion_insights(
        self,
        mbti_result: Optional[MbtiResult],
        sbti_result: Optional[SBTIResult],
        attachment_result: Optional[AttachmentResult]
    ) -> List[Dict[str, Any]]:
        """生成融合洞察"""
        insights = []

        if mbti_result and sbti_result:
            mbti_type = mbti_result.mbti_type if hasattr(mbti_result, 'mbti_type') else mbti_result.type
            insights.append({
                "type": "mbti_sbti_fusion",
                "title": f"{mbti_type}人格与SBTI才干融合",
                "content": f"你的{mbti_type}人格特质与SBTI优势才干相互作用，形成独特的行为模式。",
                "priority": "high"
            })

        if mbti_result and attachment_result:
            mbti_type = mbti_result.mbti_type if hasattr(mbti_result, 'mbti_type') else mbti_result.type
            style = attachment_result.attachment_style.value if hasattr(attachment_result.attachment_style, 'value') else attachment_result.attachment_style
            insights.append({
                "type": "mbti_attachment_fusion",
                "title": f"{mbti_type}人格与{style}依恋风格融合",
                "content": f"你的{mbti_type}认知方式与{style}依恋模式共同塑造了你的人际关系风格。",
                "priority": "high"
            })

        if sbti_result and attachment_result:
            style = attachment_result.attachment_style.value if hasattr(attachment_result.attachment_style, 'value') else attachment_result.attachment_style
            insights.append({
                "type": "sbti_attachment_fusion",
                "title": "SBTI才干与依恋风格融合",
                "content": f"你的优势才干在{style}依恋模式下得到独特的表达。",
                "priority": "medium"
            })

        return insights

    def _identify_synergy_effects(
        self,
        mbti_result: Optional[MbtiResult],
        sbti_result: Optional[SBTIResult],
        attachment_result: Optional[AttachmentResult]
    ) -> List[Dict[str, Any]]:
        """识别协同效应"""
        synergies = []

        if mbti_result and sbti_result:
            synergies.append({
                "effect": "认知-行动协同",
                "description": "MBTI认知偏好与SBTI行动才干形成高效协同",
                "strength": 0.8
            })

        if sbti_result and attachment_result:
            synergies.append({
                "effect": "才干-关系协同",
                "description": "SBTI优势才干在依恋风格下得到最佳发挥",
                "strength": 0.75
            })

        return synergies

    def _identify_potential_conflicts(
        self,
        mbti_result: Optional[MbtiResult],
        sbti_result: Optional[SBTIResult],
        attachment_result: Optional[AttachmentResult]
    ) -> List[Dict[str, Any]]:
        """识别潜在冲突"""
        conflicts = []

        if mbti_result and attachment_result:
            conflicts.append({
                "conflict": "认知-情感张力",
                "description": "MBTI理性/情感维度可能与依恋模式产生张力",
                "severity": "low",
                "mitigation": "通过自我觉察平衡两者"
            })

        return conflicts

    def _generate_communication_strategy(
        self,
        mbti_result: Optional[MbtiResult],
        sbti_result: Optional[SBTIResult],
        attachment_result: Optional[AttachmentResult]
    ) -> Dict[str, Any]:
        """生成沟通策略"""
        strategy = {
            "preferred_style": "balanced",
            "language_preference": {
                "detail_level": "medium",
                "emotional_tone": "supportive",
                "directness": "balanced"
            },
            "tone_adjustment": {
                "warmth": 0.7,
                "formality": 0.5,
                "enthusiasm": 0.6
            },
            "interaction_guidelines": []
        }

        if mbti_result:
            mbti_type = mbti_result.mbti_type if hasattr(mbti_result, 'mbti_type') else mbti_result.type
            if mbti_type:
                if mbti_type.startswith("I"):
                    strategy["interaction_guidelines"].append("给予充分的思考时间，避免过度催促")
                if mbti_type.startswith("E"):
                    strategy["interaction_guidelines"].append("保持对话的活跃性，鼓励表达")
                if mbti_type[2] == "T":
                    strategy["language_preference"]["detail_level"] = "high"
                    strategy["interaction_guidelines"].append("注重逻辑和事实依据")
                if mbti_type[2] == "F":
                    strategy["tone_adjustment"]["warmth"] = 0.9
                    strategy["interaction_guidelines"].append("注重情感共鸣和价值认同")

        if sbti_result:
            top_themes = [
                sbti_result.top_theme_1,
                sbti_result.top_theme_2,
                sbti_result.top_theme_3
            ]
            if "沟通" in top_themes:
                strategy["language_preference"]["directness"] = "direct"
            if "体谅" in top_themes:
                strategy["tone_adjustment"]["warmth"] = 0.95

        if attachment_result:
            style = attachment_result.attachment_style.value if hasattr(attachment_result.attachment_style, 'value') else attachment_result.attachment_style
            if style == "secure":
                strategy["preferred_style"] = "open"
            elif style == "anxious":
                strategy["interaction_guidelines"].append("提供稳定的情感支持和及时反馈")
            elif style == "avoidant":
                strategy["interaction_guidelines"].append("尊重个人空间，逐步建立信任")

        return strategy

    def _generate_personal_advice(
        self,
        mbti_result: Optional[MbtiResult],
        sbti_result: Optional[SBTIResult],
        attachment_result: Optional[AttachmentResult]
    ) -> Dict[str, Any]:
        """生成个性化建议"""
        advice = {
            "growth_pathways": [],
            "relationship_guidance": [],
            "strength_application": []
        }

        if sbti_result:
            advice["strength_application"].append({
                "theme": "发挥优势才干",
                "content": f"重点发挥你的TOP5才干：{sbti_result.top_theme_1}、{sbti_result.top_theme_2}、{sbti_result.top_theme_3}等"
            })

        if mbti_result:
            mbti_type = mbti_result.mbti_type if hasattr(mbti_result, 'mbti_type') else mbti_result.type
            advice["growth_pathways"].append({
                "area": "人格发展",
                "content": f"基于{mbti_type}人格特质，探索平衡发展的可能性"
            })

        if attachment_result:
            style = attachment_result.attachment_style.value if hasattr(attachment_result.attachment_style, 'value') else attachment_result.attachment_style
            advice["relationship_guidance"].append({
                "focus": "关系模式",
                "content": f"认识你的{style}依恋模式，发展更健康的关系互动"
            })

        return advice

    async def _save_integrated_strategy(
        self,
        user_id: int,
        mbti_result: Optional[MbtiResult],
        sbti_result: Optional[SBTIResult],
        attachment_result: Optional[AttachmentResult],
        fusion_insights: List[Dict[str, Any]],
        synergy_effects: List[Dict[str, Any]],
        potential_conflicts: List[Dict[str, Any]],
        communication_strategy: Dict[str, Any],
        personal_advice: Dict[str, Any]
    ) -> Dict[str, Any]:
        """保存融合策略"""
        existing = self.db.query(IntegratedPersonaStrategy).filter(
            IntegratedPersonaStrategy.user_id == user_id,
            IntegratedPersonaStrategy.is_latest == True
        ).first()

        if existing:
            existing.is_latest = False

        strategy = IntegratedPersonaStrategy(
            user_id=user_id,
            mbti_result_id=mbti_result.id if mbti_result else None,
            sbti_result_id=sbti_result.id if sbti_result else None,
            attachment_result_id=attachment_result.id if attachment_result else None,
            fusion_insights=fusion_insights,
            synergy_effects=synergy_effects,
            potential_conflicts=potential_conflicts,
            communication_strategy=communication_strategy,
            language_preference=communication_strategy.get("language_preference"),
            tone_adjustment=communication_strategy.get("tone_adjustment"),
            interaction_style=communication_strategy.get("preferred_style"),
            personal_advice=personal_advice,
            growth_pathways=personal_advice.get("growth_pathways"),
            relationship_guidance=personal_advice.get("relationship_guidance"),
            strategy_version=existing.strategy_version + 1 if existing else 1,
            is_latest=True
        )

        self.db.add(strategy)
        self.db.commit()
        self.db.refresh(strategy)

        return {
            "id": strategy.id,
            "version": strategy.strategy_version,
            "fusion_insights": fusion_insights,
            "synergy_effects": synergy_effects,
            "potential_conflicts": potential_conflicts,
            "communication_strategy": communication_strategy,
            "personal_advice": personal_advice
        }

    async def _get_complete_persona_profile(self, user_id: int) -> Dict[str, Any]:
        """获取完整的人格画像"""
        mbti_result = self._get_latest_mbti_result(user_id)
        sbti_result = self._get_latest_sbti_result(user_id)
        attachment_result = self._get_latest_attachment_result(user_id)

        deep_profile = self.db.query(DeepPersonaProfile).filter(
            DeepPersonaProfile.user_id == user_id
        ).first()

        integrated_strategy = self.db.query(IntegratedPersonaStrategy).filter(
            IntegratedPersonaStrategy.user_id == user_id,
            IntegratedPersonaStrategy.is_latest == True
        ).first()

        return {
            "mbti": {
                "type": mbti_result.mbti_type if (mbti_result and hasattr(mbti_result, 'mbti_type')) else (mbti_result.type if mbti_result else None),
                "has_result": mbti_result is not None
            },
            "sbti": {
                "top_themes": [
                    sbti_result.top_theme_1,
                    sbti_result.top_theme_2,
                    sbti_result.top_theme_3,
                    sbti_result.top_theme_4,
                    sbti_result.top_theme_5
                ] if sbti_result else [],
                "has_result": sbti_result is not None
            },
            "attachment": {
                "style": attachment_result.attachment_style.value if (attachment_result and hasattr(attachment_result.attachment_style, 'value')) else (attachment_result.attachment_style if attachment_result else None),
                "has_result": attachment_result is not None
            },
            "deep_profile": {
                "completeness": deep_profile.completeness if deep_profile else 0,
                "has_deep_report": deep_profile.has_deep_report if deep_profile else False
            },
            "integrated_strategy": {
                "has_strategy": integrated_strategy is not None,
                "version": integrated_strategy.strategy_version if integrated_strategy else None
            }
        }


def get_enhanced_persona_service(db: Session) -> EnhancedPersonaService:
    """获取增强的人格画像服务实例"""
    return EnhancedPersonaService(db)
