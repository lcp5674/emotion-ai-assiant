"""
Neo4j知识图谱服务 - 生产级图数据库
支持实体、关系、路径查询、图算法
"""
from typing import Optional, List, Dict, Any, Tuple
import loguru
import json

from app.core.config import settings


class Neo4jGraphStore:
    """Neo4j图数据库存储"""

    def __init__(self):
        self.driver = None
        self._connected = False

    async def _get_driver(self):
        """获取Neo4j驱动"""
        if self.driver is None:
            try:
                from neo4j import AsyncGraphDatabase
                from neo4j.exceptions import AuthError, ServiceUnavailable

                uri = getattr(settings, 'NEO4J_URI', 'bolt://localhost:7687')
                user = getattr(settings, 'NEO4J_USER', 'neo4j')
                password = getattr(settings, 'NEO4J_PASSWORD', 'password')

                self.driver = AsyncGraphDatabase.driver(
                    uri,
                    auth=(user, password),
                    max_connection_pool_size=50
                )

                # 测试连接
                async with self.driver.session() as session:
                    await session.run("RETURN 1")
                self._connected = True
                loguru.logger.info(f"Neo4j connected: {uri}")

            except ImportError:
                loguru.logger.error("Neo4j driver not installed. Run: pip install neo4j")
                raise
            except Exception as e:
                loguru.logger.error(f"Neo4j connection failed: {e}")
                raise

        return self.driver

    async def close(self):
        """关闭连接"""
        if self.driver:
            await self.driver.close()
            self.driver = None
            self._connected = False

    # ==================== 实体操作 ====================

    async def create_entity(
        self,
        user_id: int,
        entity_type: str,
        entity_name: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        创建实体
        Returns: entity_id
        """
        try:
            driver = await self._get_driver()
            async with driver.session() as session:
                query = """
                CREATE (e:Entity {
                    id: randomUUID(),
                    user_id: $user_id,
                    entity_type: $entity_type,
                    entity_name: $entity_name,
                    properties: $properties,
                    created_at: datetime()
                })
                RETURN e.id as id
                """
                result = await session.run(
                    query,
                    user_id=user_id,
                    entity_type=entity_type,
                    entity_name=entity_name,
                    properties=json.dumps(properties) if properties else "{}"
                )
                record = await result.single()
                entity_id = record["id"] if record else None

                loguru.logger.info(f"Neo4j: Created entity {entity_id} for user {user_id}")
                return entity_id

        except Exception as e:
            loguru.logger.error(f"Neo4j create_entity error: {e}")
            raise

    async def get_entity(
        self,
        user_id: int,
        entity_name: str
    ) -> Optional[Dict]:
        """获取实体"""
        try:
            driver = await self._get_driver()
            async with driver.session() as session:
                query = """
                MATCH (e:Entity {user_id: $user_id, entity_name: $entity_name})
                RETURN e.id as id, e.entity_type as entity_type, e.entity_name as entity_name,
                       e.properties as properties, e.created_at as created_at
                LIMIT 1
                """
                result = await session.run(query, user_id=user_id, entity_name=entity_name)
                record = await result.single()

                if record:
                    return {
                        "id": record["id"],
                        "entity_type": record["entity_type"],
                        "entity_name": record["entity_name"],
                        "properties": json.loads(record["properties"]) if record["properties"] else {},
                        "created_at": str(record["created_at"])
                    }
                return None

        except Exception as e:
            loguru.logger.error(f"Neo4j get_entity error: {e}")
            return None

    async def find_entities(
        self,
        user_id: int,
        entity_type: Optional[str] = None,
        keyword: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """搜索实体"""
        try:
            driver = await self._get_driver()
            async with driver.session() as session:

                if entity_type:
                    query = """
                    MATCH (e:Entity {user_id: $user_id, entity_type: $entity_type})
                    WHERE e.entity_name CONTAINS $keyword
                    RETURN e.id as id, e.entity_type as entity_type, e.entity_name as entity_name,
                           e.properties as properties
                    LIMIT $limit
                    """
                    params = {"user_id": user_id, "entity_type": entity_type, "keyword": keyword or "", "limit": limit}
                else:
                    query = """
                    MATCH (e:Entity {user_id: $user_id})
                    WHERE e.entity_name CONTAINS $keyword OR e.entity_type CONTAINS $keyword
                    RETURN e.id as id, e.entity_type as entity_type, e.entity_name as entity_name,
                           e.properties as properties
                    LIMIT $limit
                    """
                    params = {"user_id": user_id, "keyword": keyword or "", "limit": limit}

                result = await session.run(query, **params)

                entities = []
                async for record in result:
                    entities.append({
                        "id": record["id"],
                        "entity_type": record["entity_type"],
                        "entity_name": record["entity_name"],
                        "properties": json.loads(record["properties"]) if record["properties"] else {}
                    })
                return entities

        except Exception as e:
            loguru.logger.error(f"Neo4j find_entities error: {e}")
            return []

    async def delete_entity(self, user_id: int, entity_id: str) -> bool:
        """删除实体及其关系"""
        try:
            driver = await self._get_driver()
            async with driver.session() as session:
                query = """
                MATCH (e:Entity {user_id: $user_id, id: $entity_id})
                DETACH DELETE e
                """
                await session.run(query, user_id=user_id, entity_id=entity_id)
                loguru.logger.info(f"Neo4j: Deleted entity {entity_id}")
                return True

        except Exception as e:
            loguru.logger.error(f"Neo4j delete_entity error: {e}")
            return False

    # ==================== 关系操作 ====================

    async def create_relation(
        self,
        user_id: int,
        from_entity: str,
        to_entity: str,
        relation_type: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        创建关系
        关系会自动创建不存在的实体
        """
        try:
            driver = await self._get_driver()
            async with driver.session() as session:
                query = """
                MERGE (e1:Entity {user_id: $user_id, entity_name: $from_entity})
                    ON CREATE SET e1.entity_type = 'auto', e1.created_at = datetime()
                MERGE (e2:Entity {user_id: $user_id, entity_name: $to_entity})
                    ON CREATE SET e2.entity_type = 'auto', e2.created_at = datetime()
                CREATE (e1)-[r:RELATES {
                    relation_type: $relation_type,
                    properties: $properties,
                    created_at: datetime()
                }]->(e2)
                RETURN r
                """
                await session.run(
                    query,
                    user_id=user_id,
                    from_entity=from_entity,
                    to_entity=to_entity,
                    relation_type=relation_type,
                    properties=json.dumps(properties) if properties else "{}"
                )

                loguru.logger.info(f"Neo4j: Created relation {from_entity} -> {to_entity}")
                return True

        except Exception as e:
            loguru.logger.error(f"Neo4j create_relation error: {e}")
            return False

    async def get_relations(
        self,
        user_id: int,
        entity_name: str,
        direction: str = "both",  # outgoing, incoming, both
        relation_type: Optional[str] = None
    ) -> List[Dict]:
        """获取实体的关系"""
        try:
            driver = await self._get_driver()
            async with driver.session() as session:

                if direction == "outgoing":
                    query = """
                    MATCH (e:Entity {user_id: $user_id, entity_name: $entity_name})-[r]->(target)
                    RETURN target.entity_name as target, type(r) as relation_type,
                           r.relation_type as relation_label, r.properties as properties
                    """
                elif direction == "incoming":
                    query = """
                    MATCH (source)-[r]->(e:Entity {user_id: $user_id, entity_name: $entity_name})
                    RETURN source.entity_name as source, type(r) as relation_type,
                           r.relation_type as relation_label, r.properties as properties
                    """
                else:  # both
                    query = """
                    MATCH (e:Entity {user_id: $user_id, entity_name: $entity_name})-[r]-(other)
                    RETURN other.entity_name as other, type(r) as relation_type,
                           r.relation_type as relation_label, r.properties as properties,
                           CASE WHEN other.entity_name = $entity_name THEN 'source' ELSE 'target' END as direction
                    """

                result = await session.run(query, user_id=user_id, entity_name=entity_name)

                relations = []
                async for record in result:
                    rel = {
                        "relation_type": record["relation_type"],
                        "relation_label": record["relation_label"],
                        "properties": json.loads(record["properties"]) if record["properties"] else {}
                    }
                    if "target" in record:
                        rel["target"] = record["target"]
                    if "source" in record:
                        rel["source"] = record["source"]
                    if "other" in record:
                        rel["other"] = record["other"]
                    if "direction" in record:
                        rel["direction"] = record["direction"]
                    relations.append(rel)

                return relations

        except Exception as e:
            loguru.logger.error(f"Neo4j get_relations error: {e}")
            return []

    async def delete_relation(
        self,
        user_id: int,
        from_entity: str,
        to_entity: str,
        relation_type: Optional[str] = None
    ) -> bool:
        """删除关系"""
        try:
            driver = await self._get_driver()
            async with driver.session() as session:

                if relation_type:
                    query = """
                    MATCH (e1:Entity {user_id: $user_id, entity_name: $from_entity})-
                          [r:RELATES {relation_type: $relation_type}]->
                          (e2:Entity {user_id: $user_id, entity_name: $to_entity})
                    DELETE r
                    """
                    await session.run(query, user_id=user_id, from_entity=from_entity,
                                    to_entity=to_entity, relation_type=relation_type)
                else:
                    query = """
                    MATCH (e1:Entity {user_id: $user_id, entity_name: $from_entity})-[r]->
                          (e2:Entity {user_id: $user_id, entity_name: $to_entity})
                    DELETE r
                    """
                    await session.run(query, user_id=user_id, from_entity=from_entity, to_entity=to_entity)

                loguru.logger.info(f"Neo4j: Deleted relation {from_entity} -> {to_entity}")
                return True

        except Exception as e:
            loguru.logger.error(f"Neo4j delete_relation error: {e}")
            return False

    # ==================== 图查询 ====================

    async def find_path(
        self,
        user_id: int,
        from_entity: str,
        to_entity: str,
        max_depth: int = 3
    ) -> List[Dict]:
        """查找两个实体之间的路径"""
        try:
            driver = await self._get_driver()
            async with driver.session() as session:
                query = f"""
                MATCH path = (e1:Entity {{user_id: $user_id, entity_name: $from_entity}})
                            -[*1..{max_depth}]->
                             (e2:Entity {{user_id: $user_id, entity_name: $to_entity}})
                RETURN path, length(path) as depth
                ORDER BY depth
                LIMIT 5
                """
                result = await session.run(query, user_id=user_id, from_entity=from_entity, to_entity=to_entity)

                paths = []
                async for record in result:
                    nodes = []
                    relationships = []
                    for node in record["path"].nodes:
                        nodes.append(node.get("entity_name"))
                    for rel in record["path"].relationships:
                        relationships.append({
                            "from": rel.start_node.get("entity_name"),
                            "to": rel.end_node.get("entity_name"),
                            "type": rel.get("relation_type")
                        })
                    paths.append({
                        "nodes": nodes,
                        "relationships": relationships,
                        "depth": record["depth"]
                    })
                return paths

        except Exception as e:
            loguru.logger.error(f"Neo4j find_path error: {e}")
            return []

    async def get_subgraph(
        self,
        user_id: int,
        center_entity: str,
        depth: int = 2
    ) -> Dict:
        """获取实体周围的子图"""
        try:
            driver = await self._get_driver()
            async with driver.session() as session:
                query = f"""
                MATCH path = (e:Entity {{user_id: $user_id, entity_name: $center_entity}})
                            -[*1..{depth}]-(other)
                RETURN path
                """
                result = await session.run(query, user_id=user_id, center_entity=center_entity)

                nodes = {}
                edges = []
                async for record in result:
                    for node in record["path"].nodes:
                        node_id = node.get("id", node.get("entity_name"))
                        if node_id not in nodes:
                            nodes[node_id] = {
                                "id": node_id,
                                "entity_name": node.get("entity_name"),
                                "entity_type": node.get("entity_type")
                            }
                    for rel in record["path"].relationships:
                        edges.append({
                            "source": rel.start_node.get("entity_name"),
                            "target": rel.end_node.get("entity_name"),
                            "type": rel.get("relation_type")
                        })

                return {
                    "center": center_entity,
                    "nodes": list(nodes.values()),
                    "edges": edges
                }

        except Exception as e:
            loguru.logger.error(f"Neo4j get_subgraph error: {e}")
            return {"center": center_entity, "nodes": [], "edges": []}

    # ==================== 图算法 ====================

    async def get_degree_centrality(
        self,
        user_id: int,
        entity_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """获取度数中心性（最常被提及的实体）"""
        try:
            driver = await self._get_driver()
            async with driver.session() as session:

                if entity_type:
                    query = """
                    MATCH (e:Entity {user_id: $user_id, entity_type: $entity_type})-[r]-()
                    RETURN e.entity_name as entity, count(r) as degree
                    ORDER BY degree DESC
                    LIMIT $limit
                    """
                    result = await session.run(query, user_id=user_id, entity_type=entity_type, limit=limit)
                else:
                    query = """
                    MATCH (e:Entity {user_id: $user_id})-[r]-()
                    RETURN e.entity_name as entity, count(r) as degree
                    ORDER BY degree DESC
                    LIMIT $limit
                    """
                    result = await session.run(query, user_id=user_id, limit=limit)

                return [{"entity": record["entity"], "degree": record["degree"]}
                       async for record in result]

        except Exception as e:
            loguru.logger.error(f"Neo4j get_degree_centrality error: {e}")
            return []

    async def get_common_relations(
        self,
        user_id: int,
        entity_names: List[str]
    ) -> List[Dict]:
        """获取多个实体的共同关系"""
        try:
            driver = await self._get_driver()
            async with driver.session() as session:
                # 构建IN查询
                placeholders = [f"$name{i}" for i in range(len(entity_names))]
                query = f"""
                MATCH (e:Entity {{user_id: $user_id, entity_name IN [{','.join(placeholders)}]}})-[r]-()
                WITH e.entity_name as entity, type(r) as rel_type, count(*) as weight
                WHERE weight >= 2
                RETURN entity, collect({{type: rel_type, weight: weight}}) as relations
                ORDER BY size(relations) DESC
                """
                params = {f"name{i}": name for i, name in enumerate(entity_names)}
                result = await session.run(query, user_id=user_id, **params)

                return [{"entity": record["entity"], "relations": record["relations"]}
                       async for record in result]

        except Exception as e:
            loguru.logger.error(f"Neo4j get_common_relations error: {e}")
            return []

    # ==================== 批量操作 ====================

    async def batch_create_entities(
        self,
        user_id: int,
        entities: List[Dict[str, Any]]
    ) -> int:
        """批量创建实体"""
        try:
            driver = await self._get_driver()
            async with driver.session() as session:
                query = """
                UNWIND $entities as entity
                CREATE (e:Entity {
                    id: randomUUID(),
                    user_id: $user_id,
                    entity_type: entity.entity_type,
                    entity_name: entity.entity_name,
                    properties: entity.properties,
                    created_at: datetime()
                })
                """
                entities_data = [
                    {
                        "entity_type": e.get("entity_type", "unknown"),
                        "entity_name": e.get("entity_name", ""),
                        "properties": json.dumps(e.get("properties", {}))
                    }
                    for e in entities
                ]
                await session.run(query, user_id=user_id, entities=entities_data)
                loguru.logger.info(f"Neo4j: Batch created {len(entities)} entities")
                return len(entities)

        except Exception as e:
            loguru.logger.error(f"Neo4j batch_create_entities error: {e}")
            return 0

    async def batch_create_relations(
        self,
        user_id: int,
        relations: List[Dict[str, Any]]
    ) -> int:
        """批量创建关系"""
        try:
            driver = await self._get_driver()
            async with driver.session() as session:
                query = """
                UNWIND $relations as rel
                MERGE (e1:Entity {user_id: $user_id, entity_name: rel.from_entity})
                MERGE (e2:Entity {user_id: $user_id, entity_name: rel.to_entity})
                CREATE (e1)-[r:RELATES {
                    relation_type: rel.relation_type,
                    properties: rel.properties,
                    created_at: datetime()
                }]->(e2)
                """
                relations_data = [
                    {
                        "from_entity": r.get("from_entity", ""),
                        "to_entity": r.get("to_entity", ""),
                        "relation_type": r.get("relation_type", "RELATES"),
                        "properties": json.dumps(r.get("properties", {}))
                    }
                    for r in relations
                ]
                await session.run(query, user_id=user_id, relations=relations_data)
                loguru.logger.info(f"Neo4j: Batch created {len(relations)} relations")
                return len(relations)

        except Exception as e:
            loguru.logger.error(f"Neo4j batch_create_relations error: {e}")
            return 0

    # ==================== 统计 ====================

    async def get_stats(self, user_id: int) -> Dict:
        """获取用户图谱统计"""
        try:
            driver = await self._get_driver()
            async with driver.session() as session:
                # 实体数量
                entity_count_query = """
                MATCH (e:Entity {user_id: $user_id})
                RETURN count(e) as count
                """
                entity_result = await session.run(entity_count_query, user_id=user_id)
                entity_record = await entity_result.single()
                entity_count = entity_record["count"] if entity_record else 0

                # 关系数量
                relation_count_query = """
                MATCH ()-[r:RELATES]->() WHERE r.user_id = $user_id OR NOT EXISTS(r.user_id)
                WITH count(r) as count
                MATCH (e:Entity {user_id: $user_id})-[r:RELATES]-()
                RETURN count(DISTINCT r) as count
                """
                relation_result = await session.run(relation_count_query, user_id=user_id)
                relation_record = await relation_result.single()
                relation_count = relation_record["count"] if relation_record else 0

                # 按类型统计实体
                type_query = """
                MATCH (e:Entity {user_id: $user_id})
                RETURN e.entity_type as type, count(e) as count
                ORDER BY count DESC
                """
                type_result = await session.run(type_query, user_id=user_id)

                type_counts = {}
                async for record in type_result:
                    type_counts[record["type"]] = record["count"]

                return {
                    "entity_count": entity_count,
                    "relation_count": relation_count,
                    "entity_types": type_counts
                }

        except Exception as e:
            loguru.logger.error(f"Neo4j get_stats error: {e}")
            return {"entity_count": 0, "relation_count": 0, "entity_types": {}}


# 全局实例
_neo4j_store: Optional[Neo4jGraphStore] = None


def get_neo4j_store() -> Neo4jGraphStore:
    """获取Neo4j存储实例"""
    global _neo4j_store
    if _neo4j_store is None:
        _neo4j_store = Neo4jGraphStore()
    return _neo4j_store
