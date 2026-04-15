"""
大模型工厂 - 创建和管理LLM Provider (支持15+国内厂商)
支持多Provider自动切换的熔断降级机制
"""
import asyncio
from typing import Optional, List, Dict
import loguru

from app.core.config import settings
from app.services.llm.providers import PROVIDER_MAP, LLMProvider

_llm_provider: Optional[LLMProvider] = None

# 默认的Provider降级顺序（国内优先）
DEFAULT_FAILOVER_CHAIN = [
    "volcengine",    # 火山引擎（字节官方）
    "doubao",        # 豆包
    "glm",          # 智谱GLM
    "qwen",         # 阿里通义
    "siliconflow",  # SiliconFlow聚合平台
    "ernie",        # 百度文心
    "hunyuan",      # 腾讯混元
]


def _get_failover_chain() -> List[str]:
    """
    获取降级Provider链
    
    优先级策略：
    1. 首先尝试配置的Provider
    2. 然后按降级链顺序尝试其他Provider
    
    Returns:
        Provider名称列表
    """
    # 如果配置了自定义降级链
    custom_chain = getattr(settings, 'LLM_FAILOVER_CHAIN', None)
    if custom_chain:
        return [p.strip() for p in custom_chain.split(',')]
    
    # 使用默认降级链
    return DEFAULT_FAILOVER_CHAIN


def _create_provider(provider_name: str) -> Optional[LLMProvider]:
    """
    根据Provider名称创建Provider实例
    
    Args:
        provider_name: Provider名称
        
    Returns:
        Provider实例，失败返回None
    """
    if provider_name not in PROVIDER_MAP:
        loguru.logger.warning(f"Unknown provider: {provider_name}")
        return None
    
    provider_class = PROVIDER_MAP[provider_name]
    
    try:
        # 各Provider初始化
        if provider_name == "openai":
            return provider_class(
                api_key=settings.OPENAI_API_KEY or "",
                model=settings.OPENAI_MODEL,
                base_url=settings.OPENAI_BASE_URL,
            )
        elif provider_name == "anthropic":
            return provider_class(
                api_key=settings.ANTHROPIC_API_KEY or "",
                model=settings.ANTHROPIC_MODEL,
                base_url=settings.ANTHROPIC_BASE_URL,
            )
        elif provider_name == "glm":
            return provider_class(
                api_key=settings.GLM_API_KEY or "",
                model=settings.GLM_MODEL,
                base_url=settings.GLM_BASE_URL,
            )
        elif provider_name == "qwen":
            return provider_class(
                api_key=settings.QWEN_API_KEY or "",
                model=settings.QWEN_MODEL,
                base_url=settings.QWEN_BASE_URL,
            )
        elif provider_name == "minimax":
            return provider_class(
                api_key=settings.MINIMAX_API_KEY or "",
                model=settings.MINIMAX_MODEL,
                base_url=settings.MINIMAX_BASE_URL,
            )
        elif provider_name == "ernie":
            return provider_class(
                api_key=settings.ERNIE_API_KEY or "",
                model=settings.ERNIE_MODEL,
                base_url=settings.ERNIE_BASE_URL,
            )
        elif provider_name == "hunyuan":
            return provider_class(
                api_key=settings.HUNYUAN_API_KEY or "",
                model=settings.HUNYUAN_MODEL,
                base_url=settings.HUNYUAN_BASE_URL,
            )
        elif provider_name == "spark":
            return provider_class(
                api_key=settings.SPARK_API_KEY or "",
                model=settings.SPARK_MODEL,
                base_url=settings.SPARK_BASE_URL,
            )
        elif provider_name == "doubao":
            return provider_class(
                api_key=settings.DOUBAO_API_KEY or "",
                model=settings.DOUBAO_MODEL,
                base_url=settings.DOUBAO_BASE_URL,
            )
        elif provider_name == "siliconflow":
            return provider_class(
                api_key=settings.SILICONFLOW_API_KEY or "",
                model=settings.SILICONFLOW_MODEL,
            )
        elif provider_name == "volcengine":
            return provider_class(
                api_key=getattr(settings, 'VOLCENGINE_API_KEY', None) or "",
                model=getattr(settings, 'VOLCENGINE_MODEL', 'doubao-pro-32k'),
                base_url=getattr(settings, 'VOLCENGINE_BASE_URL', 'https://ark.cn-beijing.volces.com/api/v3'),
            )
        elif provider_name == "sensetime":
            return provider_class(
                api_key=getattr(settings, 'SENSETIME_API_KEY', None) or "",
                model=getattr(settings, 'SENSETIME_MODEL', 'sensechat-5'),
            )
        elif provider_name == "baichuan":
            return provider_class(
                api_key=getattr(settings, 'BAICHUAN_API_KEY', None) or "",
                model=getattr(settings, 'BAICHUAN_MODEL', 'baichuan4'),
            )
        elif provider_name == "moonshot":
            return provider_class(
                api_key=getattr(settings, 'MOONSHOT_API_KEY', None) or "",
                model=getattr(settings, 'MOONSHOT_MODEL', 'moonshot-v1-8k'),
            )
        elif provider_name == "lingyi":
            return provider_class(
                api_key=getattr(settings, 'LINGYI_API_KEY', None) or "",
                model=getattr(settings, 'LINGYI_MODEL', 'yi-medium'),
            )
    except Exception as e:
        loguru.logger.error(f"Failed to create provider {provider_name}: {e}")
        return None


def get_llm_provider() -> LLMProvider:
    """获取LLM Provider实例 - 支持15+国内主流厂商"""
    global _llm_provider

    if _llm_provider is None:
        provider_name = settings.LLM_PROVIDER.lower() if settings.LLM_PROVIDER else ""

        if not provider_name:
            raise ValueError(
                "LLM_PROVIDER is not configured. "
                "Please set LLM_PROVIDER environment variable. "
                f"Available providers: {list(PROVIDER_MAP.keys())}"
            )

        if provider_name not in PROVIDER_MAP:
            raise ValueError(f"Unknown LLM provider: {provider_name}. Available providers: {list(PROVIDER_MAP.keys())}")

        _llm_provider = _create_provider(provider_name)
        
        if _llm_provider is None:
            raise RuntimeError(f"Failed to initialize LLM provider: {provider_name}")

        loguru.logger.info(f"LLM Provider initialized: {provider_name}")

    return _llm_provider


def get_llm_provider_with_failover() -> LLMProvider:
    """
    获取LLM Provider实例，支持自动降级
    
    当主Provider失败时，自动尝试降级链中的其他Provider
    
    Returns:
        可用的Provider实例
        
    Raises:
        RuntimeError: 当所有Provider都失败时
    """
    # 首先尝试主Provider
    primary_provider = settings.LLM_PROVIDER.lower() if settings.LLM_PROVIDER else ""
    
    if primary_provider:
        provider = _create_provider(primary_provider)
        if provider:
            loguru.logger.info(f"Using primary LLM Provider: {primary_provider}")
            return provider
    
    # 主Provider失败或未配置，尝试降级链
    failover_chain = _get_failover_chain()
    
    for provider_name in failover_chain:
        # 检查是否已配置了该Provider的API Key
        api_key_attr = f"{provider_name.upper()}_API_KEY"
        api_key = getattr(settings, api_key_attr, None)
        
        if not api_key:
            # 尝试其他命名方式
            if provider_name == "volcengine":
                api_key = getattr(settings, "VOLCENGINE_API_KEY", None)
            elif provider_name == "doubao":
                api_key = getattr(settings, "DOUBAO_API_KEY", None)
            elif provider_name == "glm":
                api_key = getattr(settings, "GLM_API_KEY", None)
            elif provider_name == "qwen":
                api_key = getattr(settings, "QWEN_API_KEY", None)
            elif provider_name == "siliconflow":
                api_key = getattr(settings, "SILICONFLOW_API_KEY", None)
            elif provider_name == "ernie":
                api_key = getattr(settings, "ERNIE_API_KEY", None)
            elif provider_name == "hunyuan":
                api_key = getattr(settings, "HUNYUAN_API_KEY", None)
        
        if api_key:
            provider = _create_provider(provider_name)
            if provider:
                loguru.logger.info(f"LLM Provider failover to: {provider_name}")
                return provider
            else:
                loguru.logger.warning(f"Failed to create provider: {provider_name}, trying next...")
    
    # 所有Provider都失败
    raise RuntimeError(
        f"All LLM providers failed. "
        f"Please check API key configuration. "
        f"Tried: {failover_chain}"
    )


def list_available_providers() -> List[Dict[str, str]]:
    """列出所有可用的LLM Provider信息"""
    providers = []
    for name in PROVIDER_MAP.keys():
        # 获取provider的默认模型信息
        default_models = {
            "openai": "gpt-3.5-turbo",
            "anthropic": "claude-3-haiku",
            "glm": "glm-4",
            "qwen": "qwen-turbo",
            "minimax": "abab5.5-chat",
            "ernie": "ernie-4.0-8k",
            "hunyuan": "hunyuan-pro",
            "spark": "spark-v3.5",
            "doubao": "doubao-pro-32k",
            "siliconflow": "Qwen/Qwen2-72B-Instruct",
            "volcengine": "doubao-pro-32k",
            "sensetime": "sensechat-5",
            "baichuan": "baichuan4",
            "moonshot": "moonshot-v1-8k",
            "lingyi": "yi-medium",
        }
        providers.append({
            "name": name,
            "default_model": default_models.get(name, "unknown"),
            "region": "国内" if name not in ["openai", "anthropic"] else "国外"
        })
    return providers


async def _retry_with_backoff(coro_fn, max_retries: int = 3, base_delay: float = 1.0) -> str:
    last_error = None
    for attempt in range(max_retries):
        try:
            return await coro_fn()
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                loguru.logger.warning(
                    f"LLM call failed (attempt {attempt + 1}/{max_retries}): {e}. "
                    f"Retrying in {delay:.1f}s..."
                )
                await asyncio.sleep(delay)
    raise RuntimeError(f"LLM call failed after {max_retries} attempts: {last_error}")


async def chat(
    messages: list,
    temperature: float = 0.7,
    max_tokens: int = 2000,
    **kwargs
) -> str:
    # 使用支持failover的Provider
    provider = get_llm_provider_with_failover()
    return await _retry_with_backoff(
        lambda: provider.chat(messages, temperature, max_tokens, **kwargs)
    )


async def chat_stream(messages: list, temperature: float = 0.7, max_tokens: int = 2000, **kwargs):
    # 使用支持failover的Provider
    provider = get_llm_provider_with_failover()
    async for chunk in provider.chat_stream(messages, temperature, max_tokens, **kwargs):
        yield chunk