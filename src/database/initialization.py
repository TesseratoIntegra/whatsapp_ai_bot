"""Inicialização e configuração do banco de dados."""

from sqlalchemy import text

from .connection import Base, async_engine, engine, get_db_context


def init_db() -> None:
    """Inicializa tabelas do banco de dados."""
    Base.metadata.create_all(bind=engine)


async def init_async_db() -> None:
    """Inicializa tabelas do banco de dados de forma assíncrona."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def check_pgvector_extension() -> None:
    """
    Verifica e instala extensão pgvector no PostgreSQL.
    
    Raises:
        Exception: Se não for possível instalar a extensão
    """
    with get_db_context() as db:
        try:
            # Verifica se extensão pgvector existe e a instala se necessário
            result = db.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            db.commit()
            print("✅ Extensão pgvector habilitada com sucesso")
        except Exception as e:
            print(f"❌ Erro ao habilitar extensão pgvector: {e}")
            print("Certifique-se de que o pgvector está instalado na instância PostgreSQL")
            raise
