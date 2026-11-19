# DEFECTVISION AI 2.1 — EXPERIMENTAL DATASET INTEGRITY & PARTITION AUDIT

**Audit Date**: 2026-11-19T01:10:00+05:30  
**Artifact**: [`release/experiments/dataset_manifest.json`](file:///c:/Users/surya/Downloads/Mini%20Project/release/experiments/dataset_manifest.json)  
**Total Catalogued Records**: 218  
**Unique SHA-256 Hashes**: 218 (Zero hash collisions)  

---

## 1. Explicit Partition Distribution

Every catalogued specimen is strictly assigned to one of four mutually exclusive experimental partitions:

| Partition | Specimen Count | Primary Role & Leakage Boundary Rules |
| :--- | :---: | :--- |
| **`MEMORY_BANK_TRAIN`** | 55 | Used strictly to extract patch features for PatchCore memory banks. **Never evaluated for performance metrics.** |
| **`NORMAL_CALIBRATION`** | 7 | Independent nominal specimens evaluated strictly to select decision thresholds ($	au$). **Completely excluded from memory banks.** |
| **`VALIDATION`** | 13 | Hyperparameter tuning, coreset ratio tuning, and intermediate sanity checks. |
| **`FINAL_TEST`** | 143 | **Frozen held-out evaluation benchmark.** No specimen in this partition was ever used to train a memory bank or calibrate a threshold. |

---

## 2. Physical vs. Synthetic Specimen Integrity

```
Total Specimens: 218
├── Genuine Physical Specimens: 170 (78.0%)
│   ├── MVTec AD Benchmark laboratory captures (Domain A)
│   └── External studio and defective photographs (Domain B)
└── Synthetic Jitter Captures: 48 (22.0%)
    └── Station 01 simulated rig (Domain D)
        ├── Nominal Jitter: Derived from 1 single physical nominal bottle
        └── Defect Jitter: Derived from 1 single physical broken bottle
```

> [!CRITICAL]
> **Scientific Finding on Domain D Jitter Data**:
> All 48 images in `data/station_01/` originate from **only two underlying physical bottles** (1 nominal, 1 defective) augmented via OpenCV affine transforms, lighting scale, and Gaussian noise.
> While synthetic jitter models camera mount vibration and backlight fluctuation, **it does not constitute an independent multi-sample industrial population**. Metrics evaluated on Domain D reflect jitter invariance, not broad product defect diversity.

---

## 3. Specimen Grouping & Train-Test Leakage Mitigation

To eliminate correlated leakage, specimens sharing a common physical acquisition sequence are grouped:

| Specimen Group | Physical Origin | Assigned Partitions | Leakage Safeguard |
| :--- | :--- | :--- | :--- |
| `PHYS_SPECIMEN_EXT_BTL_A` | External Clear Bottle Photo 1 | `MEMORY_BANK_TRAIN` | Excluded from `FINAL_TEST`. |
| `PHYS_SPECIMEN_EXT_BTL_B` | External Clear Bottle Photo 2 | `MEMORY_BANK_TRAIN` | Excluded from `FINAL_TEST`. |
| `PHYS_SPECIMEN_EXT_BTL_BROKEN` | External Broken Bottle Specimen | `FINAL_TEST` | **Never seen in training.** |
| `PHYS_SOURCE_MVTEC_BOTTLE_NOMINAL_JITTER` | Station 01 Jitter Generator (Nominal) | `MEMORY_BANK_TRAIN` (000-019), `NORMAL_CALIBRATION` (003-004, val 000-004), `FINAL_TEST` (val 010-014) | **Strict Index Separation**: Only held-out validation indices 010-014 permitted in `FINAL_TEST`. |
| `PHYS_SOURCE_MVTEC_BOTTLE_DEFECT_JITTER` | Station 01 Jitter Generator (Defect) | `VALIDATION` (000-002), `FINAL_TEST` (004-007) | Training never observes defective frames. |

---

## 4. Domain Breakdown

| Domain | Catalogued Samples | Acquisition Protocol |
| :--- | :---: | :--- |
| **Domain A: MVTec AD Benchmark** | 167 | High-resolution laboratory controlled lighting and positioning across 7 categories. |
| **Domain B: Controlled External Photos** | 3 | High-resolution studio lightbox photography of external product SKUs. |
| **Domain D: Factory-Style Stationary** | 48 | Automated camera mount simulation with mechanical jitter and thermal noise. |

This manifest is frozen under version control as the authoritative basis for all Phase 4 benchmarking.
