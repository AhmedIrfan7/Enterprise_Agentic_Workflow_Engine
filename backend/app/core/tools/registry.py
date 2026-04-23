from typing import List
from langchain_core.tools import BaseTool
from app.core.tools.web_tools import WEB_TOOLS
from app.core.tools.file_tools import FILE_TOOLS
from app.core.tools.vector_tool import VECTOR_TOOLS

_ALL_TOOLS: dict[str, BaseTool] = {t.name: t for t in WEB_TOOLS + FILE_TOOLS + VECTOR_TOOLS}


def get_tools(tool_ids: List[str]) -> List[BaseTool]:
    """Return requested tools; fall back to full set if no IDs specified."""
    if not tool_ids:
        return list(_ALL_TOOLS.values())
    selected = [_ALL_TOOLS[tid] for tid in tool_ids if tid in _ALL_TOOLS]
    return selected if selected else list(_ALL_TOOLS.values())


def list_available_tools() -> List[dict]:
    return [
        {"id": name, "description": t.description[:120]}
        for name, t in _ALL_TOOLS.items()
    ]
