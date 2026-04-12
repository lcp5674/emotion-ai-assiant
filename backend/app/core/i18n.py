"""
国际化支持
"""
import gettext
import os
from typing import Optional

from app.core.config import settings

# 支持的语言
SUPPORTED_LANGUAGES = ['zh_CN', 'en_US']

# 翻译目录
LOCALE_DIR = os.path.join(os.path.dirname(__file__), '../locale')

# 确保翻译目录存在
os.makedirs(LOCALE_DIR, exist_ok=True)

# 翻译对象缓存
translations = {}


def get_translation(language: str = 'zh_CN') -> gettext.GNUTranslations:
    """
    获取指定语言的翻译对象
    """
    if language not in translations:
        try:
            # 尝试加载指定语言的翻译
            translations[language] = gettext.translation(
                'messages',
                localedir=LOCALE_DIR,
                languages=[language],
                fallback=True
            )
        except Exception:
            # 如果加载失败，使用默认语言
            translations[language] = gettext.NullTranslations()
    return translations[language]


def _(message: str, language: str = 'zh_CN') -> str:
    """
    翻译函数
    """
    translation = get_translation(language)
    return translation.gettext(message)


def get_supported_languages() -> list:
    """
    获取支持的语言列表
    """
    return SUPPORTED_LANGUAGES
