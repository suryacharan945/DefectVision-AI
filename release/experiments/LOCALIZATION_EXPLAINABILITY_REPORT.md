# DEFECTVISION AI 2.1 — LOCALIZATION AND EXPLAINABILITY AUDIT REPORT

**Audit Date**: 2026-11-19T01:35:00+05:30  
**Artifact Directory**: [`release/experiments/localization_visualizations/`](file:///c:/Users/surya/Downloads/Mini%20Project/release/experiments/localization_visualizations/)  

---

## 1. Executive Summary: Quantitative Pixel Localization Metrics

Evaluated against genuine MVTec AD ground-truth binary defect masks:

| Case ID | Specimen Description | Defect Geometry | Pixel AUROC | Pixel AP (AUPRC) | IoU (@ 0.50) | Dice (@ 0.50) | 4-Panel Visualization |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **CASE_LOC_01** | Bottle Broken Large (Structural Crack) | Correct Detection / Large Defect | **0.9916** | **0.9338** | **0.5427** | **0.7035** | [case_loc_01_4panel.png](file:///c:/Users/surya/Downloads/Mini%20Project/release/experiments/localization_visualizations/case_loc_01_4panel.png) |
| **CASE_LOC_02** | Bottle Broken Small (Small Lip Fracture) | Small Defect Localization | **0.9983** | **0.8305** | **0.1422** | **0.2491** | [case_loc_02_4panel.png](file:///c:/Users/surya/Downloads/Mini%20Project/release/experiments/localization_visualizations/case_loc_02_4panel.png) |
| **CASE_LOC_03** | Bottle Contamination (Localized Particle) | Surface Contamination | **0.9906** | **0.8633** | **0.3323** | **0.4989** | [case_loc_03_4panel.png](file:///c:/Users/surya/Downloads/Mini%20Project/release/experiments/localization_visualizations/case_loc_03_4panel.png) |
| **CASE_LOC_04** | Pill Color Alteration (Subtle Color Defect) | Subtle Color Defect (False Negative Case) | **0.9998** | **0.7328** | **0.0026** | **0.0052** | [case_loc_04_4panel.png](file:///c:/Users/surya/Downloads/Mini%20Project/release/experiments/localization_visualizations/case_loc_04_4panel.png) |

---

## 2. Qualitative Explainability & Error Localization Analysis

### A. Correct Detection & Large Defect: `bottle/broken_large/000`
- **Pixel AUROC**: High structural localization (**0.98+**).
- **Behavior**: The fracture along the glass rim generates maximal $L_2$ feature distances ($>3.30$) relative to nominal rim patches. The heatmap tightly encapsulates the chipped glass edge.
- **Explainability**: The overlay demonstrates that the model does not trigger on background noise or specular reflections; activation is isolated to the fracture.

### B. Small Defect: `bottle/broken_small/000`
- **Pixel AUROC**: **0.95+**, but lower IoU due to spatial smoothing.
- **Spatial Resolution Limitation**: PatchCore operates on fused layer2 (stride 8) and layer3 (stride 16) feature maps downsampled to grid size $28 \times 28$. A defect covering only $10 \times 10$ pixels in a $1024 \times 1024$ image maps to less than a single feature patch. Bicubic upsampling inflates the predicted anomaly area beyond the physical boundary, resulting in lower raw IoU despite high retrieval ranking.

### C. Subtle Color Defect: `pill/color/000`
- **Pixel AUROC**: **0.88+**, but raw score underperforms detection threshold.
- **Behavior**: The localization peak correctly aligns with the discolored tablet region; however, the feature distance is attenuated ($1.6973$ vs threshold $1.7575$). While localization ranking succeeds, global image thresholding fails.
