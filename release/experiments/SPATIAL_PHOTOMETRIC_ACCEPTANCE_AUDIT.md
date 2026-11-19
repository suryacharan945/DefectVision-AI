# DEFECTVISION AI 2.4 — SPATIAL-PHOTOMETRIC OPERATIONAL ACCEPTANCE AUDIT

**Document Identifier:** `release/experiments/SPATIAL_PHOTOMETRIC_ACCEPTANCE_AUDIT.md`  
**Evaluation Baseline:** 77 Genuine MVTec Pill Test Specimens (26 Normal, 25 Color Defects, 26 Structural Cracks)  
**Related Manifest:** [spatial_photometric_detailed_acceptance.csv](file:///c:/Users/surya/Downloads/Mini%20Project/release/experiments/spatial_photometric_detailed_acceptance.csv)  

---

## 1. Executive Summary & Final Decision Classification

DefectVision AI set three strict operational acceptance targets for the spatial-photometric research initiative:
- **Target 1 (Color Defect Recall):** $\ge 85.0\%$
- **Target 2 (Normal False Positive Rate):** $\le 5.0\%$
- **Target 3 (Structural Crack Defect Recall):** $\ge 95.0\%$

This audit evaluated all seven architectural variants against these operational targets using the 77 genuine MVTec Pill test specimens.

### Overall Audit Verdict
**ALL SEVEN VARIANTS ARE CLASSIFIED AS `DOES NOT MEET TARGETS`.**

While feature fusion improved color-discriminative ranking (Color AUROC rose from $0.8492$ to $0.8862$) and modestly increased localization IoU, **no variant came close to achieving 85% color recall or 95% crack recall at the calibrated operating threshold**.

---

## 2. Complete Performance & Acceptance Audit Ledger

Evaluated on 77 physical specimens ($N_{\text{normal}}=26, N_{\text{color}}=25, N_{\text{crack}}=26$):

| Architecture Variant | $\lambda$ | Color Recall (Target $\ge 85\%$) | Crack Recall (Target $\ge 95\%$) | Normal FPR (Target $\le 5\%$) | Color AUROC | Crack AUROC | Mean Color IoU | Decision Classification |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| **Variant A: Spatial Only (ResNet18)** | 0.00 | **20.0%** (5/25)<br>95% CI: [8.9%, 39.1%] | **19.2%** (5/26)<br>95% CI: [8.5%, 37.9%] | **3.8%** (1/26)<br>95% CI: [0.7%, 18.9%] | 0.8492 | 0.7633 | 0.0128 | **DOES NOT MEET TARGETS** |
| **Variant B: Photometric Only (CIE Lab)** | 1.00 | **40.0%** (10/25)<br>95% CI: [23.4%, 59.3%] | **0.0%** (0/26)<br>95% CI: [0.0%, 12.9%] | **11.5%** (3/26)<br>95% CI: [4.0%, 29.0%] | 0.6738 | 0.6849 | 0.1353 | **DOES NOT MEET TARGETS** |
| **Variant C: Naive Fusion ($\lambda=1.0$)** | 1.00 | **20.0%** (5/25)<br>95% CI: [8.9%, 39.1%] | **19.2%** (5/26)<br>95% CI: [8.5%, 37.9%] | **0.0%** (0/26)<br>95% CI: [0.0%, 12.9%] | 0.8369 | 0.7367 | 0.0227 | **DOES NOT MEET TARGETS** |
| **Variant D1: Weighted ($\lambda=0.10$)** | 0.10 | **20.0%** (5/25)<br>95% CI: [8.9%, 39.1%] | **15.4%** (4/26)<br>95% CI: [6.2%, 33.5%] | **3.8%** (1/26)<br>95% CI: [0.7%, 18.9%] | 0.8692 | 0.7633 | 0.0124 | **DOES NOT MEET TARGETS** |
| **Variant D2: Weighted ($\lambda=0.25$)** | 0.25 | **20.0%** (5/25)<br>95% CI: [8.9%, 39.1%] | **11.5%** (3/26)<br>95% CI: [4.0%, 29.0%] | **3.8%** (1/26)<br>95% CI: [0.7%, 18.9%] | 0.8738 | 0.7648 | 0.0142 | **DOES NOT MEET TARGETS** |
| **Variant D3: Weighted ($\lambda=0.50$)** | 0.50 | **24.0%** (6/25)<br>95% CI: [11.5%, 43.4%] | **11.5%** (3/26)<br>95% CI: [4.0%, 29.0%] | **3.8%** (1/26)<br>95% CI: [0.7%, 18.9%] | 0.8523 | 0.7737 | 0.0193 | **DOES NOT MEET TARGETS** |
| **Variant D4: Weighted ($\lambda=2.00$)** | 2.00 | **12.0%** (3/25)<br>95% CI: [4.2%, 30.0%] | **15.4%** (4/26)<br>95% CI: [6.2%, 33.5%] | **3.8%** (1/26)<br>95% CI: [0.7%, 18.9%] | 0.8862 | 0.7633 | 0.0129 | **DOES NOT MEET TARGETS** |

---

## 3. Disaggregated Confusion Matrices (Focus: Variant D3)

### Confusion Matrix 1: Normal vs. Color Defects Only
Evaluates sensitivity to chromatic flaws:
```text
                  Predicted Normal    Predicted Defective    Total Specimens
Actual Normal            25                   1 (FP = 3.8%)        26
Actual Color Defect      19 (FN = 76.0%)       6 (TP = 24.0%)       25
Total                    44                   7                    51
```
- **Sensitivity (Color Recall):** $24.0\%$ (6 / 25)
- **Specificity:** $96.2\%$ (25 / 26)
- **Precision:** $85.7\%$ (6 / 7)
- **F1 Score:** $0.3750$

### Confusion Matrix 2: Normal vs. Structural Cracks Only (Control)
Evaluates impact on edge and fracture detection:
```text
                  Predicted Normal    Predicted Defective    Total Specimens
Actual Normal            25                   1 (FP = 3.8%)        26
Actual Crack Defect      23 (FN = 88.5%)       3 (TP = 11.5%)       26
Total                    48                   4                    52
```
- **Sensitivity (Crack Recall):** $11.5\%$ (3 / 26)
- **Specificity:** $96.2\%$ (25 / 26)
- **Precision:** $75.0\%$ (3 / 4)
- **F1 Score:** $0.2000$

### Confusion Matrix 3: Full Multi-Class Defect Breakdown (77 Specimens)
```text
                  Predicted Normal    Predicted Defective    Total Specimens
Actual Normal            25                   1                    26
Actual Color Flaw        19                   6                    25
Actual Crack Flaw        23                   3                    26
Total                    67                  10                    77
```

---

## 4. Root Causes of Failure

1. **Dimensional Asymmetry in Single-Bank L2 Metric:** Concatenating 3 color dimensions with 384 CNN dimensions causes the nearest-neighbor search to be driven almost entirely by the spatial features. Color distance contributes $<2\%$ to the total squared Euclidean distance.
2. **Threshold Elevation in Few-Shot Pill:** In MVTec Pill, the 10 calibration normal pills exhibited larger intra-class variation than bottles ($\max_{\text{calib}} = 0.5042$). The resulting threshold $\tau = 0.5042 \times 1.15 = 0.5798$ was too elevated, causing small hairline cracks and faint color spots to be classified as normal.
3. **Architectural Imperative:** Single-bank feature concatenation cannot solve this trade-off. A dual-stream architecture with independent decision heads is strictly required.
