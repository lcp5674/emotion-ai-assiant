"""
API v1路由
"""
from fastapi import APIRouter

from app.api.v1 import auth, user, mbti, chat, diary, knowledge, member, payment, admin

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(user.router)
api_router.include_router(mbti.router)
api_router.include_router(chat.router)
api_router.include_router(diary.router)
api_router.include_router(knowledge.router)
api_router.include_router(member.router)
api_router.include_router(payment.router)
api_router.include_router(admin.router)

from app.websocket import router as ws_router
api_router.include_router(ws_router)