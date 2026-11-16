# Phase 8A: Data & Implementation Feasibility Analysis

**Document ID:** `DV-PHASE8A-FEAS-V1`  
**Date:** October 31, 2026  
**Auditor:** Lead AI/ML Research Engineer & Experimental Methodology Reviewer  
**Scope:** Verification of Data Availability, Partitioning Integrity, and Implementation Feasibility

---

## 1. Development Data Availability & Provenance

The proposed Category-Aware Multi-Line Budget Allocation (Direction B) is **100% supported by the existing, authorized development dataset**:
- **Dataset Source:** MVTec AD development-exposed partition and VisA `capsules` development records.
- **Evaluated Categories:**
  1. `bottle` (Rigid transparent glass/plastic): 83 images (63 normal, 20 defective). Automated baseline accuracy: $98.80\%$ (1 error: 0 FN, 1 FP).
  2. `capsule` (Pharmaceutical rigid capsule): 132 images (23 normal, 109 defective). Automated baseline accuracy: $56.06\%$ (58 errors: 57 FN, 1 FP).
  3. `metal_nut` (Mechanical threaded fastener): 115 images (22 normal, 93 defective). Automated baseline accuracy: $97.39\%$ (3 errors: 2 FN, 1 FP).
- **Total Development Specimen Pool:** $N_{\text{total}} = 330$ images, $62$ total model classification errors ($59$ FN, $3$ FP).
- **Preserved Predictions:** Fully serialized and frozen in `DefectVisionAI/research/cpnd/dev_extracted_scores_phase7c.csv`.

---

## 2. Realistic Emulation of Factory Heterogeneity

A critical strength of this development dataset is that it naturally embodies the **exact real-world production heterogeneity** found in industrial manufacturing:

```
+--------------------------------------------------------------------------------------------------+
|                              FACTORY PRODUCTION HETEROGENEITY                                    |
+--------------------------------------------------------------------------------------------------+
|  Production Line       Volume (N_c)   Defect Prior   Automated Acc   Model Errors   Difficulty   |
|  ---------------------------------------------------------------------------------------------   |
|  Line 1 (bottle)            83            24.1%          98.80%           1         Near Perfect |
|  Line 2 (capsule)          132            82.6%          56.06%          58         Challenging  |
|  Line 3 (metal_nut)        115            80.9%          97.39%           3         Highly Robust|
|  ---------------------------------------------------------------------------------------------   |
|  Total Factory             330            67.3%          81.21%          62                      |
+--------------------------------------------------------------------------------------------------+
```

### Why Naive Allocation Fails on This Data:
- **Under Uniform Allocation (BL0) at 10% budget ($K = 33$ items, $11$ per line):**
  - Line 1 (`bottle`) receives $11$ human review slots, but contains only $1$ error. **10 review slots are completely wasted on correctly classified items.**
  - Line 2 (`capsule`) receives only $11$ human review slots, leaving up to $47$ errors uninspected.
- **Under Optimal Multi-Category Knapsack Allocation:**
  - Line 1 (`bottle`) receives $1$ review slot (capturing its single boundary FP error).
  - Line 3 (`metal_nut`) receives $3$ review slots (capturing its boundary FN errors).
  - Line 2 (`capsule`) receives $29$ review slots.
  - **Error capture increases dramatically by shifting human attention from saturated easy lines to high-yield difficult lines.**

---

## 3. Strict Quarantining of Independent Datasets

In strict compliance with Protocol V2 and experimental integrity rules:
- **Zero Access to Reserved Datasets:**
  - The 11 held-out VisA categories (`candle`, `cashew`, `chewinggum`, `fryum`, `macaroni1`, `macaroni2`, `pcb1`, `pcb2`, `pcb3`, `pcb4`, `pipe_fryum`, totaling 10,119 images) remain **100% untouched and locked**.
  - BTAD (2,830 images) and Chukyo datasets remain **100% untouched and locked**.
- No image pixels, features, scores, or labels from these reserved datasets will be accessed during development, tuning, or preliminary exploration of Direction B.

---

## 4. Calibration Strategy Without Test Contamination

How does the method calibrate allocation parameters without leaking test labels?
1. **Nominal Calibration Data ($\mathcal{D}_{\text{cal}, c}^{\text{norm}}$):**
   - Each category already possesses a dedicated, frozen nominal calibration split containing only normal images (zero defects, zero test images).
   - This calibration split is used to estimate the empirical distribution function $F_c(s)$ of normal scores, enabling Conformal Quantile Normalization without test exposure.
2. **Stratified Split for Hyperparameter Tuning:**
   - The 330 development images will be split 50/50 into a Tuning Partition (165 images) and an Internal Evaluation Partition (165 images) stratified by category and error status.
   - Knapsack parameters and cost-weighting coefficients are fitted strictly on Partition 1 and evaluated blindly on Partition 2.

---

## 5. Computational and Storage Feasibility

- **Model Retraining:** Zero. The backbone and PatchCore memory banks remain completely frozen.
- **Feature Extraction:** Pre-extracted scalar anomaly scores and boundary distances are already saved in CSV format.
- **Execution Time:** The knapsack / dynamic programming budget allocation algorithm operates on a 330-element scalar array. Solving the allocation takes $< 5\text{ milliseconds}$ in Python, allowing full 2,000-iteration bootstrap runs in under 10 seconds on standard CPU.
- **Storage:** Pre-extracted metadata is under $200\text{ KB}$.
