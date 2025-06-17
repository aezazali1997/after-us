from .auth import router as auth_router
from .chat import router as chat_router
from .memory import router as memory_router
from .healing import router as healing_router
from .ai import router as ai_router
from .dashboard import router as dashboard_router
from .user import router as user_router

__all__ = [
    "auth_router",
    "chat_router",
    "memory_router",
    "healing_router",
    "ai_router",
    "dashboard_router",
    "user_router"
]
