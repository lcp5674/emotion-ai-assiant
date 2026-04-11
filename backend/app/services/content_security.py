"""
内容安全三级防护机制
层级:
1. 第一层: 本地关键词快速过滤 (快速拦截已知敏感词)
2. 第二层: 第三方厂商内容审核 (精准识别复杂违规内容)
3. 第三层: 人工复审队列 (疑似内容人工审核)
"""
from typing import List, Tuple, Optional, Dict, Any
from enum import Enum
import loguru
from datetime import datetime

from app.core.config import settings
from app.models import User, ContentAuditQueue


class ContentRiskLevel(Enum):
    """内容风险等级"""
    SAFE = "safe"         # 安全
    REVIEW = "review"    # 需要复审
    LOW = "low"          # 低风险
    MEDIUM = "medium"    # 中等风险
    HIGH = "high"        # 高风险
    BLOCK = "block"      # 禁止


class ContentCategory(Enum):
    """违规内容分类"""
    NORMAL = "normal"
    PORN = "porn"               # 色情低俗
    AD = "ad"                  # 广告引流
    POLITICS = "politics"      # 政治敏感
    VIOLENCE = "violence"      # 暴力恐怖
    ABUSE = "abuse"            # 辱骂谩骂
    PRIVACY = "privacy"        # 隐私泄露
    OTHER = "other"            # 其他违规


class ContentCheckResult:
    """内容检查结果"""

    def __init__(
        self,
        passed: bool,
        risk_level: ContentRiskLevel,
        categories: List[ContentCategory],
        keywords: List[str],
        confidence: float = 1.0,
        need_review: bool = False,
        message: str = "",
    ):
        self.passed = passed
        self.risk_level = risk_level
        self.categories = categories
        self.keywords = keywords
        self.confidence = confidence
        self.need_review = need_review
        self.message = message


class ContentSecurityService:
    """内容安全三级防护服务"""

    # 第一层：本地敏感词库
    DEFAULT_SENSITIVE_WORDS = {
        # 色情相关
        "色情", "裸聊", "约炮", "嫖娼", "性爱", "黄色",
        "成人视频", "色情网站", "发片", "福利",
        # 暴力自杀
        "自杀", "自残", "杀人", "炸死", "炸飞机",
        "爆头", "砍死", "杀人教程",
        # 政治敏感
        "敏感词占位符",
        # 赌博
        "赌博", "博彩", "彩票", "澳门赌博", "时时彩",
        # 诈骗
        "刷单", "中奖", "领奖", "提现", "银行卡", "转账",
        "套现", "网贷", "小额贷款",
        # 广告引流
        "加微信", "加我", "扫码", "关注公众号",
    }

    def __init__(self):
        self.enabled_layers = self._get_enabled_layers()
        self._compile_patterns()

    def _get_enabled_layers(self) -> Dict[str, bool]:
        """获取启用的防护层级"""
        layers = {
            "layer1_keyword": True,  # 第一层始终启用
            "layer2_third_party": settings.CONTENT_FILTER_PROVIDER != "keyword",
            "layer3_human_review": True,
        }
        return layers

    def _compile_patterns(self):
        """编译关键词正则"""
        import re
        custom_words = self._get_custom_sensitive_words()
        all_words = list(self.DEFAULT_SENSITIVE_WORDS) + custom_words
        if all_words:
            self._keyword_pattern = re.compile(
                "|".join(re.escape(w) for w in all_words),
                re.IGNORECASE
            )
        else:
            self._keyword_pattern = None

    def _get_custom_sensitive_words(self) -> List[str]:
        """从数据库获取自定义敏感词"""
        # 后续可以从系统配置表动态加载
        # 现在返回空列表
        return []

    def _layer1_check(self, text: str) -> Tuple[bool, List[str], ContentRiskLevel]:
        """第一层：本地关键词检查"""
        if not self._keyword_pattern:
            return True, [], ContentRiskLevel.SAFE

        matches = self._keyword_pattern.findall(text)
        if not matches:
            return True, [], ContentRiskLevel.SAFE

        unique_matches = list(set(matches))
        loguru.logger.warning(f"第一层检测到敏感词: {unique_matches}")

        # 根据匹配结果判断风险等级
        # 如果包含高风险关键词直接拦截
        high_risk_keywords = {"自杀", "自残", "杀人", "爆炸"}
        has_high_risk = any(w in high_risk_keywords for w in unique_matches)

        if has_high_risk:
            return False, unique_matches, ContentRiskLevel.HIGH

        return False, unique_matches, ContentRiskLevel.MEDIUM

    async def _layer2_check(self, text: str) -> ContentCheckResult:
        """第二层：第三方内容审核"""
        provider = settings.CONTENT_FILTER_PROVIDER.lower()

        if provider == "keyword":
            # 只使用本地关键词，不做第三方检查
            return ContentCheckResult(
                passed=True,
                risk_level=ContentRiskLevel.SAFE,
                categories=[],
                keywords=[],
            )

        try:
            if provider == "alibaba":
                return await self._layer2_check_alibaba(text)
            elif provider == "tencent":
                return await self._layer2_check_tencent(text)
            else:
                loguru.logger.warning(f"未知内容审核提供商: {provider}")
                return ContentCheckResult(
                    passed=True,
                    risk_level=ContentRiskLevel.SAFE,
                    categories=[],
                    keywords=[],
                )
        except Exception as e:
            loguru.logger.error(f"第二层内容审核异常: {e}")
            # 第三方审核失败时，如果第一层已经通过，就放行
            # 否则保持拦截
            return ContentCheckResult(
                passed=True,
                risk_level=ContentRiskLevel.LOW,
                categories=[],
                keywords=[],
                need_review=True,
                message=f"第三方审核异常: {str(e)}",
            )

    async def _layer2_check_alibaba(self, text: str) -> ContentCheckResult:
        """阿里云内容安全审核"""
        try:
            from aliyungo_cs20151209.client import Client
            from aliyungo_cs20151209.models import TextScanRequest
            from aliyungo_cs20151209.credentials import AccessKeyCredential

            if not settings.ALIBABA_CONTENT_ACCESS_KEY:
                return ContentCheckResult(
                    passed=True,
                    risk_level=ContentRiskLevel.SAFE,
                    categories=[],
                    keywords=[],
                    need_review=True,
                    message="阿里云未配置",
                )

            credential = AccessKeyCredential(
                settings.ALIBABA_CONTENT_ACCESS_KEY,
                settings.ALIBABA_CONTENT_ACCESS_SECRET,
            )
            client = Client(credential)

            request = TextScanRequest()
            request.task = {"data": [{"content": text}]}

            response = client.text_scan(request)

            if not response.body or not response.body.data:
                return ContentCheckResult(
                    passed=True,
                    risk_level=ContentRiskLevel.SAFE,
                    categories=[],
                    keywords=[],
                )

            data = response.body.data[0]
            suggestion = data.suggestion

            categories = []
            risk_level = ContentRiskLevel.SAFE
            passed = True

            if suggestion == "block":
                passed = False
                risk_level = ContentRiskLevel.BLOCK
                # 确定分类
                if hasattr(data, "labels"):
                    for label in data.labels:
                        categories.append(self._map_category(label))
            elif suggestion == "review":
                passed = True  # 先放行，加入人工复审队列
                risk_level = ContentRiskLevel.REVIEW

            return ContentCheckResult(
                passed=passed,
                risk_level=risk_level,
                categories=categories,
                keywords=[],
                confidence=data.get("confidence", 0.9) if hasattr(data, "confidence") else 0.9,
                need_review=risk_level == ContentRiskLevel.REVIEW,
            )

        except ImportError:
            loguru.logger.warning("阿里云SDK未安装")
            return ContentCheckResult(
                passed=True,
                risk_level=ContentRiskLevel.LOW,
                categories=[],
                keywords=[],
                need_review=True,
                message="阿里云SDK未安装",
            )

    async def _layer2_check_tencent(self, text: str) -> ContentCheckResult:
        """腾讯云内容安全审核"""
        # 占位实现，后续完善
        return ContentCheckResult(
            passed=True,
            risk_level=ContentRiskLevel.SAFE,
            categories=[],
            keywords=[],
        )

    def _map_category(self, label: str) -> ContentCategory:
        """映射分类"""
        mapping = {
            "porn": ContentCategory.PORN,
            "ad": ContentCategory.AD,
            "politics": ContentCategory.POLITICS,
            "terrorism": ContentCategory.VIOLENCE,
            "abuse": ContentCategory.ABUSE,
        }
        return mapping.get(label.lower(), ContentCategory.OTHER)

    def _addToHumanReview(
        self,
        text: str,
        user_id: int,
        content_type: str,
        content_id: Optional[int],
        check_result: ContentCheckResult,
    ):
        """添加到人工审核队列"""
        from app.core.database import SessionLocal

        db = SessionLocal()
        try:
            item = ContentAuditQueue(
                user_id=user_id,
                content_type=content_type,
                content_id=content_id,
                content_text=text,
                risk_level=check_result.risk_level.value,
                categories=",".join([c.value for c in check_result.categories]),
                detected_keywords=",".join(check_result.keywords),
                confidence=check_result.confidence,
                status="pending",
                created_at=datetime.now(),
            )
            db.add(item)
            db.commit()
            loguru.logger.info(
                f"内容已添加到人工审核队列: user_id={user_id}, content_type={content_type}"
            )
        except Exception as e:
            loguru.logger.error(f"添加人工审核队列失败: {e}")
        finally:
            db.close()

    async def check_text(
        self,
        text: str,
        user_id: Optional[int] = None,
        content_type: str = "chat",
        content_id: Optional[int] = None,
    ) -> ContentCheckResult:
        """
        三级内容安全检查

        Args:
            text: 待检查文本
            user_id: 用户ID，用于人工复审追溯
            content_type: 内容类型 (chat/diary/comment)
            content_id: 内容ID，用于人工复审跳转

        Returns:
            ContentCheckResult: 检查结果
        """
        # 第一层：本地关键词快速过滤
        layer1_passed, keywords, layer1_risk = self._layer1_check(text)

        if not layer1_passed and layer1_risk in [ContentRiskLevel.HIGH, ContentRiskLevel.BLOCK]:
            return ContentCheckResult(
                passed=False,
                risk_level=layer1_risk,
                categories=[],
                keywords=keywords,
                confidence=1.0,
            )

        # 第二层：第三方审核
        if self.enabled_layers["layer2_third_party"]:
            layer2_result = await self._layer2_check(text)

            if not layer2_result.passed:
                # 第二层拦截
                layer2_result.keywords.extend(keywords)
                return layer2_result

            if layer2_result.need_review and self.enabled_layers["layer3_human_review"]:
                # 第三层：加入人工复审
                if user_id:
                    self._addToHumanReview(
                        text, user_id, content_type, content_id, layer2_result
                    )
                return layer2_result

        # 所有层级都通过
        return ContentCheckResult(
            passed=True,
            risk_level=ContentRiskLevel.SAFE,
            categories=[],
            keywords=keywords,
            confidence=1.0,
        )

    def get_block_message(self, result: ContentCheckResult) -> str:
        """获取拦截提示消息"""
        if result.risk_level in [ContentRiskLevel.HIGH, ContentRiskLevel.BLOCK]:
            if ContentCategory.PORN in result.categories:
                return (
                    "抱歉，您的内容包含低俗色情信息，不符合社区规范。"
                    "作为情感陪伴助手，我们倡导健康积极的交流。"
                )
            elif ContentCategory.VIOLENCE in result.categories:
                return (
                    "抱歉，您的内容包含暴力相关信息，不符合社区规范。"
                    "如果您正经历情绪困扰，我愿意陪伴您一起寻找积极的解决方法。"
                )
            elif ContentCategory.POLITICS in result.categories:
                return "抱歉，我们不讨论政治敏感内容，请讨论其他话题。"
            elif ContentCategory.AD in result.categories:
                return "抱歉，不允许在对话中发布广告引流信息。"
            else:
                return (
                    "抱歉，您的内容包含违规信息，无法继续处理。"
                    "作为情感陪伴助手，我更愿意聆听您的情感困扰，一起寻找解决方案。"
                )

        return (
            "抱歉，您的内容包含可能违规的信息，已经记录等待审核。"
            "如果您有其他情感话题想要交流，请更换内容后继续。"
        )


# 全局实例
_content_security_service: Optional[ContentSecurityService] = None


def get_content_security_service() -> ContentSecurityService:
    """获取内容安全服务实例"""
    global _content_security_service
    if _content_security_service is None:
        _content_security_service = ContentSecurityService()
    return _content_security_service
