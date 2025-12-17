"""FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from . import datasets, executors, judges, results, runs, scenarios, streaming

app = FastAPI(title="VibeLab API", version="0.0.1")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(scenarios.router, prefix="/api/scenarios", tags=["scenarios"])
app.include_router(results.router, prefix="/api/results", tags=["results"])
app.include_router(runs.router, prefix="/api/runs", tags=["runs"])
app.include_router(executors.router, prefix="/api/executors", tags=["executors"])
app.include_router(streaming.router, prefix="/api/results", tags=["streaming"])
app.include_router(datasets.router, prefix="/api/datasets", tags=["datasets"])
app.include_router(judges.router, prefix="/api/judges", tags=["judges"])

# Serve static files (React app)
try:
    from pathlib import Path

    # Try to find static files in the installed package
    # When installed via build hook, files are at vibelab/web/dist
    package_dir = Path(__file__).parent.parent
    static_dir = package_dir / "web" / "dist"
    
    # If not found in package, try relative to source (development)
    if not static_dir.exists():
        static_dir = Path(__file__).parent.parent.parent.parent / "web" / "dist"
    
    if static_dir.exists():
        app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
except Exception:
    pass  # Static files not available


@app.get("/api/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}
