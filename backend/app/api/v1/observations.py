import uuid
import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.domain import Project, BIMElement, ProgressObservation, EvidenceRecord
from app.schemas.schemas import (
    ProgressObservationCreate,
    ProgressObservationResponse
)
from app.services.progress_service import evaluate_element_schedule_state

router = APIRouter()

@router.post(
    "/projects/{project_id}/observations",
    response_model=ProgressObservationResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Progress Observations"]
)
def record_observation(
    project_id: str,
    payload: ProgressObservationCreate,
    db: Session = Depends(get_db)
):
    """
    Record a new field progress observation captured via Mobile AR or site inspection.
    Updates the target BIM element's verification state in accordance with
    4D schedule business rules (SRS 8.1).
    """
    # 1. Validate project and element existence
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found."
        )

    element = db.query(BIMElement).filter(
        BIMElement.project_id == project_id,
        BIMElement.id == payload.element_id
    ).first()
    if not element:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"BIM element '{payload.element_id}' does not exist in project '{project_id}'."
        )

    # 2. Create ProgressObservation record
    obs_id = f"obs-{uuid.uuid4().hex[:12]}"
    obs_time = payload.captured_at or datetime.datetime.now(datetime.timezone.utc)

    observation = ProgressObservation(
        id=obs_id,
        project_id=project_id,
        element_id=payload.element_id,
        observer_id=payload.observer_id,
        reported_state=payload.reported_state,
        confidence_score=payload.confidence_score,
        camera_pose_json=payload.camera_pose_json,
        notes=payload.notes,
        review_state=payload.review_state,
        captured_at=obs_time
    )
    db.add(observation)
    db.flush()

    # 3. Store attached evidence records if provided
    if payload.evidence:
        for idx, evi in enumerate(payload.evidence):
            evi_id = f"evi-{uuid.uuid4().hex[:12]}"
            evidence = EvidenceRecord(
                id=evi_id,
                observation_id=obs_id,
                media_type=evi.media_type,
                media_url=evi.media_url,
                file_hash=evi.file_hash,
                metadata_json=evi.metadata_json,
                captured_at=evi.captured_at or obs_time
            )
            db.add(evidence)

    # 4. Evaluate and update element 4D verification state
    new_state, reason = evaluate_element_schedule_state(
        element=element,
        latest_observation=observation,
        evaluation_date=obs_time.date()
    )
    element.verification_state = new_state
    element.last_inspected_at = obs_time

    db.commit()
    db.refresh(observation)
    return observation


@router.get(
    "/projects/{project_id}/observations",
    response_model=List[ProgressObservationResponse],
    tags=["Progress Observations"]
)
def list_observations(
    project_id: str,
    element_id: Optional[str] = Query(None, description="Filter observations by stable BIM element ID"),
    db: Session = Depends(get_db)
):
    """Retrieve historical observations and evidence for a project or specific element."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found."
        )

    query = db.query(ProgressObservation).filter(ProgressObservation.project_id == project_id)
    if element_id:
        query = query.filter(ProgressObservation.element_id == element_id)

    observations = query.order_by(ProgressObservation.captured_at.desc()).all()
    return observations
