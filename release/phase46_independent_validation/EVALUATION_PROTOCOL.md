# DefectVision AI — Phase 46: Pre-Registered Independent Evaluation Protocol

**Document Version:** 1.0.0  
**Phase:** Phase 46 — Independent Validation and Applied Research Gate  
**Effective Date:** November 2, 2026  
**Status:** **PRE-REGISTERED & LOCKED (EXECUTION HALTED AT PHASE A/B GATE)**  
**Governing Manifest:** `release/phase46_independent_validation/FROZEN_MODEL_MANIFEST.json`  
**Author:** DefectVision AI Methodology & Quality Assurance Team  

---

## 1. Scientific Governance & Pre-Registration Mandate

This protocol establishes the rigorous, leakage-free empirical methodology required to evaluate DefectVision AI against independent, out-of-distribution manufacturing datasets.

### 1.1 Integrity Principles
1. **Zero-Contamination Boundary:** Under no circumstances may test images, defect specimens, or external target validation images be accessed during feature extraction, memory bank coreset selection, or threshold calibration.
2. **Pre-Registered Decision Rules:** All decision boundaries ($\tau_{\text{p99}}$ for PatchCore, $p \ge 0.50$ for EfficientNet) must be permanently locked prior to unblinding test labels or computing test metrics. Post-hoc threshold searching or metric-guided threshold shifting is strictly prohibited.
3. **Deterministic Execution:** All inference runs must execute with frozen weights, fixed seeds ($seed = 42$), and bitwise reproducible PyTorch/FAISS configurations.
4. **Transparent Negative Result Preservation:** All prediction errors, false alarms, defect escapes, and latency bottlenecks must be preserved in immutable prediction logs without selective filtering.

---

## 2. Model Architectures & Decision Rules

Under this protocol, three inspection paradigms are evaluated simultaneously on identical image inputs:

### 2.1 Model A: PatchCore (Unsupervised Memory-Bank Anomaly Detector)
- **Backbone Architecture:** ResNet-18 pretrained on ImageNet-1K (`IMAGENET1K_V1`), parameters permanently frozen.
- **Feature Extraction:** Concatenation of locally average-pooled (kernel size $3 \times 3$, stride 1, padding 1) feature maps from `layer2` (128 channels) and `layer3` (256 channels), bilinearly interpolated to a uniform spatial grid of $28 \times 28$ ($g=28$). Total patch feature dimension $D = 384$.
- **Coreset Construction:** 10% greedy k-center coreset subsampled exclusively from nominal target specimens:
  $$\mathcal{M} = \text{k-center}(\{P_i\}_{i=1}^{N_{\text{patches}}}, \text{ratio}=0.10)$$
- **Image-Level Scoring Function:** For a test image with patch features $P \in \mathbb{R}^{784 \times 384}$, patch anomaly is determined by nearest-neighbor Euclidean distance in FAISS:
  $$s(P_i) = \min_{m \in \mathcal{M}} \|P_i - m\|_2$$
  The image anomaly score is the supremum:
  $$S_{\text{raw}} = \max_{i \in \{1 \dots 784\}} s(P_i)$$
- **Pre-Registered Decision Rule:**
  $$\hat{y}_{\text{PatchCore}} = \mathbb{I}(S_{\text{raw}} > \tau_{\text{p99}})$$
  where $\tau_{\text{p99}}$ is the pre-registered 99.5th percentile nominal calibration threshold established on target nominals.

### 2.2 Model B: EfficientNet-B0 v3 (Supervised Visual Classifier)
- **Backbone Architecture:** Pretrained EfficientNet-B0 fine-tuned on industrial training images (`supervised_train_split_v3.csv`).
- **Classification Output:** Logits $z_{\text{normal}}, z_{\text{defective}}$ converted via softmax to posterior defect probability:
  $$p_{\text{defective}} = \frac{e^{z_{\text{defective}}}}{e^{z_{\text{normal}}} + e^{z_{\text{defective}}}}$$
- **Pre-Registered Decision Rule:**
  $$\hat{y}_{\text{EffNet}} = \mathbb{I}(p_{\text{defective}} \ge 0.50)$$

### 2.3 Model C: DefectVision AI Dual-Engine Hybrid
- **Decision Rule (Disjunctive Union):**
  $$\hat{y}_{\text{Hybrid}} = \hat{y}_{\text{PatchCore}} \lor \hat{y}_{\text{EffNet}}$$
  A specimen is rejected if *either* the unsupervised structural memory bank detects an anomalous patch *or* the supervised classifier flags defect patterns.
- **Continuous Severity Score:** Fused score $\in [0, 100]$:
  $$\text{Severity} = 0.50 \cdot \tilde{S}_{\text{norm}} + 0.30 \cdot A_{\text{defect}} + 0.20 \cdot C_{\text{confidence}}$$
  where:
  - $\tilde{S}_{\text{norm}} = \text{clip}\left(\frac{S_{\text{raw}} - \mu_{\text{baseline}}}{\tau_{\text{p99}} - \mu_{\text{baseline}}}, 0, 1.5\right) \times 100$
  - $A_{\text{defect}} = \frac{100}{784} \sum_{i=1}^{784} \mathbb{I}(\tilde{M}_i \ge 0.50)$ (percentage of defective patch area)
  - $C_{\text{confidence}} = p_{\text{defective}} \times 100$

---

## 3. Quantitative Evaluation Metrics

For every model configuration across the evaluation partition, the following metrics must be computed:

### 3.1 Binary Classification & Error Trade-Offs
1. **Confusion Matrix Elements:**
   - $\text{TP}$: Defective specimen correctly flagged ($\hat{y}=1, y=1$)
   - $\text{TN}$: Nominal specimen correctly cleared ($\hat{y}=0, y=0$)
   - $\text{FP}$: Nominal specimen falsely flagged ($\hat{y}=1, y=0$) — *False Alarm / Overkill*
   - $\text{FN}$: Defective specimen escaped inspection ($\hat{y}=0, y=1$) — *Defect Escape / Underkill*
2. **Statistical Rates:**
   - **Defect Recall (Sensitivity, TPR):** $\frac{\text{TP}}{\text{TP} + \text{FN}}$
   - **Specificity (TNR):** $\frac{\text{TN}}{\text{TN} + \text{FP}}$
   - **Precision (PPV):** $\frac{\text{TP}}{\text{TP} + \text{FP}}$
   - **Balanced Accuracy:** $\frac{\text{TPR} + \text{TNR}}{2}$
   - **F1-Score:** $\frac{2 \cdot \text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$
   - **False Positive Rate (FPR):** $\frac{\text{FP}}{\text{FP} + \text{TN}} = 1 - \text{Specificity}$
   - **False Negative Rate (FNR):** $\frac{\text{FN}}{\text{FN} + \text{TP}} = 1 - \text{Recall}$

### 3.2 Threshold-Free Discrimination Metrics
1. **AUROC (Area Under ROC Curve):** Area under the TPR vs. FPR curve across all operating thresholds, computed from continuous raw scores ($S_{\text{raw}}$, $p_{\text{defective}}$, and Severity).
2. **AUPRC (Area Under Precision-Recall Curve):** Average precision across recall levels, providing robust evaluation under class imbalance.

### 3.3 Localization & Pixel Segmentation (Ground-Truth Masks Required)
When pixel-level binary annotation masks $M \in \{0, 1\}^{H \times W}$ are available:
1. **Pixel-AUROC:** Receiver operating characteristic computed over individual pixel anomaly heatmaps.
2. **AUPRO (Per-Region Overlap):** Average overlap across connected defect components, integrated up to 30% false positive rate.

### 3.4 Operational & Computational Latency
- Measured using high-resolution monotonic timers (`time.perf_counter()`):
  - Preprocessing time (resizing, tensor conversion, normalization)
  - PatchCore feature extraction & FAISS search latency
  - EfficientNet forward pass latency
  - End-to-end API round-trip latency (CPU execution)
  - Peak resident set memory usage (RAM)

---

## 4. Category Compatibility and Domain Shift Boundary Rules

A critical constraint of industrial computer vision architectures is **category specificity**:
1. **No Silent Cross-Mapping:** A PatchCore memory bank constructed on nominal instances of Product A (e.g., MVTec translucent cosmetic bottles) cannot evaluate Product B (e.g., VisA printed circuit boards or Chukyo medicinal capsules) without target domain registration.
2. **Pre-Deployment Calibration Requirement:** In any industrial transfer setting, DefectVision AI requires an on-site calibration cohort of at least 50 verified nominal specimens ($N_{\text{cal}} \ge 50$) to build the local FAISS coreset and establish the 99.5th percentile baseline ($\tau_{\text{p99}}$).
3. **Supervised Head Boundary:** The supervised EfficientNet-B0 v3 classifier is restricted to its 15 trained product classes. When encountering an unmodeled product, the supervised head must either be disabled or retrained; forcing inference through mismatched class logits produces uncalibrated defect posteriors.

---

## 5. Execution Status: Gatekeeper Determination

In accordance with Phase A findings (`DATASET_ELIGIBILITY_AUDIT.md`), zero external candidate datasets meet the combined criteria of unexposed status, local physical availability, and frozen category compatibility.

- **Phase A Verdict:** INELIGIBLE / CONDITIONALLY ELIGIBLE (CRITICAL STOP RULE TRIGGERED).
- **Phase B Verification:** Completed and frozen in `FROZEN_MODEL_MANIFEST.json`.
- **Phase C Execution:** **HALTED.** No external test inference was executed.
- **Phase D Execution:** **HALTED.** No empirical perturbation benchmarks were run on unverified data.

This protocol remains preserved and fully specified as the pre-registered blueprint for future independent validation upon authorized dataset acquisition.
