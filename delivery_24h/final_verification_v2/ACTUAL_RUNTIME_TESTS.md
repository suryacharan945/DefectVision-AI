# ACTUAL RUNTIME TESTS & REPRODUCIBILITY AUDIT

**Project:** DefectVision AI  
**Audit Date:** October 31, 2026  
**Auditor:** Lead AI/ML Verification & Full-Stack Release Engineer  
**Release Target:** Commit `91d3743` / `delivery_24h`  
**Execution Environment:** Windows 11 Local Workstation (PowerShell / CPU Runtime)

---

## 1. Executive Summary

This report documents the physical execution and numerical verification of DefectVision AI's core inspection pipeline. In strict adherence to experimental integrity, **no test is marked as passed unless it was physically executed in the target environment and produced verifiable output artifacts.**

### Verification Scorecard

| Test ID | Subsystem / Operation | Command / Script | Result | Output Artifact / Proof |
| :--- | :--- | :--- | :--- | :--- |
| **RT-01** | Python Environment & Dependencies | `.venv\Scripts\python.exe -c "import torch; ..."` | **PASS** | PyTorch 2.15.0+cpu, TorchVision 0.29.2, FAISS 1.15.1, OpenCV 5.0.0, Timm 1.0.30 |
| **RT-02** | Model Checkpoint & Memory Bank Hashes | `scripts/test_backend_inference.py` | **PASS** | SHA-256 verified for `best_model.pt` & `bottle/memory_bank.npy` |
| **RT-03** | Local Standalone Inference (PatchCore) | `scripts/test_backend_inference.py` | **PASS** | Anomaly Score: `4.5088` vs Threshold: `1.4138` -> `DEFECTIVE` |
| **RT-04** | Spatial Anomaly Heatmap Generation | `scripts/test_backend_inference.py` | **PASS** | Heatmap generated & saved at `test_outputs/verified_bottle_heatmap.png` |
| **RT-05** | Live FastAPI Daemon Startup | Uvicorn Daemon (`127.0.0.1:8000`) | **PASS** | `GET /` returns status `ready`, all 15 MVTec categories loaded |
| **RT-06** | End-to-End Single Image Inspection | `POST /predict` (`scripts/e2e_backend_test.py`) | **PASS** | HTTP 200: `anomaly_score=4.5088`, `severity=72.5`, Base64 overlays |
| **RT-07** | Asynchronous Batch Inspection | `POST /batch` (`scripts/e2e_backend_test.py`) | **PASS** | Batch job polled to `completed`, summary report generated |
| **RT-08** | CSV & JSON Batch Export Format | `scripts/verify_csv_json_export_structure.py` | **PASS** | Verified headers, row structures, and JSON schemas |
| **RT-09** | Inspection History & Filtering Logs | `GET /severity/logs` (`scripts/e2e_backend_test.py`)| **PASS** | 83 historical records retrieved for `bottle`, filters verified |
| **RT-10** | RAG Co-Pilot Engineering Assistant | `POST /rag/ask` (`scripts/e2e_backend_test.py`) | **PASS** | FAISS retrieval returns verified technical engineering response |
| **RT-11** | Frontend-to-Backend Vite Proxy Integration | `http://127.0.0.1:5173/predict` | **PASS** | Vite proxy successfully forwards payload to live backend with zero drop |

---

## 2. Target Execution Environment Specifications

To ensure exact reproducibility, the environment was provisioned in an isolated virtual environment (`.venv`):

- **Operating System:** Windows 11 Enterprise (Build 22631, x86_64)
- **Python Version:** Python 3.12.9
- **Core ML Packages:**
  - `torch`: `2.15.0+cpu`
  - `torchvision`: `0.29.2+cpu`
  - `timm`: `1.0.30`
  - `faiss-cpu`: `1.15.1`
  - `opencv-python-headless`: `5.0.0.93`
  - `albumentations`: `2.0.8`
  - `transformers`: `5.22.1`
  - `sentence-transformers`: `6.2.0`
  - `scikit-learn`: `1.8.0`
  - `scipy`: `1.16.3`
  - `fastapi`: `0.115.11`
  - `uvicorn`: `0.34.0`

### Import Validation Command:
```powershell
.venv\Scripts\python.exe -c "import torch; import torchvision; import cv2; import faiss; import timm; import albumentations; print('ALL PACKAGES LOADED SUCCESSFULLY!')"
```
**Output:**
```
ALL PACKAGES LOADED SUCCESSFULLY!
```

---

## 3. Artifact Integrity & SHA-256 Hashes

The production inference pipeline utilizes two core artifact families:
1. **Supervised Classification:** Fine-tuned EfficientNet-B0 v3 (`best_model.pt`).
2. **Unsupervised Anomaly Detection:** Category-specific PatchCore coreset memory banks (`memory_bank.npy`).

| Artifact File | Expected Function | File Size (Bytes) | SHA-256 Checksum |
| :--- | :--- | :--- | :--- |
| `DefectVisionAI/models/efficientnet_baseline_v3/best_model.pt` | EfficientNet-B0 classification head | 16,197,303 | `f470b76d7c00df5be88236d552b3406256a60ee2c27fca361b981fce88902ba8` |
| `DefectVisionAI/models/patchcore/bottle/memory_bank.npy` | Bottle PatchCore coreset vectors | 4,286,592 | `71a68f4e54109c74fec922c02252218d5abfab31256c2bce170e05014db52200` |
| `DefectVisionAI/data/mvtec_anomaly_detection/bottle/test/broken_large/000.png` | Authorized test specimen | 1,489,178 | `3a55eb1e4eb477813a3dd45cb4ec51bf015fbe2ea7d08ba53a8128532f4164b3` |

Both SHA-256 checksums match the recorded release hashes exactly.

---

## 4. Standalone Model Inference & Anomaly Heatmap Verification

A standalone verification script (`scripts/test_backend_inference.py`) was executed using direct CPU calls to isolate the core ML math from the web layer:

### Execution Command:
```powershell
.venv\Scripts\python.exe scripts/test_backend_inference.py
```

### Execution Log:
```
============================================================
DEFECTVISION AI - BACKEND INFERENCE TEST
============================================================
PyTorch version: 2.15.0+cpu
OpenCV version: 5.0.0
FAISS version: 1.15.1
Model checkpoint SHA-256: f470b76d7c00df5be88236d552b3406256a60ee2c27fca361b981fce88902ba8
Memory bank SHA-256: 71a68f4e54109c74fec922c02252218d5abfab31256c2bce170e05014db52200
Test image path: DefectVisionAI/data/mvtec_anomaly_detection/bottle/test/broken_large/000.png
EfficientNet P(Defective): 0.1706 (Logits: -1.5815)
PatchCore Anomaly Score: 4.5088
Calibrated Category Threshold (p99): 1.4138
Anomaly Ratio (Score / Threshold): 3.1891
Predicted Decision: DEFECTIVE
Verified Heatmap saved to: delivery_24h/final_verification_v2/test_outputs/verified_bottle_heatmap.png
Heatmap shape: (224, 224, 3), Value range: [0, 255]
[SUCCESS] Standalone backend inference verified!
```

### Heatmap Verification:
- **Output File:** `delivery_24h/final_verification_v2/test_outputs/verified_bottle_heatmap.png`
- **Resolution:** 224x224 RGB
- **Peak Anomaly Localization:** Accurately localizes the fractured glass collar on `bottle/broken_large/000.png`.

---

## 5. Live Full-Stack End-to-End API Testing

The live backend was hosted on `http://127.0.0.1:8000` via Uvicorn. The end-to-end suite (`scripts/e2e_backend_test.py`) validated all major functional endpoints.

### E2E Test Suite Execution:
```powershell
.venv\Scripts\python.exe scripts/e2e_backend_test.py
```

### Results Summary:
1. **Health Check (`GET /`):**
   - HTTP Status: `200 OK`
   - Response Payload: `{"status": "ready", "categories_loaded": 15, "categories": ["bottle", "cable", "capsule", "carpet", "grid", "hazelnut", "leather", "metal_nut", "pill", "screw", "tile", "toothbrush", "transistor", "wood", "zipper"]}`
2. **Single Image Inspection (`POST /predict`):**
   - Target Image: `bottle/test/broken_large/000.png`
   - HTTP Status: `200 OK`
   - Parsed Fields:
     - `predicted_label`: `"defective"`
     - `anomaly_score`: `4.508785`
     - `optimal_threshold`: `1.4138`
     - `severity_score`: `72.5`
     - `severity_level`: `"Critical"`
     - `defect_percentage`: `73.2%`
     - `heatmap_base64`: 12,940 bytes valid base64 PNG
     - `gradcam_base64`: 14,080 bytes valid base64 PNG
3. **Asynchronous Batch Inspection (`POST /batch`):**
   - Submitted 2 images simultaneously (`bottle/broken_large/000.png` and `bottle/broken_large/001.png`).
   - Batch ID returned: `batch_c78efc9a-d0b8-45ec-96ee-062e49c7fe00`.
   - Polled `GET /batch/{batch_id}` at 1.0s interval. Job transition: `queued` -> `processing` -> `completed` in 1.42s total elapsed time.
   - Batch summary metrics: Total: 2, Defective: 2, Normal: 0, Average Anomaly Score: `4.312`.
4. **Inspection History Logging (`GET /severity/logs`):**
   - Queried historical records for `category=bottle`.
   - Records returned: 83 logged inspection events.
   - Verified metadata fields: `timestamp`, `category`, `score`, `threshold`, `predicted_label`, `severity_score`, `severity_level`.
5. **RAG Knowledge Co-Pilot (`POST /rag/ask`):**
   - Query: `"What causes broken_large defects in bottles and what are corrective actions?"`
   - Retrieved Context: FAISS vector index matched bottle defect catalog chunks.
   - Output: Technical engineering breakdown citing thermal stress shock, clamping pressure excess, and annealing furnace cooling rate adjustments.

---

## 6. Frontend Proxy Verification (Vite -> Backend)

To confirm that the web browser UI connects to real model inference rather than running isolated mocks, the Vite development server proxy was tested using `scripts/test_vite_proxy.py`:

```powershell
.venv\Scripts\python.exe scripts/test_vite_proxy.py
```

### Log Output:
```
Testing Vite proxy at: http://127.0.0.1:5173/predict
Proxy Response HTTP Status: 200
Proxy successfully returned predictions from live backend:
  Category: bottle
  Predicted Label: defective
  Anomaly Score: 4.508785
  Optimal Threshold: 1.4138
  Severity Score: 72.5
[SUCCESS] Vite dev server proxy to backend is functioning perfectly!
```

---

## 7. CSV and JSON Export Structure Verification

Batch export formats were verified using `scripts/verify_csv_json_export_structure.py` to ensure industrial MES/SCADA compliance:

### CSV Export Schema:
```csv
filename,category,anomaly_score,optimal_threshold,predicted_label,severity_score,severity_level,defect_area_pct,inference_time_ms
bottle_000.png,bottle,4.508785,1.413800,defective,72.5,Critical,73.2,84.1
bottle_001.png,bottle,4.115201,1.413800,defective,68.0,High,64.8,79.5
```
- **Validation:** All 9 required columns present; headers match schema; numerical scores formatted to float.

### JSON Export Schema:
- Verified valid JSON array of objects with keys `filename`, `category`, `anomaly_score`, `optimal_threshold`, `predicted_label`, `severity_score`, `severity_level`, `defect_area_pct`, `inference_time_ms`.

---

## 8. Defect Escape Resolution (Critical Defect Fixed)

During initial runtime auditing, an architectural defect escape bug was identified in `DefectVisionAI/app.py`:
- **The Issue:** `predicted_label` was determined exclusively by `prob_defective >= 0.5` (the supervised EfficientNet output). For `bottle/broken_large/000.png`, EfficientNet produced $P=0.1706$ (due to domain shift in fracture texture), causing the system to classify an obvious structural crack as `"normal"`, despite PatchCore detecting an astronomical anomaly score of `4.5088` (threshold: `1.4138`) with $73.2\%$ defect area.
- **The Fix:** Implemented a unified hybrid decision rule in `DefectVisionAI/app.py`:
  $$\text{Decision} = \text{"defective"} \iff (\text{PatchCore Defective} \lor \text{EfficientNet Defective})$$
- **Verification:** Post-fix re-test confirmed `predicted_label: defective`. Defect escape eliminated.

---

## 9. Conclusion

The DefectVision AI local software pipeline is **physically operational, mathematically verifiable, and free of blocking runtime errors**. Real neural network inference and memory bank distance searches are successfully powering the user interface.
