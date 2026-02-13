from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from routers import media, android, files, analysis, jobs, ai
from config import settings
from pathlib import Path

app = FastAPI(
    title="Mobile Media Organizer API",
    description="API to control file organization tasks with real-time progress tracking.",
    version=settings.app_version,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
)

# CORS - configurable origins from .env
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for UI
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Routers
app.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
app.include_router(media.router, prefix="/media", tags=["Media"])
app.include_router(android.router, prefix="/android", tags=["Android"])
app.include_router(files.router, prefix="/files", tags=["Files"])
app.include_router(analysis.router, prefix="/analyze", tags=["Analysis"])
app.include_router(ai.router, prefix="/ai", tags=["AI"])


@app.get("/")
def root():
    """Serve the dashboard UI."""
    index_path = static_path / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": "Mobile Media Organizer API is running. Visit /docs for Swagger UI."}


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.app_env,
    }
