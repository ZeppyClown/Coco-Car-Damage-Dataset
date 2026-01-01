from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError
from pathlib import Path

from app.core.config import settings
from app.core.logging import get_logger
from app.core.middleware import (
    error_handling_middleware,
    validation_exception_handler,
    http_exception_handler,
    database_exception_handler,
)
from app.api.v1 import query, parts, valuation, paint_code, specifications, diagnostics
from app.db.session import init_db

logger = get_logger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered automotive knowledge and assistant system",
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(SQLAlchemyError, database_exception_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Error handling middleware
app.middleware("http")(error_handling_middleware)

# Serve static files (HTML, CSS, JS)
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Root endpoint - Serve web interface
@app.get("/")
async def root():
    """Serve the web interface"""
    index_file = Path(__file__).parent / "static" / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    else:
        # Fallback to API info if static files don't exist
        return {
            "service": settings.APP_NAME,
            "version": settings.API_VERSION,
            "description": "AI-powered automotive knowledge and assistant system",
            "documentation": "/docs",
            "health": "/health",
            "endpoints": {
                "query": "/api/v1/query",
                "parts": "/api/v1/parts/identify",
                "valuation": "/api/v1/valuation/estimate",
                "paint_code": "/api/v1/paint-code/lookup",
                "specifications": "/api/v1/specifications/{vin}",
                "diagnostics": "/api/v1/diagnostics/troubleshoot"
            }
        }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.API_VERSION
    }

# Include API routers
app.include_router(query.router, prefix=f"/api/{settings.API_VERSION}", tags=["Query"])
app.include_router(parts.router, prefix=f"/api/{settings.API_VERSION}", tags=["Parts"])
app.include_router(valuation.router, prefix=f"/api/{settings.API_VERSION}", tags=["Valuation"])
app.include_router(paint_code.router, prefix=f"/api/{settings.API_VERSION}", tags=["Paint Code"])
app.include_router(specifications.router, prefix=f"/api/{settings.API_VERSION}", tags=["Specifications"])
app.include_router(diagnostics.router, prefix=f"/api/{settings.API_VERSION}", tags=["Diagnostics"])

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("startup", message="Starting Automotive Assistant API")

    try:
        # Initialize database tables
        logger.info("startup", message="Initializing database tables")
        init_db()
        logger.info("startup", message="Database initialized successfully")
    except Exception as e:
        logger.error("startup_error", error=str(e), exc_info=True)
        raise

    # TODO: Load ML models
    # TODO: Initialize caches

    logger.info("startup", message="API started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("shutdown", message="Shutting down Automotive Assistant API")
    # TODO: Close database connections
    # TODO: Cleanup resources
    logger.info("shutdown", message="API shutdown complete")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=settings.DEBUG)
