"""
API v1路由
"""
from fastapi import APIRouter

from app.api.v1 import auth, user, mbti, chat, diary, knowledge, member, payment, admin, user_memory, voice, growth, sbti, attachment, profile

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
api_router.include_router(user_memory.router)
api_router.include_router(voice.router)
api_router.include_router(growth.router)
api_router.include_router(sbti.router)
api_router.include_router(attachment.router)
api_router.include_router(profile.router)

from app.websocket import router as ws_router
api_router.include_router(ws_router)