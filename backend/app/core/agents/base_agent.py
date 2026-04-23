from __future__ import annotations
import logging
from typing import Any, Callable, List, Optional

from langchain_classic.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.tools import BaseTool
from langchain_core.language_models import BaseChatModel
from langchain_core.callbacks import BaseCallbackHandler

from app.config import get_settings
from app.core.agents.llm_factory import build_llm
from app.core.memory.conversation_memory import build_memory
from app.core.agents.prompt_templates import build_agent_prompt

logger = logging.getLogger(__name__)
settings = get_settings()


class EnterpriseAgent:
    """
    Wraps LangChain AgentExecutor with provider-agnostic LLM, persistent memory,
    dynamic tool selection, and structured callback support.
    """

    def __init__(
        self,
        workflow_id: str,
        tools: List[BaseTool],
        llm_provider: str = "openai",
        llm_model: str = "gpt-4o-mini",
        callbacks: Optional[List[BaseCallbackHandler]] = None,
    ) -> None:
        self.workflow_id = workflow_id
        self.tools = tools
        self.callbacks = callbacks or []

        self.llm: BaseChatModel = build_llm(
            provider=llm_provider,
            model=llm_model,
            callbacks=self.callbacks,
        )
        self.memory = build_memory(session_id=workflow_id)
        self.prompt = build_agent_prompt(provider=llm_provider)
        self._executor: Optional[AgentExecutor] = None

    def _build_executor(self) -> AgentExecutor:
        agent = create_openai_tools_agent(self.llm, self.tools, self.prompt)
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=settings.DEBUG,
            max_iterations=15,
            max_execution_time=300,
            handle_parsing_errors=True,
            return_intermediate_steps=True,
        )

    async def arun(self, goal: str) -> dict[str, Any]:
        if self._executor is None:
            self._executor = self._build_executor()
        logger.info("Agent starting for workflow %s: %s", self.workflow_id, goal[:80])
        result = await self._executor.ainvoke(
            {"input": goal},
            config={"callbacks": self.callbacks},
        )
        return result
