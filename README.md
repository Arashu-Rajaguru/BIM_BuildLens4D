# BuildLens 4D — Mobile AR & 4D BIM Construction Progress Monitoring

**BuildLens 4D** is a mobile Augmented Reality (AR) construction progress monitoring system designed to bridge Building Information Modeling (BIM) with real-world site execution. It compares the planned construction state from a 4D BIM model and schedule against actual physical observations captured on-site.

---

## 1. System Overview

```
                      +-----------------------------+
                      |   Field Engineer (Android)  |
                      |    Unity + AR Foundation    |
                      +--------------+--------------+
                                     |  HTTP / JSON (LAN IP)
                                     v
+------------------+         +-------+-------+         +--------------------+
|  PostgreSQL /    | <-----> |   FastAPI     | <-----> |   Web Dashboard    |
|  SQLite Database |         |   Backend     |         |   (React + Vite)   |
+------------------+         +---------------+         +--------------------+
```

### Key Capabilities
1. **Mobile AR Alignment**: Tap-to-place lightweight BIM models onto detected real-world horizontal surfaces.
2. **Stable Element Tracking**: Associates construction components (columns, beams, slabs, walls) with persistent IDs (e.g., `COL-B1-01`).
3. **4D Schedule Comparison**: Compares visual observations against planned start and completion dates.
4. **Separation of Evidence and Schedule**: AR alignment or computer vision alone never proves completion. Uncertain, occluded, or out-of-frame elements are flagged for manual review rather than declared missing.
5. **Web Dashboard**: Provides construction managers with a 4D progress overview, delay alerts, and review queues.

---

## 2. Directory Structure

```
BuildLens4D/
├── UnityApp/
│   └── BuildLens4D/
│       └── Assets/
│           └── Scripts/             # Unity C# AR integration scripts (source-only)
│               ├── ARPlacementController.cs
│               ├── BIMElementMetadata.cs
│               ├── ProgressCaptureController.cs
│               └── BuildLensApiClient.cs
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI application entry point
│   │   ├── api/v1/                  # API routers (health, projects, elements, observations)
│   │   ├── core/                    # Config & database engine
│   │   ├── models/                  # SQLAlchemy domain models
│   │   ├── schemas/                 # Pydantic v2 validation schemas
│   │   └── services/                # 4D progress evaluation engine & seed data
│   ├── tests/                       # Pytest unit & integration test suite
│   ├── requirements.txt
│   └── .env.example
├── dashboard/                       # React + Vite web dashboard
├── docs/
│   ├── ARCHITECTURE.md              # System architecture & data flow
│   ├── SETUP.md                     # Step-by-step Windows PowerShell setup
│   └── API_CONTRACT.md              # REST API interface specification
├── BuildLens4D_SRS.docx             # Software Requirements Specification
└── README.md
```

---

## 3. Quick Start (Windows PowerShell)

### Backend Service
```powershell
cd C:\BuildLens4D\backend
# Create & activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run unit tests
pytest -v

# Start FastAPI development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Open [http://localhost:8000/docs](http://localhost:8000/docs) to view interactive OpenAPI documentation.

### Web Dashboard
```powershell
cd C:\BuildLens4D\dashboard
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) to view the construction progress dashboard.

---

## 4. Hardware Optimization Notes
Designed for development on modest hardware (e.g. 16 GB RAM, Intel Iris integrated GPU + 2 GB dedicated GPU):
- Uses lightweight bounding-box and low-poly visual representations in AR rather than heavy multi-gigabyte IFC geometries.
- Supports zero-friction local SQLite development database without running memory-heavy database services.
- Clean separation of backend, web frontend, and Unity source scripts.
