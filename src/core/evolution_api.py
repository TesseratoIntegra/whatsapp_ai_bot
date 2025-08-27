"""Integração com Evolution API para WhatsApp."""

import aiohttp

from .config import settings


async def send_message(chat_id: str, message: str) -> bool:
    """
    Envia mensagem via Evolution API.
    
    Args:
        chat_id: ID único do chat do WhatsApp
        message: Mensagem a ser enviada
        
    Returns:
        bool: True se enviada com sucesso
    """
    url = f"{settings.EVOLUTION_API_URL}/message/sendText/{settings.EVOLUTION_INSTANCE_NAME}"
    
    headers = {
        'Content-Type': 'application/json',
        'apikey': settings.EVOLUTION_AUTHENTICATION_API_KEY
    }
    
    payload = {
        'number': chat_id,
        'text': message
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                return response.status == 200
    except Exception as e:
        print(f"Erro ao enviar mensagem via Evolution API: {e}")
        return False
