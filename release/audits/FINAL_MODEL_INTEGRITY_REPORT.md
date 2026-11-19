# DEFECTVISION AI — FINAL MODEL INTEGRITY REPORT
**Sprint:** Emergency Release Sprint: v1.0.0-rc1 (72-Hour Project Closure)  
**Date:** 2026-11-19  
**Auditor:** Senior ML Engineer, Computer Vision Research Engineer, QA Lead & Release Manager  

---

## 1. Executive Summary

This report documents the exhaustive integrity verification of all machine learning models in **DefectVision AI v1.0.0-rc1**. Every category-specific PatchCore model, FAISS nearest-neighbor index, and the auxiliary EfficientNet-B0 classifier checkpoint was verified for existence, tensor compatibility, feature dimensions, and execution validity.

**Summary of Findings:**
- **PatchCore Models:** 15 of 15 industrial categories verified and operational.
- **Embedding Dimensions:** Uniformly 384 across all 15 categories (ResNet-18 Layers 2 & 3).
- **FAISS Indexes:** 15 of 15 available with valid metadata and token counts.
- **Calibrated Thresholds:** 15 of 15 operational thresholds verified against `category_thresholds.json`.
- **EfficientNet-B0 Classifier:** Verified with output shape $(1, 2)$ and validated weights.
- **Status:** **PASS — 100% INTEGRITY CERTIFIED**

---

## 2. 15-Category PatchCore Model Verification Matrix

The memory banks and FAISS indexes are stored in `DefectVisionAI/models/patchcore/` and `DefectVisionAI/models/faiss_index/`:

| Category | Type | Memory Bank Tokens | Feature Dim | Memory Bank Status | FAISS Index Status | Calibrated Threshold ($\tau$) | Baseline Mean ($\mu$) | Baseline P99 |
|---|---|---:|---:|:---:|:---:|---:|---:|---:|
| **bottle** | Object | 14,739 | 384 | Verified | Verified | 1.4666 | 0.9732 | 1.4348 |
| **cable** | Object | 15,758 | 384 | Verified | Verified | 2.4577 | 1.7409 | 2.4556 |
| **capsule** | Object | 15,444 | 384 | Verified | Verified | 1.1502 | 0.7614 | 1.1124 |
| **carpet** | Texture | 19,756 | 384 | Verified | Verified | 1.3543 | 0.9690 | 1.2974 |
| **grid** | Texture | 18,580 | 384 | Verified | Verified | 1.4634 | 1.0921 | 1.4592 |
| **hazelnut** | Object | 27,518 | 384 | Verified | Verified | 2.3403 | 1.2826 | 2.2507 |
| **leather** | Texture | 17,248 | 384 | Verified | Verified | 1.1136 | 0.8975 | 1.0973 |
| **metal_nut** | Object | 15,523 | 384 | Verified | Verified | 1.8271 | 1.3742 | 1.7745 |
| **pill** | Object | 18,816 | 384 | Verified | Verified | 1.7575 | 1.2280 | 1.7478 |
| **screw** | Object | 22,579 | 384 | Verified | Verified | 1.4684 | 1.0915 | 1.4636 |
| **tile** | Texture | 16,228 | 384 | Verified | Verified | 1.4735 | 1.2218 | 1.4723 |
| **toothbrush** | Object | 4,233 | 384 | Verified | Verified | 1.4593 | 1.1695 | 1.4410 |
| **transistor** | Object | 14,974 | 384 | Verified | Verified | 1.7787 | 1.4013 | 1.7582 |
| **wood** | Texture | 17,404 | 384 | Verified | Verified | 1.3440 | 1.0621 | 1.3371 |
| **zipper** | Object | 16,934 | 384 | Verified | Verified | 1.1627 | 0.9202 | 1.1625 |

---

## 3. Auxiliary Classifier Integrity (EfficientNet-B0 v3)

- **Checkpoint Location:** `DefectVisionAI/models/efficientnet_baseline_v3/best_model.pt`
- **Model Architecture:** `timm.models.efficientnet_b0`
- **File Size:** 16,336,185 bytes (~16.3 MB)
- **Output Channels:** 2 (Binary Normal vs. Defect Baseline)
- **Tensor Verification:**
  - Input: $(1, 3, 224, 224)$ normalized image tensor
  - Output: $(1, 2)$ raw logits
  - Probability Distribution: Softmax probabilities sum strictly to $1.0000$.
- **Operational Role:** Supports auxiliary category scoring and confidence routing without replacing the primary PatchCore memory bank engine.

---

## 4. Hardware & Device Execution Compatibility

- **Primary Runtime Device:** CPU (`torch.device("cpu")`)
- **OpenMP Optimization:** `KMP_DUPLICATE_LIB_OK = "TRUE"` configured to prevent Windows OpenMP threading collisions.
- **Inference Latency Profile:**
  - PatchCore feature extraction: $60 - 95 \text{ ms}$ (CPU)
  - FAISS $k$-NN search: $8 - 18 \text{ ms}$ (CPU)
  - Heatmap generation and interpolation: $12 - 25 \text{ ms}$
  - Total end-to-end latency: $\approx 110 - 160 \text{ ms}$ on standard multi-core CPU.

---

## 5. Model Integrity Verdict

- **PatchCore Models (15/15):** **VERIFIED**
- **FAISS Indexes (15/15):** **VERIFIED**
- **EfficientNet-B0 Classifier:** **VERIFIED**
- **Overall Status:** **READY FOR v1.0.0-rc1 RELEASE**
