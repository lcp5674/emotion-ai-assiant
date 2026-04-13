"""
Redis缓存服务 - 提供统一的缓存管理
"""
import json
import loguru
from typing import Optional, Any, List
from datetime import timedelta
import redis.asyncio as redis

from app.core.database import get_redis


class CacheService:
    """缓存服务"""

    # 缓存键前缀
    PREFIX = "emotion_ai:"

    # 默认过期时间
    DEFAULT_TTL = 3600  # 1小时

    def __init__(self):
        self._redis: Optional[redis.Redis] = None

    async def _get_redis(self) -> redis.Redis:
        """获取Redis连接"""
        if self._redis is None:
            self._redis = await get_redis()
        return self._redis

    def _make_key(self, key: str) -> str:
        """生成缓存键"""
        return f"{self.PREFIX}{key}"

    # ==================== 基础操作 ====================

    async def get(self, key: str, default: Any = None) -> Any:
        """获取缓存值"""
        try:
            r = await self._get_redis()
            value = await r.get(self._make_key(key))
            if value is None:
                return default
            return json.loads(value)
        except Exception as e:
            loguru.logger.warning(f"Cache get error: {e}")
            return default

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = DEFAULT_TTL
    ) -> bool:
        """设置缓存值"""
        try:
            r = await self._get_redis()
            serialized = json.dumps(value, ensure_ascii=False, default=str)
            await r.setex(self._make_key(key), ttl, serialized)
            return True
        except Exception as e:
            loguru.logger.warning(f"Cache set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            r = await self._get_redis()
            await r.delete(self._make_key(key))
            return True
        except Exception as e:
            loguru.logger.warning(f"Cache delete error: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        try:
            r = await self._get_redis()
            return await r.exists(self._make_key(key)) > 0
        except Exception as e:
            loguru.logger.warning(f"Cache exists error: {e}")
            return False

    async def expire(self, key: str, ttl: int) -> bool:
        """设置过期时间"""
        try:
            r = await self._get_redis()
            await r.expire(self._make_key(key), ttl)
            return True
        except Exception as e:
            loguru.logger.warning(f"Cache expire error: {e}")
            return False

    # ==================== 列表操作 ====================

    async def get_list(self, key: str, start: int = 0, end: int = -1) -> List[Any]:
        """获取列表缓存"""
        try:
            r = await self._get_redis()
            values = await r.lrange(self._make_key(key), start, end)
            return [json.loads(v) for v in values]
        except Exception as e:
            loguru.logger.warning(f"Cache get_list error: {e}")
            return []

    async def push_list(self, key: str, *values: Any) -> int:
        """向列表添加元素"""
        try:
            r = await self._get_redis()
            serialized = [json.dumps(v, ensure_ascii=False, default=str) for v in values]
            return await r.rpush(self._make_key(key), *serialized)
        except Exception as e:
            loguru.logger.warning(f"Cache push_list error: {e}")
            return 0

    # ==================== 计数器操作 ====================

    async def incr(self, key: str, amount: int = 1) -> int:
        """增加计数器"""
        try:
            r = await self._get_redis()
            return await r.incrby(self._make_key(key), amount)
        except Exception as e:
            loguru.logger.warning(f"Cache incr error: {e}")
            return 0

    async def decr(self, key: str, amount: int = 1) -> int:
        """减少计数器"""
        try:
            r = await self._get_redis()
            return await r.decrby(self._make_key(key), amount)
        except Exception as e:
            loguru.logger.warning(f"Cache decr error: {e}")
            return 0

    async def get_counter(self, key: str) -> int:
        """获取计数器值"""
        try:
            r = await self._get_redis()
            value = await r.get(self._make_key(key))
            return int(value) if value else 0
        except Exception as e:
            loguru.logger.warning(f"Cache get_counter error: {e}")
            return 0

    # ==================== 模式匹配操作 ====================

    async def delete_pattern(self, pattern: str) -> int:
        """删除匹配模式的所有键"""
        try:
            r = await self._get_redis()
            keys = []
            async for key in r.scan_iter(f"{self.PREFIX}{pattern}"):
                keys.append(key)
            if keys:
                return await r.delete(*keys)
            return 0
        except Exception as e:
            loguru.logger.warning(f"Cache delete_pattern error: {e}")
            return 0

    # ==================== 分布式锁 ====================

    async def acquire_lock(
        self,
        lock_name: str,
        timeout: int = 30,
        blocking_timeout: int = 10
    ) -> bool:
        """获取分布式锁"""
        try:
            r = await self._get_redis()
            lock_key = f"{self.PREFIX}lock:{lock_name}"
            result = await r.set(
                lock_key,
                "1",
                ex=timeout,
                nx=True
            )
            return result is not None
        except Exception as e:
            loguru.logger.warning(f"Cache acquire_lock error: {e}")
            return False

    async def release_lock(self, lock_name: str) -> bool:
        """释放分布式锁"""
        try:
            r = await self._get_redis()
            lock_key = f"{self.PREFIX}lock:{lock_name}"
            await r.delete(lock_key)
            return True
        except Exception as e:
            loguru.logger.warning(f"Cache release_lock error: {e}")
            return False

    # ==================== 业务特定缓存 ====================

    async def cache_user_profile(self, user_id: int, profile: dict, ttl: int = 3600) -> bool:
        """缓存用户画像"""
        return await self.set(f"user:profile:{user_id}", profile, ttl)

    async def get_user_profile(self, user_id: int) -> Optional[dict]:
        """获取用户画像缓存"""
        return await self.get(f"user:profile:{user_id}")

    async def invalidate_user_profile(self, user_id: int) -> bool:
        """清除用户画像缓存"""
        return await self.delete(f"user:profile:{user_id}")

    async def cache_mbti_result(self, user_id: int, result: dict, ttl: int = 86400) -> bool:
        """缓存MBTI测试结果"""
        return await self.set(f"mbti:result:{user_id}", result, ttl)

    async def get_mbti_result(self, user_id: int) -> Optional[dict]:
        """获取MBTI测试结果缓存"""
        return await self.get(f"mbti:result:{user_id}")

    async def cache_conversation_context(
        self,
        conversation_id: int,
        context: dict,
        ttl: int = 1800
    ) -> bool:
        """缓存对话上下文"""
        return await self.set(f"conv:context:{conversation_id}", context, ttl)

    async def get_conversation_context(self, conversation_id: int) -> Optional[dict]:
        """获取对话上下文缓存"""
        return await self.get(f"conv:context:{conversation_id}")

    async def invalidate_conversation_context(self, conversation_id: int) -> bool:
        """清除对话上下文缓存"""
        return await self.delete(f"conv:context:{conversation_id}")

    async def cache_llm_response(
        self,
        cache_key: str,
        response: str,
        ttl: int = 3600
    ) -> bool:
        """缓存LLM响应（用于去重）"""
        return await self.set(f"llm:response:{cache_key}", response, ttl)

    async def get_llm_response(self, cache_key: str) -> Optional[str]:
        """获取LLM响应缓存"""
        return await self.get(f"llm:response:{cache_key}")

    async def cache_rate_limit(
        self,
        user_id: int,
        action: str,
        limit: int,
        window: int = 60
    ) -> tuple[bool, int]:
        """
        缓存限流计数
        返回: (是否允许, 剩余次数)
        """
        key = f"ratelimit:{action}:{user_id}"
        try:
            r = await self._get_redis()
            current = await r.get(self._make_key(key))
            if current is None:
                # 首次请求，设置计数
                await r.setex(self._make_key(key), window, 1)
                return True, limit - 1
            current = int(current)
            if current >= limit:
                return False, 0
            await r.incr(self._make_key(key))
            return True, limit - current - 1
        except Exception as e:
            loguru.logger.warning(f"Cache rate_limit error: {e}")
            return True, limit

    async def invalidate_user_cache(self, user_id: int) -> int:
        """清除用户相关的所有缓存"""
        return await self.delete_pattern(f"user:*:{user_id}")

    async def invalidate_conversation_cache(self, conversation_id: int) -> int:
        """清除对话相关的所有缓存"""
        return await self.delete_pattern(f"conv:*:{conversation_id}")


# 全局实例
_cache_service: Optional[CacheService] = None


def get_cache_service() -> CacheService:
    """获取缓存服务实例"""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service
