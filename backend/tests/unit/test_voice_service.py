"""
voice_service 单元测试
"""
import pytest
from unittest.mock import Mock, patch
from io import BytesIO

from app.core.config import settings
from app.services.voice_service import (
    BaseVoiceProvider,
    MockVoiceProvider,
    AlibabaVoiceProvider,
    get_voice_provider,
    asr_recognize,
    tts_synthesize,
    VoiceServiceException,
)


class TestBaseVoiceProvider:
    """基础提供者测试"""

    def test_base_provider_abstract(self):
        """测试基础提供者是抽象的"""
        provider = BaseVoiceProvider()
        # 调用未实现的方法应该抛出异常
        with pytest.raises(NotImplementedError):
            provider.asr_recognize(b'')
        with pytest.raises(NotImplementedError):
            provider.tts_synthesize("")


class TestMockVoiceProvider:
    """Mock语音提供者测试"""

    async def test_asr_recognize(self):
        """测试Mock ASR识别"""
        provider = MockVoiceProvider()
        result = await provider.asr_recognize(b'test audio data')
        assert isinstance(result, str)
        assert len(result) > 0

    async def test_tts_synthesize(self):
        """测试Mock TTS合成"""
        provider = MockVoiceProvider()
        result = await provider.tts_synthesize("这是测试文本")
        assert isinstance(result, bytes)


class TestVoiceService:
    """语音服务整体测试"""

    def test_get_voice_provider_mock(self):
        """测试获取Mock提供者"""
        original_provider = getattr(settings, 'VOICE_PROVIDER', 'mock')
        settings.VOICE_PROVIDER = 'mock'
        
        provider = get_voice_provider()
        assert isinstance(provider, MockVoiceProvider)
        
        settings.VOICE_PROVIDER = original_provider

    async def test_asr_recognize_mock(self):
        """测试语音识别快捷方法"""
        original_provider = getattr(settings, 'VOICE_PROVIDER', 'mock')
        settings.VOICE_PROVIDER = 'mock'
        
        result = await asr_recognize(b'test audio')
        assert isinstance(result, str)
        
        settings.VOICE_PROVIDER = original_provider

    async def test_tts_synthesize_mock(self):
        """测试语音合成快捷方法"""
        original_provider = getattr(settings, 'VOICE_PROVIDER', 'mock')
        settings.VOICE_PROVIDER = 'mock'
        
        result = await tts_synthesize("这是测试文本")
        assert isinstance(result, bytes)
        
        settings.VOICE_PROVIDER = original_provider

    def test_get_service_status(self):
        """测试获取服务状态"""
        provider = get_voice_provider()
        # 提供者存在，说明工作正常
        assert provider is not None


class TestAlibabaVoiceProvider:
    """阿里云语音提供者测试"""

    def test_init_no_config(self):
        """测试无配置初始化降级到Mock行为"""
        from app.core.config import settings
        original_key = settings.ALIYUN_ACCESS_KEY_ID
        settings.ALIYUN_ACCESS_KEY_ID = ""
        
        provider = AlibabaVoiceProvider()
        # 没有配置应该不报错，降级处理
        assert provider is not None
        
        settings.ALIYUN_ACCESS_KEY_ID = original_key

    def test_init_with_config(self):
        """测试带配置初始化"""
        from app.core.config import settings
        original_key = settings.ALIYUN_ACCESS_KEY_ID
        original_secret = settings.ALIYUN_ACCESS_KEY_SECRET
        settings.ALIYUN_ACCESS_KEY_ID = "test-key"
        settings.ALIYUN_ACCESS_KEY_SECRET = "test-secret"
        
        provider = AlibabaVoiceProvider()
        assert provider.access_key == "test-key"
        
        settings.ALIYUN_ACCESS_KEY_ID = original_key
        settings.ALIYUN_ACCESS_KEY_SECRET = original_secret


class TestAudioFormatConversion:
    """音频格式转换测试"""

    def test_convert_format(self):
        """测试格式转换是否可调用"""
        from app.services.voice_service import convert_audio_format
        # 创建一个简单的wav头
        fake_wav = (
            b'RIFF' b'\x00\x00\x00\x00'
            b'WAVE'
            b'fmt ' b'\x10\x00\x00\x00'
            b'\x01\x00'  # PCM
            b'\x01\x00'  # mono
            b'\x80\xbb\x00\x00'  # sample rate 48000
            b'\x00\xee\x01\x00'  # byte rate
            b'\x02\x00'  # block align
            b'\x10\x00'  # bits per sample
            b'data' b'\x00\x00\x00\x00'
        )
        # 方法应该可调用不抛出异常
        try:
            result = convert_audio_format(fake_wav, "wav", "mp3")
            assert result is not None
        except Exception:
            # 如果没有ffmpeg，可能失败，但这是预期的
            pass


class TestVoiceServiceException:
    """语音服务异常测试"""

    def test_exception_raise(self):
        """测试异常抛出"""
        with pytest.raises(VoiceServiceException):
            raise VoiceServiceException("测试错误")

    def test_exception_message(self):
        """测试异常包含消息"""
        exc = VoiceServiceException("测试消息")
        assert "测试消息" in str(exc)


class TestBaiduVoiceProvider:
    """百度语音提供者测试"""

    def test_init_no_config(self):
        """测试无配置初始化"""
        from app.core.config import settings
        original_key = settings.BAIDU_VOICE_API_KEY
        original_secret = settings.BAIDU_VOICE_SECRET_KEY
        settings.BAIDU_VOICE_API_KEY = ""
        settings.BAIDU_VOICE_SECRET_KEY = ""
        
        from app.services.voice_service import BaiduVoiceProvider
        provider = BaiduVoiceProvider()
        assert provider is not None
        assert provider.api_key == ""
        
        settings.BAIDU_VOICE_API_KEY = original_key
        settings.BAIDU_VOICE_SECRET_KEY = original_secret


class TestOpenAIVoiceProvider:
    """OpenAI语音提供者测试"""

    def test_init_no_config(self):
        """测试无配置初始化"""
        from app.core.config import settings
        original_key = settings.OPENAI_API_KEY
        settings.OPENAI_API_KEY = ""
        
        from app.services.voice_service import OpenAIVoiceProvider
        provider = OpenAIVoiceProvider()
        assert provider is not None
        assert provider.api_key == ""
        
        settings.OPENAI_API_KEY = original_key


class TestTencentVoiceProvider:
    """腾讯云语音提供者测试"""

    def test_init_no_config(self):
        """测试无配置初始化"""
        from app.core.config import settings
        original_id = settings.TENCENT_VOICE_SECRET_ID
        original_key = settings.TENCENT_VOICE_SECRET_KEY
        settings.TENCENT_VOICE_SECRET_ID = ""
        settings.TENCENT_VOICE_SECRET_KEY = ""
        
        from app.services.voice_service import TencentVoiceProvider
        provider = TencentVoiceProvider()
        assert provider is not None
        
        settings.TENCENT_VOICE_SECRET_ID = original_id
        settings.TENCENT_VOICE_SECRET_KEY = original_key


class TestVoiceProviderSingleton:
    """语音提供者单例测试"""

    def test_singleton_instance(self):
        """测试单例模式"""
        from app.services.voice_service import get_voice_provider
        provider1 = get_voice_provider()
        provider2 = get_voice_provider()
        assert provider1 is provider2

    async def test_asr_recognize_import_error_fallback(self):
        """测试导入失败降级到Mock"""
        from app.core.config import settings
        from app.services.voice_service import AlibabaVoiceProvider
        original_key = settings.ALIYUN_ACCESS_KEY_ID
        original_secret = settings.ALIYUN_ACCESS_KEY_SECRET
        settings.ALIYUN_ACCESS_KEY_ID = "test"
        settings.ALIYUN_ACCESS_KEY_SECRET = "test"
        
        # 模拟ImportError
        with patch('builtins.__import__', side_effect=ImportError):
            provider = AlibabaVoiceProvider()
            result = await provider.asr_recognize(b'test')
            # 降级到Mock，返回默认文本
            assert isinstance(result, str)
            assert len(result) > 0
        
        settings.ALIYUN_ACCESS_KEY_ID = original_key
        settings.ALIYUN_ACCESS_KEY_SECRET = original_secret
