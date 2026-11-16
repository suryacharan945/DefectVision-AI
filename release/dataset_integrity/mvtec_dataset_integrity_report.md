# DefectVision AI — Official MVTec AD Dataset Integrity Audit Report

**Reference:** Paul Bergmann et al., 'MVTec AD — A Comprehensive Real-World Dataset for Unsupervised Anomaly Detection', CVPR 2019 / IJCV 2021.

**License:** Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0).

**Dataset Location:** `C:\Users\surya\Downloads\Mini Project\DefectVisionAI\dataset\raw\mvtec`

## 1. Summary of All 15 Categories

| Category | Type | Train (Good) | Test (Good) | Test (Defect) | Total Test | Defect Types | GT Masks | Resolution | Formats | Status |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `bottle` | object | 209 | 20 | 63 | 83 | 3 | 63 | 900x900 | PNG | **VERIFIED** |
| `cable` | object | 224 | 58 | 92 | 150 | 8 | 92 | 1024x1024 | PNG | **VERIFIED** |
| `capsule` | object | 219 | 23 | 109 | 132 | 5 | 109 | 1000x1000 | PNG | **VERIFIED** |
| `hazelnut` | object | 391 | 40 | 70 | 110 | 4 | 70 | 1024x1024 | PNG | **VERIFIED** |
| `metal_nut` | object | 220 | 22 | 93 | 115 | 4 | 93 | 700x700 | PNG | **VERIFIED** |
| `pill` | object | 267 | 26 | 141 | 167 | 7 | 141 | 800x800 | PNG | **VERIFIED** |
| `screw` | object | 320 | 41 | 119 | 160 | 5 | 119 | 1024x1024 | PNG | **VERIFIED** |
| `toothbrush` | object | 60 | 12 | 30 | 42 | 1 | 30 | 1024x1024 | PNG | **VERIFIED** |
| `transistor` | object | 213 | 60 | 40 | 100 | 4 | 40 | 1024x1024 | PNG | **VERIFIED** |
| `zipper` | object | 240 | 32 | 119 | 151 | 7 | 119 | 1024x1024 | PNG | **VERIFIED** |
| `carpet` | texture | 280 | 28 | 89 | 117 | 5 | 89 | 1024x1024 | PNG | **VERIFIED** |
| `grid` | texture | 264 | 21 | 57 | 78 | 5 | 57 | 1024x1024 | PNG | **VERIFIED** |
| `leather` | texture | 245 | 32 | 92 | 124 | 5 | 92 | 1024x1024 | PNG | **VERIFIED** |
| `tile` | texture | 230 | 33 | 84 | 117 | 5 | 84 | 840x840 | PNG | **VERIFIED** |
| `wood` | texture | 247 | 19 | 60 | 79 | 5 | 60 | 1024x1024 | PNG | **VERIFIED** |
| **TOTAL** | **15 Categories** | **3629** | **467** | **1258** | **1725** | **-** | **1258** | - | - | **100% VERIFIED** |

## 2. Benchmark Concordance Verification

- **Expected Total Train Images:** 3,629 nominal images across 15 categories.
- **Audited Total Train Images:** 3629 nominal images.
- **Expected Total Test Images:** 1,725 images (467 nominal, 1,258 defective).
- **Audited Total Test Images:** 1725 images (467 nominal, 1258 defective).
- **Expected Total Ground-Truth Masks:** Exactly equal to defective test images (1258).
- **Audited Total Ground-Truth Masks:** 1258.
- **Unreadable/Corrupted Images:** 0.
- **Missing Category Folders:** 0.

## 3. Defect-Type Breakdown per Category

### `bottle` (OBJECT)
- **Train Good:** 209
- **Test Good:** 20
- **Defect Classes (3):** broken_large, broken_small, contamination
  - `broken_large`: 20 test images
  - `broken_small`: 22 test images
  - `contamination`: 21 test images

### `cable` (OBJECT)
- **Train Good:** 224
- **Test Good:** 58
- **Defect Classes (8):** bent_wire, cable_swap, combined, cut_inner_insulation, cut_outer_insulation, missing_cable, missing_wire, poke_insulation
  - `bent_wire`: 13 test images
  - `cable_swap`: 12 test images
  - `combined`: 11 test images
  - `cut_inner_insulation`: 14 test images
  - `cut_outer_insulation`: 10 test images
  - `missing_cable`: 12 test images
  - `missing_wire`: 10 test images
  - `poke_insulation`: 10 test images

### `capsule` (OBJECT)
- **Train Good:** 219
- **Test Good:** 23
- **Defect Classes (5):** crack, faulty_imprint, poke, scratch, squeeze
  - `crack`: 23 test images
  - `faulty_imprint`: 22 test images
  - `poke`: 21 test images
  - `scratch`: 23 test images
  - `squeeze`: 20 test images

### `hazelnut` (OBJECT)
- **Train Good:** 391
- **Test Good:** 40
- **Defect Classes (4):** crack, cut, hole, print
  - `crack`: 18 test images
  - `cut`: 17 test images
  - `hole`: 18 test images
  - `print`: 17 test images

### `metal_nut` (OBJECT)
- **Train Good:** 220
- **Test Good:** 22
- **Defect Classes (4):** bent, color, flip, scratch
  - `bent`: 25 test images
  - `color`: 22 test images
  - `flip`: 23 test images
  - `scratch`: 23 test images

### `pill` (OBJECT)
- **Train Good:** 267
- **Test Good:** 26
- **Defect Classes (7):** color, combined, contamination, crack, faulty_imprint, pill_type, scratch
  - `color`: 25 test images
  - `combined`: 17 test images
  - `contamination`: 21 test images
  - `crack`: 26 test images
  - `faulty_imprint`: 19 test images
  - `pill_type`: 9 test images
  - `scratch`: 24 test images

### `screw` (OBJECT)
- **Train Good:** 320
- **Test Good:** 41
- **Defect Classes (5):** manipulated_front, scratch_head, scratch_neck, thread_side, thread_top
  - `manipulated_front`: 24 test images
  - `scratch_head`: 24 test images
  - `scratch_neck`: 25 test images
  - `thread_side`: 23 test images
  - `thread_top`: 23 test images

### `toothbrush` (OBJECT)
- **Train Good:** 60
- **Test Good:** 12
- **Defect Classes (1):** defective
  - `defective`: 30 test images

### `transistor` (OBJECT)
- **Train Good:** 213
- **Test Good:** 60
- **Defect Classes (4):** bent_lead, cut_lead, damaged_case, misplaced
  - `bent_lead`: 10 test images
  - `cut_lead`: 10 test images
  - `damaged_case`: 10 test images
  - `misplaced`: 10 test images

### `zipper` (OBJECT)
- **Train Good:** 240
- **Test Good:** 32
- **Defect Classes (7):** broken_teeth, combined, fabric_border, fabric_interior, rough, split_teeth, squeezed_teeth
  - `broken_teeth`: 19 test images
  - `combined`: 16 test images
  - `fabric_border`: 17 test images
  - `fabric_interior`: 16 test images
  - `rough`: 17 test images
  - `split_teeth`: 18 test images
  - `squeezed_teeth`: 16 test images

### `carpet` (TEXTURE)
- **Train Good:** 280
- **Test Good:** 28
- **Defect Classes (5):** color, cut, hole, metal_contamination, thread
  - `color`: 19 test images
  - `cut`: 17 test images
  - `hole`: 17 test images
  - `metal_contamination`: 17 test images
  - `thread`: 19 test images

### `grid` (TEXTURE)
- **Train Good:** 264
- **Test Good:** 21
- **Defect Classes (5):** bent, broken, glue, metal_contamination, thread
  - `bent`: 12 test images
  - `broken`: 12 test images
  - `glue`: 11 test images
  - `metal_contamination`: 11 test images
  - `thread`: 11 test images

### `leather` (TEXTURE)
- **Train Good:** 245
- **Test Good:** 32
- **Defect Classes (5):** color, cut, fold, glue, poke
  - `color`: 19 test images
  - `cut`: 19 test images
  - `fold`: 17 test images
  - `glue`: 19 test images
  - `poke`: 18 test images

### `tile` (TEXTURE)
- **Train Good:** 230
- **Test Good:** 33
- **Defect Classes (5):** crack, glue_strip, gray_stroke, oil, rough
  - `crack`: 17 test images
  - `glue_strip`: 18 test images
  - `gray_stroke`: 16 test images
  - `oil`: 18 test images
  - `rough`: 15 test images

### `wood` (TEXTURE)
- **Train Good:** 247
- **Test Good:** 19
- **Defect Classes (5):** color, combined, hole, liquid, scratch
  - `color`: 8 test images
  - `combined`: 11 test images
  - `hole`: 10 test images
  - `liquid`: 10 test images
  - `scratch`: 21 test images

