"""Modelos de banco de dados para base de conhecimento."""

from typing import Dict, Any

from sqlalchemy import Column, Integer, String, Text, DateTime, ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from src.database.connection import Base


class KnowledgeBase(Base):
    """
    Modelo para armazenar conhecimento/respostas do bot.
    
    Esta tabela contém o conhecimento que será usado pelo bot para responder
    perguntas dos usuários, incluindo embeddings para busca semântica.
    """
    __tablename__ = "knowledge_base"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    category = Column(String(100), index=True)
    tags = Column(ARRAY(String))
    embedding = Column(JSONB)  # Embeddings como array JSON (sem pgvector)
    metadata_ = Column('metadata', JSONB)
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )

    def __repr__(self) -> str:
        """Representação string do objeto."""
        return (
            f"<KnowledgeBase(id={self.id}, title='{self.title}', "
            f"category='{self.category}')>"
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Converte o modelo para dicionário.
        
        Returns:
            Dict[str, Any]: Representação em dicionário do objeto
        """
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'tags': self.tags,
            'metadata': self.metadata_,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
