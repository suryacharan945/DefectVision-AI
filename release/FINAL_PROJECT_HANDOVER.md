# DefectVision AI — Final Project Handover Report

**Milestone:** `v1.0.0-rc1` — Benchmark-Evaluated Industrial Anomaly Detection Research Prototype  
**Date:** 2026-11-19  
**Repository:** [suryacharan945/DefectVision-AI](https://github.com/suryacharan945/DefectVision-AI)  
**Working Branch:** `fix/localhost-live-inference-restoration`  
**Base Commit:** `7a298d7cd778b9cb06580bee0922630ed91ab1a6`  
**Pull Request:** [PR #6](https://github.com/suryacharan945/DefectVision-AI/pull/6) — **OPEN AND UNMERGED**  
**Final Release Status:**  
`DefectVision AI v1.0.0-rc1 — RELEASE READY WITH DOCUMENTED METRIC LIMITATIONS`

---

## 1. Project Overview

DefectVision AI is an end-to-end industrial machine vision and automated visual inspection platform engineered for unsupervised visual anomaly detection. 

Traditional supervised defect classifiers fail in discrete manufacturing because defects are rare, catastrophic, unpredictable, and cost-prohibitive to label at scale. DefectVision AI resolves this by implementing a cold-start, one-class representation architecture based on **PatchCore** (Roth et al., 2022) coupled with an upstream **EfficientNet-B0** product category recognition engine.

By learning what nominal ("golden") specimens look like exclusively from nominal imagery, the system detects any structural fracture, surface scratch, contamination, or missing component as a distance outlier in feature space without requiring defect training annotations.

---

## 2. Final Architecture

The production architecture operates as a decoupled microservice pipeline:

```
[Camera / File Upload]
       │
       ▼
[Image Quality Gate] ──── (Fails: Blur / Under-exposure / Saturation) ──► [HTTP 422 Rejection]
       │
       ▼ (Passes)
[Category Classifier] ─── (EfficientNet-B0: 15 Classes, 99.94% Acc)
       │
       ▼
[Category Consistency] ── (Profile Mismatch / Entropy > 0.85) ─────────► [HTTP 409 Rejection]
       │
       ▼ (Passes)
[Category Routing] ────── (Selects 1 of 15 Resident Memory Banks)
       │
       ▼
[ResNet18 Featurizer] ─── (Layers 2 & 3 Concatenation, d=384, N=784 patches)
       │
       ▼
[FAISS Nearest Neighbor]  (Exact L2 Query: faiss.IndexFlatL2 on CPU)
       │
       ▼
[Anomaly Scoring] ─────── (Image Score = Max Patch Distance; Decision via Threshold)
       │
       ▼
[Dense Heatmap Synthesis] (Bicubic Upsample + Gaussian Filter + Jet Colormap Overlay)
       │
       ▼
[FastAPI Telemetry API] ─► [React 18 + Vite Production Dashboard]
```

---

## 3. Model Inventory

| Component | Model Backbone | Checkpoint Location | Parameters / Memory | Operational Function |
| :--- | :--- | :--- | :--- | :--- |
| **Category Classifier** | EfficientNet-B0 | `DefectVisionAI/models/category_classifier.pt` | 4.02M params (~16 MB) | 15-class SKU routing and entropy OOD gating |
| **Feature Extractor** | ResNet18 (Torchvision) | Pretrained weights (ImageNet-1k) | 11.7M params (~45 MB) | Extracts layers 2 & 3 patch representations |
| **Memory Banks (15)** | `faiss.IndexFlatL2` | `DefectVisionAI/models/patchcore_banks/*.pt` | 15 resident indices (~1.8 GB RAM) | Category-specific nominal vector retrieval |
| **Quality Engine** | OpenCV 2D Laplacian | Algorithmic (`src/camera_service/`) | Memory-negligible | Blur and exposure boundary filtering |

---

## 4. Verified Benchmark Results

All metrics below have been independently audited and reconciled against the full 1,725-specimen MVTec AD test benchmark:

### 4.1 15-Class Product Category Recognition
- **Test Accuracy:** **99.94%** (1,724 / 1,725 correct)
- **Top-1 Categorization Failure:** Exactly 1 specimen (`wood` sample `002.png`) misrouted to `screw` due to high textural entropy.
- **Clarification:** This metric evaluates SKU routing; it is completely distinct from defect detection.

### 4.2 PatchCore Anomaly Detection Performance
- **Macro Image AUROC:** **97.15%** (unweighted mean across 15 categories)
- **Macro Image AUPRC:** **98.98%**
- **Mean Pixel Localization AUROC:** **98.02%**
- **Micro Defect Recall ($\tau = 1.50$):** **94.04%** (1,183 / 1,258 defects detected; 75 escapes)
- **Micro False Positive Rate ($\tau = 1.50$):** **24.84%** (116 / 467 nominal specimens flagged)
- **Micro Precision:** **91.07%** (1,183 / 1,299)
- **Micro F1-Score:** **0.9253**
- **Overall Operational Accuracy:** **88.93%** (1,534 / 1,725 correct verdicts)

### 4.3 Few-Shot Adaptation (Bottle SKU, 83 Test Specimens)
- **K = 10 Few-Shot (Frozen $\tau = 1.50$):** Recall **96.83%** (61/63), FPR **0.00%** (0/20), F1 **0.9839**. Validated candidate.
- **K = 20 Few-Shot (Frozen $\tau = 1.50$):** Recall **100.00%** (63/63), FPR **20.00%** (4/20), F1 **0.9692**. Validated baseline.
- **K = 20 Post-Hoc Multiplier ($1.25\times \implies \tau = 1.875$):** Recall 98.41%, FPR 0.00%, F1 0.9841. **Development-only ablation** (excluded from release claims).

---

## 5. Operational Limitations & Statistical Realities

1. **False Alarms Under Global Thresholding:** Applying a static threshold ($\tau = 1.50$) across diverse product types causes texture categories (`tile`, `wood`, `leather`) to experience 60%–68% false-positive rates due to natural material grain. Production deployment requires per-category calibrated thresholds.
2. **Small-Sample Statistical Intervals:** Observing 0 errors out of 20 normal samples ($k=0, n=20$) yields an exact Clopper–Pearson 95% confidence interval of **$[0.00\%, 16.84\%]$** (Wilson: $[0.00\%, 16.11\%]$). A true $<1\%$ FPR requires $N \ge 300$ independent nominal validation captures.
3. **External Domain Shift (Track B):** Generalization to uncalibrated smartphone or external factory environments remains unvalidated due to sample limitations ($n=1$ physical defect specimen).
4. **Physical Specimen Confounding:** File-level SHA-256 uniqueness guarantees image-capture separation across splits but does not guarantee distinct physical production units in public benchmark sets.

---

## 6. Test and Build Verification Results

- **Backend Regression Suite:** **92 passed in 64.30s** (100% test pass rate across unit, integration, and security suites).
- **Frontend Production Build:** Vite build clean in **4.30s**, zero bundle errors, zero warnings.
- **Live Service Health:** FastAPI on `http://127.0.0.1:8001` responds `"status": "ready"`, `"models_loaded": 15`, `"classifier_ready": true`.
- **Frontend Service:** Vite on `http://127.0.0.1:5174` active with real-time reactive telemetry and verified `LIVE INFERENCE ACTIVE` state.

---

## 7. Repository and Pull Request Status

- **Repository:** `https://github.com/suryacharan945/DefectVision-AI`
- **Working Branch:** `fix/localhost-live-inference-restoration`
- **Base Commit:** `7a298d7cd778b9cb06580bee0922630ed91ab1a6`
- **Local & Remote Sync:** Local branch is up to date with `origin/fix/localhost-live-inference-restoration`.
- **Pull Request #6:** Verified **OPEN and UNMERGED** via GitHub remote tracking (`refs/pull/6/head`).

---

## 8. Release Tag Decision

- **Existing Tag:** `v1.0.0-research-prototype`
- **Release Candidate Tag:** `v1.0.0-rc1` pointing to commit `7a298d7cd778b9cb06580bee0922630ed91ab1a6`.
- **Annotated Tag Message:** `"DefectVision AI v1.0.0-rc1 — Benchmark-Evaluated Industrial Anomaly Detection Research Prototype"`.
- **Policy Enforcement:** No final production `v1.0.0` tag is created; `v1.0.0-rc1` strictly reflects research prototype maturity with documented limitations.

---

## 9. Complete Documentation Inventory

The project documentation suite is fully synchronized across the repository:

| File Path | Document Purpose |
| :--- | :--- |
| `README.md` | Public project introduction, quickstart, and audited headline performance table |
| `release/portfolio/PROJECT_OVERVIEW.md` | Executive problem motivation, one-class paradigm, and technology stack |
| `release/portfolio/TECHNICAL_ARCHITECTURE_OVERVIEW.md` | In-depth pipeline description with full Mermaid architecture diagram |
| `release/portfolio/MODEL_AND_EXPERIMENT_SUMMARY.md` | Model backbones, FAISS indexing, evaluation protocols, and negative results |
| `release/portfolio/KEY_RESULTS_AND_LIMITATIONS.md` | Disaggregated 15-category results, AUROC/FPR disconnect, and confidence intervals |
| `release/portfolio/DEMO_SCRIPT.md` | 3–5 minute step-by-step live demonstration script for technical evaluation |
| `release/portfolio/INTERVIEW_PREPARATION.md` | 13 rigorous technical Q&As covering theory, math, edge cases, and factory rollout |
| `release/portfolio/screenshots/README.md` | Curated inventory of 15 verified visual evidence assets |
| `release/REPRODUCIBILITY_CHECKLIST.md` | Clean-environment reproduction steps, exact commands, and output schemas |
| `release/audits/FINAL_CLASSIFIER_METRIC_AUDIT.md` | Independent audit reconciling 99.94% category accuracy vs. 86.92% defect baseline |
| `release/audits/FINAL_15_CATEGORY_METRIC_AUDIT.md` | Independent audit reconciling 97.15% Macro AUROC across 1,725 specimens |
| `release/audits/FINAL_STATISTICAL_INTERVAL_AUDIT.md` | Mathematical audit of Clopper–Pearson, Wilson score, and Rule of Three intervals |
| `release/audits/FINAL_POST_RELEASE_VERIFICATION.md` | Verification log of regression tests, build performance, and live API endpoints |
| `release/FINAL_RESEARCH_REPORT.md` | Comprehensive scientific research paper covering all sprint findings |
| `release/DEFECTVISION_V1_FINAL_HANDOVER.md` | Pre-existing final sprint handover document |

---

## 10. Reproduction Instructions

To reproduce the live environment from a fresh terminal:
```powershell
# 1. Start FastAPI Backend (Port 8001):
cd DefectVisionAI
..\.venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8001

# 2. Start Vite Frontend (Port 5174):
cd frontend
npm run dev

# 3. Run Test Suite:
$env:PYTHONPATH = "DefectVisionAI"
.\.venv\Scripts\python.exe -m pytest DefectVisionAI/tests -q
```
Refer to [REPRODUCIBILITY_CHECKLIST.md](file:///c:/Users/surya/Downloads/Mini%20Project/release/REPRODUCIBILITY_CHECKLIST.md) for full reproduction commands.

---

## 11. Demonstration Instructions

Follow the walkthrough in [DEMO_SCRIPT.md](file:///c:/Users/surya/Downloads/Mini%20Project/release/portfolio/DEMO_SCRIPT.md):
1. **Startup:** Open `http://127.0.0.1:5174` and verify `LIVE INFERENCE ACTIVE`.
2. **Nominal Inspection:** Upload `bottle/test/good/000.png` $\to$ Confirm green PASS verdict ($S = 0.82 < 1.50$).
3. **Defective Inspection:** Upload `bottle/test/broken_large/000.png` $\to$ Confirm red FAIL verdict ($S = 1.94 > 1.50$) and dense localized heatmap.
4. **Quality Gate:** Upload a blurry frame $\to$ Confirm HTTP 422 blur rejection.
5. **Profile Guard:** Set profile to `bottle` and upload `cable` $\to$ Confirm category mismatch warning.

---

## 12. Known Issues & Future Research Roadmap

1. **Extreme Value Theory (EVT) Thresholding:** Replace global static thresholds with per-category statistical distribution tail modeling (e.g., Weibull / GPD fitting) to eliminate the 24.84% global false-positive rate.
2. **DINOv2 Self-Supervised Backbone:** Transition from supervised ImageNet ResNet18 to self-supervised DINOv2 (ViT-S/14), which exhibits superior fine-grained structural patch clustering without domain bias.
3. **External Domain Multi-Specimen Benchmark:** Acquire a physically diverse test set ($N \ge 300$ normal, $N \ge 50$ distinct physical defect units) under varied factory illumination to formally validate Track B domain adaptation.
4. **ONNX Runtime / TensorRT Acceleration:** Quantize ResNet18 feature extraction and FAISS retrieval to FP16/INT8 for ultra-low latency edge deployment ($<15\text{ms}$ total cycle time).

---

## 13. Final Project Status

```
========================================================================================
STATUS: RELEASE READY WITH DOCUMENTED METRIC LIMITATIONS
MILESTONE: DefectVision AI v1.0.0-rc1
VERDICT: The system is verified, stable, reproducible, and fully documented.
         All experimental claims are empirically defensible and statistically bounded.
         PR #6 remains OPEN and UNMERGED as specified.
========================================================================================
```
