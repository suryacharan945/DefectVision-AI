# 🔬 DefectVision AI — Autonomous 3D Industrial Defect Inspection Platform

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![React](https://img.shields.io/badge/react-19.2-cyan)
![TailwindCSS](https://img.shields.io/badge/tailwindcss-4.3-teal)
![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-orange)

**DefectVision AI** is a production-grade, full-stack industrial defect inspection platform powered by resident memory-bank anomaly detection (PatchCore), leak-free classification (EfficientNet-B0 v3), real-time optical video streaming, grounded RAG explanation assistance, and interactive 3D sensor core rendering across all 15 categories of the MVTec AD benchmark.

---

## 🌟 Key Features

- **Real-Time Optical Inspection**:
  - **Dual-Source Streaming**: Switch between Client Browser Webcam (`getUserMedia`) or Backend MJPEG Video Stream (`/api/stream/{category}`).
  - **Holographic Reticle HUD**: Neon corner brackets dynamically reacting to severity (`#10B981` Normal/Minor, `#F59E0B` Moderate, `#EF4444` Critical), crosshair tracking reticle, and laser scanline sweep.
  - **Spacebar Snapshot Hotkey**: Instant frame capture triggering in-memory PatchCore feature distance scoring & EfficientNet inference in under ~60ms.
  - **Live Audit Ticker & Split Heatmap Modal**: Tracks all inspected specimens with interactive before/after blend slider and raw anomaly distance maps.
- **Specimen Inspection & Presets**: 1-click test specimen presets across all 15 MVTec AD categories (`bottle`, `cable`, `capsule`, `carpet`, `grid`, `hazelnut`, `leather`, `metal_nut`, `pill`, `screw`, `tile`, `toothbrush`, `transistor`, `wood`, `zipper`).
- **4-Model Benchmark Leaderboard**:
  - **EfficientNet-B0 v3**: 0.9732 Mean AUROC (Best Classifier)
  - **PatchCore**: 0.9651 Mean AUROC (Best Localization)
  - **PaDiM**: 0.8911 Mean AUROC
  - **Autoencoder**: 0.6872 Mean AUROC
- **1,725 Benchmark History Browser**: Searchable, filterable audit log of every official test sample with modal defect overlays.
- **High-Throughput Batch Processing**: Multi-file dropzone with async polling and defect rate distribution analytics.
- **Grounded RAG Defect Copilot**: 16 industrial defect taxonomies and semantic Q&A assistant querying `all-MiniLM-L6-v2` embeddings.
- **Ask the Data**: Natural language conversational analytics calculated directly from inspection logs.
- **Production Drift Monitor & Active Learning / RCA**: 3-stream feature drift detection and review budget sensitivity curves (checking 10.4% uncertain items recovers 82.5% of errors).

---

## 🏗️ Architecture

```
DefectVision AI
├── frontend/                     # React 19 + Vite + Tailwind CSS + Three.js
│   ├── src/
│   │   ├── api/client.js        # Production API client with VITE_API_URL support
│   │   ├── components/3d/       # 3D AI Sensor Core (Three.js / React Three Fiber)
│   │   ├── components/sections/ # Inspection, Models, History, Batch, RAG, Drift, RCA
│   │   ├── pages/               # LiveStreamInspector.jsx (Real-time optical studio)
│   │   └── utils/               # 15 MVTec category metadata
│   ├── vercel.json              # SPA rewrite configuration for Vercel
│   └── package.json
│
├── DefectVisionAI/              # FastAPI High-Throughput Inference Backend
│   ├── app.py                   # Resident model loader & endpoints (/predict, /stream, /inspect-frame)
│   ├── src/                     # PatchCore, severity scoring, similarity, RAG, analytics
│   ├── models/                  # Checkpoints, FAISS indexes, PatchCore memory banks
│   └── reports/ & logs/         # AUROC matrix, severity logs, drift data
│
├── vercel.json                  # Root Vercel build delegation
├── package.json                 # Monorepo build script
└── start_defectvision.bat       # 1-Click local startup launcher
```

---

## 🚀 Deployment to Vercel

### Step 1: Import Repository in Vercel
1. Go to [vercel.com](https://vercel.com/) and click **"Add New Project"**.
2. Select your repository: **`suryacharan945/DefectVision-AI`**.

### Step 2: Configure Project Settings
- **Framework Preset**: `Vite`
- **Root Directory**: Keep `./` (default) or select `frontend`
- **Build Command**: `cd frontend && npm install && npm run build` (or leave default if Root Directory is `frontend`)
- **Output Directory**: `frontend/dist` (or `dist` if Root Directory is `frontend`)

### Step 3: (Optional) Environment Variables
If your FastAPI backend is deployed on a cloud provider (Render, Railway, Fly.io, AWS EC2):
- Add `VITE_API_URL`: `https://your-backend-api.onrender.com`

Click **Deploy**! Vercel will build the frontend and serve your live application.

---

## 💻 Running Locally

### Option A: 1-Click Launcher (Windows)
Double-click [`start_defectvision.bat`](./start_defectvision.bat) to launch both FastAPI and Vite servers.

### Option B: Manual Startup

**1. Launch Backend (Port 8000):**
```bash
cd DefectVisionAI
set KMP_DUPLICATE_LIB_OK=TRUE
python -m uvicorn app:app --host 127.0.0.1 --port 8000
```

**2. Launch Frontend (Port 5173):**
```bash
cd frontend
npm install
npm run dev
```

Open [**`http://localhost:5173`**](http://localhost:5173) in your browser!

---

## 📄 License
This project is licensed under the MIT License.
