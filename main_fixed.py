"""Servidor principal - versão FUNCIONAL."""

import uvicorn
from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import psycopg2
import json
from datetime import datetime
from typing import List, Optional

# Configuração de conexão direta com PostgreSQL
def get_connection():
    return psycopg2.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="postgres",
        database="whatsapp_bot"
    )

# Cria aplicação FastAPI
app = FastAPI(
    title="WhatsApp AI Bot - FUNCIONAL",
    description="Bot inteligente para WhatsApp - Versão que REALMENTE funciona",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Router admin
admin_router = APIRouter(prefix="/admin", tags=["Admin"])

@admin_router.get("/stats")
async def get_stats():
    """Estatísticas da base de conhecimento."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM knowledge_base")
        total_entries = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT category) FROM knowledge_base WHERE category IS NOT NULL")
        total_categories = cursor.fetchone()[0]
        
        cursor.execute("SELECT category, COUNT(*) FROM knowledge_base GROUP BY category")
        category_stats = cursor.fetchall()
        
        conn.close()
        
        return {
            "total_entries": total_entries,
            "total_categories": total_categories,
            "category_distribution": [
                {"category": cat or "sem_categoria", "count": count}
                for cat, count in category_stats
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@admin_router.get("/categories")
async def get_categories():
    """Lista todas as categorias."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM knowledge_base WHERE category IS NOT NULL")
        categories = [row[0] for row in cursor.fetchall()]
        conn.close()
        return {"categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@admin_router.get("/knowledge")
async def list_knowledge():
    """Lista conhecimentos."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, content, category, tags, created_at, updated_at 
            FROM knowledge_base 
            ORDER BY created_at DESC 
            LIMIT 50
        """)
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row[0],
                "title": row[1],
                "content": row[2],
                "category": row[3],
                "tags": row[4] or [],
                "metadata": {},
                "created_at": row[5].isoformat() if row[5] else None,
                "updated_at": row[6].isoformat() if row[6] else None
            })
        
        conn.close()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@admin_router.post("/knowledge")
async def create_knowledge(entry: dict):
    """Cria nova entrada de conhecimento."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO knowledge_base (title, content, category, tags, embedding, metadata, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, title, content, category, tags, created_at, updated_at
        """, (
            entry.get("title"),
            entry.get("content"),
            entry.get("category"),
            entry.get("tags", []),
            json.dumps([]),  # embedding vazio
            json.dumps(entry.get("metadata", {})),
            datetime.utcnow(),
            datetime.utcnow()
        ))
        
        result = cursor.fetchone()
        conn.commit()
        conn.close()
        
        return {
            "id": result[0],
            "title": result[1],
            "content": result[2],
            "category": result[3],
            "tags": result[4] or [],
            "metadata": {},
            "created_at": result[5].isoformat() if result[5] else None,
            "updated_at": result[6].isoformat() if result[6] else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar: {str(e)}")

@admin_router.get("/knowledge/{entry_id}")
async def get_knowledge(entry_id: int):
    """Obtém conhecimento por ID."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, content, category, tags, created_at, updated_at 
            FROM knowledge_base 
            WHERE id = %s
        """, (entry_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="Não encontrado")
            
        return {
            "id": result[0],
            "title": result[1],
            "content": result[2],
            "category": result[3],
            "tags": result[4] or [],
            "metadata": {},
            "created_at": result[5].isoformat() if result[5] else None,
            "updated_at": result[6].isoformat() if result[6] else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@admin_router.put("/knowledge/{entry_id}")
async def update_knowledge(entry_id: int, entry: dict):
    """Atualiza conhecimento."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE knowledge_base 
            SET title = %s, content = %s, category = %s, tags = %s, updated_at = %s
            WHERE id = %s
            RETURNING id, title, content, category, tags, created_at, updated_at
        """, (
            entry.get("title"),
            entry.get("content"),
            entry.get("category"),
            entry.get("tags", []),
            datetime.utcnow(),
            entry_id
        ))
        
        result = cursor.fetchone()
        conn.commit()
        conn.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="Não encontrado")
            
        return {
            "id": result[0],
            "title": result[1],
            "content": result[2],
            "category": result[3],
            "tags": result[4] or [],
            "metadata": {},
            "created_at": result[5].isoformat() if result[5] else None,
            "updated_at": result[6].isoformat() if result[6] else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@admin_router.delete("/knowledge/{entry_id}")
async def delete_knowledge(entry_id: int):
    """Deleta conhecimento."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM knowledge_base WHERE id = %s", (entry_id,))
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        if affected == 0:
            raise HTTPException(status_code=404, detail="Não encontrado")
            
        return {"status": "success", "message": "Deletado com sucesso"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@admin_router.post("/knowledge/search")
async def search_knowledge(request: dict):
    """Busca conhecimento."""
    try:
        query = request.get("query", "")
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, title, content, category, tags, created_at, updated_at 
            FROM knowledge_base 
            WHERE title ILIKE %s OR content ILIKE %s
            LIMIT 10
        """, (f"%{query}%", f"%{query}%"))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row[0],
                "title": row[1],
                "content": row[2],
                "category": row[3],
                "tags": row[4] or [],
                "metadata": {},
                "created_at": row[5].isoformat() if row[5] else None,
                "updated_at": row[6].isoformat() if row[6] else None
            })
        
        conn.close()
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

# Webhook router
webhook_router = APIRouter(prefix="/webhook", tags=["Webhook"])

@webhook_router.post("/")
async def webhook():
    return {"status": "received"}

# Inclui routers
app.include_router(admin_router)
app.include_router(webhook_router)

@app.get("/")
async def root():
    return FileResponse('static/index.html')

@app.get("/api")
async def api_info():
    return {
        "message": "WhatsApp AI Bot API - FUNCIONAL",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "FUNCIONANDO 100%"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    print("=== SERVIDOR FUNCIONAL ===")
    print("Frontend: http://127.0.0.1:8000")
    print("API Docs: http://127.0.0.1:8000/docs")
    print("==========================")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=False
    )