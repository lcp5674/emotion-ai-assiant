"""
支付服务 - Stripe
"""
from typing import Optional, Dict, Any
import stripe
import loguru

from app.core.config import settings


class StripePayService:
    def __init__(self):
        stripe.api_key = settings.STRIPE_API_KEY if hasattr(settings, 'STRIPE_API_KEY') else None
    
    async def create_checkout_session(
        self,
        order_no: str,
        amount: int,
        description: str,
        success_url: str,
        cancel_url: str,
    ) -> Dict[str, Any]:
        """创建Stripe支付会话"""
        if not stripe.api_key:
            return {
                "mode": "mock",
                "order_no": order_no,
                "pay_url": f"/payment/mock/{order_no}/complete",
            }
        
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'cny',
                        'product_data': {
                            'name': description,
                        },
                        'unit_amount': amount,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={'order_no': order_no},
            )
            
            return {
                "mode": "stripe",
                "session_id": session.id,
                "checkout_url": session.url,
                "order_no": order_no,
            }
        except Exception as e:
            loguru.logger.error(f"Stripe创建会话失败: {e}")
            return {
                "mode": "mock",
                "order_no": order_no,
                "pay_url": f"/payment/mock/{order_no}/complete",
            }
    
    async def verify_payment(self, session_id: str) -> Optional[Dict[str, Any]]:
        """验证Stripe支付状态"""
        if not stripe.api_key:
            return {"status": "paid", "order_no": "mock"}
        
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            return {
                "status": session.payment_status,
                "order_no": session.metadata.get("order_no"),
            }
        except Exception as e:
            loguru.logger.error(f"Stripe验证失败: {e}")
            return None
    
    async def handle_webhook(self, payload: bytes, signature: str) -> Optional[Dict[str, Any]]:
        """处理Stripe webhook"""
        if not stripe.api_key:
            return None
        
        webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', None)
        if not webhook_secret:
            return None
        
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, webhook_secret
            )
            
            if event['type'] == 'checkout.session.completed':
                session = event['data']['object']
                return {
                    "status": "paid",
                    "order_no": session.metadata.get("order_no"),
                }
            
            return None
        except Exception as e:
            loguru.logger.error(f"Stripe webhook处理失败: {e}")
            return None


_stripe_service: Optional[StripePayService] = None


def get_stripe_pay_service() -> StripePayService:
    global _stripe_service
    if _stripe_service is None:
        _stripe_service = StripePayService()
    return _stripe_service
