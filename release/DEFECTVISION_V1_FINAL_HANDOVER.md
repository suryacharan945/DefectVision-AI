# DEFECTVISION AI — FINAL PROJECT HANDOVER
**Sprint:** Emergency Release Sprint: v1.0.0-rc1 (72-Hour Project Closure)  
**Date:** 2026-11-19  
**Authors:** Senior ML Engineer, Computer Vision Research Engineer, QA Lead & Release Manager  

---

## 1. Executive Handover Summary

This document serves as the formal engineering and research handover for **DefectVision AI v1.0.0-rc1**. The system is frozen as a verified, benchmark-evaluated industrial visual anomaly detection research prototype.

All major components—including memory bank feature extraction, fast nearest-neighbor FAISS querying, temperature-calibrated category classification, optical quality gating, FastAPI backend services, and the React frontend interface—are verified operational and covered by a 92-test regression suite.

---

## 2. Release Status & Git Identity

| Field | Value |
|---|---|
| **Release Tag / Milestone** | `v1.0.0-rc1` (Release Candidate 1) |
| **Repository URL** | `https://github.com/suryacharan945/DefectVision-AI` |
| **Working Branch** | `fix/localhost-live-inference-restoration` |
| **Upstream Remote** | `origin` (`https://github.com/suryacharan945/DefectVision-AI.git`) |
| **Pull Request** | **PR #6** ([https://github.com/suryacharan945/DefectVision-AI/pull/6](https://github.com/suryacharan945/DefectVision-AI/pull/6)) |
| **PR State** | **OPEN and UNMERGED** (Strictly maintained per project instructions) |
| **Python Regression Test Suite** | **92 / 92 Passed** in 64.258s (Exit code: 0) |
| **Frontend Production Build** | **Clean Build** (2,459 modules in 4.30s, Exit code: 0) |
| **Security Secrets Audit** | **0 Secrets Found** across 707 scanned files |

---

## 3. Final Architecture & Implemented Capabilities

```
[ Input Frame (File or Live Camera) ]
                 │
                 ▼
    [ Optical Quality Gate ] ────────► Intercepts Blur (<25) or Glare (<30, >240) -> REVIEW REQUIRED
                 │ (Passed)
                 ▼
    [ Category Recognition ] ────────► Shannon Entropy >= 0.65 or Conf < 0.70 -> UNSUPPORTED
                 │ (Supported)
                 ▼
    [ PatchCore Extractor ]  ────────► ResNet-18 Layers 2 & 3 -> 384-dim Patch Embeddings
                 │
                 ▼
    [ FAISS Coreset Banks ]  ────────► Category-specific nearest-neighbor distance scoring
                 │
                 ▼
    [ 4-State Decision Fusion ] ─────► Score vs. Calibrated Threshold tau (+/- 8% Borderline Band)
                 │
                 ├─► Score <= tau * 0.92: NORMAL (NO DEFECT DETECTED)
                 ├─► Score >= tau * 1.08: DEFECTIVE (POSSIBLE DEFECT DETECTED)
                 └─► Borderline:          REVIEW REQUIRED (MANUAL INSPECTION REQUIRED)
                 │
                 ▼
    [ Heatmap Overlay Engine ] ──────► Bi-linear Upsampling, Gaussian Filter & False-Color JET Map
```

### Key Implemented Capabilities
1. **15 Category Resident Models:** 10 object and 5 texture categories fully supported.
2. **Quality Gate:** Intercepts optical defects before machine learning inference.
3. **Automated SKU Recognition:** EfficientNet-B0 temperature-calibrated classification.
4. **Interactive Heatmap Viewport:** Dual-pane visual inspection with alpha-blending slider.
5. **Batch Inspection API:** Multipart asynchronous queue for multi-image processing.
6. **Audit History Log:** Thread-safe ring buffer capturing operational decisions and latencies.

---

## 4. Model Inventory & Calibrated Parameters

All 15 category models are resident in `DefectVisionAI/models/patchcore/`:

| Category | Type | Tokens | Embedding Dim | Calibrated Threshold ($\tau$) | Baseline Mean ($\mu$) |
|---|---|---:|---:|---:|---:|
| **bottle** | Object | 14,739 | 384 | 1.4666 | 0.9732 |
| **cable** | Object | 15,758 | 384 | 2.4577 | 1.7409 |
| **capsule** | Object | 15,444 | 384 | 1.1502 | 0.7614 |
| **carpet** | Texture | 19,756 | 384 | 1.3543 | 0.9690 |
| **grid** | Texture | 18,580 | 384 | 1.4634 | 1.0921 |
| **hazelnut** | Object | 27,518 | 384 | 2.3403 | 1.2826 |
| **leather** | Texture | 17,248 | 384 | 1.1136 | 0.8975 |
| **metal_nut** | Object | 15,523 | 384 | 1.8271 | 1.3742 |
| **pill** | Object | 18,816 | 384 | 1.7575 | 1.2280 |
| **screw** | Object | 22,579 | 384 | 1.4684 | 1.0915 |
| **tile** | Texture | 16,228 | 384 | 1.4735 | 1.2218 |
| **toothbrush** | Object | 4,233 | 384 | 1.4593 | 1.1695 |
| **transistor** | Object | 14,974 | 384 | 1.7787 | 1.4013 |
| **wood** | Texture | 17,404 | 384 | 1.3440 | 1.0621 |
| **zipper** | Object | 16,934 | 384 | 1.1627 | 0.9202 |

---

## 5. Summary of Verified vs. Failed Experiments

### Verified Research Findings
- **MVTec AD Full Evaluation (1,725 Test Images):** Mean Image AUROC: **$97.8\%$**, Category Accuracy: **$99.94\%$**, Overall FPR: **$2.10\%$**, Defect Recall: **$97.40\%$**.
- **Few-Shot K=10 (Bottle Benchmark, N=83):** Under a priori frozen threshold $\tau = \max(S_{\text{cal}}) = 1.6410$, achieved **$0.00\%$ FPR**, **$96.83\%$ Recall**, and **$0.9839$ F1-Score**.
- **Pill Test Set Reconciliation:** Audited and verified at exactly **77 physical specimens** ($26$ normal, $25$ color defect, $26$ crack defect).

### Failed / Disqualified Experiments
- **K=20 Threshold Post-Hoc Tuning ($1.20\times$):** Disqualified as a `DEVELOPMENT-SET RESULT`. The multiplier $1.20\times$ was selected post-hoc after inspecting test scores. Under the strict un-tuned rule, K=20 produced a $20.0\%$ FPR.
- **Single-Bank Spatial-Photometric Fusion:** Failed all factory acceptance targets ($8\% - 24\%$ color defect recall). 384 spatial channels overpowered 3 color channels ($< 2\%$ distance contribution).
- **Track B External Factory Adaptation:** Blocked due to data insufficiency ($N=1$ physical defect specimen).

---

## 6. Known Issues and Limitations

1. **Photometric / Color Anomaly Insensitivity:** Standard PatchCore CNN embeddings miss pure color variations without structural deformation.
2. **Calibration Tail Variance:** Sample maximums from small calibration sets ($N=10$) exhibit high sampling variance.
3. **Throughput:** Single-frame CPU inference takes $110 - 165 \text{ ms}$ ($\approx 7 \text{ FPS}$). High-speed lines require GPU acceleration.

---

## 7. Local Deployment & Run Instructions

### Step 1: Start Backend (Port 8001)
```powershell
Set-Location "DefectVisionAI"
& "..\.venv\Scripts\python.exe" -m uvicorn app:app --host 127.0.0.1 --port 8001
```

### Step 2: Start Frontend (Port 5174)
```powershell
npm --prefix frontend run dev
```

### Step 3: Run Full Regression Suite
```powershell
.\.venv\Scripts\python -m unittest discover tests
npm --prefix frontend run build
```

---

## 8. Verifiable Demonstration Sequence

Execute the following commands to demonstrate genuine inference on physical specimens:

1. **Demonstrate Nominal Specimen Inspection:**
   ```powershell
   .\.venv\Scripts\python -c "
   import urllib.request, json
   from scripts.verify_day1_pipeline import multipart_post
   with open('release/portfolio_handover/assets/04_genuine_specimen_raw_bottle_nominal.png', 'rb') as f:
       s, d = multipart_post('http://127.0.0.1:8001/api/inspect-frame', {'category': 'bottle'}, {'file': ('bottle.png', f.read(), 'image/png')})
   print(f'Normal Bottle -> Status: {s}, Verdict: {d.get(\"verdict\")}, Score: {d.get(\"anomaly_score\")}, Tau: {d.get(\"anomaly_threshold\")}')
   "
   ```
   **Expected Output:** `Verdict: NORMAL, Score: ~1.2869, Tau: 1.4666`.

2. **Demonstrate Defective Specimen Inspection & Heatmap:**
   ```powershell
   .\.venv\Scripts\python -c "
   import urllib.request, json
   from scripts.verify_day1_pipeline import multipart_post
   with open('release/portfolio_handover/assets/01_genuine_specimen_raw_bottle_defective.png', 'rb') as f:
       s, d = multipart_post('http://127.0.0.1:8001/api/inspect-frame', {'category': 'bottle'}, {'file': ('bottle.png', f.read(), 'image/png')})
   print(f'Defective Bottle -> Status: {s}, Verdict: {d.get(\"verdict\")}, Score: {d.get(\"anomaly_score\")}, Heatmap Length: {len(d.get(\"heatmap_base64\", \"\"))}')
   "
   ```
   **Expected Output:** `Verdict: DEFECTIVE, Score: ~3.3056, Heatmap Length: ~91315`.

3. **Demonstrate Optical Quality Gate Interception:**
   ```powershell
   .\.venv\Scripts\python -c "
   import urllib.request, json, numpy as np, cv2
   from scripts.verify_day1_pipeline import multipart_post
   black = np.zeros((224, 224, 3), dtype=np.uint8)
   _, enc = cv2.imencode('.png', black)
   s, d = multipart_post('http://127.0.0.1:8001/api/inspect-frame', {'category': 'bottle'}, {'file': ('black.png', enc.tobytes(), 'image/png')})
   print(f'Black Image -> Status: {s}, Verdict: {d.get(\"verdict\")}, Rejection: {d.get(\"rejection_stage\")}')
   "
   ```
   **Expected Output:** `Verdict: REVIEW REQUIRED, Rejection: quality_gate`.

---

## 9. Recommended Next Steps for Post-v1 Research

1. **Implement Decoupled Dual-Stream Fusion:** Implement separate spatial and photometric memory banks with max-ratio decision fusion ($s = \max(s_s/\tau_s, s_c/\tau_c)$) as detailed in `SPATIAL_PHOTOMETRIC_EXPERIMENT_2_SPECIFICATION.md`.
2. **Collect Powered External Dataset:** Collect $N \ge 300$ normal and $N \ge 30$ defect units under factory capture geometry to unblock Track B.
3. **Transition to DINOv2:** Benchmark self-supervised vision transformers to improve color sensitivity without handcrafted descriptors.
4. **TensorRT Compilation:** Export ResNet-18 to TensorRT for sub-15ms edge inference.
