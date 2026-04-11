"""
core/database.py 单元测试
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

from app.core.database import get_db, get_redis, engine, SessionLocal


class TestDatabaseConnection:
    """数据库连接测试"""

    def test_engine_created(self):
        """测试引擎已创建"""
        assert engine is not None

    def test_session_local_created(self):
        """测试会话工厂已创建"""
        assert SessionLocal is not None

    def test_get_db_generator(self):
        """测试get_db生成器"""
        gen = get_db()
        db = next(gen)
        assert db is not None
        
        try:
            next(gen)
        except StopIteration:
            pass  # 预期

    def test_get_db_closes_on_exception(self):
        """测试异常时关闭连接"""
        gen = get_db()
        db = next(gen)
        
        with patch.object(db, 'close') as mock_close:
            try:
                next(gen)
            except StopIteration:
                pass
            
            mock_close.assert_called_once()


class TestRedisConnection:
    """Redis连接测试"""

    async def test_get_redis_returns_client(self):
        """测试获取Redis客户端"""
        from redis import Redis
        result = await get_redis()
        # 即使连接失败，也应该返回Redis实例
        assert result is not None

    async def test_get_redis_singleton(self):
        """测试Redis单例"""
        client1 = await get_redis()
        client2 = await get_redis()
        assert client1 is client2
