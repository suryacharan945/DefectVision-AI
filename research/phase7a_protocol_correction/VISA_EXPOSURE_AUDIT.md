# Forensic Exposure Audit: Visual Anomaly (VisA) Dataset

**Document ID:** `DV-AUDIT-VISA-EXPOSURE-V1`  
**Audit Date:** October 31, 2026  
**Auditor:** Lead AI/ML Research Engineer & Experimental Methodology Reviewer  
**Scope:** Re-evaluation of VisA dataset exposure across local repository and Google Drive cloud storage  

---

## 1. Executive Summary & Audit Correction

In prior documentation (`INDEPENDENT_DATA_INVENTORY.md` and `Q1_EXPERIMENT_PROTOCOL_V1.json`), the Visual Anomaly (VisA) dataset (10,821 images across 12 categories) was incorrectly designated as 100% untouched.

A systematic forensic examination of the associated Google Drive cloud storage repository (`G:\My Drive\DefectVisionAI\experiments`, corresponding to `/content/drive/MyDrive/DefectVisionAI/experiments` in the Google Colab environment) reveals that **earlier experiments extensively developed, calibrated, and evaluated models on the VisA `capsules` category.**

### Formal Audit Correction:
1. **VisA `capsules` is strictly DEVELOPMENT-EXPOSED.** It cannot be utilized as an untouched, independent benchmark in any Q1 journal submission.
2. **The remaining 11 VisA categories (10,119 images) are UNTOUCHED / POTENTIALLY INDEPENDENT.** They were previously inventoried at the archive metadata level during dataset extraction, but have never been subjected to feature extraction, memory bank fitting, decision threshold calibration, or model evaluation.

---

## 2. Forensic Investigation of Google Drive Artifacts

Direct inspection of `G:\My Drive\DefectVisionAI\experiments` uncovered three historical experiment directories:
1. `G:\My Drive\DefectVisionAI\experiments\visa_external_validation_v1`
2. `G:\My Drive\DefectVisionAI\experiments\visa_independent_validation_v1`
3. `G:\My Drive\DefectVisionAI\experiments\visa_development_v2`

### 2.1. Dataset Ingestion & Initial Inventory (`visa_external_validation_v1`)
- **Source Archive:** `/content/defectvision_external/VisA_20220922.tar`
- **Extraction Target:** `/content/defectvision_external/visa_extracted`
- **Recorded Inventory:** `visa_dataset_inventory.csv` cataloged all 12 categories (9,621 normal images, 1,200 anomaly images, 1,200 ground truth masks).
- **Exposure Level:** Pure metadata file-system audit; zero image pixels were passed into neural network backbones.

### 2.2. V1 Official Test Exposure (`visa_independent_validation_v1`)
- **Protocol:** `capsules_protocol.json` (Seed: 42, Split: official `1cls.csv`).
- **Nominal Training Split:** 542 total normal images partitioned into:
  - `fit_images`: 461 images (`capsules_fit.csv`, SHA-256: `e02442ca2359d9a5b8cc169b921a1413bcbfdb0c069945ace15c1c134e9053f8`).
  - `calibration_images`: 81 images (`capsules_calibration.csv`, SHA-256: `5beb523a603933ad688aed189fd1f8d5329da4146c269c5695d8e96e69b9ad18`).
- **Official Test Set Evaluated:** 160 images (60 normal, 100 anomaly; SHA-256: `0504c421af55d33c3fa7da1d29d9f642bb1ad00e31bca155da7a8e5e5295db80`).
- **Evaluation Executed (`official_test_v1`):**
  - Model 1 (`visa_capsules_224_random_max`): AUROC $0.7210$, Recall $0.3700$ (37 TP, 63 FN, 56 TN, 4 FP).
  - Model 2 (`visa_capsules_320_random_p99`): AUROC $0.6883$, Recall $0.3700$ (37 TP, 63 FN, 59 TN, 1 FP).
- **Audit Verdict:** The official test split of VisA `capsules` was **fully evaluated**.

### 2.3. V2 Development & Model Freeze (`visa_development_v2`)
- **Protocol:** `v2_protocol.json` (Seed: 2027, Category: `capsules`).
- **Repartitioning of Normal Split:** The 542 normal training images were repartitioned into:
  - `v2_fit.csv`: 461 images (used for feature extraction; feature matrix `fit_features_224.npy`, 555 MB).
  - `v2_calibration_normal.csv`: 40 images (empirical 95th percentile threshold calibration).
  - `v2_validation_normal.csv`: 41 images (false positive rate validation).
- **Candidates Fitted:**
  - Candidate A: `v2_a_224_random_max` (Threshold: $2.3988$).
  - Candidate B: `v2_b_224_coreset_max` (Threshold: $2.3636$).
  - Candidate C: `v2_c_224_random_p99`.
- **Frozen Anchor:** `v2_development_freeze.json` (SHA-256: `e7b5b5e9f6d1b23759d9918d23db8699d8a09ec1e3822468d2c9346a250216bc`).
- **Audit Verdict:** VisA `capsules` underwent multi-round model selection, memory-bank subsampling, threshold calibration, and validation analysis.

---

## 3. Category-by-Category VisA Exposure Matrix

The full Visual Anomaly (VisA) dataset comprises 10,821 images across 12 distinct categories. Below is the audited exposure classification for each category:

| Category | Normal Images | Anomaly Images | Total Images | Exposure Classification | Detailed Forensic Evidence | Eligible for Final Q1 Test? |
| :--- | :---: | :---: | :---: | :--- | :--- | :---: |
| **capsules** | 602 | 100 | 702 | **DEVELOPMENT-EXPOSED** | • 461 images used for training fit (`v2_fit.csv`)<br>• 40 images used for calibration (`v2_calibration_normal.csv`)<br>• 41 images used for normal validation (`v2_validation_normal.csv`)<br>• 160 test images evaluated in `official_test_v1`<br>• 3 PatchCore candidates fitted and frozen (`v2_development_freeze.json`) | **NO** (Strictly excluded from final independent evaluation; eligible for development ablations only) |
| **candle** | 1,000 | 100 | 1,100 | **POTENTIALLY INDEPENDENT** | Cataloged in archive extraction inventory only. Zero model fitting, feature extraction, calibration, or evaluation. | **YES** |
| **cashew** | 500 | 100 | 600 | **POTENTIALLY INDEPENDENT** | Cataloged in archive extraction inventory only. Zero model fitting, feature extraction, calibration, or evaluation. | **YES** |
| **chewinggum** | 503 | 100 | 603 | **POTENTIALLY INDEPENDENT** | Cataloged in archive extraction inventory only. Zero model fitting, feature extraction, calibration, or evaluation. | **YES** |
| **fryum** | 500 | 100 | 600 | **POTENTIALLY INDEPENDENT** | Cataloged in archive extraction inventory only. Zero model fitting, feature extraction, calibration, or evaluation. | **YES** |
| **macaroni1** | 1,000 | 100 | 1,100 | **POTENTIALLY INDEPENDENT** | Cataloged in archive extraction inventory only. Zero model fitting, feature extraction, calibration, or evaluation. | **YES** |
| **macaroni2** | 1,000 | 100 | 1,100 | **POTENTIALLY INDEPENDENT** | Cataloged in archive extraction inventory only. Zero model fitting, feature extraction, calibration, or evaluation. | **YES** |
| **pcb1** | 1,004 | 100 | 1,104 | **POTENTIALLY INDEPENDENT** | Cataloged in archive extraction inventory only. Zero model fitting, feature extraction, calibration, or evaluation. | **YES** |
| **pcb2** | 1,001 | 100 | 1,101 | **POTENTIALLY INDEPENDENT** | Cataloged in archive extraction inventory only. Zero model fitting, feature extraction, calibration, or evaluation. | **YES** |
| **pcb3** | 1,006 | 100 | 1,106 | **POTENTIALLY INDEPENDENT** | Cataloged in archive extraction inventory only. Zero model fitting, feature extraction, calibration, or evaluation. | **YES** |
| **pcb4** | 1,005 | 100 | 1,105 | **POTENTIALLY INDEPENDENT** | Cataloged in archive extraction inventory only. Zero model fitting, feature extraction, calibration, or evaluation. | **YES** |
| **pipe_fryum** | 500 | 100 | 600 | **POTENTIALLY INDEPENDENT** | Cataloged in archive extraction inventory only. Zero model fitting, feature extraction, calibration, or evaluation. | **YES** |
| **Total Untouched** | **9,019** | **1,100** | **10,119** | **UNTOUCHED BENCHMARK** | **11 Categories completely unexposed to any model parameters or evaluations.** | **YES** |

---

## 4. Formal Categorization Definitions Applied

In compliance with experimental methodology requirements:
- **Training-Exposed:** Images directly used to extract patch feature vectors and construct PatchCore memory banks (461 normal capsule images).
- **Calibration-Exposed:** Images used to compute non-conformity quantiles or score percentiles (40 normal capsule images in v2; 81 in v1).
- **Validation-Exposed:** Images used to select model architectures, aggregation rules, or coreset subsampling strategies (41 normal capsule images in v2).
- **Official-Test-Exposed:** Images evaluated in `official_test_predictions.csv` and summarized in `official_test_summary.json` (160 capsule images: 60 normal, 100 anomaly).
- **Previously Inspected:** Data where individual specimen images or heatmaps were manually viewed to guide development hypotheses (capsule failure diagnoses).
- **Unverified Exposure:** None identified.
- **Potentially Independent:** Data residing in external archives that has never been processed by any feature extractor or inference script (10,119 images across 11 VisA categories).

---

## 5. Corrective Action Mandate for Protocol V2

1. **Protocol Amendment:** The pre-registered protocol must be amended to remove any claim that VisA is completely unexposed.
2. **Category Segregation:**
   - VisA `capsules` is assigned to the **Development & Ablation Suite** alongside MVTec AD.
   - The remaining **11 VisA categories (10,119 images)** are formally quarantined as the **Held-Out External Generalization Benchmark**.
3. **Execution Gate:** No feature extraction or inference may be performed on the 11 held-out categories until the final algorithm, hyperparameters, and decision rules are frozen.
