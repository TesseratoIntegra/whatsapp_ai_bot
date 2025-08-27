"""Aplicação principal FastAPI - versão funcional sem PostgreSQL."""

import uvicorn
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Cria aplicação FastAPI
app = FastAPI(
    title="WhatsApp AI Bot",
    description="Bot inteligente para WhatsApp - Versão de Desenvolvimento",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurações CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configura arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Router administrativo com dados mock
admin_router = APIRouter(prefix="/admin", tags=["Administração"])

@admin_router.get("/stats")
async def get_stats():
    """Estatísticas mock da base de conhecimento."""
    return {
        "total_entries": 5,
        "total_categories": 3,
        "category_distribution": [
            {"category": "ajuda", "count": 2},
            {"category": "login", "count": 2},
            {"category": "geral", "count": 1}
        ]
    }

@admin_router.get("/categories")
async def get_categories():
    """Categorias mock."""
    return {"categories": ["ajuda", "login", "geral", "suporte"]}

@admin_router.get("/knowledge")
async def list_knowledge():
    """Lista de conhecimento mock."""
    return [
        {
            "id": 1,
            "title": "Como fazer login",
            "content": "Para fazer login, acesse a página inicial e digite suas credenciais.",
            "category": "login",
            "tags": ["login", "acesso", "credenciais"],
            "created_at": "2024-01-01T10:00:00",
            "updated_at": "2024-01-01T10:00:00"
        },
        {
            "id": 2,
            "title": "Esqueci minha senha",
            "content": "Se você esqueceu sua senha, clique em 'Esqueci minha senha' na tela de login.",
            "category": "login",
            "tags": ["senha", "recuperar", "esqueci"],
            "created_at": "2024-01-01T11:00:00",
            "updated_at": "2024-01-01T11:00:00"
        },
        {
            "id": 3,
            "title": "Como solicitar suporte",
            "content": "Para solicitar suporte, envie uma mensagem para nosso WhatsApp ou email de suporte.",
            "category": "ajuda",
            "tags": ["suporte", "ajuda", "contato"],
            "created_at": "2024-01-01T12:00:00",
            "updated_at": "2024-01-01T12:00:00"
        },
        {
            "id": 4,
            "title": "Funcionalidades principais",
            "content": "O bot oferece respostas automáticas, busca na base de conhecimento e suporte 24/7.",
            "category": "geral",
            "tags": ["funcionalidades", "recursos", "bot"],
            "created_at": "2024-01-01T13:00:00",
            "updated_at": "2024-01-01T13:00:00"
        },
        {
            "id": 5,
            "title": "Configurações avançadas",
            "content": "Acesse as configurações avançadas através do painel administrativo.",
            "category": "ajuda",
            "tags": ["configurações", "admin", "avançado"],
            "created_at": "2024-01-01T14:00:00",
            "updated_at": "2024-01-01T14:00:00"
        }
    ]

@admin_router.post("/knowledge")
async def create_knowledge(entry: dict):
    """Criar conhecimento mock."""
    return {
        "id": 999,
        "title": entry.get("title", "Novo conhecimento"),
        "content": entry.get("content", "Conteúdo do conhecimento"),
        "category": entry.get("category", "geral"),
        "tags": entry.get("tags", []),
        "created_at": "2024-01-01T15:00:00",
        "updated_at": "2024-01-01T15:00:00"
    }

@admin_router.get("/knowledge/{entry_id}")
async def get_knowledge(entry_id: int):
    """Obter conhecimento por ID mock."""
    return {
        "id": entry_id,
        "title": f"Conhecimento {entry_id}",
        "content": f"Este é o conteúdo do conhecimento número {entry_id}.",
        "category": "geral",
        "tags": ["exemplo", "teste"],
        "created_at": "2024-01-01T10:00:00",
        "updated_at": "2024-01-01T10:00:00"
    }

@admin_router.put("/knowledge/{entry_id}")
async def update_knowledge(entry_id: int, entry: dict):
    """Atualizar conhecimento mock."""
    return {
        "id": entry_id,
        "title": entry.get("title", f"Conhecimento {entry_id} atualizado"),
        "content": entry.get("content", "Conteúdo atualizado"),
        "category": entry.get("category", "geral"),
        "tags": entry.get("tags", []),
        "created_at": "2024-01-01T10:00:00",
        "updated_at": "2024-01-01T16:00:00"
    }

@admin_router.delete("/knowledge/{entry_id}")
async def delete_knowledge(entry_id: int):
    """Deletar conhecimento mock."""
    return {
        "status": "success",
        "message": f"Conhecimento {entry_id} removido com sucesso"
    }

@admin_router.post("/knowledge/search")
async def search_knowledge(request: dict):
    """Buscar conhecimento mock."""
    query = request.get("query", "teste")
    return [
        {
            "id": 1,
            "title": f"Resultado para: {query}",
            "content": f"Este é um resultado de busca para '{query}'. O sistema encontrou informações relevantes na base de conhecimento.",
            "category": "busca",
            "tags": ["resultado", "busca", query.lower()],
            "created_at": "2024-01-01T13:00:00",
            "updated_at": "2024-01-01T13:00:00"
        }
    ]

# Router webhook
webhook_router = APIRouter(prefix="/webhook", tags=["Webhook"])

@webhook_router.post("/")
async def webhook():
    """Endpoint do webhook."""
    return {"status": "received", "message": "Webhook funcionando"}

# Inclui routers
app.include_router(admin_router)
app.include_router(webhook_router)

@app.get("/")
async def root():
    """Serve a página inicial do frontend."""
    return FileResponse('static/index.html')

@app.get("/api")
async def api_info():
    """Endpoint com informações da API."""
    return {
        "message": "WhatsApp AI Bot API - Versão de Desenvolvimento",
        "version": "1.0.0",
        "docs": "/docs",
        "admin": "/admin",
        "frontend": "/",
        "status": "Funcionando com dados mock - PostgreSQL não configurado"
    }

@app.get("/health")
async def health_check():
    """Endpoint de verificação de saúde."""
    return {"status": "healthy", "database": "mock"}

def main():
    """Função principal para iniciar servidor."""
    print("=== WhatsApp AI Bot - Servidor de Desenvolvimento ===")
    print("AVISO: Esta versão usa dados mock. Configure PostgreSQL para produção.")
    print("")
    print("URLs disponíveis:")
    print("  Frontend: http://127.0.0.1:8000")
    print("  API Docs: http://127.0.0.1:8000/docs")
    print("  Admin API: http://127.0.0.1:8000/admin/stats")
    print("  Health: http://127.0.0.1:8000/health")
    print("")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()