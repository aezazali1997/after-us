from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .utils.database import create_db_and_tables
from .api import (
    auth_router,
    chat_router,
    memory_router,
    healing_router,
    ai_router,
    dashboard_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Create database tables on startup
    create_db_and_tables()
    yield


app = FastAPI(
    title="After Us - Breakup Healing Assistant",
    description="An AI-powered platform to help users heal from breakups by analyzing conversations and providing therapeutic guidance.",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(memory_router)
app.include_router(healing_router)
app.include_router(ai_router)
app.include_router(dashboard_router)


@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "message": "Welcome to After Us - Your Breakup Healing Assistant",
        "status": "healthy",
        "version": "1.0.0",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
