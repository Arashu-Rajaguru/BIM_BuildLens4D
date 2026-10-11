import os
import uuid
import hashlib
import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.domain import Project, BIMElement, ProgressObservation, EvidenceRecord, AuditLog
from app.schemas.schemas import EvidenceRecordResponse

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post(
    "/projects/{project_id}/elements/{element_id}/evidence",
    response_model=EvidenceRecordResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Evidence Gallery & Uploads"]
)
async def upload_element_evidence(
    project_id: str,
    element_id: str,
    file: UploadFile = File(...),
    observer_id: str = Form("eng_field_01"),
    reported_state: str = Form("in_progress"),
    notes: Optional[str] = Form("Site photographic evidence captured via AR inspector"),
    camera_pose_json: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Upload on-site inspection photo and attach it as immutable evidence to a BIM element.
    Saves file to static /uploads server, records SHA-256 hash, and updates element inspection date.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project '{project_id}' not found.")

    element = db.query(BIMElement).filter(
        BIMElement.project_id == project_id,
        BIMElement.id == element_id
    ).first()
    if not element:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"BIM element '{element_id}' not found.")

    # Read and save file
    content = await file.read()
    file_hash = hashlib.sha256(content).hexdigest()
    
    unique_suffix = uuid.uuid4().hex[:10]
    safe_name = file.filename.replace(" ", "_") if file.filename else "evidence.jpg"
    filename = f"{unique_suffix}_{safe_name}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as f:
        f.write(content)

    media_url = f"/uploads/{filename}"
    now = datetime.datetime.now(datetime.timezone.utc)

    # Create parent ProgressObservation
    obs_id = f"obs-{uuid.uuid4().hex[:10]}"
    observation = ProgressObservation(
        id=obs_id,
        project_id=project_id,
        element_id=element_id,
        observer_id=observer_id,
        reported_state=reported_state,
        confidence_score=0.95,
        camera_pose_json=camera_pose_json or '{"pos":[0.0, 1.5, -4.0], "rot":[0, 0, 0, 1]}',
        notes=notes,
        review_state="verified" if reported_state == "accepted_complete" else "pending_review",
        captured_at=now
    )
    db.add(observation)
    db.flush()

    # Create EvidenceRecord
    evi_id = f"evi-{uuid.uuid4().hex[:10]}"
    evidence = EvidenceRecord(
        id=evi_id,
        observation_id=obs_id,
        media_type=file.content_type or "image/jpeg",
        media_url=media_url,
        file_hash=file_hash,
        metadata_json=f'{{"original_name":"{safe_name}", "filesize":{len(content)}}}',
        captured_at=now
    )
    db.add(evidence)

    # Update element state and inspection date
    if reported_state in ("verified_complete", "accepted_complete"):
        element.verification_state = "verified_complete"
    elif reported_state in ("in_progress", "potentially_delayed", "needs_manual_review"):
        element.verification_state = reported_state
    element.last_inspected_at = now

    # Emit Audit Log
    audit = AuditLog(
        id=f"aud-{uuid.uuid4().hex[:10]}",
        project_id=project_id,
        entity_type="evidence",
        entity_id=element_id,
        action="evidence_uploaded",
        actor_id=observer_id,
        details_json=f'{{"filename":"{safe_name}", "hash":"{file_hash[:12]}...", "state":"{element.verification_state}"}}',
        created_at=now
    )
    db.add(audit)

    db.commit()
    db.refresh(evidence)
    return evidence


@router.get(
    "/projects/{project_id}/elements/{element_id}/evidence",
    response_model=List[EvidenceRecordResponse],
    tags=["Evidence Gallery & Uploads"]
)
def list_element_evidence(
    project_id: str,
    element_id: str,
    db: Session = Depends(get_db)
):
    """Retrieve all uploaded photographic evidence and inspection media for a BIM element."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project '{project_id}' not found.")

    element = db.query(BIMElement).filter(
        BIMElement.project_id == project_id,
        BIMElement.id == element_id
    ).first()
    if not element:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"BIM element '{element_id}' not found.")

    # Join through ProgressObservation
    evidences = db.query(EvidenceRecord).join(
        ProgressObservation, EvidenceRecord.observation_id == ProgressObservation.id
    ).filter(
        ProgressObservation.project_id == project_id,
        ProgressObservation.element_id == element_id
    ).order_by(EvidenceRecord.captured_at.desc()).all()

    return evidences
