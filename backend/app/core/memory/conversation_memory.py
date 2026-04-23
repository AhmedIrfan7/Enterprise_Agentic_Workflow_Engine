from langchain.memory import ConversationBufferWindowMemory
from langchain_community.chat_message_histories import SQLChatMessageHistory
from app.config import get_settings

settings = get_settings()

# Sync SQLite URL for SQLChatMessageHistory (uses plain sqlite3, not aiosqlite)
_SYNC_DB_URL = settings.DATABASE_URL.replace("sqlite+aiosqlite", "sqlite")


def build_memory(session_id: str, window_k: int = 10) -> ConversationBufferWindowMemory:
    """
    Persistent conversational memory backed by SQLite.
    Uses a sliding window of k=10 exchanges to keep context bounded.
    """
    history = SQLChatMessageHistory(
        session_id=session_id,
        connection_string=_SYNC_DB_URL,
    )
    return ConversationBufferWindowMemory(
        chat_memory=history,
        k=window_k,
        memory_key="chat_history",
        return_messages=True,
        output_key="output",
    )
