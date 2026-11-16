# DefectVision AI — Phase 47: Resource, Compute, and Storage Budget

**Document Type:** Computational Resource Allocation & Execution Time Budget  
**Phase:** Phase 47 — Three-Hour Research Feasibility Sprint  
**Target Category:** Visual Anomaly (VisA) Benchmark — `cashew`  
**Date:** November 2, 2026  
**Git Baseline Commit:** `20ec56e`  
**Author:** Industrial AI Systems Engineer & Performance Auditor  

---

## 1. Executive Resource Summary

The proposed independent validation experiment on VisA `cashew` has been engineered to minimize compute, storage, and network bandwidth while satisfying peer-reviewed experimental rigor.

```
+------------------------------------+--------------------------+-------------------------------------------------------+
| Resource Category                  | Estimated Requirement    | Allocation Strategy & Location                        |
+------------------------------------+--------------------------+-------------------------------------------------------+
| Network Transfer (Download)        | ~230 MB                  | Single category archive from official VisA repository |
| Cloud Storage (Google Drive)       | ~310 MB                  | G:\My Drive\DefectVisionAI\dataset\raw\visa\cashew\   |
| Local Disk Consumption (C: Drive)  | ~86 MB                   | models/patchcore/visa_cashew/ (Memory bank + Index)   |
| Peak Host RAM                      | < 2.0 GB                 | Process memory during FAISS k-center subsampling      |
| Specialized Accelerators (GPU/TPU) | NONE (0 GPU hours)       | 100% CPU-compatible execution                         |
| Google Colab Dependency            | UNNECESSARY              | Fully executable on local Windows workstation         |
| Active Compute Execution Time      | ~3.1 minutes             | Local CPU processing (PyTorch + FAISS)                |
| Total End-to-End Elapsed Time      | ~6 to 8 minutes          | Download, coresetting, inference, and reporting       |
+------------------------------------+--------------------------+-------------------------------------------------------+
```

---

## 2. Detailed Storage Footprint Breakdown

### 2.1 Cloud Staging (Google Drive)
To avoid depleting limited local workstation disk space on `C:\Users\surya\`, raw dataset images will be uncompressed directly into the persistent cloud folder:
- Path: `G:\My Drive\DefectVisionAI\dataset\raw\visa\cashew\`
- 500 Nominal Images ($y=0$): $\approx 255\text{ MB}$
- 100 Defective Images ($y=1$): $\approx 51\text{ MB}$
- 100 Ground-Truth Polygon Masks: $\approx 4\text{ MB}$
- Total Google Drive Allocation: **$\approx 310\text{ MB}$**

### 2.2 Local Repository Disk Impact (`C:\Users\surya\Downloads\Mini Project`)
Only the mathematical model representations and tabular results will be saved locally:
- `models/patchcore/visa_cashew/memory_bank.npy`: $27,440 \times 384 \times 4\text{ bytes} \approx 42.1\text{ MB}$
- `models/patchcore/visa_cashew/index.faiss`: $\approx 42.2\text{ MB}$
- `models/patchcore/visa_cashew/cashew_baselines.json`: $< 1\text{ KB}$
- `release/phase47_results/prediction_records.csv`: $\approx 45\text{ KB}$
- Total Local Disk Footprint: **$\approx 84.4\text{ MB}$**

---

## 3. Computational and Time Budget Breakdown

All compute steps run deterministically on the existing Python 3.12 / PyTorch 2.15.0+cpu environment without requiring external cloud GPU instances:

```
================================================================================
                    TASK-BY-TASK COMPUTATIONAL RUNTIME
================================================================================

1. Network Download & Checksum Validation:
   - Payload: ~230 MB archive
   - Estimated Transfer Duration: ~120 to 180 seconds (2.0 - 3.0 min)

2. Manifest Generation & Cryptographic Partitioning:
   - Specimen Count: 600 images
   - Operation: SHA-256 calculation & split mapping
   - Estimated Duration: ~30 seconds

3. Feature Extraction on Registration Cohort:
   - Specimen Count: 350 normal images
   - Operation: ResNet-18 Layer 2+3 forward pass (CPU: ~25 ms/img)
   - Estimated Duration: 350 * 0.025s = 8.75 seconds (~9 seconds)

4. Greedy K-Center Coreset Selection:
   - Input: 274,400 patch vectors (384-dimensional)
   - Target Size: 27,440 prototype vectors (10% ratio)
   - Algorithm: FAISS FlatL2 iterative minimax distance search
   - Estimated Duration: ~45 seconds on CPU

5. Baseline Calibration on Held-Out Cohort:
   - Specimen Count: 50 normal images
   - Operation: Nearest-neighbor search & 99.5th percentile computation
   - Estimated Duration: ~2 seconds

6. Blinded Inference on Independent Test Partition:
   - Specimen Count: 200 images (100 normal, 100 defect)
   - Operation: Forward pass + FAISS query (CPU: ~300 ms/img)
   - Estimated Duration: 200 * 0.30s = 60.0 seconds (1.0 minute)

7. Metric Calculation & Bootstrap Statistical Verification:
   - Operation: AUROC, AUPRC, 1000 bootstrap iterations, Wilson CIs
   - Estimated Duration: ~20 seconds

8. Report & Table Generation:
   - Operation: Markdown compilation & result serialization
   - Estimated Duration: ~5 seconds

--------------------------------------------------------------------------------
TOTAL ACTIVE CPU COMPUTE RUNTIME:               ~3.1 minutes
TOTAL END-TO-END EXECUTION RUNTIME:             ~6 to 8 minutes
================================================================================
```

---

## 4. Hardware and Dependency Verification

- **CPU Architecture:** AMD64 / x86_64 (Windows 11)
- **Active Virtual Environment:** `.venv\Scripts\python.exe`
- **Core Libraries Verified:**
  - `torch`: 2.15.0+cpu
  - `torchvision`: 0.29.2+cpu
  - `faiss`: 1.15.1
  - `timm`: 1.0.30
  - `numpy`: 1.26.4
  - `scikit-learn`: 1.4.2
- **Hardware Acceleration:** None required. The entire pipeline executes locally within standard CPU system constraints.
- **Feasibility Verdict:** **FULLY FEASIBLE WITHIN WORKSTATION CONSTRAINTS.**
