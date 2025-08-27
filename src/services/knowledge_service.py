"""Serviço para gerenciamento da base de conhecimento."""

from typing import List, Optional, Dict, Any

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from sqlalchemy import text, desc

from src.database import get_db_context
from src.models import KnowledgeBase


class KnowledgeService:
    """Serviço para gerenciar entradas da base de conhecimento."""
    
    def __init__(self):
        """Inicializa o serviço com embeddings do OpenAI."""
        self.embeddings = OpenAIEmbeddings()
    
    def create_entry(
        self,
        title: str,
        content: str,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> KnowledgeBase:
        """
        Cria nova entrada na base de conhecimento.
        
        Args:
            title: Título da entrada
            content: Conteúdo principal
            category: Categoria opcional
            tags: Lista de tags opcionais
            metadata: Metadados adicionais opcionais
            
        Returns:
            KnowledgeBase: Entrada criada
        """
        # Gera embedding do conteúdo
        embedding = self.embeddings.embed_query(content)
        
        with get_db_context() as db:
            entry = KnowledgeBase(
                title=title,
                content=content,
                category=category,
                tags=tags or [],
                embedding=embedding,
                metadata_=metadata or {}
            )
            db.add(entry)
            db.flush()
            db.refresh(entry)
            return entry
    
    def get_entry(self, entry_id: int) -> Optional[KnowledgeBase]:
        """
        Busca entrada por ID.
        
        Args:
            entry_id: ID da entrada
            
        Returns:
            Optional[KnowledgeBase]: Entrada encontrada ou None
        """
        with get_db_context() as db:
            return db.query(KnowledgeBase).filter(
                KnowledgeBase.id == entry_id
            ).first()
    
    def update_entry(
        self,
        entry_id: int,
        title: Optional[str] = None,
        content: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[KnowledgeBase]:
        """
        Atualiza entrada existente.
        
        Args:
            entry_id: ID da entrada
            title: Novo título opcional
            content: Novo conteúdo opcional
            category: Nova categoria opcional
            tags: Novas tags opcionais
            metadata: Novos metadados opcionais
            
        Returns:
            Optional[KnowledgeBase]: Entrada atualizada ou None
        """
        with get_db_context() as db:
            entry = db.query(KnowledgeBase).filter(
                KnowledgeBase.id == entry_id
            ).first()
            if not entry:
                return None
            
            # Atualiza campos se fornecidos
            if title is not None:
                entry.title = title
            if content is not None:
                entry.content = content
                # Re-gera embedding se conteúdo mudou
                entry.embedding = self.embeddings.embed_query(content)
            if category is not None:
                entry.category = category
            if tags is not None:
                entry.tags = tags
            if metadata is not None:
                entry.metadata_ = metadata
            
            db.flush()
            db.refresh(entry)
            return entry
    
    def delete_entry(self, entry_id: int) -> bool:
        """
        Remove entrada da base de conhecimento.
        
        Args:
            entry_id: ID da entrada
            
        Returns:
            bool: True se removida com sucesso
        """
        with get_db_context() as db:
            entry = db.query(KnowledgeBase).filter(
                KnowledgeBase.id == entry_id
            ).first()
            if entry:
                db.delete(entry)
                return True
            return False
    
    def list_entries(
        self,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[KnowledgeBase]:
        """
        Lista entradas com filtros opcionais.
        
        Args:
            category: Filtrar por categoria
            tags: Filtrar por tags
            limit: Limite de resultados
            offset: Offset para paginação
            
        Returns:
            List[KnowledgeBase]: Lista de entradas
        """
        with get_db_context() as db:
            query = db.query(KnowledgeBase)
            
            if category:
                query = query.filter(KnowledgeBase.category == category)
            
            if tags:
                for tag in tags:
                    query = query.filter(KnowledgeBase.tags.contains([tag]))
            
            return query.order_by(desc(KnowledgeBase.updated_at)).offset(
                offset
            ).limit(limit).all()
    
    def search_by_text(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 5
    ) -> List[KnowledgeBase]:
        """
        Busca entradas usando busca textual completa do PostgreSQL.
        
        Args:
            query: Termo de busca
            category: Filtrar por categoria opcional
            limit: Limite de resultados
            
        Returns:
            List[KnowledgeBase]: Lista de entradas relevantes
        """
        with get_db_context() as db:
            sql_query = """
                SELECT *, ts_rank(
                    to_tsvector('portuguese', content), 
                    plainto_tsquery('portuguese', :query)
                ) as rank
                FROM knowledge_base
                WHERE to_tsvector('portuguese', content) @@ plainto_tsquery('portuguese', :query)
            """
            
            if category:
                sql_query += " AND category = :category"
            
            sql_query += " ORDER BY rank DESC LIMIT :limit"
            
            params = {"query": query, "limit": limit}
            if category:
                params["category"] = category
            
            result = db.execute(text(sql_query), params)
            
            entries = []
            for row in result:
                entry = KnowledgeBase(
                    id=row.id,
                    title=row.title,
                    content=row.content,
                    category=row.category,
                    tags=row.tags,
                    embedding=row.embedding,
                    metadata_=row.metadata,
                    created_at=row.created_at,
                    updated_at=row.updated_at
                )
                entries.append(entry)
            
            return entries
    
    def search_by_similarity(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[KnowledgeBase]:
        """
        Busca entradas usando similaridade semântica.
        
        Args:
            query: Termo de busca
            category: Filtrar por categoria opcional
            limit: Limite de resultados
            similarity_threshold: Limiar de similaridade (0.0-1.0)
            
        Returns:
            List[KnowledgeBase]: Lista de entradas similares
        """
        # Por enquanto, usa busca textual (sem pgvector)
        # TODO: Implementar similaridade cosseno com JSONB embeddings
        return self.search_by_text(query, category, limit)
    
    def hybrid_search(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[KnowledgeBase]:
        """
        Combina busca textual e semântica para melhores resultados.
        
        Args:
            query: Termo de busca
            category: Filtrar por categoria opcional
            limit: Limite de resultados
            similarity_threshold: Limiar de similaridade para busca semântica
            
        Returns:
            List[KnowledgeBase]: Lista combinada de entradas relevantes
        """
        # Obtém resultados de ambos os métodos
        text_results = self.search_by_text(query, category, limit)
        semantic_results = self.search_by_similarity(
            query, category, limit, similarity_threshold
        )
        
        # Combina e remove duplicatas
        combined_results = {}
        
        # Adiciona resultados da busca textual (prioridade maior)
        for i, entry in enumerate(text_results):
            # Score maior para matches textuais
            combined_results[entry.id] = (entry, len(text_results) - i + 10)
        
        # Adiciona resultados da busca semântica
        for i, entry in enumerate(semantic_results):
            if entry.id in combined_results:
                # Aumenta score se encontrado em ambas as buscas
                current_entry, current_score = combined_results[entry.id]
                combined_results[entry.id] = (current_entry, current_score + 5)
            else:
                combined_results[entry.id] = (entry, len(semantic_results) - i)
        
        # Ordena por score combinado e retorna
        sorted_results = sorted(
            combined_results.values(), 
            key=lambda x: x[1], 
            reverse=True
        )
        return [entry for entry, score in sorted_results[:limit]]
    
    def get_categories(self) -> List[str]:
        """
        Obtém todas as categorias únicas.
        
        Returns:
            List[str]: Lista de categorias
        """
        with get_db_context() as db:
            result = db.query(KnowledgeBase.category).distinct().filter(
                KnowledgeBase.category.isnot(None)
            ).all()
            return [row.category for row in result]
    
    def bulk_import_from_documents(
        self, 
        documents: List[Document], 
        category: str = "imported"
    ) -> int:
        """
        Importa múltiplos documentos de uma vez.
        
        Args:
            documents: Lista de documentos do LangChain
            category: Categoria para os documentos importados
            
        Returns:
            int: Número de documentos importados com sucesso
        """
        count = 0
        for doc in documents:
            try:
                title = doc.metadata.get('title', f"Document {count + 1}")
                self.create_entry(
                    title=title,
                    content=doc.page_content,
                    category=category,
                    metadata=doc.metadata
                )
                count += 1
            except Exception as e:
                print(f"Erro ao importar documento: {e}")
                continue
        
        return count


# Instância global do serviço
knowledge_service = KnowledgeService()