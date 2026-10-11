import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def create_test_project_and_element():
    unique_suffix = uuid.uuid4().hex[:6]
    project_id = f"prj-srs-{unique_suffix}"
    element_id = f"el-srs-{unique_suffix}"

    # Create project
    proj_resp = client.post(
        "/api/projects",
        json={
            "id": project_id,
            "name": f"SRS Test Project {unique_suffix}",
            "description": "Validation of FR-022 to FR-032",
            "timezone": "UTC"
        }
    )
    assert proj_resp.status_code == 201

    # Create element in 'needs_manual_review'
    elem_resp = client.post(
        f"/api/projects/{project_id}/elements",
        json={
            "id": element_id,
            "label": f"Transfer Beam {unique_suffix}",
            "element_type": "beam",
            "spatial_zone": "Level 1 North",
            "planned_start": "2026-10-01",
            "planned_end": "2026-10-10",
            "verification_state": "needs_manual_review"
        }
    )
    assert elem_resp.status_code == 201

    return project_id, element_id


def test_human_review_decision_and_audit():
    project_id, element_id = create_test_project_and_element()

    # Submit human review decision confirming completion
    review_resp = client.post(
        f"/api/projects/{project_id}/reviews",
        json={
            "element_id": element_id,
            "reviewer_id": "coord_tester_01",
            "decision": "confirmed",
            "reason": "Scaffolding cleared; photographic evidence confirms 100% concrete pour."
        }
    )
    assert review_resp.status_code == 201
    data = review_resp.json()
    assert data["decision"] == "confirmed"
    assert data["element_id"] == element_id
    assert data["reviewer_id"] == "coord_tester_01"

    # Verify element state updated to 'verified_complete'
    elem_check = client.get(f"/api/projects/{project_id}/elements/{element_id}")
    assert elem_check.status_code == 200
    assert elem_check.json()["verification_state"] == "verified_complete"

    # Check reviews list
    reviews_list = client.get(f"/api/projects/{project_id}/reviews")
    assert reviews_list.status_code == 200
    assert len(reviews_list.json()) >= 1
    assert reviews_list.json()[0]["element_id"] == element_id

    # Check audit trail
    audit_resp = client.get(f"/api/projects/{project_id}/audit-trail")
    assert audit_resp.status_code == 200
    audits = audit_resp.json()
    assert len(audits) >= 1
    assert any(a["action"] == "review_confirmed" and a["entity_id"] == element_id for a in audits)


def test_cv_detection_guardrails():
    project_id, element_id = create_test_project_and_element()

    # Call CV detect with low confidence and occlusion (should flag for human review)
    cv_resp = client.post(
        f"/api/projects/{project_id}/cv-detect",
        json={
            "simulated_element_id": element_id,
            "simulated_confidence": 0.52,
            "simulated_occlusion": True
        }
    )
    assert cv_resp.status_code == 200
    cv_data = cv_resp.json()
    assert cv_data["status"] == "success"
    assert cv_data["requires_human_review"] is True
    assert len(cv_data["proposals"]) == 1
    prop = cv_data["proposals"][0]
    assert prop["is_suggestion"] is True
    assert prop["is_occluded"] is True
    assert "Occlusion" in prop["guardrail_note"]


def test_csv_export_and_summary_report():
    project_id, element_id = create_test_project_and_element()

    # Export CSV
    csv_resp = client.get(f"/api/projects/{project_id}/export/csv")
    assert csv_resp.status_code == 200
    assert "text/csv" in csv_resp.headers["content-type"]
    csv_text = csv_resp.text
    assert "element_id,type,label,zone" in csv_text
    assert element_id in csv_text

    # Summary Report
    rep_resp = client.get(f"/api/projects/{project_id}/report/summary")
    assert rep_resp.status_code == 200
    rep_data = rep_resp.json()
    assert "summary" in rep_data
    assert "governance" in rep_data
    assert rep_data["summary"]["total_elements"] >= 1
