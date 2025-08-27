#!/usr/bin/env python3
"""Script para testar imports da aplicação."""

import sys
import os

# Adiciona src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Testa imports principais do projeto."""
    print("Testando imports da aplicacao...")
    
    try:
        # Test core imports
        print("Testando imports do core...")
        from src.core.config import settings
        print("OK - Config importado com sucesso")
        
        from src.core.prompts import contextualize_prompt, qa_prompt
        print("OK - Prompts importados com sucesso")
        
        # Test database imports
        print("Testando imports do database...")
        from src.database import Base, get_db_context
        print("OK - Database imports com sucesso")
        
        # Test models
        print("Testando imports dos models...")
        from src.models import KnowledgeBase
        print("OK - Models importados com sucesso")
        
        # Test API imports
        print("Testando imports da API...")
        from src.api import admin_router, webhook_router
        print("OK - API imports com sucesso")
        
        # Test main app
        print("Testando import da aplicacao principal...")
        from main import app
        print("OK - Aplicacao principal importada com sucesso")
        
        print("\nTodos os imports funcionando corretamente!")
        print("Estrutura do projeto esta OK!")
        
        return True
        
    except ImportError as e:
        print(f"ERRO de import: {e}")
        return False
    except Exception as e:
        print(f"ERRO inesperado: {e}")
        return False


def test_config():
    """Testa configurações."""
    print("\nTestando configuracoes...")
    
    try:
        from src.core.config import settings
        
        print(f"   - OpenAI Model: {settings.OPENAI_MODEL_NAME}")
        print(f"   - Database Host: {settings.DATABASE_HOST}")
        print(f"   - Database Name: {settings.DATABASE_NAME}")
        print(f"   - Redis URL: {settings.REDIS_URL}")
        
        # Test database URL generation
        db_url = settings.database_url
        print(f"   - Database URL: {db_url}")
        
        print("OK - Configuracoes carregadas corretamente!")
        return True
        
    except Exception as e:
        print(f"ERRO nas configuracoes: {e}")
        return False


if __name__ == "__main__":
    print("WhatsApp Bot - Teste de Estrutura")
    print("="*50)
    
    # Test imports
    imports_ok = test_imports()
    
    # Test config
    config_ok = test_config()
    
    if imports_ok and config_ok:
        print("\nProjeto pronto para execucao!")
        print("   Para iniciar: python main.py")
    else:
        print("\nHa problemas na estrutura do projeto")
        sys.exit(1)