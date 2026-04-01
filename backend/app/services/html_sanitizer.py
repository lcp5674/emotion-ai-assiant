"""
HTML安全过滤 - XSS防护
"""
import re
from typing import Optional
import loguru

from app.core.config import settings


ALLOWED_TAGS = frozenset({
    "p", "br", "h1", "h2", "h3", "h4", "h5", "h6",
    "strong", "b", "em", "i", "u", "s", "del",
    "ul", "ol", "li", "dl", "dt", "dd",
    "a", "img", "blockquote", "pre", "code", "span", "div",
    "table", "thead", "tbody", "tr", "th", "td",
    "hr", "figure", "figcaption",
})

ALLOWED_ATTRIBUTES = {
    "a": {"href", "title", "target"},
    "img": {"src", "alt", "title", "width", "height"},
    "*": {"class"},
}


class HtmlSanitizer:
    """HTML安全过滤器"""

    def __init__(self):
        self.allowed_tags = set(settings.HTML_SANITIZER_ALLOWED_TAGS)
        self.allowed_attrs = settings.HTML_SANITIZER_ALLOWED_ATTRIBUTES

    def sanitize(self, html: str) -> str:
        if not html:
            return ""

        try:
            import bleach
            cleaned = bleach.clean(
                html,
                tags=self.allowed_tags,
                attributes=self.allowed_attrs,
                strip=True,
                strip_comments=True,
            )
            return cleaned
        except ImportError:
            loguru.logger.warning("bleach未安装，使用基础正则过滤")
            return self._basic_sanitize(html)

    def _basic_sanitize(self, html: str) -> str:
        """基础正则过滤（bleach未安装时的降级方案）"""
        dangerous_tags = [
            r'<script[^>]*>.*?</script>',
            r'<iframe[^>]*>.*?</iframe>',
            r'<object[^>]*>.*?</object>',
            r'<embed[^>]*>',
            r'<form[^>]*>.*?</form>',
            r'<input[^>]*>',
            r'<button[^>]*>.*?</button>',
            r'javascript:',
            r'on\w+\s*=',
        ]

        result = html
        for pattern in dangerous_tags:
            result = re.sub(pattern, "", result, flags=re.IGNORECASE | re.DOTALL)

        result = re.sub(
            r'<a([^>]+)href\s*=\s*["\']?([^"\'>\s]+)["\']?',
            self._safe_link,
            result,
            flags=re.IGNORECASE
        )

        return result

    def _safe_link(self, match: re.Match) -> str:
        """处理a标签，确保是安全链接"""
        attrs = match.group(1)
        href = match.group(2)

        safe_protocols = ("http://", "https://", "mailto:")
        if any(href.lower().startswith(p) for p in safe_protocols):
            target = '_blank' if 'target' not in attrs else ''
            return f'<a href="{href}"{target} rel="noopener noreferrer">'
        return ''


_html_sanitizer: Optional[HtmlSanitizer] = None


def get_html_sanitizer() -> HtmlSanitizer:
    """获取HTML过滤器实例"""
    global _html_sanitizer
    if _html_sanitizer is None:
        _html_sanitizer = HtmlSanitizer()
    return _html_sanitizer
