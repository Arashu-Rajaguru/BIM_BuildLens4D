import datetime
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.schemas.schemas import HealthResponse

router = APIRouter()

@router.get("/health", response_model=HealthResponse, tags=["Health"])
def get_health(db: Session = Depends(get_db)):
    """
    Health check endpoint returning system operational status,
    API version, database connectivity, and UTC timestamp.
    """
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return HealthResponse(
        status="ok" if "unhealthy" not in db_status else "degraded",
        version=settings.VERSION,
        database=db_status,
        environment=settings.ENVIRONMENT,
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )
