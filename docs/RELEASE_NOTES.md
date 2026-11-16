# DefectVision AI — Release Notes

## Version 1.1.0 — Real-Time Automatic Category Recognition & 15-Category Anomaly Inspection

**Release Date:** November 2026
**Target Branch:** `feature/realtime-category-inspection`
**Base:** `main`

---

### 1. Key Features & Highlights

1. **Automatic Category Recognition Across All 15 MVTec AD Classes:**
   - Both **Image Upload** (`/predict`, `InspectSection.jsx`) and **Live Camera Stream** (`/api/optical-inspection/inspect-frame`, `LiveStreamInspector.jsx`) now default to automatic category recognition (`category = "auto"`).
   - Eliminates manual operator selection errors while preserving an optional manual category override.

2. **Calibrated Deep Visual Recognizer (EfficientNet-B0):**
   - Fine-tuned lightweight classification head on nominal training samples across all 15 MVTec AD classes.
   - Softmax temperature calibration ($T = 1.3696$) and normalized Shannon entropy ($H_{norm}$) calculation.
   - Achieved **100.00% validation accuracy** (726 images) and **99.94% accuracy** on the official 1,725-image test split (13 out of 15 classes with 100% precision and recall).
   - Fast multi-core CPU inference: median 82.92 ms (mean: 86.82 ms).

3. **Open-Set Out-of-Distribution (OOD) Rejection:**
   - Evaluates Shannon entropy ($H_{norm} \ge 0.65$) and top probability ($p_{top} < 0.70$) to intercept unknown or non-industrial objects.
   - Tested on synthetic noise and solid colors with 100% rejection rate.
   - Returns safe operational verdict `UNSUPPORTED` with conclusion `"UNSUPPORTED OR UNKNOWN CATEGORY"`.

4. **15-Category PatchCore Memory Bank Anomaly Inspection:**
   - Evaluated across all 1,725 official test specimens:
     - **Macro Image AUROC:** **97.15%**
     - **Macro Image AUPRC:** **98.98%**
     - **Defect Recall (Sensitivity):** **95.40%** (1,200 defects detected out of 1,258)
     - **Specificity:** **70.96%** (reflecting a known false-alarm burden on complex textures)
     - **Macro F1-Score:** **92.40%**

5. **Strict 4-State Verdict Contract:**
   - **`NORMAL`** $\rightarrow$ `"NO DEFECT DETECTED"`
   - **`DEFECTIVE`** $\rightarrow$ `"POSSIBLE DEFECT DETECTED"`
   - **`REVIEW REQUIRED`** $\rightarrow$ `"MANUAL INSPECTION REQUIRED"` (borderline $\pm 8\%$ margin or optical quality failure)
   - **`UNSUPPORTED`** $\rightarrow$ `"UNSUPPORTED OR UNKNOWN CATEGORY"`

6. **Standardized Operational Disclaimer:**
   - Embedded across all generated operator diagnostic records:
     > *"The result reflects the model's learned visual patterns and does not guarantee the absence of all possible defects."*

7. **Full Test Suite & Production Build:**
   - 48 / 48 unit and integration tests passing (100% success in 4.47s).
   - Frontend production build (`npm run build`) succeeded in 4.20s with 0 errors.

---

### 2. Upgrades & Backwards Compatibility

- **Backwards Compatible `/predict` Endpoint:** Accepts legacy requests with explicit category names (e.g., `category="bottle"`) while defaulting to `category="auto"` when omitted or explicitly requested.
- **Backwards Compatible Client API:** `client.predict(file, category = 'auto')` preserves existing call sites while enabling zero-click category routing.

---

### 3. File Inventory Summary

#### New Services & Backends:
- `DefectVisionAI/src/camera_service.py`: Real-Time Optical Engine with unified schema and conclusion mapping.
- `DefectVisionAI/src/category_classifier.py`: EfficientNet-B0 15-class recognizer with temperature scaling.
- `DefectVisionAI/src/category_model_registry.py`: Model deployment status and metadata lookup.
- `DefectVisionAI/src/decision_fusion_service.py`: 4-state verdict fusion engine with $\pm 8\%$ borderline band.
- `DefectVisionAI/src/image_quality_service.py`: Calibrated optical quality gate (sharpness, luminance, contrast).
- `DefectVisionAI/src/inspection_history_service.py`: Thread-safe inspection audit ring buffer.
- `DefectVisionAI/src/object_region_service.py`: Otsu contour extraction for objects and center crops for textures.

#### Updated User Interfaces:
- `frontend/src/components/sections/InspectSection.jsx`: Image Upload with auto-recognition default, colored 4-state banners, and quality chips.
- `frontend/src/pages/LiveStreamInspector.jsx`: Live Camera with HUD reticle, conclusion banners, and audit modal.
- `frontend/src/api/client.js`: Default `category = 'auto'` with backwards compatibility.

#### Comprehensive Benchmark Artefacts:
- `release/category_recognition/category_metrics.csv`
- `release/category_recognition/category_recognition_report.md`
- `release/category_recognition/confusion_matrix_val.png`
- `release/category_recognition/confusion_matrix_test.png`
- `release/patchcore_evaluation/patchcore_per_category_metrics.csv`
- `release/patchcore_evaluation/patchcore_evaluation_report.md`
- `release/dataset_manifests/`: Full deterministic split CSVs.
