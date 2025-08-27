"""Serviço de vector store baseado em PostgreSQL com pgvector."""

from typing import List, Optional, Dict, Any

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore, VectorStoreRetriever

from src.models import KnowledgeBase
from .knowledge_service import knowledge_service


class PostgreSQLVectorStore(VectorStore):
    """
    Implementação de vector store usando PostgreSQL com pgvector.
    Compatível com interface VectorStore do LangChain.
    """
    
    def __init__(self, embeddings: Embeddings):
        """
        Inicializa vector store PostgreSQL.
        
        Args:
            embeddings: Instância de embeddings do LangChain
        """
        self.embeddings = embeddings
        self.knowledge_service = knowledge_service
    
    def add_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        titles: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> List[str]:
        """
        Adiciona textos ao vector store.
        
        Args:
            texts: Lista de textos a serem adicionados
            metadatas: Lista opcional de metadados
            titles: Lista opcional de títulos
            categories: Lista opcional de categorias
            **kwargs: Argumentos adicionais
            
        Returns:
            List[str]: Lista de IDs dos textos adicionados
        """
        ids = []
        
        for i, text in enumerate(texts):
            metadata = metadatas[i] if metadatas else {}
            title = titles[i] if titles else f"Document {i + 1}"
            category = categories[i] if categories else metadata.get(
                'category', 'general'
            )
            
            entry = self.knowledge_service.create_entry(
                title=title,
                content=text,
                category=category,
                metadata=metadata
            )
            ids.append(str(entry.id))
        
        return ids
    
    def add_documents(
        self, 
        documents: List[Document], 
        **kwargs: Any
    ) -> List[str]:
        """
        Adiciona documentos ao vector store.
        
        Args:
            documents: Lista de documentos do LangChain
            **kwargs: Argumentos adicionais
            
        Returns:
            List[str]: Lista de IDs dos documentos adicionados
        """
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        titles = [
            doc.metadata.get('title', f'Document {i+1}') 
            for i, doc in enumerate(documents)
        ]
        categories = [
            doc.metadata.get('category', 'general') 
            for doc in documents
        ]
        
        return self.add_texts(
            texts=texts,
            metadatas=metadatas,
            titles=titles,
            categories=categories,
            **kwargs
        )
    
    def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> List[Document]:
        """
        Retorna documentos mais similares usando busca semântica.
        
        Args:
            query: Consulta de busca
            k: Número de resultados a retornar
            filter: Filtros opcionais
            **kwargs: Argumentos adicionais
            
        Returns:
            List[Document]: Lista de documentos similares
        """
        category = filter.get('category') if filter else None
        similarity_threshold = kwargs.get('similarity_threshold', 0.7)
        
        entries = self.knowledge_service.search_by_similarity(
            query=query,
            category=category,
            limit=k,
            similarity_threshold=similarity_threshold
        )
        
        return [self._entry_to_document(entry) for entry in entries]
    
    def similarity_search_with_score(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> List[tuple[Document, float]]:
        """
        Retorna documentos com scores de similaridade.
        
        Args:
            query: Consulta de busca
            k: Número de resultados
            filter: Filtros opcionais
            **kwargs: Argumentos adicionais
            
        Returns:
            List[tuple[Document, float]]: Documentos com scores
        """
        # Por enquanto, retorna similarity_search com scores fictícios
        # Pode ser aprimorado para retornar distâncias cosseno reais
        docs = self.similarity_search(query, k, filter, **kwargs)
        return [(doc, 0.8) for doc in docs]  # Scores de placeholder
    
    def hybrid_search(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> List[Document]:
        """
        Retorna documentos usando busca híbrida (textual + semântica).
        
        Args:
            query: Consulta de busca
            k: Número de resultados
            filter: Filtros opcionais
            **kwargs: Argumentos adicionais
            
        Returns:
            List[Document]: Lista de documentos relevantes
        """
        category = filter.get('category') if filter else None
        similarity_threshold = kwargs.get('similarity_threshold', 0.7)
        
        entries = self.knowledge_service.hybrid_search(
            query=query,
            category=category,
            limit=k,
            similarity_threshold=similarity_threshold
        )
        
        return [self._entry_to_document(entry) for entry in entries]
    
    def text_search(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> List[Document]:
        """
        Retorna documentos usando busca textual completa.
        
        Args:
            query: Consulta de busca
            k: Número de resultados
            filter: Filtros opcionais
            **kwargs: Argumentos adicionais
            
        Returns:
            List[Document]: Lista de documentos encontrados
        """
        category = filter.get('category') if filter else None
        
        entries = self.knowledge_service.search_by_text(
            query=query,
            category=category,
            limit=k
        )
        
        return [self._entry_to_document(entry) for entry in entries]
    
    def delete(
        self, 
        ids: Optional[List[str]] = None, 
        **kwargs: Any
    ) -> Optional[bool]:
        """
        Remove entradas por IDs.
        
        Args:
            ids: Lista de IDs a serem removidos
            **kwargs: Argumentos adicionais
            
        Returns:
            Optional[bool]: True se removido com sucesso
        """
        if not ids:
            return False
        
        success = True
        for id_str in ids:
            try:
                entry_id = int(id_str)
                if not self.knowledge_service.delete_entry(entry_id):
                    success = False
            except ValueError:
                success = False
        
        return success
    
    def get_by_ids(self, ids: List[str]) -> List[Document]:
        """
        Obtém documentos por IDs.
        
        Args:
            ids: Lista de IDs
            
        Returns:
            List[Document]: Lista de documentos encontrados
        """
        docs = []
        for id_str in ids:
            try:
                entry_id = int(id_str)
                entry = self.knowledge_service.get_entry(entry_id)
                if entry:
                    docs.append(self._entry_to_document(entry))
            except ValueError:
                continue
        
        return docs
    
    def _entry_to_document(self, entry: KnowledgeBase) -> Document:
        """
        Converte entrada KnowledgeBase para Document do LangChain.
        
        Args:
            entry: Entrada da base de conhecimento
            
        Returns:
            Document: Documento do LangChain
        """
        metadata = entry.metadata_.copy() if entry.metadata_ else {}
        metadata.update({
            'id': entry.id,
            'title': entry.title,
            'category': entry.category,
            'tags': entry.tags,
            'created_at': entry.created_at.isoformat() if entry.created_at else None,
            'updated_at': entry.updated_at.isoformat() if entry.updated_at else None,
        })
        
        return Document(
            page_content=entry.content,
            metadata=metadata
        )
    
    @classmethod
    def from_texts(
        cls,
        texts: List[str],
        embeddings: Embeddings,
        metadatas: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> "PostgreSQLVectorStore":
        """
        Cria vector store a partir de textos.
        
        Args:
            texts: Lista de textos
            embeddings: Instância de embeddings
            metadatas: Lista opcional de metadados
            **kwargs: Argumentos adicionais
            
        Returns:
            PostgreSQLVectorStore: Instância do vector store
        """
        store = cls(embeddings)
        store.add_texts(texts, metadatas, **kwargs)
        return store
    
    @classmethod
    def from_documents(
        cls,
        documents: List[Document],
        embeddings: Embeddings,
        **kwargs: Any,
    ) -> "PostgreSQLVectorStore":
        """
        Cria vector store a partir de documentos.
        
        Args:
            documents: Lista de documentos
            embeddings: Instância de embeddings
            **kwargs: Argumentos adicionais
            
        Returns:
            PostgreSQLVectorStore: Instância do vector store
        """
        store = cls(embeddings)
        store.add_documents(documents, **kwargs)
        return store
    
    def as_retriever(self, **kwargs):
        """
        Retorna como retriever do LangChain.
        
        Args:
            **kwargs: Argumentos do retriever
            
        Returns:
            Retriever configurado
        """
        from langchain_core.vectorstores import VectorStoreRetriever
        
        # Define tipo de busca como híbrida por padrão
        search_type = kwargs.get('search_type', 'hybrid')
        search_kwargs = kwargs.get('search_kwargs', {})
        
        if search_type == 'hybrid':
            # Retriever customizado para busca híbrida
            return PostgreSQLRetriever(
                vectorstore=self, 
                search_kwargs=search_kwargs
            )
        else:
            return VectorStoreRetriever(
                vectorstore=self, 
                search_type=search_type, 
                search_kwargs=search_kwargs
            )


class PostgreSQLRetriever(VectorStoreRetriever):
    """Retriever customizado para vector store PostgreSQL com busca híbrida."""
    
    def _get_relevant_documents(self, query: str) -> List[Document]:
        """
        Obtém documentos relevantes usando busca híbrida.
        
        Args:
            query: Consulta de busca
            
        Returns:
            List[Document]: Documentos relevantes
        """
        if hasattr(self.vectorstore, 'hybrid_search'):
            return self.vectorstore.hybrid_search(query, **self.search_kwargs)
        else:
            return self.vectorstore.similarity_search(query, **self.search_kwargs)