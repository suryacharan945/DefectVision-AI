# DefectVision AI — Intellectual Property, License & Artifact Audit

**Document Version:** 2.0.0  
**Audit Date:** November 1, 2026  
**Auditor:** Legal Compliance & Open-Source Release Gatekeeper  
**Target Repository:** DefectVision AI Open-Source Research Prototype  

---

## 1. Executive Summary

This audit assesses the intellectual property (IP), redistribution permissions, third-party licenses, and binary artifact profiles of the DefectVision AI codebase and its associated pretrained artifacts.

### 1.1 Key Compliance Takeaways
1. **Application Source Code:** Released under the permissive **MIT License** (`LICENSE`), allowing open reproduction, modification, and academic distribution.
2. **Pretrained PatchCore Feature Banks:** The memory banks (`DefectVisionAI/models/patchcore/*/memory_bank.npy`) are derived directly from patch embeddings of the **MVTec Anomaly Detection (MVTec AD)** benchmark. Under the terms set by MVTec Software GmbH, these derivative feature banks are restricted to **non-commercial research and academic use only**.
3. **Dual-Licensing Demarcation:** The repository must explicitly differentiate between the application software (MIT) and the pre-computed MVTec feature banks (MVTec Non-Commercial Research License).
4. **Binary Artifact Sizes:** All tracked artifacts comply with GitHub file size boundaries. The largest single tracked file is $46.35\text{ MB}$, below GitHub's $50\text{ MB}$ warning threshold and well within GitHub's $100\text{ MB}$ block limit.

---

## 2. Component-by-Component License Inventory

### 2.1 Software Codebase & Frontend Assets
| Component | Files / Directory | License | Commercial Permissibility | Notes |
|:---|:---|:---:|:---:|:---|
| **DefectVision AI Core** | `DefectVisionAI/src/`, `backend/`, `scripts/`, `tests/` | **MIT** | Yes | Full source code, test harnesses, and FastAPI routing. |
| **Frontend Web Console** | `frontend/src/`, `frontend/index.html` | **MIT** | Yes | React 19, Tailwind CSS v4, Three.js 3D inspection view. |
| **Research Protocols** | `research/`, `DefectVisionAI/research/` | **MIT** | Yes | Reproducibility scripts, protocol definitions, decision audits. |

### 2.2 Deep Learning Models & Feature Banks
| Artifact | Location | Source / Upstream Origin | Applicable License | Redistribution Condition |
|:---|:---|:---|:---:|:---|
| **EfficientNet-B0 Classifier** | `DefectVisionAI/models/efficientnet_baseline_v3/` | Fine-tuned from `timm` (PyTorch Image Models) pretrained weights | **Apache 2.0 / Custom** | Weights fine-tuned on MVTec development images; restricted to research evaluation. |
| **PatchCore Memory Banks (15 categories)** | `DefectVisionAI/models/patchcore/*/memory_bank.npy` | Feature embeddings extracted from nominal MVTec AD images via WideResNet-50-2 | **MVTec AD Research License** | **STRICTLY NON-COMMERCIAL.** Commercial deployment requires retraining on proprietary client data or licensing from MVTec Software GmbH. |
| **PaDiM Feature Models** | `DefectVisionAI/models/padim/*/padim_model.npz` | Gaussian distributions fitted on nominal MVTec AD patch activations | **MVTec AD Research License** | **STRICTLY NON-COMMERCIAL.** Derivative research weights. |

### 2.3 Third-Party Runtime Dependencies
| Library / Dependency | Primary Role | Upstream License | Compliance Verification |
|:---|:---|:---:|:---|
| **PyTorch (`torch`, `torchvision`)** | Deep learning framework & tensor math | Modified BSD | Verified; standard runtime dependency. |
| **FAISS (`faiss-cpu`)** | Vector similarity search & nearest neighbors | MIT License | Verified; fully compatible. |
| **FastAPI / Starlette / Uvicorn** | Asynchronous REST backend & ASGI server | MIT / BSD-3-Clause | Verified; fully compatible. |
| **OpenCV (`opencv-python-headless`)** | Heatmap rendering & image transformations | Apache 2.0 | Verified; headless distribution prevents GUI library bloat. |
| **timm (`pytorch-image-models`)** | Backbone network definitions | Apache 2.0 | Verified; attribution preserved in model cards. |
| **React / React-DOM** | Frontend UI framework | MIT License | Verified; fully compatible. |
| **Three.js (`three`, `@react-three/fiber`)** | Interactive 3D component rendering | MIT License | Verified; fully compatible. |
| **Lucide Icons (`lucide-react`)** | Industrial icon library | ISC License | Verified; fully compatible. |

---

## 3. Dataset Redistribution Rights & Boundaries

### 3.1 MVTec Anomaly Detection (MVTec AD)
- **Copyright:** MVTec Software GmbH, Munich, Germany.
- **Reference:** Bergmann et al., "MVTec AD — A Comprehensive Real-World Dataset for Unsupervised Anomaly Detection", CVPR 2019 / IJCV 2021.
- **Redistribution Policy:**
  - Raw benchmark images are **NOT bundled** in this repository (only minimal single-specimen demonstration images for smoke tests are included).
  - Users wishing to retrain memory banks or replicate full baseline evaluations must download the original dataset directly from [MVTec Software GmbH](https://www.mvtec.com/company/research/datasets/mvtec-ad).
  - Bundled `.npy` memory banks are pre-computed feature representations provided solely for research reproducibility under MVTec's academic terms.

### 3.2 Visual Anomaly (VisA)
- **Copyright:** Zou et al., "SPOT-the-Difference: Self-Supervised Pre-training for Anomaly Detection and Segmentation", ECCV 2022.
- **License:** Creative Commons Attribution 4.0 International (CC BY 4.0).
- **Status in Repo:** VisA images are **NOT redistributed**. The 7 quarantined categories remain untouched externally.

### 3.3 BeanTech Anomaly Detection (BTAD) & Chukyo
- **BTAD:** Mishra et al., IEEE Access 2021. Not bundled.
- **Chukyo:** Industrial fastener benchmark. Not bundled.

---

## 4. Git Artifact Size & Storage Profile

A complete audit of tracked blobs using `git ls-tree -r -l HEAD` confirms that no file violates repository hosting bounds:

| Rank | Tracked Path | File Type | Size (Bytes) | Size (MB) | GitHub Threshold Status |
|:---:|:---|:---:|:---:|:---:|:---:|
| 1 | `DefectVisionAI/models/efficientnet_baseline/last_checkpoint.pt` | PyTorch Weight Checkpoint | 48,605,721 | 46.35 MB | **PASS** (<50MB warning threshold) |
| 2 | `DefectVisionAI/models/efficientnet_baseline_v3/last_checkpoint.pt` | PyTorch Weight Checkpoint | 48,604,825 | 46.35 MB | **PASS** (<50MB warning threshold) |
| 3 | `DefectVisionAI/models/efficientnet_baseline_v2/last_checkpoint.pt` | PyTorch Weight Checkpoint | 48,604,825 | 46.35 MB | **PASS** (<50MB warning threshold) |
| 4 | `DefectVisionAI/models/checkpoint.pth` | PyTorch Weight Checkpoint | 48,601,656 | 46.35 MB | **PASS** (<50MB warning threshold) |
| 5 | `DefectVisionAI/models/patchcore/hazelnut/memory_bank.npy` | NumPy Memory Bank | 42,267,776 | 40.31 MB | **PASS** (<50MB warning threshold) |
| 6 | `DefectVisionAI/models/patchcore/screw/memory_bank.npy` | NumPy Memory Bank | 34,681,472 | 33.07 MB | **PASS** (<50MB warning threshold) |
| 7–15 | `DefectVisionAI/models/padim/*/padim_model.npz` (9 files) | PaDiM NumPy Model Archives | 31,674,628 | 30.21 MB each | **PASS** (<50MB warning threshold) |

**Audit Result:** Zero tracked files exceed 50 MB. The repository can be pushed to standard GitHub remotes without requiring Git LFS configuration or triggering file size rejections.

---

## 5. Mandatory Public Release Notices

Prior to making the repository publicly accessible, the following notice must appear prominently in `README.md` and `LICENSE`:

> **Notice Regarding Pretrained Weights & Feature Banks:**  
> The software architecture and implementation code of DefectVision AI are licensed under the MIT License. However, the precomputed PatchCore memory banks (`models/patchcore/`) and PaDiM models (`models/padim/`) distributed with this repository were computed from images belonging to the MVTec Anomaly Detection dataset. These artifacts are strictly provided for non-commercial academic research and demonstration purposes. Commercial users must fit memory banks exclusively on their own proprietary inspection imagery.
