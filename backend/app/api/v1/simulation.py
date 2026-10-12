import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.domain import Project, BIMElement

router = APIRouter()

@router.get(
    "/projects/{project_id}/simulation",
    tags=["4D Time Scrubber & Simulation"]
)
def simulate_4d_progress_at_date(
    project_id: str,
    target_date: Optional[str] = Query(None, description="Target simulation date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    4D Time-Lapse Schedule Scrubber API (SRS Section 4 / 4D Engine).
    Computes exact construction state and completion percentage across past, present,
    and future scheduled dates.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project '{project_id}' not found.")

    if target_date:
        try:
            sim_date = datetime.date.fromisoformat(target_date)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid date format. Expected YYYY-MM-DD.")
    else:
        sim_date = datetime.date(2026, 10, 12)

    elements = db.query(BIMElement).filter(BIMElement.project_id == project_id).all()
    
    simulated_items = []
    completed_count = 0
    in_progress_count = 0
    not_started_count = 0
    total_progress_accum = 0.0

    for el in elements:
        start_d = el.planned_start
        end_d = el.planned_end

        if sim_date < start_d:
            sim_state = "not_started"
            progress_pct = 0.0
            not_started_count += 1
        elif start_d <= sim_date <= end_d:
            sim_state = "in_progress"
            total_days = max(1, (end_d - start_d).days)
            elapsed_days = max(1, (sim_date - start_d).days)
            progress_pct = min(99.0, round((elapsed_days / total_days) * 100.0, 1))
            in_progress_count += 1
        else:
            sim_state = "verified_complete"
            progress_pct = 100.0
            completed_count += 1

        total_progress_accum += progress_pct

        simulated_items.append({
            "id": el.id,
            "label": el.label,
            "element_type": el.element_type,
            "spatial_zone": el.spatial_zone or "General",
            "planned_start": start_d.isoformat(),
            "planned_end": end_d.isoformat(),
            "simulated_state": sim_state,
            "simulated_progress_percentage": progress_pct,
            "is_active_on_date": (start_d <= sim_date <= end_d)
        })

    total = len(elements)
    weighted_progress = round((total_progress_accum / total), 1) if total > 0 else 0.0
    discrete_progress = round((completed_count / total * 100.0), 1) if total > 0 else 0.0

    return {
        "project_id": project_id,
        "simulated_date": sim_date.isoformat(),
        "total_elements": total,
        "completed_elements": completed_count,
        "in_progress_elements": in_progress_count,
        "not_started_elements": not_started_count,
        "simulated_completion_percentage": weighted_progress,
        "discrete_completion_percentage": discrete_progress,
        "elements": simulated_items
    }
