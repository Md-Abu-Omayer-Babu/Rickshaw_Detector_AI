"""
Main FastAPI application entry point.
Configures the application, registers routes, and sets up middleware.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.startup import startup_event, shutdown_event
from app.routes import detect_image, detect_video, history


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description=settings.description,
    docs_url="/docs",
    redoc_url="/redoc"
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)


# Register startup and shutdown events
@app.on_event("startup")
async def on_startup():
    """Execute startup tasks."""
    startup_event()


@app.on_event("shutdown")
async def on_shutdown():
    """Execute shutdown tasks."""
    shutdown_event()


# Mount static files for serving processed images and videos
app.mount(
    "/outputs",
    StaticFiles(directory=str(settings.outputs_dir)),
    name="outputs"
)


# Register API routes
app.include_router(detect_image.router, prefix=settings.api_prefix)
app.include_router(detect_video.router, prefix=settings.api_prefix)
app.include_router(history.router, prefix=settings.api_prefix)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint providing API information.
    """
    return {
        "name": settings.app_name,
        "version": settings.version,
        "description": settings.description,
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "detect_image": f"{settings.api_prefix}/detect/image",
            "detect_video": f"{settings.api_prefix}/detect/video",
            "history": f"{settings.api_prefix}/history"
        }
    }


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.version
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors.
    """
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else "An unexpected error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
