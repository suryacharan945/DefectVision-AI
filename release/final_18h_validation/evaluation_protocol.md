# DefectVision AI — Quantitative Evaluation Protocol

**Document Version:** 1.0  
**Effective Date:** 2026-11-01  
**Sprint Phase:** Phase 2 (Quantitative Evaluation)  
**Author:** DefectVision AI Validation Team  
**Evaluation Scope:** MVTec Anomaly Detection Benchmark (15 Industrial Categories)

---

## 1. Objective and Scientific Integrity Principles

This protocol governs the reproducible, leakage-free empirical evaluation of DefectVision AI. The evaluation adheres strictly to the following scientific integrity principles:
1. **Zero Contamination:** No test images or defect samples were utilized for model training, coreset selection, or threshold calibration.
2. **Deterministic Inference:** All pipelines operate under frozen model weights and fixed random seeds ($seed = 42$).
3. **No Retroactive Threshold Search:** All decision thresholds correspond to pre-registered 99.5th percentile nominal calibration baselines established in development (`step9_severity_baselines.csv`) and standard classifier decision boundaries ($p \ge 0.50$).
4. **Transparent Negative Result Reporting:** Subsystem trade-offs, false alarms, and failure modes are explicitly documented without selective filtering or metric cherry-picking.

---

## 2. Benchmark Cohorts & Data Provenance

The evaluation is conducted across all 15 industrial manufacturing categories of the MVTec AD dataset:
- **Objects (10):** `bottle`, `cable`, `capsule`, `hazelnut`, `metal_nut`, `pill`, `screw`, `toothbrush`, `transistor`, `zipper`.
- **Textures (5):** `carpet`, `grid`, `leather`, `tile`, `wood`.

### Evaluation Partitions:
- **Primary Benchmark Set (`benchmark_test_v2.csv`):** 856 total images comprising 625 defective specimens and 231 nominal specimens across 15 categories. This constitutes the primary benchmark partition standardized across Phase 7, 8, and 9 evaluations.
- **Full Standard MVTec AD Test Set (`test_split.csv`):** 1,725 total images comprising 1,258 defective specimens and 467 nominal specimens, providing comprehensive census validation.

---

## 3. Evaluated Model Architectures & Decision Rules

Three distinct configurations are evaluated independently under identical conditions:

### Model A: PatchCore (Unsupervised Patch Distribution)
- **Feature Extractor:** ResNet-18 pretrained on ImageNet-1K (`IMAGENET1K_V1`), freezing all parameters.
- **Feature Representations:** Concatenation of locally average-pooled (kernel size 3, stride 1, padding 1) feature representations from `layer2` (128 channels) and `layer3` (256 channels), bilinearly interpolated to a uniform spatial grid of $28 \times 28$ ($g=28$). Total patch feature dimension $D = 384$.
- **Memory Bank:** 10% greedy k-center coreset subsampled exclusively from nominal training images.
- **Scoring Function:** For test patch features $P \in \mathbb{R}^{784 \times 384}$, nearest neighbor distance is computed via FAISS FlatL2:
  $$s(P_i) = \min_{m \in \mathcal{M}} \|P_i - m\|_2$$
  The image-level raw anomaly score is the supremum:
  $$S_{\text{raw}} = \max_{i \in \{1 \dots 784\}} s(P_i)$$
- **Decision Rule:**
  $$\hat{y}_{\text{PatchCore}} = \mathbb{I}(S_{\text{raw}} > \tau_{\text{p99}})$$
  where $\tau_{\text{p99}}$ is the frozen 99.5th percentile calibration baseline for that category.

### Model B: EfficientNet-B0 v3 (Supervised Visual Classifier)
- **Architecture:** Pretrained `efficientnet_b0` fine-tuned on the supervised training split (`supervised_train_split_v3.csv`) with cross-entropy loss.
- **Scoring Function:** Softmax posterior probability of the defective class:
  $$p_{\text{defective}} = \frac{e^{z_{\text{defective}}}}{e^{z_{\text{normal}}} + e^{z_{\text{defective}}}}$$
- **Decision Rule:**
  $$\hat{y}_{\text{EffNet}} = \mathbb{I}(p_{\text{defective}} \ge 0.50)$$

### Model C: DefectVision AI Hybrid System
- **Decision Logic:** Disjunctive union (logical OR) of the unsupervised and supervised signals:
  $$\hat{y}_{\text{Hybrid}} = \hat{y}_{\text{PatchCore}} \lor \hat{y}_{\text{EffNet}}$$
- **Severity Scoring:** Multi-factor fused score $\in [0, 100]$:
  $$\text{Severity} = 0.50 \cdot \tilde{S}_{\text{norm}} + 0.30 \cdot A_{\text{defect}} + 0.20 \cdot C_{\text{confidence}}$$
  where:
  - $\tilde{S}_{\text{norm}} = \text{clip}\left(\frac{S_{\text{raw}} - \mu_{\text{baseline}}}{\tau_{\text{p99}} - \mu_{\text{baseline}}}, 0, 1.5\right) \times 100$
  - $A_{\text{defect}} = \frac{100}{784} \sum_{i=1}^{784} \mathbb{I}(\tilde{M}_i \ge 0.50)$
  - $C_{\text{confidence}} = p_{\text{defective}} \times 100$

---

## 4. Formal Metric Definitions

For each evaluated model across the evaluation set:

1. **Confusion Matrix Elements:**
   - **True Positive (TP):** Defective specimen correctly flagged as defective ($\hat{y}=1, y=1$).
   - **True Negative (TN):** Nominal specimen correctly classified as normal ($\hat{y}=0, y=0$).
   - **False Positive (FP):** Nominal specimen incorrectly flagged as defective ($\hat{y}=1, y=0$) — *Type I Error / False Alarm*.
   - **False Negative (FN):** Defective specimen missed and labeled normal ($\hat{y}=0, y=1$) — *Type II Error / Defect Escape*.

2. **Classification Metrics:**
   - **Accuracy:** $\frac{TP + TN}{TP + TN + FP + FN}$
   - **Balanced Accuracy:** $\frac{1}{2} \left(\frac{TP}{TP + FN} + \frac{TN}{TN + FP}\right)$
   - **Defect Precision (Positive Predictive Value, PPV):** $\frac{TP}{TP + FP}$
   - **Normal Precision (Negative Predictive Value, NPV):** $\frac{TN}{TN + FN}$
   - **Defect Recall / Sensitivity (True Positive Rate, TPR):** $\frac{TP}{TP + FN}$
   - **Specificity (True Negative Rate, TNR):** $\frac{TN}{TN + FP}$
   - **F1-Score:** $\frac{2 \cdot \text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$
   - **False Positive Rate (FPR):** $\frac{FP}{FP + TN} = 1 - \text{Specificity}$
   - **False Negative Rate (FNR):** $\frac{FN}{FN + TP} = 1 - \text{Recall}$

3. **Threshold-Free Discrimination Metrics:**
   - **AUROC (Area Under Receiver Operating Characteristic):** Area under the TPR vs. FPR curve across all classification thresholds $\tau \in (-\infty, \infty)$.
   - **AUPRC (Area Under Precision-Recall Curve):** Average precision across all decision recall operating points.
