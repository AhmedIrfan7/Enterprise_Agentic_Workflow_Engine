import logging
from typing import Optional
import httpx
from bs4 import BeautifulSoup
from langchain_core.tools import tool
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)


@tool
def web_search(query: str, max_results: int = 5) -> str:
    """
    Search the web using DuckDuckGo and return a formatted list of results.
    Use this to find current information, news, or research topics.
    Input should be a clear, specific search query string.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        if not results:
            return "No results found for the given query."
        formatted = []
        for i, r in enumerate(results, 1):
            formatted.append(f"[{i}] {r.get('title', 'N/A')}\nURL: {r.get('href', 'N/A')}\n{r.get('body', '')}")
        return "\n\n".join(formatted)
    except Exception as e:
        logger.error("web_search failed: %s", e)
        return f"Search failed: {e}"


@tool
def scrape_webpage(url: str) -> str:
    """
    Fetch and extract the main text content from a webpage URL.
    Use this to read the full content of a specific web page after identifying its URL via web_search.
    Returns cleaned plain text (up to 8000 characters).
    """
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
            )
        }
        with httpx.Client(timeout=15, follow_redirects=True, headers=headers) as client:
            resp = client.get(url)
            resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        text = " ".join(soup.get_text(separator=" ").split())
        return text[:8000] if len(text) > 8000 else text
    except Exception as e:
        logger.error("scrape_webpage failed for %s: %s", url, e)
        return f"Failed to scrape {url}: {e}"


WEB_TOOLS = [web_search, scrape_webpage]
TOOL_IDS = ["web_search", "scrape_webpage"]
