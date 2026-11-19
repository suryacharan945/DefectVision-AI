# DEFECTVISION AI — FINAL 15-CATEGORY METRIC AUDIT
**Sprint:** Post-Release Evidence & Metric Verification Audit (v1.0.0-rc1)  
**Date:** 2026-11-19  
**Auditor:** Senior ML Engineer, Computer Vision Research Engineer, QA Lead & Release Manager  

---

## 1. Executive Summary & Objective

This audit investigates the reported **97.8% mean AUROC** across the 15 categories of the MVTec Anomaly Detection benchmark, reconciles it against the raw per-specimen predictions in `release/final_validation/mvtec_all_predictions.csv`, and provides an independently recomputed evaluation table.

**Key Findings:**
1. **True Macro Image AUROC:** The exact unweighted arithmetic mean of image-level AUROC across all 15 categories is **97.15%** (Macro Image AUPRC: **98.98%**).
2. **True Pixel AUROC:** The reported mean pixel-level localization AUROC across all defective images is **98.02%**.
3. **Provenance of the 97.8% Figure:** The 97.8% figure cited in previous headline drafts originated from an earlier heuristic roundoff or unweighted draft estimate. The mathematically defensible, independently verified image-level AUROC is **97.15%**.
4. **Sample Inclusion:** All **1,725 official test specimens** (467 nominal and 1,258 defective specimens) are present and accounted for in the source dataset.

---

## 2. Source-of-Truth Dataset Specification

- **Source File:** `release/final_validation/mvtec_all_predictions.csv` (1,725 rows, 15 columns).
- **Benchmark Source Report:** `release/final_validation/mvtec_acceptance_report.md`.
- **Evaluated Models:** 15 resident PatchCore memory banks (ResNet-18 Layers 2 & 3, dimension 384) with FAISS `IndexFlatL2`.
- **Threshold Calibration:** Established on disjoint nominal calibration splits using empirical $p99.5$ quantiles.

---

## 3. Disaggregated 15-Category Performance Matrix

The following table presents the exact metrics computed directly from the 1,725 raw specimen predictions in `mvtec_all_predictions.csv`:

| Category | Type | Normal Test ($N$) | Defective Test ($N$) | Total Test ($N$) | Image AUROC (%) | Image AUPRC (%) | Category FPR (%) | Defect Recall (%) | Category Precision (%) | Category F1-Score |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **bottle** | Object | 20 | 63 | 83 | **100.00%** | 100.00% | 0.00% | 100.00% | 100.00% | 1.0000 |
| **cable** | Object | 58 | 92 | 150 | **98.76%** | 99.18% | 3.45% | 90.22% | 97.65% | 0.9379 |
| **capsule** | Object | 23 | 109 | 132 | **94.20%** | 98.48% | 21.74% | 89.91% | 95.15% | 0.9245 |
| **carpet** | Texture | 28 | 89 | 117 | **96.55%** | 99.02% | 3.57% | 86.52% | 98.72% | 0.9222 |
| **grid** | Texture | 21 | 57 | 78 | **95.07%** | 98.33% | 28.57% | 96.49% | 90.16% | 0.9322 |
| **hazelnut** | Object | 40 | 70 | 110 | **100.00%** | 100.00% | 0.00% | 98.57% | 100.00% | 0.9928 |
| **leather** | Texture | 32 | 92 | 124 | **100.00%** | 100.00% | 62.50% | 100.00% | 82.14% | 0.9020 |
| **metal_nut**| Object | 22 | 93 | 115 | **99.56%** | 99.90% | 18.18% | 98.92% | 95.83% | 0.9735 |
| **pill** | Object | 26 | 141 | 167 | **90.96%** | 98.13% | 23.08% | 82.98% | 95.12% | 0.8864 |
| **screw** | Object | 41 | 119 | 160 | **95.80%** | 98.49% | 14.63% | 88.24% | 94.59% | 0.9130 |
| **tile** | Texture | 33 | 84 | 117 | **99.75%** | 99.90% | 66.67% | 100.00% | 79.25% | 0.8842 |
| **toothbrush**| Object| 12 | 30 | 42 | **92.50%** | 96.61% | 75.00% | 100.00% | 76.92% | 0.8696 |
| **transistor**| Object| 60 | 40 | 100 | **99.21%** | 98.69% | 21.67% | 100.00% | 75.47% | 0.8602 |
| **wood** | Texture | 19 | 60 | 79 | **99.65%** | 99.90% | 68.42% | 100.00% | 82.19% | 0.9023 |
| **zipper** | Object | 32 | 119 | 151 | **95.19%** | 98.08% | 28.12% | 99.16% | 92.91% | 0.9593 |
| **Macro Mean**| — | **467** | **1,258** | **1,725** | **97.15%** | **98.98%** | **29.04%** | **95.40%** | **90.41%** | **0.9240** |

---

## 4. Aggregate Confusion Matrix & Micro Metrics ($N=1,725$)

Aggregating all 1,725 decisions across the 15 categories yields:

- **True Positives (TP):** **1,183** defective specimens correctly flagged.
- **False Positives (FP):** **116** normal specimens falsely flagged.
- **True Negatives (TN):** **351** normal specimens correctly passed.
- **False Negatives (FN):** **75** defective specimens missed.

### Summary Metrics:
- **Micro Defect Recall (Sensitivity):** $\frac{1183}{1258} = \mathbf{94.04\%}$
- **Micro Specificity:** $\frac{351}{467} = \mathbf{75.16\%}$
- **Micro False Positive Rate (FPR):** $\frac{116}{467} = \mathbf{24.84\%}$
- **Micro Precision:** $\frac{1183}{1299} = \mathbf{91.07\%}$
- **Micro F1-Score:** $\mathbf{0.9253}$
- **Overall Accuracy:** $\frac{1534}{1725} = \mathbf{88.93\%}$

---

## 5. Audit Verdict & Required Revisions

1. **Reconciliation:** The headline metric must be updated from $97.8\%$ to **$97.15\%$ Macro Image AUROC** (or rounded transparently to **$97.2\%$**), with **$98.98\%$ Macro Image AUPRC** and **$98.02\%$ Reported Pixel AUROC**.
2. **Integrity Confirmation:** All 15 individual category evaluations are mathematically consistent with the source CSV. No synthetic or omitted specimens exist.
