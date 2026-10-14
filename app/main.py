from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from html import escape
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from pathlib import Path

from app.core.config import settings
from app.db.session import get_db
from app.core.workshop_auth import WorkshopAccessMiddleware, login_router
from app.core.logging import get_logger
from app.assistant import assistant_app
from app.core.middleware import (
    error_handling_middleware,
    validation_exception_handler,
    http_exception_handler,
    database_exception_handler,
    WorkshopUploadLimitMiddleware,
)
from app.api.v1 import query, parts, valuation, paint_code, specifications, diagnostics, workshop

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
app.add_middleware(WorkshopUploadLimitMiddleware)
app.add_middleware(WorkshopAccessMiddleware)
app.middleware("http")(error_handling_middleware)

# Serve static files (HTML, CSS, JS)
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
app.mount("/assistant", assistant_app)

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
                "diagnostics": "/api/v1/diagnostics/troubleshoot",
                "compatibility": "/api/v1/parts/compatibility"
            }
        }

# Health check endpoint
@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint. It also asks the database one trivial question, so a host's health check notices a lost
    database, and the scheduled keep-awake ping counts as database activity (free Supabase projects pause when idle)."""
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return JSONResponse(status_code=503, content={"status": "database unavailable", "service": settings.APP_NAME})
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
app.include_router(workshop.router, prefix=f"/api/{settings.API_VERSION}", tags=["Workshop"])


AI_LINKS = ('<a class="ai-link" href="/assistant/">Manual assistant</a>'
            '<a class="ai-link" href="/static/index.html">Parts &amp; vehicle tools</a>')


@app.get("/workshop", dependencies=[Depends(workshop.require_workshop_enabled)], include_in_schema=False)
def workshop_page(request: Request):
    page = (Path(__file__).parent / "templates/workshop.html").read_text(encoding="utf-8")
    page = page.replace("{{workshop_api}}", escape(f"/api/{settings.API_VERSION}/workshop", quote=True))
    page = page.replace("{{workshop_user}}", escape(request.state.workshop_user, quote=True))
    page = page.replace("{{ai_links}}", AI_LINKS if settings.AI_TOOLS_ENABLED else "")
    return HTMLResponse(page, headers={"Cache-Control": "no-store"})


SIGN_IN_MESSAGES = {
    "wrong": "That login name or password is not right. Try again.",
    "locked": "Too many wrong passwords. Wait five minutes and try again.",
    "out": "You have signed out.",
}
app.include_router(login_router)


@app.get("/workshop/login", include_in_schema=False)
def workshop_login_page(error: str = ""):
    page = (Path(__file__).parent / "templates/workshop_login.html").read_text(encoding="utf-8")
    page = page.replace("{{workshop_api}}", escape(f"/api/{settings.API_VERSION}/workshop", quote=True))
    message = SIGN_IN_MESSAGES.get(error)
    page = page.replace("{{message}}", f'<p id="status" role="status" class="{"" if error == "out" else "error"}">{message}</p>' if message else "")
    return HTMLResponse(page, headers={"Cache-Control": "no-store"})

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("startup", message="Starting Automotive Assistant API")

    # Schema changes run once through Alembic before application startup.
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
