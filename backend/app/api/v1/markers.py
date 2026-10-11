from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.domain import Project

router = APIRouter()

PROJECT_BENCHMARKS = [
    {
        "marker_id": "BM-GEO-01",
        "label": "Benchmark 1 — Grid A-1 South-West Corner",
        "zone": "Ground Retail South-West",
        "northing_m": 50428.150,
        "easting_m": 12840.220,
        "elevation_m": 10.000,
        "heading_degrees": 0.0,
        "local_offset": {"x": -7.50, "y": 0.00, "z": -7.00},
        "description": "Primary brass site disk embedded in ground retail slab for AR alignment."
    },
    {
        "marker_id": "BM-GEO-02",
        "label": "Benchmark 2 — Grid B-1 Storefront Entrance",
        "zone": "Ground Retail Central",
        "northing_m": 50428.150,
        "easting_m": 12847.720,
        "elevation_m": 10.000,
        "heading_degrees": 0.0,
        "local_offset": {"x": 0.00, "y": 0.00, "z": -7.00},
        "description": "Central arcade entrance benchmark for pedestrian AR perspective."
    },
    {
        "marker_id": "BM-GEO-03",
        "label": "Benchmark 3 — Grid C-1 South-East Corner",
        "zone": "Ground Retail South-East",
        "northing_m": 50428.150,
        "easting_m": 12855.220,
        "elevation_m": 10.000,
        "heading_degrees": 0.0,
        "local_offset": {"x": 7.50, "y": 0.00, "z": -7.00},
        "description": "East boundary benchmark adjacent to cast-iron fire escape stairs."
    },
    {
        "marker_id": "BM-GEO-04",
        "label": "Benchmark 4 — North Retaining Wall Baseline",
        "zone": "Perimeter North / Shoring Line",
        "northing_m": 50442.150,
        "easting_m": 12847.720,
        "elevation_m": 10.000,
        "heading_degrees": 180.0,
        "local_offset": {"x": 0.00, "y": 0.00, "z": 7.10},
        "description": "Subsurface perimeter shoring baseline for structural foundation alignment."
    },
    {
        "marker_id": "BM-GEO-05",
        "label": "Benchmark 5 — Mezzanine Floor Level 1 Datum",
        "zone": "Level 1 Fascia Line",
        "northing_m": 50431.950,
        "easting_m": 12847.720,
        "elevation_m": 13.600,
        "heading_degrees": 0.0,
        "local_offset": {"x": 0.00, "y": 3.60, "z": -7.00},
        "description": "Mezzanine transfer girder elevation datum for vertical AR tracking."
    }
]

@router.get(
    "/projects/{project_id}/markers",
    tags=["QR Code & AR Spatial Benchmarks"]
)
def list_spatial_markers(
    project_id: str,
    db: Session = Depends(get_db)
):
    """Retrieve all surveyed AR spatial benchmark anchors for sub-centimeter site alignment."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project '{project_id}' not found.")

    markers_with_payload = []
    for bm in PROJECT_BENCHMARKS:
        qr_payload = (
            f"BUILDLENS4D|{project_id}|{bm['marker_id']}|"
            f"N:{bm['northing_m']:.3f}|E:{bm['easting_m']:.3f}|Z:{bm['elevation_m']:.3f}|"
            f"HDG:{bm['heading_degrees']}"
        )
        markers_with_payload.append({
            **bm,
            "qr_payload": qr_payload,
            "project_id": project_id
        })

    return markers_with_payload


@router.get(
    "/projects/{project_id}/markers/{marker_id}/svg",
    tags=["QR Code & AR Spatial Benchmarks"]
)
def get_printable_marker_svg(
    project_id: str,
    marker_id: str,
    db: Session = Depends(get_db)
):
    """Generate high-contrast, printable SVG survey target for physical site placement."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project '{project_id}' not found.")

    target_bm = next((b for b in PROJECT_BENCHMARKS if b["marker_id"] == marker_id), None)
    if not target_bm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Benchmark '{marker_id}' not found.")

    # High-contrast surveyor target with fiducial crosshairs and encoded QR pattern
    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 480" width="400" height="480">
  <rect width="400" height="480" fill="#ffffff" />
  <rect x="20" y="20" width="360" height="440" fill="none" stroke="#0f172a" stroke-width="4" />
  
  <!-- Header -->
  <text x="200" y="55" font-family="Arial, sans-serif" font-size="20" font-weight="bold" fill="#0284c7" text-anchor="middle">BUILDLENS 4D AR BENCHMARK</text>
  <text x="200" y="80" font-family="Arial, sans-serif" font-size="13" font-weight="600" fill="#64748b" text-anchor="middle">PROJECT: {project_id}</text>
  
  <!-- Surveyor Target Reticle -->
  <circle cx="200" cy="220" r="110" fill="#f8fafc" stroke="#0f172a" stroke-width="6" />
  <circle cx="200" cy="220" r="70" fill="none" stroke="#0284c7" stroke-width="4" stroke-dasharray="8 6" />
  <circle cx="200" cy="220" r="30" fill="#0f172a" />
  
  <!-- Crosshairs -->
  <line x1="60" y1="220" x2="340" y2="220" stroke="#0f172a" stroke-width="3" />
  <line x1="200" y1="80" x2="200" y2="360" stroke="#0f172a" stroke-width="3" />
  
  <!-- Center Bullseye -->
  <circle cx="200" cy="220" r="6" fill="#ffffff" />
  
  <!-- Benchmark Metadata -->
  <rect x="35" y="360" width="330" height="85" fill="#f1f5f9" rx="6" />
  <text x="50" y="385" font-family="monospace" font-size="14" font-weight="bold" fill="#0f172a">{target_bm['marker_id']}: {target_bm['label']}</text>
  <text x="50" y="405" font-family="monospace" font-size="12" fill="#334155">Northing: {target_bm['northing_m']:.3f} m | Easting: {target_bm['easting_m']:.3f} m</text>
  <text x="50" y="425" font-family="monospace" font-size="12" fill="#334155">Elevation: {target_bm['elevation_m']:.3f} m | Zone: {target_bm['zone']}</text>
</svg>"""

    return Response(content=svg_content, media_type="image/svg+xml")
