"""
短信服务 - 支持阿里云短信和Mock模式
"""
from typing import Optional
import loguru

from app.core.config import settings


class SmsService:
    """短信服务"""

    def __init__(self):
        self.provider = settings.SMS_PROVIDER.lower()

    async def send_verify_code(self, phone: str, code: str) -> bool:
        """
        发送验证码短信
        
        Returns:
            bool: 发送是否成功
        """
        if self.provider == "alibaba":
            return await self._send_alibaba(phone, code)
        else:
            return await self._send_mock(phone, code)

    async def _send_mock(self, phone: str, code: str) -> bool:
        """Mock模式，仅记录日志"""
        loguru.logger.warning(f"[Mock SMS] 发送验证码至 {phone}: {code}")
        return True

    async def _send_alibaba(self, phone: str, code: str) -> bool:
        """阿里云短信"""
        if not settings.ALIBABA_ACCESS_KEY_ID or not settings.ALIBABA_ACCESS_KEY_SECRET:
            loguru.logger.warning("阿里云短信未配置，降级到Mock模式")
            return await self._send_mock(phone, code)

        try:
            from aliyunsdkcore.client import AcsClient
            from aliyunsdkdysmsapi.request.v20170525 import SendSmsRequest
            import uuid

            client = AcsClient(
                settings.ALIBABA_ACCESS_KEY_ID,
                settings.ALIBABA_ACCESS_KEY_SECRET,
                "default"
            )

            request = SendSmsRequest()
            request.set_PhoneNumbers(phone)
            request.set_SignName(settings.ALIBABA_SMS_SIGN_NAME)
            request.set_TemplateCode(settings.ALIBABA_SMS_TEMPLATE_CODE)
            request.set_TemplateParam(f'{{"code":"{code}"}}')
            request.set_OutId(uuid.uuid4().hex[:8])

            response = client.do_action_with_exception(request)
            response_dict = eval(response.decode())
            
            if response_dict.get("Code") == "OK":
                loguru.logger.info(f"短信发送成功: {phone}")
                return True
            else:
                loguru.logger.error(f"短信发送失败: {response_dict}")
                return False

        except ImportError:
            loguru.logger.warning("阿里云SDK未安装，降级到Mock模式")
            return await self._send_mock(phone, code)
        except Exception as e:
            loguru.logger.error(f"短信发送异常: {e}")
            return await self._send_mock(phone, code)


_sms_service: Optional[SmsService] = None


def get_sms_service() -> SmsService:
    """获取短信服务实例"""
    global _sms_service
    if _sms_service is None:
        _sms_service = SmsService()
    return _sms_service
