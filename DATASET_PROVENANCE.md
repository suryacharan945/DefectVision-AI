# DefectVision AI — Dataset Provenance and Exposure Manifest

**Document Version:** 1.0.0  
**Status:** COMPLETE & VERIFIED  
**Scope:** Dataset Accounting, Exposure History, and Benchmark Quarantine  

---

## 1. Executive Statement of Provenance

To guarantee complete scientific integrity and prevent data contamination, this document defines the exact boundaries between datasets utilized for exploratory development and datasets held in pristine quarantine for future independent benchmarking.

**Core Principles:**
1. **No Data Leakage:** Development prototypes and calibration models were fitted strictly on authorized development categories.
2. **Quarantine Preserved:** The 11 unexposed VisA categories, the BTAD dataset, and the Chukyo dataset were **never accessed or evaluated** during the research audits.
3. **Reproducible Provenance:** All datasets derive from standard, publicly available academic benchmarks.

---

## 2. Dataset Exposure Inventory

### 2.1 Exposed Development Pool (Authorized for Prototyping)
These categories were accessed during model development, threshold tuning, and exploratory experiments in Google Colab and local testing:

| Dataset | Category | Split Composition | Image Count | Exposure History |
|:---|:---|:---|:---:|:---|
| **MVTec AD** | `bottle` | Train Normal (209), Test Normal (20), Test Defect (63) | 292 | Exposed during initial training; used for UI presets, latency benchmarking, and smoke testing. |
| **MVTec AD** | `capsule` | Train Normal (219), Test Normal (23), Test Defect (109) | 351 | Exposed during initial PatchCore fitting; used for Phase 7C and Phase 8B calibration sweeps. |
| **MVTec AD** | `metal_nut` | Train Normal (220), Test Normal (22), Test Defect (93) | 335 | Exposed during initial PatchCore fitting; used for Phase 7C and Phase 8B calibration sweeps. |
| **VisA** | `candle` | Official train normal and test splits | $\approx 1,000$ | Exposed during early exploratory multi-category runs. |
| **VisA** | `capsule` | Official train normal and test splits | $\approx 700$ | Exposed during early exploratory multi-category runs. |
| **VisA** | `macaroni` | Official train normal and test splits | $\approx 1,000$ | Exposed during early exploratory multi-category runs. |
| **VisA** | `pcb1` | Official train normal and test splits | $\approx 1,200$ | Exposed during early exploratory multi-category runs. |

### 2.2 Quarantined Independent Evaluation Pool (Strictly Unaccessed)
These datasets and categories were strictly quarantined during Phase 7A and have **never been accessed, read, or evaluated** in any phase of this project:

| Benchmark | Quarantined Categories | Estimated Images | Status | Quarantine Condition |
|:---|:---|:---:|:---:|:---|
| **VisA** (Zou et al., 2022) | 11 categories: `bones`, `cashew`, `chewinggum`, `fryum`, `pipefryum`, `pushpins`, `screw`, `socket`, `tag`, `wallnut`, `waterbottle` | $\approx 8,500$ | **PRISTINE** | Completely unaccessed. No feature extraction, no threshold tuning, no test inference. |
| **BTAD** (Mishra et al., 2021) | 3 industrial categories: `01`, `02`, `03` (wood, metal, plastic components) | $2,830$ | **PRISTINE** | Completely unaccessed. |
| **Chukyo** Benchmark | Industrial screw and fastener surface defects | $\approx 1,000$ | **PRISTINE** | Completely unaccessed. |

---

## 3. Disjoint Partitioning Protocol for Development Experiments

For all reported Phase 7C, 8B, and 8C experiments, the 330 development images were partitioned using a group-aware stratified split:

```
Total Development Pool: 330 specimens (bottle, capsule, metal_nut)
                       |
       +---------------+---------------+
       |                               |
       v                               v
[ Calibration Split (50%) ]    [ Internal Evaluation Split (50%) ]
  N = 156 images                 N = 174 images
  27 Errors (27 FN, 0 FP)        35 Errors (32 FN, 3 FP)
       |                               |
       v                               v
- Fit decision thresholds        - Measure policy cost reduction
- Fit Platt logistic calibrators - Evaluate false negative capture
- Zero holdout labels seen!      - Compute realized loss curves
```

### Protocol Validation:
- Stratification key: `category_defecttype_iserror` ensuring balanced defect representation across splits.
- Random Seed: Fixed at `SEED = 42` for exact reproducibility.
- Cryptographic hash of development score extraction:
  `DefectVisionAI/research/cpnd/dev_extracted_scores_phase7c.csv` (SHA-256 verified).

---

## 4. Licenses and Third-Party Rights

1. **MVTec Anomaly Detection (MVTec AD):**
   - Released by MVTec Software GmbH for non-commercial research and academic evaluation.
   - Reference: Bergmann et al., CVPR 2019 / IJCV 2021.
2. **VisA (Visual Anomaly):**
   - Released by Zou et al., ECCV 2022 under CC BY 4.0 license.
3. **BTAD (BeanTech Anomaly Detection):**
   - Released by Mishra et al., IEEE Access 2021 under academic research permissions.
