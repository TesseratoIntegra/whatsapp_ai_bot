"""Sistema de buffer de mensagens com debounce."""

import asyncio
import redis.asyncio as redis
from typing import Dict

from .config import settings
from .chains import get_conversational_rag_chain
from .evolution_api import send_message


# Cache Redis para buffer de mensagens
redis_client = redis.from_url(settings.REDIS_URL)

# Dicionário para controlar timers de debounce
debounce_timers: Dict[str, asyncio.Task] = {}


async def buffer_message(chat_id: str, message: str) -> None:
    """
    Adiciona mensagem ao buffer com sistema de debounce.
    
    Args:
        chat_id: ID único do chat
        message: Mensagem recebida
    """
    buffer_key = f"{chat_id}{settings.BUFFER_KEY_SUFFIX}"
    
    # Adiciona mensagem ao buffer
    await redis_client.lpush(buffer_key, message)
    await redis_client.expire(buffer_key, settings.BUFFER_TTL)
    
    # Cancela timer anterior se existir
    if chat_id in debounce_timers:
        debounce_timers[chat_id].cancel()
    
    # Cria novo timer de debounce
    debounce_timers[chat_id] = asyncio.create_task(
        _process_after_debounce(chat_id)
    )


async def _process_after_debounce(chat_id: str) -> None:
    """
    Processa mensagens após período de debounce.
    
    Args:
        chat_id: ID único do chat
    """
    # Aguarda período de debounce
    await asyncio.sleep(settings.DEBOUNCE_SECONDS)
    
    buffer_key = f"{chat_id}{settings.BUFFER_KEY_SUFFIX}"
    
    # Recupera todas as mensagens do buffer
    messages = await redis_client.lrange(buffer_key, 0, -1)
    await redis_client.delete(buffer_key)
    
    if messages:
        # Combina mensagens (ordem reversa pois Redis lista é LIFO)
        combined_message = ' '.join(msg.decode() for msg in reversed(messages))
        
        # Processa com chain RAG
        await _process_with_rag(chat_id, combined_message)
    
    # Remove timer do dicionário
    if chat_id in debounce_timers:
        del debounce_timers[chat_id]


async def _process_with_rag(chat_id: str, message: str) -> None:
    """
    Processa mensagem com chain RAG e envia resposta.
    
    Args:
        chat_id: ID único do chat
        message: Mensagem combinada para processar
    """
    try:
        # Obtém chain conversacional
        chain = get_conversational_rag_chain()
        
        # Processa mensagem
        response = await chain.ainvoke(
            {'input': message},
            config={'configurable': {'session_id': chat_id}}
        )
        
        # Envia resposta
        await send_message(chat_id, response['answer'])
        
    except Exception as e:
        print(f"Erro ao processar mensagem: {e}")
        # Envia mensagem de erro genérica
        await send_message(
            chat_id, 
            "Desculpe, ocorreu um erro ao processar sua mensagem."
        )