# DefectVision AI — Category Recognition Model Evaluation Report

**Model Architecture:** ImageNet-Pretrained EfficientNet-B0 with Fine-Tuned Top Blocks and Calibrated Head.

**Number of Classes:** 15 official MVTec AD categories.

## 1. Executive Summary

- **Validation Accuracy (726 images):** 100.00%
- **Validation Macro F1:** 100.00%
- **Official Test Set Accuracy (1,725 images):** 99.94%
- **Official Test Set Macro F1:** 99.94%
- **Unknown-Category Rejection Rate:** 40.0%
- **CPU Inference Latency (p50):** 82.92 ms (mean: 86.82 ms, p95: 124.05 ms)

## 2. Per-Category Performance on Official Test Set (1,725 images)

| Category | Type | Test Images | Precision | Recall | F1-Score | Status |
|:---|:---|:---:|:---:|:---:|:---:|:---:|
| `bottle` | object | 83 | 100.00% | 100.00% | 100.00% | **PASS** |
| `cable` | object | 150 | 100.00% | 100.00% | 100.00% | **PASS** |
| `capsule` | object | 132 | 100.00% | 100.00% | 100.00% | **PASS** |
| `carpet` | texture | 117 | 100.00% | 100.00% | 100.00% | **PASS** |
| `grid` | texture | 78 | 100.00% | 100.00% | 100.00% | **PASS** |
| `hazelnut` | object | 110 | 100.00% | 100.00% | 100.00% | **PASS** |
| `leather` | texture | 124 | 100.00% | 100.00% | 100.00% | **PASS** |
| `metal_nut` | object | 115 | 100.00% | 100.00% | 100.00% | **PASS** |
| `pill` | object | 167 | 100.00% | 100.00% | 100.00% | **PASS** |
| `screw` | object | 160 | 99.38% | 100.00% | 99.69% | **PASS** |
| `tile` | texture | 117 | 100.00% | 100.00% | 100.00% | **PASS** |
| `toothbrush` | object | 42 | 100.00% | 100.00% | 100.00% | **PASS** |
| `transistor` | object | 100 | 100.00% | 100.00% | 100.00% | **PASS** |
| `wood` | texture | 79 | 100.00% | 98.73% | 99.36% | **PASS** |
| `zipper` | object | 151 | 100.00% | 100.00% | 100.00% | **PASS** |
| **MACRO AVERAGE** | - | **1,725** | **99.96%** | **99.92%** | **99.94%** | **VERIFIED** |

## 3. Open-Set Unknown Category Rejection

- **Unknown Evaluation Samples:** 125 (VisA Cashew, out-of-domain textures, noise, solid color).
- **Unknown Rejection Rate:** 40.0%
- **False Acceptance Rate:** 60.0%
- **Mean Calibrated Confidence on Unknowns:** 0.7075
- **Mean Normalized Entropy on Unknowns:** 0.4717

