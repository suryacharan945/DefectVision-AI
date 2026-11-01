# DefectVision AI — Final Validation & Demonstration Script

**Document Version:** 1.0  
**Effective Date:** 2026-11-01  
**Sprint Phase:** Phase 6 Final Demonstration & Operational Protocol  
**Repository State:** Frozen Local Research Prototype & GitHub Clean-Room Release

---

## 1. System Requirements & Setup

### Environment:
- **Operating System:** Windows 10/11 or Ubuntu 22.04 LTS (x86_64)
- **Python Version:** 3.12.x (64-bit)
- **Hardware Minimum:** 4-Core CPU, 8 GB RAM (No dedicated GPU required)
- **Virtual Environment:** Active virtual environment (`.venv`) with verified dependencies:
  - `torch==2.15.0+cpu`
  - `torchvision`
  - `timm==1.1.2`
  - `faiss-cpu==1.15.1`
  - `fastapi==0.115.0`
  - `uvicorn==0.31.0`
  - `opencv-python==4.10.0.84`
  - `scikit-learn==1.9.1`

---

## 2. Step-by-Step Demonstration & Verification Runbook

### Step 1: Model Artifacts Integrity Check
Verify SHA-256 cryptographic hashes and shapes of all 15 category PatchCore memory banks and the EfficientNet-B0 v3 classifier:
```powershell
.venv\Scripts\python.exe scripts\verify_model_artifacts.py
```
**Expected Outcome:**
- 15/15 categories report valid shape `(N, 384)`.
- EfficientNet checkpoint verified (16,336,185 bytes, 360 tensor keys).
- Manifest output: `release/final_18h_validation/verified_model_artifacts.csv`.

---

### Step 2: Deterministic Real Inference & API Equivalence Verification
Demonstrate bitwise mathematical equivalence between direct Python function execution and FastAPI HTTP endpoints (`/predict` and `/inspect-frame`):
```powershell
.venv\Scripts\python.exe scripts\verify_real_inference_deterministic.py
```
**Expected Outcome:**
- Exact numerical match ($\Delta = 0.00\times 10^0$) between direct inference and `/predict`.
- Negligible delta ($\le 1.6\times 10^{-5}$) on `/inspect-frame` due to deliberate 4-decimal formatting.
- 5-run repeated inference produces variance $= 0.000000$ (perfect determinism).
- Manifest output: `release/final_18h_validation/inference_verification_matrix.csv`.

---

### Step 3: Comprehensive Quantitative Benchmark Evaluation
Execute full quantitative evaluation across the 856 primary benchmark images:
```powershell
.venv\Scripts\python.exe scripts\run_quantitative_evaluation.py
```
**Expected Outcome:**
- Complete per-specimen predictions in `release/final_18h_validation/evaluation_predictions.csv`.
- Aggregate metrics in `release/final_18h_validation/evaluation_metrics.csv`.
- Per-category breakdown in `release/final_18h_validation/per_category_metrics.csv`.
- Confusion matrices in `release/final_18h_validation/confusion_matrices.json`.

---

### Step 4: Reliability & Operational Resilience Stress Test
Verify API stability against corrupt payloads, unknown categories, SQL injection strings, and extreme aspect ratios:
```powershell
.venv\Scripts\python.exe scripts\run_reliability_stress_test.py
```
**Expected Outcome:**
- 6/6 reliability tests PASS.
- Corrupted payloads return clean HTTP 400 Bad Request.
- Malicious and unknown categories rejected safely.
- Ultra-wide (1200x50) and high-resolution (2048x2048) images process without memory faults.
- Manifest output: `release/final_18h_validation/reliability_test_results.csv`.

---

### Step 5: Robustness & Photometric Perturbation Benchmark
Stress test dual-model classification against noise ($\sigma=0.05, 0.10$), brightness ($\pm 20\%$), contrast ($\pm 20\%$), blur, and rotation ($\pm 5^\circ$):
```powershell
.venv\Scripts\python.exe scripts\run_robustness_benchmark.py
```
**Expected Outcome:**
- Manifest output: `release/final_18h_validation/robustness_results.csv`.
- Hybrid decision rule maintains defect detection under lighting and orientation shifts.

---

### Step 6: Edge Latency & Component Breakdown Profiling
Profile end-to-end processing speeds across 50 iterations:
```powershell
.venv\Scripts\python.exe scripts\run_latency_benchmark.py
```
**Expected Outcome:**
- PatchCore FAISS query: $\approx 35\text{--}40$ ms.
- EfficientNet-B0 inference: $\approx 18\text{--}22$ ms.
- In-memory frame API round-trip: $\approx 70\text{--}85$ ms.
- Manifest output: `release/final_18h_validation/latency_benchmark.csv`.

---

### Step 7: Launch Interactive Local Inspection Server
Launch the production FastAPI application:
```powershell
.venv\Scripts\python.exe -m uvicorn DefectVisionAI.app:app --host 127.0.0.1 --port 8000
```
- Open browser at `http://127.0.0.1:8000/`.
- Interactive live stream with animated holographic reticles: `http://127.0.0.1:8000/stream/bottle`.
- Interactive Swagger API docs: `http://127.0.0.1:8000/docs`.
