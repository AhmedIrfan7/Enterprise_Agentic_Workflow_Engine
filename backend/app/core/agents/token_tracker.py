from __future__ import annotations
import logging
from typing import Any, List
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult
from app.core.agents.llm_factory import estimate_cost

logger = logging.getLogger(__name__)


class TokenUsageTracker(BaseCallbackHandler):
    """Accumulates token counts and estimates USD cost across the full agent run."""

    def __init__(self, model: str) -> None:
        super().__init__()
        self.model = model
        self.prompt_tokens: int = 0
        self.completion_tokens: int = 0
        self.total_tokens: int = 0
        self.llm_calls: int = 0

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        for generations in response.generations:
            for gen in generations:
                usage = getattr(gen, "generation_info", {}) or {}
                pt = usage.get("prompt_tokens", 0)
                ct = usage.get("completion_tokens", 0)
                self.prompt_tokens += pt
                self.completion_tokens += ct
                self.total_tokens += pt + ct
                self.llm_calls += 1

        # Also check response.llm_output for aggregated usage
        if response.llm_output and "token_usage" in response.llm_output:
            tu = response.llm_output["token_usage"]
            self.prompt_tokens = max(self.prompt_tokens, tu.get("prompt_tokens", 0))
            self.completion_tokens = max(self.completion_tokens, tu.get("completion_tokens", 0))
            self.total_tokens = max(self.total_tokens, tu.get("total_tokens", 0))

    @property
    def estimated_cost_usd(self) -> float:
        return estimate_cost(self.model, self.prompt_tokens, self.completion_tokens)

    def summary(self) -> dict[str, Any]:
        return {
            "model": self.model,
            "llm_calls": self.llm_calls,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "estimated_cost_usd": round(self.estimated_cost_usd, 6),
        }
