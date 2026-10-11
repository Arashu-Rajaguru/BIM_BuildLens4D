import datetime
from typing import Tuple
from app.models.domain import BIMElement, ProgressObservation

def evaluate_element_schedule_state(
    element: BIMElement,
    latest_observation: ProgressObservation = None,
    evaluation_date: datetime.date = None
) -> Tuple[str, str]:
    """
    Core business rule engine implementing SRS Section 8.1:
    Separates observation / field evidence state from 4D schedule interpretation.

    AR alignment or an object detector alone is NEVER treated as proof that an element is complete.
    If an element is hidden, occluded, or uncertain, mark it as 'needs_manual_review'
    rather than declaring it missing or incomplete.

    Returns:
        (verification_state, reasoning_note)
    """
    if evaluation_date is None:
        evaluation_date = datetime.date.today()

    # Case 1: No site observation has ever been logged
    if latest_observation is None:
        if evaluation_date < element.planned_start:
            return "not_started", "Within planned pre-construction window; no field evidence logged yet."
        elif evaluation_date > element.planned_end:
            return "potentially_delayed", "Past planned completion date without verified completion evidence."
        else:
            return "in_progress", "Planned construction in progress; awaiting field evidence verification."

    reported = latest_observation.reported_state
    obs_date = latest_observation.captured_at.date() if isinstance(latest_observation.captured_at, datetime.datetime) else latest_observation.captured_at

    # Case 2: Occluded, low-confidence, or uncertain observation
    if reported in ("occluded", "uncertain") or latest_observation.confidence_score < 0.6:
        return "needs_manual_review", (
            f"Observation recorded as '{reported}' with confidence {latest_observation.confidence_score:.2f}. "
            "Site inspection or clear line-of-sight required before status declaration."
        )

    # Case 3: Accepted Complete
    if reported == "accepted_complete":
        if obs_date < element.planned_start:
            return "ahead_of_schedule", f"Completed ahead of planned start date ({element.planned_start})."
        elif obs_date <= element.planned_end:
            return "verified_complete", f"Verified complete within planned schedule (ended {obs_date} <= {element.planned_end})."
        else:
            return "verified_complete", f"Verified complete, finished late on {obs_date} (planned {element.planned_end})."

    # Case 4: In Progress
    if reported == "in_progress":
        if evaluation_date > element.planned_end:
            return "potentially_delayed", f"Element currently in progress but past planned completion date ({element.planned_end})."
        else:
            return "in_progress", "Element actively under construction and within schedule parameters."

    # Case 5: Not Started
    if reported == "not_started":
        if evaluation_date > element.planned_end:
            return "potentially_delayed", f"Field confirmed not started; milestone past planned end date ({element.planned_end})."
        elif evaluation_date > element.planned_start:
            return "needs_manual_review", f"Field confirmed not started, but planned start date ({element.planned_start}) has elapsed."
        else:
            return "not_started", "Confirmed not started; planned start date is in the future."

    return "needs_manual_review", f"Unrecognized reported state: {reported}"


def compute_project_summary(project_id: str, db):
    """
    Compute project progress counts and completion percentage (SRS Section 4 / FR-028).
    """
    from app.models.domain import Project, BIMElement
    from app.schemas.schemas import ProjectSummaryResponse

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return None

    elements = db.query(BIMElement).filter(BIMElement.project_id == project_id).all()
    total = len(elements)

    counts = {
        "verified_complete": 0,
        "in_progress": 0,
        "potentially_delayed": 0,
        "ahead_of_schedule": 0,
        "needs_manual_review": 0,
        "not_started": 0
    }

    for el in elements:
        state = el.verification_state or "not_started"
        if state in counts:
            counts[state] += 1
        else:
            counts["needs_manual_review"] += 1

    completion_percentage = (
        ((counts["verified_complete"] + counts["ahead_of_schedule"]) / total * 100.0)
        if total > 0 else 0.0
    )

    return ProjectSummaryResponse(
        project_id=project.id,
        project_name=project.name,
        total_elements=total,
        verified_complete=counts["verified_complete"],
        in_progress=counts["in_progress"],
        potentially_delayed=counts["potentially_delayed"],
        ahead_of_schedule=counts["ahead_of_schedule"],
        needs_manual_review=counts["needs_manual_review"],
        not_started=counts["not_started"],
        completion_percentage=round(completion_percentage, 1),
        computed_at=datetime.datetime.now(datetime.timezone.utc)
    )

