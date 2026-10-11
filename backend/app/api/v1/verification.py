import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Response, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.domain import Project, VerificationReport
from app.schemas.schemas import ImageVerificationResponse
from app.services.image_verifier import verify_building_image_or_plan, generate_verification_report_html

router = APIRouter()

@router.post(
    "/projects/{project_id}/verify-image",
    response_model=ImageVerificationResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Image & Plan Verification"]
)
async def upload_and_verify_building_image_or_plan(
    project_id: str,
    file: UploadFile = File(...),
    plan_type: str = Form("site_photo"), # 'site_photo', 'floor_plan', 'structural_drawing', 'drone_capture'
    target_zone: Optional[str] = Form("ALL"),
    target_element_id: Optional[str] = Form(None),
    observer_id: str = Form("eng_field_01"),
    db: Session = Depends(get_db)
):
    """
    Upload a real-world building image, site photo, or 2D floor plan / CAD drawing,
    verify visible structural components against the 4D BIM digital twin,
    and generate an automated compliance verification report (SRS FR-026, FR-027, FR-030).
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found."
        )

    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty."
        )

    result = verify_building_image_or_plan(
        project_id=project_id,
        file_bytes=file_bytes,
        original_filename=file.filename or "building_capture.jpg",
        content_type=file.content_type or "image/jpeg",
        plan_type=plan_type,
        target_zone=target_zone,
        target_element_id=target_element_id,
        observer_id=observer_id,
        db=db
    )

    return result


@router.get(
    "/projects/{project_id}/verification-reports",
    tags=["Image & Plan Verification"]
)
def list_verification_reports(
    project_id: str,
    db: Session = Depends(get_db)
):
    """Retrieve history of all automated image & building plan verification reports."""
    reports = db.query(VerificationReport).filter(
        VerificationReport.project_id == project_id
    ).order_by(VerificationReport.created_at.desc()).all()

    return [
        {
            "id": r.id,
            "project_id": r.project_id,
            "plan_type": r.plan_type,
            "media_url": r.media_url,
            "file_hash": r.file_hash,
            "compliance_percentage": r.compliance_percentage,
            "overall_verdict": r.overall_verdict,
            "requires_human_review": r.requires_human_review == "true",
            "created_at": r.created_at.isoformat(),
            "report_url": f"/api/projects/{project_id}/reports/verification/{r.id}/html"
        }
        for r in reports
    ]


@router.api_route(
    "/projects/{project_id}/reports/verification/{report_id}/html",
    methods=["GET", "HEAD"],
    tags=["Image & Plan Verification"]
)
def get_verification_report_html_page(
    project_id: str,
    report_id: str,
    db: Session = Depends(get_db)
):
    """
    Render and download printable executive HTML/PDF inspection report
    complete with BuildLens 4D letterhead, cryptographic hash, bounding boxes, and sign-offs.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    report = db.query(VerificationReport).filter(
        VerificationReport.project_id == project_id,
        VerificationReport.id == report_id
    ).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Verification report not found.")

    html_content = generate_verification_report_html(report, project)
    return Response(content=html_content, media_type="text/html")


@router.get(
    "/projects/{project_id}/reports/verification/{report_id}",
    tags=["Image & Plan Verification"]
)
def get_verification_report_json(
    project_id: str,
    report_id: str,
    db: Session = Depends(get_db)
):
    """Retrieve structured JSON data for an image verification report."""
    report = db.query(VerificationReport).filter(
        VerificationReport.project_id == project_id,
        VerificationReport.id == report_id
    ).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Verification report not found.")

    return {
        "id": report.id,
        "project_id": report.project_id,
        "plan_type": report.plan_type,
        "media_url": report.media_url,
        "file_hash": report.file_hash,
        "metadata": json.loads(report.metadata_json or "{}"),
        "compliance_percentage": report.compliance_percentage,
        "overall_verdict": report.overall_verdict,
        "requires_human_review": report.requires_human_review == "true",
        "elements": json.loads(report.results_json or "[]"),
        "created_at": report.created_at.isoformat(),
        "report_url": f"/api/projects/{project_id}/reports/verification/{report.id}/html"
    }
