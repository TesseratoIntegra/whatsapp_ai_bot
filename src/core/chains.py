"""Chains do LangChain para processamento de conversas."""

from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from .config import settings
from .prompts import contextualize_prompt, qa_prompt
from src.core.memory import get_session_history
from src.services import PostgreSQLVectorStore


def get_pg_vectorstore():
    """
    Obtém vector store baseado em PostgreSQL.
    
    Returns:
        PostgreSQLVectorStore: Instância do vector store
    """
    embeddings = OpenAIEmbeddings()
    return PostgreSQLVectorStore(embeddings)


def get_rag_chain(use_postgres: bool = True):
    """
    Obtém chain RAG com opção de usar PostgreSQL ou ChromaDB.
    
    Args:
        use_postgres: Se deve usar PostgreSQL (padrão: True)
        
    Returns:
        Chain configurado para RAG
    """
    llm = ChatOpenAI(
        model=settings.OPENAI_MODEL_NAME,
        temperature=settings.OPENAI_MODEL_TEMPERATURE,
    )
    
    if use_postgres:
        retriever = get_pg_vectorstore().as_retriever(
            search_type='hybrid',
            search_kwargs={'k': 4}
        )
    else:
        # Fallback para ChromaDB (compatibilidade)
        from src.core.legacy_vectorstore import get_vectorstore
        retriever = get_vectorstore().as_retriever()
    
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_prompt
    )
    question_answer_chain = create_stuff_documents_chain(
        llm=llm,
        prompt=qa_prompt,
    )
    return create_retrieval_chain(history_aware_retriever, question_answer_chain)


def get_conversational_rag_chain(use_postgres: bool = True):
    """
    Obtém chain RAG conversacional com opção de usar PostgreSQL ou ChromaDB.
    
    Args:
        use_postgres: Se deve usar PostgreSQL (padrão: True)
        
    Returns:
        Chain conversacional configurado
    """
    rag_chain = get_rag_chain(use_postgres=use_postgres)
    return RunnableWithMessageHistory(
        runnable=rag_chain,
        get_session_history=get_session_history,
        input_messages_key='input',
        history_messages_key='chat_history',
        output_messages_key='answer',
    )