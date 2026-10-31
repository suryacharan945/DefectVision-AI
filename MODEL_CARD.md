# DefectVision AI — Model Card

**Model Name:** DefectVision AI Optical Anomaly Suite  
**Version:** 1.0.0-research-prototype  
**Release Date:** November 2026  
**License:** MIT License  

---

## 1. Model Details

### 1.1 Architecture Specifications
The DefectVision AI system utilizes two complementary neural network models:

1. **PatchCore Anomaly Detector:**
   - **Backbone Network:** WideResNet-50-2 pre-trained on ImageNet-1k.
   - **Feature Extraction Layers:** Mid-level feature maps from `layer2` and `layer3`, combined via adaptive average pooling to create local neighborhood patch representations (dimension $d = 384$).
   - **Memory Subsampling:** Greedy minimax facility location coreset reduction retaining $10\%$ of patch tokens.
   - **Indexing & Retrieval:** FAISS `IndexFlatL2` (exact Euclidean distance search).
   - **Decision Rule:** $k\text{NN}$ distance ($k=3$) compared against category-specific empirical threshold $\tau_c$.

2. **EfficientNet-B0 Classifier:**
   - **Backbone Network:** EfficientNet-B0 (Tan & Le, 2019).
   - **Pre-training:** ImageNet pre-trained weights fine-tuned on multi-category industrial defect samples.
   - **Head:** Linear classification head producing class logits for defect categorization.
   - **Explainability:** Grad-CAM backpropagation targeting final convolutional feature maps (`features[8]`).

3. **Platt Probability Calibrator:**
   - **Model:** Univariate logistic regression fitted on signed score margin $S(X) - \tau_c$.
   - **Objective:** Predicts posterior defect probability $\hat{P}(Y=1 \mid S(X) - \tau_c) \in [0, 1]$.

---

## 2. Intended Use and Target Domain

### 2.1 Primary Intended Applications
- **Quality Control Screening:** High-throughput screening of manufactured components in industrial manufacturing lines.
- **Operator Decision Support:** Presenting localized anomaly heatmaps and defect root-cause suggestions to human visual inspectors.
- **Selective Review Triage:** Prioritizing specimens with ambiguous anomaly margins for manual audit under strict inspection capacity limits.
- **Academic & Research Benchmarking:** Evaluating selective classification algorithms, calibration stability, and human-in-the-loop workflows.

### 2.2 Out-of-Scope and Prohibited Uses
- **Autonomous Safety-Critical Certification:** Deploying the model without human oversight in life-critical domains (e.g., aerospace turbine manufacturing, nuclear component fabrication, implantable medical devices).
- **Uncalibrated Distributional Shifts:** Operating on novel object geometries, altered lighting configurations, or camera resolutions without re-calibrating decision thresholds $\tau_c$.
- **Surveillance and Non-Industrial Imaging:** The models are strictly calibrated for industrial surface quality inspection and are unsuitable for general natural image classification or facial detection.

---

## 3. Training and Calibration Data

### 3.1 Training Data (PatchCore Nominal Fitting)
- **Source:** MVTec Anomaly Detection (MVTec AD) benchmark.
- **Condition:** 100% nominal (defect-free) images. No defective specimens are ever included in PatchCore memory banks.
- **Resolution:** Resized and center-cropped to $224 \times 224$ pixels, normalized using standard ImageNet mean and variance.

### 3.2 Calibration Data
- **Composition:** Disjoint $50\%$ split of available validation specimens (both normal and labeled anomalies).
- **Function:** Used strictly to determine decision threshold $\tau_c$ at the $99.5^{\text{th}}$ percentile of nominal validation samples, and to fit Platt scaling parameters $(\beta_0, \beta_1)$.
- **Quarantine Guarantee:** Evaluation holdout sets (and the 11 reserved VisA categories) are strictly excluded from calibration.

---

## 4. Quantitative Performance Summary

Performance evaluated on the 330 development specimens across MVTec development categories:

| Category | Image AUROC (PatchCore) | Optimal Threshold ($\tau_c$) | F1-Score | Mean Latency (CPU) |
|:---|:---:|:---:|:---:|:---:|
| **Bottle** | $99.8\%$ | $1.4138$ | $0.985$ | $42.3\text{ ms}$ |
| **Capsule** | $98.6\%$ | $1.3850$ | $0.962$ | $45.1\text{ ms}$ |
| **Metal Nut** | $99.1\%$ | $1.4420$ | $0.974$ | $39.8\text{ ms}$ |

*(Note: Exact performance varies based on hardware configuration and camera optics. Metrics reflect isolated benchmark runs.)*

---

## 5. Limitations and Operational Risks

1. **Camera Angle & Fixture Sensitivity:** The nearest-neighbor memory bank assumes consistent specimen positioning. Variations in camera angle $>10^\circ$ or significant rotation will register as false anomalies.
2. **Surface Reflectivity:** Highly specular metallic surfaces (e.g., polished aluminum, chrome) can produce specular glare artifacts that inflate anomaly scores.
3. **Platt Scaling Variance on Small Samples:** Calibrated probabilities on categories with fewer than 20 validation defects exhibit wider confidence intervals ($95\%\text{ CI} \approx \pm 0.12$).
4. **Class Imbalance in Manufacturing:** Because true defects represent $<1\%$ of real factory volume, false alarm rates must be closely monitored to prevent operator cognitive fatigue.

---

## 6. Human-in-the-Loop Safeguards

DefectVision AI is intentionally designed as an **augmented intelligence tool** rather than an autonomous decision-maker:
- All borderline predictions are flagged for manual operator review.
- The UI displays explicit confidence margins and nearest training exemplars to allow human validation before physical part rejection.
- Operator overrides are logged to ensure traceability and audit compliance.
