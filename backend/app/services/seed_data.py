import datetime
from sqlalchemy.orm import Session
from app.models.domain import Project, BIMElement, ProgressObservation, EvidenceRecord
from app.services.progress_service import evaluate_element_schedule_state

def seed_initial_data(db: Session):
    """
    Populates the database with realistic sample construction data
    if the database is currently empty.
    """
    existing_project = db.query(Project).first()
    if existing_project:
        return  # Data already seeded

    # 1. Project
    project = Project(
        id="proj-terminal-04",
        name="Metro Station Box - Terminal 4",
        description="Subsurface reinforced concrete concourse and track-level platform structure.",
        location="Zone 3, Central Transit Hub",
        timezone="UTC",
        lifecycle_state="active"
    )
    db.add(project)
    db.commit()

    # 2. BIM Elements with 4D schedule windows
    today = datetime.date(2026, 10, 9)
    
    raw_elements = [
        {
            "id": "COL-B1-01",
            "element_type": "Column",
            "label": "Track Level Heavy Column Grid A1",
            "spatial_zone": "Concourse Level / Grid A-1",
            "planned_start": datetime.date(2026, 9, 1),
            "planned_end": datetime.date(2026, 9, 20),
            "obs_state": "accepted_complete",
            "obs_date": datetime.date(2026, 9, 18),
            "confidence": 0.98,
            "notes": "Reinforcement rebar inspected and certified; concrete pour finished and cured.",
            "evidence_url": "mock_evidence/col_b1_01_complete.jpg"
        },
        {
            "id": "COL-B1-02",
            "element_type": "Column",
            "label": "Track Level Heavy Column Grid A2",
            "spatial_zone": "Concourse Level / Grid A-2",
            "planned_start": datetime.date(2026, 9, 5),
            "planned_end": datetime.date(2026, 9, 25),
            "obs_state": "accepted_complete",
            "obs_date": datetime.date(2026, 9, 22),
            "confidence": 0.95,
            "notes": "Cylindrical column cast in-situ. Ultrasonic testing passed.",
            "evidence_url": "mock_evidence/col_b1_02_complete.jpg"
        },
        {
            "id": "COL-B1-03",
            "element_type": "Column",
            "label": "Concourse Central Pillar Grid B1",
            "spatial_zone": "Concourse Level / Grid B-1",
            "planned_start": datetime.date(2026, 9, 15),
            "planned_end": datetime.date(2026, 10, 2),  # Planned end has passed!
            "obs_state": "in_progress",
            "obs_date": datetime.date(2026, 10, 8),
            "confidence": 0.88,
            "notes": "Formwork 75% complete; rebar cage partially assembled. Delayed due to rebar delivery wait.",
            "evidence_url": "mock_evidence/col_b1_03_delayed.jpg"
        },
        {
            "id": "BM-L1-01",
            "element_type": "Beam",
            "label": "Longitudinal Transfer Beam Grid A1-A2",
            "spatial_zone": "Mezzanine Level / Spans A1-A2",
            "planned_start": datetime.date(2026, 9, 25),
            "planned_end": datetime.date(2026, 10, 15),
            "obs_state": "in_progress",
            "obs_date": datetime.date(2026, 10, 7),
            "confidence": 0.92,
            "notes": "Falsework scaffolding erected; post-tensioning ducts placed.",
            "evidence_url": "mock_evidence/bm_l1_01_progress.jpg"
        },
        {
            "id": "SLB-L1-01",
            "element_type": "Slab",
            "label": "Ticket Hall Suspended Slab Bay 1",
            "spatial_zone": "Ticket Hall Level / Bay 1",
            "planned_start": datetime.date(2026, 10, 5),
            "planned_end": datetime.date(2026, 10, 25),
            "obs_state": "in_progress",
            "obs_date": datetime.date(2026, 10, 8),
            "confidence": 0.89,
            "notes": "Decking panels installed. Mesh reinforcement laying in progress.",
            "evidence_url": "mock_evidence/slb_l1_01_decking.jpg"
        },
        {
            "id": "WL-RET-01",
            "element_type": "Wall",
            "label": "Perimeter Diaphragm Retaining Wall North",
            "spatial_zone": "Perimeter North / Shoring Line",
            "planned_start": datetime.date(2026, 8, 15),
            "planned_end": datetime.date(2026, 9, 10),
            "obs_state": "accepted_complete",
            "obs_date": datetime.date(2026, 9, 8),
            "confidence": 0.99,
            "notes": "Guide walls and panel slurries completed and grouted.",
            "evidence_url": "mock_evidence/wl_ret_01_complete.jpg"
        },
        {
            "id": "BM-L1-02",
            "element_type": "Beam",
            "label": "Transverse Header Beam Grid B1-B2",
            "spatial_zone": "Mezzanine Level / Spans B1-B2",
            "planned_start": datetime.date(2026, 9, 28),
            "planned_end": datetime.date(2026, 10, 12),
            "obs_state": "occluded",
            "obs_date": datetime.date(2026, 10, 8),
            "confidence": 0.40,
            "notes": "Field camera obstructed by mobile crane arm and safety safety netting. Cannot confirm beam seating.",
            "evidence_url": "mock_evidence/bm_l1_02_occluded.jpg"
        },
        {
            "id": "FTG-P1-01",
            "element_type": "Footing",
            "label": "Deep Pile Cap Foundation P1",
            "spatial_zone": "Sub-foundation Level / Pier 1",
            "planned_start": datetime.date(2026, 10, 18),
            "planned_end": datetime.date(2026, 11, 5),
            "obs_state": None,
            "obs_date": None,
            "confidence": 0.0,
            "notes": None,
            "evidence_url": None
        }
    ]

    for item in raw_elements:
        element = BIMElement(
            id=item["id"],
            project_id=project.id,
            element_type=item["element_type"],
            label=item["label"],
            spatial_zone=item["spatial_zone"],
            model_version_id="v1.0",
            planned_start=item["planned_start"],
            planned_end=item["planned_end"],
            verification_state="not_started"
        )
        db.add(element)
        db.flush()

        obs = None
        if item["obs_state"]:
            obs_dt = datetime.datetime.combine(item["obs_date"], datetime.time(10, 30), tzinfo=datetime.timezone.utc)
            obs = ProgressObservation(
                id=f"obs-{item['id'].lower()}-01",
                project_id=project.id,
                element_id=element.id,
                observer_id="eng_sarah_01",
                reported_state=item["obs_state"],
                confidence_score=item["confidence"],
                notes=item["notes"],
                review_state="approved" if item["obs_state"] == "accepted_complete" else "pending_review",
                captured_at=obs_dt
            )
            db.add(obs)
            db.flush()

            if item["evidence_url"]:
                evidence = EvidenceRecord(
                    id=f"evi-{item['id'].lower()}-01",
                    observation_id=obs.id,
                    media_type="image/jpeg",
                    media_url=item["evidence_url"],
                    captured_at=obs_dt
                )
                db.add(evidence)

        # Run business logic to evaluate verification_state
        state, note = evaluate_element_schedule_state(element, obs, evaluation_date=today)
        element.verification_state = state
        if obs:
            element.last_inspected_at = obs.captured_at

    db.commit()
