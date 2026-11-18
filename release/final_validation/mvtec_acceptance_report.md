# DefectVision AI — Official 15-Category MVTec AD Acceptance & Verification Report

**Date:** 2026-11-18 11:28:37 UTC  
**Dataset Location:** `C:\Users\surya\Downloads\Mini Project\DefectVisionAI\dataset\raw\mvtec`  
**Total Specimens Evaluated:** 1725 (467 nominal, 1,258 defective)  

## 1. Executive Benchmark Summary

| Evaluation Dimension | Workflow A: Known Category | Workflow B: Auto-Category Routing |
|:---|:---:|:---:|
| **Macro Image AUROC** | **97.15%** | - |
| **Macro Image AUPRC** | **98.98%** | - |
| **Defect Sensitivity / Recall** | **95.40%** (1183 / 1258) | - |
| **Nominal Specificity** | **70.96%** (351 / 467) | - |
| **Macro F1-Score** | **92.40%** | - |
| **Pixel AUROC (Localization)** | **98.02%** | - |
| **Category Recognition Accuracy** | 100.0% (Operator Override) | **92.83%** |

## 2. Per-Category Performance Breakdown

| Category | Type | Test (Nom/Def) | AUROC | AUPRC | Recall | Specificity | F1 | Pix AUROC | Mean Latency | Auto-Cat Acc |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `bottle` | object | 20/63 | **100.00%** | 100.00% | 100.00% | 100.00% | 100.00% | 98.6% | 1009.4 ms | 98.8% |
| `cable` | object | 58/92 | **98.76%** | 99.18% | 90.22% | 96.55% | 93.79% | 98.1% | 1859.2 ms | 96.7% |
| `capsule` | object | 23/109 | **94.20%** | 98.48% | 89.91% | 78.26% | 92.45% | 98.8% | 1956.8 ms | 100.0% |
| `carpet` | texture | 28/89 | **96.55%** | 99.02% | 86.52% | 96.43% | 92.22% | 98.7% | 2218.8 ms | 96.6% |
| `grid` | texture | 21/57 | **95.07%** | 98.33% | 96.49% | 71.43% | 93.22% | 97.6% | 3045.6 ms | 100.0% |
| `hazelnut` | object | 40/70 | **100.00%** | 100.00% | 98.57% | 100.00% | 99.28% | 98.7% | 2430.8 ms | 90.9% |
| `leather` | texture | 32/92 | **100.00%** | 100.00% | 100.00% | 37.50% | 90.20% | 99.7% | 1816.3 ms | 92.7% |
| `metal_nut` | object | 22/93 | **99.56%** | 99.90% | 98.92% | 81.82% | 97.35% | 97.8% | 1884.5 ms | 88.7% |
| `pill` | object | 26/141 | **90.96%** | 98.13% | 82.98% | 76.92% | 88.64% | 97.1% | 1184.3 ms | 97.6% |
| `screw` | object | 41/119 | **95.80%** | 98.49% | 88.24% | 85.37% | 91.30% | 99.2% | 1325.6 ms | 100.0% |
| `tile` | texture | 33/84 | **99.75%** | 99.90% | 100.00% | 33.33% | 88.42% | 97.2% | 4580.9 ms | 71.8% |
| `toothbrush` | object | 12/30 | **92.50%** | 96.61% | 100.00% | 25.00% | 86.96% | 98.5% | 1429.3 ms | 90.5% |
| `transistor` | object | 60/40 | **99.21%** | 98.69% | 100.00% | 78.33% | 86.02% | 96.1% | 1499.2 ms | 96.0% |
| `wood` | texture | 19/60 | **99.65%** | 99.90% | 100.00% | 31.58% | 90.23% | 95.4% | 1678.5 ms | 72.2% |
| `zipper` | object | 32/119 | **95.19%** | 98.08% | 99.16% | 71.88% | 95.93% | 98.9% | 1958.0 ms | 100.0% |
| **MACRO AVERAGE** | **15 Categories** | **467/1258** | **97.15%** | **98.98%** | **95.40%** | **70.96%** | **92.40%** | **98.02%** | **1991.8 ms** | **92.83%** |

## 3. Scientific Disclosures & Integrity Protocol Compliance

1. **Data Separation:** The 1,725 official test specimens were strictly quarantined during training and calibration. Zero test specimens were used for memory-bank construction or threshold calibration.
2. **Preprocessing Consistency:** Live Benchmark Mode and offline evaluation use identical full-frame preprocessing (RGB -> 224x224 -> ImageNet normalization) without ROI cropping.
3. **Threshold Calibration:** Decision boundaries were calibrated strictly on disjoint calibration images using the empirical p99 quantile.
4. **Full Artifact Integrity:** Confusion matrices, prediction logs, and visual comparison grids are published in `C:\Users\surya\Downloads\Mini Project\release\final_validation`.
