from typing import List, Optional
from langchain_core.language_models import BaseChatModel
from langchain_core.callbacks import BaseCallbackHandler
from app.config import get_settings

settings = get_settings()

# Pricing per 1K tokens (input, output) — USD, approximate
_OPENAI_PRICING: dict[str, tuple[float, float]] = {
    "gpt-4o":       (0.005, 0.015),
    "gpt-4o-mini":  (0.00015, 0.0006),
    "gpt-4-turbo":  (0.010, 0.030),
    "gpt-3.5-turbo": (0.0005, 0.0015),
}


def build_llm(
    provider: str,
    model: str,
    callbacks: Optional[List[BaseCallbackHandler]] = None,
) -> BaseChatModel:
    callbacks = callbacks or []
    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model,
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS,
            api_key=settings.OPENAI_API_KEY,
            callbacks=callbacks,
            streaming=True,
        )
    if provider == "ollama":
        from langchain_community.chat_models import ChatOllama
        return ChatOllama(
            model=settings.OLLAMA_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
            temperature=settings.LLM_TEMPERATURE,
            callbacks=callbacks,
        )
    raise ValueError(f"Unknown LLM provider: {provider!r}")


def estimate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    if model not in _OPENAI_PRICING:
        return 0.0
    input_price, output_price = _OPENAI_PRICING[model]
    return (prompt_tokens / 1000) * input_price + (completion_tokens / 1000) * output_price
