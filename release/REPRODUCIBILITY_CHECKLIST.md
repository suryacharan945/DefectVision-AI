# DefectVision AI — Reproducibility Checklist

**Milestone:** `v1.0.0-rc1` — Benchmark-Evaluated Industrial Anomaly Detection Research Prototype  
**Target Environment:** Windows 10/11 or Ubuntu Linux 22.04 LTS  
**Python Version:** Python 3.10 / 3.11  
**Node.js Version:** Node.js $\ge 18.0$ (npm $\ge 9.0$)  
**Status:** `RELEASE READY WITH DOCUMENTED METRIC LIMITATIONS`

This checklist details every environment variable, dependency, file path, command, and validation procedure required to reproduce DefectVision AI from a clean repository clone.

---

## 1. System Requirements & Prerequisites

| Component | Minimum Specification | Recommended Specification |
| :--- | :--- | :--- |
| **OS** | Windows 10 (64-bit) / Ubuntu 22.04 | Windows 11 / Ubuntu 22.04 LTS |
| **CPU** | Quad-core Intel Core i5 / AMD Ryzen 5 | 8-core CPU with AVX2 instruction support |
| **RAM** | 8 GB RAM | 16 GB RAM (for resident memory banks) |
| **Disk** | 10 GB free space | 25 GB SSD (if downloading full MVTec dataset) |
| **Python** | Python 3.10 or 3.11 | Python 3.10.x |
| **Node.js** | Node.js v18.x or v20.x | Node.js v20.x LTS |

---

## 2. Directory Structure & Checkpoint Locations

Before starting the application, ensure the following core model checkpoints and directories are present:

```
DefectVision-AI/
├── DefectVisionAI/
│   ├── app.py                         # FastAPI backend service entry point
│   ├── config.py                      # Application configuration & thresholds
│   ├── models/
│   │   ├── category_classifier.pt     # EfficientNet-B0 15-class classifier (4.02M params)
│   │   └── patchcore_banks/           # 15 category PatchCore memory banks
│   │       ├── bottle.pt
│   │       ├── cable.pt
│   │       ├── capsule.pt
│   │       ├── carpet.pt
│   │       ├── grid.pt
│   │       ├── hazelnut.pt
│   │       ├── leather.pt
│   │       ├── metal_nut.pt
│   │       ├── pill.pt
│   │       ├── screw.pt
│   │       ├── tile.pt
│   │       ├── toothbrush.pt
│   │       ├── transistor.pt
│   │       ├── wood.pt
│   │       └── zipper.pt
│   ├── src/                           # Backend python packages
│   │   ├── core/                      # Pipeline orchestration & scoring
│   │   ├── patchcore/                 # PatchCore feature extraction & FAISS indexing
│   │   ├── camera_service/            # Universal image intake & quality gates
│   │   └── evaluation/                # Benchmark evaluation harness
│   └── tests/                         # 92 unit and integration tests
├── frontend/                          # React 18 + Vite frontend
│   ├── src/
│   │   ├── App.jsx                    # Primary inspection dashboard
│   │   ├── api/client.js              # HTTP client to FastAPI backend
│   │   └── components/                # Modular UI components
│   ├── package.json
│   └── vite.config.js
└── release/                           # Release artifacts, reports, and audits
```

---

## 3. Step-by-Step Installation Instructions

### Step 3.1: Repository Setup
```bash
git clone https://github.com/suryacharan945/DefectVision-AI.git
cd DefectVision-AI
git checkout fix/localhost-live-inference-restoration
```

### Step 3.2: Python Virtual Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate on Windows PowerShell:
.\.venv\Scripts\Activate.ps1

# Activate on Linux/macOS:
# source .venv/bin/activate

# Upgrade packaging tools:
python -m pip install --upgrade pip setuptools wheel
```

### Step 3.3: Install Python Dependencies
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install faiss-cpu fastapi uvicorn pydantic opencv-python Pillow numpy scipy scikit-learn pandas requests httpx pytest
```

### Step 3.4: Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

---

## 4. Live Service Execution Commands

### Step 4.1: Start FastAPI Backend (Port 8001)
```powershell
# From the repository root (PowerShell):
Set-Location "DefectVisionAI"
& "..\.venv\Scripts\python.exe" -m uvicorn app:app --host 127.0.0.1 --port 8001 --reload
```

**Verification:** In a new terminal, run:
```bash
curl -s http://127.0.0.1:8001/health
```
**Expected Response:**
```json
{
  "status": "ready",
  "models_loaded": 15,
  "classifier_ready": true,
  "inference_mode": "live"
}
```

### Step 4.2: Start Vite Frontend (Port 5174)
```powershell
# In a separate terminal:
npm --prefix frontend run dev
```
**Access:** Open your browser to `http://127.0.0.1:5174`. The dashboard header will display **`LIVE INFERENCE ACTIVE`** with green status badges.

---

## 5. Verification & Test Suite Execution

### Step 5.1: Execute Full Regression Suite (92 Tests)
```powershell
# Set PYTHONPATH to include DefectVisionAI directory
$env:PYTHONPATH = "DefectVisionAI"
.\.venv\Scripts\python.exe -m pytest DefectVisionAI/tests -q
```
**Expected Result:** `92 passed in 64.30s` (zero failures, zero errors).

### Step 5.2: Execute Frontend Production Build
```powershell
npm --prefix frontend run build
```
**Expected Result:** Vite creates `frontend/dist/` in under 5.0 seconds with zero compilation warnings or type errors.

---

## 6. Metric Reproduction Instructions

To reproduce the benchmark evaluation CSV and audited metrics:

### Step 6.1: Run Full 15-Category MVTec Evaluation Harness
```powershell
$env:PYTHONPATH = "DefectVisionAI"
.\.venv\Scripts\python.exe -m src.evaluation.eval_all_categories \
  --data_dir DefectVisionAI/data/mvtec \
  --output_csv release/final_validation/mvtec_all_predictions.csv
```
**Expected Output File:** `release/final_validation/mvtec_all_predictions.csv` containing 1,725 rows.

### Step 6.2: Compute Audited Metrics from Prediction CSV
```powershell
.\.venv\Scripts\python.exe -c "
import pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score

df = pd.read_csv('release/final_validation/mvtec_all_predictions.csv')
print('Total Rows:', len(df))
aurocs = [roc_auc_score(grp['is_defect'], grp['anomaly_score']) for _, grp in df.groupby('category')]
auprcs = [average_precision_score(grp['is_defect'], grp['anomaly_score']) for _, grp in df.groupby('category')]
print(f'Macro Image AUROC: {sum(aurocs)/len(aurocs)*100:.2f}%')
print(f'Macro Image AUPRC: {sum(auprcs)/len(auprcs)*100:.2f}%')
tp = len(df[(df['is_defect'] == 1) & (df['predicted_defect'] == 1)])
fn = len(df[(df['is_defect'] == 1) & (df['predicted_defect'] == 0)])
fp = len(df[(df['is_defect'] == 0) & (df['predicted_defect'] == 1)])
tn = len(df[(df['is_defect'] == 0) & (df['predicted_defect'] == 0)])
print(f'Micro Defect Recall: {tp/(tp+fn)*100:.2f}%')
print(f'Micro FPR: {fp/(fp+tn)*100:.2f}%')
print(f'Micro F1: {2*tp/(2*tp+fp+fn):.4f}')
"
```
**Expected Output:**
```
Total Rows: 1725
Macro Image AUROC: 97.15%
Macro Image AUPRC: 98.98%
Micro Defect Recall: 94.04%
Micro FPR: 24.84%
Micro F1: 0.9253
```

---

## 7. Known Environment Constraints

1. **Windows CPU SIMD Support:** On Windows, `faiss-cpu` relies on AVX2 instructions. Virtualized environments lacking AVX2 passthrough will encounter runtime faults during `faiss.IndexFlatL2` allocation.
2. **Port Binding:** Port 8001 must be free. If another process is listening on 8001, configure the port in `DefectVisionAI/config.py` and update `frontend/src/api/client.js`.
3. **RAM Allocation:** When all 15 memory banks are resident in memory, the backend consumes approximately 1.8 GB RAM. Ensure at least 4 GB available system RAM before launch.
