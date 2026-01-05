import os

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api import (
    auth,
    documents,
    frontend,
    recommendations,
    search,
    semantic_search,
    users,
    web_auth,
)
from app.middleware.auth_middleware import AuthMiddleware

app = FastAPI(title="Knowledge Base API", version="1.0.0")

# Add middleware
app.add_middleware(AuthMiddleware)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(documents.router, prefix="/documents", tags=["documents"])
app.include_router(search.router, prefix="/search", tags=["search"])
app.include_router(
    semantic_search.router,
    prefix="/search/semantic",
    tags=["search"]
)
app.include_router(frontend.router, tags=["frontend"])
app.include_router(
    recommendations.router,
    prefix="/api/recommendations",
    tags=["recommendations"]
)
app.include_router(web_auth.router, tags=["web_auth"])


@app.on_event("startup")
async def startup_event():
    """Actions on application startup"""
    # Create directories if needed
    os.makedirs("data/indices", exist_ok=True)
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("app/static/css", exist_ok=True)
    os.makedirs("app/static/js", exist_ok=True)


@app.get("/")
def read_root():
    """Root endpoint"""
    return {"message": "Knowledge Base API with AI features is running"}


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "database": "postgresql"}


@app.get("/debug-tables")
def debug_tables():
    """Check table existence"""
    from sqlalchemy import inspect

    from app.core.database import engine

    inspector = inspect(engine)
    tables = inspector.get_table_names()

    return {
        "tables": tables,
        "has_users": "users" in tables,
        "has_documents": "documents" in tables,
        "has_embeddings": "embeddings" in tables
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )
