# DefectVision AI — Production Deployment Baseline & Architecture Audit

**Document Version:** 1.0.0  
**Audit Date:** 2026-11-17  
**System Status:** Stale Deployed Frontend (39 commits behind) / Backend Unconnected  
**Authoritative Git Branch:** `main` (commit `660accec0ed41d59606eb2bb365153268d6f58a8`)  
**Production Frontend Host:** Vercel (`https://defectvision-ai.vercel.app/`)  
**Active Production Deployed Commit:** `2fd48675bc7515d01cade08376e75fe607dcd112`  

---

## 1. Executive Summary

A comprehensive infrastructure and deployment audit of the DefectVision AI project was performed across GitHub, Vercel, and local runtime environments.

The audit verified two critical findings:
1. **Frontend Version Drift:** The production URL `https://defectvision-ai.vercel.app/` is serving build assets compiled from commit `2fd4867` (authored before the 15-category automatic optical inspection engine and OOD gating implementation), leaving production **39 commits behind `main`**.
2. **Backend Detachment:** The production frontend does not have an active backend connection. Because Vercel only hosts the static Vite bundle and the environment variable `VITE_API_URL` is undefined, the frontend issues API requests to its own domain (`/predict`, `/api/inspect-frame`, `/api/optical-inspection/model-status`). On Vercel, these requests hit the static file server, returning **HTTP 405 Method Not Allowed** for POST requests and **HTTP 200 with HTML (SPA catch-all rewrite)** for GET requests.

This document details the exact technical baseline, diagnostic evidence, root causes, resource requirements for 15-category anomaly detection, and the architectural blueprint to achieve a production-connected system.

---

## 2. Infrastructure Baseline Matrix

| Component | Target / Production Reality | Source of Truth / Identifier | Status |
| :--- | :--- | :--- | :--- |
| **GitHub Repository** | `https://github.com/suryacharan945/DefectVision-AI` | Remote `origin` | Authoritative |
| **Default Branch** | `main` | Commit `660accec0ed41d59606eb2bb365153268d6f58a8` | Fully Passing CI (Run #18) |
| **Feature Branch** | `fix/production-backend-integration` | Branch tracking `origin/main` | Active Working Branch |
| **Vercel Project** | `defectvision-ai` | Project ID `prj_jmVHZCfTfEc6DYJp2nHn51vCJIVF` | Connected to GitHub Repo |
| **Live Frontend URL** | `https://defectvision-ai.vercel.app/` | Vercel Edge Network | Active, Serving Stale Build |
| **Deployed Frontend SHA**| `2fd48675bc7515d01cade08376e75fe607dcd112` | JS Bundle Hash `index-BAvQJhD-.js` | **39 Commits Behind Main** |
| **FastAPI Backend Host** | Unset / Missing in Production | `VITE_API_URL` undefined | **Disconnected (HTTP 405 / HTML Fallback)** |
| **Continuous Integration** | GitHub Actions Workflow `ci.yml` | Workflow Run #20 & PR #3 | **100% Green (62 Passed, 2 Skipped)** |

---

## 3. Live Production Endpoint Audit

Live HTTP audit was executed directly against `https://defectvision-ai.vercel.app/`:

```
================================================================================
AUDITING PRODUCTION FRONTEND: https://defectvision-ai.vercel.app/
================================================================================

[1] GET /
  -> Status: 200 OK
  -> Content-Type: text/html; charset=utf-8
  -> Title: DefectVision AI - Industrial Anomaly Detection
  -> Discovered Script: /assets/index-BAvQJhD-.js
  -> Discovered CSS:    /assets/index-D7U5R7L3.css
  -> Script matched commit: 2fd48675bc7515d01cade08376e75fe607dcd112 (39 commits behind main!)

[2] GET /api/
  -> Status: 200 OK
  -> Content-Type: text/html; charset=utf-8
  -> Observation: Returns HTML SPA container, NOT JSON API health response.

[3] GET /api/optical-inspection/model-status
  -> Status: 200 OK
  -> Content-Type: text/html; charset=utf-8
  -> Observation: Returns HTML SPA container, NOT JSON model registry.

[4] POST /predict
  -> Status: 405 Method Not Allowed
  -> Observation: Vercel static hosting rejects HTTP POST requests.

[5] POST /api/inspect-frame
  -> Status: 405 Method Not Allowed
  -> Observation: Vercel static hosting rejects HTTP POST requests.
```

### Key Behavioral Consequences:
- When a user uploads an image on the live website, the browser sends `POST https://defectvision-ai.vercel.app/predict`.
- Vercel rejects the request with `HTTP 405 Method Not Allowed`.
- In the legacy code on `2fd4867`, this triggered a fallback that could confuse users or leave them with an uninformative error.
- Live camera inspection cannot capture or route frames to PatchCore models because no backend is answering at the frontend origin.

---

## 4. Root Cause Analysis: Frontend & Backend Disconnect

```
+---------------------------------------------------------------------------------------+
|                                    CURRENT STATE                                      |
|                                                                                       |
|   User Browser                     Vercel Edge CDN                 Backend (Nowhere)  |
|  +-------------+                 +------------------+             +-----------------+ |
|  |             |  POST /predict  |                  |             |                 | |
|  | Live Client | --------------> | defectvision-ai  |    XXXXX    |  FastAPI Host   | |
|  |             | <-------------- | .vercel.app      |             |  (Not Deployed) | |
|  +-------------+   HTTP 405      | (Static SPA only)|             +-----------------+ |
|                                  +------------------+                                 |
+---------------------------------------------------------------------------------------+

+---------------------------------------------------------------------------------------+
|                                  TARGET ARCHITECTURE                                  |
|                                                                                       |
|   User Browser                     Vercel Edge CDN                Container Cloud     |
|  +-------------+                 +------------------+            +------------------+ |
|  |             |  Static Assets  |                  |            | FastAPI Backend  | |
|  | Live Client | <============== | defectvision-ai  |            | (Docker Container| |
|  |             |                 | .vercel.app      |            |  Render/Railway) | |
|  |             |                 +------------------+            +------------------+ |
|  |             |                                                          ^           |
|  |             |          API Requests (VITE_API_URL)                     |           |
|  |             | ---------------------------------------------------------+           |
|  |             | <--------------------------------------------------------+           |
|  +-------------+          JSON Responses & Anomaly Maps                               |
+---------------------------------------------------------------------------------------+
```

### Technical Root Causes:
1. **Serverless Limitations for ML Weights:**
   - The DefectVision AI backend uses PyTorch, FAISS, and 15 PatchCore memory banks (`~360 MB` total).
   - Standard Vercel Serverless Functions enforce a 50 MB / 250 MB compressed artifact size limit and a 10s-15s execution timeout on hobby/pro tiers, making direct Vercel hosting of PyTorch + 15 memory banks unviable.
2. **Missing Environment Configuration:**
   - The frontend was architected with `import.meta.env.VITE_API_URL || ''`.
   - In production, no `VITE_API_URL` was defined in the Vercel project environment dashboard.
   - Consequently, `BASE_URL` defaulted to empty string `''`, directing all API traffic to the Vercel frontend host.
3. **Repository Build Directory:**
   - The repository root contains both `DefectVisionAI/` (backend) and `frontend/` (Vite SPA).
   - `.vercelignore` properly ignores `DefectVisionAI/`, `models/`, and `*.pth` to allow the frontend to compile cleanly. However, without a companion backend deployment, the frontend operates in a detached state.

---

## 5. Machine Learning Resource Specifications (15 Categories)

To ensure high-performance, real-time inspection in cloud deployment, the hardware and memory requirements were measured:

| Resource Dimension | Requirement | Technical Notes |
| :--- | :--- | :--- |
| **RAM Footprint (Static Models)** | ~550 MB | 15 PatchCore memory banks (360 MB) + EfficientNet-B0 classifier (17 MB) + Embedding extractors |
| **RAM Footprint (Peak Runtime)** | 1.2 GB – 1.8 GB | Peak during concurrent image batch tensor transformation and FAISS neighbor searches |
| **Recommended Cloud Memory** | **2.0 GB minimum (4.0 GB recommended)** | Prevents Out-Of-Memory (OOM) kernel kills under sustained camera frame streaming |
| **CPU Recommendation** | 1 to 2 vCPUs | Python 3.11 / 3.12 with PyTorch CPU-optimized wheels and OpenMP threading |
| **Disk Storage** | ~2.5 GB container image | Slim Debian/Ubuntu container with CPU PyTorch, OpenCV headless, FAISS-cpu, and model checkpoints |
| **Per-Frame Inference Latency** | 35 ms – 55 ms (CPU) | ResNet-18 patch feature extraction + FAISS index distance computation |

> [!NOTE]
> **Cloud Provider Plan Mapping:**
> - **Render:** Recommended production tier is `plan: 2c-4g` (2 vCPUs, 4 GB RAM); lower-cost minimum is `plan: 1c-2g` (1 vCPU, 2 GB RAM). Legacy `starter` (512 MB) is unsuitable and will fail with OOM.
> - **Owner Approval Required:** Render cloud services are paid. No cloud deployment should be initiated without repository owner approval of the recurring cost.

---

## 6. Execution Plan & Hardening Milestones

The following hardening milestones were executed and validated on branch `fix/production-backend-integration` (PR #3):

1. **Frontend API Hardening (`frontend/src/api/client.js` & `frontend/src/App.jsx`):**
   - Normalized `VITE_API_URL` (stripped trailing slashes, validated URL structure).
   - Detects HTML SPA fallback responses (`text/html`) and throws explicit `ApiError('Backend Unavailable: Endpoint returned HTML SPA fallback', 503)`.
   - Truthful health interpretation: No unconditional promotion to `status: 'ready'`. Distinguishes 4 operational states (`LIVE INFERENCE ACTIVE`, `BACKEND DEGRADED`, `BACKEND UNAVAILABLE`, and `DEMO MODE ACTIVE`).
   - Prefixes MJPEG stream URLs with `BASE_URL`.
2. **FastAPI Backend Readiness & CORS Hardening (`DefectVisionAI/app.py`):**
   - Truthful readiness evaluation: Inspects optical engine initialization, category classifier readiness, all 15 category memory banks, and decision thresholds. Returns `status: "ready"`, `"degraded"`, or `"not_ready"`.
   - Project-scoped CORS regex: Replaced broad wildcard with strict project-scoped regex `^https:\/\/defectvision-ai(-[a-zA-Z0-9_\-]+)?\.vercel\.app$` alongside explicit `CORS_ORIGINS`.
   - Unified health endpoints: `/health`, `/api/health`, `/api`, and `/api/`.
3. **Optimized Containerization (`Dockerfile` & `.dockerignore`):**
   - Excluded ~2.5 GB of offline research models, PaDiM artifacts, Autoencoder checkpoints, and plot exports via `.dockerignore`.
   - Retained ~495 MB of genuine production runtime assets (15 PatchCore memory banks, EfficientNet-B0 classifier, FAISS indices, baseline CSVs, demo samples).
   - Added runtime directory scaffolding (`mkdir -p /app/outputs/similarity_search_samples /app/logs /app/batch_inspections`).
4. **CI Docker Build & Container Healthcheck Verification (`.github/workflows/ci.yml`):**
   - Builds container image in CI, starts container detached on port 8000, polls `/health`, asserts `process_reachable: true` and `status: ready`, queries `/api/models/status` verifying 15 categories, and performs graceful teardown.
5. **Comprehensive Integration Test Suite (`tests/test_production_api_integration.py`):**
   - Expanded to 12 automated integration tests covering positive CORS, project preview CORS, unapproved origin rejection, arbitrary domain rejection, truthful degraded state reporting, missing memory bank detection, preflight OPTIONS handling, and frontend health evaluation contracts.

---

## 7. Truthful Backend Readiness & Frontend Health Interpretation

### The "Process Reachable" vs. "Inference Ready" Fallacy
A critical design vulnerability in ML API deployments is confusing network reachability with inference readiness:
- A basic FastAPI server will respond with `HTTP 200 OK` as soon as Uvicorn binds to the socket.
- However, if the resident PatchCore memory banks failed to load (e.g., missing directory or corrupt `.npy`), or the EfficientNet category classifier failed to initialize, any subsequent inspection call (`POST /predict` or `POST /api/inspect-frame`) will fail or return invalid classifications.

### Authoritative Readiness States
`DefectVisionAI/app.py` enforces three distinct health states via `get_system_health()`:

| State | Optical Engine | Classifier Ready | 15 Models Ready | Thresholds Ready | Frontend Banner |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **`ready`** | `true` | `true` | `true` (15/15) | `true` | **`LIVE INFERENCE ACTIVE`** (Emerald) |
| **`degraded`** | `true` | Partial / `false` | `< 15` | Any | **`BACKEND DEGRADED`** (Amber) |
| **`not_ready`** | `false` | `false` | `0` | `false` | **`BACKEND UNAVAILABLE`** (Rose) |

In `frontend/src/api/client.js`, `checkHealth()` parses the backend JSON object strictly:
- If `status === 'ready'` and `optical_engine_ready === true`, the system enters **LIVE INFERENCE ACTIVE**.
- If `status === 'degraded'`, the frontend alerts the operator that certain categories or classifier features are unavailable.
- If network connection fails or status is `not_ready`, the UI surfaces **BACKEND UNAVAILABLE**.
- Demo Mode remains an explicit opt-in state clearly labeled **DEMO MODE ACTIVE (SYNTHETIC FALLBACK)**, preventing operators from mistaking simulated data for genuine optical inspection.

---

## 8. Restricted Project-Scoped CORS Architecture

### Security Vulnerability of Broad Wildcard Regex
Earlier iterations utilized a broad regular expression:
```python
# INSECURE: Matches ANY project on Vercel
allow_origin_regex=r"^https://.*\.vercel\.app$"
```
Because Vercel allows anyone to register subdomains (e.g., `attacker-site.vercel.app`), an arbitrary third-party application hosted on Vercel could make credentialed requests to the DefectVision AI backend, exposing camera telemetry, inspection histories, and model endpoints.

### Hardened Project-Scoped Origin Policy
The production backend now enforces:
```python
PROJECT_PREVIEW_ORIGIN_REGEX = r"^https:\/\/defectvision-ai(-[a-zA-Z0-9_\-]+)?\.vercel\.app$"
```
This regex strictly restricts CORS access to:
1. Production Frontend: `https://defectvision-ai.vercel.app`
2. Genuine Project Preview Deployments: `https://defectvision-ai-git-branch.vercel.app`, `https://defectvision-ai-hash-team.vercel.app`
3. Explicit allowlist: Localhost ports (`http://localhost:5173`, `http://127.0.0.1:5173`, etc.) configured via `CORS_ORIGINS`.

Unrelated Vercel projects (e.g., `https://malicious-project.vercel.app`) and arbitrary domains are strictly rejected without `Access-Control-Allow-Origin` headers.

---

## 9. Container Context Optimization & Runtime Asset Inventory

### Docker Context Reduction
By configuring `.dockerignore` to filter out obsolete research checkpoints and offline evaluation directories, the Docker build context was reduced from **~3.5 GB down to ~550 MB (~84% reduction)**.

### Runtime Asset Inventory Breakdown

| Asset Category | Path | Size | Purpose | Included in Docker |
| :--- | :--- | :---: | :--- | :---: |
| **PatchCore Memory Banks** | `models/patchcore/<15_classes>/` | ~374 MB | Nearest-neighbor anomaly detection for all 15 classes | Yes |
| **Category Classifier** | `models/category_classifier/` | ~33 MB | EfficientNet-B0 weights, metadata, class prototypes | Yes |
| **Feature Baseline** | `models/efficientnet_baseline_v3/` | ~61 MB | Feature extraction weights | Yes |
| **FAISS Defect Indices** | `models/faiss_index/<15_classes>/` | ~26 MB | Similarity retrieval defect galleries | Yes |
| **RAG Knowledge Base** | `models/rag_knowledge_base/` | ~0.01 MB | Maintenance runbooks & defect explanations | Yes |
| **Similarity Demo PNGs** | `outputs/similarity_search_samples/` | ~0.32 MB | 15 category gallery demo images | Yes |
| **Baseline Threshold Reports** | `reports/step9_severity_baselines.csv` | ~0.01 MB | Category decision thresholds & guard bands | Yes |
| **Autoencoder Checkpoints** | `models/autoencoder*` | ~335 MB | Deprecated benchmark model | **Excluded** |
| **PaDiM Feature Models** | `models/padim*` | ~480 MB | Offline research baseline | **Excluded** |
| **Legacy Checkpoints** | `models/checkpoint.pth`, `baseline*` | ~166 MB | Intermediate training artifacts | **Excluded** |
| **Offline Heatmap Dumps** | `outputs/padim*`, `outputs/gradcam*` | ~1.5 GB | Offline benchmark plots & visualizations | **Excluded** |
| **Raw MVTec AD Dataset** | `dataset/` | ~5.0 GB | Uncompressed dataset images | **Excluded** |

---

## 10. Docker Build & Startup Verification in CI

The GitHub Actions workflow (`.github/workflows/ci.yml`) now includes end-to-end container verification:
1. **Build Image:** Executes `docker build -t defectvision-backend:ci .`.
2. **Launch Container:** Starts container detached with environment flags `-e PORT=8000 -e HOST=0.0.0.0`.
3. **Healthcheck Polling:** Iteratively polls `http://localhost:8000/health` up to 45 attempts with 2s sleep intervals.
4. **Contract Assertions:**
   - Verifies `process_reachable: true`.
   - Verifies `status: "ready"`.
   - Queries `http://localhost:8000/api/models/status` and verifies `total_categories: 15`.
5. **Teardown:** Stops and removes the test container cleanly. If any assertion fails, container logs are printed to CI console.

---

## 11. Vercel Git Repository Reconciliation Runbook

To ensure that the production frontend on Vercel deploys automatically from this repository, complete the following reconciliation:

1. **Inspect Vercel Project Git Connection:**
   - Open [Vercel Dashboard](https://vercel.com/dashboard) and select project `defectvision-ai`.
   - Navigate to **Settings** > **Git**.
   - Verify that **Connected Git Repository** points to `suryacharan945/DefectVision-AI`.
   - If pointing to an older fork or detached repository, click **Disconnect** and re-connect `suryacharan945/DefectVision-AI`.
2. **Production Branch Setting:**
   - Under **Production Branch**, ensure it is set to `main`.
3. **Root Directory Configuration:**
   - In **Settings** > **General**, verify **Root Directory** is set to `frontend` (or left blank if using the root `package.json` proxy build).
4. **Environment Variables:**
   - In **Settings** > **Environment Variables**, ensure `VITE_API_URL` is set to the deployed backend URL (e.g., `https://defectvision-backend.onrender.com`).
5. **Trigger Verification Deployment:**
   - Under **Deployments**, select **Redeploy** on the latest commit with cache disabled to verify live connection.
