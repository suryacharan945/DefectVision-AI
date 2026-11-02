# DefectVision AI — Phase 49: Computational Resource and Latency Audit

**Document Type:** System Resource Allocation, Latency Profiling, and Environmental Audit  
**Phase:** Phase 49 — Official VisA Acquisition and Independent PatchCore Validation  
**Date:** November 2, 2026  
**Auditor:** Senior Computer Vision Research Engineer & Industrial AI Systems Specialist  
**Git Baseline Commit:** `763597c`  

---

## 1. Network & Storage Resource Allocation

```
+------------------------------------+--------------------------+-------------------------------------------------------+
| Metric / Resource Dimension        | Measured Value           | Technical Specification & Storage Mapping             |
+------------------------------------+--------------------------+-------------------------------------------------------+
| Official Archive S3 Source         | s3://amazon-visual-anomaly/VisA_20220922.tar (1.93 GB total archive)             |
| Network Transfer Mode              | HTTP Streaming Tar Reader| In-memory extraction via Python tarfile mode='r|'     |
| Total Network Data Streamed        | ~350 MB                  | Skipped 2,018 entries (candle, capsules); read cashew |
| Active Stream Extraction Time      | 106.7 seconds (~1.78 min)| Terminated immediately upon encountering chewinggum   |
| Raw Image Storage Location         | Cloud-backed Google Drive| G:\My Drive\DefectVisionAI\dataset\raw\visa\cashew\   |
| Extracted Files Count              | 701 files                | 500 normal, 100 defect, 100 masks, 1 image_anno.csv   |
| Extracted Cashew Image Payload     | 175.00 MB                | 600 color JPEG images (1274x1176 native resolution)   |
| Local Workstation C: Disk Impact   | 0 MB (Raw images)        | Zero temporary archive files staged on local drive C: |
| Memory Bank Model Storage          | 42.14 MB                 | release/phase49_independent_results/models/           |
| FAISS Index Model Storage          | 42.15 MB                 | release/phase49_independent_results/models/           |
| Total Local Disk Footprint         | ~84.5 MB                 | Completely isolated from production MVTec models      |
+------------------------------------+--------------------------+-------------------------------------------------------+
```

---

## 2. Execution Environment & Reproducibility Specifications

- **Operating System:** Microsoft Windows 11 Enterprise (Build 10.0.26300)
- **Host Architecture:** AMD64 / x86_64
- **Python Runtime:** Python 3.12.4 (`.venv\Scripts\python.exe`)
- **PyTorch Engine:** PyTorch 2.15.0+cpu (Deterministic CPU execution mode)
- **Torchvision Library:** Torchvision 0.29.2+cpu
- **Vector Search Engine:** FAISS-CPU 1.15.1 (`IndexFlatL2`, Euclidean distance metric)
- **Computer Vision Utilities:** OpenCV 4.10.0, Pillow 10.4.0, Scikit-Learn 1.4.2, SciPy 1.13.1
- **Random Seed:** Permanent seed `42` applied across NumPy, PyTorch, Python RNG, and FAISS initialization.
- **Hardware Acceleration:** **None.** 100% CPU execution without requiring GPU or Google Colab cloud instances.

---

## 3. Operational Feasibility Assessment

1. **Memory Footprint:** Peak host RAM consumption during greedy k-center coreset selection remained below $1.8\text{ GB}$, fitting comfortably within standard workstation memory constraints.
2. **Drive Health:** Cloud-staging directly into Google Drive (`G:`) preserved all available capacity on local drive `C:` ($> 58.4\text{ GB}$ free).
3. **Reproducibility Guarantee:** All image paths, split assignments, and cryptographic hashes are frozen in [`SPLIT_MANIFEST.csv`](file:///C:/Users/surya/Downloads/Mini%20Project/release/phase49_independent_results/SPLIT_MANIFEST.csv).
