from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import query, parts, valuation, paint_code, specifications, diagnostics

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered automotive knowledge and assistant system",
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    # TODO: Initialize database connections
    # TODO: Load ML models
    # TODO: Initialize caches
    pass

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    # TODO: Close database connections
    # TODO: Cleanup resources
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=settings.DEBUG)
