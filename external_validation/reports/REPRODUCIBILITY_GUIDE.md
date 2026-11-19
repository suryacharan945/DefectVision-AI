# DefectVision AI — Technical Reproducibility & Replication Guide

**Release Candidate:** `v1.0.0-rc1`  
**Working Branch:** `feat/reliable-mvtec-like-predictions`  
**Base Commit:** `598eaf9`  
**Repository:** `suryacharan945/DefectVision-AI`  
**PR:** #6 (OPEN and UNMERGED)  
**Date:** November 2026

---

## 1. System Requirements & Environment Setup

### 1.1 Hardware Specifications
- **CPU:** Intel/AMD x86_64 CPU with AVX2 instruction support (multithreaded FAISS index search).
- **RAM:** Minimum 8 GB (16 GB recommended for concurrent batch inference).
- **Disk Space:** Minimum 15 GB free space (to store MVTec AD datasets, model weights, and external evaluation images).
- **GPU (Optional):** NVIDIA GPU with CUDA 11.8+ / 12.1+ (PyTorch auto-detects CUDA; CPU fallback is fully verified).

### 1.2 Software Dependencies
- **OS:** Windows 10/11, Ubuntu 20.04+, or macOS (x86_64 / Apple Silicon).
- **Python:** Version `3.10` or `3.11`.
- **Node.js:** Version `18.x` or `20.x` with `npm 9+`.

### 1.3 Virtual Environment Installation
```bash
# Clone repository and checkout feature branch
git clone https://github.com/suryacharan945/DefectVision-AI.git
cd DefectVision-AI
git checkout feat/reliable-mvtec-like-predictions

# Initialize Python virtual environment
python -m venv .venv

# Activate environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1
# OR (Linux / macOS)
# source .venv/bin/activate

# Install core runtime dependencies
pip install -r DefectVisionAI/requirements.txt
pip install pytest pandas scikit-learn faiss-cpu

# Install frontend dependencies
npm --prefix frontend install
```

---

## 2. Service Orchestration

DefectVision AI operates as a decoupled microservices architecture with a FastAPI backend and a React/Vite web application:

### 2.1 Starting the FastAPI Backend Server
```powershell
# Launch backend server on port 8001
Set-Location "DefectVisionAI"
& "..\.venv\Scripts\python.exe" -m uvicorn app:app --host 127.0.0.1 --port 8001
```

### 2.2 Verifying Server Health
```powershell
# Poll health status endpoint
& "..\.venv\Scripts\python.exe" -c "
import urllib.request, json
with urllib.request.urlopen('http://127.0.0.1:8001/api/health') as r:
    print(json.loads(r.read().decode()))
"
```
**Expected Output:**
```json
{
  "status": "ready",
  "optical_engine_initialized": true,
  "ready_category_models_count": 15,
  "all_required_models_ready": true
}
```

### 2.3 Starting the Vite Frontend
```powershell
npm --prefix frontend run dev
```
Accessible at: `http://localhost:5173` or `http://localhost:5174`.

---

## 3. End-to-End Experimental Execution Sequence

Every experimental deliverable is generated through deterministically reproducible Python CLI scripts:

### Step 1: Export Trusted MVTec AD Baseline Metrics
Evaluates all 1,725 official MVTec test specimens through the resident models:
```powershell
& .venv\Scripts\python.exe scripts/export_mvtec_baseline.py
```
**Outputs Generated:**
- `external_validation/baseline/baseline_summary.json`
- `external_validation/baseline/category_recognition_results.csv`
- `external_validation/baseline/anomaly_detection_results.csv`
- *Expected Verification:* Category accuracy $= 99.94\%$, Image AUROC $= 97.15\%$, Pixel AUROC $= 98.02\%$.

### Step 2: Harvest & Validate 150 Internet Specimens
Collects 150 images across all 15 categories with complete provenance:
```powershell
& .venv\Scripts\python.exe scripts/search_and_collect_images.py
```
**Outputs Generated:**
- 150 image files in `external_validation/images/<category>/normal/` and `defective/`
- `external_validation/source_manifest.json`
- `external_validation/image_labels.csv`

### Step 3: ResNet-18 Visual Similarity Stratification
Extracts feature embeddings and stratifies similarity relative to MVTec prototypes:
```powershell
& .venv\Scripts\python.exe scripts/validate_and_assess_similarity.py
```
**Outputs Generated:**
- `external_validation/metadata/external_image_metadata.csv`
- `external_validation/metadata/external_similarity_results.csv`

### Step 4: Execute Live Inference Evaluation Suite
Dispatches all 150 images through the running FastAPI engine:
```powershell
& .venv\Scripts\python.exe scripts/run_improved_evaluation_suite.py
```
**Outputs Generated:**
- `external_validation/results/predictions.csv`
- `external_validation/results/predictions.json`
- `external_validation/results/failure_analysis.csv`
- `external_validation/results/threshold_audit.csv`
- `external_validation/results/category_metrics.csv`
- `external_validation/results/confusion_matrix.csv`
- `external_validation/results/before_after_comparison.csv`

### Step 5: Execute Automated 10-Point Regression Suite
Executes the comprehensive verification test suite:
```powershell
& .venv\Scripts\python.exe scripts/run_regression_suite.py
```
**Outputs Generated:**
- `external_validation/results/regression_test_results.json`
- *Expected Verification:* $10 / 10$ tests passing (`OVERALL_STATUS: PASSED`).

### Step 6: Generate Interactive Visual HTML Gallery
Compiles the responsive web gallery embedding the dataset and dense heatmaps:
```powershell
& .venv\Scripts\python.exe scripts/generate_html_gallery.py
```
**Outputs Generated:**
- `external_validation/galleries/index.html`
- `external_validation/gallery/index.html`

---

## 4. Quality & Build Verification

Before committing or releasing changes, execute the automated test and build verification checks:

### 4.1 Backend PyTest Suite
```powershell
& .venv\Scripts\python.exe -m pytest DefectVisionAI/tests -q
```
**Pass Criterion:** All tests pass with 0 failures.

### 4.2 Frontend Production Build
```powershell
npm --prefix frontend run build
```
**Pass Criterion:** Clean Vite production bundle in `frontend/dist/` without JSX or TypeScript compile errors.

### 4.3 Git Protection Rules
```powershell
# Confirm active feature branch
git branch --show-current
# Verify working tree cleanliness
git status
```
**Safety Constraints:**
- PR #6 must remain **OPEN and UNMERGED**.
- Release tag `v1.0.0-rc1` must remain unchanged.
- All 16 model checkpoint files must remain byte-identical to original release.
