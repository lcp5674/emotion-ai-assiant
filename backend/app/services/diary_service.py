"""
情感日记服务
"""
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
import loguru

from app.models import User
from app.models.diary import EmotionDiary, MoodRecord, DiaryTag, MoodLevel, EmotionType

from app.schemas.diary import DiaryCreate, DiaryUpdate, MoodCreate, TagCreate, TagUpdate


class DiaryService:
    """情感日记服务"""

    # 情绪配置
    EMOTION_CONFIGS = {
        "happy": {"name": "开心", "label": "开心", "color": "#FFD700", "emoji": "😊", "description": "感到快乐和满足"},
        "sad": {"name": "难过", "label": "难过", "color": "#A29BFE", "emoji": "😢", "description": "感到悲伤和失落"},
        "angry": {"name": "生气", "label": "生气", "color": "#FF4757", "emoji": "😠", "description": "感到愤怒和不满"},
        "calm": {"name": "平静", "label": "平静", "color": "#74B9FF", "emoji": "😌", "description": "内心宁静和平和"},
        "excited": {"name": "兴奋", "label": "兴奋", "color": "#FF6B6B", "emoji": "🎉", "description": "充满激情和活力"},
        "anxious": {"name": "焦虑", "label": "焦虑", "color": "#FD79A8", "emoji": "😰", "description": "感到紧张和不安"},
        "confused": {"name": "困惑", "label": "困惑", "color": "#00CEC9", "emoji": "🤔", "description": "感到迷茫和不确定"},
        "surprised": {"name": "惊讶", "label": "惊讶", "color": "#EB2F96", "emoji": "😮", "description": "感到意外和惊讶"},
    }

    # 心情等级配置
    MOOD_CONFIGS = {
        "terrible": {"level": "terrible", "label": "糟糕", "score_range": [1, 2], "color": "#FF4757", "emoji": "😢", "description": "感觉非常糟糕"},
        "bad": {"level": "bad", "label": "不好", "score_range": [3, 4], "color": "#FA8C16", "emoji": "😔", "description": "感觉不太好"},
        "neutral": {"level": "neutral", "label": "一般", "score_range": [5, 5], "color": "#FAAD14", "emoji": "😐", "description": "感觉一般"},
        "good": {"level": "good", "label": "不错", "score_range": [6, 8], "color": "#52C41A", "emoji": "🙂", "description": "感觉不错"},
        "excellent": {"level": "excellent", "label": "很棒", "score_range": [9, 10], "color": "#1890FF", "emoji": "😄", "description": "感觉非常棒"},
    }

    def _get_mood_level(self, score: int) -> str:
        """根据分数获取心情等级"""
        for level, config in self.MOOD_CONFIGS.items():
            if config["score_range"][0] <= score <= config["score_range"][1]:
                return level
        return "neutral"

    # ============ 日记操作 ============

    async def create_diary(self, db: Session, user_id: int, request: DiaryCreate) -> EmotionDiary:
        """创建日记"""
        try:
            db.begin()
            
            from datetime import datetime
            # 输入验证
            if not request.date:
                raise ValueError("日期不能为空")
            if request.mood_score < 1 or request.mood_score > 10:
                raise ValueError("心情评分必须在1-10之间")
            if not request.content or len(request.content.strip()) < 10:
                raise ValueError("日记内容至少10个字符")
            if request.primary_emotion and request.primary_emotion not in [e.value for e in EmotionType]:
                raise ValueError("无效的情绪类型")

            # 转换日期字符串为date对象
            diary_date = datetime.strptime(request.date, "%Y-%m-%d").date()
            
            # 检查该日期是否已有日记
            existing = db.query(EmotionDiary).filter(
                and_(
                    EmotionDiary.user_id == user_id,
                    EmotionDiary.date == diary_date,
                    EmotionDiary.is_deleted == False,
                )
            ).first()

            if existing:
                raise ValueError(f"{request.date} 已经有日记记录了")

            mood_level = request.mood_level or self._get_mood_level(request.mood_score)

            diary = EmotionDiary(
                user_id=user_id,
                date=diary_date,
                mood_score=request.mood_score,
                mood_level=MoodLevel(mood_level) if mood_level else None,
                primary_emotion=EmotionType(request.primary_emotion) if request.primary_emotion else None,
                secondary_emotions=request.secondary_emotions,
                emotion_tags=request.emotion_tags,
                content=request.content,
                category=request.category,
                tags=request.tags,
                is_shared=request.is_shared,
                share_public=request.share_public,
                analysis_status="pending",
            )

            db.add(diary)
            db.commit()
            db.refresh(diary)

            # 更新标签使用计数
            if request.tags:
                self._update_tag_usage(db, user_id, request.tags, 1)

            return diary
        except Exception as e:
            db.rollback()
            raise

    def get_diary(self, db: Session, user_id: int, diary_id: int) -> Optional[EmotionDiary]:
        """获取日记详情"""
        return db.query(EmotionDiary).filter(
            and_(
                EmotionDiary.id == diary_id,
                EmotionDiary.user_id == user_id,
                EmotionDiary.is_deleted == False,
            )
        ).first()

    def get_diary_by_date(self, db: Session, user_id: int, diary_date: date) -> Optional[EmotionDiary]:
        """根据日期获取日记"""
        return db.query(EmotionDiary).filter(
            and_(
                EmotionDiary.user_id == user_id,
                EmotionDiary.date == diary_date,
                EmotionDiary.is_deleted == False,
            )
        ).first()

    def list_diaries(
        self,
        db: Session,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        mood_level: Optional[str] = None,
        emotion: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[List[EmotionDiary], int]:
        """获取日记列表"""
        query = db.query(EmotionDiary).filter(
            and_(
                EmotionDiary.user_id == user_id,
                EmotionDiary.is_deleted == False,
            )
        )

        if start_date:
            query = query.filter(EmotionDiary.date >= start_date)
        if end_date:
            query = query.filter(EmotionDiary.date <= end_date)
        if mood_level:
            query = query.filter(EmotionDiary.mood_level == MoodLevel(mood_level))
        if emotion:
            query = query.filter(EmotionDiary.primary_emotion == EmotionType(emotion))
        if category:
            query = query.filter(EmotionDiary.category == category)
        if tags:
            tag_list = [t.strip() for t in tags.split(",")]
            for tag in tag_list:
                query = query.filter(EmotionDiary.tags.like(f"%{tag}%"))

        total = query.count()

        diaries = query.order_by(desc(EmotionDiary.date)).offset(
            (page - 1) * page_size
        ).limit(page_size).all()

        return diaries, total

    async def update_diary(
        self,
        db: Session,
        user_id: int,
        diary_id: int,
        request: DiaryUpdate,
    ) -> Optional[EmotionDiary]:
        """更新日记"""
        diary = self.get_diary(db, user_id, diary_id)
        if not diary:
            return None

        old_tags = diary.tags or ""

        update_data = request.model_dump(exclude_unset=True)

        if "mood_score" in update_data:
            if request.mood_level:
                update_data["mood_level"] = request.mood_level
            else:
                mood_level_str = self._get_mood_level(request.mood_score)
                update_data["mood_level"] = mood_level_str
        if "secondary_emotions" in update_data and request.secondary_emotions:
            update_data["secondary_emotions"] = request.secondary_emotions

        for key, value in update_data.items():
            if hasattr(diary, key):
                setattr(diary, key, value)

        # 如果内容更新了，重新设置分析状态
        if "content" in update_data:
            diary.analysis_status = "pending"

        # 更新标签使用计数
        if "tags" in update_data:
            self._update_tag_usage(db, user_id, old_tags, -1)
            self._update_tag_usage(db, user_id, request.tags or "", 1)

        db.commit()
        db.refresh(diary)
        return diary

    def delete_diary(self, db: Session, user_id: int, diary_id: int) -> bool:
        """删除日记（软删除）"""
        diary = self.get_diary(db, user_id, diary_id)
        if not diary:
            return False

        # 减少标签使用计数
        if diary.tags:
            self._update_tag_usage(db, user_id, diary.tags, -1)

        diary.is_deleted = True
        db.commit()
        return True

    # ============ 心情记录操作 ============

    def create_mood_record(self, db: Session, user_id: int, request: MoodCreate) -> MoodRecord:
        """创建心情快速记录"""
        mood_level = request.mood_level or self._get_mood_level(request.mood_score)

        record = MoodRecord(
            user_id=user_id,
            mood_score=request.mood_score,
            mood_level=MoodLevel(mood_level) if mood_level else None,
            emotion=EmotionType(request.emotion) if request.emotion else None,
            note=request.note,
            location=request.location,
            activity=request.activity,
        )

        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def list_mood_records(
        self,
        db: Session,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100,
    ) -> List[MoodRecord]:
        """获取心情记录列表"""
        query = db.query(MoodRecord).filter(MoodRecord.user_id == user_id)

        if start_date:
            query = query.filter(func.date(MoodRecord.created_at) >= start_date)
        if end_date:
            query = query.filter(func.date(MoodRecord.created_at) <= end_date)

        return query.order_by(desc(MoodRecord.created_at)).limit(limit).all()

    # ============ 标签操作 ============

    def create_tag(self, db: Session, user_id: int, request: TagCreate) -> DiaryTag:
        """创建标签"""
        # 检查是否已存在同名标签
        existing = db.query(DiaryTag).filter(
            and_(
                DiaryTag.user_id == user_id,
                DiaryTag.name == request.name,
            )
        ).first()

        if existing:
            raise ValueError("该标签已存在")

        tag = DiaryTag(
            user_id=user_id,
            name=request.name,
            color=request.color,
            use_count=0,
        )

        db.add(tag)
        db.commit()
        db.refresh(tag)
        return tag

    def list_tags(self, db: Session, user_id: int) -> List[DiaryTag]:
        """获取用户标签列表"""
        return db.query(DiaryTag).filter(
            DiaryTag.user_id == user_id
        ).order_by(desc(DiaryTag.use_count), DiaryTag.name).all()

    def update_tag(
        self,
        db: Session,
        user_id: int,
        tag_id: int,
        request: TagUpdate,
    ) -> Optional[DiaryTag]:
        """更新标签"""
        tag = db.query(DiaryTag).filter(
            and_(
                DiaryTag.id == tag_id,
                DiaryTag.user_id == user_id,
            )
        ).first()

        if not tag:
            return None

        update_data = request.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(tag, key):
                setattr(tag, key, value)

        db.commit()
        db.refresh(tag)
        return tag

    def delete_tag(self, db: Session, user_id: int, tag_id: int) -> bool:
        """删除标签"""
        tag = db.query(DiaryTag).filter(
            and_(
                DiaryTag.id == tag_id,
                DiaryTag.user_id == user_id,
            )
        ).first()

        if not tag:
            return False

        db.delete(tag)
        db.commit()
        return True

    def _update_tag_usage(self, db: Session, user_id: int, tags_str: str, delta: int):
        """更新标签使用计数"""
        if not tags_str:
            return

        tag_names = [t.strip() for t in tags_str.split(",") if t.strip()]

        for tag_name in tag_names:
            tag = db.query(DiaryTag).filter(
                and_(
                    DiaryTag.user_id == user_id,
                    DiaryTag.name == tag_name,
                )
            ).first()

            if tag:
                tag.use_count = max(0, tag.use_count + delta)
            elif delta > 0:
                # 自动创建新标签
                new_tag = DiaryTag(user_id=user_id, name=tag_name, use_count=1)
                db.add(new_tag)

        db.commit()

    # ============ 统计和趋势 ============

    def get_mood_trend(
        self,
        db: Session,
        user_id: int,
        time_range: str = "week",  # week/month/quarter/year
    ) -> Dict[str, Any]:
        """获取心情趋势"""
        today = date.today()

        if time_range == "week":
            start_date = today - timedelta(days=7)
        elif time_range == "month":
            start_date = today - timedelta(days=30)
        elif time_range == "quarter":
            start_date = today - timedelta(days=90)
        elif time_range == "year":
            start_date = today - timedelta(days=365)
        else:
            start_date = today - timedelta(days=7)

        # 获取范围内的日记
        diaries = db.query(EmotionDiary).filter(
            and_(
                EmotionDiary.user_id == user_id,
                EmotionDiary.date >= start_date,
                EmotionDiary.date <= today,
                EmotionDiary.is_deleted == False,
            )
        ).order_by(EmotionDiary.date).all()

        # 计算趋势数据
        trend_data = []
        emotion_distribution = {}
        mood_distribution = {}
        total_score = 0

        for diary in diaries:
            total_score += diary.mood_score

            # 趋势点
            trend_data.append({
                "date": diary.date,
                "mood_score": diary.mood_score,
                "mood_level": diary.mood_level.value if diary.mood_level else None,
                "primary_emotion": diary.primary_emotion.value if diary.primary_emotion else None,
                "count": 1,
            })

            # 情绪分布
            if diary.primary_emotion:
                emo_key = diary.primary_emotion.value
                emotion_distribution[emo_key] = emotion_distribution.get(emo_key, 0) + 1

            # 心情等级分布
            if diary.mood_level:
                mood_key = diary.mood_level.value
                mood_distribution[mood_key] = mood_distribution.get(mood_key, 0) + 1

        avg_score = total_score / len(diaries) if diaries else 0

        return {
            "time_range": time_range,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": today.isoformat() if today else None,
            "avg_score": round(avg_score, 2),
            "trend_data": trend_data,
            "emotion_distribution": emotion_distribution,
            "mood_distribution": mood_distribution,
        }

    def get_stats(self, db: Session, user_id: int) -> Dict[str, Any]:
        """获取日记统计"""
        # 总日记数
        total_count = db.query(EmotionDiary).filter(
            and_(
                EmotionDiary.user_id == user_id,
                EmotionDiary.is_deleted == False,
            )
        ).count()

        # 计算连续记录天数
        diaries = db.query(EmotionDiary).filter(
            and_(
                EmotionDiary.user_id == user_id,
                EmotionDiary.is_deleted == False,
            )
        ).order_by(desc(EmotionDiary.date)).all()

        current_streak = 0
        max_streak = 0
        temp_streak = 0
        expected_date = date.today()

        for diary in diaries:
            if diary.date == expected_date:
                temp_streak += 1
                expected_date -= timedelta(days=1)
            elif diary.date < expected_date:
                if temp_streak > max_streak:
                    max_streak = temp_streak
                if current_streak == 0:
                    current_streak = temp_streak
                temp_streak = 1
                expected_date = diary.date - timedelta(days=1)

        if temp_streak > max_streak:
            max_streak = temp_streak
        if current_streak == 0:
            current_streak = temp_streak

        # 平均心情
        avg_mood_query = db.query(func.avg(EmotionDiary.mood_score)).filter(
            and_(
                EmotionDiary.user_id == user_id,
                EmotionDiary.is_deleted == False,
            )
        ).scalar()
        avg_mood = float(avg_mood_query) if avg_mood_query else 0

        # 最常见情绪
        emotion_query = db.query(
            EmotionDiary.primary_emotion,
            func.count(EmotionDiary.primary_emotion).label("count"),
        ).filter(
            and_(
                EmotionDiary.user_id == user_id,
                EmotionDiary.primary_emotion.isnot(None),
                EmotionDiary.is_deleted == False,
            )
        ).group_by(EmotionDiary.primary_emotion).order_by(desc("count")).first()

        most_common_emotion = emotion_query[0].value if emotion_query else None

        # 分类统计
        category_query = db.query(
            EmotionDiary.category,
            func.count(EmotionDiary.category).label("count"),
        ).filter(
            and_(
                EmotionDiary.user_id == user_id,
                EmotionDiary.category.isnot(None),
                EmotionDiary.is_deleted == False,
            )
        ).group_by(EmotionDiary.category).all()

        categories = {cat: cnt for cat, cnt in category_query}

        # 本月和上月记录数
        today = date.today()
        this_month_start = date(today.year, today.month, 1)
        last_month_start = date(today.year, today.month - 1, 1) if today.month > 1 else date(today.year - 1, 12, 1)

        this_month_count = db.query(func.count(EmotionDiary.id)).filter(
            and_(
                EmotionDiary.user_id == user_id,
                EmotionDiary.date >= this_month_start,
                EmotionDiary.is_deleted == False,
            )
        ).scalar() or 0

        last_month_count = db.query(func.count(EmotionDiary.id)).filter(
            and_(
                EmotionDiary.user_id == user_id,
                EmotionDiary.date >= last_month_start,
                EmotionDiary.date < this_month_start,
                EmotionDiary.is_deleted == False,
            )
        ).scalar() or 0

        # 平均字数
        word_count_query = db.query(func.avg(func.length(EmotionDiary.content))).filter(
            and_(
                EmotionDiary.user_id == user_id,
                EmotionDiary.content.isnot(None),
                EmotionDiary.is_deleted == False,
            )
        ).scalar()
        avg_words = float(word_count_query) if word_count_query else 0

        return {
            "total_count": total_count,
            "current_streak": current_streak,
            "max_streak": max_streak,
            "avg_mood": round(avg_mood, 2),
            "most_common_emotion": most_common_emotion,
            "avg_words_per_day": round(avg_words, 2),
            "categories": categories,
            "this_month_count": this_month_count,
            "last_month_count": last_month_count,
        }

    # ============ AI分析 ============

    async def analyze_diary(
        self,
        db: Session,
        user_id: int,
        diary_id: int,
    ) -> Optional[Dict[str, Any]]:
        """AI分析日记"""
        from app.services.llm import chat

        diary = self.get_diary(db, user_id, diary_id)
        if not diary:
            return None

        if not diary.content:
            return {"status": "no_content", "analysis": None, "suggestion": None}

        diary.analysis_status = "processing"
        db.commit()

        try:
            # 构建提示词
            prompt = f"""
请分析以下情感日记，提供专业的情绪分析和建议。

日记信息：
- 日期：{diary.date}
- 心情评分：{diary.mood_score}/10

日记内容：
{diary.content}

请以JSON格式返回分析结果，包含以下字段：
{{
    "analysis": "情绪分析（200字以内）",
    "suggestion": "建议（200字以内）",
    "keywords": ["关键词1", "关键词2", "关键词3"]
}}
"""

            # 调用大模型
            result = await chat(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000,
            )

            # 解析结果
            import json
            try:
                # 尝试解析JSON
                start_idx = result.find("{")
                end_idx = result.rfind("}") + 1
                if start_idx != -1 and end_idx != -1:
                    json_str = result[start_idx:end_idx]
                    analysis_result = json.loads(json_str)
                else:
                    analysis_result = {"analysis": result, "suggestion": "继续保持记录，观察情绪变化。", "keywords": []}
            except:
                analysis_result = {"analysis": result, "suggestion": "继续保持记录，观察情绪变化。", "keywords": []}

            # 更新日记
            diary.ai_analysis = analysis_result.get("analysis", "")
            diary.ai_suggestion = analysis_result.get("suggestion", "")
            diary.analysis_status = "completed"
            db.commit()
            db.refresh(diary)

            return {
                "status": "completed",
                "analysis": diary.ai_analysis,
                "suggestion": diary.ai_suggestion,
                "keywords": analysis_result.get("keywords", []),
            }

        except Exception as e:
            loguru.logger.error(f"AI分析失败: {e}")
            diary.analysis_status = "failed"
            db.commit()
            return {"status": "failed", "analysis": None, "suggestion": None}


# 全局服务实例
_diary_service: Optional[DiaryService] = None


def get_diary_service() -> DiaryService:
    """获取日记服务实例"""
    global _diary_service
    if _diary_service is None:
        _diary_service = DiaryService()
    return _diary_service
