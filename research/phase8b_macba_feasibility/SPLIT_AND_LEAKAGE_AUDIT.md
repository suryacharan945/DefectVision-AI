# Phase 8B: Data Split & Leakage Audit

**Document ID:** `DV-PHASE8B-SPLIT-V1`  
**Date:** October 31, 2026  
**Auditor:** Lead AI/ML Research Engineer & Experimental Methodology Reviewer  
**Scope:** Partitioning Integrity, Defect-Group Mapping, and Anti-Leakage Verification

---

## 1. Development Population Inventory

The feasibility experiment is conducted exclusively on the 330 authorized development images:
- **Total Images:** 330
- **Total Classification Errors:** 62 (59 False Negatives, 3 False Positives)
- **Production Lines (Categories):**
  1. `bottle`: 83 images, 1 error (1 FP, 0 FN).
  2. `capsule`: 132 images, 58 errors (1 FP, 57 FN).
  3. `metal_nut`: 115 images, 3 errors (1 FP, 2 FN).

### Defect Sub-Type Breakdown:
- **`bottle`:** `broken_large` (20), `broken_small` (22), `contamination` (21), `good` (20).
- **`capsule`:** `crack` (23), `faulty_imprint` (22), `poke` (21), `scratch` (23), `squeeze` (20), `good` (23).
- **`metal_nut`:** `bent` (25), `color` (22), `flip` (23), `scratch` (23), `good` (22).

---

## 2. Partitioning Strategy & Anti-Leakage Protocol

To ensure 100% leakage-free evaluation:
1. **Calibration Partition ($\mathcal{D}_{\text{cal}}$, 50%, 165 images):**
   - Used **exclusively** to fit category error-risk estimators $P(\text{Error} \mid S(X), c)$, estimate category error priors $\hat{\pi}_c^{\text{cal}}$, and compute non-conformity calibration parameters.
2. **Internal Evaluation Partition ($\mathcal{D}_{\text{eval}}$, 50%, 165 images):**
   - Used **exclusively** to measure realized allocation performance, error capture rate, and financial loss reduction.
   - **Zero Evaluation Labels in Allocation:** No labels from $\mathcal{D}_{\text{eval}}$, no ground-truth error flags, and no future review outcomes are accessible to any allocation policy at decision time.

### Group-Aware Stratification:
Splitting is stratified by `(category, defect_type, is_error)` using deterministic seed 42 to guarantee balanced defect-type representation across both folds:
- **Calibration Split:** 165 images (31 errors: 0 in bottle, 29 in capsule, 2 in metal_nut).
- **Internal Evaluation Split:** 165 images (31 errors: 1 in bottle, 29 in capsule, 1 in metal_nut).

---

## 3. Methodological Limitation & Exploratory Designation

### Honest Assessment of Sample Size Limitations:
Because `bottle` contains only 1 error and `metal_nut` contains only 3 errors in the development set:
- Any 50/50 partition splits these rare errors into 0 vs 1 observation per line.
- A single captured or missed specimen on `bottle` causes its category ECR to jump between $0\%$ and $100\%$.
- **Formal Protocol Designation:** In compliance with Phase 2 guidelines, this 3-category development analysis is formally designated as an **EXPLORATORY FEASIBILITY STUDY**, not a statistically definitive multi-line proof. Definite validation requires unblinding the 11-category VisA suite under Protocol V3.1.

---

## 4. Quarantining Ledger

The following external datasets remain strictly locked and unread:
- **VisA 11 Untouched Categories:** `candle`, `cashew`, `chewinggum`, `fryum`, `macaroni1`, `macaroni2`, `pcb1`, `pcb2`, `pcb3`, `pcb4`, `pipe_fryum` (10,119 images).
- **BeanTech Anomaly Detection (BTAD):** Categories `01`, `02`, `03` (2,830 images).
- **Chukyo Automotive Dataset:** Quarantined.
- **Audit Confirmation:** Zero test images from these datasets have been loaded, preprocessed, or inspected.
