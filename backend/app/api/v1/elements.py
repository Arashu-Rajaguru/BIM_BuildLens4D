from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.domain import Project, BIMElement
from app.schemas.schemas import BIMElementCreate, BIMElementResponse

router = APIRouter()

@router.get("/projects/{project_id}/elements", response_model=List[BIMElementResponse], tags=["BIM Elements"])
def list_elements(
    project_id: str,
    verification_state: Optional[str] = Query(None, description="Filter by status: verified_complete, in_progress, potentially_delayed, ahead_of_schedule, needs_manual_review, not_started"),
    element_type: Optional[str] = Query(None, description="Filter by element type: Column, Beam, Slab, Wall, Footing"),
    db: Session = Depends(get_db)
):
    """Retrieve BIM elements belonging to a project, with optional filtering."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found."
        )

    query = db.query(BIMElement).filter(BIMElement.project_id == project_id)
    if verification_state:
        query = query.filter(BIMElement.verification_state == verification_state)
    if element_type:
        query = query.filter(BIMElement.element_type == element_type)

    elements = query.order_by(BIMElement.planned_start.asc(), BIMElement.id.asc()).all()
    return elements

@router.post("/projects/{project_id}/elements", response_model=BIMElementResponse, status_code=status.HTTP_201_CREATED, tags=["BIM Elements"])
def create_element(project_id: str, payload: BIMElementCreate, db: Session = Depends(get_db)):
    """Register a new BIM element with planned start/end schedule dates."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found."
        )

    existing = db.query(BIMElement).filter(
        BIMElement.project_id == project_id,
        BIMElement.id == payload.id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Element '{payload.id}' already exists in project '{project_id}'."
        )

    element = BIMElement(
        id=payload.id,
        project_id=project_id,
        element_type=payload.element_type,
        label=payload.label,
        spatial_zone=payload.spatial_zone,
        model_version_id=payload.model_version_id,
        planned_start=payload.planned_start,
        planned_end=payload.planned_end,
        verification_state=payload.verification_state
    )
    db.add(element)
    db.commit()
    db.refresh(element)
    return element

@router.get("/projects/{project_id}/elements/{element_id}", response_model=BIMElementResponse, tags=["BIM Elements"])
def get_element(project_id: str, element_id: str, db: Session = Depends(get_db)):
    """Retrieve a single BIM element by ID."""
    element = db.query(BIMElement).filter(
        BIMElement.project_id == project_id,
        BIMElement.id == element_id
    ).first()
    if not element:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Element '{element_id}' not found in project '{project_id}'."
        )
    return element
