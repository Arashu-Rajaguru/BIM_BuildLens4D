import uuid
import json
import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.domain import Project, BIMElement, ProgressObservation, ReviewDecision, AuditLog
from app.schemas.schemas import ReviewDecisionCreate, ReviewDecisionResponse, AuditLogResponse

router = APIRouter()

@router.post(
    "/projects/{project_id}/reviews",
    response_model=ReviewDecisionResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Human Review & Auditing"]
)
def record_review_decision(
    project_id: str,
    payload: ReviewDecisionCreate,
    db: Session = Depends(get_db)
):
    """
    Record an auditable human review decision (SRS FR-022, FR-024).
    Resolves elements flagged with 'needs_manual_review' or disputed observations.
    Emits an immutable AuditLog entry (SRS FR-025, SRS 8.1).
    """
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

    valid_decisions = {"confirmed", "rejected", "corrected", "rescan_requested"}
    if payload.decision not in valid_decisions:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid decision '{payload.decision}'. Allowed values: {sorted(list(valid_decisions))}"
        )

    previous_state = element.verification_state
    now = datetime.datetime.now(datetime.timezone.utc)

    # State transition mapping based on human reviewer verdict
    if payload.decision == "confirmed":
        new_state = "verified_complete"
    elif payload.decision == "rejected":
        new_state = "potentially_delayed"
    elif payload.decision == "corrected":
        new_state = "in_progress"
    elif payload.decision == "rescan_requested":
        new_state = "needs_manual_review"
    else:
        new_state = element.verification_state

    element.verification_state = new_state
    element.last_inspected_at = now

    # Record ReviewDecision
    review_id = f"rev-{uuid.uuid4().hex[:10]}"
    review_decision = ReviewDecision(
        id=review_id,
        project_id=project_id,
        element_id=payload.element_id,
        observation_id=payload.observation_id,
        reviewer_id=payload.reviewer_id,
        decision=payload.decision,
        reason=payload.reason,
        decided_at=now
    )
    db.add(review_decision)

    # Record AuditLog
    audit_id = f"aud-{uuid.uuid4().hex[:10]}"
    audit_log = AuditLog(
        id=audit_id,
        project_id=project_id,
        entity_type="element",
        entity_id=payload.element_id,
        action=f"review_{payload.decision}",
        actor_id=payload.reviewer_id,
        details_json=json.dumps({
            "previous_state": previous_state,
            "new_state": new_state,
            "decision": payload.decision,
            "reason": payload.reason,
            "observation_id": payload.observation_id
        }),
        created_at=now
    )
    db.add(audit_log)

    db.commit()
    db.refresh(review_decision)
    return review_decision


@router.get(
    "/projects/{project_id}/reviews",
    response_model=List[ReviewDecisionResponse],
    tags=["Human Review & Auditing"]
)
def list_review_decisions(
    project_id: str,
    element_id: Optional[str] = Query(None, description="Filter review decisions by element ID"),
    db: Session = Depends(get_db)
):
    """Retrieve review decision history for an entire project or specific element (SRS FR-024)."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found."
        )

    query = db.query(ReviewDecision).filter(ReviewDecision.project_id == project_id)
    if element_id:
        query = query.filter(ReviewDecision.element_id == element_id)
    return query.order_by(ReviewDecision.decided_at.desc()).all()


@router.get(
    "/projects/{project_id}/audit-trail",
    response_model=List[AuditLogResponse],
    tags=["Human Review & Auditing"]
)
def get_audit_trail(
    project_id: str,
    entity_type: Optional[str] = Query(None, description="Filter by entity type ('element', 'observation')"),
    db: Session = Depends(get_db)
):
    """Retrieve chronological audit trail of all state modifications and decisions (SRS FR-025)."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found."
        )

    query = db.query(AuditLog).filter(AuditLog.project_id == project_id)
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    return query.order_by(AuditLog.created_at.desc()).all()
