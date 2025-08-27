"""Gerenciamento de memória e histórico de conversas."""

import redis
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import RedisChatMessageHistory

from .config import settings


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """
    Obtém histórico de chat para uma sessão específica.
    
    Args:
        session_id: ID único da sessão
        
    Returns:
        BaseChatMessageHistory: Histórico da sessão
    """
    return RedisChatMessageHistory(session_id, url=settings.REDIS_URL)