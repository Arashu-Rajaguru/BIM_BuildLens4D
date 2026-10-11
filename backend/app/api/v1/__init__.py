from fastapi import APIRouter
from app.api.v1 import health, projects, elements, observations, reviews, vision, reports, evidence, simulation, markers, verification

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(projects.router)
api_router.include_router(elements.router)
api_router.include_router(observations.router)
api_router.include_router(reviews.router)
api_router.include_router(vision.router)
api_router.include_router(reports.router)
api_router.include_router(evidence.router)
api_router.include_router(simulation.router)
api_router.include_router(markers.router)
api_router.include_router(verification.router)



