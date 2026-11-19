# DefectVision AI — Installation & Setup Guide
**Release:** v1.0.0-rc1 (Research Prototype)  
**Date:** 2026-11-19  

---

## 1. System Requirements & Prerequisites

- **Operating System:** Windows 10/11, Ubuntu 20.04/22.04 LTS, or macOS 12+ (Apple Silicon supported).
- **Python:** Version 3.10, 3.11, or 3.12 (64-bit).
- **Node.js & npm:** Node.js v18.0+ or v20.0+ LTS with npm 9+.
- **Hardware (CPU):** Minimum 4 CPU cores, 8 GB RAM (16 GB recommended for multi-model resident caching).
- **Hardware (GPU Optional):** CUDA 11.8+ or 12.1+ compatible NVIDIA GPU with $\ge 4\text{ GB}$ VRAM. (Default execution is optimized for CPU).

---

## 2. Environment Setup

### 2.1 Clone Repository
```bash
git clone https://github.com/suryacharan945/DefectVision-AI.git
cd DefectVision-AI
git checkout fix/localhost-live-inference-restoration
```

### 2.2 Python Virtual Environment
On Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

On Linux / macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2.3 Frontend Dependencies
```bash
npm --prefix frontend install
```

---

## 3. Launching the Services

### 3.1 Starting the FastAPI Backend
The backend service must be launched from within the `DefectVisionAI` directory so local package imports resolve correctly:

On Windows (PowerShell):
```powershell
Set-Location "DefectVisionAI"
& "..\.venv\Scripts\python.exe" -m uvicorn app:app --host 127.0.0.1 --port 8001
```

On Linux / macOS:
```bash
cd DefectVisionAI
../.venv/bin/python -m uvicorn app:app --host 127.0.0.1 --port 8001
```

### 3.2 Starting the React Frontend
In a separate terminal:
```bash
npm --prefix frontend run dev
```
The frontend will start on `http://127.0.0.1:5174` (or `5173`).

---

## 4. Verification and Health Checking

### 4.1 Check API Health
```bash
curl http://127.0.0.1:8001/health
```
Expected output:
```json
{
  "status": "ready",
  "all_required_models_ready": true,
  "ready_category_models_count": 15
}
```

### 4.2 Run Test Suite
```bash
.\.venv\Scripts\python -m unittest discover tests
```
Expected output: `Ran 92 tests ... OK`.

### 4.3 Verify Frontend Production Build
```bash
npm --prefix frontend run build
```
Expected output: `built in ~4.30s` with exit code 0.
