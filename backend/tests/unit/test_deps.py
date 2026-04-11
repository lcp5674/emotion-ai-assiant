"""
deps.py 依赖注入模块单元测试
"""
import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.api.deps import (
    get_current_user,
    get_current_user_optional,
    get_current_active_user,
    get_current_user_ws,
)
from app.models import User


class TestGetCurrentUser:
    """获取当前用户测试"""

    async def test_get_current_user_valid_token(self, db_session):
        """测试有效token获取用户"""
        from app.core.security import create_access_token
        
        # 创建测试用户
        user = User(
            id=1,
            phone="13800138001",
            nickname="测试",
            password_hash="hashed",
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()

        token = create_access_token(data={"sub": "1"})
        
        result = await get_current_user(token=token, db=db_session)
        assert result is not None
        assert result.id == 1
        assert result.phone == "13800138001"
        assert result.is_active is True

    async def test_get_current_user_invalid_token(self, db_session):
        """测试无效token"""
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token="invalid_token", db=db_session)
        assert exc_info.value.status_code == 401

    async def test_get_current_user_user_not_exists(self, db_session):
        """测试用户不存在"""
        from app.core.security import create_access_token
        
        token = create_access_token(data={"sub": "99999"})  # 不存在的用户ID
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=token, db=db_session)
        assert exc_info.value.status_code == 401

    async def test_get_current_user_user_inactive(self, db_session):
        """测试用户未激活"""
        from app.core.security import create_access_token
        
        user = User(
            id=2,
            phone="13800138002",
            nickname="不活跃用户",
            password_hash="hashed",
            is_active=False,
        )
        db_session.add(user)
        db_session.commit()

        token = create_access_token(data={"sub": "2"})
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=token, db=db_session)
        assert exc_info.value.status_code == 403


class TestGetCurrentUserOptional:
    """可选获取当前用户测试"""

    async def test_get_current_user_optional_no_token(self, db_session):
        """测试没有token返回None"""
        result = await get_current_user_optional(token=None, db=db_session)
        assert result is None

    async def test_get_current_user_optional_valid_token(self, db_session):
        """测试有效token返回用户"""
        from app.core.security import create_access_token
        
        user = User(
            id=3,
            phone="13800138003",
            nickname="可选测试",
            password_hash="hashed",
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()

        token = create_access_token(data={"sub": "3"})
        
        result = await get_current_user_optional(token=token, db=db_session)
        assert result is not None
        assert result.id == 3

    async def test_get_current_user_optional_invalid_token(self, db_session):
        """测试无效token返回None"""
        result = await get_current_user_optional(token="invalid", db=db_session)
        assert result is None


class TestGetCurrentActiveUser:
    """获取当前活跃用户测试"""

    def test_get_current_active_user_ok(self):
        """测试用户活跃"""
        mock_user = Mock(spec=User)
        mock_user.is_active = True
        
        result = get_current_active_user(current_user=mock_user)
        assert result == mock_user

    def test_get_current_active_user_inactive(self):
        """测试用户不活跃抛出异常"""
        mock_user = Mock(spec=User)
        mock_user.is_active = False
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_active_user(current_user=mock_user)
        assert exc_info.value.status_code == 400


class TestGetCurrentUserWs:
    """WebSocket获取用户测试"""

    async def test_get_current_user_ws_valid(self, db_session):
        """测试WebSocket有效token"""
        from app.core.security import create_access_token
        
        user = User(
            id=4,
            phone="13800138004",
            nickname="ws测试",
            password_hash="hashed",
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()

        token = create_access_token(data={"sub": "4"})
        
        result = await get_current_user_ws(token=token, db=db_session)
        assert result is not None
        assert result.id == 4
        assert result.is_active is True

    async def test_get_current_user_ws_invalid_token(self, db_session):
        """测试WebSocket无效token返回None"""
        result = await get_current_user_ws(token="invalid", db=db_session)
        assert result is None

    async def test_get_current_user_ws_user_not_exists(self, db_session):
        """测试用户不存在返回None"""
        from app.core.security import create_access_token
        
        token = create_access_token(data={"sub": "99999"})
        result = await get_current_user_ws(token=token, db=db_session)
        assert result is None

    async def test_get_current_user_ws_user_inactive(self, db_session):
        """测试用户不活跃返回None"""
        from app.core.security import create_access_token
        
        user = User(
            id=5,
            phone="13800138005",
            nickname="不活跃ws",
            password_hash="hashed",
            is_active=False,
        )
        db_session.add(user)
        db_session.commit()

        token = create_access_token(data={"sub": "5"})
        
        result = await get_current_user_ws(token=token, db=db_session)
        assert result is None

    async def test_get_current_user_ws_exception_returns_none(self, db_session):
        """测试异常情况下返回None"""
        with patch("app.api.deps.verify_token", side_effect=Exception("test error")):
            result = await get_current_user_ws(token="anytoken", db=db_session)
            assert result is None
