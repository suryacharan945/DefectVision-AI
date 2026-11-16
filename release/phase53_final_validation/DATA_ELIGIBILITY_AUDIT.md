# DefectVision AI — Forensic Data and Model Eligibility Audit

**Phase:** Phase 53 — Final Independent Hybrid Validation and Research Decision  
**Role:** Senior Computer Vision Engineer, Independent ML Evaluator, and Research Integrity Auditor  
**Workspace:** `C:\Users\surya\Downloads\Mini Project`  
**Date:** November 2, 2026  
**Primary Source Reference:** `release/phase46_independent_validation/DATASET_ELIGIBILITY_AUDIT.md`, `release/final_18h_validation/FINAL_EVIDENCE_AUDIT.md`, `release/phase49_independent_results/`  

---

## 1. Executive Summary & Stop Condition Determination

```
================================================================================
                    DATA ELIGIBILITY AUDIT DETERMINATION
================================================================================

STATUS: INDEPENDENT HYBRID VALIDATION: BLOCKED — NO ELIGIBLE DATA

RATIONALE:
1. The frozen supervised classifier (EfficientNet-B0 v3) was trained exclusively 
   on the 15 MVTec AD industrial categories (closed-world binary classification).
2. The only untouched, independently acquired dataset physically resident on local 
   storage is the Visual Anomaly (VisA) Cashew benchmark (200 test specimens).
3. The existing EfficientNet-B0 v3 classifier does not support the Cashew category. 
   Evaluating EfficientNet on Cashew would produce uncalibrated out-of-distribution 
   noise, while retraining EfficientNet is strictly prohibited under research freeze.
4. The 856-image MVTec AD benchmark is Category C Development-Exposed and cannot 
   be substituted as an independent zero-leakage benchmark.
5. All other external datasets (VisA other 11 categories, Chukyo capsules, BTAD) 
   are either quarantined, physically absent, or architecturally unsupported.

STOP CONDITION INVOCATION:
Under Step 1 governing rules: "If no eligible independent cohort exists, record: 
INDEPENDENT HYBRID VALIDATION: BLOCKED — NO ELIGIBLE DATA... Step 2 is skipped."
Evaluation of the complete hybrid architecture on an independent benchmark cannot 
proceed without violating research integrity or retraining models.

================================================================================
```

---

## 2. Complete Inventory of Frozen Models & Checkpoints

| Component | Architecture & Pretraining | Supported Categories | Checkpoint Location & Size | Training Split Provenance | Exposure Classification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Supervised Classifier** | EfficientNet-B0 v3 (`timm`, ImageNet pre-trained) | **15 MVTec Categories Only** (`bottle`, `cable`, `capsule`, `carpet`, `grid`, `hazelnut`, `leather`, `metal_nut`, `pill`, `screw`, `tile`, `toothbrush`, `transistor`, `wood`, `zipper`) | `DefectVisionAI/models/efficientnet_baseline_v3/best_model.pt` ($16,336,185$ bytes, 360 tensor keys) | `supervised_train_split_v3.csv` ($3,499$ images), `supervised_val_split_v3.csv` ($632$ images) | **Development-Exposed (MVTec AD)** |
| **PatchCore Memory Banks (MVTec)** | ResNet-18 (layer2 + layer3, $D=384$) + FAISS `IndexFlatL2` | **15 MVTec Categories Only** | `DefectVisionAI/models/patchcore/<cat>/memory_bank.npy` ($400\text{ MB}$ total across 15 classes) | $3,629$ MVTec nominal training images; baseline calibration in `step9_severity_baselines.csv` ($750$ images) | **Development-Exposed (MVTec AD)** |
| **PatchCore Memory Bank (Cashew)** | ResNet-18 (layer2 + layer3, $D=384$) + FAISS `IndexFlatL2` | **VisA Cashew Only** | `release/phase49_independent_results/models/patchcore_cashew/` ($40.2\text{ MB}$, $27,440$ coreset tokens) | $350$ VisA cashew nominal registration images; $\tau_{\text{p99}} = 1.745232$ ($50$ held-out nominals) | **Independent Target-Domain Registered (Phase 49)** |

---

## 3. Forensic Dataset Accounting Across All Available Repositories

### A. MVTec Anomaly Detection (MVTec AD)
*   **Total Images:** 5,354 images across 15 categories.
*   **Test Cohort Evaluated:** 856 images (625 defective, 231 nominal).
*   **Exposure Status:** **Category C Development-Exposed.** Models, coreset subsampling ratios ($\kappa = 0.10$), and decision thresholds ($\tau_{\text{p99}}$) were iteratively tuned against MVTec data during development phases.
*   **Eligibility for Step 2:** **DISQUALIFIED.** Explicitly prohibited by directive: *"Do not substitute the previously development-exposed 856-image MVTec benchmark."*

### B. Visual Anomaly Dataset (VisA) — Cashew Category
*   **Total Images:** 600 images (500 nominal, 100 defective).
*   **Partitioning:** 350 registration nominals, 50 calibration nominals, 200 test specimens (100 nominal, 100 defective).
*   **Physical Presence:** Resident locally at `G:\My Drive\DefectVisionAI\dataset\raw\visa\cashew\`.
*   **PatchCore Compatibility:** Compatible and independently evaluated in Phase 49 ($0.9237$ AUROC, $0.9930$ pixel AUROC).
*   **EfficientNet Compatibility:** **INCOMPATIBLE.** EfficientNet-B0 v3 was trained as a binary classifier on MVTec objects and has never seen cashew nuts. Passing cashew images to EfficientNet-B0 produces arbitrary logits ($p_{\text{defect}}$ fluctuates with zero calibration).
*   **Eligibility for Step 2:** **DISQUALIFIED AS A COMPLETE HYBRID BENCHMARK.** Explicitly prohibited by directive: *"Do not use VisA cashew as complete hybrid validation because the existing EfficientNet classifier does not support that category."*

### C. Visual Anomaly Dataset (VisA) — Other 11 Categories
*   **Categories:** `candle`, `capsules`, `chewinggum`, `fryum`, `macaroni1`, `macaroni2`, `pcb1`, `pcb2`, `pcb3`, `pcb4`, `pipe_fryum`.
*   **Physical Presence:** **ABSENT FROM LOCAL DISK.** Raw images were hosted on ephemeral cloud storage during historical surveys and were never retained on local storage or Google Drive.
*   **Model Compatibility:** Zero memory banks exist; EfficientNet does not support these classes.
*   **Eligibility for Step 2:** **DISQUALIFIED.** Downloading GBs of data is strictly prohibited.

### D. Chukyo Industrial Capsule Dataset
*   **Physical Location:** `G:\My Drive\DefectVisionAI\experiments\external_capsule_chukyo_v1\dataset\chukyo_capsules.zip`.
*   **Audit Status:** Quarantined under classification `BLOCKED_INCOMPLETE_REFERENCE_AUDIT`.
*   **Eligibility for Step 2:** **DISQUALIFIED.** Quarantines must not be breached.

### E. BeanTech Anomaly Detection (BTAD)
*   **Status:** Completely unextracted, absent from disk, and lacks target-domain nominal memory banks.
*   **Eligibility for Step 2:** **DISQUALIFIED.**

---

## 4. Synthesis of Data & Model Compatibility Matrix

```
+------------------+-----------------------+---------------------+-------------------------------+
| Dataset Category | EfficientNet Support  | PatchCore Support   | Joint Hybrid Eligibility      |
+------------------+-----------------------+---------------------+-------------------------------+
| MVTec (15 cats)  | YES (Trained on it)   | YES (Fitted on it)  | INELIGIBLE (Dev-Exposed)      |
| VisA Cashew      | NO (Unsupported class)| YES (Registered)    | INELIGIBLE (EffNet Incompatible)|
| VisA Capsules    | NO (Unsupported class)| NO (MVTec mismatch) | INELIGIBLE (Exposed & Absent) |
| VisA Other (10)  | NO (Unsupported class)| NO (No memory bank) | INELIGIBLE (Physically Absent)|
| Chukyo Capsules  | NO (Unsupported class)| NO (Uncalibrated)   | INELIGIBLE (Quarantined)      |
| BTAD (01, 02, 03)| NO (Unsupported class)| NO (No memory bank) | INELIGIBLE (Physically Absent)|
+------------------+-----------------------+---------------------+-------------------------------+
```

---

## 5. Formal Conclusion

No dataset exists that satisfies the dual constraints of:
1.  Complete zero-leakage independence from previous model development; AND
2.  Joint architectural compatibility with both frozen components (EfficientNet-B0 v3 and PatchCore).

Therefore, in strict compliance with research integrity standards:
**INDEPENDENT HYBRID VALIDATION: BLOCKED — NO ELIGIBLE DATA.**
Step 2 is skipped.
