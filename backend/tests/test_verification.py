import io
from fastapi.testclient import TestClient
from app.main import app
from PIL import Image

client = TestClient(app)

def create_test_image_bytes():
    # Generate a simple 100x100 RGB image in memory
    img = Image.new("RGB", (300, 200), color=(30, 60, 90))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()

def test_verify_building_image_upload_and_report():
    img_bytes = create_test_image_bytes()
    files = {
        "file": ("test_building_site.jpg", img_bytes, "image/jpeg")
    }
    data = {
        "plan_type": "site_photo",
        "target_zone": "ALL",
        "observer_id": "test_engineer_01"
    }

    # 1. POST to verify-image
    res = client.post("/api/projects/proj-terminal-04/verify-image", files=files, data=data)
    assert res.status_code == 201
    payload = res.json()
    assert "verification_id" in payload
    assert payload["plan_type"] == "site_photo"
    assert payload["total_detected_elements"] > 0
    assert "compliance_percentage" in payload
    assert "report_url" in payload
    report_id = payload["verification_id"]

    # 2. GET verification reports list
    res_list = client.get("/api/projects/proj-terminal-04/verification-reports")
    assert res_list.status_code == 200
    reports = res_list.json()
    assert any(r["id"] == report_id for r in reports)

    # 3. GET JSON report
    res_json = client.get(f"/api/projects/proj-terminal-04/reports/verification/{report_id}")
    assert res_json.status_code == 200
    json_data = res_json.json()
    assert json_data["id"] == report_id
    assert len(json_data["elements"]) > 0

    # 4. GET Official HTML Report
    res_html = client.get(f"/api/projects/proj-terminal-04/reports/verification/{report_id}/html")
    assert res_html.status_code == 200
    assert "text/html" in res_html.headers["content-type"]
    assert "BuildLens 4D" in res_html.text
    assert "Official Inspection Report" in res_html.text
    assert report_id in res_html.text
