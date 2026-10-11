# BuildLens 4D — Setup & Execution Guide

This guide details how to set up, configure, test, and run each component of the **BuildLens 4D** project on Windows 11 using PowerShell.

---

## 1. Prerequisites

- **OS:** Windows 10 or Windows 11 (64-bit)
- **Python:** Python 3.10+ (tested with Python 3.14)
- **Node.js:** v18+ (tested with v24.21.0) and npm (v10+)
- **Unity Editor:** Unity 2022.3 LTS or 2023 LTS with **Android Build Support**, **Android SDK & NDK Tools**, and **OpenJDK** installed via Unity Hub.

---

## 2. Backend Setup (FastAPI)

### 2.1 Virtual Environment & Installation
Open Windows PowerShell:
```powershell
# Navigate to backend directory
cd C:\BuildLens4D\backend

# Create Python virtual environment
python -m venv .venv

# Activate virtual environment
# Note: If PowerShell displays an Execution Policy restriction, run:
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1

# Install required dependencies
pip install -r requirements.txt
```

### 2.2 Environment Configuration
Copy `.env.example` to create your local `.env`:
```powershell
Copy-Item .env.example .env
```
Default settings are pre-configured to use **SQLite** (`sqlite:///./buildlens4d.db`), which requires zero database server setup.

If using PostgreSQL, edit `.env`:
```env
DATABASE_URL="postgresql://username:password@localhost:5432/buildlens4d"
```

### 2.3 Running Backend Tests
Execute the pytest suite:
```powershell
pytest -v
```
All tests verify endpoint availability, schema validation, and the 4D progress calculation engine.

### 2.4 Running the Backend Server
Start the FastAPI server:
```powershell
# Note: Binding to 0.0.0.0 allows mobile devices on the same Wi-Fi to connect
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- Interactive Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health Check: [http://localhost:8000/api/health](http://localhost:8000/api/health)

---

## 3. Web Dashboard Setup (React + Vite)

### 3.1 Installation
Open a separate PowerShell window:
```powershell
cd C:\BuildLens4D\dashboard
npm.cmd install
```

### 3.2 Starting Development Server
```powershell
npm.cmd run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

The dashboard includes a toggle between **Live Backend Mode** (connecting to `http://localhost:8000/api`) and **Demonstrator / Mock Data Mode** to facilitate testing without needing a running backend.

---

## 4. Unity AR Setup (Mobile Field Client)

> **Important:** The Unity project scripts in `UnityApp/BuildLens4D/Assets/Scripts/` are delivered as source files. Unity Editor must create the Unity project and package cache itself.

### 4.1 Creating the Unity Project
1. Open **Unity Hub**.
2. Click **New project** $\rightarrow$ Select **3D (URP)** or **3D (Core)**.
3. Name the project `BuildLens4D` and set the location to `C:\BuildLens4D\UnityApp`.
4. Once the project opens in Unity Editor:
   - Go to **Window $\rightarrow$ Package Manager**.
   - Install **AR Foundation** (v5.x or v6.x).
   - Install **Google ARCore XR Plug-in**.
   - Go to **Edit $\rightarrow$ Project Settings $\rightarrow$ XR Plug-in Management** $\rightarrow$ Check **Google ARCore** under Android tab.

### 4.2 Script Placement & Scene Setup
The source files are located in:
`C:\BuildLens4D\UnityApp\BuildLens4D\Assets\Scripts\`
- `ARPlacementController.cs`: Attach to an empty GameObject with `ARPlaneManager` and `ARRaycastManager`.
- `BIMElementMetadata.cs`: Attach to each BIM element prefab collider.
- `ProgressCaptureController.cs`: Attach to the capture UI manager.
- `BuildLensApiClient.cs`: Attach to the scene manager. Set `apiBaseUrl` to your laptop's Wi-Fi IP (e.g., `http://192.168.1.100:8000`).

### 4.3 Discovering Your Laptop's LAN IP
In PowerShell:
```powershell
ipconfig
```
Look for `IPv4 Address` under your active Wi-Fi adapter (e.g. `192.168.1.45`). In Unity, set:
`Api Base Url` = `http://192.168.1.45:8000/api`
Ensure your Android mobile device is connected to the same Wi-Fi network.
