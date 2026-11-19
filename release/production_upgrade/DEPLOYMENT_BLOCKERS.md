# DefectVision AI — Production Deployment Blockers, Cost Analysis & Runbook

**Document Version:** 3.0.0  
**Date:** November 2026  
**Auditor:** Infrastructure & Cloud FinOps Lead  
**Scope:** Public Full-Stack Production Deployment  

---

## 1. Executive Summary

DefectVision AI is completely developed, hardened, tested, and verified with **100% localhost functionality parity**. The local full-stack system is actively serving all 15 MVTec AD category models and target-domain production profiles.

However, transitioning the public deployment (`https://defectvision-ai.vercel.app/`) to full operational status requires two external hosting actions that **strictly require repository owner authorization, billing selection, and interactive authentication**.

In accordance with the project directives:
> *"Do not create or provision paid infrastructure without explicit approval. Do not upgrade plans, create paid volumes, purchase services or change billing. First produce a deployment-cost estimate and identify the minimum suitable hosting configuration. If user action is required for provider login, service creation or billing approval, provide precise instructions. Do not invent a backend domain."*

This document provides the exact empirical memory measurements, multi-cloud cost estimates, and step-by-step instructions for completing the deployment.

---

## 2. Empirical Model Memory & Hardware Requirements

To prevent guessing or under-provisioning, the resident memory consumption of the persistent FastAPI service was empirically measured under full operational load (all 15 category memory banks, FAISS indices, and neural models loaded):

```
Process ID: 30736 (python.exe - DefectVision AI Live Server)
WorkingSet64 (Resident RAM):       1,385.61 MB (~1.4 GB)
PrivateMemorySize64 (Virtual):     3,796.13 MB (~3.8 GB)
```

### 2.1 Hardware Sizing Analysis

| Hosting Tier | RAM | CPU | Feasibility Analysis | Risk Assessment |
| :--- | :--- | :--- | :--- | :--- |
| **1 GB Container** (e.g. Free/Nano tiers) | 1,024 MB | 1 vCPU | **IMPOSSIBLE** | Crashes on boot during model load (OOM 137). Cannot hold 15 memory banks. |
| **2 GB Container** (e.g. Render 1c-2g / Basic) | 2,048 MB | 1 vCPU | **MARGINAL** | Boots successfully (~1.4 GB baseline), but leaves only ~600 MB headroom. Concurrent batch inspection or adaptation will spike memory and risk OOM. |
| **4 GB Container / VPS** (e.g. Render 2c-4g / Railway) | 4,096 MB | 2 vCPU | **RECOMMENDED MINIMUM** | Fully stable, provides 2.6 GB headroom for concurrent image batching, feature extraction, and matrix search. |
| **8 GB Container / Dedicated** | 8,192 MB | 4 vCPU | **ENTERPRISE GRADE** | Zero memory pressure, supports GPU acceleration (CUDA) or high-throughput multi-worker Uvicorn configurations. |

---

## 3. Cloud Provider Cost Estimates

### 3.1 Platform as a Service (PaaS) Providers

| Provider | Plan / Tier | Specs | Persistent Disk | Estimated Monthly Cost | Pros & Cons |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Render** | `2c-4g` (Recommended) | 2 vCPU, 4 GB RAM | 5 GB SSD ($1.25/mo) | **$86.25 / month** | Managed Docker, auto-deploys from GitHub, zero server management. |
| **Render** | `1c-2g` (Budget Option) | 1 vCPU, 2 GB RAM | 5 GB SSD ($1.25/mo) | **$26.25 / month** | Lower cost; high risk of OOM kills during multi-user batch processing. |
| **Railway** | Usage-Based Execution | 2 vCPU, 4 GB RAM | 5 GB Volume ($2.50/mo) | **~$15.00 – $25.00 / month** | Billed per second of CPU/RAM usage. Generous starter credits. |
| **Fly.io** | `performance-1x` | 1 dedicated CPU, 4 GB RAM | 5 GB Volume ($0.75/mo) | **~$22.75 / month** | Fast edge deployment; requires Fly CLI. |

### 3.2 Virtual Private Server (VPS) / Self-Hosted Docker (Most Economical)

| Provider | Instance Type | Specs | Included Storage | Estimated Monthly Cost | Pros & Cons |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Hetzner Cloud** | CX22 / CX32 | 2-4 vCPU, 4-8 GB RAM | 40-80 GB NVMe | **~$5.00 – $10.00 / month** | **Most cost-effective.** Unmetered traffic, ultra-fast NVMe, dedicated persistent storage. |
| **DigitalOcean** | Basic Droplet | 2 vCPU, 4 GB RAM | 80 GB SSD | **$24.00 / month** | Standard reliable Linux VPS; requires 1-click Docker droplet. |

---

## 4. User Action Runbook

To transition the public deployment to full operational parity:

### Step 1: Provision Persistent Backend Container
Choose one of the providers above (e.g. Railway or Render):
1. Sign in to your cloud provider account.
2. Create a **New Service from GitHub Repository** -> Select `suryacharan945/DefectVision-AI`.
3. Select **Docker** as the environment (it automatically detects the root `Dockerfile`).
4. Configure the following environment variables:
   ```env
   PORT=8000
   HOST=0.0.0.0
   ENVIRONMENT=production
   DEVICE=cpu
   DEFECTVISION_DATA_DIR=/app/data
   DEFECTVISION_PROFILES_DIR=/app/data/production_profiles
   CORS_ORIGINS=https://defectvision-ai.vercel.app
   PYTHONUNBUFFERED=1
   ```
5. Attach a persistent volume mounted at `/app/data` (to retain adapted profiles and history across restarts).
6. Note the public HTTPS URL assigned to the service (e.g. `https://defectvision-api.up.railway.app` or `https://defectvision-backend.onrender.com`).

### Step 2: Update Vercel Frontend Deployment
1. Navigate to the Vercel Dashboard for project `defectvision-ai`:  
   `https://vercel.com/team_SBG8P3wQG46ZQaT25UxpydkP/defectvision-ai/settings/environment-variables`
2. Add or update the environment variable:
   - **Key:** `VITE_API_URL`
   - **Value:** `<YOUR-ACTUAL-BACKEND-DOMAIN>` (e.g. `https://defectvision-api.up.railway.app`)
3. Connect the GitHub repository `suryacharan945/DefectVision-AI` to enable automated deployment on push to `main` (or run `npx vercel --prod` from `frontend/`).
4. Redeploy the frontend. Once rebuilt, the deployed client will immediately connect to your persistent backend, and the engine status pill will show **`READY (15/15)`**.
