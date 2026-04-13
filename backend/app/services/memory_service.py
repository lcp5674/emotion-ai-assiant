"""
用户记忆服务 - 长期记忆存储 + 知识图谱 + 数据同步
"""
from typing import List, Dict, Any, Optional
import json
import loguru

from app.core.database import SessionLocal
from app.services.rag.vectorstore import get_vector_store
from app.services.cache_service import get_session_memory


class MemoryType:
    """记忆类型枚举"""
    MBTI_RESULT = "mbti_result"      # MBTI测试结果
    DIARY = "diary"                  # 情感日记
    PREFERENCE = "preference"        # 用户偏好
    EVENT = "event"                  # 重要事件
    CONVERSATION = "conversation"    # 对话摘要
    HABIT = "habit"                  # 习惯


class MemoryService:
    """用户记忆服务"""

    # 用户记忆集合名称
    USER_MEMORY_COLLECTION = "user_memories"

    def __init__(self):
        from app.core.config import settings
        self.vector_store = get_vector_store()
        self.session_memory = get_session_memory()
        # 用户记忆使用单独的 collection
        self.user_collection = settings.MILVUS_COLLECTION  # 使用主 collection，依赖 metadata 区分

    # ==================== 用户记忆管理 ====================

    async def add_user_memory(
        self,
        user_id: int,
        content: str,
        memory_type: str,
        metadata: Optional[Dict] = None
    ) -> bool:
        """添加用户记忆到向量数据库"""
        try:
            # 构建metadata
            meta = {
                "user_id": str(user_id),
                "memory_type": memory_type,
                "collection": self.USER_MEMORY_COLLECTION,
            }
            if metadata:
                meta.update(metadata)

            # 添加到向量库
            texts = [content]
            metadatas = [meta]

            # 调用 vector_store 添加文本
            ids = await self.vector_store.add_texts(texts, metadatas)

            loguru.logger.info(f"添加用户记忆: user_id={user_id}, type={memory_type}, id={ids}")

            return len(ids) > 0
        except Exception as e:
            loguru.logger.error(f"添加用户记忆失败: {e}")
            return False

    async def search_user_memories(
        self,
        user_id: int,
        query: str,
        memory_types: Optional[List[str]] = None,
        top_k: int = 5
    ) -> List[Dict]:
        """检索用户记忆"""
        try:
            # 构建filter
            filter_conditions = {
                "user_id": str(user_id),
                "collection": self.USER_MEMORY_COLLECTION,
            }
            if memory_types:
                filter_conditions["memory_type"] = {"$in": memory_types}

            results = await self.vector_store.similarity_search(
                query=query,
                top_k=top_k,
                filter=filter_conditions
            )

            # 过滤用户记忆
            user_memories = [
                r for r in results
                if r.get("user_id") == str(user_id)
            ]

            return user_memories

        except Exception as e:
            loguru.logger.error(f"检索用户记忆失败: {e}")
            return []

    async def get_user_all_memories(
        self,
        user_id: int,
        memory_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """获取用户所有记忆（按类型）"""
        try:
            from app.core.database import SessionLocal
            from app.models.memory import UserMemory

            db = SessionLocal()
            try:
                query = db.query(UserMemory).filter(
                    UserMemory.user_id == user_id,
                    UserMemory.is_deleted == False,
                )

                if memory_type:
                    query = query.filter(UserMemory.memory_type == memory_type)

                memories = query.order_by(UserMemory.created_at.desc()).limit(limit).all()

                return [
                    {
                        "id": str(m.id),
                        "content": m.content,
                        "memory_type": m.memory_type,
                        "created_at": m.created_at.isoformat() if m.created_at else None,
                        "metadata": m.metadata or {},
                    }
                    for m in memories
                ]
            finally:
                db.close()
        except Exception as e:
            loguru.logger.error(f"获取用户记忆列表失败: {e}")
            return []

    async def delete_user_memory(self, user_id: int, memory_id: str) -> bool:
        """删除用户记忆"""
        try:
            await self.vector_store.delete([memory_id])
            return True
        except Exception as e:
            loguru.logger.error(f"删除用户记忆失败: {e}")
            return False

    # ==================== MBTI 结果同步 ====================

    async def sync_mbti_result(self, user_id: int, mbti_result: Dict) -> bool:
        """同步MBTI结果到记忆系统"""
        try:
            mbti_type = mbti_result.get("mbti_type", "")
            dimensions = mbti_result.get("dimensions", [])
            personality = mbti_result.get("personality", "")

            # 构建记忆内容
            content = f"""用户MBTI类型: {mbti_type}

性格特征:
{personality}

维度得分:
"""
            for dim in dimensions:
                content += f"- {dim.get('dimension', '')}: {dim.get('score', 0)} ({dim.get('倾向', '')})"

            metadata = {
                "mbti_type": mbti_type,
                "test_date": mbti_result.get("created_at", ""),
                "title": f"MBTI测试结果: {mbti_type}",
            }

            await self.add_user_memory(
                user_id=user_id,
                content=content,
                memory_type=MemoryType.MBTI_RESULT,
                metadata=metadata
            )

            loguru.logger.info(f"MBTI结果已同步: user_id={user_id}, type={mbti_type}")
            return True

        except Exception as e:
            loguru.logger.error(f"同步MBTI结果失败: {e}")
            return False

    # ==================== 情感日记同步 ====================

    async def sync_diary(self, user_id: int, diary: Dict) -> bool:
        """同步情感日记到记忆系统"""
        try:
            content = f"""日期: {diary.get('date', '')}
情绪: {diary.get('emotion', '')}
心情等级: {diary.get('mood_level', '')}

内容:
{diary.get('content', '')}

分析:
{diary.get('analysis', '')}
"""

            metadata = {
                "diary_date": diary.get("date", ""),
                "emotion": diary.get("emotion", ""),
                "mood_level": diary.get("mood_level", ""),
                "title": f"情感日记: {diary.get('date', '')}",
            }

            await self.add_user_memory(
                user_id=user_id,
                content=content,
                memory_type=MemoryType.DIARY,
                metadata=metadata
            )

            loguru.logger.info(f"情感日记已同步: user_id={user_id}, date={diary.get('date')}")
            return True

        except Exception as e:
            loguru.logger.error(f"同步情感日记失败: {e}")
            return False

    async def sync_all_diaries(self, user_id: int) -> int:
        """同步用户所有日记"""
        db = SessionLocal()
        count = 0
        try:
            from app.models.diary import EmotionDiary
            diaries = db.query(EmotionDiary).filter(
                EmotionDiary.user_id == user_id
            ).all()

            for diary in diaries:
                diary_dict = {
                    "date": diary.date.isoformat() if diary.date else "",
                    "emotion": diary.emotion or "",
                    "mood_level": diary.mood_level or "",
                    "content": diary.content or "",
                    "analysis": diary.ai_analysis or "",
                }
                if await self.sync_diary(user_id, diary_dict):
                    count += 1

            loguru.logger.info(f"已同步 {count} 篇日记: user_id={user_id}")
            return count

        except Exception as e:
            loguru.logger.error(f"同步所有日记失败: {e}")
            return count
        finally:
            db.close()

    # ==================== 知识图谱 ====================

    def __init__(self):
        from app.core.config import settings
        self.vector_store = get_vector_store()
        self.session_memory = get_session_memory()
        # 用户记忆使用单独的 collection
        self.user_collection = settings.MILVUS_COLLECTION  # 使用主 collection，依赖 metadata 区分
        # Neo4j图数据库（生产级）
        self._neo4j_enabled = getattr(settings, 'NEO4J_ENABLED', False)
        self._neo4j_store = None

    async def _get_neo4j_store(self):
        """获取Neo4j存储实例（延迟加载）"""
        if self._neo4j_store is None and self._neo4j_enabled:
            try:
                from app.services.neo4j_graph_service import get_neo4j_store
                self._neo4j_store = get_neo4j_store()
            except Exception as e:
                loguru.logger.warning(f"Neo4j不可用，使用SQLAlchemy回退: {e}")
                self._neo4j_enabled = False
        return self._neo4j_store

    async def add_entity(
        self,
        user_id: int,
        entity_type: str,
        entity_name: str,
        properties: Optional[Dict] = None
    ) -> bool:
        """添加实体到知识图谱"""
        try:
            # 优先使用Neo4j（生产级）
            neo4j = await self._get_neo4j_store()
            if neo4j:
                entity_id = await neo4j.create_entity(
                    user_id=user_id,
                    entity_type=entity_type,
                    entity_name=entity_name,
                    properties=properties
                )
                loguru.logger.info(f"Neo4j添加实体: user_id={user_id}, entity={entity_name}")
                return entity_id is not None
            else:
                # 回退到SQLAlchemy
                return await self._add_entity_sqlalchemy(user_id, entity_type, entity_name, properties)

        except Exception as e:
            loguru.logger.error(f"添加知识图谱实体失败: {e}")
            # 回退到SQLAlchemy
            return await self._add_entity_sqlalchemy(user_id, entity_type, entity_name, properties)

    async def _add_entity_sqlalchemy(
        self,
        user_id: int,
        entity_type: str,
        entity_name: str,
        properties: Optional[Dict] = None
    ) -> bool:
        """使用SQLAlchemy添加实体（回退方案）"""
        try:
            from app.core.database import SessionLocal
            from app.models.memory_graph import KnowledgeGraph

            content = f"实体: {entity_name} (类型: {entity_type})"
            if properties:
                content += f"\n属性: {json.dumps(properties, ensure_ascii=False)}"

            db = SessionLocal()
            try:
                graph = KnowledgeGraph(
                    user_id=user_id,
                    graph_type="entity",
                    entity_type=entity_type,
                    entity_name=entity_name,
                    content=content,
                    metadata=json.dumps(properties) if properties else None,
                )
                db.add(graph)
                db.commit()
                loguru.logger.info(f"SQLAlchemy添加实体: user_id={user_id}, entity={entity_name}")
                return True
            finally:
                db.close()
        except Exception as e:
            loguru.logger.error(f"SQLAlchemy添加实体失败: {e}")
            return False

    async def add_relation(
        self,
        user_id: int,
        subject: str,
        relation: str,
        object_: str
    ) -> bool:
        """添加关系到知识图谱"""
        try:
            # 优先使用Neo4j（生产级）
            neo4j = await self._get_neo4j_store()
            if neo4j:
                success = await neo4j.create_relation(
                    user_id=user_id,
                    from_entity=subject,
                    to_entity=object_,
                    relation_type=relation
                )
                loguru.logger.info(f"Neo4j添加关系: {subject} --[{relation}]--> {object_}")
                return success
            else:
                # 回退到SQLAlchemy
                return await self._add_relation_sqlalchemy(user_id, subject, relation, object_)

        except Exception as e:
            loguru.logger.error(f"添加知识图谱关系失败: {e}")
            # 回退到SQLAlchemy
            return await self._add_relation_sqlalchemy(user_id, subject, relation, object_)

    async def _add_relation_sqlalchemy(
        self,
        user_id: int,
        subject: str,
        relation: str,
        object_: str
    ) -> bool:
        """使用SQLAlchemy添加关系（回退方案）"""
        try:
            from app.core.database import SessionLocal
            from app.models.memory_graph import KnowledgeGraph

            content = f"{subject} --[{relation}]--> {object_}"

            db = SessionLocal()
            try:
                graph = KnowledgeGraph(
                    user_id=user_id,
                    graph_type="relation",
                    entity_name=f"{subject} -> {object_}",
                    content=content,
                    metadata=json.dumps({
                        "subject": subject,
                        "relation": relation,
                        "object": object_,
                    }),
                )
                db.add(graph)
                db.commit()
                loguru.logger.info(f"SQLAlchemy添加关系: {subject} --[{relation}]--> {object_}")
                return True
            finally:
                db.close()
        except Exception as e:
            loguru.logger.error(f"SQLAlchemy添加关系失败: {e}")
            return False

    async def query_graph(
        self,
        user_id: int,
        entity: str,
        depth: int = 2
    ) -> List[Dict]:
        """查询知识图谱"""
        try:
            # 优先使用Neo4j（生产级）
            neo4j = await self._get_neo4j_store()
            if neo4j:
                # 获取子图
                subgraph = await neo4j.get_subgraph(user_id, entity, depth)
                if subgraph["nodes"]:
                    return [{
                        "source": "neo4j",
                        "center": entity,
                        "nodes": subgraph["nodes"],
                        "edges": subgraph["edges"]
                    }]

            # 回退到SQLAlchemy
            return await self._query_graph_sqlalchemy(user_id, entity)

        except Exception as e:
            loguru.logger.error(f"查询知识图谱失败: {e}")
            return await self._query_graph_sqlalchemy(user_id, entity)

    async def _query_graph_sqlalchemy(self, user_id: int, entity: str) -> List[Dict]:
        """使用SQLAlchemy查询知识图谱（回退方案）"""
        try:
            from app.core.database import SessionLocal
            from app.models.memory_graph import KnowledgeGraph

            db = SessionLocal()
            try:
                # 搜索相关实体和关系
                graphs = db.query(KnowledgeGraph).filter(
                    KnowledgeGraph.user_id == user_id,
                    KnowledgeGraph.is_deleted == False,
                ).filter(
                    KnowledgeGraph.entity_name.contains(entity) |
                    KnowledgeGraph.content.contains(entity)
                ).limit(10).all()

                return [
                    {
                        "source": "sqlalchemy",
                        "id": g.id,
                        "graph_type": g.graph_type,
                        "entity_name": g.entity_name,
                        "content": g.content,
                        "metadata": json.loads(g.metadata) if g.metadata else {},
                    }
                    for g in graphs
                ]
            finally:
                db.close()
        except Exception as e:
            loguru.logger.error(f"SQLAlchemy查询知识图谱失败: {e}")
            return []

    async def get_graph_stats(self, user_id: int) -> Dict:
        """获取知识图谱统计"""
        try:
            neo4j = await self._get_neo4j_store()
            if neo4j:
                return await neo4j.get_stats(user_id)

            # 回退到SQLAlchemy
            from app.core.database import SessionLocal
            from app.models.memory_graph import KnowledgeGraph

            db = SessionLocal()
            try:
                entity_count = db.query(KnowledgeGraph).filter(
                    KnowledgeGraph.user_id == user_id,
                    KnowledgeGraph.graph_type == "entity"
                ).count()

                relation_count = db.query(KnowledgeGraph).filter(
                    KnowledgeGraph.user_id == user_id,
                    KnowledgeGraph.graph_type == "relation"
                ).count()

                return {
                    "entity_count": entity_count,
                    "relation_count": relation_count,
                    "backend": "sqlalchemy"
                }
            finally:
                db.close()

        except Exception as e:
            loguru.logger.error(f"获取图谱统计失败: {e}")
            return {"entity_count": 0, "relation_count": 0}

    # ==================== 对话摘要 ====================

    async def summarize_conversation(
        self,
        user_id: int,
        session_id: str,
        messages: List[Dict]
    ) -> bool:
        """生成对话摘要并存储"""
        try:
            topics = await self.session_memory.get_topics(session_id)
            emotion_state = await self.session_memory.get_emotion_state(session_id)

            # 构建摘要内容
            content = f"""对话主题: {', '.join(topics) if topics else '一般聊天'}
当前情绪状态: {emotion_state.get('current') if emotion_state else '未知'}

对话记录 ({len(messages)} 条消息):
"""
            for msg in messages[-10:]:  # 最近10条
                content += f"- {msg.get('role', '')}: {msg.get('content', '')[:100]}...\n"

            metadata = {
                "session_id": session_id,
                "topics": ",".join(topics) if topics else "",
                "emotion": emotion_state.get("current") if emotion_state else "",
                "message_count": len(messages),
                "title": f"对话摘要: {session_id[:8]}...",
            }

            await self.add_user_memory(
                user_id=user_id,
                content=content,
                memory_type=MemoryType.CONVERSATION,
                metadata=metadata
            )

            loguru.logger.info(f"对话摘要已存储: user_id={user_id}, session={session_id}")
            return True

        except Exception as e:
            loguru.logger.error(f"生成对话摘要失败: {e}")
            return False

    # ==================== 偏好提取 ====================

    async def extract_preference(
        self,
        user_id: int,
        message: str,
        assistant_response: str
    ) -> bool:
        """从对话中提取用户偏好"""
        # 简单的关键词检测
        # 实际生产中应该使用LLM来分析
        preference_keywords = {
            "喜欢": "喜欢",
            "讨厌": "讨厌",
            "想要": "想要",
            "需要": "需要",
            "偏好": "偏好",
            "习惯": "习惯",
        }

        for keyword, pref_type in preference_keywords.items():
            if keyword in message:
                content = f"用户{pref_type}: {message}"
                await self.add_user_memory(
                    user_id=user_id,
                    content=content,
                    memory_type=MemoryType.PREFERENCE,
                    metadata={"extracted_from": "conversation", "keyword": keyword}
                )

        return True


# 全局实例
_memory_service: Optional[MemoryService] = None


def get_memory_service() -> MemoryService:
    """获取记忆服务实例"""
    global _memory_service
    if _memory_service is None:
        _memory_service = MemoryService()
    return _memory_service