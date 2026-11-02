# DefectVision AI — Phase 47: Pre-Registered Independent Validation Protocol

**Document Type:** Pre-Registered Experimental Protocol & Hypothesis Blueprint  
**Phase:** Phase 47 — Three-Hour Research Feasibility Sprint  
**Target Evaluation Cohort:** Visual Anomaly (VisA) Benchmark — `cashew`  
**Date:** November 2, 2026  
**Git Baseline Commit:** `20ec56e`  
**Status:** **PRE-REGISTERED & LOCKED (PENDING EXECUTION AUTHORIZATION)**  
**Author:** DefectVision AI Research Methodology & Validation Team  

---

## 1. Scientific Hypothesis & Research Questions

This experimental protocol establishes the pre-registered methodology for evaluating DefectVision AI on an unmodeled industrial manufacturing category, adhering to peer-reviewed reproducibility standards.

### 1.1 Central Hypothesis
> **Hypothesis $H_1$:**  
> A non-parametric patch memory-bank architecture (PatchCore) operating on frozen ResNet-18 mid-level representations (`layer2` + `layer3`), registered exclusively on $\le 350$ nominal target specimens and calibrated on 50 held-out nominals, can reliably distinguish anomalous from nominal specimens in an unseen product domain (VisA `cashew`), achieving an image-level AUROC $\ge 0.8500$ and defect recall $\ge 80.00\%$ without requiring any defect training samples.

### 1.2 Core Research Questions
1. Does DefectVision AI’s patch-level feature representation transfer successfully to non-MVTec industrial geometries without weight fine-tuning?
2. Does the pre-registered 99.5th percentile nominal calibration threshold ($\tau_{\text{p99}}$) maintain a false alarm rate $\le 10\%$ on held-out test nominals?
3. How does independent out-of-distribution performance on VisA compare to the development-exposed baseline on MVTec AD?

---

## 2. Experimental Partitions and Zero-Contamination Boundary

The 600 specimens of VisA `cashew` are partitioned into three strictly non-overlapping cohorts:

```
+---------------------------+----------------+---------------+----------------------------------------------------------+
| Partition Name            | Specimen Count | Labels        | Experimental Role & Contamination Control                |
+---------------------------+----------------+---------------+----------------------------------------------------------+
| 1. Registration Cohort    | 350 images     | Nominal (y=0) | Feature extraction & 10% greedy k-center coreset fitting.|
|                           |                |               | Zero defect images; zero test images permitted.          |
+---------------------------+----------------+---------------+----------------------------------------------------------+
| 2. Calibration Cohort     | 50 images      | Nominal (y=0) | Derive empirical null distribution, baseline mean        |
|                           |                |               | (mu_baseline) and 99.5th percentile threshold (tau_p99).|
+---------------------------+----------------+---------------+----------------------------------------------------------+
| 3. Untouched Test Cohort  | 200 images     | 100 Nominal   | Blinded evaluation of discrimination and localization.   |
|                           |                | 100 Defect    | Locked weights and thresholds; 50% defect prevalence.    |
+---------------------------+----------------+---------------+----------------------------------------------------------+
```

---

## 3. Detailed Algorithmic Specifications

### 3.1 Preprocessing Pipeline
1. Input images resized to $224 \times 224$ pixels using PyTorch `InterpolationMode.BILINEAR` with antialiasing enabled.
2. Pixel intensity values normalized to floating-point tensors in $[0.0, 1.0]$.
3. Standard ImageNet channel-wise standardization:
   $$\mu = [0.485, 0.456, 0.406], \quad \sigma = [0.229, 0.224, 0.225]$$

### 3.2 Feature Extraction Backbone
- **Model:** Pretrained ResNet-18 (`torchvision.models.resnet18(weights=ResNet18_Weights.IMAGENET1K_V1)`).
- **Execution Mode:** Inference mode (`torch.no_grad()`, `model.eval()`), parameters permanently frozen.
- **Layer Taps:**
  - `layer2`: 128 channels, spatial resolution $28 \times 28$.
  - `layer3`: 256 channels, spatial resolution $14 \times 14$.
- **Local Neighborhood Aggregation:**
  - Feature maps from `layer2` and `layer3` are smoothed using $3 \times 3$ local average pooling (stride 1, padding 1).
  - `layer3` feature maps are bilinearly upsampled to match the $28 \times 28$ spatial resolution ($g=28$).
- **Concatenated Feature Tensor:**
  $$\phi(x) \in \mathbb{R}^{784 \times 384}$$
  Each image produces exactly 784 spatial patch embeddings of dimension $D = 384$.

### 3.3 Target Memory Bank Registration
1. For the 350 registration images, extract patch representations, yielding an initial matrix:
   $$\mathcal{P}_{\text{raw}} \in \mathbb{R}^{274,400 \times 384}$$
2. Apply the **greedy k-center coreset subsampling algorithm** with subsampling ratio $r = 0.10$:
   $$\mathcal{M}_{\text{cashew}} = \text{k-center}(\mathcal{P}_{\text{raw}}, N_{\text{coreset}} = 27,440)$$
3. Build a FAISS index (`faiss.IndexFlatL2(384)`) loaded with $\mathcal{M}_{\text{cashew}}$.

### 3.4 Baseline Calibration & Threshold Locking
1. Pass the 50 calibration nominal specimens through the feature extractor and compute patch-level nearest-neighbor distances:
   $$s(P_i) = \min_{m \in \mathcal{M}_{\text{cashew}}} \|P_i - m\|_2, \quad \forall i \in \{1 \dots 784\}$$
2. Derive the image-level maximum patch distance:
   $$S_{\text{raw}}^{(k)} = \max_{i \in \{1 \dots 784\}} s(P_i^{(k)})$$
3. Compute and permanently freeze the calibration parameters:
   $$\mu_{\text{baseline}} = \frac{1}{50} \sum_{k=1}^{50} S_{\text{raw}}^{(k)}$$
   $$\tau_{\text{p99}} = \text{Percentile}\left(\{S_{\text{raw}}^{(k)}\}_{k=1}^{50}, 99.5\right)$$
4. Save parameters to `cashew_baselines.json`. **No subsequent modification of $\tau_{\text{p99}}$ is permitted.**

### 3.5 Treatment of Supervised Classifier (EfficientNet-B0 v3)
- DefectVision AI’s EfficientNet-B0 v3 was trained exclusively as a 15-class classifier over MVTec AD.
- Because `cashew` is an external biological/industrial category outside MVTec, the classifier head has no valid representation or decision boundary for cashew defects.
- **Protocol Rule:** EfficientNet-B0 v3 is **explicitly excluded** from the test decision gate for VisA `cashew`. Attempting to force cashew images through MVTec class logits would produce ungrounded out-of-distribution hallucinations. The experiment tests the transferability of the unsupervised memory-bank engine.

---

## 4. Quantitative Evaluation Metrics

All metrics will be computed on the 200 untouched test specimens:

### 4.1 Binary Classification & Error Rates
- **Confusion Matrix:** True Positives (TP), True Negatives (TN), False Positives (FP), False Negatives (FN) based on decision rule $\hat{y} = \mathbb{I}(S_{\text{raw}} > \tau_{\text{p99}})$.
- **Defect Recall (Sensitivity, TPR):** $\frac{\text{TP}}{\text{TP} + \text{FN}}$
- **Specificity (TNR):** $\frac{\text{TN}}{\text{TN} + \text{FP}}$
- **Precision (PPV):** $\frac{\text{TP}}{\text{TP} + \text{FP}}$
- **Balanced Accuracy:** $\frac{\text{TPR} + \text{TNR}}{2}$
- **F1-Score:** $\frac{2 \cdot \text{PPV} \cdot \text{TPR}}{\text{PPV} + \text{TPR}}$
- **False Positive Rate (FPR):** $\frac{\text{FP}}{\text{FP} + \text{TN}} = 1 - \text{Specificity}$
- **False Negative Rate (FNR):** $\frac{\text{FN}}{\text{FN} + \text{TP}} = 1 - \text{Recall}$

### 4.2 Discrimination & Localization Metrics
- **Image-Level AUROC:** Calculated across the continuous score spectrum of $S_{\text{raw}}$.
- **Image-Level AUPRC:** Area under the precision-recall curve.
- **Pixel-Level AUROC:** Computed by comparing interpolated pixel anomaly heatmaps ($\tilde{M} \in \mathbb{R}^{224 \times 224}$) against ground-truth binary segmentation masks.
- **Pixel-Level AUPRO (Per-Region Overlap):** Evaluated across connected component defect regions up to a false positive rate of 0.30.

### 4.3 Statistical Uncertainty & Confidence Intervals
- Proportions (Recall, Specificity, Precision, Balanced Accuracy) will include **95% Wilson score confidence intervals**.
- Image AUROC and Pixel AUROC will include **95% empirical bootstrap confidence intervals** (1,000 resamples).

---

## 5. Pre-Registered Pass / Fail Criteria

To maintain experimental objectivity, the outcome of the experiment will be evaluated against the following strict, pre-registered benchmarks:

```
+--------------------+------------------------------------------------------------------------------------------+
| Outcome Category   | Pre-Registered Criteria                                                                  |
+--------------------+------------------------------------------------------------------------------------------+
| PASS (Success)     | 1. Image-Level AUROC >= 0.8500                                                           |
|                    | 2. Defect Recall >= 80.00% at tau_p99                                                    |
|                    | 3. False Alarm Rate (FPR) <= 10.00% on test nominals                                     |
|                    | 4. Pixel-Level AUROC >= 0.9000                                                           |
|                    | 5. Memory Bank Registration Time <= 120 seconds on CPU                                   |
+--------------------+------------------------------------------------------------------------------------------+
| MARGINAL (Partial) | Image-Level AUROC between 0.7500 and 0.8500; Defect Recall between 70.00% and 80.00%.    |
+--------------------+------------------------------------------------------------------------------------------+
| FAIL (Rejection)   | Image-Level AUROC < 0.7500, OR Defect Recall < 70.00%, OR False Alarm Rate > 15.00%.    |
+--------------------+------------------------------------------------------------------------------------------+
```

---

## 6. Scientific Negative-Result Governance

If the empirical results trigger a **MARGINAL** or **FAIL** outcome, the result will **NOT** be discarded, retried with adjusted hyperparameters, or hidden. It will be formally documented and published as an empirical boundary of non-parametric transfer: demonstrating that mid-level ImageNet feature representations require domain-adaptive fine-tuning when transferred from artificial industrial objects to natural organic surface morphologies.
