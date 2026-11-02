# DefectVision AI — Phase 47: Independent Data Access and Provenance Plan

**Document Type:** Data Acquisition, Storage Architecture, and Partition Integrity Plan  
**Phase:** Phase 47 — Three-Hour Research Feasibility Sprint  
**Target Category:** Visual Anomaly (VisA) Benchmark — `cashew`  
**Date:** November 2, 2026  
**Git Baseline Commit:** `20ec56e`  
**Status:** **LOCKED SPECIFICATION — PENDING USER ACQUISITION AUTHORIZATION**  

---

## 1. Candidate Dataset Provenance & Licensing

The selected evaluation cohort is the **`cashew`** subset of the official Visual Anomaly (VisA) dataset:

- **Benchmark Citation:** Zou et al., *"Spot-the-Difference: An Anomaly Detection Benchmark for Spotting Component and Surface Defects"*, European Conference on Computer Vision (ECCV), 2022.
- **Official Repository:** `https://github.com/amazon-science/spot-the-difference`
- **License Terms:** Creative Commons Attribution 4.0 International (CC BY 4.0).
  - Open academic and commercial use permitted.
  - Non-restrictive redistribution rights with attribution.
- **Specimen Population:** Exactly **600 images**:
  - Nominal (Conforming) Specimens: $500\text{ images}$ ($y=0$).
  - Defective (Anomalous) Specimens: $100\text{ images}$ ($y=1$).
- **Defect Taxonomy:** Structural cracks, surface burns, fungal mold, mechanical chips, and severe surface abrasions.
- **Ground-Truth Annotations:** Full-resolution binary pixel-level segmentation masks for all 100 defective images.

---

## 2. Storage Architecture & Cloud-Staging Strategy

To preserve local disk space on `C:\Users\surya\` (where available space is constrained), all raw image assets will be stored in Google Drive cloud storage:

- **Primary Cloud Storage Target:**  
  `G:\My Drive\DefectVisionAI\dataset\raw\visa\cashew\`
- **Expected Bandwidth & Storage Footprint:**
  - Compressed Category Archive (`cashew.tar.gz`): $\approx 230\text{ MB}$.
  - Extracted Directory Footprint: $\approx 310\text{ MB}$ (600 color JPEG/PNG images at standard resolution).
  - Local Workstation Disk Impact: $\mathbf{0\text{ MB}}$ permanent disk usage on drive `C:`. Features and memory bank ($\approx 25\text{ MB}$) reside in workspace directory `models/patchcore/visa_cashew/`.

---

## 3. Cryptographic Partitioning & Anti-Contamination Design

To guarantee zero leakage and prevent duplicate or capture-correlated specimens from crossing experimental boundaries, the 600 specimens are partitioned deterministically into three strictly disjoint sets:

```
================================================================================
                    VISA CASHEW PARTITION ARCHITECTURE
================================================================================

Total Specimen Population: 600 Images (500 Normal, 100 Defect)

[1] REGISTRATION COHORT (Nominal Only, y=0)
    - Specimen Count: 350 Normal Images
    - Role: Feature extraction & 10% greedy k-center memory bank construction
    - Contamination Guard: Zero defect specimens; zero test images

[2] CALIBRATION COHORT (Nominal Only, y=0)
    - Specimen Count: 50 Held-Out Normal Images
    - Role: Compute 99.5th percentile baseline (tau_p99) and mean baseline
    - Contamination Guard: Zero defect specimens; strictly isolated from test

[3] UNTOUCHED INDEPENDENT TEST COHORT (Balanced Evaluation, y in {0, 1})
    - Specimen Count: 200 Images (100 Normal, 100 Defective)
    - Defect Prevalence: Exactly 50.0% (Balanced 1:1 distribution)
    - Role: Blinded, frozen-weight inference and metric computation
    - Contamination Guard: Never accessed during memory bank or threshold setup

================================================================================
```

### 3.1 Partition Allocation Integrity
- **Registration Partition ($N_{\text{reg}} = 350$, $y=0$):**  
  Used solely to populate the patch representation space and construct $\mathcal{M}_{\text{cashew}}$.
- **Calibration Partition ($N_{\text{cal}} = 50$, $y=0$):**  
  Held-out nominal cohort providing the empirical null distribution to lock decision boundary $\tau_{\text{p99}}$ and $\mu_{\text{baseline}}$ in `cashew_baselines.json`.
- **Untouched Test Partition ($N_{\text{test}} = 200$, $100\text{ nominal} + 100\text{ defective}$):**  
  Completely unblinded only after the memory bank and decision threshold are permanently committed to disk.

---

## 4. Execution Workflow & Stop-Gate Controls

1. **Pre-Flight Manifest Generation:** Prior to feature extraction, an immutable partition manifest (`visa_cashew_split_manifest.json`) will be generated, recording the absolute path, relative path, SHA-256 hash, and partition assignment for each of the 600 images.
2. **Current Gate Status:** **NO DATA DOWNLOAD HAS BEEN PERFORMED.** In strict compliance with Phase 47 constraints, downloading and extraction are deferred until the user explicitly approves this feasibility plan.
