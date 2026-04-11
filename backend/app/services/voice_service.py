"""
语音服务 - 语音识别(ASR)和语音合成(TTS)对接
支持多个厂商：阿里云、百度、腾讯、OpenAI
"""
from typing import Optional, List, Dict, Any
import os
import loguru

from app.core.config import settings


class VoiceServiceException(Exception):
    """语音服务异常"""
    pass


class BaseVoiceProvider:
    """语音提供商基类"""

    async def asr_recognize(self, audio_data: bytes, format: str = "wav") -> str:
        """
        语音识别

        Args:
            audio_data: 音频二进制数据
            format: 音频格式 (wav/mp3/ogg)

        Returns:
            识别出的文本
        """
        raise NotImplementedError()

    async def tts_synthesize(self, text: str, voice: Optional[str] = None) -> bytes:
        """
        语音合成

        Args:
            text: 要合成的文本
            voice: 音色名称

        Returns:
            合成后的音频二进制数据
        """
        raise NotImplementedError()


class MockVoiceProvider(BaseVoiceProvider):
    """Mock语音提供商 - 用于开发测试"""

    async def asr_recognize(self, audio_data: bytes, format: str = "wav") -> str:
        """Mock识别"""
        return "这是一段测试语音识别结果"

    async def tts_synthesize(self, text: str, voice: Optional[str] = None) -> bytes:
        """Mock合成 - 返回空数据"""
        loguru.logger.info(f"TTS合成请求: {text[:50]}...")
        return b""


class AlibabaVoiceProvider(BaseVoiceProvider):
    """阿里云语音服务"""

    def __init__(self):
        self.access_key = settings.ALIBABA_ACCESS_KEY_ID
        self.access_secret = settings.ALIBABA_ACCESS_KEY_SECRET
        self.app_key = settings.ALIBABA_VOICE_APP_KEY or ""

        if not self.access_key or not self.access_secret:
            loguru.logger.warning("阿里云语音服务未配置，降级到Mock")

    async def asr_recognize(self, audio_data: bytes, format: str = "wav") -> str:
        """阿里云语音识别"""
        if not self.access_key or not self.access_secret:
            return "未配置阿里云语音服务"

        try:
            import alioss
            from aliyunsdkcore.client import AcsClient
            from aliyunsdknls.request.v20180817 import SpeechRecognizerRequest

            client = AcsClient(self.access_key, self.access_secret, 'cn-shanghai')

            request = SpeechRecognizerRequest.SpeechRecognizerRequest()
            request.set_AppKey(self.app_key)
            request.set_Body(audio_data)
            request.set_Format(format)

            response = client.do_action_with_exception(request)
            # 解析响应
            import json
            result = json.loads(response.decode('utf-8'))

            if result.get("status") == 200:
                return result.get("result", "")
            else:
                loguru.logger.error(f"阿里云ASR识别失败: {result}")
                raise VoiceServiceException(result.get("message", "识别失败"))

        except ImportError:
            loguru.logger.warning("阿里云SDK未安装，降级到Mock")
            return (await MockVoiceProvider().asr_recognize(audio_data, format))
        except Exception as e:
            loguru.logger.error(f"阿里云ASR错误: {e}")
            raise VoiceServiceException(str(e))

    async def tts_synthesize(self, text: str, voice: Optional[str] = None) -> bytes:
        """阿里云语音合成"""
        if not self.access_key or not self.access_secret:
            return b""

        try:
            from aliyunsdkcore.client import AcsClient
            from aliyunsdknls.request.v20180817 import SpeechSynthesizerRequest

            client = AcsClient(self.access_key, self.access_secret, 'cn-shanghai')

            request = SpeechSynthesizerRequest.SpeechSynthesizerRequest()
            request.set_AppKey(self.app_key)
            request.set_Text(text)
            if voice:
                request.set_Voice(voice)
            request.set_Format("mp3")

            response = client.do_action_with_exception(request)
            return response  # 响应就是二进制音频数据

        except ImportError:
            loguru.logger.warning("阿里云SDK未安装，降级到Mock")
            return (await MockVoiceProvider().tts_synthesize(text, voice))
        except Exception as e:
            loguru.logger.error(f"阿里云TTS错误: {e}")
            raise VoiceServiceException(str(e))


class BaiduVoiceProvider(BaseVoiceProvider):
    """百度语音"""

    def __init__(self):
        self.api_key = settings.BAIDU_VOICE_API_KEY
        self.secret_key = settings.BAIDU_VOICE_SECRET_KEY
        self.access_token = None

    async def _get_access_token(self) -> str:
        """获取百度访问令牌"""
        if self.access_token:
            return self.access_token

        import aiohttp
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.secret_key,
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                data = await resp.json()
                self.access_token = data.get("access_token")
                return self.access_token

    async def asr_recognize(self, audio_data: bytes, format: str = "wav") -> str:
        """百度语音识别"""
        if not self.api_key or not self.secret_key:
            loguru.logger.warning("百度语音未配置，降级到Mock")
            return (await MockVoiceProvider().asr_recognize(audio_data, format))

        try:
            import aiohttp
            token = await self._get_access_token()
            url = f"https://vbd.hz.baidu.com/rest/2.0/asr/enable?access_token={token}"

            form = aiohttp.FormData()
            form.add_field("speech", audio_data, filename=f"audio.{format}")
            form.add_field("format", format)
            form.add_field("rate", "16000")
            form.add_field("channel", "1")
            form.add_field("cuid", "emotion-ai-assistant")

            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=form) as resp:
                    result = await resp.json()

                    if result.get("err_no") == 0:
                        return result.get("result", [""])[0] if result.get("result") else ""
                    else:
                        loguru.logger.error(f"百度ASR失败: {result}")
                        raise VoiceServiceException(result.get("err_msg", "识别失败"))

        except ImportError:
            loguru.logger.warning("aiohttp未安装，降级到Mock")
            return (await MockVoiceProvider().asr_recognize(audio_data, format))
        except Exception as e:
            loguru.logger.error(f"百度ASR错误: {e}")
            raise VoiceServiceException(str(e))

    async def tts_synthesize(self, text: str, voice: Optional[str] = None) -> bytes:
        """百度语音合成"""
        if not self.api_key or not self.secret_key:
            loguru.logger.warning("百度语音未配置，降级到Mock")
            return (await MockVoiceProvider().tts_synthesize(text, voice))

        try:
            import aiohttp
            import urllib.parse

            token = await self._get_access_token()
            url = f"https://tsn.baidu.com/text2audio"

            params = {
                "tex": urllib.parse.quote(text),
                "tok": token,
                "cuid": "emotion-ai-assistant",
                "ctp": "1",
                "lan": "zh",
            }
            if voice:
                params["per"] = voice

            full_url = url + "?" + "&".join(f"{k}={v}" for k, v in params.items())

            async with aiohttp.ClientSession() as session:
                async with session.get(full_url) as resp:
                    if resp.content_type == "audio/mp3":
                        return await resp.read()
                    else:
                        result = await resp.json()
                        loguru.logger.error(f"百度TTS失败: {result}")
                        raise VoiceServiceException(result.get("err_msg", "合成失败"))

        except Exception as e:
            loguru.logger.error(f"百度TTS错误: {e}")
            raise VoiceServiceException(str(e))


class OpenAIVoiceProvider(BaseVoiceProvider):
    """OpenAI Whisper ASR + TTS"""

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.base_url = settings.OPENAI_BASE_URL or "https://api.openai.com/v1"

    async def asr_recognize(self, audio_data: bytes, format: str = "wav") -> str:
        """OpenAI Whisper语音识别"""
        if not self.api_key:
            loguru.logger.warning("OpenAI未配置，降级到Mock")
            return (await MockVoiceProvider().asr_recognize(audio_data, format))

        try:
            import aiohttp
            url = f"{self.base_url}/audio/transcriptions"

            headers = {
                "Authorization": f"Bearer {self.api_key}",
            }

            form = aiohttp.FormData()
            form.add_field("file", audio_data, filename=f"audio.{format}")
            form.add_field("model", "whisper-1")
            form.add_field("language", "zh")

            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, data=form) as resp:
                    result = await resp.json()

                    if resp.status == 200:
                        return result.get("text", "")
                    else:
                        loguru.logger.error(f"OpenAI ASR失败: {result}")
                        raise VoiceServiceException(result.get("error", {}).get("message", "识别失败"))

        except Exception as e:
            loguru.logger.error(f"OpenAI ASR错误: {e}")
            raise VoiceServiceException(str(e))

    async def tts_synthesize(self, text: str, voice: Optional[str] = None) -> bytes:
        """OpenAI TTS"""
        if not self.api_key:
            loguru.logger.warning("OpenAI未配置，降级到Mock")
            return (await MockVoiceProvider().tts_synthesize(text, voice))

        try:
            import aiohttp
            url = f"{self.base_url}/audio/speech"

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            data = {
                "model": "tts-1",
                "input": text,
                "voice": voice or "alloy",
                "response_format": "mp3",
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data) as resp:
                    if resp.status == 200:
                        return await resp.read()
                    else:
                        result = await resp.json()
                        loguru.logger.error(f"OpenAI TTS失败: {result}")
                        raise VoiceServiceException(result.get("error", {}).get("message", "合成失败"))

        except Exception as e:
            loguru.logger.error(f"OpenAI TTS错误: {e}")
            raise VoiceServiceException(str(e))


class TencentVoiceProvider(BaseVoiceProvider):
    """腾讯云语音"""

    def __init__(self):
        self.secret_id = settings.TENCENT_VOICE_SECRET_ID
        self.secret_key = settings.TENCENT_VOICE_SECRET_KEY

        if not self.secret_id or not self.secret_key:
            loguru.logger.warning("腾讯云语音未配置，降级到Mock")

    async def asr_recognize(self, audio_data: bytes, format: str = "wav") -> str:
        """腾讯云语音识别"""
        if not self.secret_id or not self.secret_key:
            return (await MockVoiceProvider().asr_recognize(audio_data, format))

        try:
            from tencentcloud.common import credential
            from tencentcloud.common.profile.client_profile import ClientProfile
            from tencentcloud.common.profile.http_profile import HttpProfile
            from tencentcloud.asr.v20190614 import asr_client, models

            cred = credential.Credential(self.secret_id, self.secret_key)
            httpProfile = HttpProfile()
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            client = asr_client.AsrClient(cred, "ap-beijing", clientProfile)

            req = models.SentenceRecognitionRequest()
            # 简单实现，使用一句话识别
            import base64
            req.Data = base64.b64encode(audio_data).decode('utf-8')
            req.EngSerBizType = "general"
            req.SourceType = 1

            resp = client.SentenceRecognition(req)
            return resp.ResponseResult or ""

        except ImportError:
            loguru.logger.warning("腾讯云SDK未安装，降级到Mock")
            return (await MockVoiceProvider().asr_recognize(audio_data, format))
        except Exception as e:
            loguru.logger.error(f"腾讯云ASR错误: {e}")
            raise VoiceServiceException(str(e))

    async def tts_synthesize(self, text: str, voice: Optional[str] = None) -> bytes:
        """腾讯云语音合成"""
        if not self.secret_id or not self.secret_key:
            return (await MockVoiceProvider().tts_synthesize(text, voice))

        try:
            from tencentcloud.common import credential
            from tencentcloud.common.profile.client_profile import ClientProfile
            from tencentcloud.common.profile.http_profile import HttpProfile
            from tencentcloud.tts.v20190823 import tts_client, models

            cred = credential.Credential(self.secret_id, self.secret_key)
            httpProfile = HttpProfile()
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            client = tts_client.TtsClient(cred, "ap-beijing", clientProfile)

            req = models.TextToVoiceRequest()
            req.Text = text
            req.SessionId = "emotion-ai-" + str(hash(text) % 100000)
            if voice:
                req.VoiceType = int(voice) if voice.isdigit() else 0

            resp = client.TextToVoice(req)
            import base64
            return base64.b64decode(resp.Audio)

        except ImportError:
            loguru.logger.warning("腾讯云SDK未安装，降级到Mock")
            return (await MockVoiceProvider().tts_synthesize(text, voice))
        except Exception as e:
            loguru.logger.error(f"腾讯云TTS错误: {e}")
            raise VoiceServiceException(str(e))


# 提供商映射
PROVIDER_MAP = {
    "mock": MockVoiceProvider,
    "alibaba": AlibabaVoiceProvider,
    "baidu": BaiduVoiceProvider,
    "openai": OpenAIVoiceProvider,
    "tencent": TencentVoiceProvider,
}


# 全局服务实例
_voice_provider: Optional[BaseVoiceProvider] = None


def get_voice_provider() -> BaseVoiceProvider:
    """获取语音提供商"""
    global _voice_provider
    if _voice_provider is None:
        provider_name = getattr(settings, "VOICE_PROVIDER", "mock").lower()
        provider_class = PROVIDER_MAP.get(provider_name, MockVoiceProvider)
        _voice_provider = provider_class()
        loguru.logger.info(f"语音服务提供商初始化: {provider_name}")
    return _voice_provider


async def asr_recognize(audio_data: bytes, format: str = "wav") -> str:
    """语音识别快捷方法"""
    provider = get_voice_provider()
    return await provider.asr_recognize(audio_data, format)


async def tts_synthesize(text: str, voice: Optional[str] = None) -> bytes:
    """语音合成快捷方法"""
    provider = get_voice_provider()
    return await provider.tts_synthesize(text, voice)
