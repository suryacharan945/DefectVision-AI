# Phase 7C Precheck: Provenance, Category Reconciliation & Evaluation Parity

**Document ID:** `DV-PHASE7C-PRECHECK-V1`  
**Date:** October 31, 2026  
**Auditor:** Lead AI/ML Research Engineer & Experimental Methodology Reviewer  
**Status:** **PASSED / VERIFIED**

---

## 1. VisA Official Inventory Verification

The Visual Anomaly (VisA) dataset inventory was verified against official Google Drive records (`G:\My Drive\DefectVisionAI\experiments\visa_external_validation_v1\reports\visa_dataset_inventory.csv`) and the pre-registered protocol (`research/protocols/Q1_EXPERIMENT_PROTOCOL_V2.json`).

| Category Name | Normal Images | Anomaly Images | Total Images | Exposure Classification | Independent Benchmark Eligibility |
| :--- | :---: | :---: | :---: | :--- | :---: |
| `candle` | 1,000 | 100 | 1,100 | Untouched | **YES** |
| `capsules` | 602 | 100 | 702 | **Development-Exposed** | **NO (Quarantined to Dev)** |
| `cashew` | 500 | 100 | 600 | Untouched | **YES** |
| `chewinggum` | 503 | 100 | 603 | Untouched | **YES** |
| `fryum` | 500 | 100 | 600 | Untouched | **YES** |
| `macaroni1` | 1,000 | 100 | 1,100 | Untouched | **YES** |
| `macaroni2` | 1,000 | 100 | 1,100 | Untouched | **YES** |
| `pcb1` | 1,004 | 100 | 1,104 | Untouched | **YES** |
| `pcb2` | 1,001 | 100 | 1,101 | Untouched | **YES** |
| `pcb3` | 1,006 | 100 | 1,106 | Untouched | **YES** |
| `pcb4` | 1,005 | 100 | 1,105 | Untouched | **YES** |
| `pipe_fryum` | 500 | 100 | 600 | Untouched | **YES** |
| **Total Untouched (11)** | **9,019** | **1,100** | **10,119** | **Untouched** | **YES** |
| **Total VisA (12)** | **9,621** | **1,200** | **10,821** | — | — |

---

## 2. Category Name Discrepancies Resolution

Historical texts and transitional notes contained typographical and colloquial variants of category names. The formal canonical names are resolved as follows:

1. **VisA `capsules` vs MVTec `capsule`:**
   - MVTec AD category is strictly singular: `capsule` (132 test images: 23 good, 109 anomaly).
   - VisA category is strictly plural: `capsules` (160 test images in official test split: 60 good, 100 anomaly; 702 total).
   - The two categories are distinct industrial objects from different datasets with separate memory banks and thresholds.
2. **`chewinggum` vs `chewing_gum`:**
   - Canonical name in VisA official archive is `chewinggum` (no underscore).
3. **`pcb1` through `pcb4` vs `printed_circuit_board`:**
   - Canonical names in VisA are `pcb1`, `pcb2`, `pcb3`, `pcb4`.
   - `printed_circuit_board` and `aerospace_casings` were informal umbrella or placeholder terms; neither exists as a raw category folder in VisA.

---

## 3. Preservation of 330-Image Development Predictions

The exact per-image predictions, scores, and features from Phase 7B are preserved in:
- `DefectVisionAI/research/cpnd/dev_extracted_scores.csv` (SHA-256: verified)
- `research/phase7b_cpnd_development/DEVELOPMENT_BASELINE_COMPARISON.csv`
- `research/phase7b_cpnd_development/REVIEW_BUDGET_RESULTS.csv`
- `research/phase7b_cpnd_development/ABLATION_RESULTS.csv`

All Phase 7B artifacts remain intact and unmodified.

---

## 4. Reconstruction of the 62 Classification Errors

Verification of `DefectVisionAI/research/cpnd/dev_extracted_scores.csv` confirms:
- **Total Evaluated Images:** 330
- **Total Model Classification Errors:** 62 ($18.79\%$ error rate, $81.21\%$ baseline accuracy)
- **False Negatives (FN):** 59 (defects classified as good)
- **False Positives (FP):** 3 (good items classified as defect)

Breakdown by category:
- `bottle`: 83 images, 1 error (0 FN, 1 FP)
- `capsule`: 132 images, 58 errors (57 FN, 1 FP)
- `metal_nut`: 115 images, 3 errors (2 FN, 1 FP)

---

## 5. Metric Disambiguation: Review Yield

Audit of `DefectVisionAI/research/cpnd/cpnd_core.py` (lines 283-296) reveals that the previously reported `review_yield` was computed as:
$$\text{Yield}_{\text{historical}} = \frac{\text{Captured Defects}}{K}$$
where $K$ is the number of reviewed images.

To eliminate ambiguity between auditing defects versus auditing model errors, Phase 7C establishes two explicitly named, standardized metrics:
1. **`Defect_Review_Yield` ($\%$):**
   $$\text{Defect\_Review\_Yield} = \frac{\text{Number of True Defective Images in Audit Sample}}{K} \times 100$$
   *(Indicates operational defect density among reviewed items; high for top-score review).*
2. **`Error_Review_Yield` ($\%$):**
   $$\text{Error\_Review\_Yield} = \frac{\text{Number of Model Classification Errors (FN + FP) in Audit Sample}}{K} \times 100$$
   *(Indicates audit triage efficiency; captures the human reviewer's error-finding rate).*

---

## 6. Verification of Evaluation Parity

All baselines (BL0 Random, BL1 Top Anomaly Score, BL2 Distance-to-Threshold) and candidate uncertainty methods in Phase 7B and Phase 7C operate on the **exact same 330 image IDs, identical PatchCore anomaly scores, identical decision thresholds, and identical ground-truth labels**.

No data leakages, variable test sets, or shifting error definitions exist across candidate comparisons.
