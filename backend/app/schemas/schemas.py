import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

# ---------------------------------------------------------------------------
# Health Schema
# ---------------------------------------------------------------------------
class HealthResponse(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "ok"})
    version: str = Field(..., json_schema_extra={"example": "1.0.0"})
    database: str = Field(..., json_schema_extra={"example": "connected"})
    environment: str = Field(..., json_schema_extra={"example": "development"})
    timestamp: datetime.datetime


# ---------------------------------------------------------------------------
# Project Schemas
# ---------------------------------------------------------------------------
class ProjectBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255, json_schema_extra={"example": "Metro Station Box - Terminal 4"})
    description: Optional[str] = Field(None, json_schema_extra={"example": "Subsurface reinforced concrete concourse structure"})
    location: Optional[str] = Field(None, json_schema_extra={"example": "Zone 3, Pier 12"})
    timezone: str = Field("UTC", json_schema_extra={"example": "UTC"})
    lifecycle_state: str = Field("active", json_schema_extra={"example": "active"})

class ProjectCreate(ProjectBase):
    id: str = Field(..., min_length=3, max_length=64, json_schema_extra={"example": "proj-terminal-04"})

class ProjectResponse(ProjectBase):
    id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# BIM Element Schemas
# ---------------------------------------------------------------------------
class BIMElementBase(BaseModel):
    element_type: str = Field(..., json_schema_extra={"example": "Column"})
    label: str = Field(..., json_schema_extra={"example": "Level 1 Structural Column B4"})
    spatial_zone: Optional[str] = Field(None, json_schema_extra={"example": "Grid B-4 / Level 1"})
    model_version_id: str = Field("v1.0", json_schema_extra={"example": "v1.0"})
    planned_start: datetime.date = Field(..., json_schema_extra={"example": "2026-10-01"})
    planned_end: datetime.date = Field(..., json_schema_extra={"example": "2026-10-15"})
    verification_state: str = Field(
        "not_started",
        description="Current verification state (verified_complete, in_progress, potentially_delayed, ahead_of_schedule, needs_manual_review, not_started)",
        json_schema_extra={"example": "not_started"}
    )

class BIMElementCreate(BIMElementBase):
    id: str = Field(..., min_length=2, max_length=64, json_schema_extra={"example": "COL-B1-04"})

class BIMElementResponse(BIMElementBase):
    id: str
    project_id: str
    last_inspected_at: Optional[datetime.datetime] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Evidence Record Schemas
# ---------------------------------------------------------------------------
class EvidenceRecordBase(BaseModel):
    media_type: str = Field("image/jpeg", json_schema_extra={"example": "image/jpeg"})
    media_url: str = Field(..., json_schema_extra={"example": "uploads/evidence_col_b1_04_20261009.jpg"})
    file_hash: Optional[str] = Field(None, json_schema_extra={"example": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"})
    metadata_json: Optional[str] = Field(None, json_schema_extra={"example": '{"lighting": "bright", "tracking_quality": "normal"}'})
    captured_at: Optional[datetime.datetime] = None

class EvidenceRecordCreate(EvidenceRecordBase):
    pass

class EvidenceRecordResponse(EvidenceRecordBase):
    id: str
    observation_id: str
    captured_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Progress Observation Schemas
# ---------------------------------------------------------------------------
class ProgressObservationCreate(BaseModel):
    element_id: str = Field(..., json_schema_extra={"example": "COL-B1-04"})
    observer_id: str = Field(..., json_schema_extra={"example": "eng_sarah_01"})
    reported_state: str = Field(
        ...,
        description="Observed physical state: accepted_complete, in_progress, not_started, occluded, uncertain",
        json_schema_extra={"example": "accepted_complete"}
    )
    confidence_score: float = Field(1.0, ge=0.0, le=1.0, json_schema_extra={"example": 0.95})
    camera_pose_json: Optional[str] = Field(None, json_schema_extra={"example": '{"pos":[1.2,0.5,-3.4],"rot":[0,0,0,1]}'})
    notes: Optional[str] = Field(None, json_schema_extra={"example": "Reinforcement rebar tied and formwork stripped; concrete curing complete."})
    review_state: str = Field("pending_review", json_schema_extra={"example": "pending_review"})
    captured_at: Optional[datetime.datetime] = None
    evidence: Optional[List[EvidenceRecordCreate]] = None

class ProgressObservationResponse(BaseModel):
    id: str
    project_id: str
    element_id: str
    observer_id: str
    reported_state: str
    confidence_score: float
    camera_pose_json: Optional[str]
    notes: Optional[str]
    review_state: str
    captured_at: datetime.datetime
    created_at: datetime.datetime
    evidence_records: List[EvidenceRecordResponse] = []

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Project Summary / Progress Metric Schema
# ---------------------------------------------------------------------------
class ProjectSummaryResponse(BaseModel):
    project_id: str
    project_name: str
    total_elements: int
    verified_complete: int
    in_progress: int
    potentially_delayed: int
    ahead_of_schedule: int
    needs_manual_review: int
    not_started: int
    completion_percentage: float
    computed_at: datetime.datetime


# ---------------------------------------------------------------------------
# Human Review Decision Schemas (SRS FR-022, FR-024)
# ---------------------------------------------------------------------------
class ReviewDecisionCreate(BaseModel):
    element_id: str = Field(..., json_schema_extra={"example": "BM-L1-02"})
    observation_id: Optional[str] = Field(None, json_schema_extra={"example": "obs-abc123"})
    reviewer_id: str = Field(..., json_schema_extra={"example": "coord_elena_01"})
    decision: str = Field(
        ...,
        description="Review outcome: 'confirmed' (accepts work as complete), 'rejected' (declares incomplete/delayed), 'corrected' (sets in_progress), 'rescan_requested'",
        json_schema_extra={"example": "confirmed"}
    )
    reason: str = Field(
        ...,
        description="Justification note preserving audit trail (SRS 8.1)",
        json_schema_extra={"example": "Verified secondary engineering photo; scaffolding obstruction cleared and transfer girder accepted."}
    )

class ReviewDecisionResponse(BaseModel):
    id: str
    project_id: str
    element_id: str
    observation_id: Optional[str]
    reviewer_id: str
    decision: str
    reason: str
    decided_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Audit Trail Schemas (SRS FR-025)
# ---------------------------------------------------------------------------
class AuditLogResponse(BaseModel):
    id: str
    project_id: str
    entity_type: str
    entity_id: str
    action: str
    actor_id: str
    details_json: Optional[str]
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Computer-Vision Assistance Schemas (SRS FR-026, FR-027, SRS 8.3)
# ---------------------------------------------------------------------------
class CVDetectRequest(BaseModel):
    image_reference: Optional[str] = Field(None, json_schema_extra={"example": "uploads/frame_20261011_0915.jpg"})
    simulated_element_id: Optional[str] = Field("BM-L1-02", json_schema_extra={"example": "BM-L1-02"})
    simulated_confidence: Optional[float] = Field(0.55, ge=0.0, le=1.0, json_schema_extra={"example": 0.55})
    simulated_occlusion: Optional[bool] = Field(True, json_schema_extra={"example": True})

class CVProposal(BaseModel):
    element_id: str
    visual_state_proposed: str
    confidence_score: float
    is_occluded: bool
    bounding_box: List[float] # [x, y, w, h] normalized
    is_suggestion: bool = True
    guardrail_note: str

class CVDetectResponse(BaseModel):
    status: str
    proposals: List[CVProposal]
    requires_human_review: bool
    explanation: str
