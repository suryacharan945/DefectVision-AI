# DefectVision AI — Formal Experimental Program Matrix

**Document ID:** `DV-EXP-MATRIX-2026-Q1-V1`  
**Date:** October 31, 2026  
**Standards Compliance:** IEEE Guidelines for Rigorous Computer Vision Benchmarking  
**Primary Focus:** Calibrated Selective Review & Benchmarking Across 15 Industrial Categories  

---

## 1. Experimental Architecture & Baseline Portfolio

The experimental program benchmarks four distinct paradigm baselines against the proposed Calibrated Patch-Neighborhood Dispersion (CPND) selective inspection framework.

| Model ID | Paradigm | Feature Extraction Backbone | Training Supervision | Memory / Weight Footprint | Output Representation |
|:---|:---|:---|:---|:---|:---|
| **M1: AE** | Reconstruction | Custom 6-layer Conv-Deconv | Nominal images only (MSE) | ~14.8 MB / category | Pixel-wise residual map $L_2(x, \hat{x})$ |
| **M2: PaDiM** | Parametric Density | ResNet-18 (Layers 1, 2, 3) | Nominal images only (Gaussian) | ~42.3 MB / category | Mahalanobis patch distance map |
| **M3: PatchCore** | Non-Parametric Memory Bank | WideResNet-50-2 (Layers 2, 3) | Nominal images only (10% Coreset) | ~98.4 MB / category | $1$-NN Euclidean distance in $\mathcal{M}$ |
| **M4: EffNet-B0 (v3)**| Supervised Classification | EfficientNet-B0 (ImageNet init) | Binary (Nominal + Dev Defects) | ~21.2 MB (Global) | Sigmoid class probability $P(y=1\|x)$ |
| **M5: Proposed (CPND)**| Uncertainty-Gated Ensemble | WideResNet-50-2 + $k$-NN FAISS | Nominal images only (Conformalized)| ~98.4 MB / category | Anomaly Score $S(x)$ + Gating Metric $U(x)$ |

---

## 2. Benchmark Dataset & Stratification Protocol

### 2.1 Dataset Stratification (Leak-Free Protocol)
The benchmark evaluates 15 industrial manufacturing categories partitioned into two primary structural groups:
* **Rigid Object Categories (10):** `bottle`, `cable`, `capsule`, `hazelnut`, `metal_nut`, `pill`, `screw`, `toothbrush`, `transistor`, `zipper`.
* **Surface Texture Categories (5):** `carpet`, `grid`, `leather`, `tile`, `wood`.

| Dataset Split | Specimen Volume | Composition | Protocol Constraints |
|:---|:---:|:---|:---|
| **Nominal Training Split** | 3,629 images | Exclusively normal/defect-free parts | Used to construct memory banks $\mathcal{M}$, fit PaDiM Gaussians, and train Autoencoders. Zero defectives permitted. |
| **Development Split (Dev)** | 869 images | 50% of official test split (Normal + Defective) | Used for threshold calibration ($\tau$), hyperparameter grid search, and active learning uncertainty tuning. |
| **Held-Out Benchmark Split** | 856 images | 50% of official test split (Strictly Quarantined) | Evaluated once with completely frozen parameters and thresholds. Zero hyperparameter tuning. |
| **Chukyo Transfer Set** | Cold Storage | External real-world automotive stampings | **BLOCKED:** Unseen target domain evaluation only after benchmark protocol is locked. |

---

## 3. Core Quantitative Evaluation Metrics

All metrics are computed on the identical 856-image Held-Out Benchmark Partition.

### 3.1 Detection & Classification Metrics (Image-Level)
1. **Image-Level AUROC:** Area under the ROC curve computed trapezoidally over continuous anomaly scores $S(x)$.
2. **Average Precision (AP / PR-AUC):** Area under the Precision-Recall curve, resilient to class imbalance.
3. **Recall at Fixed False Positive Rate ($\text{Recall}@\text{FPR}=1\%$ and $\text{Recall}@\text{FPR}=5\%$):** Crucial industrial KPI reflecting defect detection capability when false alarms are strictly capped.
4. **Precision, Specificity, Balanced Accuracy, and F1-Score:** Evaluated at frozen threshold $\tau$ determined on the Development Split.

### 3.2 Spatial Localization Metrics (Pixel-Level)
1. **Pixel-Level AUROC:** Evaluated across all pixel positions $(u, v)$ against ground-truth binary defect masks.
2. **Area Under Per-Region Overlap (AUPRO):** Computed up to $\text{FPR} = 0.30$. Prevents large defect regions from dominating the score over tiny micro-scratches.

### 3.3 Selective Classification Metrics (Uncertainty & Gating)
1. **Area Under the Risk-Coverage Curve (AURC):** Evaluates risk (defect escape rate) as coverage increases from $0\%$ to $100\%$.
2. **Defect Escape Reduction Rate (DERR):**
   $$\text{DERR}(B) = \frac{\text{Escape Rate}_{\text{Uncalibrated}} - \text{Escape Rate}_{\text{Gated}}(B)}{\text{Escape Rate}_{\text{Uncalibrated}}}$$
   for human review budgets $B \in \{2\%, 5\%, 10\%\}$.
3. **Capture Efficiency Ratio (CER):** Proportion of audited images that were true misclassifications.

### 3.4 Operational & Computational Efficiency Metrics
1. **Inference Latency (ms):** Mean, median, and 99th-percentile wall-clock latency per image on:
   - Intel Core i7 / Xeon CPU (Batch Size = 1)
   - NVIDIA RTX 3080 / 4090 GPU (TensorRT FP16)
2. **Peak Memory Consumption (MB):** Resident Set Size (RSS) and GPU VRAM during steady-state inference.
3. **Memory Bank Disk & RAM Footprint:** Storage required to host the 15-category FAISS indexes.

---

## 4. Formal Domain-Shift Definitions & Protocol Rules

To prevent misleading cross-domain generalizations, the experimental program enforces strict separation between three distinct types of distribution shift:

```
                            DISTRIBUTION SHIFTS
                                    │
       ┌────────────────────────────┼────────────────────────────┐
       ▼                            ▼                            ▼
Category Shift              Acquisition Shift             External Domain Shift
(Product Cross-Transfer)    (Sensor/Optics Perturbation) (Real-World Manufacturing)
       │                            │                            │
 Train: Bottle, Screw       Apply: Illumination ±30%,    MVTec AD ──► Chukyo Set
 Test:  Cable, Pill                Gaussian Blur σ∈[1,3], (Rigid cold storage lock;
 (Evaluates semantic               Perspective skew 15°   zero fine-tuning permitted)
 representation depth)      (Evaluates camera invariance)
```

### Protocol Rules for Chukyo Evaluation:
1. **Zero Fine-Tuning:** All feature extractors and memory banks remain frozen.
2. **No Post-Hoc Threshold Optimization:** Thresholds calibrated on MVTec AD must be tested directly on Chukyo without tuning to Chukyo score distributions.
3. **Calibrated Normalization:** Only fixed sensor-level normalization (zero-mean unit-variance per channel) is permissible.

---

## 5. Statistical Rigor & Verification Procedures

### 5.1 Multi-Seed Stochastic Verification
For stochastic components (e.g. PatchCore greedy coreset subsampling and supervised classifier initialization):
* All experiments are repeated across 5 distinct seeds: $\mathcal{S} = \{42, 101, 2024, 777, 999\}$.
* Report values as $\text{Mean} \pm \text{Standard Deviation}$.

### 5.2 Clustered Bootstrap Confidence Intervals
Industrial inspection images of the same physical object under different lighting or angles are statistically correlated.
* We compute $95\%$ Confidence Intervals using Non-Parametric Clustered Bootstrapping ($B = 10,000$ iterations).
* Resampling is clustered by physical specimen ID rather than treating individual frames as independent identically distributed (i.i.d.) observations.

---

## 6. Full Experiment Matrix Execution Plan

| Experiment ID | Target Question | Backbone Models | Dataset / Split | Primary Dependent Variables |
|:---|:---|:---|:---|:---|
| **EXP-01-BENCH** | Held-Out Baseline Comparison | M1, M2, M3, M4 | 856 Held-Out Benchmark | Image-AUROC, Acc, Prec, Rec, F1 |
| **EXP-02-LOCAL** | Spatial Localization Fidelity | M1, M2, M3 | 856 Held-Out Benchmark | Pixel-AUROC, AUPRO ($\le 0.30$) |
| **EXP-03-SELECT**| Selective Review Efficacy | M3, M4, M5 (CPND)| 856 Held-Out Benchmark | AURC, DERR ($B=5\%, 10\%$), CER |
| **EXP-04-ABL-K** | Neighborhood Size Sensitivity | M5 ($k \in \{1, 3, 5, 10, 20\}$) | Development Split (869) | CER, Latency overhead |
| **EXP-05-ROBUST**| Sensor Noise & Blur Shift | M3, M4, M5 | Perturbed 856 Split | AUROC degradation slope $\Delta\text{AUC}$ |
| **EXP-06-COMP**  | Efficiency & Footprint Audit | M1, M2, M3, M4, M5 | Single-image stream | Latency (CPU/GPU), VRAM, RAM |
| **EXP-07-CHUKYO**| External Domain Generalization | M3, M5 (Frozen) | Chukyo Industrial Set | Cross-domain AUROC, Escape Rate |

---
*Certified for Experimental Execution:*  
**Lead AI/ML Research Engineer**  
DefectVision AI Project
