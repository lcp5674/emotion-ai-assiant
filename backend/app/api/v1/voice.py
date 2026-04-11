"""
语音API - 语音识别(ASR)和语音合成(TTS)
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import Optional
import loguru

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models import User
from app.services.voice_service import get_voice_provider, VoiceServiceException

router = APIRouter(prefix="/voice", tags=["语音"])


@router.post("/asr", summary="语音识别")
async def speech_recognition(
    audio: UploadFile = File(..., description="音频文件"),
    format: Optional[str] = "wav",
    current_user: User = Depends(get_current_user),
):
    """
    语音识别 - 将语音转换为文本

    - 支持格式: wav, mp3, ogg, m4a
    - 返回识别出的文本
    """
    # 检查会员权限 - 语音功能需要VIP
    from app.models.user import MemberLevel
    if current_user.member_level == MemberLevel.FREE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="语音识别功能需要VIP会员才能使用"
        )

    try:
        audio_data = await audio.read()
        await audio.close()

        provider = get_voice_provider()
        text = await provider.asr_recognize(audio_data, format or "wav")

        return {
            "text": text,
            "success": True,
        }

    except VoiceServiceException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"语音识别失败: {str(e)}"
        )
    except Exception as e:
        loguru.logger.error(f"ASR错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务器错误: {str(e)}"
        )


@router.post("/tts", summary="语音合成")
async def text_to_speech(
    text: str,
    voice: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """
    语音合成 - 将文本转换为语音

    - text: 要合成的文本 (最大1000字符)
    - voice: 音色名称 (可选，依赖不同提供商)
    - 返回mp3音频文件
    """
    # 检查会员权限 - 语音功能需要VIP
    from app.models.user import MemberLevel
    if current_user.member_level == MemberLevel.FREE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="语音合成功能需要VIP会员才能使用"
        )

    if len(text) > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文本长度不能超过1000字符"
        )

    try:
        provider = get_voice_provider()
        audio_data = await provider.tts_synthesize(text, voice)

        if not audio_data:
            raise VoiceServiceException("合成结果为空")

        return Response(
            content=audio_data,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": f"inline; filename=speech.mp3"
            }
        )

    except VoiceServiceException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"语音合成失败: {str(e)}"
        )
    except Exception as e:
        loguru.logger.error(f"TTS错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务器错误: {str(e)}"
        )


@router.get("/status", summary="获取语音服务状态")
async def get_voice_status(
    current_user: User = Depends(get_current_user),
):
    """获取语音服务配置状态"""
    from app.core.config import settings

    provider_name = getattr(settings, "VOICE_PROVIDER", "mock")

    # 检查是否可用
    provider = get_voice_provider()
    available = provider_name != "mock"

    # 获取支持的音色列表 (简化版)
    supported_voices = []
    if provider_name == "openai":
        supported_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    elif provider_name == "alibaba":
        supported_voices = ["xiaoyun", "xiaogang", "xiaoming", "xiaoyan"]

    return {
        "provider": provider_name,
        "available": available,
        "supported_voices": supported_voices,
        "asr_enabled": True,
        "tts_enabled": True,
    }
