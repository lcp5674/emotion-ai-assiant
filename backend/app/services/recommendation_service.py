"""
推荐系统服务
提供个性化内容推荐功能
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from app.models import (
    User,
    KnowledgeArticle,
    UserContentInteraction,
    UserPreference,
    ContentTag,
    ContentTagRelation,
    RecommendationHistory,
    ContentType,
    RecommendationReason,
)
from app.models.diary import MoodRecord, MoodLevel


class RecommendationService:
    """推荐系统服务"""
    
    def __init__(self):
        self.cold_start_threshold = 5  # 冷启动阈值
    
    def get_personalized_recommendations(
        self, 
        db: Session, 
        user_id: int, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        获取个性化推荐内容
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            limit: 推荐数量限制
            
        Returns:
            推荐内容列表
        """
        recommendations = []
        
        # 检查用户是否有足够的交互记录
        interaction_count = db.query(func.count(UserContentInteraction.id)).filter(
            UserContentInteraction.user_id == user_id
        ).scalar()
        
        if interaction_count < self.cold_start_threshold:
            # 冷启动：基于MBTI和热门内容推荐
            recommendations.extend(self._get_cold_start_recommendations(db, user_id, limit))
        else:
            # 混合推荐策略
            recommendations.extend(self._get_mbti_based_recommendations(db, user_id, limit // 3))
            recommendations.extend(self._get_mood_based_recommendations(db, user_id, limit // 3))
            recommendations.extend(self._get_history_based_recommendations(db, user_id, limit // 3))
            recommendations.extend(self._get_popular_recommendations(db, limit // 3))
        
        # 去重并返回
        seen_ids = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec["id"] not in seen_ids:
                seen_ids.add(rec["id"])
                unique_recommendations.append(rec)
                if len(unique_recommendations) >= limit:
                    break
        
        # 保存推荐历史
        self._save_recommendation_history(db, user_id, unique_recommendations)
        
        return unique_recommendations
    
    def _get_cold_start_recommendations(
        self, 
        db: Session, 
        user_id: int, 
        limit: int
    ) -> List[Dict[str, Any]]:
        """
        冷启动推荐策略
        基于MBTI类型和热门内容
        """
        recommendations = []
        
        # 获取用户MBTI类型
        user = db.query(User).filter(User.id == user_id).first()
        if user and user.mbti_type:
            # 基于MBTI类型推荐
            mbti_recommendations = self._get_mbti_based_recommendations(db, user_id, limit // 2)
            recommendations.extend(mbti_recommendations)
        
        # 补充热门内容
        popular_recommendations = self._get_popular_recommendations(db, limit - len(recommendations))
        recommendations.extend(popular_recommendations)
        
        return recommendations
    
    def _get_mbti_based_recommendations(
        self, 
        db: Session, 
        user_id: int, 
        limit: int
    ) -> List[Dict[str, Any]]:
        """
        基于MBTI类型的推荐
        """
        recommendations = []
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.mbti_type:
            return recommendations
        
        # 查找与MBTI相关的内容
        articles = db.query(KnowledgeArticle).filter(
            KnowledgeArticle.title.contains(user.mbti_type) | 
            KnowledgeArticle.content.contains(user.mbti_type)
        ).limit(limit).all()
        
        for article in articles:
            recommendations.append({
                "id": article.id,
                "title": article.title,
                "content": article.content[:200] if article.content else "",
                "type": "article",
                "reason": RecommendationReason.MBTI_MATCH,
                "score": 0.8,
            })
        
        return recommendations
    
    def _get_mood_based_recommendations(
        self, 
        db: Session, 
        user_id: int, 
        limit: int
    ) -> List[Dict[str, Any]]:
        """
        基于当前情绪的推荐
        """
        recommendations = []
        
        # 获取用户最近的情绪记录
        recent_mood = db.query(MoodRecord).filter(
            MoodRecord.user_id == user_id
        ).order_by(desc(MoodRecord.created_at)).first()
        
        if not recent_mood:
            return recommendations
        
        # 根据情绪推荐相应内容
        mood_keywords = {
            MoodLevel.VERY_HAPPY: ["快乐", "积极", "成长", "感恩"],
            MoodLevel.HAPPY: ["快乐", "积极", "成长"],
            MoodLevel.NEUTRAL: ["平静", "思考", "学习"],
            MoodLevel.SAD: ["安慰", "疗愈", "希望", "支持"],
            MoodLevel.VERY_SAD: ["危机干预", "紧急求助", "心理支持"],
        }
        
        keywords = mood_keywords.get(recent_mood.mood_level, ["思考", "学习"])
        
        # 查找包含关键词的内容
        for keyword in keywords:
            articles = db.query(KnowledgeArticle).filter(
                KnowledgeArticle.title.contains(keyword) | 
                KnowledgeArticle.content.contains(keyword)
            ).limit(limit // len(keywords)).all()
            
            for article in articles:
                recommendations.append({
                    "id": article.id,
                    "title": article.title,
                    "content": article.content[:200] if article.content else "",
                    "type": "article",
                    "reason": RecommendationReason.MOOD_MATCH,
                    "score": 0.7,
                })
        
        return recommendations[:limit]
    
    def _get_history_based_recommendations(
        self, 
        db: Session, 
        user_id: int, 
        limit: int
    ) -> List[Dict[str, Any]]:
        """
        基于用户历史行为的推荐
        """
        recommendations = []
        
        # 获取用户喜欢的内容标签
        liked_interactions = db.query(UserContentInteraction).filter(
            UserContentInteraction.user_id == user_id,
            UserContentInteraction.interaction_type.in_(["like", "complete", "bookmark"])
        ).all()
        
        if not liked_interactions:
            return recommendations
        
        # 获取相关内容
        for interaction in liked_interactions:
            if interaction.content_id:
                article = db.query(KnowledgeArticle).filter(
                    KnowledgeArticle.id == interaction.content_id
                ).first()
                
                if article:
                    # 查找相似内容
                    similar_articles = db.query(KnowledgeArticle).filter(
                        KnowledgeArticle.id != article.id,
                        KnowledgeArticle.category == article.category
                    ).limit(limit // len(liked_interactions)).all()
                    
                    for similar_article in similar_articles:
                        recommendations.append({
                            "id": similar_article.id,
                            "title": similar_article.title,
                            "content": similar_article.content[:200] if similar_article.content else "",
                            "type": "article",
                            "reason": RecommendationReason.USER_HISTORY,
                            "score": 0.75,
                        })
        
        return recommendations[:limit]
    
    def _get_popular_recommendations(
        self, 
        db: Session, 
        limit: int
    ) -> List[Dict[str, Any]]:
        """
        获取热门内容推荐
        """
        recommendations = []
        
        # 获取最近7天的热门内容
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        # 统计内容的交互次数
        popular_articles = db.query(
            KnowledgeArticle,
            func.count(UserContentInteraction.id).label('interaction_count')
        ).join(
            UserContentInteraction, 
            KnowledgeArticle.id == UserContentInteraction.content_id
        ).filter(
            UserContentInteraction.created_at >= seven_days_ago
        ).group_by(
            KnowledgeArticle.id
        ).order_by(
            desc('interaction_count')
        ).limit(limit).all()
        
        for article, count in popular_articles:
            recommendations.append({
                "id": article.id,
                "title": article.title,
                "content": article.content[:200] if article.content else "",
                "type": "article",
                "reason": RecommendationReason.POPULAR,
                "score": 0.6 + (count * 0.01),  # 基于交互次数调整分数
            })
        
        return recommendations
    
    def _save_recommendation_history(
        self, 
        db: Session, 
        user_id: int, 
        recommendations: List[Dict[str, Any]]
    ):
        """
        保存推荐历史
        """
        for rec in recommendations:
            history = RecommendationHistory(
                user_id=user_id,
                content_id=rec["id"],
                recommendation_reason=rec["reason"],
                score=rec["score"],
                clicked=0
            )
            db.add(history)
        
        db.commit()
    
    def record_content_interaction(
        self,
        db: Session,
        user_id: int,
        content_id: Optional[int],
        content_type: ContentType,
        interaction_type: str,
        duration: Optional[int] = None,
        rating: Optional[float] = None
    ):
        """
        记录用户内容交互
        """
        interaction = UserContentInteraction(
            user_id=user_id,
            content_id=content_id,
            content_type=content_type,
            interaction_type=interaction_type,
            duration=duration,
            rating=rating,
        )
        db.add(interaction)
        db.commit()
    
    def update_user_preference(
        self,
        db: Session,
        user_id: int,
        preferred_content_types: Optional[List[str]] = None,
        preferred_topics: Optional[List[str]] = None,
        learning_goal: Optional[str] = None,
        time_preference: Optional[str] = None
    ):
        """
        更新用户偏好
        """
        preference = db.query(UserPreference).filter(
            UserPreference.user_id == user_id
        ).first()
        
        if not preference:
            preference = UserPreference(user_id=user_id)
            db.add(preference)
        
        if preferred_content_types is not None:
            preference.preferred_content_types = preferred_content_types
        if preferred_topics is not None:
            preference.preferred_topics = preferred_topics
        if learning_goal is not None:
            preference.learning_goal = learning_goal
        if time_preference is not None:
            preference.time_preference = time_preference
        
        db.commit()
        db.refresh(preference)
        return preference
    
    def add_content_tags(
        self,
        db: Session,
        content_id: int,
        tags: List[str]
    ):
        """
        为内容添加标签
        """
        for tag_name in tags:
            # 查找或创建标签
            tag = db.query(ContentTag).filter(
                ContentTag.name == tag_name
            ).first()
            
            if not tag:
                tag = ContentTag(name=tag_name)
                db.add(tag)
                db.flush()
            
            # 创建标签关系
            relation = ContentTagRelation(
                content_id=content_id,
                tag_id=tag.id
            )
            db.add(relation)
        
        db.commit()


def get_recommendation_service() -> RecommendationService:
    """获取推荐服务实例"""
    return RecommendationService()
