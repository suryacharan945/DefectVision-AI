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
| **Continuous Integration** | GitHub Actions Workflow `ci.yml` | Workflow Run #18 on `main` | **100% Green (50 Passed, 2 Skipped)** |

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

---

## 6. Action Plan for Production Readiness

1. **Frontend API Hardening (`frontend/src/api/client.js`):**
   - Normalize `VITE_API_URL` (strip trailing slashes, validate URL structure).
   - Detect HTML SPA fallback responses (text/html) and throw explicit `ApiError('Backend Unavailable: Endpoint returned HTML SPA fallback', 503)`.
   - Fix `getStreamUrl` to prepend `BASE_URL`.
   - Prevent silent degradation: Demo Mode must be strictly opt-in; LIVE mode must report truthful connectivity diagnostics.
2. **FastAPI Backend Hardening (`DefectVisionAI/app.py`):**
   - Add dynamic CORS middleware supporting `https://defectvision-ai.vercel.app`, Vercel preview domains (`https://*.vercel.app`), and local development hosts.
   - Add dedicated health endpoints (`/health`, `/api/health`, `/api/`, `/api`) returning JSON status with model registry verification.
   - Bind host and port dynamically via `HOST` and `PORT` environment variables.
3. **Containerization & Deployment Runbook:**
   - Provide a production-ready `Dockerfile` targeting Python 3.11/3.12 with PyTorch CPU.
   - Provide `render.yaml` and `railway.json` for 1-click cloud deployment.
   - Publish `docs/DEPLOYMENT_RUNBOOK.md` detailing step-by-step instructions for hosting the backend and setting `VITE_API_URL` on Vercel.
4. **Automated Verification:**
   - Execute the 52-test Python test suite.
   - Build the frontend bundle cleanly via `npm run build`.
   - Submit Pull Request from `fix/production-backend-integration` into `main`.
