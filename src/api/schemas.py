"""Schemas Pydantic para validação de dados da API."""

from typing import List, Optional, Dict, Any

from pydantic import BaseModel


class KnowledgeEntryCreate(BaseModel):
    """Schema para criação de entrada na base de conhecimento."""
    title: str
    content: str
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class KnowledgeEntryUpdate(BaseModel):
    """Schema para atualização de entrada na base de conhecimento."""
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class KnowledgeEntryResponse(BaseModel):
    """Schema de resposta para entrada na base de conhecimento."""
    id: int
    title: str
    content: str
    category: Optional[str]
    tags: Optional[List[str]]
    metadata: Optional[Dict[str, Any]]
    created_at: Optional[str]
    updated_at: Optional[str]


class SearchRequest(BaseModel):
    """Schema para requisição de busca."""
    query: str
    category: Optional[str] = None
    limit: int = 5
    search_type: str = "hybrid"  # hybrid, text, semantic


class CategoryStats(BaseModel):
    """Schema para estatísticas de categoria."""
    category: str
    count: int


class StatsResponse(BaseModel):
    """Schema de resposta para estatísticas."""
    total_entries: int
    total_categories: int
    category_distribution: List[CategoryStats]


class BulkImportResponse(BaseModel):
    """Schema de resposta para importação em lote."""
    status: str
    message: str
    count: int


class StandardResponse(BaseModel):
    """Schema de resposta padrão."""
    status: str
    message: str