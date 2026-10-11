import pytest

def test_list_projects(client):
    response = client.get("/api/projects")
    assert response.status_code == 200
    projects = response.json()
    assert isinstance(projects, list)
    assert len(projects) >= 1
    assert any(p["id"] == "proj-terminal-04" for p in projects)

def test_create_project_and_elements(client):
    import uuid
    uid = uuid.uuid4().hex[:6]
    test_proj_id = f"proj-test-pier9-{uid}"
    
    # 1. Create a test project
    new_proj = {
        "id": test_proj_id,
        "name": "Pier 9 Viaduct Segment",
        "description": "Pre-stressed concrete bridge deck segment",
        "location": "North River Crossway",
        "timezone": "UTC",
        "lifecycle_state": "active"
    }
    create_resp = client.post("/api/projects", json=new_proj)
    assert create_resp.status_code == 201
    assert create_resp.json()["id"] == test_proj_id

    # 2. Add a BIM element with 4D schedule
    new_element = {
        "id": f"PIER-COL-{uid}",
        "element_type": "Column",
        "label": "Pier 9 Support Column P1",
        "spatial_zone": "Pier 9 Foundation",
        "model_version_id": "v1.0",
        "planned_start": "2026-10-01",
        "planned_end": "2026-10-20",
        "verification_state": "not_started"
    }
    el_resp = client.post(f"/api/projects/{test_proj_id}/elements", json=new_element)
    assert el_resp.status_code == 201
    assert el_resp.json()["id"] == f"PIER-COL-{uid}"

    # 3. Test progress observation with 'occluded' status -> must mark 'needs_manual_review'
    # (Engineering rule: AR detector / alignment alone must never assume complete or missing if occluded)
    obs_payload = {
        "element_id": f"PIER-COL-{uid}",
        "observer_id": "eng_mark_02",
        "reported_state": "occluded",
        "confidence_score": 0.45,
        "notes": "Scaffolding tarpaulin blocking direct sightline to column top.",
        "evidence": [
            {
                "media_type": "image/jpeg",
                "media_url": "evidence/pier_col_01_occluded.jpg"
            }
        ]
    }
    obs_resp = client.post(f"/api/projects/{test_proj_id}/observations", json=obs_payload)
    assert obs_resp.status_code == 201

    # Check that element verification state is now 'needs_manual_review'
    el_check = client.get(f"/api/projects/{test_proj_id}/elements/PIER-COL-{uid}")
    assert el_check.status_code == 200
    assert el_check.json()["verification_state"] == "needs_manual_review"

def test_project_summary_calculation(client):
    response = client.get("/api/projects/proj-terminal-04/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["project_id"] == "proj-terminal-04"
    assert data["total_elements"] > 0
    assert "completion_percentage" in data
    assert "verified_complete" in data
    assert "potentially_delayed" in data
    assert "needs_manual_review" in data
