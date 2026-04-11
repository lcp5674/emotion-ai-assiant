"""
依赖注入
"""
from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import redis.asyncio as redis

from app.core.database import get_db, get_redis
from app.core.security import verify_token
from app.models import User

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """获取当前登录用户"""
    payload = verify_token(token)
    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的用户ID",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用",
        )

    # 检查并更新会员状态
    from app.services.member_service import get_member_service
    member_service = get_member_service()
    await member_service.check_and_update_member_status(user.id, db)

    return user


async def get_current_user_optional(
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)),
    db: Session = Depends(get_db),
) -> User | None:
    """获取当前用户 (可选，未登录返回None)"""
    if not token:
        return None
    try:
        return await get_current_user(token, db)
    except HTTPException:
        return None


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="用户已被禁用")
    return current_user


async def get_current_user_ws(
    token: str,
    db: Session = Depends(get_db),
) -> User | None:
    """WebSocket获取当前用户 (无异常抛出，失败返回None)"""
    try:
        payload = verify_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            return None
        user = db.query(User).filter(User.id == int(user_id)).first()
        if user and user.is_active:
            return user
        return None
    except Exception:
        return None