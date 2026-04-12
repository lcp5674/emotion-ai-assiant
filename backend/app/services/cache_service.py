"""
Redis缓存服务
"""
import json
import loguru
from typing import Optional, Any, Dict, List
from datetime import timedelta
import asyncio

from app.core.config import settings
from app.core.database import get_redis


class RedisCacheService:
    """Redis缓存服务"""

    def __init__(self):
        self.enabled = True
        self._client = None
        self._memory_cache = {}
        self._memory_cache_expiry = {}

    async def _get_client(self):
        """获取Redis客户端"""
        if self._client is None:
            try:
                self._client = await get_redis()
                await self._client.ping()
                self.enabled = True
                loguru.logger.info("Redis缓存服务已启用")
            except Exception as e:
                loguru.logger.warning(f"Redis连接失败，使用内存缓存: {e}")
                self.enabled = False
        return self._client

    async def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        # 检查内存缓存
        if key in self._memory_cache:
            # 检查是否过期
            if key in self._memory_cache_expiry:
                import time
                if time.time() > self._memory_cache_expiry[key]:
                    del self._memory_cache[key]
                    del self._memory_cache_expiry[key]
                    return None
            return self._memory_cache[key]
        
        # 检查Redis
        if self.enabled:
            try:
                client = await self._get_client()
                if client:
                    value = await client.get(key)
                    if value:
                        return json.loads(value)
            except Exception as e:
                loguru.logger.error(f"Redis获取缓存失败: {e}")
        
        return None

    async def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """设置缓存"""
        # 设置内存缓存
        self._memory_cache[key] = value
        import time
        self._memory_cache_expiry[key] = time.time() + expire
        
        # 设置Redis缓存
        if self.enabled:
            try:
                client = await self._get_client()
                if client:
                    await client.setex(key, expire, json.dumps(value, ensure_ascii=False))
                return True
            except Exception as e:
                loguru.logger.error(f"Redis设置缓存失败: {e}")
                return False
        
        return True

    async def delete(self, key: str) -> bool:
        """删除缓存"""
        # 删除内存缓存
        if key in self._memory_cache:
            del self._memory_cache[key]
        if key in self._memory_cache_expiry:
            del self._memory_cache_expiry[key]
        
        # 删除Redis缓存
        if self.enabled:
            try:
                client = await self._get_client()
                if client:
                    await client.delete(key)
                return True
            except Exception as e:
                loguru.logger.error(f"Redis删除缓存失败: {e}")
                return False
        
        return True

    async def exists(self, key: str) -> bool:
        """检查key是否存在"""
        # 检查内存缓存
        if key in self._memory_cache:
            # 检查是否过期
            if key in self._memory_cache_expiry:
                import time
                if time.time() > self._memory_cache_expiry[key]:
                    del self._memory_cache[key]
                    del self._memory_cache_expiry[key]
                    return False
            return True
        
        # 检查Redis
        if self.enabled:
            try:
                client = await self._get_client()
                if client:
                    return await client.exists(key) > 0
            except Exception as e:
                loguru.logger.error(f"Redis检查key失败: {e}")
                return False
        
        return False

    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """批量获取缓存"""
        result = {}
        
        # 先检查内存缓存
        for key in keys:
            if key in self._memory_cache:
                # 检查是否过期
                if key in self._memory_cache_expiry:
                    import time
                    if time.time() > self._memory_cache_expiry[key]:
                        del self._memory_cache[key]
                        del self._memory_cache_expiry[key]
                    else:
                        result[key] = self._memory_cache[key]
        
        # 检查Redis
        if self.enabled and len(result) < len(keys):
            remaining_keys = [key for key in keys if key not in result]
            try:
                client = await self._get_client()
                if client and remaining_keys:
                    values = await client.mget(remaining_keys)
                    for key, value in zip(remaining_keys, values):
                        if value:
                            result[key] = json.loads(value)
            except Exception as e:
                loguru.logger.error(f"Redis批量获取缓存失败: {e}")
        
        return result

    async def set_many(self, items: Dict[str, Any], expire: int = 3600) -> bool:
        """批量设置缓存"""
        # 设置内存缓存
        import time
        expiry_time = time.time() + expire
        for key, value in items.items():
            self._memory_cache[key] = value
            self._memory_cache_expiry[key] = expiry_time
        
        # 设置Redis缓存
        if self.enabled:
            try:
                client = await self._get_client()
                if client:
                    pipe = client.pipeline()
                    for key, value in items.items():
                        pipe.setex(key, expire, json.dumps(value, ensure_ascii=False))
                    await pipe.execute()
                return True
            except Exception as e:
                loguru.logger.error(f"Redis批量设置缓存失败: {e}")
                return False
        
        return True

    async def delete_many(self, keys: List[str]) -> bool:
        """批量删除缓存"""
        # 删除内存缓存
        for key in keys:
            if key in self._memory_cache:
                del self._memory_cache[key]
            if key in self._memory_cache_expiry:
                del self._memory_cache_expiry[key]
        
        # 删除Redis缓存
        if self.enabled and keys:
            try:
                client = await self._get_client()
                if client:
                    await client.delete(*keys)
                return True
            except Exception as e:
                loguru.logger.error(f"Redis批量删除缓存失败: {e}")
                return False
        
        return True

    async def ping(self) -> bool:
        """Ping Redis"""
        if self.enabled:
            try:
                client = await self._get_client()
                if client:
                    await client.ping()
                    return True
            except Exception as e:
                loguru.logger.error(f"Redis ping失败: {e}")
        return False


_cache_service: Optional[RedisCacheService] = None


def get_cache_service() -> RedisCacheService:
    """获取缓存服务实例"""
    global _cache_service
    if _cache_service is None:
        _cache_service = RedisCacheService()
    return _cache_service


CACHE_KEYS = {
    "MBTI_QUESTIONS": "mbti:questions:v1",
    "MBTI_QUESTIONS_DIMENSION": "mbti:questions:{dimension}:v1",
    "AI_ASSISTANTS": "ai:assistants:v1",
    "AI_ASSISTANTS_MBTI": "ai:assistants:mbti:{mbti_type}",
    "SYSTEM_CONFIG": "system:config:{key}",
    "USER_SESSION": "user:session:{user_id}",
    "RATE_LIMIT": "ratelimit:{identifier}",
}


async def cache_mbti_questions(questions: list, dimension: Optional[str] = None):
    """缓存MBTI题目"""
    service = get_cache_service()
    if dimension:
        key = CACHE_KEYS["MBTI_QUESTIONS_DIMENSION"].format(dimension=dimension)
    else:
        key = CACHE_KEYS["MBTI_QUESTIONS"]
    
    await service.set(key, questions, expire=86400 * 7)


async def get_cached_mbti_questions(dimension: Optional[str] = None) -> Optional[list]:
    """获取缓存的MBTI题目"""
    service = get_cache_service()
    if dimension:
        key = CACHE_KEYS["MBTI_QUESTIONS_DIMENSION"].format(dimension=dimension)
    else:
        key = CACHE_KEYS["MBTI_QUESTIONS"]
    
    return await service.get(key)


async def cache_assistants(assistants: list, mbti_type: Optional[str] = None):
    """缓存AI助手"""
    service = get_cache_service()
    if mbti_type:
        key = CACHE_KEYS["AI_ASSISTANTS_MBTI"].format(mbti_type=mbti_type)
    else:
        key = CACHE_KEYS["AI_ASSISTANTS"]
    
    await service.set(key, assistants, expire=86400 * 7)


async def get_cached_assistants(mbti_type: Optional[str] = None) -> Optional[list]:
    """获取缓存的AI助手"""
    service = get_cache_service()
    if mbti_type:
        key = CACHE_KEYS["AI_ASSISTANTS_MBTI"].format(mbti_type=mbti_type)
    else:
        key = CACHE_KEYS["AI_ASSISTANTS"]
    
    return await service.get(key)
