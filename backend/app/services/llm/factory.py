"""
大模型工厂 - 创建和管理LLM Provider
"""
import asyncio
from typing import Optional
import loguru

from app.core.config import settings
from app.services.llm.providers import PROVIDER_MAP, LLMProvider

_llm_provider: Optional[LLMProvider] = None


def get_llm_provider() -> LLMProvider:
    global _llm_provider

    if _llm_provider is None:
        provider_name = settings.LLM_PROVIDER.lower()

        if provider_name not in PROVIDER_MAP:
            raise ValueError(f"Unknown LLM provider: {provider_name}. Available providers: {list(PROVIDER_MAP.keys())}")

        provider_class = PROVIDER_MAP[provider_name]

        if provider_name == "openai":
            _llm_provider = provider_class(
                api_key=settings.OPENAI_API_KEY or "",
                model=settings.OPENAI_MODEL,
                base_url=settings.OPENAI_BASE_URL,
            )
        elif provider_name == "anthropic":
            _llm_provider = provider_class(
                api_key=settings.ANTHROPIC_API_KEY or "",
                model=settings.ANTHROPIC_MODEL,
                base_url=settings.ANTHROPIC_BASE_URL,
            )
        elif provider_name == "glm":
            _llm_provider = provider_class(
                api_key=settings.GLM_API_KEY or "",
                model=settings.GLM_MODEL,
                base_url=settings.GLM_BASE_URL,
            )
        elif provider_name == "qwen":
            _llm_provider = provider_class(
                api_key=settings.QWEN_API_KEY or "",
                model=settings.QWEN_MODEL,
                base_url=settings.QWEN_BASE_URL,
            )
        elif provider_name == "minimax":
            _llm_provider = provider_class(
                api_key=settings.MINIMAX_API_KEY or "",
                model=settings.MINIMAX_MODEL,
                base_url=settings.MINIMAX_BASE_URL,
            )
        elif provider_name == "ernie":
            _llm_provider = provider_class(
                api_key=settings.ERNIE_API_KEY or "",
                model=settings.ERNIE_MODEL,
                base_url=settings.ERNIE_BASE_URL,
            )
        elif provider_name == "hunyuan":
            _llm_provider = provider_class(
                api_key=settings.HUNYUAN_API_KEY or "",
                model=settings.HUNYUAN_MODEL,
                base_url=settings.HUNYUAN_BASE_URL,
            )
        elif provider_name == "spark":
            _llm_provider = provider_class(
                api_key=settings.SPARK_API_KEY or "",
                model=settings.SPARK_MODEL,
                base_url=settings.SPARK_BASE_URL,
            )
        elif provider_name == "doubao":
            _llm_provider = provider_class(
                api_key=settings.DOUBAO_API_KEY or "",
                model=settings.DOUBAO_MODEL,
                base_url=settings.DOUBAO_BASE_URL,
            )
        elif provider_name == "siliconflow":
            _llm_provider = provider_class(
                api_key=settings.SILICONFLOW_API_KEY or "",
                model=settings.SILICONFLOW_MODEL,
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider_name}")

        loguru.logger.info(f"LLM Provider initialized: {provider_name}")

    return _llm_provider


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
    provider = get_llm_provider()
    return await _retry_with_backoff(
        lambda: provider.chat(messages, temperature, max_tokens, **kwargs)
    )


async def chat_stream(messages: list, temperature: float = 0.7, max_tokens: int = 2000, **kwargs):
    provider = get_llm_provider()
    async for chunk in provider.chat_stream(messages, temperature, max_tokens, **kwargs):
        yield chunk
