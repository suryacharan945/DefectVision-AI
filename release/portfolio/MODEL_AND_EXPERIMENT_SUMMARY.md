# DefectVision AI — Model and Experiment Summary

**Milestone:** `v1.0.0-rc1`  
**Evaluation Scope:** 15 MVTec AD Industrial Categories, Few-Shot K-Shot Adaptation, and Statistical Calibration  
**Status:** `RELEASE READY WITH DOCUMENTED METRIC LIMITATIONS`

---

## 1. Core Model Architectures

DefectVision AI deploys two synergistic neural networks: an upstream supervised classifier for product category identification and an unsupervised patch-based nearest-neighbor engine for anomaly detection.

### 1.1 Category Routing Classifier: EfficientNet-B0
- **Task:** 15-class closed-set industrial product category classification.
- **Backbone:** EfficientNet-B0 pretrained on ImageNet-1k, with a custom linear classification head ($1000 \to 15$).
- **Input Resolution:** $224 \times 224$ pixels, RGB normalized with ImageNet mean and standard deviation.
- **Trained Parameters:** 4.02 million.
- **Checkpoint Location:** `DefectVisionAI/models/category_classifier.pt`
- **Performance:** **99.94% accuracy** across 1,725 benchmark test images (1,724 correct, 1 error).
- **Distinction Notice:** This 99.94% metric measures **product SKU identification** (e.g., distinguishing a bottle from a cable), *not* binary defect detection.

### 1.2 Anomaly Detection Engine: PatchCore
- **Task:** Localized unsupervised visual anomaly detection and segmentation without defect training data.
- **Feature Extractor:** ResNet18 pretrained on ImageNet-1k (frozen weights, zero backpropagation during enrollment or inference).
- **Extracted Layers:** `layer2` (128 channels, stride 8) and `layer3` (256 channels, stride 16).
- **Spatial Grid Alignment:** `layer2` is pooled via $3 \times 3$ adaptive average pooling (stride 2) to align spatially with `layer3`, forming a $28 \times 28$ spatial feature map.
- **Patch Representation:** Each spatial location is represented by concatenating features across layers:
  $$p_{(x,y)} = \left[ \phi_{\text{layer2}}(x,y) \parallel \phi_{\text{layer3}}(x,y) \right] \in \mathbb{R}^{384}$$
- **Total Patches per Image:** $28 \times 28 = 784$ localized patch embeddings.

### 1.3 Memory Bank & FAISS Indexing
- **Memory Bank Creation:** Nominal patch embeddings from training images are extracted and accumulated into category-specific matrices.
- **Index Implementation:** `faiss.IndexFlatL2(d=384)` executed on CPU.
- **Coreset Reduction:** For large training sets, greedy coreset subsampling selects a subset $\mathcal{M}^* \subset \mathcal{M}$ (typically 10%–20%) that minimizes the Hausdorff distance to the full set, maintaining detection performance while reducing memory footprint and search latency.
- **Query Mechanism:** For a test image with patch set $\mathcal{P}_{\text{test}} = \{p_1, \dots, p_{784}\}$, FAISS computes:
  $$s_i = \min_{m \in \mathcal{M}^*} \| p_i - m \|_2$$
  The image anomaly score is $S = \max_{i} s_i$.

---

## 2. Experimental Methodology & Rigorous Evaluation Protocol

To prevent evaluation leakage and maintain reproducibility, all evaluations adhere to strict protocols:

1. **Split Isolation:** Nominal training images are used exclusively to build memory banks. Test sets contain both unseen nominal specimens and defective specimens.
2. **Deterministic Preprocessing:** Fixed bicubic resizing to $224 \times 224$, standard PyTorch normalization. Zero stochastic augmentation during evaluation.
3. **Threshold Freeze Rule:** Thresholds evaluated on test sets must be established *a priori* on calibration splits or frozen across categories; post-hoc threshold optimization on the test set is strictly prohibited for release claims.
4. **Metric Definitions:**
   - **Macro Image AUROC:** Arithmetic mean of individual category Area Under the ROC Curve metrics across all 15 categories (unweighted by category sample counts).
   - **Macro Image AUPRC:** Arithmetic mean of Precision-Recall curves across 15 categories.
   - **Mean Pixel AUROC:** Pixel-level anomaly segmentation accuracy evaluated against ground-truth binary defect masks.
   - **Micro Operational Metrics:** Pooled confusion matrix over all 1,725 test images at operational threshold $\tau = 1.50$.

---

## 3. Summary of Validated Experiments

### 3.1 15-Category Benchmark Evaluation (MVTec AD)
Comprehensive evaluation across all 1,725 test images (467 nominal, 1,258 defective):
- **Macro Image AUROC:** **97.15%**
- **Macro Image AUPRC:** **98.98%**
- **Mean Pixel AUROC:** **98.02%**
- **Micro Operational Accuracy ($\tau = 1.50$):** **88.93%** (1,534 / 1,725 correct)
- **Micro Defect Recall:** **94.04%** (1,183 / 1,258 defects detected; 75 escapes)
- **Micro False Positive Rate (FPR):** **24.84%** (116 / 467 nominal flagged as false alarms)
- **Micro Precision:** **91.07%** (1,183 / 1,299)
- **Micro F1 Score:** **0.9253**

### 3.2 Few-Shot Adaptation Experiment (Bottle SKU Specimen Set)
Evaluated few-shot onboarding using limited nominal reference images ($K=10$ and $K=20$) tested on 83 held-out specimens (20 nominal, 63 defective across multiple defect types):

| Adaptation Regime | Threshold Selection Policy | Defect Recall | False Alarm Rate (FPR) | F1 Score | Status & Provenance |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Full Memory Bank** | Frozen $\tau = 1.50$ | 100.0% (63/63) | 20.00% (4/20) | 0.9692 | Validated benchmark baseline |
| **K = 10 Few-Shot** | Frozen $\tau = 1.50$ | 96.83% (61/63) | 0.00% (0/20) | **0.9839** | **Validated release candidate** |
| **K = 20 Few-Shot** | Frozen $\tau = 1.50$ | 100.0% (63/63) | 20.00% (4/20) | 0.9692 | Validated frozen baseline |
| **K = 20 Few-Shot** | Post-Hoc Multiplier ($1.25\times \implies \tau = 1.875$) | 98.41% (62/63) | 0.00% (0/20) | 0.9841 | **Development-only ablation** (Excluded from release claims) |

---

## 4. Failed Experiments & Negative Findings

Scientific integrity requires documenting approaches that failed or proved inadequate:

### 4.1 Supervised Binary Defect Classification Baseline
- **Approach:** Trained a standard ResNet18 binary classifier directly on normal vs. defective images.
- **Outcome:** **Failed.** Achieved only **86.92% accuracy** (764/856 specimens) with **111 defect escapes** (false negatives).
- **Root Cause:** Novel defect types not present in the training set were classified as nominal with $>95\%$ confidence. Confirmed that supervised classification is fundamentally unsuitable for open-world defect detection.

### 4.2 Spatial-Photometric Feature Fusion (Color Anomaly Failure)
- **Approach:** Attempted early/late feature fusion combining spatial CNN embeddings with localized HSV/Lab photometric histograms to resolve subtle discoloration defects (e.g., pill contamination).
- **Outcome:** **Inconclusive / Ineffective.** Photometric histograms introduced extreme variance across normal specular highlights, increasing the false-positive rate on nominal metallic/glass surfaces without statistically significant gains in defect recall.

### 4.3 Track B: Smartphone & External Factory Adaptation
- **Approach:** Evaluated few-shot PatchCore adaptation on smartphone captures under non-standardized industrial lighting.
- **Outcome:** **Blocked.** Only 1 physical defective specimen was available. Although initial runs reported 100% metrics, audit revealed extreme sample dependency ($N=1$ defect). Track B is formally classified as unvalidated due to lack of statistical power.

---

## 5. Statistical Reliability & Confidence Intervals

A critical audit finding concerns the statistical interpretation of small-sample evaluation:
- In the K=10 adaptation experiment, 0 false alarms were observed among 20 normal test images ($k=0, n=20$).
- **Statistical Fact:** $0/20$ observed errors does **not** prove a true false-alarm rate below 1%.
- **Clopper–Pearson Exact 95% Confidence Interval:** $[0.00\%, 16.84\%]$.
- **Wilson Score 95% Confidence Interval:** $[0.00\%, 16.11\%]$.
- **Rule of Three ($3/n$):** $3 / 20 = 15.00\%$.
- **Conclusion:** Guaranteeing a production-grade false-alarm rate of $<1\%$ with 95% confidence requires testing at least $N \ge 300$ independent nominal specimens without a single false alarm.
