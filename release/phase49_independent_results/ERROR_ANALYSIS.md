# DefectVision AI — Phase 49: Forensic Error and Failure Mode Analysis

**Document Type:** Failure Mode Classification, Root Cause Analysis, and Error Forensics  
**Phase:** Phase 49 — Official VisA Acquisition and Independent PatchCore Validation  
**Target Category:** Visual Anomaly (VisA) Benchmark — `cashew` Category  
**Date:** November 2, 2026  
**Git Baseline Commit:** `763597c`  
**Author:** Senior Computer Vision Research Engineer & Experimental Methodology Specialist  

---

## 1. Executive Summary of Inspection Errors

On the 200-specimen independent test cohort, PatchCore operated under the locked 99.5th percentile nominal calibration threshold ($\tau_{\text{p99}} = 1.7452$), yielding:
- **True Positives (TP):** 57 specimens
- **True Negatives (TN):** 98 specimens
- **False Positives (FP / Type I Overkill):** **2 specimens** ($2.00\%$ false alarm rate)
- **False Negatives (FN / Type II Defect Escapes):** **43 specimens** ($43.00\%$ escape rate)

---

## 2. Fine-Grained Performance Breakdown by Defect Taxonomy

Cross-referencing the prediction log ([`TEST_PREDICTIONS.csv`](file:///C:/Users/surya/Downloads/Mini%20Project/release/phase49_independent_results/TEST_PREDICTIONS.csv)) with the official Amazon Science annotations (`image_anno.csv`) reveals that detection capability is strictly partitioned by physical defect morphology:

```
+------------------------------------------+-------+----+----+-----------+----------------------------------------------+
| Defect Category / Morphology             | Total | TP | FN | Recall    | Empirical Detection Profile                  |
+------------------------------------------+-------+----+----+-----------+----------------------------------------------+
| middle breakage                          | 6     | 6  | 0  | 100.0%    | Flawless detection (Gross structural break)   |
| stuck together                           | 6     | 6  | 0  | 100.0%    | Flawless detection (Boundary distortion)     |
| middle breakage, small holes             | 1     | 1  | 0  | 100.0%    | Flawless detection (Multi-defect component)  |
| middle breakage, same colour spot        | 1     | 1  | 0  | 100.0%    | Flawless detection (Structural dominate)     |
| different colour spot                    | 9     | 8  | 1  | 88.9%     | Robust detection (High chrominance contrast) |
| small holes                              | 20    | 17 | 3  | 85.0%     | High detection (Dark localized voids)        |
| corner or edge breakage                  | 14    | 11 | 3  | 78.6%     | Strong detection (Silhouette deformation)    |
| burnt, corner or edge breakage           | 2     | 1  | 1  | 50.0%     | Moderate detection                           |
| different colour spot, same colour spot  | 2     | 1  | 1  | 50.0%     | Moderate detection                           |
| burnt                                    | 10    | 4  | 6  | 40.0%     | Weak detection (Subtle thermal discolouring) |
| small scratches                          | 15    | 1  | 14 | 6.7%      | SEVERE ESCAPE (14/15 missed)                 |
| same colour spot                         | 10    | 0  | 10 | 0.0%      | TOTAL FAILURE (10/10 missed)                 |
| burnt, different colour spot             | 1     | 0  | 1  | 0.0%      | Escape (Subtle combination)                  |
| different colour spot, small holes       | 1     | 0  | 1  | 0.0%      | Escape (Micro defect)                        |
| burnt, same colour spot                  | 1     | 0  | 1  | 0.0%      | Escape                                       |
| corner breakage, small scratches         | 1     | 0  | 1  | 0.0%      | Escape                                       |
+------------------------------------------+-------+----+----+-----------+----------------------------------------------+
| TOTAL DEFECTIVE COHORT                   | 100   | 57 | 43 | 57.0%     | 57 Caught, 43 Escapes                        |
+------------------------------------------+-------+----+----+-----------+----------------------------------------------+
```

---

## 3. Root Cause Analysis of Detection Failures

### 3.1 Why `small scratches` Escaped Detection (6.7% Recall, 14 Misses)
- **Mechanism:** In VisA `cashew`, "small scratches" represent hairline surface abrasions that measure fewer than $2\text{ to }4$ pixels in width across a $1274 \times 1176$ image.
- **Backbone Feature Dilution:** ResNet-18 features are extracted from `layer2` (stride 8) and `layer3` (stride 16) and smoothed via $3 \times 3$ local average pooling. A hairline surface scratch occupying $< 0.5\%$ of an effective receptive field produces minimal feature displacement when averaged with surrounding healthy cashew tissue.
- **Organic Texture Masking:** Unlike polished metal surfaces in MVTec (e.g. `metal_nut`), natural cashew nuts possess natural surface striations, grooves, and folds. The patch embeddings of hairline scratches remain well inside the Euclidean convex hull of natural nominal cashew textures.

### 3.2 Why `same colour spot` Suffered Total Failure (0.0% Recall, 10 Misses)
- **Mechanism:** "Same colour spots" represent shallow physical indentations, bruises, or micro-depressions that share the exact chromatic signature (hue and saturation) of normal cashew kernel meat.
- **Invariance Limitation:** Pretrained ImageNet features are highly sensitive to contrast edges and color distributions, but exhibit partial invariance to shallow depth depressions under diffuse lighting. The maximum nearest-neighbor patch distance for these specimens stayed below the strict 99.5th percentile boundary ($\tau_{\text{p99}} = 1.7452$).

### 3.3 Why Gross Defects Achieved Near-Perfect Recall (85% to 100%)
- **Mechanism:** Gross morphological breaks (`middle breakage`, `corner breakage`, `stuck together`) completely alter the contour and boundary patch embeddings.
- **Chrominance Shift:** Defects involving color shifts (`different colour spot`, dark fungal `small holes`) produce substantial activation in early convolutional filter banks, pushing nearest-neighbor patch distances to $S_{\text{raw}} \in [2.10, 3.85]$, comfortably above $\tau_{\text{p99}}$.

---

## 4. Analysis of the 2 False Alarms (Type I Overkill)

The two nominal specimens falsely rejected under $\tau_{\text{p99}} = 1.7452$ were:
1. **`CASHEW_0428` (`185.JPG`):** Raw anomaly score $S_{\text{raw}} = 2.1065$ (vs. $\tau = 1.7452$).
   - *Cause:* Extreme specular reflection along an unusually sharp natural curved tip, causing local pixel saturation.
2. **`CASHEW_0470` (`486.JPG`):** Raw anomaly score $S_{\text{raw}} = 1.8295$ (vs. $\tau = 1.7452$).
   - *Cause:* Prominent natural furrow and deep surface fold that was under-represented in the 350 registration images.

---

## 5. Industrial and Engineering Takeaways

1. **Trade-off Quantification:** The 99.5th percentile calibration successfully prevented false alarms ($FPR = 2.00\%$), achieving near-perfect specificity ($98.00\%$). However, in natural food and agricultural inspection, suppressing false alarms forces fine topological flaws (`scratches`, `same-colour indentations`) to escape.
2. **Backbone Resolution Prerequisite:** Catching hairline scratches on organic substrates requires higher-resolution feature maps (e.g., extracting from `layer1` at stride 4, or utilizing multi-scale patch resolutions $320 \times 320$) rather than relying purely on downsampled mid-level features.
3. **Publication Value:** Documenting this exact failure boundary (100% on breaks vs 6.7% on scratches) provides authentic, high-impact empirical value for peer-reviewed applied research.
