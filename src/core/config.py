"""Configurações globais do sistema."""

import os
from typing import Optional

from dotenv import load_dotenv


# Carrega variáveis de ambiente do arquivo .env
load_dotenv()


class Settings:
    """Configurações centralizadas do sistema."""
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')
    OPENAI_MODEL_NAME: str = os.getenv('OPENAI_MODEL_NAME', 'gpt-4o-mini')
    OPENAI_MODEL_TEMPERATURE: float = float(os.getenv('OPENAI_MODEL_TEMPERATURE', '0'))
    
    # Prompts do sistema
    AI_CONTEXTUALIZE_PROMPT: str = os.getenv(
        'AI_CONTEXTUALIZE_PROMPT',
        'Dado um histórico de conversa e a pergunta mais recente do usuário, '
        'que pode fazer referência ao contexto anterior, formule uma pergunta '
        'independente, que possa ser compreendida sem o histórico da conversa. '
        'NÃO responda à pergunta — apenas reformule se necessário; caso contrário, '
        'retorne a pergunta como está.'
    )
    AI_SYSTEM_PROMPT: str = os.getenv(
        'AI_SYSTEM_PROMPT',
        'Você é um assistente virtual que irá responder dúvidas dos clientes. '
        'Use os seguintes trechos de contexto recuperado para responder à pergunta. '
        'Se você não souber a resposta, diga que não sabe. '
        'Use no máximo três frases e mantenha a resposta concisa. {context}'
    )
    
    # Evolution API Configuration
    EVOLUTION_API_URL: str = os.getenv('EVOLUTION_API_URL', 'http://evolution-api:8080')
    EVOLUTION_INSTANCE_NAME: str = os.getenv('EVOLUTION_INSTANCE_NAME', '')
    EVOLUTION_AUTHENTICATION_API_KEY: str = os.getenv('AUTHENTICATION_API_KEY', '')
    
    # Redis Configuration
    REDIS_URL: str = os.getenv('CACHE_REDIS_URI', 'redis://redis:6379/6')
    BUFFER_KEY_SUFFIX: str = os.getenv('BUFFER_KEY_SUFIX', '_msg_buffer')
    DEBOUNCE_SECONDS: int = int(os.getenv('DEBOUNCE_SECONDS', '10'))
    BUFFER_TTL: int = int(os.getenv('BUFFER_TTL', '300'))
    
    # Vector Store Configuration (Legacy ChromaDB)
    VECTOR_STORE_PATH: str = os.getenv('VECTOR_STORE_PATH', 'vectorstore')
    RAG_FILES_DIR: str = os.getenv('RAG_FILES_DIR', 'rag_files')
    
    # Database Configuration
    DATABASE_HOST: str = os.getenv('DATABASE_HOST', 'localhost')
    DATABASE_PORT: str = os.getenv('DATABASE_PORT', '5432')
    DATABASE_NAME: str = os.getenv('DATABASE_NAME', 'whatsapp_bot')
    DATABASE_USER: str = os.getenv('DATABASE_USER', 'postgres')
    DATABASE_PASSWORD: str = os.getenv('DATABASE_PASSWORD', '')
    
    @property
    def database_url(self) -> str:
        """URL de conexão com PostgreSQL."""
        return (
            f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )
    
    @property
    def async_database_url(self) -> str:
        """URL de conexão assíncrona com PostgreSQL."""
        return (
            f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )
    
    def validate_required_settings(self) -> None:
        """Valida se todas as configurações obrigatórias estão presentes."""
        required_settings = [
            ('OPENAI_API_KEY', self.OPENAI_API_KEY),
            ('DATABASE_PASSWORD', self.DATABASE_PASSWORD),
        ]
        
        missing_settings = [
            name for name, value in required_settings if not value
        ]
        
        if missing_settings:
            raise ValueError(
                f"Configurações obrigatórias não encontradas: {', '.join(missing_settings)}"
            )


# Instância global das configurações
settings = Settings()

# Manter compatibilidade com imports antigos
OPENAI_API_KEY = settings.OPENAI_API_KEY
OPENAI_MODEL_NAME = settings.OPENAI_MODEL_NAME
OPENAI_MODEL_TEMPERATURE = settings.OPENAI_MODEL_TEMPERATURE
AI_CONTEXTUALIZE_PROMPT = settings.AI_CONTEXTUALIZE_PROMPT
AI_SYSTEM_PROMPT = settings.AI_SYSTEM_PROMPT
EVOLUTION_API_URL = settings.EVOLUTION_API_URL
EVOLUTION_INSTANCE_NAME = settings.EVOLUTION_INSTANCE_NAME
EVOLUTION_AUTHENTICATION_API_KEY = settings.EVOLUTION_AUTHENTICATION_API_KEY
REDIS_URL = settings.REDIS_URL
VECTOR_STORE_PATH = settings.VECTOR_STORE_PATH
RAG_FILES_DIR = settings.RAG_FILES_DIR
BUFFER_KEY_SUFIX = settings.BUFFER_KEY_SUFFIX
DEBOUNCE_SECONDS = settings.DEBOUNCE_SECONDS
BUFFER_TTL = settings.BUFFER_TTL
DATABASE_URL = settings.database_url
ASYNC_DATABASE_URL = settings.async_database_url