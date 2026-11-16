# DefectVision AI — Official 15-Category PatchCore Benchmark Report

**Benchmark:** MVTec Anomaly Detection (1,725 Official Test Images, CC BY-NC-SA 4.0).

**Evaluation Protocol:** Quarantined test evaluation using category-specific nominal memory banks and disjoint calibration thresholds.

## 1. Executive Macro Summary

- **Macro Image AUROC:** 97.15%
- **Macro Image AUPRC:** 98.98%
- **Macro Defect Recall (Sensitivity):** 95.40%
- **Macro Specificity:** 70.96%
- **Macro F1-Score:** 92.40%

## 2. Per-Category Quantitative Results

| Category | Type | Test (N/D) | Threshold | Image AUROC | Image AUPRC | Pixel AUROC | Recall | Specificity | F1 | Escapes (FN) | False Alarms (FP) |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `bottle` | object | 20/63 | 1.4666 | 100.00% | 100.00% | 0.9857 | 100.00% | 100.00% | 100.00% | 0 | 0 |
| `cable` | object | 58/92 | 2.4577 | 98.76% | 99.18% | 0.9805 | 90.22% | 96.55% | 93.79% | 9 | 2 |
| `capsule` | object | 23/109 | 1.1502 | 94.22% | 98.49% | 0.9868 | 89.91% | 78.26% | 92.45% | 11 | 5 |
| `carpet` | texture | 28/89 | 1.3543 | 96.55% | 99.02% | 0.9869 | 86.52% | 96.43% | 92.22% | 12 | 1 |
| `grid` | texture | 21/57 | 1.4634 | 95.07% | 98.33% | 0.9753 | 96.49% | 71.43% | 93.22% | 2 | 6 |
| `hazelnut` | object | 40/70 | 2.3403 | 100.00% | 100.00% | 0.9872 | 98.57% | 100.00% | 99.28% | 1 | 0 |
| `leather` | texture | 32/92 | 1.1136 | 100.00% | 100.00% | 0.9968 | 100.00% | 37.50% | 90.20% | 0 | 20 |
| `metal_nut` | object | 22/93 | 1.8271 | 99.56% | 99.90% | 0.9776 | 98.92% | 81.82% | 97.35% | 1 | 4 |
| `pill` | object | 26/141 | 1.7575 | 90.97% | 98.13% | 0.97 | 82.98% | 76.92% | 88.64% | 24 | 6 |
| `screw` | object | 41/119 | 1.4684 | 95.80% | 98.49% | 0.9916 | 88.24% | 85.37% | 91.30% | 14 | 6 |
| `tile` | texture | 33/84 | 1.4735 | 99.75% | 99.90% | 0.9716 | 100.00% | 33.33% | 88.42% | 0 | 22 |
| `toothbrush` | object | 12/30 | 1.4593 | 92.50% | 96.61% | 0.9846 | 100.00% | 25.00% | 86.96% | 0 | 9 |
| `transistor` | object | 60/40 | 1.7787 | 99.21% | 98.69% | 0.9603 | 100.00% | 78.33% | 86.02% | 0 | 13 |
| `wood` | texture | 19/60 | 1.344 | 99.65% | 99.90% | 0.9536 | 100.00% | 31.58% | 90.23% | 0 | 13 |
| `zipper` | object | 32/119 | 1.1627 | 95.19% | 98.08% | 0.9888 | 99.16% | 71.88% | 95.93% | 1 | 9 |
| **MACRO AVG** | - | **467/1258** | - | **97.15%** | **98.98%** | - | **95.40%** | **70.96%** | **92.40%** | **75** | **116** |

