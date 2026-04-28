"""
Spug推送服务 - 支持多种通知渠道
包括 Bark(iOS)、Server酱(微信)、钉钉、飞书、Telegram、邮件等
"""
from typing import Optional
import loguru
import httpx
import base64
import hmac
import hashlib
import time
import json
from urllib.parse import urlencode

from app.core.config import settings


class SpugNotifier:
    """Spug通知服务"""

    def __init__(self):
        self.enabled = settings.SPUG_ENABLED
        self.webhook_url = settings.SPUG_WEBHOOK_URL
        self.channel = settings.SPUG_CHANNEL.lower()

    async def send(self, title: str, content: str, **kwargs) -> bool:
        """
        发送通知

        Args:
            title: 通知标题
            content: 通知内容
            **kwargs: 额外参数

        Returns:
            bool: 发送是否成功
        """
        if not self.enabled:
            loguru.logger.warning("[Spug] Spug通知未启用")
            return True

        if not self.webhook_url:
            loguru.logger.warning("[Spug] Spug Webhook URL未配置")
            return False

        try:
            if self.channel == "bark":
                return await self._send_bark(title, content, **kwargs)
            elif self.channel == "serverchan":
                return await self._send_serverchan(title, content, **kwargs)
            elif self.channel == "dingtalk":
                return await self._send_dingtalk(title, content, **kwargs)
            elif self.channel == "feishu":
                return await self._send_feishu(title, content, **kwargs)
            elif self.channel == "telegram":
                return await self._send_telegram(title, content, **kwargs)
            elif self.channel == "email":
                return await self._send_email(title, content, **kwargs)
            else:
                # 通用webhook
                return await self._send_webhook(title, content, **kwargs)
        except Exception as e:
            loguru.logger.error(f"[Spug] 通知发送失败: {e}")
            return False

    async def _send_bark(self, title: str, content: str, **kwargs) -> bool:
        """发送 Bark 通知 (iOS)"""
        if not settings.SPUG_BARK_KEY:
            loguru.logger.warning("[Bark] Bark DeviceKey 未配置")
            return False

        bark_url = f"https://api.day.app/{settings.SPUG_BARK_KEY}"

        # 构建请求参数
        params = {
            "title": title,
            "body": content,
            "sound": kwargs.get("sound", "alarm"),
        }

        # 可选参数
        if kwargs.get("icon"):
            params["icon"] = kwargs["icon"]
        if kwargs.get("group"):
            params["group"] = kwargs["group"]
        if kwargs.get("url"):
            params["url"] = kwargs["url"]

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(bark_url, params=params, timeout=10)
                result = response.json()
                if result.get("code") == 200:
                    loguru.logger.info(f"[Bark] 通知发送成功: {title}")
                    return True
                else:
                    loguru.logger.error(f"[Bark] 通知发送失败: {result}")
                    return False
        except Exception as e:
            loguru.logger.error(f"[Bark] 请求异常: {e}")
            return False

    async def _send_serverchan(self, title: str, content: str, **kwargs) -> bool:
        """发送 Server酱 通知 (微信)"""
        if not self.webhook_url:
            loguru.logger.warning("[ServerChan] Webhook URL 未配置")
            return False

        # ServerChan Turbo 版本
        data = {
            "title": title,
            "content": content,
            "template": kwargs.get("template", "html"),
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.webhook_url,
                    json=data,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                result = response.json()
                if result.get("code") == 0:
                    loguru.logger.info(f"[ServerChan] 通知发送成功: {title}")
                    return True
                else:
                    loguru.logger.error(f"[ServerChan] 通知发送失败: {result}")
                    return False
        except Exception as e:
            loguru.logger.error(f"[ServerChan] 请求异常: {e}")
            return False

    async def _send_dingtalk(self, title: str, content: str, **kwargs) -> bool:
        """发送钉钉通知"""
        if not self.webhook_url:
            loguru.logger.warning("[DingTalk] Webhook URL 未配置")
            return False

        timestamp = str(round(time.time() * 1000))
        secret = settings.SPUG_DINGTALK_SECRET or ""

        # 计算签名
        if secret:
            sign = self._generate_dingtalk_sign(timestamp, secret)
            url = f"{self.webhook_url}&timestamp={timestamp}&sign={sign}"
        else:
            url = self.webhook_url

        # 构建消息
        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": f"### {title}\n\n{content}"
            }
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=data,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                result = response.json()
                if result.get("errcode") == 0:
                    loguru.logger.info(f"[DingTalk] 通知发送成功: {title}")
                    return True
                else:
                    loguru.logger.error(f"[DingTalk] 通知发送失败: {result}")
                    return False
        except Exception as e:
            loguru.logger.error(f"[DingTalk] 请求异常: {e}")
            return False

    def _generate_dingtalk_sign(self, timestamp: str, secret: str) -> str:
        """生成钉钉签名"""
        secret_enc = secret.encode("utf-8")
        string_to_sign = f"{timestamp}\n{secret}"
        string_to_sign_enc = string_to_sign.encode("utf-8")
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = base64.b64encode(hmac_code).decode("utf-8")
        return sign

    async def _send_feishu(self, title: str, content: str, **kwargs) -> bool:
        """发送飞书通知"""
        if not self.webhook_url:
            loguru.logger.warning("[Feishu] Webhook URL 未配置")
            return False

        timestamp = str(round(time.time()))
        secret = settings.SPUG_FEISHU_SECRET or ""

        # 如果有签名密钥，计算签名
        if secret:
            sign = self._generate_feishu_sign(timestamp, secret)
            url = f"{self.webhook_url}&timestamp={timestamp}&sign={sign}"
        else:
            url = self.webhook_url

        # 构建消息
        data = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": title
                    },
                    "template": kwargs.get("color", "blue")
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": content
                        }
                    }
                ]
            }
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=data,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                result = response.json()
                if result.get("code") == 0 or result.get("StatusCode") == 0:
                    loguru.logger.info(f"[Feishu] 通知发送成功: {title}")
                    return True
                else:
                    loguru.logger.error(f"[Feishu] 通知发送失败: {result}")
                    return False
        except Exception as e:
            loguru.logger.error(f"[Feishu] 请求异常: {e}")
            return False

    def _generate_feishu_sign(self, timestamp: str, secret: str) -> str:
        """生成飞书签名"""
        secret_enc = secret.encode("utf-8")
        string_to_sign = f"{timestamp}\n{secret}"
        string_to_sign_enc = string_to_sign.encode("utf-8")
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = base64.b64encode(hmac_code).decode("utf-8")
        return sign

    async def _send_telegram(self, title: str, content: str, **kwargs) -> bool:
        """发送 Telegram 通知"""
        if not self.webhook_url:
            loguru.logger.warning("[Telegram] Webhook URL 未配置")
            return False

        # Telegram Bot API
        message = f"*{title}*\n\n{content}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.webhook_url,
                    json={
                        "text": message,
                        "parse_mode": "Markdown"
                    },
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                result = response.json()
                if result.get("ok"):
                    loguru.logger.info(f"[Telegram] 通知发送成功: {title}")
                    return True
                else:
                    loguru.logger.error(f"[Telegram] 通知发送失败: {result}")
                    return False
        except Exception as e:
            loguru.logger.error(f"[Telegram] 请求异常: {e}")
            return False

    async def _send_email(self, title: str, content: str, **kwargs) -> bool:
        """发送邮件通知"""
        import aiosmtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        if not all([settings.SPUG_EMAIL_HOST, settings.SPUG_EMAIL_USER, settings.SPUG_EMAIL_PASSWORD]):
            loguru.logger.warning("[Email] 邮件配置不完整")
            return False

        to_email = kwargs.get("to") or settings.SPUG_EMAIL_TO
        if not to_email:
            loguru.logger.warning("[Email] 收件人未配置")
            return False

        message = MIMEMultipart("alternative")
        message["Subject"] = title
        message["From"] = settings.SPUG_EMAIL_USER
        message["To"] = to_email

        # 纯文本和HTML版本
        text_part = MIMEText(content, "plain", "utf-8")
        html_part = MIMEText(f"""
        <html>
        <body>
            <h2>{title}</h2>
            <div style="font-size: 14px; line-height: 1.6;">
                {content.replace('\n', '<br>')}
            </div>
        </body>
        </html>
        """, "html", "utf-8")

        message.attach(text_part)
        message.attach(html_part)

        try:
            async with aiosmtplib.SMTP(
                settings.SPUG_EMAIL_HOST,
                settings.SPUG_EMAIL_PORT or 587
            ) as smtp:
                await smtp.login(settings.SPUG_EMAIL_USER, settings.SPUG_EMAIL_PASSWORD)
                await smtp.send_message(message)
                loguru.logger.info(f"[Email] 邮件发送成功: {title} -> {to_email}")
                return True
        except Exception as e:
            loguru.logger.error(f"[Email] 邮件发送失败: {e}")
            return False

    async def _send_webhook(self, title: str, content: str, **kwargs) -> bool:
        """发送通用 Webhook 通知"""
        if not self.webhook_url:
            return False

        data = {
            "title": title,
            "content": content,
            "timestamp": time.time(),
        }
        data.update(kwargs)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.webhook_url,
                    json=data,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                if response.status_code == 200:
                    loguru.logger.info(f"[Webhook] 通知发送成功: {title}")
                    return True
                else:
                    loguru.logger.error(f"[Webhook] 通知发送失败: {response.status_code}")
                    return False
        except Exception as e:
            loguru.logger.error(f"[Webhook] 请求异常: {e}")
            return False


# 发送验证码的便捷方法
async def send_verification_code(phone: str, code: str) -> bool:
    """
    通过Spug发送验证码通知

    Args:
        phone: 手机号
        code: 验证码

    Returns:
        bool: 发送是否成功
    """
    notifier = SpugNotifier()
    title = "【心灵伴侣AI】验证码通知"
    content = f"您的验证码是: {code}\n\n请在5分钟内完成验证，切勿将验证码告知他人。"
    return await notifier.send(title, content, group="verification")


# 单例实例
_spug_notifier: Optional[SpugNotifier] = None


def get_spug_notifier() -> SpugNotifier:
    """获取Spug通知服务实例"""
    global _spug_notifier
    if _spug_notifier is None:
        _spug_notifier = SpugNotifier()
    return _spug_notifier
