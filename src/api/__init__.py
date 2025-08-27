"""
Módulo API - Endpoints REST para gerenciamento do sistema
"""

from .admin_routes import admin_router
from .webhook_routes import webhook_router

__all__ = ['admin_router', 'webhook_router']