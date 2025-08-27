#!/usr/bin/env python3
"""
Script para configuração inicial do banco de dados.
Cria tabelas e configura extensões necessárias.
"""

import sys
from pathlib import Path

# Adiciona diretório raiz ao path para imports
sys.path.append(str(Path(__file__).parent.parent))

from src.database import init_db, check_pgvector_extension
from src.core.config import settings


def setup_database():
    """Configura banco de dados inicial."""
    print("🔧 Configurando banco de dados...")
    
    try:
        # Valida configurações
        print("📋 Validando configurações...")
        settings.validate_required_settings()
        print("✅ Configurações válidas")
        
        # Inicializa banco
        print("🏗️  Criando tabelas...")
        init_db()
        print("✅ Tabelas criadas com sucesso")
        
        # Configura extensão pgvector
        print("🔌 Configurando extensão pgvector...")
        check_pgvector_extension()
        print("✅ Extensão pgvector configurada")
        
        print("\n🎉 Banco de dados configurado com sucesso!")
        print("   Você pode agora iniciar a aplicação com: python main.py")
        
    except Exception as e:
        print(f"❌ Erro na configuração: {str(e)}")
        return False
    
    return True


if __name__ == "__main__":
    print("🎯 WhatsApp Bot - Configuração de Banco de Dados")
    print("="*50)
    
    success = setup_database()
    if not success:
        sys.exit(1)
