import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.domain import Project, BIMElement
from app.schemas.schemas import CVDetectRequest, CVDetectResponse, CVProposal

router = APIRouter()

@router.post(
    "/projects/{project_id}/cv-detect",
    response_model=CVDetectResponse,
    tags=["Computer Vision Assistance"]
)
def run_cv_detection(
    project_id: str,
    payload: CVDetectRequest,
    db: Session = Depends(get_db)
):
    """
    Execute AI Computer Vision element detection & matching (SRS FR-026, FR-027).
    Enforces SRS 8.3 Guardrails:
    - CV proposals are strictly assistive and never autonomously approve completions.
    - Low confidence (< 0.60) or occluded viewpoints trigger mandatory human review.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found."
        )

    target_element_id = payload.simulated_element_id or "BM-L1-02"
    element = db.query(BIMElement).filter(
        BIMElement.project_id == project_id,
        BIMElement.id == target_element_id
    ).first()

    if not element:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target BIM element '{target_element_id}' not found in project '{project_id}'."
        )

    confidence = payload.simulated_confidence if payload.simulated_confidence is not None else 0.55
    is_occluded = payload.simulated_occlusion if payload.simulated_occlusion is not None else True

    # Guardrail evaluation (SRS 8.3)
    requires_human_review = confidence < 0.60 or is_occluded
    
    if confidence >= 0.75 and not is_occluded:
        proposed_state = "detected_installed"
        guardrail_note = "High-confidence detection. Proposal matches design geometry."
        explanation = "Object detected with high visual fidelity. Human sign-off recommended before marking verified."
    elif confidence >= 0.50:
        proposed_state = "needs_manual_review" if is_occluded else "partially_detected"
        guardrail_note = (
            "Occlusion detected (scaffolding/equipment)" if is_occluded 
            else "Moderate confidence. Visual confirmation warranted."
        )
        explanation = (
            "Observation exhibits visual occlusion or borderline confidence (<0.60). "
            "Flagged for BIM Coordinator / Field Inspector review in accordance with SRS 8.3."
        )
    else:
        proposed_state = "unverified"
        guardrail_note = "Low confidence detection (<0.50). Potential false positive."
        explanation = "Confidence below operational threshold. Inspector manual rescan advised."

    # Simulated bounding box [x, y, width, height] normalized in camera frame
    bbox = [0.24, 0.38, 0.52, 0.28]

    proposal = CVProposal(
        element_id=element.id,
        visual_state_proposed=proposed_state,
        confidence_score=round(confidence, 2),
        is_occluded=is_occluded,
        bounding_box=bbox,
        is_suggestion=True,
        guardrail_note=guardrail_note
    )

    return CVDetectResponse(
        status="success",
        proposals=[proposal],
        requires_human_review=requires_human_review,
        explanation=explanation
    )
