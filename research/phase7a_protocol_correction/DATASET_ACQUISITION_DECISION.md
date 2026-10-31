# Dataset Acquisition Strategy & Storage Feasibility Decision

**Document ID:** `DV-DECISION-DATASET-ACQUISITION-V1`  
**Date:** October 31, 2026  
**Auditor:** Lead AI/ML Research Engineer & Release Infrastructure Engineer  
**Scope:** Evaluation of candidate independent datasets, disk storage constraints, cloud mounting options, and data acquisition timing  

---

## 1. Executive Summary & Availability Verdict

### Core Question: Is an independent benchmark available without acquiring new data?
**Formal Finding: NO.**  
A thorough scan of both the local Windows environment (`C:\Users\surya\Downloads\Mini Project`) and the Google Drive cloud mount (`G:\My Drive\DefectVisionAI\`) reveals that:
1. **Local Disk:** Contains only MVTec AD images and local evaluation logs.
2. **Google Drive Cloud Storage:** Contains MVTec AD images, Chukyo data (quarantined), and historical metadata/feature matrices for the VisA `capsules` subset. Raw image archives for the other 11 VisA categories were previously processed in an ephemeral Google Colab `/content` session and are not permanently retained on disk.
3. **Conclusion:** To evaluate models on an unexposed, independent benchmark (the 11 untouched VisA categories and/or BTAD), image archives must be downloaded when the independent evaluation phase is initiated.

---

## 2. Candidate Independent Dataset Portfolio

| Dataset | Modality & Scope | Total Images | Image Breakdown | License & Provenance | Compressed Size | Uncompressed Size | Recommended Storage Target |
| :--- | :--- | :---: | :---: | :--- | :---: | :---: | :--- |
| **VisA (11 Untouched Subsets)** | Industrial multi-instance objects, complex textures, PCBs | 10,119 | 9,019 Normal<br>1,100 Defective | **CC BY 4.0**<br>(Amazon Science / Zou et al., ECCV 2022) | ~2.1 GB | ~4.8 GB | Ephemeral Google Colab VM (`/content/visa/`) or Google Drive |
| **BTAD (BeanTech Anomaly Detection)** | Real industrial manufacturing lines (metal/plastic components) | 2,830 | 2,540 Normal<br>290 Defective | **Academic Open Research**<br>(Mishra et al., IEEE T-II 2021) | ~520 MB | ~1.2 GB | Ephemeral Google Colab VM (`/content/btad/`) or Google Drive |
| **MPDD (Mobile Phone Defect Dataset)** | Painted metal surfaces with varying illumination & angles | 1,346 | 1,076 Normal<br>270 Defective | **CC BY-NC-SA 4.0**<br>(Jezek et al., 2021) | ~380 MB | ~950 MB | Secondary Cloud Candidate |

---

## 3. Storage Architecture & Disk Protection Policy

### Local Machine Constraint:
- The local Windows disk (`C:\`) has approximately $57.3\text{ GB}$ of free storage.
- Storing uncompressed raw images and extracted dense feature arrays for 10,000+ high-resolution images locally would consume substantial space and risk file-system thrashing.

### Mandated Cloud Architecture:
```
+---------------------------------------------------------------------------------------------------------+
|                                    GOOGLE COLAB RUNTIME (T4 GPU / CPU)                                  |
| 1. Download dataset archive directly to ephemeral VM disk: /content/visa_extracted/                     |
| 2. Run feature extraction (WideResNet-50-2) in batches using GPU acceleration.                          |
| 3. Compute 10% coreset subsampling memory banks and non-conformity calibration quantiles.              |
+---------------------------------------------------------------------------------------------------------+
                                                     |
                                                     v (Persist only lightweight artifacts)
+---------------------------------------------------------------------------------------------------------+
|                              GOOGLE DRIVE CLOUD STORAGE (G:\My Drive\DefectVisionAI)                     |
| - Store only coreset memory banks (~4.2 MB per category, ~46 MB total for 11 categories).              |
| - Store evaluation prediction CSVs, metric JSONs, and calibration logs (~15 MB).                         |
| - ZERO raw images duplicated to local Windows C: drive.                                                 |
+---------------------------------------------------------------------------------------------------------+
```

---

## 4. Dataset Acquisition Gate & Execution Sequence

In accordance with strict research integrity constraints:
- **GATE 1 (Current Status — Phase 7A):** **DATA DOWNLOAD STRICTLY BLOCKED.** No external datasets will be acquired during this audit and protocol correction phase.
- **GATE 2 (Phase 7B — Controlled Development):** Implement and evaluate the selective-review baseline suite and CPND algorithm strictly on **development data** (MVTec AD 15 categories + VisA `capsules` development partition).
- **GATE 3 (Phase 7C — Independent Evaluation Authorization):** Only after the CPND algorithm, decision thresholds, and hyperparameter combinations are frozen and verified on development data, authorize downloading the 11 unexposed VisA categories into Google Colab for a **single, blind evaluation run**.

---

## 5. Formal Acquisition Decision

1. **Immediate Action:** **NO DOWNLOADS AUTHORIZED AT THIS STAGE.**
2. **Target Primary Benchmark:** **VisA (11 Untouched Categories, 10,119 images)** provides the gold-standard cross-category industrial benchmark required for IEEE T-II / Pattern Recognition.
3. **Target Secondary Benchmark:** **BTAD (3 Categories, 2,830 images)** will serve as an independent domain-shift validation suite.
4. **Execution Medium:** Cloud-native execution on Google Colab / Google Drive, keeping the local Windows disk unencumbered.
