from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from src.core.config import settings
from src.api.auth import router as auth_router
from src.api.tasks import router as tasks_router
from src.api.chat_api import router as chat_router
from src.db.init_db import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.

    This replaces the deprecated @app.on_event decorators.
    """
    # Startup: Initialize database tables
    logger.info("Starting application...")
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    yield

    # Shutdown: Cleanup resources
    logger.info("Shutting down application...")


app = FastAPI(
    title="Todo API",
    description="A RESTful Todo application with JWT authentication",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://hackathon-ii-git-main-shanyal-siddiquis-projects.vercel.app/",
        settings.BETTER_AUTH_URL,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/",
    tags=["Health"],
    summary="Health check",
    description="Check if the API is running and healthy.",
)
async def root():
    """
    Health check endpoint.

    Returns API status and version information.
    """
    return {
        "status": "ok",
        "message": "Todo API is running",
        "version": "1.0.0",
    }


# Register routers with updated URL structure
# Auth routes: /api/auth/register, /api/auth/login
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])

# Task routes: /api/tasks (user_id derived from JWT token)
app.include_router(tasks_router, prefix="/api", tags=["Tasks"])

# Chat routes: /api/{user_id}/chat (for AI agent communication)
app.include_router(chat_router, prefix="/api", tags=["AI Chat"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
        log_level="info",
    )
