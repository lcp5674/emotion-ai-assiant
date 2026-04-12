"""
数据可视化与洞察服务
提供情绪趋势分析、成长洞察、个性化报告等功能
"""
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from datetime import datetime, timedelta
from app.models import User, MoodRecord, EmotionDiary, Conversation, Message
from app.models.diary import MoodLevel


class AnalyticsInsightService:
    """数据可视化与洞察服务"""
    
    def get_mood_trend_analysis(
        self,
        db: Session,
        user_id: int,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        获取情绪趋势分析
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            days: 分析天数
            
        Returns:
            情绪趋势分析数据
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 获取情绪记录
        mood_records = db.query(MoodRecord).filter(
            MoodRecord.user_id == user_id,
            MoodRecord.created_at >= start_date
        ).order_by(MoodRecord.created_at).all()
        
        # 按日期分组统计
        daily_moods = {}
        for record in mood_records:
            date_key = record.created_at.date().isoformat()
            if date_key not in daily_moods:
                daily_moods[date_key] = []
            daily_moods[date_key].append(record.mood_level)
        
        # 计算每日平均情绪
        daily_averages = []
        for date, moods in sorted(daily_moods.items()):
            avg_mood = sum(
                self._mood_level_to_score(mood) for mood in moods
            ) / len(moods)
            daily_averages.append({
                "date": date,
                "average_mood": avg_mood,
                "mood_level": self._score_to_mood_level(avg_mood),
                "record_count": len(moods)
            })
        
        # 计算总体统计
        if daily_averages:
            overall_avg = sum(d["average_mood"] for d in daily_averages) / len(daily_averages)
            trend = self._calculate_trend(daily_averages)
        else:
            overall_avg = 0
            trend = "stable"
        
        return {
            "period_days": days,
            "daily_moods": daily_averages,
            "overall_average": overall_avg,
            "overall_mood_level": self._score_to_mood_level(overall_avg),
            "trend": trend,
            "total_records": len(mood_records)
        }
    
    def _mood_level_to_score(self, mood_level: MoodLevel) -> float:
        """
        将情绪级别转换为分数
        """
        mood_scores = {
            MoodLevel.VERY_SAD: 1,
            MoodLevel.SAD: 2,
            MoodLevel.NEUTRAL: 3,
            MoodLevel.HAPPY: 4,
            MoodLevel.VERY_HAPPY: 5
        }
        return mood_scores.get(mood_level, 3)
    
    def _score_to_mood_level(self, score: float) -> MoodLevel:
        """
        将分数转换为情绪级别
        """
        if score <= 1.5:
            return MoodLevel.VERY_SAD
        elif score <= 2.5:
            return MoodLevel.SAD
        elif score <= 3.5:
            return MoodLevel.NEUTRAL
        elif score <= 4.5:
            return MoodLevel.HAPPY
        else:
            return MoodLevel.VERY_HAPPY
    
    def _calculate_trend(self, daily_averages: List[Dict[str, Any]]) -> str:
        """
        计算情绪趋势
        """
        if len(daily_averages) < 7:
            return "insufficient_data"
        
        # 使用最近7天的数据计算趋势
        recent_data = daily_averages[-7:]
        first_half = recent_data[:3]
        second_half = recent_data[4:]
        
        first_avg = sum(d["average_mood"] for d in first_half) / len(first_half)
        second_avg = sum(d["average_mood"] for d in second_half) / len(second_half)
        
        difference = second_avg - first_avg
        
        if difference > 0.5:
            return "improving"
        elif difference < -0.5:
            return "declining"
        else:
            return "stable"
    
    def get_emotion_insights(
        self,
        db: Session,
        user_id: int,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        获取情感洞察
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            days: 分析天数
            
        Returns:
            情感洞察数据
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 获取情感日记
        diaries = db.query(EmotionDiary).filter(
            EmotionDiary.user_id == user_id,
            EmotionDiary.created_at >= start_date
        ).all()
        
        # 统计情绪类型分布
        emotion_distribution = {}
        for diary in diaries:
            if diary.emotion_type:
                emotion_type = diary.emotion_type.value if hasattr(diary.emotion_type, 'value') else diary.emotion_type
                emotion_distribution[emotion_type] = emotion_distribution.get(emotion_type, 0) + 1
        
        # 最常见的情绪
        most_common_emotion = None
        if emotion_distribution:
            most_common_emotion = max(emotion_distribution.items(), key=lambda x: x[1])[0]
        
        # 情绪触发模式分析
        trigger_patterns = self._analyze_trigger_patterns(diaries)
        
        # 情绪周期分析
        weekly_pattern = self._analyze_weekly_pattern(diaries)
        
        return {
            "period_days": days,
            "total_diaries": len(diaries),
            "emotion_distribution": emotion_distribution,
            "most_common_emotion": most_common_emotion,
            "trigger_patterns": trigger_patterns,
            "weekly_pattern": weekly_pattern,
            "insights": self._generate_emotion_insights(emotion_distribution, trigger_patterns, weekly_pattern)
        }
    
    def _analyze_trigger_patterns(self, diaries: List[EmotionDiary]) -> Dict[str, Any]:
        """
        分析情绪触发模式
        """
        trigger_keywords = ["工作", "家庭", "朋友", "健康", "学习", "金钱", "感情"]
        trigger_counts = {keyword: 0 for keyword in trigger_keywords}
        
        for diary in diaries:
            if diary.content:
                for keyword in trigger_keywords:
                    if keyword in diary.content:
                        trigger_counts[keyword] += 1
        
        # 找出最常见的触发因素
        top_triggers = sorted(
            [(k, v) for k, v in trigger_counts.items() if v > 0],
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        return {
            "trigger_counts": trigger_counts,
            "top_triggers": [{"trigger": t[0], "count": t[1]} for t in top_triggers]
        }
    
    def _analyze_weekly_pattern(self, diaries: List[EmotionDiary]) -> Dict[str, Any]:
        """
        分析周模式
        """
        days_of_week = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        weekly_moods = {day: [] for day in days_of_week}
        
        for diary in diaries:
            if diary.created_at:
                day_idx = diary.created_at.weekday()
                if diary.mood_level:
                    mood_score = self._mood_level_to_score(diary.mood_level)
                    weekly_moods[days_of_week[day_idx]].append(mood_score)
        
        # 计算每日平均情绪
        weekly_averages = []
        for day in days_of_week:
            moods = weekly_moods[day]
            if moods:
                avg_mood = sum(moods) / len(moods)
                weekly_averages.append({
                    "day": day,
                    "average_mood": avg_mood,
                    "record_count": len(moods)
                })
            else:
                weekly_averages.append({
                    "day": day,
                    "average_mood": 0,
                    "record_count": 0
                })
        
        # 找出最佳和最差情绪日
        if weekly_averages:
            best_day = max(weekly_averages, key=lambda x: x["average_mood"] if x["record_count"] > 0 else -1)
            worst_day = min(weekly_averages, key=lambda x: x["average_mood"] if x["record_count"] > 0 else 10)
        else:
            best_day = None
            worst_day = None
        
        return {
            "weekly_averages": weekly_averages,
            "best_day": best_day,
            "worst_day": worst_day
        }
    
    def _generate_emotion_insights(
        self,
        emotion_distribution: Dict[str, int],
        trigger_patterns: Dict[str, Any],
        weekly_pattern: Dict[str, Any]
    ) -> List[str]:
        """
        生成情感洞察
        """
        insights = []
        
        # 基于情绪分布的洞察
        if emotion_distribution:
            positive_emotions = ["快乐", "平静", "感激", "兴奋"]
            negative_emotions = ["悲伤", "焦虑", "愤怒", "压力"]
            
            positive_count = sum(emotion_distribution.get(e, 0) for e in positive_emotions)
            negative_count = sum(emotion_distribution.get(e, 0) for e in negative_emotions)
            
            if positive_count > negative_count * 2:
                insights.append("你近期的积极情绪非常突出，继续保持这种积极的心态！")
            elif negative_count > positive_count:
                insights.append("你近期可能经历了一些困难，建议尝试一些放松技巧或寻求支持。")
        
        # 基于触发模式的洞察
        if trigger_patterns.get("top_triggers"):
            top_trigger = trigger_patterns["top_triggers"][0] if trigger_patterns["top_triggers"] else None
            if top_trigger:
                insights.append(f"你提到最多的话题是'{top_trigger['trigger']}'，这可能是你情绪变化的重要因素。")
        
        # 基于周模式的洞察
        if weekly_pattern.get("best_day") and weekly_pattern["best_day"]["record_count"] > 0:
            insights.append(f"你在{weekly_pattern['best_day']['day']}的情绪通常最好，可以在这一天安排更多积极的活动。")
        
        return insights
    
    def get_conversation_analysis(
        self,
        db: Session,
        user_id: int,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        获取对话分析
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            days: 分析天数
            
        Returns:
            对话分析数据
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 获取对话数量
        conversation_count = db.query(func.count(Conversation.id)).filter(
            Conversation.user_id == user_id,
            Conversation.created_at >= start_date
        ).scalar()
        
        # 获取消息数量
        message_count = db.query(func.count(Message.id)).join(
            Conversation, Message.conversation_id == Conversation.id
        ).filter(
            Conversation.user_id == user_id,
            Message.created_at >= start_date
        ).scalar()
        
        # 获取用户消息和AI消息数量
        user_message_count = db.query(func.count(Message.id)).join(
            Conversation, Message.conversation_id == Conversation.id
        ).filter(
            Conversation.user_id == user_id,
            Message.created_at >= start_date,
            Message.role == "user"
        ).scalar()
        
        ai_message_count = db.query(func.count(Message.id)).join(
            Conversation, Message.conversation_id == Conversation.id
        ).filter(
            Conversation.user_id == user_id,
            Message.created_at >= start_date,
            Message.role == "assistant"
        ).scalar()
        
        # 获取每日对话统计
        daily_conversations = db.query(
            func.date(Conversation.created_at).label('date'),
            func.count(Conversation.id).label('count')
        ).filter(
            Conversation.user_id == user_id,
            Conversation.created_at >= start_date
        ).group_by(
            func.date(Conversation.created_at)
        ).order_by(
            func.date(Conversation.created_at)
        ).all()
        
        daily_stats = [
            {"date": str(dc.date), "count": dc.count}
            for dc in daily_conversations
        ]
        
        # 计算活跃度
        active_days = len(daily_stats)
        average_conversations_per_day = conversation_count / active_days if active_days > 0 else 0
        
        return {
            "period_days": days,
            "conversation_count": conversation_count,
            "message_count": message_count,
            "user_message_count": user_message_count,
            "ai_message_count": ai_message_count,
            "daily_conversations": daily_stats,
            "active_days": active_days,
            "average_conversations_per_day": round(average_conversations_per_day, 2),
            "engagement_level": self._calculate_engagement_level(conversation_count, days)
        }
    
    def _calculate_engagement_level(self, conversation_count: int, days: int) -> str:
        """
        计算参与度级别
        """
        avg_per_day = conversation_count / days
        
        if avg_per_day >= 2:
            return "high"
        elif avg_per_day >= 0.5:
            return "medium"
        else:
            return "low"
    
    def generate_personalized_report(
        self,
        db: Session,
        user_id: int,
        report_type: str = "weekly"
    ) -> Dict[str, Any]:
        """
        生成个性化报告
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            report_type: 报告类型
            
        Returns:
            个性化报告数据
        """
        if report_type == "weekly":
            days = 7
        elif report_type == "monthly":
            days = 30
        elif report_type == "quarterly":
            days = 90
        else:
            days = 7
        
        # 获取各部分分析数据
        mood_analysis = self.get_mood_trend_analysis(db, user_id, days)
        emotion_insights = self.get_emotion_insights(db, user_id, days)
        conversation_analysis = self.get_conversation_analysis(db, user_id, days)
        
        # 生成综合建议
        recommendations = self._generate_recommendations(mood_analysis, emotion_insights, conversation_analysis)
        
        return {
            "report_type": report_type,
            "period_days": days,
            "generated_at": datetime.utcnow().isoformat(),
            "mood_analysis": mood_analysis,
            "emotion_insights": emotion_insights,
            "conversation_analysis": conversation_analysis,
            "recommendations": recommendations,
            "summary": self._generate_summary(mood_analysis, emotion_insights, conversation_analysis)
        }
    
    def _generate_recommendations(
        self,
        mood_analysis: Dict[str, Any],
        emotion_insights: Dict[str, Any],
        conversation_analysis: Dict[str, Any]
    ) -> List[str]:
        """
        生成个性化建议
        """
        recommendations = []
        
        # 基于情绪趋势的建议
        if mood_analysis.get("trend") == "declining":
            recommendations.append("你的情绪近期有所下降，建议增加一些你喜欢的活动来提升心情。")
        elif mood_analysis.get("trend") == "stable":
            recommendations.append("你的情绪保持稳定，继续保持良好的生活习惯！")
        elif mood_analysis.get("trend") == "improving":
            recommendations.append("你的情绪正在改善，做得很好！继续保持积极的心态。")
        
        # 基于参与度的建议
        if conversation_analysis.get("engagement_level") == "low":
            recommendations.append("建议增加与AI助手的交流频率，这有助于你更好地了解自己的情绪变化。")
        
        # 基于触发模式的建议
        if emotion_insights.get("trigger_patterns", {}).get("top_triggers"):
            top_trigger = emotion_insights["trigger_patterns"]["top_triggers"][0] if emotion_insights["trigger_patterns"]["top_triggers"] else None
            if top_trigger and top_trigger["count"] > 3:
                recommendations.append(f"'{top_trigger['trigger']}'是你经常提到的话题，建议深入探索这个话题，可能会有新的发现。")
        
        return recommendations
    
    def _generate_summary(
        self,
        mood_analysis: Dict[str, Any],
        emotion_insights: Dict[str, Any],
        conversation_analysis: Dict[str, Any]
    ) -> str:
        """
        生成报告总结
        """
        summary_parts = []
        
        # 情绪总结
        overall_mood = mood_analysis.get("overall_mood_level")
        if overall_mood:
            mood_desc = {
                MoodLevel.VERY_SAD: "很不好",
                MoodLevel.SAD: "不太好",
                MoodLevel.NEUTRAL: "平稳",
                MoodLevel.HAPPY: "不错",
                MoodLevel.VERY_HAPPY: "很好"
            }
            summary_parts.append(f"你的整体情绪状态{mood_desc.get(overall_mood, '平稳')}。")
        
        # 活跃度总结
        engagement = conversation_analysis.get("engagement_level")
        if engagement == "high":
            summary_parts.append("你非常活跃地使用了这个平台。")
        elif engagement == "medium":
            summary_parts.append("你有规律地使用了这个平台。")
        else:
            summary_parts.append("你偶尔使用了这个平台。")
        
        # 洞察数量总结
        insights_count = len(emotion_insights.get("insights", []))
        if insights_count > 0:
            summary_parts.append(f"我们发现了{insights_count}个值得关注的洞察。")
        
        return " ".join(summary_parts)


def get_analytics_insight_service() -> AnalyticsInsightService:
    """获取数据分析与洞察服务实例"""
    return AnalyticsInsightService()
