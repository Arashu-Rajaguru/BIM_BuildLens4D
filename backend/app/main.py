import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import Base, engine, SessionLocal
from app.services.seed_data import seed_initial_data
from app.api.v1 import api_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("buildlens4d")

# Ensure database tables exist immediately
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure database schema exists and seed initial data
    logger.info("Initializing database schema...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        seed_initial_data(db)
        logger.info("Database schema initialized and verified.")
    except Exception as e:
        logger.error(f"Error seeding initial database data: {e}")
    finally:
        db.close()
        
    yield
    logger.info("BuildLens 4D API shutting down cleanly.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="4D Augmented Reality Construction Progress Monitoring API linking BIM elements to field observations and schedule milestones.",
    lifespan=lifespan
)

# Configure CORS for React mobile PWA, Unity AR client, and external tunnels
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

import os
from fastapi.staticfiles import StaticFiles

# Mount static files directory for evidence images
upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
os.makedirs(upload_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")

# Include API v1 router under /api
app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount compiled React PWA Mobile App on root for unified hosting
dashboard_dist = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "dashboard",
    "dist"
)
if os.path.exists(dashboard_dist):
    app.mount("/", StaticFiles(directory=dashboard_dist, html=True), name="mobile_app")
else:
    @app.get("/", tags=["Root"])
    def read_root():
        return {
            "system": "BuildLens 4D API",
            "version": settings.VERSION,
            "docs_url": "/docs",
            "health_url": f"{settings.API_V1_STR}/health",
            "description": "Mobile AR & 4D BIM progress monitoring backend."
        }


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred in BuildLens 4D backend."}
    )
