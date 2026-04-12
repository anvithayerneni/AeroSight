"""
AeroSight FastAPI Main Application Entrypoint
"""

import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.config import settings
from backend.api.v1.health import router as health_router
from backend.api.v1.flights import router as flights_router
from backend.api.v1.airports import router as airports_router
from backend.api.v1.airlines import router as airlines_router
from backend.api.v1.routes import router as routes_router
from backend.api.v1.analytics import router as analytics_router
from backend.api.v1.ml import router as ml_router
from backend.api.v1.streaming import router as streaming_router
from backend.api.v1.reports import router as reports_router

app = FastAPI(
    title="AeroSight API",
    description="End-to-End Airline Operations Intelligence & Data Platform API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for local development and live preview
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "InternalServerError", "detail": str(exc), "path": request.url.path}
    )

# Mount API Routers
app.include_router(health_router, prefix=settings.api_prefix)
app.include_router(flights_router, prefix=settings.api_prefix)
app.include_router(airports_router, prefix=settings.api_prefix)
app.include_router(airlines_router, prefix=settings.api_prefix)
app.include_router(routes_router, prefix=settings.api_prefix)
app.include_router(analytics_router, prefix=settings.api_prefix)
app.include_router(ml_router, prefix=settings.api_prefix)
app.include_router(streaming_router, prefix=settings.api_prefix)
app.include_router(reports_router, prefix=settings.api_prefix)

# Mount Frontend SPA if built
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "dist")
if os.path.exists(frontend_dist):
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse
    
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")
    
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("redoc") or full_path.startswith("openapi.json"):
            return JSONResponse(status_code=404, content={"detail": "Not Found"})
        index_file = os.path.join(frontend_dist, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return JSONResponse(status_code=404, content={"detail": "Frontend build not found"})
else:
    @app.get("/", tags=["Root"])
    def root():
        return {
            "name": "AeroSight — Airline Operations Intelligence Platform",
            "docs": "/docs",
            "health": "/api/health",
            "version": "1.0.0"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
