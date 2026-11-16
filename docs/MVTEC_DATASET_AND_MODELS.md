# MVTec AD Dataset, Model Architectures, and Retrieval Guide

## 1. MVTec Anomaly Detection (AD) Benchmark

The MVTec Anomaly Detection dataset (Bergmann et al., 2019/2021) is the standard benchmark for industrial optical inspection. It contains 5,354 high-resolution color images divided across 15 industrial domains:

### Ten Object Categories
1. **`bottle`** (Glass beverage bottles; broken small/large, contamination)
2. **`cable`** (Multi-core colored cables; bent wire, missing cable, cut wire)
3. **`capsule`** (Pharmaceutical capsules; crack, poke, squeeze, scratch)
4. **`hazelnut`** (Organic hazelnuts; crack, cut, hole, print)
5. **`metal_nut`** (Threaded metal hex nuts; bent, color, flip, scratch)
6. **`pill`** (Coated pills; color, contamination, crack, faulty imprint)
7. **`screw`** (Threaded fasteners; manipulated front, scratch head, thread side)
8. **`toothbrush`** (Molded toothbrushes; defective bristle patterns)
9. **`transistor`** (TO-92 electronic transistors; bent lead, cut lead, damaged case)
10. **`zipper`** (Interlocking slide fasteners; broken teeth, fabric split, rough)

### Five Texture Categories
11. **`carpet`** (Woven textiles; color, cut, hole, metal contamination, thread)
12. **`grid`** (Wire mesh; bent wire, broken wire, glue, metal contamination)
13. **`leather`** (Surface leather; color, cut, fold, glue, poke)
14. **`tile`** (Ceramic tiles; crack, glue strip, gray stroke, oil, rough)
15. **`wood`** (Hardwood grain; color, combined, hole, liquid, scratch)

---

## 2. Rigorous Dataset Partitioning & Disjoint Splitting

To ensure scientific integrity and eliminate all data leakage, the repository uses deterministic split manifests located in `release/dataset_manifests/`:

```
+--------------------------------------------------------------------------------+
|                         FULL MVTEC AD CORPUS (5,354 IMAGES)                    |
+--------------------------------------------------------------------------------+
                                       |
          +----------------------------+-----------------------------+
          |                                                          |
  [ NOMINAL TRAIN POOL ]                                   [ OFFICIAL TEST POOL ]
       (3,629 IMAGES)                                          (1,725 IMAGES)
          |                                                          |
    +-----+-----+                                            +-------+-------+
    |           |                                            |               |
[ REGISTRATION ] [ CALIBRATION ]                        [ NOMINAL TEST ] [ DEFECT TEST ]
 (2,903 IMAGES)    (726 IMAGES)                           (467 IMAGES)    (1,258 IMAGES)
    80% Split        20% Split                             Pure Normal     Real Anomalies
```

1. **PatchCore Memory Bank Registration Split (2,903 images):**
   Nominal training images used exclusively to populate PatchCore nearest-neighbor memory banks and fit the EfficientNet-B0 category classifier feature head.
2. **Disjoint Calibration & Validation Split (726 images):**
   A strictly separated 20% validation split of nominal images used exclusively to calibrate decision thresholds ($T_{cal}$) and determine softmax temperature scaling ($T = 1.3696$).
3. **Quarantined Official Test Split (1,725 images):**
   Consists of 467 nominal images and 1,258 defective specimens with pixel-level ground truth masks. These images were completely untouched during training and threshold calibration.

---

## 3. Model Artefact Policy & File Inventory

All model artefacts required for application inference are managed to maintain high reproducibility while respecting Git storage limits:

| Artefact Path | Size | Storage Strategy | Purpose |
| :--- | :---: | :---: | :--- |
| `DefectVisionAI/models/category_classifier/category_classifier.pth` | 17.65 MB | Git Tracked | EfficientNet-B0 15-class classification head weights. |
| `DefectVisionAI/models/category_classifier/category_metadata.json` | 2.1 KB | Git Tracked | Class IDs, temperature scale ($T=1.3696$), and threshold (0.70). |
| `DefectVisionAI/models/patchcore/category_thresholds.json` | 3.6 KB | Git Tracked | Category-specific calibrated decision thresholds and borderline bands. |
| `DefectVisionAI/models/patchcore/<category>/memory_bank.npy` | 6.5 MB – 42.2 MB | Git Tracked | Coreset-subsampled memory banks for all 15 categories. |
| `DefectVisionAI/models/faiss_index/<category>/` | ~1.5 MB each | Git Tracked | FAISS FlatL2 nearest-neighbor indices for top-$k$ nominal retrieval. |

*Note on Git Storage:*
All model files in this repository are under 50 MB, well within GitHub's standard per-file limit (100 MB). Git LFS is supported but not strictly required for standard cloning.

---

## 4. How to Reproduce Models from Scratch

If you wish to retrain the models or regenerate the memory banks, the following scripts provide end-to-end reproducibility:

### Step 1: Download MVTec AD Dataset
Download the official MVTec AD dataset archives from the official MVTec portal:
```powershell
# Unpack into DefectVisionAI/dataset/raw/mvtec/
# Structure:
#   DefectVisionAI/dataset/raw/mvtec/<category>/train/good/*.png
#   DefectVisionAI/dataset/raw/mvtec/<category>/test/<defect_type>/*.png
#   DefectVisionAI/dataset/raw/mvtec/<category>/ground_truth/<defect_type>/*_mask.png
```

### Step 2: Generate Disjoint Dataset Manifests
```powershell
.\.venv\Scripts\python.exe scripts/generate_mvtec_splits.py
```
Outputs deterministic split CSVs in `release/dataset_manifests/`.

### Step 3: Train the EfficientNet-B0 Category Classifier
```powershell
.\.venv\Scripts\python.exe scripts/train_category_classifier_fast.py
```
Extracts backbone features, trains the classification head with temperature calibration in under 20 seconds, and saves:
- `DefectVisionAI/models/category_classifier/category_classifier.pth`
- `DefectVisionAI/models/category_classifier/category_metadata.json`

### Step 4: Calibrate Category Thresholds
```powershell
.\.venv\Scripts\python.exe scripts/calibrate_patchcore_thresholds.py
```
Computes empirical 99.5th percentile nominal thresholds on the disjoint calibration split (726 images) and writes:
- `DefectVisionAI/models/patchcore/category_thresholds.json`

### Step 5: Run Full Benchmark Evaluations
```powershell
# Evaluate category classifier across validation, test, and OOD sets:
.\.venv\Scripts\python.exe scripts/evaluate_category_classifier.py

# Evaluate PatchCore across all 1,725 official test images:
.\.venv\Scripts\python.exe scripts/evaluate_patchcore_all_categories.py
```

---

## 5. Licensing & Attribution Notice

- **MVTec AD Dataset:** Copyright © MVTec Software GmbH. Distributed under the **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)** license.
- **Academic Research Prototype:** The pretrained feature representations derived from MVTec AD are strictly intended for non-commercial academic research and benchmarking. Commercial production deployments require training memory banks on proprietary industrial imagery.
