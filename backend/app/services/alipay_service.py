"""
支付宝支付服务
"""
import json
import time
from typing import Optional, Dict, Any
from datetime import datetime
import loguru
from urllib.parse import quote_plus, unquote, parse_qs

from app.core.config import settings


class AlipayService:
    """支付宝支付服务"""

    def __init__(self):
        self.enabled = settings.ALIPAY_ENABLED
        self.appid = settings.ALIPAY_APPID
        self.private_key_path = settings.ALIPAY_PRIVATE_KEY_PATH
        self.public_key_path = settings.ALIPAY_PUBLIC_KEY_PATH
        self.gateway = settings.ALIPAY_GATEWAY
        self.notify_url = settings.ALIPAY_NOTIFY_URL
        self.return_url = settings.ALIPAY_RETURN_URL
        
        # 加载密钥
        self.private_key = self._load_key(self.private_key_path)
        self.alipay_public_key = self._load_key(self.public_key_path)

    def _load_key(self, path: str) -> Optional[str]:
        """加载密钥文件"""
        if not path:
            return None
        try:
            with open(path, "r") as f:
                return f.read()
        except Exception as e:
            loguru.logger.error(f"加载密钥失败 {path}: {e}")
            return None

    def is_enabled(self) -> bool:
        return self.enabled and bool(
            self.appid and self.private_key and self.alipay_public_key
        )

    async def create_page_pay_order(
        self,
        order_no: str,
        amount: float,
        subject: str,
        return_url: Optional[str] = None,
        notify_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        创建支付宝网页支付订单
        
        Args:
            order_no: 商户订单号
            amount: 金额（元）
            subject: 商品标题
            return_url: 支付成功后跳转地址
            notify_url: 异步回调地址
        
        Returns:
            dict: 包含支付跳转URL
        """
        if not self.is_enabled():
            return {
                "mode": "mock",
                "order_no": order_no,
                "pay_url": f"/payment/mock/{order_no}",
            }

        try:
            # 构建请求参数
            biz_content = json.dumps({
                "out_trade_no": order_no,
                "total_amount": float(amount),
                "subject": subject,
                "product_code": "FAST_INSTANT_TRADE_PAY",
            }, ensure_ascii=False)

            params = {
                "app_id": self.appid,
                "method": "alipay.trade.page.pay",
                "format": "JSON",
                "charset": "utf-8",
                "sign_type": "RSA2",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "version": "1.0",
                "notify_url": notify_url or self.notify_url,
                "return_url": return_url or self.return_url,
                "biz_content": biz_content,
            }

            # 签名
            params["sign"] = self._sign(params)

            # 构建支付URL
            query_string = "&".join([f"{k}={quote_plus(str(v))}" for k, v in params.items()])
            pay_url = f"{self.gateway}?{query_string}"

            return {
                "mode": "alipay",
                "order_no": order_no,
                "pay_url": pay_url,
            }

        except Exception as e:
            loguru.logger.error(f"支付宝支付下单失败: {e}")
            return {
                "mode": "error",
                "message": str(e),
            }

    async def create_wap_pay_order(
        self,
        order_no: str,
        amount: float,
        subject: str,
        return_url: Optional[str] = None,
        notify_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        创建支付宝手机网站支付订单
        
        Args:
            order_no: 商户订单号
            amount: 金额（元）
            subject: 商品标题
            return_url: 支付成功后跳转地址
            notify_url: 异步回调地址
        
        Returns:
            dict: 包含支付跳转URL
        """
        if not self.is_enabled():
            return {
                "mode": "mock",
                "order_no": order_no,
                "pay_url": f"/payment/mock/{order_no}",
            }

        try:
            # 构建请求参数
            biz_content = json.dumps({
                "out_trade_no": order_no,
                "total_amount": float(amount),
                "subject": subject,
                "product_code": "QUICK_WAP_WAY",
            }, ensure_ascii=False)

            params = {
                "app_id": self.appid,
                "method": "alipay.trade.wap.pay",
                "format": "JSON",
                "charset": "utf-8",
                "sign_type": "RSA2",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "version": "1.0",
                "notify_url": notify_url or self.notify_url,
                "return_url": return_url or self.return_url,
                "biz_content": biz_content,
            }

            # 签名
            params["sign"] = self._sign(params)

            # 构建支付URL
            query_string = "&".join([f"{k}={quote_plus(str(v))}" for k, v in params.items()])
            pay_url = f"{self.gateway}?{query_string}"

            return {
                "mode": "alipay",
                "order_no": order_no,
                "pay_url": pay_url,
            }

        except Exception as e:
            loguru.logger.error(f"支付宝WAP支付下单失败: {e}")
            return {
                "mode": "error",
                "message": str(e),
            }

    async def query_order(self, order_no: str) -> Optional[Dict[str, Any]]:
        """
        查询订单支付状态
        
        Args:
            order_no: 商户订单号
            
        Returns:
            dict: 订单状态信息
        """
        if not self.is_enabled():
            return None

        try:
            biz_content = json.dumps({
                "out_trade_no": order_no,
            })

            params = {
                "app_id": self.appid,
                "method": "alipay.trade.query",
                "format": "JSON",
                "charset": "utf-8",
                "sign_type": "RSA2",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "version": "1.0",
                "biz_content": biz_content,
            }

            params["sign"] = self._sign(params)

            import httpx
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    self.gateway,
                    data=params,
                    timeout=30.0,
                )

            if resp.status_code == 200:
                data = resp.json()
                response_key = "alipay_trade_query_response"
                if response_key in data:
                    result = data[response_key]
                    if result.get("code") == "10000":
                        return {
                            "order_no": result.get("out_trade_no"),
                            "trade_no": result.get("trade_no"),
                            "status": result.get("trade_status"),
                            "total_amount": result.get("total_amount"),
                            "buyer_logon_id": result.get("buyer_logon_id"),
                            "send_pay_date": result.get("send_pay_date"),
                        }
                    else:
                        loguru.logger.error(f"支付宝订单查询失败: {result.get('msg')}")
            return None

        except Exception as e:
            loguru.logger.error(f"支付宝订单查询异常: {e}")
            return None

    def verify_notify(self, params: Dict) -> bool:
        """
        验证异步回调签名
        
        Args:
            params: 回调参数
            
        Returns:
            bool: 验证是否通过
        """
        if not self.is_enabled():
            return False

        try:
            # 取出sign和sign_type
            sign = params.pop("sign", None)
            sign_type = params.pop("sign_type", None)
            
            if not sign or sign_type != "RSA2":
                return False

            # 参数排序
            sorted_params = sorted(params.items(), key=lambda x: x[0])
            
            # 拼接待签名字符串
            message = "&".join([f"{k}={unquote(str(v))}" for k, v in sorted_params])

            # 验签
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import padding
            from cryptography.hazmat.backends import default_backend

            public_key_obj = serialization.load_pem_public_key(
                self.alipay_public_key.encode(),
                backend=default_backend()
            )
            
            public_key_obj.verify(
                bytes.fromhex(sign),
                message.encode("utf-8"),
                padding.PKCS1v15(),
                hashes.SHA256(),
            )
            return True

        except Exception as e:
            loguru.logger.error(f"支付宝回调验签失败: {e}")
            return False

    def verify_return(self, params: Dict) -> bool:
        """
        验证同步跳转签名
        
        Args:
            params: 跳转参数
            
        Returns:
            bool: 验证是否通过
        """
        return self.verify_notify(params)

    def _sign(self, params: Dict) -> str:
        """
        对参数进行RSA2签名
        
        Args:
            params: 待签名参数
            
        Returns:
            str: 签名结果
        """
        # 移除空值和sign
        params = {k: v for k, v in params.items() if v is not None and k != "sign"}
        
        # 参数排序
        sorted_params = sorted(params.items(), key=lambda x: x[0])
        
        # 拼接待签名字符串
        message = "&".join([f"{k}={v}" for k, v in sorted_params])

        # 签名
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding, rsa
        from cryptography.hazmat.backends import default_backend

        private_key_obj = serialization.load_pem_private_key(
            self.private_key.encode(),
            password=None,
            backend=default_backend()
        )
        assert isinstance(private_key_obj, rsa.RSAPrivateKey)
        
        sign = private_key_obj.sign(
            message.encode("utf-8"),
            padding.PKCS1v15(),
            hashes.SHA256(),
        )
        return sign.hex()


_alipay_service: Optional[AlipayService] = None


def get_alipay_service() -> AlipayService:
    """获取支付宝支付服务实例"""
    global _alipay_service
    if _alipay_service is None:
        _alipay_service = AlipayService()
    return _alipay_service
