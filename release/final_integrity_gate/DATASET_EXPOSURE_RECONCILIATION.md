# DefectVision AI — Dataset Exposure Reconciliation and Forensic Independence Audit

**Document Version:** 2.0.0  
**Audit Date:** November 1, 2026  
**Auditor:** Quality & Research Integrity Gatekeeper  
**Scope:** Forensic Exposure Audit across MVTec AD, VisA (12 Subsets), BTAD, and Chukyo Benchmarks  
**Classification:** Research Governance & Public Release Integrity Audit  

---

## 1. Executive Summary & Forensic Resolution

This document formally resolves the factual contradictions in dataset exposure and quarantine accounting that arose between Phase 7A, Phase 8C, Phase 9A, and the initial open-source release documentation.

### 1.1 The Core Contradiction
Earlier documentation contained mutually incompatible statements:
1. **The "11 Pristine Categories" Claim:** Multiple governance documents (`DATASET_PROVENANCE.md`, `Q1_EXPERIMENT_PROTOCOL_V2.json`, `PROPOSED_PROTOCOL_V3_1.json`) stated that *11 VisA categories remained pristine, locked, and untouched*.
2. **The "4 Development Categories" Claim:** Release documentation (`README.md`, `DATASET_PROVENANCE.md`, `RESEARCH_HISTORY_SUMMARY.md`) stated that *4 VisA categories (`candle`, `capsule`, `macaroni`, `pcb1`) were exposed during exploratory development*.
3. **The Mathematical Impossibility:** The official Visual Anomaly (VisA) benchmark (Zou et al., ECCV 2022) contains **exactly 12 categories**. Claiming 11 untouched categories while simultaneously claiming 4 exposed categories implies $11 + 4 = 15$ categories, which is mathematically impossible for VisA.
4. **Hallucinated Category Names:** In Phase 9A, six category names (`bones`, `pushpins`, `socket`, `tag`, `wallnut`, `waterbottle`) appeared in quarantine tables. These categories **do not exist in VisA**; they were inadvertently conflated with MVTec LOCO AD or draft notes.

### 1.2 Forensic Investigation Findings
A systematic audit across local Git commit history, scripts (`scripts/check_visa_categories.py`), historical Google Drive experiment directories (`visa_external_validation_v1`, `visa_independent_validation_v1`, `visa_development_v2`), and raw prediction CSVs established the ground truth:

1. **VisA Total Population:** Exactly 12 subsets grouped into three structural families:
   - **Multi-Instance (4):** `capsules`, `candle`, `macaroni1`, `macaroni2`
   - **Printed Circuit Boards (4):** `pcb1`, `pcb2`, `pcb3`, `pcb4`
   - **Aligned Objects (4):** `cashew`, `chewinggum`, `fryum`, `pipe_fryum`
2. **Empirically Confirmed Exposed VisA Subset:** Exactly **one** category: **`capsules`**.
   - `capsules` had 542 normal training images partitioned (`v2_fit.csv`, `v2_calibration_normal.csv`, `v2_validation_normal.csv`), three PatchCore models fitted (`v2_development_freeze.json`), and 160 official test images evaluated in `official_test_v1` (AUROC 0.7210).
3. **Disputed / Exploratory VisA Subsets:** Exactly **four** categories: **`candle`**, **`macaroni1`**, **`macaroni2`**, **`pcb1`**.
   - In Phase 7A, these were cataloged at the file-system level in `visa_dataset_inventory.csv` with zero model fitting. However, later exploratory memos and Phase 8C notes cited them as inspection examples (e.g., PCB inspection cycle-time modeling). Because exploratory exposure was documented in release notes, and per-image access logs cannot be conclusively proven clean, these four subsets are designated **`UNKNOWN / DISPUTED`** and **strictly excluded from pristine independent benchmark status**.
4. **Potentially Untouched VisA Subsets:** Exactly **seven** categories: **`pcb2`**, **`pcb3`**, **`pcb4`**, **`cashew`**, **`chewinggum`**, **`fryum`**, **`pipe_fryum`**.
   - Zero model weights, zero feature embeddings, zero prediction rows, and zero exploratory text references exist anywhere in the repository or experimental records.
5. **Image Content Quarantine:** No reserved image contents (from any quarantined VisA subset, BTAD, or Chukyo) were accessed, extracted, or evaluated during Phases 7B, 7C, 8A, 8B, 8C, 9A, or release packaging.

---

## 2. Definitive Category-Level Exposure Matrix

The table below catalogs every benchmark category considered across the project lifecycle, applying strict forensic standards:

| Benchmark | Category | Total Images | Training / Fit Exposure | Calibration Exposure | Validation Exposure | Benchmark Test Exposure | Historical Exploratory Access | Evidence File / Artifact Reference | Current Independence Status |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---|:---|
| **MVTec AD** | `bottle` | 292 | Yes (209) | Yes | Yes | Yes (83) | Yes (Active) | `models/patchcore/bottle/`, `step11_uncertainty_log.csv` | **DEVELOPMENT-EXPOSED** |
| **MVTec AD** | `capsule` | 351 | Yes (219) | Yes | Yes | Yes (132) | Yes (Active) | `models/patchcore/capsule/`, `dev_extracted_scores_phase7c.csv` | **DEVELOPMENT-EXPOSED** |
| **MVTec AD** | `metal_nut` | 335 | Yes (220) | Yes | Yes | Yes (115) | Yes (Active) | `models/patchcore/metal_nut/`, `FEASIBILITY_RESULTS.csv` | **DEVELOPMENT-EXPOSED** |
| **MVTec AD** | `cable` | 374 | Yes | Yes | No | Yes | Yes (Pretrained) | `models/patchcore/cable/memory_bank.npy` | **APPLICATION-EXPOSED** |
| **MVTec AD** | `carpet` | 397 | Yes | Yes | No | Yes | Yes (Pretrained) | `models/patchcore/carpet/memory_bank.npy` | **APPLICATION-EXPOSED** |
| **MVTec AD** | `grid` | 341 | Yes | Yes | No | Yes | Yes (Pretrained) | `models/patchcore/grid/memory_bank.npy` | **APPLICATION-EXPOSED** |
| **MVTec AD** | `hazelnut` | 501 | Yes | Yes | No | Yes | Yes (Pretrained) | `models/patchcore/hazelnut/memory_bank.npy` | **APPLICATION-EXPOSED** |
| **MVTec AD** | `leather` | 346 | Yes | Yes | No | Yes | Yes (Pretrained) | `models/patchcore/leather/memory_bank.npy` | **APPLICATION-EXPOSED** |
| **MVTec AD** | `pill` | 441 | Yes | Yes | No | Yes | Yes (Pretrained) | `models/patchcore/pill/memory_bank.npy` | **APPLICATION-EXPOSED** |
| **MVTec AD** | `screw` | 480 | Yes | Yes | No | Yes | Yes (Pretrained) | `models/patchcore/screw/memory_bank.npy` | **APPLICATION-EXPOSED** |
| **MVTec AD** | `tile` | 344 | Yes | Yes | No | Yes | Yes (Pretrained) | `models/patchcore/tile/memory_bank.npy` | **APPLICATION-EXPOSED** |
| **MVTec AD** | `toothbrush` | 137 | Yes | Yes | No | Yes | Yes (Pretrained) | `models/patchcore/toothbrush/memory_bank.npy` | **APPLICATION-EXPOSED** |
| **MVTec AD** | `transistor` | 313 | Yes | Yes | No | Yes | Yes (Pretrained) | `models/patchcore/transistor/memory_bank.npy` | **APPLICATION-EXPOSED** |
| **MVTec AD** | `wood` | 326 | Yes | Yes | No | Yes | Yes (Pretrained) | `models/patchcore/wood/memory_bank.npy` | **APPLICATION-EXPOSED** |
| **MVTec AD** | `zipper` | 399 | Yes | Yes | No | Yes | Yes (Pretrained) | `models/patchcore/zipper/memory_bank.npy` | **APPLICATION-EXPOSED** |
| **VisA** | `capsules` | 702 | Yes (461) | Yes (40) | Yes (41) | Yes (160) | Yes (Extensive) | GDrive: `visa_independent_validation_v1`, `visa_development_v2` | **DEVELOPMENT-EXPOSED** |
| **VisA** | `candle` | 1,100 | None | None | None | None | Disputed | Cataloged in archive; cited in exploratory text | **UNKNOWN / DISPUTED** |
| **VisA** | `macaroni1` | 1,100 | None | None | None | None | Disputed | Cataloged in archive; cited in exploratory text | **UNKNOWN / DISPUTED** |
| **VisA** | `macaroni2` | 1,100 | None | None | None | None | Disputed | Cataloged in archive; cited in exploratory text | **UNKNOWN / DISPUTED** |
| **VisA** | `pcb1` | 1,104 | None | None | None | None | Disputed | Cataloged in archive; cited in Phase 8C cycle-time analysis | **UNKNOWN / DISPUTED** |
| **VisA** | `pcb2` | 1,101 | None | None | None | None | None | None | **POTENTIALLY UNTOUCHED** |
| **VisA** | `pcb3` | 1,106 | None | None | None | None | None | None | **POTENTIALLY UNTOUCHED** |
| **VisA** | `pcb4` | 1,105 | None | None | None | None | None | None | **POTENTIALLY UNTOUCHED** |
| **VisA** | `cashew` | 600 | None | None | None | None | None | None | **POTENTIALLY UNTOUCHED** |
| **VisA** | `chewinggum` | 603 | None | None | None | None | None | None | **POTENTIALLY UNTOUCHED** |
| **VisA** | `fryum` | 600 | None | None | None | None | None | None | **POTENTIALLY UNTOUCHED** |
| **VisA** | `pipe_fryum` | 600 | None | None | None | None | None | None | **POTENTIALLY UNTOUCHED** |
| **BTAD** | `01` | 740 | None | None | None | None | None | Archive unextracted | **PRISTINE INDEPENDENT** |
| **BTAD** | `02` | 1,590 | None | None | None | None | None | Archive unextracted | **PRISTINE INDEPENDENT** |
| **BTAD** | `03` | 500 | None | None | None | None | None | Archive unextracted | **PRISTINE INDEPENDENT** |
| **Chukyo** | Screws/Fasteners | $\approx 1,000$ | None | None | None | None | None | Separate benchmark | **PRISTINE INDEPENDENT** |

---

## 3. Forensic Classification Rules Applied

To maintain scientific integrity, the following rules govern status assignments:

1. **`DEVELOPMENT-EXPOSED`**:
   - Any category where image pixels were processed by a feature extractor, used to calibrate decision thresholds, or evaluated during model development.
   - Includes MVTec AD `bottle`, `capsule`, `metal_nut` and VisA `capsules`.
2. **`APPLICATION-EXPOSED`**:
   - Any category with a pretrained PatchCore memory bank deployed in `DefectVisionAI/models/patchcore/` to power the live web console. These categories were evaluated during initial baseline construction.
   - Includes the remaining 12 MVTec AD categories (`cable`, `carpet`, `grid`, etc.).
3. **`UNKNOWN / DISPUTED`**:
   - Any category where conflicting documentation exists regarding exploratory viewing, pilot inspection, or parameter tuning, but where concrete training logs are absent.
   - Includes VisA `candle`, `macaroni1`, `macaroni2`, and `pcb1`.
   - **Crucial Rule:** In accordance with the audit mandate, missing or conflicting evidence is **NEVER** treated as untouched. These categories are permanently barred from serving as primary benchmark controls.
4. **`POTENTIALLY UNTOUCHED`**:
   - Categories residing in extracted archives where exhaustive file searches confirm zero code references, zero feature arrays, and zero metric logs.
   - Includes VisA `pcb2`, `pcb3`, `pcb4`, `cashew`, `chewinggum`, `fryum`, and `pipe_fryum` (7 categories totaling 5,715 images).
5. **`PRISTINE INDEPENDENT`**:
   - Benchmarks that remained entirely external, unextracted, and untouched throughout the entire project lifecycle (BTAD and Chukyo).

---

## 4. Resolution of Erroneous & Conflated Category Names

Earlier drafts listed the following invalid category names under VisA quarantine tables:
- `bones`: Conflated with medical anomaly benchmarks or synthetic defect datasets. Does not exist in VisA.
- `pushpins`: Conflated with MVTec LOCO AD (`pushpins`). Does not exist in VisA.
- `socket`: Conflated with MVTec LOCO AD or industrial electrical datasets. Does not exist in VisA.
- `tag`: Conflated with exploratory packaging data. Does not exist in VisA.
- `wallnut`: Misspelling and conflation of MVTec AD `hazelnut` or external agricultural datasets. Does not exist in VisA.
- `waterbottle`: Conflated with MVTec LOCO AD `juice_bottle` or MVTec AD `bottle`. Does not exist in VisA.

**Mandate:** All references to these 6 non-existent VisA categories have been purged from project documentation and replaced with the verified 12-category VisA specification.

---

## 5. Independence Audit Conclusion

- **Total Academic Benchmarks Evaluated:** MVTec AD (15 categories fully exposed for application and development).
- **VisA Exposure Summary:**
  - 1 category exposed (`capsules`)
  - 4 categories disputed (`candle`, `macaroni1`, `macaroni2`, `pcb1`)
  - 7 categories potentially untouched (`pcb2`, `pcb3`, `pcb4`, `cashew`, `chewinggum`, `fryum`, `pipe_fryum`)
- **Pristine Independent Benchmarks Available for Future Research:** BTAD (3 categories, 2,830 images) and Chukyo ($\approx 1,000$ images).
- **Research Integrity Standard:** No claim of general external generalization across VisA may be made without a clean-slate evaluation following a pre-registered protocol on confirmed independent data.
