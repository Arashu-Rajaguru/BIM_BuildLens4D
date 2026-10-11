import datetime
from sqlalchemy import Column, String, Text, Float, DateTime, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base

def utcnow():
    return datetime.datetime.now(datetime.timezone.utc)

class Project(Base):
    __tablename__ = "projects"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)
    timezone = Column(String(64), default="UTC")
    lifecycle_state = Column(String(32), default="active")  # active, completed, archived
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    # Relationships
    elements = relationship("BIMElement", back_populates="project", cascade="all, delete-orphan")
    observations = relationship("ProgressObservation", back_populates="project", cascade="all, delete-orphan")


class BIMElement(Base):
    __tablename__ = "bim_elements"

    # Stable element identifier (e.g. "COL-B1-01", "SLAB-L1-02")
    id = Column(String(64), primary_key=True, index=True)
    project_id = Column(String(64), ForeignKey("projects.id"), nullable=False, index=True)
    element_type = Column(String(64), nullable=False)  # Column, Beam, Slab, Wall, Footing, etc.
    label = Column(String(255), nullable=False)
    spatial_zone = Column(String(128), nullable=True)  # Grid, Level or Zone reference
    model_version_id = Column(String(64), default="v1.0")

    # Schedule parameters (4D integration)
    planned_start = Column(Date, nullable=False)
    planned_end = Column(Date, nullable=False)

    # Verification status computed / updated by progress engine:
    # 'verified_complete', 'in_progress', 'potentially_delayed', 'ahead_of_schedule', 'needs_manual_review', 'not_started'
    verification_state = Column(String(64), default="not_started", nullable=False, index=True)
    last_inspected_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    # Relationships
    project = relationship("Project", back_populates="elements")
    observations = relationship("ProgressObservation", back_populates="element", cascade="all, delete-orphan")


class ProgressObservation(Base):
    __tablename__ = "progress_observations"

    id = Column(String(64), primary_key=True, index=True)
    project_id = Column(String(64), ForeignKey("projects.id"), nullable=False, index=True)
    element_id = Column(String(64), ForeignKey("bim_elements.id"), nullable=False, index=True)
    observer_id = Column(String(64), nullable=False)  # Engineer ID or system ID
    
    # Visual observation state (distinct from schedule interpretation)
    # 'accepted_complete', 'in_progress', 'not_started', 'occluded', 'uncertain'
    reported_state = Column(String(64), nullable=False)
    confidence_score = Column(Float, default=1.0)
    camera_pose_json = Column(Text, nullable=True)  # JSON {position: [x,y,z], rotation: [qx,qy,qz,qw]}
    notes = Column(Text, nullable=True)

    # Review state: 'pending_review', 'approved', 'rejected', 'flagged_for_site_visit'
    review_state = Column(String(64), default="pending_review", nullable=False)
    
    captured_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    # Relationships
    project = relationship("Project", back_populates="observations")
    element = relationship("BIMElement", back_populates="observations")
    evidence_records = relationship("EvidenceRecord", back_populates="observation", cascade="all, delete-orphan")


class EvidenceRecord(Base):
    __tablename__ = "evidence_records"

    id = Column(String(64), primary_key=True, index=True)
    observation_id = Column(String(64), ForeignKey("progress_observations.id"), nullable=False, index=True)
    media_type = Column(String(64), default="image/jpeg")  # image/jpeg, image/png, pointcloud/ply
    media_url = Column(String(512), nullable=False)
    file_hash = Column(String(128), nullable=True)  # SHA-256 checksum for audit integrity
    metadata_json = Column(Text, nullable=True)  # Sensor, illumination, camera FOV, AR tracking state
    captured_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    # Relationships
    observation = relationship("ProgressObservation", back_populates="evidence_records")


class ReviewDecision(Base):
    __tablename__ = "review_decisions"

    id = Column(String(64), primary_key=True, index=True)
    project_id = Column(String(64), ForeignKey("projects.id"), nullable=False, index=True)
    element_id = Column(String(64), ForeignKey("bim_elements.id"), nullable=False, index=True)
    observation_id = Column(String(64), ForeignKey("progress_observations.id"), nullable=True, index=True)
    reviewer_id = Column(String(64), nullable=False)  # BIM Coordinator / Project Manager ID
    decision = Column(String(32), nullable=False)     # 'confirmed', 'rejected', 'corrected', 'rescan_requested'
    reason = Column(Text, nullable=False)             # Human review rationale (SRS 8.1 / 9)
    decided_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(64), primary_key=True, index=True)
    project_id = Column(String(64), ForeignKey("projects.id"), nullable=False, index=True)
    entity_type = Column(String(64), nullable=False)  # 'element', 'observation', 'review_decision'
    entity_id = Column(String(64), nullable=False, index=True)
    action = Column(String(64), nullable=False)       # 'observation_recorded', 'status_changed', 'review_approved', 'review_rejected'
    actor_id = Column(String(64), nullable=False)     # Engineer / Reviewer / System
    details_json = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False, index=True)
