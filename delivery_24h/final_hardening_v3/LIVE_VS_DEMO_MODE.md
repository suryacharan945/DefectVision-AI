# LIVE INFERENCE VS. DEMO MODE SPECIFICATION & AUDIT

**Project:** DefectVision AI  
**Release Target:** Commit `91d3743` / `delivery_24h/final_hardening_v3`  
**Audit Date:** October 31, 2026  
**Auditor:** Lead AI/ML Verification & Full-Stack Release Engineer  

---

## 1. Executive Summary & Policy Mandate

Prior iterations of the frontend deployed on static CDN hosts (e.g., Vercel) silently executed client-side trigonometric formulas (`Math.sin`, `Math.cos`) when the Python backend was unreachable, presenting synthetic numbers as authentic machine learning inferences. 

In strict adherence to experimental integrity and industrial safety:
> **POLICY MANDATE:**  
> Under no circumstances may synthetic or prerecorded data be displayed as authentic ML model predictions. When the genuine neural network backend is offline, prediction controls must be **disabled by default**, requiring explicit user opt-in to enter clearly labeled demonstration mode.

---

## 2. Three-Tier Operational State Machine

The frontend client now enforces three mutually exclusive operating modes:

```
                          +------------------------------------------------+
                          |                APP INITIALIZATION              |
                          +------------------------------------------------+
                                                  |
                                                  v
                                     [Poll GET /api/ on Port 8000]
                                                  |
                      +---------------------------+---------------------------+
                      |                                                       |
            (HTTP 200 Received)                                    (Connection Refused / 404)
                      |                                                       |
                      v                                                       v
        +---------------------------+                           +---------------------------+
        |   MODE 1: LIVE INFERENCE  |                           |     BACKEND OFFLINE       |
        +---------------------------+                           +---------------------------+
        | - Green UI Banner Active  |                                         |
        | - Full PyTorch + FAISS    |                                         v
        | - Prediction Enabled      |                           Does user opt into Demo Mode?
        | - Live Anomaly Heatmap    |                                         |
        +---------------------------+                     +-------------------+-------------------+
                                                          |                                       |
                                                       (YES)                                     (NO)
                                                          |                                       |
                                                          v                                       v
                                            +---------------------------+           +---------------------------+
                                            |    MODE 2: DEMO MODE      |           | MODE 3: BACKEND BLOCKED   |
                                            +---------------------------+           +---------------------------+
                                            | - Amber Warning Banner    |           | - Red Warning Callout     |
                                            | - Explicit "SYNTHETIC" tag|           | - Prediction Disabled     |
                                            | - Local Mock Simulation   |           | - Clear Error Message     |
                                            | - Never cited in research |           | - "Retry Connection" CTA  |
                                            +---------------------------+           +---------------------------+
```

---

## 3. Implementation Details & Code Changes

### 3.1. Centralized API Client (`frontend/src/api/client.js`)
- **Explicit Demo Mode Flag:** Maintained via `_demoModeEnabled` with persistence in `localStorage.getItem('defectvision_demo_mode')`.
- **Health Check Decoupling:** When `request('/api/')` fails, `checkHealth()` no longer falsely reports `{ status: 'ready', mode: 'edge-cloud' }`. It returns `{ status: 'offline', mode: _demoModeEnabled ? 'demo' : 'unavailable', is_live: false }`.
- **Inference Protection:** In `predict()` and `inspectFrame()`:
  - If backend is reachable: Returns genuine inference payload marked with `is_demo: false, inference_mode: 'LIVE (Verified PyTorch + FAISS)'`.
  - If backend is offline AND `!_demoModeEnabled`: Throws an `ApiError(503, "Real inference cannot be performed: backend offline.")`.
  - If backend is offline AND `_demoModeEnabled`: Returns simulation explicitly tagged with `is_demo: true, inference_mode: 'DEMO MODE (Synthetic Simulation — Not Genuine ML)', warning: 'DEMONSTRATION ONLY'`.

### 3.2. Top Operating Mode Banner (`frontend/src/App.jsx`)
A full-width status banner sits prominently above the workspace:
- **Mode 1 (Live):**  
  `🟢 LIVE INFERENCE ACTIVE | Resident PyTorch CPU + FAISS Memory Bank (Port 8000) — 15 Categories Ready`
- **Mode 2 (Demo):**  
  `🟡 DEMO MODE ACTIVE | Synthetic simulation only. Real ML inference disabled. [Retry Live Backend] [Exit Demo]`
- **Mode 3 (Offline / Unavailable):**  
  `🔴 BACKEND UNAVAILABLE | Local daemon offline. Real model execution blocked. [Check 127.0.0.1:8000] [Enter Demo Mode]`

### 3.3. Specimen Inspection Workspace (`frontend/src/components/sections/InspectSection.jsx`)
- **Blocked State Callout:** If backend is offline and user has not enabled demo mode, a rose-tinted banner appears:
  `"Real Model Execution Offline: The local Python backend daemon (FastAPI on port 8000) is unreachable."`
- **Control Disabling:** The primary action button displays:
  `"Inference Disabled (Backend Offline)"` with `disabled={true}` and a lock cursor.
- **Result Provenance Tagging:** When inspection results are displayed:
  - If `is_demo: false`: Displays an emerald badge:
    `🟢 LIVE INFERENCE: Verified EfficientNet-B0 v3 + PatchCore Execution (Score: 4.5088 | Thresh: 1.4138) [Verified PyTorch CPU]`
  - If `is_demo: true`: Displays an amber badge:
    `⚠️ DEMO MODE: Synthetic client-side simulation. NOT genuine neural network predictions. [Backend Server Offline]`

### 3.4. Sidebar Telemetry (`frontend/src/components/ui/SidebarNav.jsx`)
The bottom engine card dynamically reflects true status:
- `ONLINE (LIVE ML)` with pulsating green beacon when connected.
- `DEMO MODE` with amber indicator when demo mode is active.
- `OFFLINE` with solid red beacon when disconnected.

---

## 4. Visual Proof & Browser Verification Screenshots

Both operational states were independently exercised and captured using automated Puppeteer browser sessions:

| Mode | Captured Screenshot Artifact | Visual Distinguishers |
| :--- | :--- | :--- |
| **Live Local Inference** | [`browser_live_inference.png`](file:///c:/Users/surya/Downloads/Mini%20Project/delivery_24h/final_hardening_v3/test_outputs/browser_live_inference.png) | Green banner `LIVE INFERENCE ACTIVE`; true PatchCore score `4.5088` vs threshold `1.4138`; verified spatial crack heatmap; `Verified PyTorch CPU` badge. |
| **Demonstration Mode** | [`browser_demo_mode.png`](file:///c:/Users/surya/Downloads/Mini%20Project/delivery_24h/final_hardening_v3/test_outputs/browser_demo_mode.png) | Amber banner `DEMO MODE ACTIVE`; explicit disclaimer that simulation is running client-side; "Exit Demo" action button. |

---

## 5. Cloud Hosting Constraints (Why Vercel Cannot Run Real Models)

Industrial inspection backends require significant runtime resources:
- **PyTorch CPU Wheel:** $\approx 180\text{ MB}$ uncompressed.
- **TorchVision + Timm:** $\approx 45\text{ MB}$.
- **FAISS CPU:** $\approx 25\text{ MB}$.
- **PatchCore Coreset Memory Banks (15 categories):** $\approx 65\text{ MB}$.
- **Resident RAM Footprint:** $\approx 850\text{ MB}$ during vector searches.

**Vercel Serverless Function Limits:**
- Serverless maximum unzipped bundle size: $250\text{ MB}$ (exceeded by PyTorch alone).
- Serverless memory limit: Standard tier defaults to $1024\text{ MB}$ with aggressive cold-start eviction.
- Execution timeout: $10\text{--}15\text{ seconds}$ on standard tiers.

### Recommended Production Deployment Topology:
To host genuine Live Inference in the cloud:
1. Deploy the React frontend on **Vercel** (`https://defectvision-ai.vercel.app`).
2. Deploy the Python backend on a dedicated container runtime with $\ge 2\text{GB RAM}$ (e.g., **AWS ECS, GCP Cloud Run, or Railway Docker**).
3. Set `VITE_API_URL=https://api.defectvision.yourdomain.com` in Vercel environment variables.
