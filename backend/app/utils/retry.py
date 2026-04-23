from __future__ import annotations
import asyncio
import logging
import random
from typing import Any, Callable, Tuple, Type

logger = logging.getLogger(__name__)


async def async_retry(
    fn: Callable,
    *args: Any,
    max_attempts: int = 4,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    jitter: bool = True,
    retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,),
    **kwargs: Any,
) -> Any:
    """
    Async exponential backoff retry with full jitter.
    Retries fn(*args, **kwargs) up to max_attempts times on retryable_exceptions.
    """
    attempt = 0
    while True:
        try:
            return await fn(*args, **kwargs)
        except retryable_exceptions as exc:
            attempt += 1
            if attempt >= max_attempts:
                logger.error("Max retries (%d) exceeded: %s", max_attempts, exc)
                raise
            delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
            if jitter:
                delay *= random.uniform(0.5, 1.0)
            logger.warning(
                "Attempt %d/%d failed (%s). Retrying in %.2fs…",
                attempt, max_attempts, exc, delay,
            )
            await asyncio.sleep(delay)
