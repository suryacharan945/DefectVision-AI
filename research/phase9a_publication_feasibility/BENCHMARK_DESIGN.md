# Phase 9A Deliverable: Empirical Benchmark Design Specification

**Project:** DefectVision AI — Advanced Quality Inspection Platform  
**Phase:** 9A (Research Reset and Publication Feasibility)  
**Status:** COMPLETE & INDEPENDENTLY SPECIFIED  
**Artifact:** `research/phase9a_publication_feasibility/BENCHMARK_DESIGN.md`  

---

## 1. Benchmark Scope and Objectives

This specification outlines the experimental design for an exhaustive empirical study evaluating visual anomaly detection models coupled with selective human inspection policies across heterogeneous industrial manufacturing lines.

The benchmark evaluates:
1. **Model Generalization:** The ability of unsupervised and pre-trained backbones to detect structural and surface anomalies across multi-category product domains.
2. **Calibration Stability:** The reliability of mapping continuous anomaly scores to calibrated posterior error risks using small validation partitions.
3. **Selective Review Efficiency:** The economic cost reduction achieved by deferring uncertain specimens to human visual inspectors under finite factory review budgets.
4. **Human Imperfection Degradation:** The resilience of selective review policies when human visual inspection is noisy or fatigued.

---

## 2. Evaluated Anomaly Detection Backbones

To ensure that empirical findings are not idiosyncratic to a single model architecture, the benchmark specifies three distinct, widely adopted detector paradigms:

| Backbone Detector | Paradigm | Feature Backbone | Memory / Compute Footprint | Rationale for Inclusion |
|:---|:---:|:---:|:---:|:---|
| **PatchCore** (Roth et al., 2022) | Nearest-Neighbor Memory Bank | WideResNet-50 / ResNet-50 (Mid-level patch tokens) | Medium-High (FAISS index, 10% minimax coreset subsampling) | Industry gold standard for surface and structural anomalies; core backbone of DefectVision AI. |
| **PaDiM** (Defard et al., 2021) | Parametric Gaussian Distribution | ResNet-18 / WideResNet-50 (Random dimensional reduction) | Low-Medium (Multi-variate Gaussian per patch location, zero neighbor search) | Fast parametric baseline; evaluates whether Gaussian density estimation calibrates differently than distance metrics. |
| **Frozen EfficientNet** (Tan & Le, 2019) | Direct Supervised / Pretrained Embedding | EfficientNet-B0 (Global Average Pooling) | Minimal (Single forward pass, lightweight classifier) | Evaluates transferability of off-the-shelf pre-trained representations without memory bank lookups; part of DefectVision AI hybrid pipeline. |

---

## 3. Evaluated Selective Inspection Policies

All policies operate under a global factory review budget constraint of $K$ specimens ($K \in [2\%, 25\%]$ of total batch throughput $N$).

1. **Random Allocation (BL0 - Null Baseline):** Selects $K$ specimens uniformly at random across all production lines. Represents unguided random quality auditing.
2. **Volume-Proportional Allocation (BL1):** Allocates inspection capacity strictly proportional to category manufacturing volume ($N_c / N$), auditing random samples within each line.
3. **Globally Pooled Raw Distance (BL2):** Ranks all specimens globally by absolute distance to category decision threshold $|S(X) - \tau_c|$ in ascending order. Represents naive uncertainty sampling.
4. **Globally Pooled Normalized Distance (BL3):** Normalizes distance by threshold $|S(X) - \tau_c| / \tau_c$ to account for inter-category score scale variations before global sorting.
5. **Historical Category Prior Allocation (BL4):** Allocates review quotas to categories proportional to historical error rate $\bar{e}_c$, then selects specimens by boundary distance within category.
6. **Calibrated Error-Risk Ranking (BL5):** Estimates posterior classification error probability $\hat{P}(\text{Error} \mid X)$ using logistic calibration, ranking items globally without cost weighting.
7. **Cost-Sensitive Bayes Risk Ranking (BL6 / Proper MACBA):** Ranks specimens by expected financial loss reduction under asymmetric cost matrix:
   $$\text{Score}(X) = \hat{P}(\text{Error} \mid X, \hat{Y}) \cdot W(\hat{Y})$$
   where $W(\hat{Y}) = c_{\text{FN}}$ if $\hat{Y} = 0$ and $W(\hat{Y}) = c_{\text{FP}}$ if $\hat{Y} = 1$.
8. **Oracle Upper Bound (BL7):** Selects true automated misclassifications ($\mathbb{I}(\hat{Y} \ne Y)$) using hidden evaluation labels, establishing the empirical ceiling of perfect triage.

---

## 4. Leakage-Free Three-Way Data Partitioning Protocol

To eliminate data leakage and ensure strict statistical validity, every category is partitioned into three strictly disjoint sets:

```
+-------------------------------------------------------------------------------+
|                             CATEGORY DATASET                                  |
+-------------------------------------------------------------------------------+
                                        |
       +--------------------------------+-------------------------------+
       |                                                                |
+---------------+                                              +----------------+
| NOMINAL POOL  |                                              | ANOMALOUS POOL |
| (Good images) |                                              | (Defect images)|
+---------------+                                              +----------------+
       |                                                                |
       |---> [1] Fitting Fold (Train Normal):                           |
       |         Exclusively defect-free images.                        |
       |         Used to construct PatchCore memory bank                |
       |         and fit PaDiM Gaussian parameters.                     |
       |                                                                |
       |---> [2] Calibration Fold (50% validation normal) ------------->| (50% validation defect)
       |         Used exclusively to:                                   |
       |         - Calibrate 99.5% nominal decision threshold tau_c     |
       |         - Fit logistic probability calibration models          |
       |         - Zero overlap with evaluation or training!            |
       |                                                                |
       +---> [3] Independent Evaluation Fold (50% holdout normal) ----->| (50% holdout defect)
                 Used exclusively to measure:                           |
                 - Realized cost reduction                              |
                 - Defect escapes and false scrap                       |
                 - Final statistical claims                             |
```

### Protocol Constraints:
- **Zero Label Contamination:** Evaluation labels are never accessed during feature fitting, threshold selection, or probability calibration.
- **Stratified Partitioning:** Calibration and evaluation splits are stratified across defect types (scratches, cracks, contamination, structural) to ensure balanced representation.

---

## 5. Comprehensive Metric Suite

The benchmark records five complementary performance dimensions:

### 5.1 Defect Escapes and Quality Risk
- **Defect Escape Rate (DER):** Fraction of true defective items that are incorrectly predicted as normal ($\hat{Y} = 0$) and escape to shipping without human review:
  $$\text{DER} = \frac{\sum_{i \in \text{Unreviewed}} \mathbb{I}(\hat{Y}_i = 0, Y_i = 1)}{\sum_{i=1}^N \mathbb{I}(Y_i = 1)}$$
- **Captured False Negatives (CFN):** Absolute count of critical defect escapes intercepted by the human reviewer.

### 5.2 False Alarms and Scrap Overhead
- **False Scrap Rate (FSR):** Fraction of normal parts incorrectly rejected by the automated model ($\hat{Y} = 1$) that are not reviewed and therefore scrapped unnecessarily:
  $$\text{FSR} = \frac{\sum_{i \in \text{Unreviewed}} \mathbb{I}(\hat{Y}_i = 1, Y_i = 0)}{\sum_{i=1}^N \mathbb{I}(Y_i = 0)}$$
- **Captured False Positives (CFP):** Absolute count of false alarms intercepted and cleared by the reviewer.

### 5.3 Economic Cost and Workload
- **Total Realized Cost (TRC):**
  $$\text{TRC} = \sum_{i \in \text{Reviewed}} c_{\text{rev}} + \sum_{i \notin \text{Reviewed}} \left[ c_{\text{FN}} \mathbb{I}(\hat{Y}_i=0, Y_i=1) + c_{\text{FP}} \mathbb{I}(\hat{Y}_i=1, Y_i=0) \right]$$
- **Expected Cost Reduction (ECR %):** Percentage reduction in total loss relative to unassisted automated inspection.
- **Review Capacity Utilization (RCU):** Percentage of allocated review budget $K$ actively consumed by items with non-zero estimated review benefit ($\Delta L > 0$).

### 5.4 Probability Calibration Reliability
- **Expected Calibration Error (ECE):** Bin-weighted average difference between predicted confidence and empirical accuracy across $M = 10$ bins:
  $$\text{ECE} = \sum_{m=1}^M \frac{|B_m|}{N} \left| \text{acc}(B_m) - \text{conf}(B_m) \right|$$
- **Brier Score:** Mean squared error of calibrated probability estimates:
  $$\text{Brier} = \frac{1}{N} \sum_{i=1}^N (\hat{p}_i - y_i)^2$$

### 5.5 Computational Latency and Runtime Overhead
- **Feature Extraction Time:** Milliseconds per image for backbone forward pass.
- **Index Query Time:** Milliseconds for FAISS nearest-neighbor retrieval.
- **Triage & Allocation Latency:** Milliseconds to compute probability calibration and execute global sort over a batch of $N = 1,000$ specimens.
- **Memory Footprint:** Peak RAM and VRAM consumption during inference.

---

## 6. Human Review Modeling

To reflect industrial reality, the benchmark evaluates selective policies under two human inspection modes:

### Mode A: Gold-Standard Human Review (Theoretical Ceiling)
- Inspector sensitivity $p_{\text{sens}} = 1.0$, specificity $p_{\text{spec}} = 1.0$.
- Any specimen reviewed by human is categorized with $100\%$ accuracy at cost $c_{\text{rev}}$.

### Mode B: Synthetic Imperfect Human Inspector Sweeps
- Human accuracy is modeled as a stochastic Bernoulli trial:
  $$P(Y_H = 1 \mid Y = 1) = p_{\text{sens}}, \quad P(Y_H = 0 \mid Y = 0) = p_{\text{spec}}$$
- Parameter Grid Sweeps:
  - Sensitivity: $p_{\text{sens}} \in \{0.80, 0.85, 0.90, 0.95, 0.98\}$
  - Specificity: $p_{\text{spec}} \in \{0.85, 0.90, 0.95, 0.98, 0.99\}$
- Analysis Goal: Determine the critical tipping point $(p^*_{\text{sens}}, p^*_{\text{spec}})$ where selective review ceases to provide positive economic return.

---

## 7. Statistical Significance and Replication Protocol

1. **Repeated Cross-Validation:** 5-fold cross-validation with 5 random initialization seeds per category (total 25 runs per experimental configuration).
2. **Hypothesis Testing:**
   - Paired Wilcoxon signed-rank tests for pairwise policy comparisons (e.g., BL6 vs. BL2).
   - Bonferroni-Holm correction for family-wise error rate control across multiple budgets and cost ratios.
   - Bootstrapped $95\%$ confidence intervals ($B = 1,000$ bootstrap replicates) for all reported ECR and DER values.
