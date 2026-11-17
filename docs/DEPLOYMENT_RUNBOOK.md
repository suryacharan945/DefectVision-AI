# DefectVision AI — Production Deployment Runbook & Cloud Architecture Guide

**System Version:** 3.0.0  
**Target Architecture:** Decoupled Cloud Native (Vercel Frontend + Containerized FastAPI Backend)  
**Authoritative Frontend URL:** `https://defectvision-ai.vercel.app/`  
**FastAPI Health Endpoint:** `/health` or `/api/health`  

---

## 1. System Architecture Overview

DefectVision AI is an enterprise-grade industrial optical inspection system consisting of:
1. **Frontend Client (Vite / React 18):** Deployed on Vercel's Edge Network for global low-latency static delivery.
2. **Inference Backend (FastAPI / PyTorch CPU):** Packaged as an optimized Linux container running 15 category-specific PatchCore memory banks, EfficientNet-B0 category classifier, FAISS nearest-neighbor galleries, and optical quality verification services.

```
                          +------------------------------------------+
                          |        User Browser / Edge Camera        |
                          +------------------------------------------+
                                       |                 |
                   HTTPS (HTML/JS/CSS) |                 | API Requests & Frames
                                       v                 v
                 +--------------------------+   +-------------------------------+
                 |     Vercel Static CDN    |   |    Containerized Backend      |
                 | defectvision-ai.vercel.app|   | (Render / Railway / Fly / AWS)|
                 +--------------------------+   +-------------------------------+
                                                                 |
                                              +------------------+------------------+
                                              | 15 PatchCore Memory Banks (~360MB)  |
                                              | EfficientNet-B0 Classifier (17MB)  |
                                              | FAISS Defect Galleries (15 indices) |
                                              | Decision Fusion & Quality Gating   |
                                              +-------------------------------------+
```

---

## 2. Cloud Backend Sizing & Prerequisites

The backend requires sufficient resident RAM to hold the 15 category memory banks and PyTorch neural network weights in memory without swapping.

| Specification | Minimum Required | Recommended Production |
| :--- | :--- | :--- |
| **RAM** | 2.0 GB | 4.0 GB |
| **vCPU** | 1.0 vCPU | 2.0 vCPUs |
| **Base OS** | Debian / Ubuntu Linux | Debian 12 Slim (`python:3.11-slim`) |
| **Disk Space** | 3.0 GB | 5.0 GB |
| **Inference Mode** | PyTorch CPU with OpenMP | PyTorch CPU with OpenMP |

---

## 3. Step-by-Step Backend Deployment

### Option A: Render (Recommended for Rapid Zero-Config Deployment)

1. **Login to Render Dashboard:** Navigate to [dashboard.render.com](https://dashboard.render.com).
2. **Create New Web Service:**
   - Click **New +** > **Web Service**.
   - Connect your GitHub repository: `suryacharan945/DefectVision-AI`.
   - Branch: `main` (or `fix/production-backend-integration`).
3. **Configure Service Settings:**
   - **Environment:** `Docker`
   - **Dockerfile Path:** `./Dockerfile`
   - **Docker Context:** `.`
   - **Instance Type:** `Starter` (2 GB RAM, 1 vCPU) or higher.
4. **Configure Environment Variables:**
   - `PORT`: `8000`
   - `HOST`: `0.0.0.0`
   - `CORS_ORIGINS`: `https://defectvision-ai.vercel.app,http://localhost:5173,http://127.0.0.1:5173`
   - `KMP_DUPLICATE_LIB_OK`: `TRUE`
5. **Set Healthcheck Path:**
   - In Advanced Settings, set **Health Check Path** to `/health`.
6. **Deploy:** Click **Create Web Service**. Wait for the build to complete and note your backend URL (e.g., `https://defectvision-backend.onrender.com`).

---

### Option B: Railway

1. **Login to Railway:** Navigate to [railway.app](https://railway.app).
2. **Create New Project:** Select **Deploy from GitHub repo** and pick `suryacharan945/DefectVision-AI`.
3. **Automatic Detection:** Railway reads `railway.json` and `Dockerfile` automatically.
4. **Configure Variables:**
   - `PORT`: `8000`
   - `CORS_ORIGINS`: `https://defectvision-ai.vercel.app`
5. **Generate Domain:** In Service Settings > Networking, click **Generate Domain** (e.g., `https://defectvision-ai-production.up.railway.app`).

---

### Option C: Fly.io

1. **Install Fly CLI:** `curl -L https://fly.io/install.sh | sh`
2. **Launch Application:**
   ```bash
   fly launch --dockerfile Dockerfile --name defectvision-backend --memory 2048 --cpus 1
   ```
3. **Set Secrets & Config:**
   ```bash
   fly secrets set CORS_ORIGINS="https://defectvision-ai.vercel.app"
   fly deploy
   ```

---

## 4. Configuring Vercel Frontend Environment

Once your backend is running and returns 200 OK on its `/health` endpoint, connect the Vercel frontend:

1. **Open Vercel Project Dashboard:**
   - Go to [vercel.com/dashboard](https://vercel.com/dashboard).
   - Select project: `defectvision-ai` (ID: `prj_jmVHZCfTfEc6DYJp2nHn51vCJIVF`).
2. **Navigate to Environment Variables:**
   - Click **Settings** > **Environment Variables**.
3. **Add `VITE_API_URL`:**
   - **Key:** `VITE_API_URL`
   - **Value:** `https://your-backend-service.onrender.com` (do not include trailing slash).
   - **Environments:** Select **Production**, **Preview**, and **Development**.
   - Click **Save**.
4. **Trigger Redeployment:**
   - Go to the **Deployments** tab.
   - Click the three dots `...` next to the latest production deployment.
   - Click **Redeploy**.
   - Ensure the option **"Use existing Build Cache"** is **UNCHECKED** so Vite compiles the new environment variable.
5. **Verify Connection:**
   - Open `https://defectvision-ai.vercel.app/`.
   - The top banner will immediately transition to:
     `LIVE INFERENCE ACTIVE | Resident PyTorch CPU + FAISS Memory Banks (https://your-backend-service.onrender.com)`
   - The Demo Mode banner will be inactive, and real live inference will execute for both upload and camera streams.

---

## 5. Verification Checklist

Execute these terminal verification tests to validate your production deployment:

```bash
# 1. Health check returns status ready with 15 categories
curl -s -X GET "https://<your-backend-domain>/health" | jq .

# Expected Output:
# {
#   "status": "ready",
#   "service": "DefectVision AI — Live Inference Server",
#   "device": "cpu",
#   "optical_engine_ready": true,
#   "classifier_ready": true,
#   "models_ready_count": 15,
#   "all_models_ready": true,
#   "thresholds_ready": true,
#   "total_categories": 15,
#   "process_reachable": true
# }

# 2. CORS Preflight & Origin check for production frontend
curl -I -X GET "https://<your-backend-domain>/health" \
  -H "Origin: https://defectvision-ai.vercel.app"

# Expected Header:
# access-control-allow-origin: https://defectvision-ai.vercel.app
# access-control-allow-credentials: true

# 3. Model status check
curl -s -X GET "https://<your-backend-domain>/api/optical-inspection/model-status" | jq .total_categories
# Expected: 15
```

---

## 6. Incident Troubleshooting Runbook

### Incident 1: HTTP 503 "Backend Unavailable (Endpoint returned HTML SPA fallback)"
- **Symptoms:** Uploading an image or capturing camera frames displays: `Backend Unavailable: Endpoint returned HTML SPA fallback`.
- **Root Cause:** `VITE_API_URL` is empty in Vercel settings or points to the Vercel frontend domain itself. The frontend request was routed to Vercel's static server which responded with `index.html`.
- **Remediation:**
  1. Open Vercel Project Settings > Environment Variables.
  2. Verify that `VITE_API_URL` is set to the external backend URL (e.g., `https://defectvision-api.onrender.com`).
  3. Redeploy on Vercel without build cache.

---

### Incident 2: Browser CORS Blocked ("No 'Access-Control-Allow-Origin' header")
- **Symptoms:** Browser Developer Console shows: `Access to fetch at ... from origin 'https://defectvision-ai.vercel.app' has been blocked by CORS policy`.
- **Root Cause:** The backend's `CORS_ORIGINS` environment variable does not allow the origin, or the domain has a typo.
- **Remediation:**
  1. Inspect the backend environment variable `CORS_ORIGINS`.
  2. Ensure `https://defectvision-ai.vercel.app` is included.
  3. Restart or redeploy the backend service. Note: Project preview URLs are automatically permitted via the configured project-scoped regular expression `^https:\/\/defectvision-ai(-[a-zA-Z0-9_\-]+)?\.vercel\.app$`. Unrelated Vercel projects are strictly denied.

---

### Incident 3: Container Crashes with Exit Code 137 (OOMKilled)
- **Symptoms:** Backend service restarts during model loading or during initial frame inference.
- **Root Cause:** Container memory limit is below 1.5 GB. Loading 15 PatchCore memory banks and PyTorch allocates ~550 MB initially and peaks at ~1.2 GB during batch tensor allocations.
- **Remediation:**
  1. Upgrade the container memory allocation to at least 2 GB RAM (4 GB recommended for concurrent multi-stream inspection).

---

### Incident 4: High Latency (>200 ms per frame)
- **Symptoms:** Live stream FPS drops below 5 FPS, or `processing_time_ms` exceeds 150 ms.
- **Root Cause:** The container is running on a shared fractional vCPU (e.g. 0.1 vCPU free tier) or CPU throttling is active.
- **Remediation:**
  1. Allocate at least 1 dedicated vCPU.
  2. Verify `KMP_DUPLICATE_LIB_OK=TRUE` and OpenMP threads: `OMP_NUM_THREADS=2`.
