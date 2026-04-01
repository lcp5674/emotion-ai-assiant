"""
微信支付服务
"""
import time
import hashlib
import json
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime
import loguru

from app.core.config import settings


class WechatPayService:
    """微信支付V3服务"""

    def __init__(self):
        self.enabled = settings.WECHAT_PAY_ENABLED
        self.mchid = settings.WECHAT_MCHID
        self.serial_no = settings.WECHAT_SERIAL_NO
        self.private_key_path = settings.WECHAT_PRIVATE_KEY_PATH
        self.apiv3_key = settings.WECHAT_APIV3_KEY
        self.appid = settings.WECHAT_APPID
        self.notify_url = settings.WECHAT_NOTIFY_URL

    def is_enabled(self) -> bool:
        return self.enabled and bool(self.mchid and self.apiv3_key)

    async def create_native_order(
        self,
        order_no: str,
        amount: int,
        description: str,
    ) -> Dict[str, Any]:
        """
        创建微信Native支付订单
        
        Args:
            order_no: 商户订单号
            amount: 金额（分）
            description: 商品描述
        
        Returns:
            dict: 包含 code_url 用于生成二维码
        """
        if not self.is_enabled():
            return {
                "mode": "mock",
                "order_no": order_no,
                "pay_url": f"/payment/mock/{order_no}",
            }

        try:
            import httpx

            url = "https://api.mch.weixin.qq.com/v3/pay/transactions/native"

            time_str = datetime.now().strftime("%Y%m-%d%H:%M:%S")
            nonce_str = self._generate_nonce()
            message = f"POST\n/v3/pay/transactions/native\n{time_str}\n{nonce_str}\n{json.dumps(self._build_order_payload(order_no, amount, description))}\n"
            signature = self._sign(message)

            headers = {
                "Authorization": f'WECHATPAY2-SHA256-RSA2048 mchid="{self.mchid}",nonce_str="{nonce_str}",signature="{signature}",timestamp="{time_str}",serial_no="{self.serial_no}"',
                "Content-Type": "application/json",
                "Accept": "application/json",
            }

            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    url,
                    headers=headers,
                    json=self._build_order_payload(order_no, amount, description),
                    timeout=30.0,
                )

            if resp.status_code == 200:
                data = resp.json()
                return {
                    "mode": "wechat",
                    "order_no": order_no,
                    "code_url": data.get("code_url"),
                    "prepay_id": data.get("prepay_id"),
                }
            else:
                loguru.logger.error(f"微信支付下单失败: {resp.text}")
                return {"mode": "error", "message": "支付创建失败"}

        except ImportError:
            loguru.logger.warning("httpx未安装，使用Mock支付")
            return {
                "mode": "mock",
                "order_no": order_no,
                "pay_url": f"/payment/mock/{order_no}",
            }
        except Exception as e:
            loguru.logger.error(f"微信支付异常: {e}")
            return {
                "mode": "error",
                "message": str(e),
            }

    def _build_order_payload(self, order_no: str, amount: int, description: str) -> Dict:
        return {
            "mchid": self.mchid,
            "out_trade_no": order_no,
            "appid": self.appid,
            "description": description,
            "notify_url": self.notify_url,
            "amount": {
                "total": amount,
                "currency": "CNY",
            },
            "time_expire": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        }

    def _generate_nonce(self) -> str:
        import random
        import string
        return "".join(random.choices(string.ascii_letters + string.digits, k=32))

    def _sign(self, message: str) -> str:
        try:
            with open(self.private_key_path, "r") as f:
                private_key = f.read()
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import padding, rsa
            from cryptography.hazmat.backends import default_backend
            private_key_obj = serialization.load_pem_private_key(
                private_key.encode(), password=None, backend=default_backend()
            )
            assert isinstance(private_key_obj, rsa.RSAPrivateKey)
            sign = private_key_obj.sign(
                message.encode("utf-8"),
                padding.PKCS1v15(),
                hashes.SHA256(),
            )
            return sign.hex()
        except Exception as e:
            loguru.logger.error(f"签名失败: {e}")
            return ""

    async def parse_notify(self, body: bytes, headers: Dict) -> Optional[Dict]:
        if not self.is_enabled():
            return None

        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM

            req_info = headers.get("Wechatpay-Serial", "")
            nonce = headers.get("Wechatpay-Nonce", "")
            associated_data = headers.get("Wechatpay-Attached-Data", "")
            ciphertext = body.decode()

            cipher = AESGCM(self.apiv3_key.encode())
            plaintext = cipher.decrypt(nonce.encode(), ciphertext.encode(), associated_data.encode())
            result = json.loads(plaintext.decode())

            if result.get("event_type") == "TRANSACTION.SUCCESS":
                return {
                    "order_no": result["resource"]["out_trade_no"],
                    "status": "paid",
                    "transaction_id": result["resource"]["transaction_id"],
                }
        except Exception as e:
            loguru.logger.error(f"解析支付回调失败: {e}")
        return None


_wechat_pay_service: Optional[WechatPayService] = None


def get_wechat_pay_service() -> WechatPayService:
    """获取微信支付服务实例"""
    global _wechat_pay_service
    if _wechat_pay_service is None:
        _wechat_pay_service = WechatPayService()
    return _wechat_pay_service
