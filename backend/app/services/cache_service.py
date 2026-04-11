"""
缓存服务
"""
import json
from typing import Optional, Any, Union
from datetime import timedelta
import redis.asyncio as redis

from app.core.config import settings


class CacheService:
    """缓存服务"""

    def __init__(self):
        self.redis_client = None
        self.is_connected = False

    async def connect(self):
        """连接到Redis"""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True
            )
            await self.redis_client.ping()
            self.is_connected = True
        except Exception as e:
            print(f"Redis连接失败: {e}")
            self.is_connected = False

    async def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if not self.is_connected:
            await self.connect()
        
        if not self.is_connected:
            return None
        
        try:
            value = await self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"获取缓存失败: {e}")
            return None

    async def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """设置缓存"""
        if not self.is_connected:
            await self.connect()
        
        if not self.is_connected:
            return False
        
        try:
            await self.redis_client.setex(
                key,
                expire,
                json.dumps(value)
            )
            return True
        except Exception as e:
            print(f"设置缓存失败: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """删除缓存"""
        if not self.is_connected:
            await self.connect()
        
        if not self.is_connected:
            return False
        
        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"删除缓存失败: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        if not self.is_connected:
            await self.connect()
        
        if not self.is_connected:
            return False
        
        try:
            return await self.redis_client.exists(key) > 0
        except Exception as e:
            print(f"检查缓存失败: {e}")
            return False

    async def get_or_set(self, key: str, func, expire: int = 3600) -> Any:
        """获取缓存，如果不存在则设置"""
        value = await self.get(key)
        if value is not None:
            return value
        
        value = func()
        await self.set(key, value, expire)
        return value


# 创建全局缓存服务实例
cache_service = CacheService()
