"""
用户长期记忆服务
存储和检索用户的个性化信息，为AI对话提供长期记忆支持
"""
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc, or_
import loguru

from app.models import UserLongTermMemory, UserMemoryInsight, UserPreference
from app.models.user_memory import MemoryType, MemoryImportance


class UserMemoryService:
    """用户长期记忆服务"""

    def __init__(self):
        pass

    # ============ 长期记忆操作 ============

    def add_memory(
        self,
        db: Session,
        user_id: int,
        memory_type: str,
        content: str,
        importance: int = 2,
        summary: Optional[str] = None,
        keywords: Optional[str] = None,
        source: str = "conversation",
        source_conversation_id: Optional[int] = None,
        source_message_id: Optional[int] = None,
        confidence: float = 1.0,
    ) -> UserLongTermMemory:
        """
        添加新的长期记忆

        Args:
            db: 数据库会话
            user_id: 用户ID
            memory_type: 记忆类型
            content: 记忆内容
            importance: 重要程度 1-4
            summary: 记忆摘要
            keywords: 关键词，逗号分隔
            source: 来源
            source_conversation_id: 来源对话ID
            source_message_id: 来源消息ID
            confidence: 置信度

        Returns:
            创建的记忆对象
        """
        memory = UserLongTermMemory(
            user_id=user_id,
            memory_type=memory_type,
            importance=importance,
            content=content,
            summary=summary,
            keywords=keywords,
            source=source,
            source_conversation_id=source_conversation_id,
            source_message_id=source_message_id,
            confidence=confidence,
            is_active=True,
            is_verified=False,
        )

        db.add(memory)
        db.commit()
        db.refresh(memory)

        loguru.logger.info(f"添加用户长期记忆: user_id={user_id}, type={memory_type}, id={memory.id}")

        return memory

    def get_memory(self, db: Session, user_id: int, memory_id: int) -> Optional[UserLongTermMemory]:
        """获取指定记忆"""
        return db.query(UserLongTermMemory).filter(
            and_(
                UserLongTermMemory.id == memory_id,
                UserLongTermMemory.user_id == user_id,
                UserLongTermMemory.is_active == True,
            )
        ).first()

    def list_memories(
        self,
        db: Session,
        user_id: int,
        memory_type: Optional[str] = None,
        min_importance: Optional[int] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[UserLongTermMemory], int]:
        """列出用户记忆"""
        query = db.query(UserLongTermMemory).filter(
            and_(
                UserLongTermMemory.user_id == user_id,
                UserLongTermMemory.is_active == True,
            )
        )

        if memory_type:
            query = query.filter(UserLongTermMemory.memory_type == memory_type)
        if min_importance:
            query = query.filter(UserLongTermMemory.importance >= min_importance)
        if keyword:
            query = query.filter(
                or_(
                    UserLongTermMemory.content.contains(keyword),
                    UserLongTermMemory.summary.contains(keyword),
                    UserLongTermMemory.keywords.contains(keyword),
                )
            )

        total = query.count()
        memories = query.order_by(
            desc(UserLongTermMemory.importance),
            desc(UserLongTermMemory.created_at)
        ).offset((page - 1) * page_size).limit(page_size).all()

        return memories, total

    def update_memory(
        self,
        db: Session,
        user_id: int,
        memory_id: int,
        updates: Dict[str, Any],
    ) -> Optional[UserLongTermMemory]:
        """更新记忆"""
        memory = self.get_memory(db, user_id, memory_id)
        if not memory:
            return None

        for key, value in updates.items():
            if hasattr(memory, key):
                setattr(memory, key, value)

        memory.updated_at = datetime.now()
        db.commit()
        db.refresh(memory)

        return memory

    def delete_memory(self, db: Session, user_id: int, memory_id: int) -> bool:
        """软删除记忆"""
        memory = self.get_memory(db, user_id, memory_id)
        if not memory:
            return False

        memory.is_active = False
        db.commit()
        return True

    def search_memories(
        self,
        db: Session,
        user_id: int,
        query: str,
        limit: int = 10,
        min_importance: int = 1,
    ) -> List[UserLongTermMemory]:
        """搜索用户记忆"""
        results = db.query(UserLongTermMemory).filter(
            and_(
                UserLongTermMemory.user_id == user_id,
                UserLongTermMemory.is_active == True,
                UserLongTermMemory.importance >= min_importance,
                or_(
                    UserLongTermMemory.content.contains(query),
                    UserLongTermMemory.summary.contains(query),
                    UserLongTermMemory.keywords.contains(query),
                )
            )
        ).order_by(
            desc(UserLongTermMemory.importance),
            desc(UserLongTermMemory.created_at)
        ).limit(limit).all()

        return results

    def get_relevant_memories(
        self,
        db: Session,
        user_id: int,
        conversation_context: str,
        limit: int = 5,
    ) -> List[UserLongTermMemory]:
        """
        根据当前对话上下文获取相关的长期记忆

        Args:
            db: 数据库会话
            user_id: 用户ID
            conversation_context: 当前对话上下文文本
            limit: 返回结果数量

        Returns:
            相关记忆列表
        """
        # 简单实现：基于关键词匹配
        # 更高级的实现可以用向量语义检索
        memories = db.query(UserLongTermMemory).filter(
            and_(
                UserLongTermMemory.user_id == user_id,
                UserLongTermMemory.is_active == True,
            )
        ).order_by(
            desc(UserLongTermMemory.importance),
            desc(UserLongTermMemory.created_at)
        ).limit(50).all()

        # 基于简单关键词匹配打分
        scored = []
        context_lower = conversation_context.lower()

        for memory in memories:
            score = 0
            # 重要性加权
            score += memory.importance * 2

            # 内容匹配
            if memory.content and any(word in memory.content.lower() for word in context_lower.split()):
                score += 3
            if memory.keywords:
                for kw in memory.keywords.split(','):
                    if kw.strip().lower() in context_lower:
                        score += 2
            if memory.summary and any(word in memory.summary.lower() for word in context_lower.split()):
                score += 1

            scored.append((score, memory))

        # 按分数排序
        scored.sort(reverse=True, key=lambda x: x[0])

        return [m for _, m in scored[:limit]]

    def get_formatted_memories_for_prompt(
        self,
        db: Session,
        user_id: int,
        conversation_context: str,
        limit: int = 5,
    ) -> str:
        """
        获取格式化的记忆文本用于拼接到提示词

        Args:
            db: 数据库会话
            user_id: 用户ID
            conversation_context: 当前对话上下文
            limit: 返回记忆数量

        Returns:
            格式化的记忆文本
        """
        relevant = self.get_relevant_memories(db, user_id, conversation_context, limit)

        if not relevant:
            return ""

        lines = ["\n【关于用户的重要信息：】"]
        for i, mem in enumerate(relevant, 1):
            summary = mem.summary or mem.content[:100]
            if len(mem.content) > 100 and not summary:
                summary = summary + "..."
            lines.append(f"{i}. {summary}")

        return "\n".join(lines)

    def get_statistics(self, db: Session, user_id: int) -> Dict[str, Any]:
        """获取用户记忆统计"""
        total = db.query(UserLongTermMemory).filter(
            and_(
                UserLongTermMemory.user_id == user_id,
                UserLongTermMemory.is_active == True,
            )
        ).count()

        type_counts = {}
        type_stats = db.query(
            UserLongTermMemory.memory_type,
            func.count(UserLongTermMemory.id)
        ).filter(
            and_(
                UserLongTermMemory.user_id == user_id,
                UserLongTermMemory.is_active == True,
            )
        ).group_by(UserLongTermMemory.memory_type).all()

        for mem_type, cnt in type_stats:
            type_counts[mem_type] = cnt

        importance_counts = {}
        imp_stats = db.query(
            UserLongTermMemory.importance,
            func.count(UserLongTermMemory.id)
        ).filter(
            and_(
                UserLongTermMemory.user_id == user_id,
                UserLongTermMemory.is_active == True,
            )
        ).group_by(UserLongTermMemory.importance).all()

        for imp, cnt in imp_stats:
            importance_counts[imp] = cnt

        return {
            "total_count": total,
            "by_type": type_counts,
            "by_importance": importance_counts,
        }

    # ============ 记忆洞察操作 ============

    def add_insight(
        self,
        db: Session,
        user_id: int,
        insight_type: str,
        content: str,
        supporting_memory_ids: Optional[List[int]] = None,
        confidence: float = 0.5,
    ) -> UserMemoryInsight:
        """添加记忆洞察"""
        memory_ids_str = ",".join(map(str, supporting_memory_ids)) if supporting_memory_ids else None

        insight = UserMemoryInsight(
            user_id=user_id,
            insight_type=insight_type,
            insight_content=content,
            supporting_memory_ids=memory_ids_str,
            confidence=confidence,
        )

        db.add(insight)
        db.commit()
        db.refresh(insight)

        return insight

    def list_insights(
        self,
        db: Session,
        user_id: int,
        insight_type: Optional[str] = None,
    ) -> List[UserMemoryInsight]:
        """列出用户洞察"""
        query = db.query(UserMemoryInsight).filter(UserMemoryInsight.user_id == user_id)

        if insight_type:
            query = query.filter(UserMemoryInsight.insight_type == insight_type)

        return query.order_by(desc(UserMemoryInsight.confidence), desc(UserMemoryInsight.created_at)).all()

    # ============ 用户偏好操作 ============

    def set_preference(
        self,
        db: Session,
        user_id: int,
        category: str,
        key: str,
        value: Any,
        source: str = "user",
    ) -> UserPreference:
        """设置用户偏好"""
        # 查找现有偏好
        existing = db.query(UserPreference).filter(
            and_(
                UserPreference.user_id == user_id,
                UserPreference.category == category,
                UserPreference.key == key,
            )
        ).first()

        # 判断值类型
        if isinstance(value, bool):
            value_type = "boolean"
            value_str = str(value).lower()
        elif isinstance(value, (int, float)):
            value_type = "number"
            value_str = str(value)
        elif isinstance(value, dict) or isinstance(value, list):
            value_type = "json"
            import json
            value_str = json.dumps(value)
        else:
            value_type = "string"
            value_str = str(value)

        if existing:
            existing.value = value_str
            existing.value_type = value_type
            existing.source = source
            existing.updated_at = datetime.now()
            pref = existing
        else:
            pref = UserPreference(
                user_id=user_id,
                category=category,
                key=key,
                value=value_str,
                value_type=value_type,
                source=source,
            )
            db.add(pref)

        db.commit()
        db.refresh(pref)

        return pref

    def get_preference(
        self,
        db: Session,
        user_id: int,
        category: str,
        key: str,
        default: Any = None,
    ) -> Any:
        """获取用户偏好"""
        pref = db.query(UserPreference).filter(
            and_(
                UserPreference.user_id == user_id,
                UserPreference.category == category,
                UserPreference.key == key,
            )
        ).first()

        if not pref:
            return default

        # 根据类型转换
        if pref.value_type == "boolean":
            return pref.value.lower() == "true"
        elif pref.value_type == "number":
            try:
                return float(pref.value) if "." in pref.value else int(pref.value)
            except:
                return pref.value
        elif pref.value_type == "json":
            import json
            try:
                return json.loads(pref.value)
            except:
                return pref.value
        else:
            return pref.value

    def get_category_preferences(
        self,
        db: Session,
        user_id: int,
        category: str,
    ) -> Dict[str, Any]:
        """获取某个分类下的所有用户偏好"""
        prefs = db.query(UserPreference).filter(
            and_(
                UserPreference.user_id == user_id,
                UserPreference.category == category,
            )
        ).all()

        result = {}
        for p in prefs:
            result[p.key] = self.get_preference(db, user_id, category, p.key)

        return result

    def delete_preference(
        self,
        db: Session,
        user_id: int,
        category: str,
        key: str,
    ) -> bool:
        """删除用户偏好"""
        pref = db.query(UserPreference).filter(
            and_(
                UserPreference.user_id == user_id,
                UserPreference.category == category,
                UserPreference.key == key,
            )
        ).first()

        if not pref:
            return False

        db.delete(pref)
        db.commit()
        return True


# 全局服务实例
_user_memory_service: Optional[UserMemoryService] = None


def get_user_memory_service() -> UserMemoryService:
    """获取用户长期记忆服务实例"""
    global _user_memory_service
    if _user_memory_service is None:
        _user_memory_service = UserMemoryService()
    return _user_memory_service
