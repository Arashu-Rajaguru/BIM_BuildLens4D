import io
import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def create_test_project_and_element():
    unique_suffix = uuid.uuid4().hex[:6]
    project_id = f"prj-feat-{unique_suffix}"
    element_id = f"el-feat-{unique_suffix}"

    # Create project
    proj_resp = client.post(
        "/api/projects",
        json={
            "id": project_id,
            "name": f"Feature Test Project {unique_suffix}",
            "description": "Validation of 4D scrubber, evidence, and benchmarks",
            "timezone": "UTC"
        }
    )
    assert proj_resp.status_code == 201

    # Create element spanning Oct 01 to Oct 20
    elem_resp = client.post(
        f"/api/projects/{project_id}/elements",
        json={
            "id": element_id,
            "label": f"Heavy Girder {unique_suffix}",
            "element_type": "Beam",
            "spatial_zone": "Mezzanine Level",
            "planned_start": "2026-10-01",
            "planned_end": "2026-10-20",
            "verification_state": "in_progress"
        }
    )
    assert elem_resp.status_code == 201
    return project_id, element_id


def test_4d_time_scrubber_simulation():
    project_id, element_id = create_test_project_and_element()

    # 1. Simulate on date BEFORE planned start (2026-09-15)
    resp_past = client.get(f"/api/projects/{project_id}/simulation?target_date=2026-09-15")
    assert resp_past.status_code == 200
    past_data = resp_past.json()
    assert past_data["not_started_elements"] == 1
    assert past_data["completed_elements"] == 0
    assert past_data["simulated_completion_percentage"] == 0.0

    # 2. Simulate on date DURING planned construction (2026-10-10)
    resp_mid = client.get(f"/api/projects/{project_id}/simulation?target_date=2026-10-10")
    assert resp_mid.status_code == 200
    mid_data = resp_mid.json()
    assert mid_data["in_progress_elements"] == 1
    elem_sim = mid_data["elements"][0]
    assert elem_sim["simulated_state"] == "in_progress"
    assert elem_sim["simulated_progress_percentage"] > 0

    # 3. Simulate on date AFTER planned completion (2026-10-25)
    resp_future = client.get(f"/api/projects/{project_id}/simulation?target_date=2026-10-25")
    assert resp_future.status_code == 200
    fut_data = resp_future.json()
    assert fut_data["completed_elements"] == 1
    assert fut_data["simulated_completion_percentage"] == 100.0


def test_spatial_benchmarks_and_svg():
    project_id, _ = create_test_project_and_element()

    # Fetch markers
    resp_markers = client.get(f"/api/projects/{project_id}/markers")
    assert resp_markers.status_code == 200
    markers = resp_markers.json()
    assert len(markers) >= 5
    assert any(m["marker_id"] == "BM-GEO-01" for m in markers)
    assert "BUILDLENS4D" in markers[0]["qr_payload"]

    # Fetch printable SVG for BM-GEO-01
    resp_svg = client.get(f"/api/projects/{project_id}/markers/BM-GEO-01/svg")
    assert resp_svg.status_code == 200
    assert "image/svg+xml" in resp_svg.headers["content-type"]
    assert "<svg" in resp_svg.text
    assert "BM-GEO-01" in resp_svg.text


def test_evidence_photo_upload_and_gallery():
    project_id, element_id = create_test_project_and_element()

    # Create dummy image bytes
    fake_img = io.BytesIO(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xff\xdb\x00C\x00test_image_data")
    fake_img.name = "site_column_inspection.jpg"

    upload_resp = client.post(
        f"/api/projects/{project_id}/elements/{element_id}/evidence",
        files={"file": ("site_column_inspection.jpg", fake_img, "image/jpeg")},
        data={
            "observer_id": "eng_tester_01",
            "reported_state": "in_progress",
            "notes": "Rebar cage tied and inspected for compliance."
        }
    )
    assert upload_resp.status_code == 201
    evidence_data = upload_resp.json()
    assert "/uploads/" in evidence_data["media_url"]
    assert len(evidence_data["file_hash"]) == 64  # Valid SHA-256

    # List evidence
    gallery_resp = client.get(f"/api/projects/{project_id}/elements/{element_id}/evidence")
    assert gallery_resp.status_code == 200
    gallery = gallery_resp.json()
    assert len(gallery) >= 1
    assert gallery[0]["id"] == evidence_data["id"]
