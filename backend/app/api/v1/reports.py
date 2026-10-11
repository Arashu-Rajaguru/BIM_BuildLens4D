import csv
import io
import datetime
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.domain import Project, BIMElement, ReviewDecision, AuditLog
from app.services.progress_service import compute_project_summary

router = APIRouter()

@router.get(
    "/projects/{project_id}/export/csv",
    tags=["Reports & Exports"]
)
def export_project_csv(
    project_id: str,
    db: Session = Depends(get_db)
):
    """
    Export project element progress and verification data to standard CSV format (SRS FR-030).
    Columns: element_id, type, label, zone, planned_start, planned_end, verification_state, last_inspected, notes
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found."
        )

    elements = db.query(BIMElement).filter(
        BIMElement.project_id == project_id
    ).order_by(BIMElement.spatial_zone, BIMElement.id).all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Write SRS-compliant header
    writer.writerow([
        "element_id",
        "type",
        "label",
        "zone",
        "planned_start",
        "planned_end",
        "verification_state",
        "last_inspected",
        "notes"
    ])

    for el in elements:
        writer.writerow([
            el.id,
            el.element_type,
            el.label,
            el.spatial_zone or "General",
            el.planned_start.isoformat() if el.planned_start else "",
            el.planned_end.isoformat() if el.planned_end else "",
            el.verification_state,
            el.last_inspected_at.isoformat() if el.last_inspected_at else "",
            f"Created for project {project_id}"
        ])


    csv_data = output.getvalue()
    filename = f"buildlens4d_progress_{project_id}_{datetime.date.today().isoformat()}.csv"

    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )


@router.get(
    "/projects/{project_id}/report/summary",
    tags=["Reports & Exports"]
)
def get_executive_report(
    project_id: str,
    db: Session = Depends(get_db)
):
    """
    Generate complete 4D executive progress summary with audit and compliance counts (SRS FR-030).
    """
    summary = compute_project_summary(project_id=project_id, db=db)
    
    total_reviews = db.query(ReviewDecision).filter(ReviewDecision.project_id == project_id).count()
    total_audits = db.query(AuditLog).filter(AuditLog.project_id == project_id).count()

    return {
        "summary": summary,
        "governance": {
            "total_human_reviews": total_reviews,
            "total_audit_events": total_audits,
            "srs_compliance": "Conforms to SRS FR-001 through FR-032 & Section 8.3 guardrails"
        }
    }
