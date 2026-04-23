import logging
from langchain_core.tools import tool
from app.core.memory.vector_store import get_vector_store

logger = logging.getLogger(__name__)


@tool
def query_knowledge_base(query: str, k: int = 5) -> str:
    """
    Search the internal knowledge base (vector store) for documents related to the query.
    Use this when you need to retrieve information from documents uploaded by the user.
    Input: a natural language query string.
    Returns: the top matching document excerpts with their source filenames.
    """
    try:
        store = get_vector_store()
        if store is None:
            return "Knowledge base is empty. Please upload documents via the Data Vault first."
        docs = store.similarity_search(query, k=k)
        if not docs:
            return "No relevant documents found in the knowledge base."
        results = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "unknown")
            results.append(f"[{i}] Source: {source}\n{doc.page_content}")
        return "\n\n---\n\n".join(results)
    except Exception as e:
        logger.error("query_knowledge_base failed: %s", e)
        return f"Knowledge base query failed: {e}"


VECTOR_TOOLS = [query_knowledge_base]
TOOL_IDS = ["query_knowledge_base"]
