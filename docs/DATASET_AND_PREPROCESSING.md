# DefectVision AI — Dataset and Preprocessing Specification
**Release:** v1.0.0-rc1 (Research Prototype)  
**Date:** 2026-11-19  

---

## 1. MVTec Anomaly Detection (MVTec AD) Benchmark

DefectVision AI is benchmarked and evaluated using the MVTec AD dataset (Bergmann et al., 2019), the international reference standard for industrial visual surface inspection.

The dataset encompasses 15 distinct industrial categories categorized into two structural typologies:
- **Texture Categories (5):** `carpet`, `grid`, `leather`, `tile`, `wood`.
- **Object Categories (10):** `bottle`, `cable`, `capsule`, `hazelnut`, `metal_nut`, `pill`, `screw`, `toothbrush`, `transistor`, `zipper`.

Each category contains high-resolution defect-free training images, along with an evaluation test set featuring both nominal units and a diverse spectrum of real-world defects (e.g., scratches, dents, structural fractures, contamination, discoloration, foreign inclusions).

---

## 2. Benchmark Split Specifications

| Category | Type | Train Normal ($N_{\text{train}}$) | Test Normal ($N_{\text{test, norm}}$) | Test Defective ($N_{\text{test, def}}$) | Total Test ($N_{\text{test}}$) | Number of Defect Types |
|---|---|---:|---:|---:|---:|---:|
| **bottle** | Object | 209 | 20 | 63 | 83 | 3 (broken large/small, contamination) |
| **cable** | Object | 224 | 58 | 92 | 150 | 8 (bent wire, cable swap, cut, poke, etc.) |
| **capsule** | Object | 219 | 23 | 109 | 132 | 5 (crack, faulty imprint, scratch, squeeze) |
| **carpet** | Texture | 280 | 28 | 89 | 117 | 5 (color, cut, hole, metal contamination, thread) |
| **grid** | Texture | 264 | 21 | 57 | 78 | 5 (bent, broken, glue, metal, thread) |
| **hazelnut** | Object | 391 | 40 | 70 | 110 | 4 (crack, cut, hole, print) |
| **leather** | Texture | 245 | 32 | 92 | 124 | 5 (color, cut, fold, glue, poke) |
| **metal_nut** | Object | 220 | 22 | 93 | 115 | 4 (bent, color, flip, scratch) |
| **pill** | Object | 267 | 26 | 141 | 167 | 7 (color, crack, faulty imprint, scratch, etc.) |
| **screw** | Object | 320 | 41 | 119 | 160 | 5 (manipulated front, scratch neck/head, thread) |
| **tile** | Texture | 230 | 33 | 84 | 117 | 5 (crack, glue strip, gray stroke, oil, rough) |
| **toothbrush** | Object | 60 | 12 | 30 | 42 | 1 (defective) |
| **transistor** | Object | 213 | 60 | 40 | 100 | 4 (bent lead, cut lead, damaged case, misplaced) |
| **wood** | Texture | 247 | 19 | 60 | 79 | 5 (color, hole, liquid, scratch, stain) |
| **zipper** | Object | 240 | 32 | 119 | 151 | 7 (broken teeth, combined, fabric border, rough) |
| **Total** | — | **3,629** | **467** | **1,258** | **1,725** | **73 Defect Classes** |

---

## 3. Pill Specimen Cohort Forensic Reconciliation

During research Sprints 2.3 and 2.4, an exhaustive forensic hash verification was executed across the pill evaluation partition to verify sample counts and independence:

| Partition Cohort | Verified Physical Count | Disk Image Range | SHA-256 Independence Status |
|---|---:|---|---|
| **Training Reference Normal** | 20 images | `000.png`–`019.png` | 100% disjoint from calibration and test sets |
| **Calibration Set** | 10 images | `020.png`–`029.png` | 100% disjoint from train and test sets |
| **Test Set: Nominal (Good)** | 26 images | `000.png`–`025.png` | 100% disjoint from train and calibration |
| **Test Set: Color Defect** | 25 images | `000.png`–`024.png` | Genuine MVTec AD color defects |
| **Test Set: Crack Defect** | 26 images | `000.png`–`025.png` | Genuine MVTec AD crack defects |
| **Audited Evaluation Cohort** | **77 images** | — | Fully verified in `spatial_photometric_partition_manifest.csv` |

*Note on Historical Discrepancy:* An earlier report header erroneously stated 61 test specimens ($26 + 15 + 20$). Forensic disk auditing confirmed that all 77 images on disk were evaluated by the code.

---

## 4. Preprocessing and Tensor Transformations

Input frames (from image uploads, batch jobs, or video frames) undergo standard deterministic preprocessing:

```
[ Raw Image (BGR, arbitrary resolution) ]
                  │
                  ▼
[ Step 1: Decode & Color Conversion ] ──► cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                  │
                  ▼
[ Step 2: Quality Gate Evaluation ]  ──► Compute Laplacian variance & intensity bounds
                  │ (Passed)
                  ▼
[ Step 3: Bilinear Resizing ]        ──► cv2.resize(img, (224, 224), interpolation=INTER_LINEAR)
                  │
                  ▼
[ Step 4: Tensor Conversion ]        ──► Convert to FloatTensor in [0.0, 1.0] range
                  │
                  ▼
[ Step 5: ImageNet Normalization ]   ──► Mean: [0.485, 0.456, 0.406]
                                          Std:  [0.229, 0.224, 0.225]
                  │
                  ▼
[ Output Tensor (1, 3, 224, 224) ]
```
