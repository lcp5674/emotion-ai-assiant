"""
系统监控与告警服务
"""
import loguru
import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import json

from app.core.database import get_db, get_redis
from app.services.cache_service import get_cache_service


class AlertLevel(str, Enum):
    """告警级别"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertType(str, Enum):
    """告警类型"""
    # 系统健康
    HIGH_ERROR_RATE = "high_error_rate"
    HIGH_LATENCY = "high_latency"
    SERVICE_DOWN = "service_down"
    # 用户行为
    UNUSUAL_USER_ACTIVITY = "unusual_user_activity"
    CRISIS_DETECTED = "crisis_detected"
    # 业务指标
    MEMBER_EXPIRED = "member_expired"
    QUOTA_EXCEEDED = "quota_exceeded"
    # 安全
    SUSPICIOUS_LOGIN = "suspicious_login"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"


class Alert:
    """告警对象"""

    def __init__(
        self,
        level: AlertLevel,
        alert_type: AlertType,
        title: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = None,
    ):
        self.level = level
        self.alert_type = alert_type
        self.title = title
        self.message = message
        self.metadata = metadata or {}
        self.user_id = user_id
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> dict:
        return {
            "level": self.level.value,
            "type": self.alert_type.value,
            "title": self.title,
            "message": self.message,
            "metadata": self.metadata,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat(),
        }

    def __str__(self) -> str:
        return f"[{self.level.value.upper()}] {self.title}: {self.message}"


class MonitoringService:
    """监控服务"""

    def __init__(self):
        self._alert_handlers: List[callable] = []
        self._metrics_cache = {}
        self._alert_history: List[Alert] = []
        self._max_history = 1000

    def register_alert_handler(self, handler: callable):
        """注册告警处理器"""
        self._alert_handlers.append(handler)

    async def send_alert(self, alert: Alert):
        """发送告警"""
        loguru.logger.log(
            self._level_to_loguru(alert.level),
            str(alert),
            extra=alert.to_dict()
        )

        # 记录到历史
        self._alert_history.append(alert)
        if len(self._alert_history) > self._max_history:
            self._alert_history = self._alert_history[-self._max_history:]

        # 调用处理器
        for handler in self._alert_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(alert)
                else:
                    handler(alert)
            except Exception as e:
                loguru.logger.warning(f"Alert handler error: {e}")

    def _level_to_loguru(self, level: AlertLevel) -> str:
        """转换告警级别到loguru级别"""
        mapping = {
            AlertLevel.INFO: "INFO",
            AlertLevel.WARNING: "WARNING",
            AlertLevel.ERROR: "ERROR",
            AlertLevel.CRITICAL: "ERROR",
        }
        return mapping.get(level, "INFO")

    # ==================== 告警方法 ====================

    async def alert_high_error_rate(self, endpoint: str, error_rate: float, threshold: float = 0.05):
        """告警：高错误率"""
        if error_rate > threshold:
            await self.send_alert(Alert(
                level=AlertLevel.ERROR,
                alert_type=AlertType.HIGH_ERROR_RATE,
                title="高错误率告警",
                message=f"端点 {endpoint} 错误率达到 {error_rate:.2%}，超过阈值 {threshold:.2%}",
                metadata={"endpoint": endpoint, "error_rate": error_rate, "threshold": threshold}
            ))

    async def alert_high_latency(self, endpoint: str, latency_ms: float, threshold_ms: float = 1000):
        """告警：高延迟"""
        if latency_ms > threshold_ms:
            await self.send_alert(Alert(
                level=AlertLevel.WARNING,
                alert_type=AlertType.HIGH_LATENCY,
                title="高延迟告警",
                message=f"端点 {endpoint} 延迟 {latency_ms:.0f}ms，超过阈值 {threshold_ms:.0f}ms",
                metadata={"endpoint": endpoint, "latency_ms": latency_ms, "threshold_ms": threshold_ms}
            ))

    async def alert_crisis_detected(self, user_id: int, crisis_level: str, message_preview: str):
        """告警：检测到危机信号"""
        level = AlertLevel.CRITICAL if crisis_level in ["HIGH", "CRITICAL"] else AlertLevel.ERROR
        await self.send_alert(Alert(
            level=level,
            alert_type=AlertType.CRISIS_DETECTED,
            title="危机信号检测",
            message=f"用户 {user_id} 触发危机检测，等级: {crisis_level}",
            metadata={"crisis_level": crisis_level, "message_preview": message_preview[:100]},
            user_id=user_id
        ))

    async def alert_service_down(self, service_name: str, error: str):
        """告警：服务不可用"""
        await self.send_alert(Alert(
            level=AlertLevel.CRITICAL,
            alert_type=AlertType.SERVICE_DOWN,
            title="服务不可用",
            message=f"服务 {service_name} 不可用: {error}",
            metadata={"service": service_name, "error": error}
        ))

    async def alert_suspicious_activity(self, user_id: int, activity_type: str, details: dict):
        """告警：可疑活动"""
        await self.send_alert(Alert(
            level=AlertLevel.WARNING,
            alert_type=AlertType.SUSPICIOUS_LOGIN,
            title="可疑活动检测",
            message=f"用户 {user_id} 存在可疑{activity_type}",
            metadata=details,
            user_id=user_id
        ))

    # ==================== 指标收集 ====================

    async def record_request_metric(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        latency_ms: float,
        user_id: Optional[int] = None
    ):
        """记录请求指标"""
        cache = get_cache_service()
        key = f"metrics:request:{datetime.utcnow().strftime('%Y%m%d%H')}"

        # 获取当前指标
        metrics = await cache.get(key) or {
            "total": 0,
            "errors": 0,
            "latency_sum": 0,
            "latency_max": 0,
            "endpoints": {},
        }

        metrics["total"] += 1
        if status_code >= 400:
            metrics["errors"] += 1
        metrics["latency_sum"] += latency_ms
        metrics["latency_max"] = max(metrics["latency_max"], latency_ms)

        # 按端点统计
        ep_key = f"{method}:{endpoint}"
        if ep_key not in metrics["endpoints"]:
            metrics["endpoints"][ep_key] = {"total": 0, "errors": 0, "latency_sum": 0}
        metrics["endpoints"][ep_key]["total"] += 1
        if status_code >= 400:
            metrics["endpoints"][ep_key]["errors"] += 1
        metrics["endpoints"][ep_key]["latency_sum"] += latency_ms

        await cache.set(key, metrics, ttl=7200)

        # 检查告警条件
        if metrics["total"] > 0:
            error_rate = metrics["errors"] / metrics["total"]
            await self.alert_high_error_rate(endpoint, error_rate)

        if latency_ms > 1000:
            await self.alert_high_latency(endpoint, latency_ms)

    async def get_metrics_summary(self, hours: int = 24) -> dict:
        """获取指标摘要"""
        cache = get_cache_service()
        summary = {
            "total_requests": 0,
            "total_errors": 0,
            "avg_latency_ms": 0,
            "max_latency_ms": 0,
            "error_rate": 0,
            "endpoints": {},
        }

        now = datetime.utcnow()
        for i in range(hours):
            key = f"metrics:request:{(now - timedelta(hours=i)).strftime('%Y%m%d%H')}"
            metrics = await cache.get(key)
            if metrics:
                summary["total_requests"] += metrics["total"]
                summary["total_errors"] += metrics["errors"]
                summary["max_latency_ms"] = max(summary["max_latency_ms"], metrics["latency_max"])

                for ep, ep_metrics in metrics.get("endpoints", {}).items():
                    if ep not in summary["endpoints"]:
                        summary["endpoints"][ep] = {"total": 0, "errors": 0, "latency_sum": 0}
                    summary["endpoints"][ep]["total"] += ep_metrics["total"]
                    summary["endpoints"][ep]["errors"] += ep_metrics["errors"]
                    summary["endpoints"][ep]["latency_sum"] += ep_metrics["latency_sum"]

        if summary["total_requests"] > 0:
            summary["avg_latency_ms"] = summary["total_requests"] and (
                sum(e["latency_sum"] for e in summary["endpoints"].values()) / summary["total_requests"]
            ) or 0
            summary["error_rate"] = summary["total_errors"] / summary["total_requests"]

        # 计算端点平均延迟
        for ep, metrics in summary["endpoints"].items():
            if metrics["total"] > 0:
                metrics["avg_latency_ms"] = metrics["latency_sum"] / metrics["total"]
            del metrics["latency_sum"]

        return summary

    # ==================== 健康检查 ====================

    async def check_system_health(self) -> dict:
        """系统健康检查"""
        health = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {}
        }

        # 数据库检查
        try:
            db = next(get_db())
            db.execute("SELECT 1")
            db.close()
            health["components"]["database"] = {"status": "ok"}
        except Exception as e:
            health["components"]["database"] = {"status": "error", "message": str(e)}
            health["status"] = "degraded"

        # Redis检查
        try:
            redis_client = await get_redis()
            await redis_client.ping()
            health["components"]["redis"] = {"status": "ok"}
        except Exception as e:
            health["components"]["redis"] = {"status": "error", "message": str(e)}
            health["status"] = "degraded"

        return health

    # ==================== 告警历史 ====================

    def get_alert_history(
        self,
        level: Optional[AlertLevel] = None,
        alert_type: Optional[AlertType] = None,
        hours: int = 24,
        limit: int = 100
    ) -> List[dict]:
        """获取告警历史"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        filtered = [
            alert for alert in self._alert_history
            if alert.timestamp >= cutoff
        ]

        if level:
            filtered = [a for a in filtered if a.level == level]
        if alert_type:
            filtered = [a for a in filtered if a.alert_type == alert_type]

        return [a.to_dict() for a in filtered[-limit:]]

    def get_alert_stats(self, hours: int = 24) -> dict:
        """获取告警统计"""
        from collections import Counter
        cutoff = datetime.utcnow() - timedelta(hours=hours)

        filtered = [a for a in self._alert_history if a.timestamp >= cutoff]

        level_counts = Counter(a.level.value for a in filtered)
        type_counts = Counter(a.alert_type.value for a in filtered)

        return {
            "total": len(filtered),
            "by_level": dict(level_counts),
            "by_type": dict(type_counts),
            "critical_count": level_counts.get("critical", 0),
        }


class WebhookAlertHandler:
    """Webhook告警处理器"""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    async def __call__(self, alert: Alert):
        """发送Webhook告警"""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                payload = {
                    "msg_type": "interactive",
                    "card": {
                        "config": {"wide_screen_mode": True},
                        "header": {
                            "title": {"tag": "plain_text", "content": f"🚨 {alert.title}"},
                            "template": self._level_to_color(alert.level)
                        },
                        "elements": [
                            {"tag": "markdown", "content": f"**级别**: {alert.level.value.upper()}"},
                            {"tag": "markdown", "content": f"**类型**: {alert.alert_type.value}"},
                            {"tag": "markdown", "content": f"**消息**: {alert.message}"},
                            {"tag": "markdown", "content": f"**时间**: {alert.timestamp.isoformat()}"},
                        ]
                    }
                }
                async with session.post(self.webhook_url, json=payload) as resp:
                    if resp.status != 200:
                        loguru.logger.warning(f"Webhook failed: {resp.status}")
        except Exception as e:
            loguru.logger.warning(f"Webhook alert error: {e}")

    def _level_to_color(self, level: AlertLevel) -> str:
        mapping = {
            AlertLevel.INFO: "blue",
            AlertLevel.WARNING: "yellow",
            AlertLevel.ERROR: "red",
            AlertLevel.CRITICAL: "red",
        }
        return mapping.get(level, "blue")


# 全局实例
_monitoring_service: Optional[MonitoringService] = None


def get_monitoring_service() -> MonitoringService:
    """获取监控服务实例"""
    global _monitoring_service
    if _monitoring_service is None:
        _monitoring_service = MonitoringService()
    return _monitoring_service
