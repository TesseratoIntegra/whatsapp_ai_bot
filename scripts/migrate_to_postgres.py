#!/usr/bin/env python3
"""
Script para migração de arquivos RAG e dados ChromaDB para PostgreSQL.
Execute após configurar PostgreSQL para migrar dados existentes.
"""

import os
import sys
from pathlib import Path

# Adiciona diretório raiz ao path para imports
sys.path.append(str(Path(__file__).parent.parent))

from src.database import init_db, check_pgvector_extension
from src.services import knowledge_service
from src.core.legacy_vectorstore import load_documents


def migrate_rag_files():
    """Migra arquivos RAG para PostgreSQL."""
    print("🔄 Iniciando migração de arquivos RAG para PostgreSQL...")
    
    try:
        # Inicializa banco de dados
        print("📊 Inicializando banco de dados...")
        init_db()
        check_pgvector_extension()
        print("✅ Banco de dados inicializado com sucesso")
        
        # Carrega documentos existentes
        print("📁 Carregando arquivos RAG existentes...")
        documents = load_documents()
        
        if not documents:
            print("⚠️  Nenhum documento encontrado para migrar")
            return
        
        print(f"📋 Encontrados {len(documents)} documentos para migrar")
        
        # Importa documentos para PostgreSQL
        print("💾 Importando documentos para PostgreSQL...")
        count = knowledge_service.bulk_import_from_documents(
            documents, 
            category="migrado_de_rag"
        )
        
        print(f"✅ Migrados {count} documentos com sucesso para PostgreSQL")
        
        # Exibe estatísticas
        print("\n📈 Estatísticas da Migração:")
        print(f"   - Total de documentos processados: {len(documents)}")
        print(f"   - Importados com sucesso: {count}")
        print(f"   - Falhas na importação: {len(documents) - count}")
        
        if count > 0:
            print(f"\n🎉 Migração concluída com sucesso!")
            print(f"   Agora você pode gerenciar sua base de conhecimento através:")
            print(f"   - Endpoints da API em /admin/knowledge")
            print(f"   - Ou programaticamente usando knowledge_service")
        
    except Exception as e:
        print(f"❌ Falha na migração: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def test_postgres_search():
    """Testa funcionalidade de busca PostgreSQL."""
    print("\n🔍 Testando funcionalidade de busca PostgreSQL...")
    
    try:
        # Testa busca textual
        results = knowledge_service.search_by_text("teste", limit=3)
        print(f"📝 Busca textual retornou {len(results)} resultados")
        
        # Testa busca semântica
        results = knowledge_service.search_by_similarity("teste", limit=3)
        print(f"🧠 Busca semântica retornou {len(results)} resultados")
        
        # Testa busca híbrida
        results = knowledge_service.hybrid_search("teste", limit=3)
        print(f"🔀 Busca híbrida retornou {len(results)} resultados")
        
        print("✅ Todos os métodos de busca funcionando corretamente")
        return True
        
    except Exception as e:
        print(f"❌ Teste de busca falhou: {str(e)}")
        return False


def display_next_steps():
    """Exibe próximos passos após migração."""
    print("\n" + "="*60)
    print("🚀 MIGRAÇÃO CONCLUÍDA - PRÓXIMOS PASSOS:")
    print("="*60)
    print()
    print("1. 📝 Atualize seu arquivo .env com configurações PostgreSQL:")
    print("   DATABASE_HOST=localhost")
    print("   DATABASE_PORT=5432")
    print("   DATABASE_NAME=whatsapp_bot")
    print("   DATABASE_USER=postgres")
    print("   DATABASE_PASSWORD=sua_senha")
    print()
    print("2. 🐳 Inicie PostgreSQL com Docker:")
    print("   docker-compose up postgres -d")
    print()
    print("3. 🤖 Atualize bot para usar PostgreSQL:")
    print("   Seu chains.py agora usa PostgreSQL por padrão (use_postgres=True)")
    print()
    print("4. 🔧 Gerencie base de conhecimento via API:")
    print("   GET    /admin/knowledge          - Listar todas as entradas")
    print("   POST   /admin/knowledge          - Criar nova entrada")
    print("   PUT    /admin/knowledge/{id}     - Atualizar entrada")
    print("   DELETE /admin/knowledge/{id}     - Remover entrada")
    print("   POST   /admin/knowledge/search   - Buscar entradas")
    print()
    print("5. 📊 Visualizar estatísticas:")
    print("   GET /admin/stats - Obter estatísticas da base de conhecimento")
    print()
    print("6. 🔄 Importar mais dados:")
    print("   POST /admin/knowledge/bulk-import - Importar mais arquivos RAG")
    print()
    print("7. 🚀 Iniciar aplicação:")
    print("   python main.py")
    print()
    print("✨ Seu bot agora usa uma poderosa base de conhecimento PostgreSQL!")


if __name__ == "__main__":
    print("🎯 WhatsApp Bot - Ferramenta de Migração PostgreSQL")
    print("="*50)
    
    # Verifica se estamos no diretório correto
    if not os.path.exists("src/core/config.py"):
        print("❌ Execute este script do diretório raiz do projeto")
        sys.exit(1)
    
    # Executa migração
    success = migrate_rag_files()
    
    if success:
        # Testa funcionalidade
        test_postgres_search()
        
        # Exibe próximos passos
        display_next_steps()
    else:
        print("\n❌ Migração falhou. Verifique os erros acima.")
        sys.exit(1)
