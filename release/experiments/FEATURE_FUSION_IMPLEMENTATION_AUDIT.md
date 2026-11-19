# DEFECTVISION AI 2.4 — FEATURE-FUSION IMPLEMENTATION & NUMERICAL AUDIT

**Document Identifier:** `release/experiments/FEATURE_FUSION_IMPLEMENTATION_AUDIT.md`  
**Governing Standard:** IEEE Trans. on Pattern Analysis & Machine Intelligence / GMLP Guidelines  
**Focus Variant:** Variant D3 ($\mathbf{f}_{\text{fused}} = [\mathbf{f}_{\text{spatial}}; 0.5 \cdot \mathbf{f}_{\text{color}}]$)  
**Related Manifest:** [spatial_photometric_detailed_acceptance.csv](file:///c:/Users/surya/Downloads/Mini%20Project/release/experiments/spatial_photometric_detailed_acceptance.csv)  

---

## 1. Architectural Architecture & Formula Audit

The feature-fusion implementation in `scripts/run_spatial_photometric_experiment.py` combines deep CNN spatial patch features with localized CIE $L^*a^*b^*$ color features:

$$\mathbf{f}_{\text{fused}} = \begin{bmatrix} \hat{\mathbf{f}}_{\text{spatial}} \\ \lambda \cdot \hat{\mathbf{f}}_{\text{color}} \end{bmatrix} \in \mathbb{R}^{387}$$

where:
- $\hat{\mathbf{f}}_{\text{spatial}} \in \mathbb{R}^{384}$ is extracted from ResNet18 Layer 2 & Layer 3, interpolated to a $28 \times 28$ grid, and normalized per patch: $\hat{\mathbf{f}}_{s} = \frac{\mathbf{f}_s}{\|\mathbf{f}_s\|_2 + \epsilon}$.
- $\hat{\mathbf{f}}_{\text{color}} \in \mathbb{R}^{3}$ is the mean CIE $L^*a^*b^*$ vector of each corresponding $8 \times 8$ pixel cell, normalized per cell: $\hat{\mathbf{f}}_c = \frac{\mathbf{f}_c}{\|\mathbf{f}_c\|_2 + \epsilon}$.
- $\lambda \in \{0.0, 0.1, 0.25, 0.5, 1.0, 2.0\}$ is the scalar weighting factor.

---

## 2. Direct Answers to the 8 Core Implementation Questions

### Question 1: Selection Data for $\lambda = 0.50$
**Audit Finding:** The weighting parameter $\lambda = 0.50$ was **selected using final-test data**.
In `scripts/run_spatial_photometric_experiment.py`, the four candidate weights $\lambda \in \{0.10, 0.25, 0.50, 2.00\}$ were swept directly across the 77 test specimens. $\lambda = 0.50$ was highlighted because it produced the highest Color Recall ($24.0\%$) among the fused variants on the test set. Because no separate validation split was held out, **Variant D3 must be categorized as an exploratory development result**, not a validated model.

### Question 2: Normalization Parameter Fitting
**Audit Finding:** Normalization was computed as **per-sample patch-level L2 unit normalization** ($\|\mathbf{f}\|_2 = 1.0$). While this avoids population mean/variance leakage across train and test sets, it normalizes each patch independently, which destroys global image-level illumination context.

### Question 3: Numerical Balance Between Color and Spatial Branches
**Audit Finding:** **The two branches are severely unbalanced numerically.**
Although both $\hat{\mathbf{f}}_s$ and $\hat{\mathbf{f}}_c$ individually have unit norm ($\|\hat{\mathbf{f}}_s\|_2 = 1.0, \|\hat{\mathbf{f}}_c\|_2 = 1.0$), the spatial branch spans **384 orthogonal dimensions**, whereas the color branch spans only **3 dimensions**.

### Question 4: Euclidean Distance Domination
**Audit Finding:** **The spatial branch overwhelmingly dominates the Euclidean distance metric in FAISS.**
The squared Euclidean distance between two fused patch vectors $\mathbf{u}, \mathbf{v}$ is:
$$\|\mathbf{u} - \mathbf{v}\|_2^2 = \sum_{i=1}^{384} (u_{s,i} - v_{s,i})^2 + \lambda^2 \sum_{j=1}^{3} (u_{c,j} - v_{c,j})^2$$
When $\lambda = 0.50$, the maximum possible contribution from the color branch is $\lambda^2 \times (2)^2 = 0.5^2 \times 4 = 1.0$, whereas the 384 spatial dimensions have an expected distance variance that is an order of magnitude larger. In FAISS nearest-neighbor queries, patches that differ significantly in color still find near-zero distances if their 384 spatial edge/texture features match. This explains why naive concatenation failed to achieve $\ge 85\%$ color defect recall.

### Question 5: Feature Scaling Consistency
**Audit Finding:** Feature scaling is mathematically identical between reference and test images (same per-patch L2 normalization and same $\lambda$ multiplier). No scaling drift occurs at inference time.

### Question 6: Evaluation of Separate Memory Banks
**Audit Finding:** **No.** All evaluated fusion variants (C, D1, D2, D3, D4) concatenated spatial and photometric features into a **single unified FAISS memory bank** ($D=387$). Separate spatial and photometric memory banks with dual-stream score aggregation were not evaluated in Sprint 2.3.

### Question 7: Spatial Alignment of Branch Heatmaps
**Audit Finding:** The heatmaps are inherently co-registered because the $28 \times 28$ spatial grid cells exactly correspond to the $8 \times 8$ pixel tiles of the $224 \times 224$ input image ($28 \times 8 = 224$). There is zero spatial coordinate misalignment between the CNN receptive fields and the color tiles.

### Question 8: Preservation of Defect Localization
**Audit Finding:** As evidenced in [spatial_photometric_localization_comparison.png](file:///c:/Users/surya/Downloads/Mini%20Project/release/experiments/spatial_photometric_localization_comparison.png), feature fusion preserves spatial localization of color flaws, improving Mean IoU from $0.0128$ (Spatial-only) to $0.0193$ (Variant D3) and $0.0227$ (Variant C). However, operational IoU remains low because the global threshold $\tau = 0.5798$ is too elevated for subtle patch distance deviations.

---

## 3. Engineering Recommendations

1. **Abandon Single-Bank Concatenation:** Concatenating 3 color channels with 384 CNN channels in an L2 metric space is mathematically flawed due to dimensionality dominance.
2. **Implement Dual-Stream Architecture:** Build separate FAISS memory banks for spatial features ($D=384$) and color features ($D=3$), compute normalized anomaly scores $s_{\text{spatial}}$ and $s_{\text{color}}$ independently, and fuse at the decision level:
   $$s_{\text{fused}}(x, y) = \max\left(\frac{s_{\text{spatial}}(x,y)}{\tau_{\text{spatial}}}, \frac{s_{\text{color}}(x,y)}{\tau_{\text{color}}}\right)$$
