import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.domain import Project, BIMElement
from app.schemas.schemas import (
    ProjectCreate,
    ProjectResponse,
    ProjectSummaryResponse
)

router = APIRouter()

@router.get("/projects", response_model=List[ProjectResponse], tags=["Projects"])
def list_projects(db: Session = Depends(get_db)):
    """Retrieve all monitored construction projects."""
    projects = db.query(Project).order_by(Project.created_at.desc()).all()
    return projects

@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED, tags=["Projects"])
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    """Register a new construction project."""
    existing = db.query(Project).filter(Project.id == payload.id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Project with ID '{payload.id}' already exists."
        )

    project = Project(
        id=payload.id,
        name=payload.name,
        description=payload.description,
        location=payload.location,
        timezone=payload.timezone,
        lifecycle_state=payload.lifecycle_state
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

@router.get("/projects/{project_id}", response_model=ProjectResponse, tags=["Projects"])
def get_project(project_id: str, db: Session = Depends(get_db)):
    """Retrieve a specific project by ID."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found."
        )
    return project

from app.services.progress_service import compute_project_summary

@router.get("/projects/{project_id}/summary", response_model=ProjectSummaryResponse, tags=["Projects"])
def get_project_summary(project_id: str, db: Session = Depends(get_db)):
    """
    Compute 4D progress summary statistics for a project:
    - Total elements
    - Element count breakdown by verification state
    - Schedule-aware completion percentage
    """
    summary = compute_project_summary(project_id=project_id, db=db)
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found."
        )
    return summary

