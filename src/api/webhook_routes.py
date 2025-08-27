"""Rotas de webhook para recebimento de mensagens do WhatsApp."""

from fastapi import APIRouter, Request

from src.core.message_buffer import buffer_message

# Cria router para webhooks
webhook_router = APIRouter(tags=["Webhook"])


@webhook_router.post('/webhook')
async def webhook(request: Request):
    """
    Endpoint para receber mensagens do WhatsApp via Evolution API.
    
    Args:
        request: Requisição HTTP com dados da mensagem
        
    Returns:
        Dict com status de processamento
    """
    try:
        data = await request.json()
        
        # Extrai informações da mensagem
        chat_id = data.get('data', {}).get('key', {}).get('remoteJid')
        message = data.get('data', {}).get('message', {}).get('conversation')
        
        # Processa apenas mensagens privadas (não grupos)
        if chat_id and message and '@g.us' not in chat_id:
            await buffer_message(
                chat_id=chat_id,
                message=message,
            )
        
        return {'status': 'ok'}
    
    except Exception as e:
        print(f"Erro no processamento do webhook: {e}")
        return {'status': 'error', 'message': str(e)}