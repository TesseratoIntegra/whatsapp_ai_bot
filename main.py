"""Aplicação principal FastAPI."""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from src.api import admin_router, webhook_router
from src.core.config import settings

# Cria aplicação FastAPI
app = FastAPI(
    title="WhatsApp AI Bot",
    description="Bot inteligente para WhatsApp com sistema de conhecimento PostgreSQL",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurações CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure conforme necessário
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configura arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

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
        "message": "WhatsApp AI Bot API",
        "version": "1.0.0",
        "docs": "/docs",
        "admin": "/admin",
        "frontend": "/",
    }


@app.get("/health")
async def health_check():
    """Endpoint de verificação de saúde."""
    return {"status": "healthy"}


def main():
    """Função principal para iniciar servidor."""
    # Valida configurações obrigatórias
    try:
        settings.validate_required_settings()
    except ValueError as e:
        print(f"Erro na configuração: {e}")
        return
    
    # Inicia servidor
    print("Iniciando servidor...")
    print("Frontend: http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    print("Admin: http://localhost:8000/admin/stats")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=False
    )


if __name__ == "__main__":
    main()
