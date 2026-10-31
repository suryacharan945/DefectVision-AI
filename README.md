# DefectVision AI — Autonomous Industrial Anomaly Detection Platform

[![Live Demo on Vercel](https://img.shields.io/badge/Live%20Demo-defectvision--ai.vercel.app-success?style=for-the-badge&logo=vercel)](https://defectvision-ai.vercel.app/)
[![GitHub Repo](https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github)](https://github.com/suryacharan945/DefectVision-AI)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![React](https://img.shields.io/badge/react-19.2-cyan)
![TailwindCSS](https://img.shields.io/badge/tailwindcss-4.3-teal)
![PyTorch](https://img.shields.io/badge/PyTorch-2.15%2Bcpu-orange)
![Release Status](https://img.shields.io/badge/Release-Conditional%20GO-amber)

> **Live Demonstration Deployment**: [**https://defectvision-ai.vercel.app/**](https://defectvision-ai.vercel.app/)  
> **Documentation & Audit Suite**: [`delivery_24h/final_hardening_v3/`](delivery_24h/final_hardening_v3/)

**DefectVision AI** is a production-hardened industrial visual anomaly detection platform combining unsupervised memory-bank localization (**PatchCore**), supervised classification (**EfficientNet-B0 v3**), real-time optical streaming, grounded **RAG defect engineering copilot**, and a selective human-review research framework across the 15 categories of the MVTec Anomaly Detection benchmark.

---

## 1. Operating Modes & Deployment Topology

DefectVision AI supports two distinct operational modes:

| Dimension | Mode A: Local Verified Production Stack | Mode B: Cloud Demonstration (Vercel) |
| :--- | :--- | :--- |
| **Execution Engine** | Resident PyTorch 2.15 CPU + FAISS Vector Search | Client-side JavaScript in Web Browser |
| **Backend Daemon** | FastAPI on `http://127.0.0.1:8000` | None (Static CDN edge deployment) |
| **Model Inference** | **GENUINE NEURAL INFERENCE** | **SYNTHETIC DEMO SIMULATION** |
| **Anomaly Localization**| True patch-level distance heatmap (OpenCV) | Static canned overlays & simulated metrics |
| **UI Indicator** | `🟢 LIVE INFERENCE ACTIVE` | `🟡 DEMO MODE ACTIVE` |
| **Offline Handling** | Full functionality | Controls disabled unless Demo Mode opted-in |
| **Academic Citation** | **Valid for physical benchmarking** | **STRICTLY PROHIBITED FOR RESEARCH BENCHMARKS** |

---

## 2. Local Installation & Setup

### 2.1. System Prerequisites
- **Operating System:** Windows 10/11, Ubuntu 22.04+, or macOS
- **Python:** Python 3.10, 3.11, or 3.12 (Python 3.12.9 recommended)
- **Node.js:** Node.js 18+ and npm

### 2.2. Python Backend Setup
```bash
# Clone the repository
git clone https://github.com/suryacharan945/DefectVision-AI.git
cd DefectVision-AI

# Create isolated virtual environment
python -m venv .venv

# Activate virtual environment
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate

# Install required backend dependencies
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install timm faiss-cpu opencv-python-headless albumentations transformers sentence-transformers scikit-learn scipy fastapi uvicorn python-multipart
```

### 2.3. Frontend Setup
```bash
# Install frontend dependencies
npm install --prefix frontend
```

### 2.4. Required Model Artifacts
Ensure the following pretrained weights are present:
- `DefectVisionAI/models/efficientnet_baseline_v3/best_model.pt` (SHA-256: `f470b7...`)
- `DefectVisionAI/models/patchcore/{category}/memory_bank.npy` (15 categories, ~65MB total)
- `DefectVisionAI/reports/step9_severity_baselines.csv` (Category p99 thresholds)

---

## 3. Starting the Application

### Step 1: Launch FastAPI Backend Daemon
```bash
# From repository root (with .venv activated):
cd DefectVisionAI
python -m uvicorn app:app --host 127.0.0.1 --port 8000
```
*Backend initializes in ~4 seconds; confirm `GET http://127.0.0.1:8000/` returns `status: "ready"`.*

### Step 2: Launch Vite Frontend Dev Server
```bash
# In a separate terminal:
npm run dev --prefix frontend
```
*Frontend opens at `http://localhost:5173/`, automatically proxying API calls to port 8000.*

---

## 4. Real Inference Workflow & Hybrid Decision Rule

1. **Specimen Routing:** The operator selects a product category (e.g. `bottle`, `cable`, `screw`). The system routes the specimen to the matching category PatchCore memory bank.
2. **Dual-Model Inference:**
   - **PatchCore:** Extracts multi-scale patch features from WideResNet-50 layers 2+3, queries the FAISS coreset index, and computes maximum nearest-neighbor distance $s(X)$.
   - **EfficientNet-B0 v3:** Evaluates supervised sigmoid defect probability $p(X)$.
3. **Hybrid Decision Rule (Safety Operating Mode):**
   $$\text{Decision} = \text{"defective"} \iff (s(X) > \tau_c \lor p(X) \ge 0.50)$$
   *Eliminates defect escapes on structural fractures where supervised texture features shift. Evaluated on 869 development specimens, cutting escapes by 51.6% (15 vs 31 escapes).*
4. **Spatial Anomaly Heatmap:** Bilinear interpolation projects patch distances onto the 224x224 RGB image, localized via Jet colormap overlay.
5. **Batch Processing:** Multi-file asynchronous worker queue with downloadable MES-compliant CSV and JSON reports.

---

## 5. Demo Mode Limitations

When accessed via Vercel without a local backend:
- The top banner displays: `🟡 DEMO MODE ACTIVE`.
- Real ML inference cannot be executed on static edge servers due to bundle limits (PyTorch + FAISS requires >850MB resident memory).
- If the backend goes offline, the UI alerts the user: `🔴 BACKEND UNAVAILABLE` and disables prediction controls to prevent misleading operators.
- Users can explicitly toggle **Demo Mode** to preview UI workflows using prerecorded sample data.

---

## 6. Known Scientific & Evaluation Limitations

In adherence to experimental integrity:
1. **Historical Benchmark Exposure:** The 856-image benchmark was partitioned post-hoc from an exposed test set after early development. It must be cited as an **Internal Development-Evaluated Partition**, NOT an untouched external test set.
2. **CPND Implementation Status:** The proposed *Calibrated Patch-Neighborhood Dispersion (CPND)* algorithm remains an **unimplemented theoretical proposal**. Metrics previously attributed to CPND originated from Supervised Margin Uncertainty on EfficientNet-B0.
3. **Chukyo Dataset Quarantine:** The external Chukyo factory dataset contains 14 identical capture pairs and duplicate frames; it is strictly quarantined in cold storage and excluded from all active inference and benchmark pipelines.

---

## 7. Research Experiment Foundation (`DefectVisionAI/research/`)

For future journal submissions (IEEE T-II, Pattern Recognition), a modular evaluation framework is provided in `DefectVisionAI/research/`:

```bash
# Run baseline selective review comparison across 4 policies:
python DefectVisionAI/research/run_baseline_comparison.py
```

### Certified Baseline Results (10% Human Review Budget, K = 172 images):
- **Uniform Random Selection:** $8.11\%$ error capture rate
- **Highest Anomaly Score:** $0.00\%$ error capture rate (catastrophic failure: reviews only blatant defects)
- **PatchCore Distance to Decision Threshold:** **$21.62\%$ error capture rate** ($2.7\times$ over random)
- **Supervised Margin Uncertainty ($|p - 0.5|$):** **$91.89\%$ error capture rate** ($95\%$ Bootstrap CI: $[78.79\%, 97.83\%]$)

> **Novelty Mandate for CPND:** Any future implementation of CPND on PatchCore must prove incremental error capture over the $21.62\%$ distance-to-threshold baseline before claiming novelty.

---

## 8. Test Execution & Verification Commands

All release claims are backed by executable automated test scripts:

```bash
# 1. Standalone CPU Inference Test
python scripts/test_backend_inference.py

# 2. End-to-End Live API Suite
python scripts/e2e_backend_test.py

# 3. Hybrid Decision Rule Evaluation
python scripts/evaluate_hybrid_decision_rule.py

# 4. Latency Profiler
python scripts/benchmark_inference_latency.py

# 5. Full Browser E2E Automation (Puppeteer / Chromium)
node scripts/verify_browser_e2e.js

# 6. Metric Reconciliation
python scripts/reconcile_step11_provenance.py
```

---

## 9. License & Ethical Research Commitment

This project is licensed under the MIT License. All benchmark claims, datasets, and models are disclosed under open science standards with complete provenance tracking.
