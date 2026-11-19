# DefectVision AI — Deployment Verification & Public Audit Report

**Date:** November 2026  
**Auditor:** ML Operations & System Infrastructure Engineering  
**Target Environment:** Public Production Frontend (`https://defectvision-ai.vercel.app/`)  
**Production Commit at Audit:** `2fd48675bc7515d01cade08376e75fe607dcd112` (68 commits behind `main`)  
**Main Branch Integration SHA:** `521107605f0ebd53d7287a9fd430690e895bcca2`  

---

## 1. Public Frontend Live Audit Findings

A rigorous automated browser audit was conducted against the live public deployment at `https://defectvision-ai.vercel.app/` on November 19, 2026.

### 1.1 Summary of Observed Behaviors

| Feature / Inspection Area | Live Vercel Status (`2fd4867`) | Current Local Main (`5211076`+) | Analysis & Discrepancy |
| :--- | :--- | :--- | :--- |
| **Commit Age** | October 13, 2026 | November 19, 2026 | Live site is 68 commits behind repository HEAD. |
| **Product Profiles** | **MISSING** | Fully Implemented & Integrated | Feature introduced in Sprint 2.5 (`feat/production-profiles`) not deployed. |
| **Navigation Drawer** | Present (9 menu links) | Present (10 menu links) | Product Profiles route (`/profiles`) absent from live bundle. |
| **API Health Check** | Returns HTML `index.html` | Returns JSON status | Catch-all rewrite in `vercel.json` intercepts all `/api/*` paths. |
| **Inference Endpoints** | Aborted / 405 Method Not Allowed | Fully operational HTTP 200 | Live frontend attempts to POST to Vercel origin with no backend proxy. |
| **Live Stream Canvas** | **FATAL RUNTIME EXCEPTION** | **RESOLVED & VERIFIED** | `TypeError: Failed to execute 'lineTo' on 'CanvasRenderingContext2D': 2 arguments required, but only 1 present.` |
| **Mobile Responsiveness** | Responsive (375x667 verified) | Responsive | Navigation drawer, modal sheets, and layout collapse cleanly. |

---

## 2. Root Cause Analysis

### 2.1 Why the Deployed Vercel Site Was Out of Sync

1. **Direct CLI Deployment Artifact:**  
   Vercel deployment `dpl_62uGDmTtcYRMi3dD8ErhzLhSiBaU` was created manually via Vercel CLI from local directory commit `2fd48675bc7515d01cade08376e75fe607dcd112`.  
   Because automatic GitHub App integration / webhook triggers were not enabled on the Vercel project, subsequent pushes to the GitHub default branch `main` did not initiate automated builds.

2. **Edge Routing Contract Misconfiguration (`vercel.json`):**  
   The prior `vercel.json` specified:
   ```json
   {
     "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }]
   }
   ```
   This catch-all pattern captured every outbound HTTP query directed at `/api/*` and returned HTTP 200 with the frontend SPA `index.html`. Calling code expecting JSON crashed on `JSON.parse()`.

3. **Missing Coordinate Parameter in Canvas Reticle Rendering:**  
   In `frontend/src/pages/LiveStreamInspector.jsx`, lines 205 and 219 passed only a single parameter to the HTML5 Canvas 2D API:
   ```javascript
   // Buggy lines:
   ctx.lineTo(roiX + roiW);            // Line 205: Missing y coordinate
   ctx.lineTo(roiX + roiW);            // Line 219: Missing y coordinate
   ```
   This triggered a fatal JavaScript TypeError on every animation frame in the live site's bundled script (`index-BAvQJhD-.js:4273`), freezing the optical inspection reticle.

---

## 3. Implemented Corrections

1. **Fixed Edge Routing in `vercel.json`:**  
   Updated rewrite pattern to ignore `/api/*`:
   ```json
   {
     "rewrites": [{ "source": "/((?!api/).*)", "destination": "/index.html" }]
   }
   ```
2. **Fixed LiveStream Reticle Rendering in `frontend/src/pages/LiveStreamInspector.jsx`:**  
   Corrected canvas path drawing coordinates:
   ```javascript
   ctx.lineTo(roiX + roiW, roiY);          // Top-right bracket
   ctx.lineTo(roiX + roiW, roiY + roiH);   // Bottom-right bracket
   ```
3. **Engineered Resilient Connection Manager in `frontend/src/api/client.js`:**  
   Implemented 6-stage lifecycle (`CONNECTING`, `ONLINE`, `MODEL_LOADING`, `READY`, `DEGRADED`, `OFFLINE`) with automatic health polling, trailing slash normalization, and mock fallback.
4. **Enhanced Sidebar Status Display in `frontend/src/components/ui/SidebarNav.jsx`:**  
   Renders real-time status pill (`READY (15/15)`, `LOADING MODELS`, `OFFLINE (DEMO MODE)`).
5. **Hardened FastAPI Readiness Endpoints in `DefectVisionAI/app.py`:**  
   Added `/ready`, `/api/ready`, `/health`, and `/api/health` returning HTTP 200 only when all 15 models are resident in memory.

---

## 4. Production Deployment Runbook

### 4.1 Deploying the React Frontend to Vercel

There are two primary methods to update the public Vercel deployment:

#### Option A: Connect Vercel Project to GitHub (Recommended)
1. Navigate to the Vercel Dashboard: `https://vercel.com/team_SBG8P3wQG46ZQaT25UxpydkP/defectvision-ai/settings/git`.
2. Under **Connected Git Repository**, connect `suryacharan945/DefectVision-AI`.
3. Set **Production Branch** to `main`.
4. Set **Root Directory** to `frontend`.
5. Under **Environment Variables**, configure:
   - `VITE_API_URL`: URL of the persistent backend (e.g., `https://api.defectvision.your-domain.com`).
6. Every push to `main` will automatically build and deploy the production frontend.

#### Option B: Deploy via Vercel CLI
```bash
# 1. Login to Vercel
npx vercel login

# 2. Build and deploy frontend directory to production
cd frontend
npx vercel --prod
```

### 4.2 Hosting the Persistent FastAPI Backend

Because DefectVision AI requires ~2 GB resident RAM to hold the 15 MVTec memory banks and PyTorch models, it must run on a persistent VM, VPS, or container service.

#### Option A: Docker Deployment (Containerized)
```bash
# 1. Build the production container using root Dockerfile
docker build -t defectvision-backend:v3.0.0 -f Dockerfile .

# 2. Run with volume mount for persistent profiles and data
docker run -d \
  --name defectvision-backend \
  -p 8001:8001 \
  -e DEFECTVISION_DATA_DIR=/app/data \
  -e CORS_ORIGINS="https://defectvision-ai.vercel.app,http://localhost:5173" \
  -v defectvision-data:/app/data \
  --restart unless-stopped \
  defectvision-backend:v3.0.0
```

#### Option B: Cloud PaaS Deployment (Render / Railway / Fly.io)
1. Create a **Persistent Web Service** with at least 2 GB RAM (e.g., Render "Standard" plan or Railway 2GB RAM container).
2. Set Build Command: `pip install -r requirements.txt`
3. Set Start Command: `cd DefectVisionAI && uvicorn app:app --host 0.0.0.0 --port $PORT`
4. Configure Environment Variables:
   - `CORS_ORIGINS`: `https://defectvision-ai.vercel.app`
   - `DEFECTVISION_DATA_DIR`: `/data`
   - `PYTHONUNBUFFERED`: `1`
5. Attach a 5 GB Persistent Volume mounted at `/data`.
6. Copy the assigned backend public URL (e.g. `https://defectvision-api.onrender.com`) and paste it as `VITE_API_URL` in the Vercel Project Settings.
