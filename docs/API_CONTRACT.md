# BuildLens 4D — REST API Specification & Contract

Version: `1.0.0`  
Base URL: `/api`  
Protocol: `HTTP / 1.1` (HTTPS recommended for production staging)  
Content-Type: `application/json`

---

## 1. System Health

### `GET /api/health`
Checks backend operational status, API version, and database connectivity.

**Request:** None

**Response (200 OK):**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "database": "connected",
  "environment": "development",
  "timestamp": "2026-10-09T05:34:39.061852Z"
}
```

---

## 2. Construction Projects

### `GET /api/projects`
Retrieves all registered construction projects.

**Response (200 OK):**
```json
[
  {
    "id": "proj-terminal-04",
    "name": "Metro Station Box - Terminal 4",
    "description": "Subsurface reinforced concrete concourse structure",
    "location": "Zone 3, Central Transit Hub",
    "timezone": "UTC",
    "lifecycle_state": "active",
    "created_at": "2026-10-09T05:00:00Z",
    "updated_at": "2026-10-09T05:00:00Z"
  }
]
```

### `POST /api/projects`
Registers a new construction project.

**Request Body (201 Created):**
```json
{
  "id": "proj-terminal-04",
  "name": "Metro Station Box - Terminal 4",
  "description": "Subsurface reinforced concrete concourse structure",
  "location": "Zone 3, Central Transit Hub",
  "timezone": "UTC",
  "lifecycle_state": "active"
}
```

### `GET /api/projects/{project_id}/summary`
Computes 4D progress metrics and schedule-aware completion percentage.

**Response (200 OK):**
```json
{
  "project_id": "proj-terminal-04",
  "project_name": "Metro Station Box - Terminal 4",
  "total_elements": 8,
  "verified_complete": 3,
  "in_progress": 2,
  "potentially_delayed": 1,
  "ahead_of_schedule": 0,
  "needs_manual_review": 1,
  "not_started": 1,
  "completion_percentage": 37.5,
  "computed_at": "2026-10-09T05:35:00Z"
}
```

---

## 3. BIM Elements (4D Schedule)

### `GET /api/projects/{project_id}/elements`
Retrieves BIM elements for a project, with optional query parameters:
- `verification_state`: `verified_complete`, `in_progress`, `potentially_delayed`, `ahead_of_schedule`, `needs_manual_review`, `not_started`
- `element_type`: `Column`, `Beam`, `Slab`, `Wall`, `Footing`

**Response (200 OK):**
```json
[
  {
    "id": "COL-B1-01",
    "project_id": "proj-terminal-04",
    "element_type": "Column",
    "label": "Track Level Heavy Column Grid A1",
    "spatial_zone": "Concourse Level / Grid A-1",
    "model_version_id": "v1.0",
    "planned_start": "2026-09-01",
    "planned_end": "2026-09-20",
    "verification_state": "verified_complete",
    "last_inspected_at": "2026-09-18T10:30:00Z",
    "created_at": "2026-10-09T05:00:00Z",
    "updated_at": "2026-10-09T05:00:00Z"
  }
]
```

### `POST /api/projects/{project_id}/elements`
Registers a new BIM element with planned start/end schedule dates.

**Request Body (201 Created):**
```json
{
  "id": "COL-B1-05",
  "element_type": "Column",
  "label": "Track Level Heavy Column Grid A5",
  "spatial_zone": "Concourse Level / Grid A-5",
  "model_version_id": "v1.0",
  "planned_start": "2026-10-15",
  "planned_end": "2026-10-30",
  "verification_state": "not_started"
}
```

---

## 4. Progress Observations & Evidence

### `POST /api/projects/{project_id}/observations`
Logs a field progress observation captured via the Unity AR application or site engineer review.  
*Automatically triggers the 4D progress evaluation engine to update the BIM element's verification state.*

**Request Body (201 Created):**
```json
{
  "element_id": "COL-B1-03",
  "observer_id": "eng_sarah_01",
  "reported_state": "in_progress",
  "confidence_score": 0.88,
  "camera_pose_json": "{\"pos\":[1.2,0.5,-3.4],\"rot\":[0,0,0,1]}",
  "notes": "Formwork 75% complete; rebar cage partially assembled.",
  "review_state": "pending_review",
  "captured_at": "2026-10-08T10:30:00Z",
  "evidence": [
    {
      "media_type": "image/jpeg",
      "media_url": "mock_evidence/col_b1_03_delayed.jpg",
      "metadata_json": "{\"tracking_state\":\"Tracking\",\"light_lumens\":520}"
    }
  ]
}
```

### `GET /api/projects/{project_id}/observations`
Retrieves observation history for a project or specific element (`?element_id=COL-B1-03`).

---

## 5. Human Review Decisions & Auditing (SRS FR-022, FR-024)

### `POST /api/projects/{project_id}/reviews`
Records an auditable human review verdict to confirm, reject, or correct a flagged BIM element. Automatically mutates target element verification state and logs an immutable audit event.

**Request Body (201 Created):**
```json
{
  "element_id": "BM-L1-02",
  "observation_id": "obs-abc123",
  "reviewer_id": "coord_elena_01",
  "decision": "confirmed",
  "reason": "Scaffolding cleared; secondary engineering photograph verifies complete rebar installation and concrete cure."
}
```

### `GET /api/projects/{project_id}/reviews`
Retrieves historical review decisions for a project or filtered by element (`?element_id=BM-L1-02`).

### `GET /api/projects/{project_id}/audit-trail` (SRS FR-025)
Retrieves the complete, chronological, immutable audit log of all element inspections, decisions, and state transitions.

---

## 6. Computer Vision Assistance (SRS FR-026, FR-027, SRS 8.3)

### `POST /api/projects/{project_id}/cv-detect`
Simulates object detection proposals and executes Section 8.3 safety guardrails (low confidence <0.60 or occlusions force manual review).

**Request Body (200 OK):**
```json
{
  "simulated_element_id": "BM-L1-02",
  "simulated_confidence": 0.55,
  "simulated_occlusion": true
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "proposals": [
    {
      "element_id": "BM-L1-02",
      "visual_state_proposed": "needs_manual_review",
      "confidence_score": 0.55,
      "is_occluded": true,
      "bounding_box": [0.24, 0.38, 0.52, 0.28],
      "is_suggestion": true,
      "guardrail_note": "Occlusion detected (scaffolding/equipment)"
    }
  ],
  "requires_human_review": true,
  "explanation": "Observation exhibits visual occlusion or borderline confidence (<0.60). Flagged for BIM Coordinator / Field Inspector review in accordance with SRS 8.3."
}
```

---

## 7. Reports & Data Exports (SRS FR-030)

### `GET /api/projects/{project_id}/export/csv`
Streams/downloads standard CSV formatted 4D progress and verification data.
Headers: `element_id, type, label, zone, planned_start, planned_end, verification_state, last_inspected, notes`.

### `GET /api/projects/{project_id}/report/summary`
Returns 4D progress metrics accompanied by governance statistics (human review count, audit event count, and compliance declaration).

---

## 8. Photographic Evidence Gallery & Uploads

### `POST /api/projects/{project_id}/elements/{element_id}/evidence`
Uploads an on-site inspection photo (`multipart/form-data`) attached to a BIM element. Generates a unique `/uploads/` URL, records SHA-256 integrity hash, and updates element inspection date.

### `GET /api/projects/{project_id}/elements/{element_id}/evidence`
Retrieves all historical photographic evidence records and thumbnails attached to the specified BIM element.

---

## 9. 4D Time-Lapse Schedule Scrubber Simulation

### `GET /api/projects/{project_id}/simulation?target_date=YYYY-MM-DD`
Computes the simulated construction progress across past, present, and future dates based on scheduled milestone windows. Returns completion percentage, active elements, and simulated state per element.

---

## 10. AR Spatial Benchmark Fiducials

### `GET /api/projects/{project_id}/markers`
Retrieves surveyed georeferenced spatial benchmark anchors (`BM-GEO-01` through `BM-GEO-05`) with Northing, Easting, Elevation, local coordinate offsets, and QR payloads for sub-centimeter mobile AR alignment.

### `GET /api/projects/{project_id}/markers/{marker_id}/svg`
Streams a high-contrast, printable surveyor target card SVG with alignment crosshairs and encoded benchmark metadata.

---

## 11. Standard Error Format
When an error occurs (e.g. 400 Bad Request, 404 Not Found, 422 Unprocessable Entity), the response body is formatted as:
```json
{
  "detail": "BIM element 'COL-99-99' does not exist in project 'proj-terminal-04'."
}
```


