"""Rotas da API de administração para gerenciamento da base de conhecimento."""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from sqlalchemy import func

from src.database import get_db_context, init_db, check_pgvector_extension
from src.models import KnowledgeBase
from src.services import knowledge_service
from .schemas import (
    KnowledgeEntryCreate,
    KnowledgeEntryUpdate,
    KnowledgeEntryResponse,
    SearchRequest,
    StatsResponse,
    CategoryStats,
    BulkImportResponse,
    StandardResponse,
)

# Cria router com prefixo e tag
admin_router = APIRouter(prefix="/admin", tags=["Administração"])


def knowledge_to_response(entry) -> KnowledgeEntryResponse:
    """Converte entrada de conhecimento para resposta."""
    try:
        return KnowledgeEntryResponse(
            id=getattr(entry, 'id', 0),
            title=getattr(entry, 'title', ''),
            content=getattr(entry, 'content', ''),
            category=getattr(entry, 'category', None),
            tags=getattr(entry, 'tags', []),
            metadata=getattr(entry, 'metadata_', {}),
            created_at=entry.created_at.isoformat() if hasattr(entry, 'created_at') and entry.created_at else None,
            updated_at=entry.updated_at.isoformat() if hasattr(entry, 'updated_at') and entry.updated_at else None
        )
    except Exception as e:
        # Se falhar, retorna resposta padrão
        return KnowledgeEntryResponse(
            id=0,
            title="Erro ao carregar",
            content="Erro ao carregar conteúdo",
            category=None,
            tags=[],
            metadata={},
            created_at=None,
            updated_at=None
        )


@admin_router.post("/init-db", response_model=StandardResponse)
async def initialize_database():
    """Inicializa banco de dados e verifica extensão pgvector."""
    try:
        init_db()
        check_pgvector_extension()
        return StandardResponse(
            status="success",
            message="Banco de dados inicializado com sucesso"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Falha na inicialização do banco: {str(e)}"
        )


@admin_router.post("/knowledge", response_model=KnowledgeEntryResponse)
async def create_knowledge_entry(entry: KnowledgeEntryCreate):
    """Cria nova entrada na base de conhecimento."""
    try:
        db_entry = knowledge_service.create_entry(
            title=entry.title,
            content=entry.content,
            category=entry.category,
            tags=entry.tags,
            metadata=entry.metadata
        )
        return knowledge_to_response(db_entry)
    except Exception as e:
        import traceback
        print(f"Erro detalhado: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Falha ao criar entrada: {str(e)}"
        )


@admin_router.get("/knowledge/{entry_id}", response_model=KnowledgeEntryResponse)
async def get_knowledge_entry(entry_id: int):
    """Obtém entrada da base de conhecimento por ID."""
    entry = knowledge_service.get_entry(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entrada não encontrada")
    return knowledge_to_response(entry)


@admin_router.put("/knowledge/{entry_id}", response_model=KnowledgeEntryResponse)
async def update_knowledge_entry(entry_id: int, entry: KnowledgeEntryUpdate):
    """Atualiza entrada da base de conhecimento."""
    db_entry = knowledge_service.update_entry(
        entry_id=entry_id,
        title=entry.title,
        content=entry.content,
        category=entry.category,
        tags=entry.tags,
        metadata=entry.metadata
    )
    if not db_entry:
        raise HTTPException(status_code=404, detail="Entrada não encontrada")
    return knowledge_to_response(db_entry)


@admin_router.delete("/knowledge/{entry_id}", response_model=StandardResponse)
async def delete_knowledge_entry(entry_id: int):
    """Remove entrada da base de conhecimento."""
    success = knowledge_service.delete_entry(entry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Entrada não encontrada")
    return StandardResponse(
        status="success",
        message="Entrada removida com sucesso"
    )


@admin_router.get("/knowledge", response_model=List[KnowledgeEntryResponse])
async def list_knowledge_entries(
    category: Optional[str] = Query(None, description="Filtrar por categoria"),
    tags: Optional[str] = Query(
        None, description="Filtrar por tags (separadas por vírgula)"
    ),
    limit: int = Query(100, description="Número máximo de entradas"),
    offset: int = Query(0, description="Número de entradas a pular")
):
    """Lista entradas da base de conhecimento com filtros opcionais."""
    tag_list = tags.split(',') if tags else None
    entries = knowledge_service.list_entries(
        category=category,
        tags=tag_list,
        limit=limit,
        offset=offset
    )
    return [knowledge_to_response(entry) for entry in entries]


@admin_router.post("/knowledge/search", response_model=List[KnowledgeEntryResponse])
async def search_knowledge(request: SearchRequest):
    """Busca entradas na base de conhecimento."""
    try:
        if request.search_type == "text":
            entries = knowledge_service.search_by_text(
                query=request.query,
                category=request.category,
                limit=request.limit
            )
        elif request.search_type == "semantic":
            entries = knowledge_service.search_by_similarity(
                query=request.query,
                category=request.category,
                limit=request.limit
            )
        else:  # hybrid
            entries = knowledge_service.hybrid_search(
                query=request.query,
                category=request.category,
                limit=request.limit
            )
        
        return [knowledge_to_response(entry) for entry in entries]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Falha na busca: {str(e)}"
        )


@admin_router.get("/categories")
async def get_categories():
    """Obtém todas as categorias únicas."""
    categories = knowledge_service.get_categories()
    return {"categories": categories}


@admin_router.post("/knowledge/bulk-import", response_model=BulkImportResponse)
async def bulk_import_from_files():
    """Importa arquivos RAG existentes para PostgreSQL."""
    try:
        from src.core.legacy_vectorstore import load_documents
        
        # Carrega documentos dos arquivos RAG existentes
        documents = load_documents()
        if not documents:
            return BulkImportResponse(
                status="success",
                message="Nenhum documento para importar",
                count=0
            )
        
        # Importa para PostgreSQL
        count = knowledge_service.bulk_import_from_documents(
            documents,
            category="migrado_de_rag"
        )
        
        return BulkImportResponse(
            status="success",
            message=f"Importados {count} documentos com sucesso",
            count=count
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Falha na importação em lote: {str(e)}"
        )


@admin_router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Obtém estatísticas da base de conhecimento."""
    try:
        with get_db_context() as db:
            total_entries = db.query(KnowledgeBase).count()
            total_categories = db.query(KnowledgeBase.category).distinct().count()
            
            # Obtém distribuição por categoria
            category_stats = db.query(
                KnowledgeBase.category,
                func.count(KnowledgeBase.id).label('count')
            ).group_by(KnowledgeBase.category).all()
            
            return StatsResponse(
                total_entries=total_entries,
                total_categories=total_categories,
                category_distribution=[
                    CategoryStats(category=cat or "sem_categoria", count=count)
                    for cat, count in category_stats
                ]
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Falha ao obter estatísticas: {str(e)}"
        )