"""
大模型工厂 - 创建和管理LLM Provider (支持15+国内厂商)
支持多Provider自动切换的熔断降级机制
"""
import asyncio
from typing import Optional, List, Dict
import loguru

from app.services.llm.providers import PROVIDER_MAP, LLMProvider

_llm_provider: Optional[LLMProvider] = None


def _get_llm_config_from_db() -> Dict[str, Optional[str]]:
    """
    从数据库获取LLM配置

    Returns:
        包含所有LLM配置的字典
    """
    try:
        from app.core.database import SessionLocal
        from app.models import SystemConfig

        db = SessionLocal()
        try:
            configs = db.query(SystemConfig).filter(
                SystemConfig.config_key.like("LLM_%")
            ).all() + db.query(SystemConfig).filter(
                SystemConfig.config_key.in_([
                    "OPENAI_API_KEY", "OPENAI_MODEL", "OPENAI_BASE_URL",
                    "ANTHROPIC_API_KEY", "ANTHROPIC_MODEL", "ANTHROPIC_BASE_URL",
                    "GLM_API_KEY", "GLM_MODEL", "GLM_BASE_URL",
                    "QWEN_API_KEY", "QWEN_MODEL", "QWEN_BASE_URL",
                    "MINIMAX_API_KEY", "MINIMAX_MODEL", "MINIMAX_BASE_URL",
                    "ERNIE_API_KEY", "ERNIE_MODEL", "ERNIE_BASE_URL",
                    "HUNYUAN_API_KEY", "HUNYUAN_MODEL", "HUNYUAN_BASE_URL",
                    "SPARK_API_KEY", "SPARK_MODEL", "SPARK_BASE_URL",
                    "DOUBAO_API_KEY", "DOUBAO_MODEL", "DOUBAO_BASE_URL",
                    "SILICONFLOW_API_KEY", "SILICONFLOW_MODEL", "SILICONFLOW_BASE_URL",
                    "VOLCENGINE_API_KEY", "VOLCENGINE_MODEL", "VOLCENGINE_BASE_URL",
                    "SENSETIME_API_KEY", "SENSETIME_MODEL",
                    "BAICHUAN_API_KEY", "BAICHUAN_MODEL",
                    "MOONSHOT_API_KEY", "MOONSHOT_MODEL",
                    "LINGYI_API_KEY", "LINGYI_MODEL",
                ])
            ).all()

            config_dict = {}
            for c in configs:
                config_dict[c.config_key] = c.config_value
            return config_dict
        finally:
            db.close()
    except Exception as e:
        loguru.logger.warning(f"从数据库获取LLM配置失败: {e}")
        return {}


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

    # 从数据库获取最新配置
    configs = _get_llm_config_from_db()

    try:
        # 各Provider初始化 - 直接从数据库读取配置
        if provider_name == "openai":
            return provider_class(
                api_key=configs.get("OPENAI_API_KEY") or "",
                model=configs.get("OPENAI_MODEL") or "gpt-3.5-turbo",
                base_url=configs.get("OPENAI_BASE_URL") or "https://api.openai.com/v1",
            )
        elif provider_name == "anthropic":
            return provider_class(
                api_key=configs.get("ANTHROPIC_API_KEY") or "",
                model=configs.get("ANTHROPIC_MODEL") or "claude-3-haiku",
                base_url=configs.get("ANTHROPIC_BASE_URL") or "",
            )
        elif provider_name == "glm":
            return provider_class(
                api_key=configs.get("GLM_API_KEY") or "",
                model=configs.get("GLM_MODEL") or "glm-4",
                base_url=configs.get("GLM_BASE_URL") or "",
            )
        elif provider_name == "qwen":
            return provider_class(
                api_key=configs.get("QWEN_API_KEY") or "",
                model=configs.get("QWEN_MODEL") or "qwen-turbo",
                base_url=configs.get("QWEN_BASE_URL") or "",
            )
        elif provider_name == "minimax":
            return provider_class(
                api_key=configs.get("MINIMAX_API_KEY") or "",
                model=configs.get("MINIMAX_MODEL") or "abab5.5-chat",
                base_url=configs.get("MINIMAX_BASE_URL") or "",
            )
        elif provider_name == "ernie":
            return provider_class(
                api_key=configs.get("ERNIE_API_KEY") or "",
                model=configs.get("ERNIE_MODEL") or "ernie-4.0-8k",
                base_url=configs.get("ERNIE_BASE_URL") or "",
            )
        elif provider_name == "hunyuan":
            return provider_class(
                api_key=configs.get("HUNYUAN_API_KEY") or "",
                model=configs.get("HUNYUAN_MODEL") or "hunyuan-pro",
                base_url=configs.get("HUNYUAN_BASE_URL") or "",
            )
        elif provider_name == "spark":
            return provider_class(
                api_key=configs.get("SPARK_API_KEY") or "",
                model=configs.get("SPARK_MODEL") or "spark-v3.5",
                base_url=configs.get("SPARK_BASE_URL") or "",
            )
        elif provider_name == "doubao":
            return provider_class(
                api_key=configs.get("DOUBAO_API_KEY") or "",
                model=configs.get("DOUBAO_MODEL") or "doubao-pro-32k",
                base_url=configs.get("DOUBAO_BASE_URL") or "https://ark.cn-beijing.volces.com/api/v3",
            )
        elif provider_name == "siliconflow":
            return provider_class(
                api_key=configs.get("SILICONFLOW_API_KEY") or "",
                model=configs.get("SILICONFLOW_MODEL") or "Qwen/Qwen2-72B-Instruct",
            )
        elif provider_name == "volcengine":
            return provider_class(
                api_key=configs.get("VOLCENGINE_API_KEY") or "",
                model=configs.get("VOLCENGINE_MODEL") or "doubao-pro-32k",
                base_url=configs.get("VOLCENGINE_BASE_URL") or "https://ark.cn-beijing.volces.com/api/v3",
            )
        elif provider_name == "sensetime":
            return provider_class(
                api_key=configs.get("SENSETIME_API_KEY") or "",
                model=configs.get("SENSETIME_MODEL") or "sensechat-5",
            )
        elif provider_name == "baichuan":
            return provider_class(
                api_key=configs.get("BAICHUAN_API_KEY") or "",
                model=configs.get("BAICHUAN_MODEL") or "baichuan4",
            )
        elif provider_name == "moonshot":
            return provider_class(
                api_key=configs.get("MOONSHOT_API_KEY") or "",
                model=configs.get("MOONSHOT_MODEL") or "moonshot-v1-8k",
            )
        elif provider_name == "lingyi":
            return provider_class(
                api_key=configs.get("LINGYI_API_KEY") or "",
                model=configs.get("LINGYI_MODEL") or "yi-medium",
            )
    except Exception as e:
        loguru.logger.error(f"Failed to create provider {provider_name}: {e}")
        return None


def _get_primary_provider_name() -> str:
    """获取主Provider名称，从数据库读取"""
    try:
        from app.core.database import SessionLocal
        from app.models import SystemConfig

        db = SessionLocal()
        try:
            config = db.query(SystemConfig).filter(
                SystemConfig.config_key == "LLM_PROVIDER"
            ).first()
            if config and config.config_value:
                return config.config_value.lower()
        finally:
            db.close()
    except Exception as e:
        loguru.logger.warning(f"获取LLM_PROVIDER失败: {e}")

    return ""


def _get_failover_chain() -> List[str]:
    """获取降级Provider链，从数据库读取"""
    try:
        from app.core.database import SessionLocal
        from app.models import SystemConfig

        db = SessionLocal()
        try:
            config = db.query(SystemConfig).filter(
                SystemConfig.config_key == "LLM_FAILOVER_CHAIN"
            ).first()
            if config and config.config_value:
                return [p.strip() for p in config.config_value.split(",") if p.strip()]
        finally:
            db.close()
    except Exception as e:
        loguru.logger.warning(f"获取LLM_FAILOVER_CHAIN失败: {e}")

    # 默认的Provider降级顺序（国内优先）
    return [
        "volcengine",
        "doubao",
        "glm",
        "qwen",
        "siliconflow",
        "ernie",
        "hunyuan",
    ]


def get_llm_provider() -> LLMProvider:
    """获取LLM Provider实例 - 支持15+国内主流厂商"""
    global _llm_provider

    if _llm_provider is None:
        provider_name = _get_primary_provider_name()

        if not provider_name:
            raise ValueError(
                "LLM_PROVIDER is not configured. "
                "Please set LLM_PROVIDER in database. "
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
    primary_provider = _get_primary_provider_name()

    if primary_provider:
        provider = _create_provider(primary_provider)
        if provider:
            loguru.logger.info(f"Using primary LLM Provider: {primary_provider}")
            return provider

    # 主Provider失败或未配置，尝试降级链
    failover_chain = _get_failover_chain()

    for provider_name in failover_chain:
        # 检查是否已配置了该Provider的API Key
        configs = _get_llm_config_from_db()
        api_key_attr = f"{provider_name.upper()}_API_KEY"
        api_key = configs.get(api_key_attr)

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
