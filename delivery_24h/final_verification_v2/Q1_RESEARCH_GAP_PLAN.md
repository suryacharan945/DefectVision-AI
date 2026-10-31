# Q1 RESEARCH GAP CLOSURE & JOURNAL ROADMAP

**Project:** DefectVision AI  
**Audit Date:** October 31, 2026  
**Auditor:** Lead AI/ML Verification & Full-Stack Release Engineer  
**Release Target:** Commit `91d3743` / `delivery_24h`  
**Target Publication Venues:** IEEE Transactions on Industrial Informatics (T-II), Machine Vision and Applications (MVA), or Pattern Recognition (PR)

---

## 1. Executive Summary

The previous release verification established that while DefectVision AI is an operational software prototype, its proposed scientific contribution—*Calibrated Patch-Neighborhood Dispersion (CPND) for selective human review in PatchCore*—exists only as an unverified concept. The reported $48.0\%$ error capture at $10\%$ review budget was derived from supervised margin sampling on EfficientNet-B0 rather than an unsupervised anomaly detection mechanism.

This document outlines the **concrete, reproducible research roadmap** required to implement, calibrate, and validate genuine CPND, resolve benchmark data leakage, and produce a submission-ready manuscript for a reputable Q1 computer vision or industrial informatics journal.

---

## 2. Identified Research Gaps & Required Solutions

```
+---------------------------------------------------------------------------------------------------+
| GAP 1: Theoretical & Algorithmic Absence of CPND                                                 |
| Status: Code does not exist; prior metrics derived from supervised margin heuristic.               |
| Solution: Formulate, implement, and calibrate CPND directly within the FAISS PatchCore pipeline.  |
+---------------------------------------------------------------------------------------------------+
                                              |
                                              v
+---------------------------------------------------------------------------------------------------+
| GAP 2: Benchmark Historical Exposure (MVTec 856 Split)                                            |
| Status: The 856-image split was exposed during early development runs.                            |
| Solution: Evaluate on external, unexposed benchmarks: VisA (10,821 images) and BTAD (2,830 images).|
+---------------------------------------------------------------------------------------------------+
                                              |
                                              v
+---------------------------------------------------------------------------------------------------+
| GAP 3: Narrow Baseline Comparison                                                                 |
| Status: Prior work lacked comparison with established selective classification literature.        |
| Solution: Benchmark against Geifman & El-Yaniv Risk-Coverage, Deep Ensembles, and Conformal Sets. |
+---------------------------------------------------------------------------------------------------+
                                              |
                                              v
+---------------------------------------------------------------------------------------------------+
| GAP 4: Chukyo Dataset Duplication & Temporal Leakage                                              |
| Status: 25 duplicate similarity pairs and 14 identical frame captures in cold storage.             |
| Solution: Run perceptual hash deduplication; publish as an independent "real-world edge" study.   |
+---------------------------------------------------------------------------------------------------+
```

---

## 3. Mathematical Formulation of Calibrated Patch-Neighborhood Dispersion (CPND)

To convert the theoretical proposal into an executable algorithm, CPND must be formalized within the PatchCore memory bank retrieval space:

### 3.1. Standard PatchCore Formulation
Let an input image $X$ generate a spatial grid of patch feature embeddings:
$$\mathcal{P}(X) = \{m_1, m_2, \dots, m_N\}, \quad m_i \in \mathbb{R}^D$$
Let $\mathcal{M} = \{v_1, \dots, v_M\}$ denote the coreset memory bank containing nominal patch features sampled from normal training images.

The standard PatchCore anomaly score for patch $m_i$ is its distance to its nearest neighbor in $\mathcal{M}$:
$$d(m_i, \mathcal{M}) = \min_{v \in \mathcal{M}} \|m_i - v\|_2$$
The image-level anomaly score is given by:
$$S(X) = \max_{m_i \in \mathcal{P}(X)} d(m_i, \mathcal{M})$$

### 3.2. Formulating Patch-Neighborhood Dispersion (PND)
Standard PatchCore considers only the single nearest neighbor ($k=1$), making it vulnerable to boundary noise and isolated outliers in the memory bank. 

For the maximally anomalous patch $m^* = \arg\max_{m_i} d(m_i, \mathcal{M})$, we query its top-$K$ nearest neighbors in $\mathcal{M}$:
$$\mathcal{N}_K(m^*) = \{v_{(1)}, v_{(2)}, \dots, v_{(K)}\}, \quad \text{where } \|m^* - v_{(1)}\|_2 \le \dots \le \|m^* - v_{(K)}\|_2$$
Let $d_{(j)} = \|m^* - v_{(j)}\|_2$ denote the distance to the $j$-th neighbor.

We define the **Patch-Neighborhood Dispersion (PND)** as the normalized variance of the neighbor distance profile:
$$\text{PND}(X) = \frac{\sqrt{\frac{1}{K}\sum_{j=1}^K \left(d_{(j)} - \bar{d}_K\right)^2}}{\bar{d}_K}, \quad \text{where } \bar{d}_K = \frac{1}{K}\sum_{j=1}^K d_{(j)}$$

- **High Confidence Defect:** All $K$ neighbors are distant, but cluster uniformly far from $m^* \implies$ Low dispersion, high certainty of defect.
- **High Confidence Normal:** All $K$ neighbors are tightly surrounding $m^* \implies$ Low dispersion, high certainty of normality.
- **High Epistemic Uncertainty (Decision Boundary):** $m^*$ lies near the boundary of the normal manifold where neighbor distances rapidly diverge $\implies$ High dispersion.

### 3.3. Calibration via Conformal Non-Conformity
To map raw PND to a calibrated uncertainty metric $U(X) \in [0, 1]$, compute the empirical cumulative distribution function (ECDF) on held-out normal validation patches:
$$U(X) = F_{\text{val}}\left(\text{PND}(X)\right) = \frac{1}{|\mathcal{D}_{\text{val}}|} \sum_{Z \in \mathcal{D}_{\text{val}}} \mathbf{1}\left(\text{PND}(Z) \le \text{PND}(X)\right)$$
Under a bounded human inspection budget $B \in (0, 1]$, the system flags the top $\lfloor B \cdot N_{\text{total}} \rfloor$ samples ranked by $U(X)$ for manual review.

---

## 4. Experimental Protocol & Required Benchmarks

To meet Q1 review standards, the experimental evaluation must be expanded beyond MVTec AD:

### 4.1. Benchmark Datasets
1. **MVTec AD (15 Categories, 5,354 images):** The de facto standard. Evaluate on the official 1,725-image test set using strict cross-validation on the train split to set thresholds.
2. **VisA Dataset (12 Categories, 10,821 images):** Complex industrial visual anomaly detection with multiple instances, complex textures, and non-rigid deformations.
3. **BTAD (BeanTech Anomaly Detection, 3 Categories, 2,830 images):** Real industrial manufacturing defects on industrial inspection lines.

### 4.2. Baseline Methods for Selective Anomaly Review
The paper must rigorously benchmark CPND against existing selective classification paradigms:

1. **Random Human Review (Baseline 0):** Uniform sampling.
2. **Top Anomaly Score (Baseline 1):** $\text{Rank by } S(X)$.
3. **Boundary Margin / Distance to Threshold (Baseline 2):** $\text{Rank by } |S(X) - \tau_c|$.
4. **Deep Ensemble Variance (Baseline 3):** Variance across 5 diverse feature extractors (ResNet-50, EfficientNet, WideResNet, ConvNeXt, Swin).
5. **Monte Carlo Feature Dropout (Baseline 4):** Latent embedding dispersion under test-time stochastic dropout.
6. **Risk-Coverage Curve (Geifman & El-Yaniv, NeurIPS 2017):** Evaluate selective risk $\mathcal{R}(f, g)$ as coverage $\phi(g)$ varies from $100\%$ down to $80\%$ ($20\%$ review budget).

### 4.3. Primary Evaluation Metrics
- **Selective Defect Escape Rate (DER@B):** Defect escape rate at review budget $B \in \{1\%, 5\%, 10\%, 20\%\}$.
- **Error Capture Efficiency (ECE@B):** Percentage of total machine misclassifications captured divided by review budget $B$.
- **Area Under the Risk-Coverage Curve (AURC):** Measures overall quality of uncertainty ranking across all operational budgets.

---

## 5. Four-Week Research Implementation Schedule

```
+-------------------------------------------------------------------------------+
| WEEK 1: CPND ALGORITHM IMPLEMENTATION & SANITY VERIFICATION                   |
| - Implement FAISS k-NN dispersion query in `models/patchcore_uncertainty.py`  |
| - Validate on MVTec `bottle` and `metal_nut` splits                          |
| - Verify computational overhead (target: <= 15ms per image CPU overhead)      |
+-------------------------------------------------------------------------------+
                                       |
                                       v
+-------------------------------------------------------------------------------+
| WEEK 2: FULL EXPERIMENTATION ON MVTEC AD & VISA DATASETS                      |
| - Execute 15-category MVTec AD selective review across all 4 baselines        |
| - Run 12-category VisA benchmark                                             |
| - Generate Risk-Coverage curves and Pareto frontier plots                     |
+-------------------------------------------------------------------------------+
                                       |
                                       v
+-------------------------------------------------------------------------------+
| WEEK 3: ABLATION STUDIES & STATISTICAL SIGNIFICANCE                           |
| - Ablate neighbor count $K \in \{3, 5, 10, 20, 50\}$                          |
| - Test sensitivity to memory bank subsampling rates (1%, 5%, 10%)             |
| - Run Wilcoxon signed-rank significance tests against boundary margin         |
+-------------------------------------------------------------------------------+
                                       |
                                       v
+-------------------------------------------------------------------------------+
| WEEK 4: MANUSCRIPT PREPARATION & REPRODUCIBILITY PACKAGING                    |
| - Write manuscript following IEEE T-II / Pattern Recognition template         |
| - Package Docker environment with automated evaluation scripts and data hashes|
| - Submit to peer review                                                       |
+-------------------------------------------------------------------------------+
```

---

## 6. Chukyo Dataset Resolution Strategy

To utilize the external Chukyo dataset ethically:
1. **Deduplication:** Run perceptual hashing (`imagehash.phash`) with Hamming distance threshold $\le 2$ to eliminate the 14 identical capture pairs.
2. **Cluster Grouping:** Group images by physical inspection batch to prevent temporal autocorrelation across splits.
3. **Paper Role:** Frame Chukyo as a **"Real-World Factory Deployment Case Study"** demonstrating domain shift adaptation, distinct from the primary controlled benchmark experiments.
