# DefectVision AI — Production Deployment Guide

## 1. System Requirements & Architecture

DefectVision AI is architected as a decoupled, multi-tier full-stack system:
- **Frontend Presentation Tier:** Static React single-page application hosted on **Vercel** (`https://defectvision-ai.vercel.app/`).
- **Persistent ML Backend Tier:** Python FastAPI service hosting 15 PatchCore memory banks, FAISS `IndexFlatL2` galleries, and an EfficientNet classifier (~1.8 GB RAM resident).

### Hardware Requirements
- **CPU:** Quad-core Intel Core i5 / AMD Ryzen 5 or higher (AVX2 support recommended for FAISS).
- **RAM:** Minimum 8 GB (16 GB recommended for resident caching of all 15 models).
- **GPU:** Optional. PyTorch runs efficiently on CPU with batch latencies under 50 ms.
- **Disk:** 5 GB free disk space for memory bank artifacts and checkpoints.

### Software Requirements
- **Operating System:** Linux (Ubuntu 20.04+), Windows 10/11, or macOS.
- **Python:** Version 3.10 to 3.12.
- **Node.js:** Version 18+ and npm 9+.

---

## 2. Decoupled Cloud Deployment Runbook

### 2.1 Frontend Deployment on Vercel

The frontend is deployed to the existing Vercel project (`defectvision-ai`):

#### Method A: GitHub App Continuous Deployment (Recommended)
1. In Vercel Project Settings (`https://vercel.com/team_SBG8P3wQG46ZQaT25UxpydkP/defectvision-ai/settings/git`), connect `suryacharan945/DefectVision-AI`.
2. Configure settings:
   - **Framework Preset:** Vite
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
3. Add Environment Variable:
   - `VITE_API_URL`: Public HTTPS URL of the persistent backend (e.g. `https://defectvision-backend.onrender.com`).
4. Pushes to `main` will automatically trigger continuous production deployments.

#### Method B: Manual CLI Deployment
```bash
# 1. Authenticate with Vercel
npx vercel login

# 2. Deploy frontend directory
cd frontend
npx vercel --prod
```

#### Edge Routing Configuration (`vercel.json`)
To prevent Vercel's SPA wildcard rewrite from intercepting API calls, `vercel.json` excludes `/api/*`:
```json
{
  "rewrites": [
    {
      "source": "/((?!api/).*)",
      "destination": "/index.html"
    }
  ]
}
```

---

### 2.2 Persistent FastAPI Backend Deployment

Because the backend holds ~1.8 GB of resident models in RAM, it requires persistent hosting.

#### Option A: Docker Container
Use the authoritative root `Dockerfile`:
```bash
# Build the production container from repository root
docker build -t defectvision-backend:v3.0.0 -f Dockerfile .

# Run with persistent volume mount for profiles and inspection history
docker run -d \
  --name defectvision-backend \
  -p 8001:8001 \
  -e DEFECTVISION_DATA_DIR=/app/data \
  -e CORS_ORIGINS="https://defectvision-ai.vercel.app,http://localhost:5173" \
  -v defectvision-data:/app/data \
  --restart unless-stopped \
  defectvision-backend:v3.0.0
```

#### Option B: Cloud PaaS (Render / Railway / Fly.io)
1. Deploy as a persistent Web Service (minimum 2 GB RAM).
2. Configure environment variables (see [`production.env.example`](../production.env.example)):
   - `PORT`: `8001`
   - `CORS_ORIGINS`: `https://defectvision-ai.vercel.app`
   - `DEFECTVISION_DATA_DIR`: `/data`
   - `PYTHONUNBUFFERED`: `1`
3. Set Build Command: `pip install -r requirements.txt`
4. Set Start Command: `cd DefectVisionAI && uvicorn app:app --host 0.0.0.0 --port $PORT`
5. Attach a persistent volume mounted at `/data` to retain adapted production profiles.

---

## 3. Local Development Quick Start

### Step 1: Environment Setup
```bash
# Clone the repository
git clone https://github.com/suryacharan945/DefectVision-AI.git
cd DefectVision-AI

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1

# Install Python dependencies
pip install -r requirements.txt
```

### Step 2: Launch Backend Server
```bash
cd DefectVisionAI
python -m uvicorn app:app --host 0.0.0.0 --port 8001
```
*Wait ~20 seconds for the resident PatchCore models and category classifier to load into memory.*

### Step 3: Launch Frontend Application
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 4. Health & Readiness Verification

Probing endpoints:
- **Readiness Probe:** `GET /api/ready` — Returns HTTP 200 with 15 category readiness statuses once all memory banks are loaded into RAM; returns HTTP 503 if degraded.
- **Liveness Probe:** `GET /api/health` — Returns system operational metadata and telemetry.
