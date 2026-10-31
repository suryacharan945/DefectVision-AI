# BENCHMARK INDEPENDENCE AUDIT: THE 856-IMAGE SPLIT

**Project:** DefectVision AI  
**Audit Date:** October 31, 2026  
**Auditor:** Lead AI/ML Verification & Full-Stack Release Engineer  
**Release Target:** Commit `91d3743` / `delivery_24h`  

---

## 1. Executive Summary & Audit Verdict

Prior project documentation designated the 856-image subset (`step8_benchmark_856.csv`) as a "strictly held-out, leak-free independent benchmark" for evaluating EfficientNet-B0 v3 and PatchCore.

This audit conducted an independent chronological and forensic investigation of the data lineage.

### Formal Audit Classification:
**DISJOINT DEVELOPMENT-EVALUATED PARTITION (NOT INDEPENDENT HELD-OUT)**

While `step8_benchmark_856.csv` is strictly disjoint from `step8_dev_split.csv` at the image-identifier level, it **was carved out of the official test set after the full test population had already been evaluated during early model selection.** Therefore, in accordance with IEEE/ACM experimental standards, it cannot be characterized as an untouched, independent benchmark in a Q1 research submission without explicit methodological qualification.

---

## 2. Chronological Data Lineage Audit

Forensic inspection of the master Google Colab notebook (`DefectVisionAI.ipynb`) and historical log files establishes the exact sequence of data partitioning:

```
[MVTec AD Official Dataset] (5,354 images across 15 categories)
   |
   +---> STEP 3 (Cell 5): Initial Partitioning
   |        |
   |        +---> train_split.csv:  1,675 Normal Images (Exclusively Normal)
   |        +---> val_split.csv:      419 Normal Images (Exclusively Normal)
   |        +---> test_split.csv:   1,725 Images (467 Normal, 1,258 Defective)
   |
   +---> STEP 8 (v1 Execution): FULL TEST EXPOSURE
   |        |
   |        v
   |     EfficientNet-B0 (v1 & v2) evaluated on ALL 1,725 images of test_split.csv!
   |     Results logged in `DefectVisionAI/reports/step8_baseline_results.csv`.
   |     Hyperparameters, thresholds, and backbone choices refined based on this evaluation.
   |
   +---> STEP 8 (v3 Patch - Cell 11): POST-HOC PARTITIONING
            |
            v
         Acknowledging leakage from earlier evaluations, Cell 11 split test_split.csv (1,725 images)
         using a stratified 50/50 split (random_state=42):
            |
            +---> step8_dev_split.csv:      869 Images (Used for threshold calibration & tuning)
            +---> step8_benchmark_856.csv:  856 Images (Preserved as "unseen" benchmark)
```

### Forensic Findings:
1. **Prior Exposure:** Every one of the 856 images in `step8_benchmark_856.csv` was subjected to inference during the Step 8 v1 evaluation run.
2. **Model Selection Feedback Loop:** The architectural modifications in EfficientNet-B0 v3 (data augmentations, learning rate schedules, and layer unfreezing) were implemented *after* inspecting failure modes on the entire 1,725-image test split.
3. **Disjoint Status:** Between `step8_dev_split.csv` (869 images) and `step8_benchmark_856.csv` (856 images), there is **0% image identifier overlap** ($869 + 856 = 1,725$).
4. **Methodological Conclusion:** Post-hoc partitioning of an already exposed dataset mitigates direct overfitting during final evaluation, but **does not restore independent test status**. The split must be reported as an *internal validation partition* rather than a blind external test set.

---

## 3. Recalculation & Verification of Reported Metrics

We executed an independent, zero-assumption numerical recalculation (`scripts/verify_fair_recalculation.py`) using the raw frozen predictions stored in `DefectVisionAI/logs/step8_efficientnet_v3_on_benchmark.csv` (856 observations).

### Verification Results

| Metric | Prior Reported Value | Independently Recalculated | Delta | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Macro-Category AUROC** | `0.9732` | `0.9732` | `0.0000` | **EXACT MATCH** |
| **Pooled-Sample AUROC** | `0.9809` | `0.9809` | `0.0000` | **EXACT MATCH** |
| **Overall Accuracy** | `86.92%` (744/856) | `86.9159%` | `0.0000` | **EXACT MATCH** |
| **Precision** | `99.81%` (526/527) | `99.8102%` | `0.0000` | **EXACT MATCH** |
| **Recall / Sensitivity** | `82.19%` (526/640) | `82.1875%` | `0.0000` | **EXACT MATCH** |
| **Specificity** | `99.54%` (215/216) | `99.5370%` | `0.0000` | **EXACT MATCH** |
| **F1-Score** | `0.9015` | `0.9015` | `0.0000` | **EXACT MATCH** |

### Confusion Matrix on the 856-Image Split:
- **True Positives (TP):** 526
- **False Negatives (FN / Defect Escapes):** 114
- **False Positives (FP / False Alarms):** 1
- **True Negatives (TN):** 215
- **Total Population:** 856 (640 Defective, 216 Normal)

---

## 4. Macro-Category AUROC vs. Pooled AUROC Discrepancy

A critical scientific distinction that must be preserved in publication is the difference between Macro-Category AUROC and Pooled AUROC:

1. **Macro-Category AUROC ($0.9732$):**
   Computed by calculating the ROC curve independently for each of the 15 MVTec categories and averaging their individual AUROCs equally:
   $$\text{AUROC}_{\text{macro}} = \frac{1}{15} \sum_{c=1}^{15} \text{AUROC}_c$$
   - Top Categories: `bottle` ($1.0000$), `capsule` ($0.9984$), `carpet` ($0.9942$), `metal_nut` ($0.9912$).
   - Lowest Categories: `screw` ($0.9214$), `transistor` ($0.9340$), `zipper` ($0.9410$).

2. **Pooled-Sample AUROC ($0.9809$):**
   Computed by merging all 856 prediction probabilities into a single global ranking vector and evaluating a single global ROC curve.
   - **Why Pooled is Higher:** Because categories with larger numbers of easily separable defects dominate the global true-positive rate, slightly inflating the pooled metric relative to the unweighted category average.

> [!IMPORTANT]
> In any Q1 journal submission, **Macro-Category AUROC ($0.9732$) must be reported as the primary metric**, as industrial standards (such as Bergmann et al., MVTec AD benchmark) require equal weighting across distinct object and texture classes.

---

## 5. Chukyo Real-World Data Quarantine Confirmation

The external Chukyo dataset (`DefectVisionAI/data/chukyo/...`) was thoroughly audited:
- **Prior Findings:** Contains 25 duplicate similarity pairs and 14 same-capture identical pairs with unresolved illumination and temporal correlation.
- **Current Status:** **CONFIRMED QUARANTINED IN COLD STORAGE.**
- **Verification:** No script in the active inference path (`app.py`, `test_backend_inference.py`, `e2e_backend_test.py`) touches or loads the Chukyo directory. It has not contributed to any reported metric in this audit.

---

## 6. Recommendations for Q1 Journal Submission

To ensure bulletproof review during peer evaluation:
1. Re-label `step8_benchmark_856.csv` in all figures and tables as:
   `"MVTec AD Internal Development-Evaluated Partition (N = 856)"`.
2. Do not use the term "Untouched Held-Out Test Set" for this partition.
3. Validate the model on a completely external, unexposed dataset such as **VisA (Visual Anomaly Dataset, 10,821 images)** or **MPDD (Mobile Phone Defect Dataset)** to present genuine held-out cross-dataset generalization results.
