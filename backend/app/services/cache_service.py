"""
Redis缓存服务
"""
import json
import loguru
from typing import Optional, Any
from datetime import timedelta

from app.core.config import settings


class RedisCacheService:
    """Redis缓存服务"""

    def __init__(self):
        self.enabled = False
        self._client = None
        self._init_client()

    def _init_client(self):
        """初始化Redis客户端"""
        try:
            import redis
            self._client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                db=settings.REDIS_DB,
                decode_responses=True,
                socket_connect_timeout=3,
                socket_timeout=3,
            )
            self._client.ping()
            self.enabled = True
            loguru.logger.info("Redis缓存服务已启用")
        except Exception as e:
            loguru.logger.warning(f"Redis连接失败，使用内存缓存: {e}")
            self.enabled = False
            self._memory_cache = {}

    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if not self.enabled:
            return self._memory_cache.get(key)
        
        try:
            value = self._client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            loguru.logger.error(f"Redis获取缓存失败: {e}")
        
        return None

    def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """设置缓存"""
        if not self.enabled:
            self._memory_cache[key] = value
            return True
        
        try:
            self._client.setex(key, expire, json.dumps(value, ensure_ascii=False))
            return True
        except Exception as e:
            loguru.logger.error(f"Redis设置缓存失败: {e}")
            return False

    def delete(self, key: str) -> bool:
        """删除缓存"""
        if not self.enabled:
            self._memory_cache.pop(key, None)
            return True
        
        try:
            self._client.delete(key)
            return True
        except Exception as e:
            loguru.logger.error(f"Redis删除缓存失败: {e}")
            return False

    def exists(self, key: str) -> bool:
        """检查key是否存在"""
        if not self.enabled:
            return key in self._memory_cache
        
        try:
            return self._client.exists(key) > 0
        except Exception as e:
            loguru.logger.error(f"Redis检查key失败: {e}")
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


def cache_mbti_questions(questions: list, dimension: Optional[str] = None):
    """缓存MBTI题目"""
    service = get_cache_service()
    if dimension:
        key = CACHE_KEYS["MBTI_QUESTIONS_DIMENSION"].format(dimension=dimension)
    else:
        key = CACHE_KEYS["MBTI_QUESTIONS"]
    
    service.set(key, questions, expire=86400 * 7)


def get_cached_mbti_questions(dimension: Optional[str] = None) -> Optional[list]:
    """获取缓存的MBTI题目"""
    service = get_cache_service()
    if dimension:
        key = CACHE_KEYS["MBTI_QUESTIONS_DIMENSION"].format(dimension=dimension)
    else:
        key = CACHE_KEYS["MBTI_QUESTIONS"]
    
    return service.get(key)


def cache_assistants(assistants: list, mbti_type: Optional[str] = None):
    """缓存AI助手"""
    service = get_cache_service()
    if mbti_type:
        key = CACHE_KEYS["AI_ASSISTANTS_MBTI"].format(mbti_type=mbti_type)
    else:
        key = CACHE_KEYS["AI_ASSISTANTS"]
    
    service.set(key, assistants, expire=86400 * 7)


def get_cached_assistants(mbti_type: Optional[str] = None) -> Optional[list]:
    """获取缓存的AI助手"""
    service = get_cache_service()
    if mbti_type:
        key = CACHE_KEYS["AI_ASSISTANTS_MBTI"].format(mbti_type=mbti_type)
    else:
        key = CACHE_KEYS["AI_ASSISTANTS"]
    
    return service.get(key)
