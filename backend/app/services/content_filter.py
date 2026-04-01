"""
内容安全过滤服务 - 敏感词检测
"""
import re
from typing import Optional
import loguru

from app.core.config import settings


SENSITIVE_WORDS = {
    "自杀", "自残", "自杀倾向", "想死", "不想活了", "活着没意思",
    "杀人", "杀人犯", "暴力", "殴打", "虐待",
    "毒品", "吸毒", "贩毒", "制毒",
    "赌博", "赌场", "博彩",
    "诈骗", "骗子", "欺诈",
    "色情", "裸照", "黄色", "成人网站",
}


class ContentFilterService:
    """内容过滤服务"""

    def __init__(self):
        self.provider = settings.CONTENT_FILTER_PROVIDER.lower()
        self._sensitive_pattern = re.compile(
            "|".join(re.escape(w) for w in SENSITIVE_WORDS)
        ) if SENSITIVE_WORDS else None

    async def check_text(self, text: str) -> tuple[bool, list[str]]:
        if self.provider == "alibaba":
            return await self._check_alibaba(text)
        else:
            return self._check_keyword(text)

    def _check_keyword(self, text: str) -> tuple[bool, list[str]]:
        """本地关键词检测"""
        if not self._sensitive_pattern:
            return True, []

        matched = self._sensitive_pattern.findall(text.lower())
        if matched:
            loguru.logger.warning(f"检测到敏感词: {matched}")
            return False, list(set(matched))
        return True, []

    async def _check_alibaba(self, text: str) -> tuple[bool, list[str]]:
        """阿里云内容安全检测"""
        if not settings.ALIBABA_CONTENT_ACCESS_KEY:
            loguru.logger.warning("阿里云内容安全未配置，降级到关键词检测")
            return self._check_keyword(text)

        try:
            from aliyungo_cs20151209.client import Client
            from aliyungo_cs20151209.models import TextScanRequest
            from aliyungo_cs20151209.credentials import AccessKeyCredential

            credential = AccessKeyCredential(
                settings.ALIBABA_CONTENT_ACCESS_KEY,
                settings.ALIBABA_CONTENT_ACCESS_SECRET
            )
            client = Client(credential)

            request = TextScanRequest()
            request.task = {"data": [{"content": text}]}
            
            response = client.text_scan(request)
            if response.body.data and response.body.data[0].suggestion == "pass":
                return True, []
            else:
                return False, ["content_flagged"]

        except ImportError:
            loguru.logger.warning("阿里云SDK未安装，降级到关键词检测")
            return self._check_keyword(text)
        except Exception as e:
            loguru.logger.error(f"内容安全检测异常: {e}")
            return self._check_keyword(text)

    def get_blocked_response(self) -> str:
        return (
            "抱歉，我注意到您分享的内容可能包含不适合讨论的话题。"
            "作为您的情感陪伴助手，我更希望能帮助您处理情绪、人际关系或个人成长方面的问题。"
            "有什么其他想要聊聊的吗？"
        )


_content_filter: Optional[ContentFilterService] = None


def get_content_filter() -> ContentFilterService:
    """获取内容过滤服务实例"""
    global _content_filter
    if _content_filter is None:
        _content_filter = ContentFilterService()
    return _content_filter
