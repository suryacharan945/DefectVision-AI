# DefectVision AI — Phase 46: Forensic Dataset Eligibility and Provenance Audit

**Document Type:** Dataset Provenance, Exposure Accounting, and Evaluation Eligibility Audit  
**Phase:** Phase 46 — Independent Validation and Applied Research Gate  
**Auditor:** Senior Computer Vision Research Engineer & Experimental Methodology Auditor  
**Date:** November 2, 2026  
**Git Baseline Commit:** `e6959ba10ddf4ce136a7a39950907582ba9938a4`  
**Primary Audit References:**  
- `release/final_18h_validation/FINAL_EVIDENCE_AUDIT.md`  
- `release/project_closure/PROJECT_CLOSURE_DECISION.md`  
- `release/project_closure/RESEARCH_LIMITATIONS.md`  
- `release/final_integrity_gate/DATASET_EXPOSURE_RECONCILIATION.md`  
- `G:\My Drive\DefectVisionAI\experiments\external_capsule_chukyo_v1\audit\dataset_audit.json`  

---

## 1. Executive Summary & Critical Stop Rule Determination

This audit provides an exhaustive, forensically verified assessment of all candidate image datasets available for evaluating DefectVision AI models outside the development cohort.

### 1.1 Findings Summary
1. **Zero Candidate Datasets Are Immediately Eligible:** No external dataset satisfies all criteria for immediate, unassisted zero-shot inference under the frozen model constraints.
2. **Exposure of Primary Benchmark:** The 856-image MVTec AD benchmark (`release/final_18h_validation/evaluation_predictions.csv`) is formally audited and classified as **Category C: Development-Exposed**. While free of direct label leakage during Phase 2 evaluation, its normal training distributions and category thresholds were repeatedly accessed during feature tuning, calibration, and early architecture iterations. It cannot serve as an independent generalization benchmark.
3. **VisA Benchmark Exposure & Structural Incompatibility:**
   - The Visual Anomaly (VisA) dataset comprises **exactly 12 categories**.
   - `capsules` (702 images) is **DEVELOPMENT-EXPOSED** (fitted in `visa_development_v2`, evaluated in `official_test_v1`).
   - `candle`, `macaroni1`, `macaroni2`, and `pcb1` (4,404 images) are **UNKNOWN / DISPUTED** due to exploratory parameter citations and unverifiable file-access logs.
   - Seven categories (`pcb2`, `pcb3`, `pcb4`, `cashew`, `chewinggum`, `fryum`, `pipe_fryum` — 5,715 images) are **POTENTIALLY UNTOUCHED**; however, their raw image files were hosted on Google Colab ephemeral storage (`/content/defectvision_external/visa_extracted/`) and are **not physically present on local storage or Google Drive**. Furthermore, DefectVision AI’s frozen models are strictly category-specific (15 MVTec categories only) and possess **zero memory banks or classifier heads** for VisA categories.
4. **Chukyo Dataset Quarantined:** The 1,200 capsule images in `external_capsule_chukyo_v1/dataset/chukyo_capsules.zip` remain legally and methodologically blocked under the prior audit classification `BLOCKED_INCOMPLETE_REFERENCE_AUDIT`. In addition, mapping medicinal gelatin capsules to translucent cosmetic MVTec capsule memory banks without on-site baseline calibration represents an invalid category conflation.
5. **BTAD Quarantined & Physically Absent:** The BeanTech Anomaly Detection (BTAD) benchmark (2,830 images across 3 products) is completely unextracted, not present on disk, and incompatible with frozen MVTec memory banks without category-specific nominal adaptation.

### 1.2 Invocation of the Critical Stop Rule
Under the governing experimental methodology directive:
> *"CRITICAL STOP RULE: If no independently eligible evaluation dataset exists, do not run external inference. Do not override any existing quarantine or data-use restriction. Report the blocker and provide the minimum legitimate steps needed to resolve it."*

**DETERMINATION: CRITICAL STOP RULE TRIGGERED.**  
External inference (Phase C) and empirical perturbation experiments (Phase D) are **PROHIBITED**. No synthetic proxies, uncalibrated domain mappings, or unauthorized downloads will be performed.

---

## 2. Forensic Candidate Dataset Audits

### 2.1 MVTec Anomaly Detection (MVTec AD)
- **Origin & Reference:** Bergmann et al., "MVTec AD — A Comprehensive Real-World Dataset for Unsupervised Anomaly Detection", CVPR 2019 / IJCV 2021.
- **License:** Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0).
- **Population:** 5,354 high-resolution color images across 15 industrial manufacturing categories (10 objects: `bottle`, `cable`, `capsule`, `hazelnut`, `metal_nut`, `pill`, `screw`, `toothbrush`, `transistor`, `zipper`; 5 textures: `carpet`, `grid`, `leather`, `tile`, `wood`).
- **Physical Location:** `G:\My Drive\DefectVisionAI\dataset\raw\mvtec` and local development caches.
- **Exposure History:**
  - 3,629 normal images utilized to fit patch memory banks and compute FAISS index vectors.
  - 15 category baseline distributions ($\mu_{\text{baseline}}$, $\tau_{\text{p99}}$) calculated in `DefectVisionAI/reports/step9_severity_baselines.csv`.
  - 856 evaluation images repeatedly evaluated across Phase 7, Phase 8, Phase 9, and the final 18-hour sprint.
  - Three categories (`bottle`, `capsule`, `metal_nut`) subjected to extensive threshold exploration during CPND and MACBA development.
- **Duplicate & Capture Bias:** All MVTec images were acquired under identical laboratory lighting, high-resolution telecentric lenses, and uniform background stages. Models exhibit severe sensitivity to camera focal length and illumination angle.
- **Category Compatibility:** 100% native compatibility (the frozen models were built specifically for these 15 categories).
- **Eligibility Verdict:** **INELIGIBLE** for independent out-of-distribution evaluation. Valid strictly as an in-domain developmental benchmark.

---

### 2.2 Visual Anomaly Dataset (VisA)
- **Origin & Reference:** Zou et al., "Spot-the-Difference: An Anomaly Detection Benchmark for Spotting Component and Surface Defects", ECCV 2022.
- **License:** Creative Commons Attribution 4.0 International (CC BY 4.0).
- **Population:** 10,821 images (9,621 normal, 1,200 defective) across exactly 12 industrial subsets grouped into three structural domains:
  1. *Multi-Instance (complex object clusters):* `capsules` (702), `candle` (1,100), `macaroni1` (1,100), `macaroni2` (1,100).
  2. *Printed Circuit Boards (structured planar electronics):* `pcb1` (1,104), `pcb2` (1,101), `pcb3` (1,106), `pcb4` (1,105).
  3. *Aligned Objects (single centered specimens):* `cashew` (600), `chewinggum` (603), `fryum` (600), `pipe_fryum` (600).
- **Resolution of Historical Erroneous Category Names:** Earlier draft notes erroneously referenced six non-existent VisA categories (`bones`, `pushpins`, `socket`, `tag`, `wallnut`, `waterbottle`). These represented conflations with MVTec LOCO AD or medical anomaly sets. They do not exist in VisA.
- **Forensic Exposure Breakdown:**
  - **`capsules` (702 images):** **DEVELOPMENT-EXPOSED (INELIGIBLE).** Extensively utilized in Google Drive experiments (`visa_development_v2`, `visa_independent_validation_v1`). 542 nominal images partitioned for fitting and calibration; 160 test images evaluated in `official_test_v1`.
  - **`candle`, `macaroni1`, `macaroni2`, `pcb1` (4,404 images):** **UNKNOWN / DISPUTED (INELIGIBLE).** Cataloged at the filesystem level in Phase 7A; cited in exploratory inspection cycle-time memos and Phase 8C notes. Because access logs cannot definitively exclude model or prompt exposure, they are disqualified from primary benchmark status.
  - **`pcb2`, `pcb3`, `pcb4`, `cashew`, `chewinggum`, `fryum`, `pipe_fryum` (5,715 images):** **POTENTIALLY UNTOUCHED.** Exhaustive search confirms zero model weights, feature arrays, or evaluation predictions exist anywhere in the repository.
- **Operational & Architectural Blockers:**
  1. *Physical Availability:* Raw image files were processed on Google Colab ephemeral disks (`/content/defectvision_external/visa_extracted/`) and were never mirrored to local workstation disks or permanent Google Drive storage (`G:\My Drive\DefectVisionAI\dataset\raw\` holds only MVTec). User instructions explicitly forbid large external downloads.
  2. *Architectural Incompatibility:* DefectVision AI’s frozen memory banks and EfficientNet-B0 v3 classifier operate strictly on the 15 MVTec classes. PatchCore requires a nominal memory bank of the target product to perform nearest-neighbor anomaly scoring. Evaluating `pcb2` or `cashew` using MVTec memory banks would yield meaningless cross-product feature divergence.
- **Eligibility Verdict:** **CONDITIONALLY ELIGIBLE (Theoretically unexposed, but physically unavailable locally and architecturally blocked without target domain calibration).**

---

### 2.3 BeanTech Anomaly Detection (BTAD)
- **Origin & Reference:** Mishra et al., "VT-ADL: A Vision-Based Industrial Anomaly Detection Dataset", IEEE Transactions on Industrial Informatics, 2021.
- **License:** Open academic research distribution.
- **Population:** 2,830 images across 3 industrial products:
  - `01` (Planar body components with surface scratches/spots): 740 images (400 train normal, 340 test).
  - `02` (Complex cylindrical metal components with shape deformations): 1,590 images (1,000 train normal, 590 test).
  - `03` (High-contrast electronic sensor surfaces): 500 images (399 train normal, 101 test).
- **Exposure History:** Zero exposure across all phases. Strictly quarantined.
- **Operational & Architectural Blockers:**
  1. *Physical Availability:* Archive unextracted and absent from local workstation and authorized Google Drive storage.
  2. *Architectural Incompatibility:* As with VisA, no nominal memory bank exists for BTAD products `01`, `02`, or `03`. Zero-shot transfer from MVTec is architecturally invalid.
- **Eligibility Verdict:** **CONDITIONALLY ELIGIBLE (Pristine, but physically unavailable and architecturally blocked).**

---

### 2.4 Chukyo Industrial Capsule Dataset
- **Origin & Reference:** Chukyo University / Industrial inspection pilot archive.
- **Population:** 1,200 capsule images (600 nominal, 600 anomalous) packaged as `chukyo_capsules.zip` (10.29 MB).
- **Physical Location:** `G:\My Drive\DefectVisionAI\experiments\external_capsule_chukyo_v1\dataset\chukyo_capsules.zip`.
- **Pre-Existing Audit Classification:** Formally classified in `external_capsule_chukyo_v1/audit/dataset_audit.json` as:
  ```json
  {
    "eligibility": "BLOCKED_INCOMPLETE_REFERENCE_AUDIT",
    "missing_reference_roots": ["MVTec_AD"],
    "commercial_rights": "UNVERIFIED",
    "status": "QUARANTINED"
  }
  ```
- **Domain Shift & Incompatibility:** Chukyo specimens represent pharmaceutical gelatin capsules with matte shell finishes and localized imprint defects. In contrast, DefectVision AI’s `capsule` memory bank was constructed on MVTec translucent two-tone nutraceutical capsules with reflective specular highlights. Silent cross-mapping without target domain calibration is strictly prohibited.
- **Eligibility Verdict:** **INELIGIBLE / QUARANTINED.**

---

## 3. Comprehensive Dataset Eligibility Matrix

| Dataset | Category / Subset | Specimen Count | Exposure Classification | Physical Disk Presence | Frozen Architecture Compatibility | Evaluation Eligibility Verdict |
|:---|:---|:---:|:---|:---:|:---:|:---:|
| **MVTec AD** | `bottle`, `capsule`, `metal_nut` | 978 | Development-Exposed | Present locally | 100% Native | **INELIGIBLE (Development-Exposed)** |
| **MVTec AD** | Remaining 12 categories | 4,376 | Application-Exposed | Present locally | 100% Native | **INELIGIBLE (Baseline-Exposed)** |
| **VisA** | `capsules` | 702 | Development-Exposed | GDrive features only | Partial (v2 model discarded) | **INELIGIBLE (Development-Exposed)** |
| **VisA** | `candle`, `macaroni1`, `macaroni2`, `pcb1` | 4,404 | Unknown / Disputed | Absent | Incompatible (no memory banks) | **INELIGIBLE (Disputed / Incompatible)** |
| **VisA** | `pcb2`, `pcb3`, `pcb4` | 3,312 | Potentially Untouched | Absent locally | Incompatible (no memory banks) | **CONDITIONALLY ELIGIBLE (Blocked)** |
| **VisA** | `cashew`, `chewinggum`, `fryum`, `pipe_fryum` | 2,403 | Potentially Untouched | Absent locally | Incompatible (no memory banks) | **CONDITIONALLY ELIGIBLE (Blocked)** |
| **BTAD** | Products `01`, `02`, `03` | 2,830 | Pristine Untouched | Absent locally | Incompatible (no memory banks) | **CONDITIONALLY ELIGIBLE (Blocked)** |
| **Chukyo** | Industrial Capsules | 1,200 | Pristine Untouched | Present (zip archive) | Incompatible (severe domain shift) | **INELIGIBLE (Audit Blocked & Quarantined)** |

---

## 4. Minimum Legitimate Steps Required for Future Independent Validation

To conduct a scientifically valid, publication-grade independent evaluation in a future phase without violating methodological integrity, the following four prerequisite steps must be executed:

1. **Formal Acquisition & Integrity Check of Pristine Target Benchmarks:**
   - Download the 7 untouched VisA categories (`pcb2-4`, `cashew`, `chewinggum`, `fryum`, `pipe_fryum`) or BTAD products `01-03` under authorized user bandwidth.
   - Verify SHA-256 archive checksums and generate a bitwise file manifest.
2. **Target-Domain Nominal Coreset Construction (Zero Contamination):**
   - For each target product, extract feature vectors exclusively from the *official nominal training partition* ($y=0$ only).
   - Perform greedy k-center coreset selection (subsampling ratio $\le 10\%$) using ResNet-18 Layer 2+3 ($D=384$).
   - Verify that zero anomalous/test specimens enter the memory bank.
3. **Pre-Registered Baseline Calibration:**
   - On a held-out nominal validation split ($N \ge 50$), establish the nominal baseline mean ($\mu_{\text{baseline}}$) and 99.5th percentile threshold ($\tau_{\text{p99}}$).
   - Lock these thresholds in a JSON manifest prior to computing inference on any test specimen.
4. **Execution of Pre-Registered Inference & Pixel Segmentation Evaluation:**
   - Execute inference across test splits using frozen weights.
   - Record specimen-level and pixel-level metrics (AUROC, AUPRO, F1, FPR, FNR, CPU latency) without post-hoc threshold adjustment.

---

## 5. Formal Certification

I hereby certify that this dataset eligibility audit adheres strictly to empirical truth, reproducible experimental governance, and anti-leakage principles. No unauthorized inference has been performed, no quarantined datasets have been breached, and no synthetic proxies have been substituted for real empirical evidence.

**Auditor Signature:** *Senior Computer Vision Research Engineer & Methodology Auditor*  
**Verification Date:** November 2, 2026  
**Status:** **INDEPENDENT EVALUATION HALTED — CRITICAL STOP RULE IN EFFECT**
