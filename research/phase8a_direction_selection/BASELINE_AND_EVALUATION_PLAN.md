# Phase 8A: Baseline & Evaluation Plan

**Document ID:** `DV-PHASE8A-PLAN-V1`  
**Date:** October 31, 2026  
**Auditor:** Lead AI/ML Research Engineer & Experimental Methodology Reviewer  
**Scope:** Multi-Category Selective Inspection Baselines, Experimental Matrix, and Statistical Verification Plan

---

## 1. Candidate Baselines Architecture

To rigorously evaluate the proposed **Category-Aware Multi-Line Budget Allocation (Direction B)**, we benchmark against a comprehensive hierarchy of simple, practical, and published baselines. All baselines operate on the **identical set of evaluated images, identical PatchCore anomaly scores, identical category thresholds, and identical total factory review budget $B_{\text{total}}$**.

```
+--------------------------------------------------------------------------------------------------------+
|                                  BASELINE ALLOCATION HIERARCHY                                         |
+--------------------------------------------------------------------------------------------------------+
|  Level 1: Uncalibrated Global Pooling (Current Common Industry Practice)                               |
|    • BL1: Global Pooled Top Anomaly Score (Pool raw S_c(X) across all lines, take top B_total)         |
|    • BL2: Global Pooled Distance-to-Threshold (Pool |S_c(X) - tau_c| globally, take smallest B_total)  |
|                                                                                                        |
|  Level 2: Heuristic Category Budget Partitioning                                                       |
|    • BL0: Uniform Category Split (K_c = B_total / C; rank within category by |S_c - tau_c|)            |
|    • BL3: Volume-Proportional Allocation (K_c = B_total * (N_c / N_total))                            |
|    • BL4: Historical Error-Rate Proportional Allocation (K_c = B_total * (pi_c / sum pi_j))           |
|                                                                                                        |
|  Level 3: Conformal Quantile Normalization                                                             |
|    • BL5: Global Conformal Non-Conformity Triage (Standardize scores via nominal p-values, rank globally)|
|                                                                                                        |
|  Level 4: Proposed Optimal Knapsack / Marginal Utility Allocation                                      |
|    • Proposed Method (MACBA): Multi-Category Adaptive Cost-Weighted Budget Allocation                  |
+--------------------------------------------------------------------------------------------------------+
```

---

## 2. Formal Baseline Specifications

### 2.1. Baseline 1: Global Pooled Top-Score Review (BL1)
- **Mechanism:** Pool raw anomaly scores across all categories: $\mathcal{S} = \{S_{c, i} \mid \forall c, i\}$. Sort all $N_{\text{total}}$ items descending by $S_{c, i}$ and select top $B_{\text{total}}$ items.
- **Flaw:** High-scale categories (e.g. `capsule` where scores exceed $3.0$) completely starve low-scale categories (e.g. `bottle` where scores peak at $2.1$). Severe defect items in low-scale lines receive zero review.

### 2.2. Baseline 2: Global Pooled Distance-to-Threshold Review (BL2)
- **Mechanism:** Compute scalar boundary distance $d_{c, i} = |S_{c, i} - \tau_c|$. Pool all distances globally, sort ascending, and select smallest $B_{\text{total}}$ items.
- **Flaw:** Implicitly assumes that a margin of $0.05$ on category A carries the identical error probability and defect consequence as a margin of $0.05$ on category B. Ignores disparate manifold density and disparate defect costs.

### 2.3. Baseline 0: Uniform Category Split (BL0)
- **Mechanism:** Assign each category an identical slice of the human workforce:
  $$K_c = \left\lfloor \frac{B_{\text{total}}}{C} \right\rfloor$$
  Within each category, items are ranked by $|S_{c, i} - \tau_c|$ ascending.
- **Flaw:** Inflexible. Allocates equal human inspector hours to a nearly zero-defect line (e.g. `bottle`) as to a high-error difficult line (e.g. `capsule`).

### 2.4. Baseline 3: Volume-Proportional Allocation (BL3)
- **Mechanism:** Allocate review budget proportionally to production throughput:
  $$K_c = \left\lfloor B_{\text{total}} \times \frac{N_c}{N_{\text{total}}} \right\rfloor$$
- **Flaw:** Allocates budget to high-volume production lines even if the automated detector is $100\%$ accurate on that line, wasting inspector labor.

### 2.5. Baseline 4: Historical Error-Rate Proportional Allocation (BL4)
- **Mechanism:** Based on pre-deployment validation estimates of error rates $\hat{\pi}_c$:
  $$K_c = \left\lfloor B_{\text{total}} \times \frac{\hat{\pi}_c}{\sum_{j=1}^C \hat{\pi}_j} \right\rfloor$$
- **Flaw:** Static; does not account for the shape of the boundary error distribution on each line.

### 2.6. Proposed Method: Multi-Category Adaptive Cost-Weighted Budget Allocation (MACBA)
- **Mechanism:**
  1. Map scores to calibrated non-conformity percentiles using nominal calibration sets.
  2. Estimate the marginal error density / marginal expected cost reduction curve $\Delta \text{Cost}_c(k)$ for each line $c$ as a function of allocated reviews $k$.
  3. Solve the bounded knapsack resource allocation via dynamic programming or greedy marginal utility selection:
     $$\mathbf{K}^* = \arg\max_{\mathbf{K}} \sum_{c=1}^C \Delta \text{Cost}_c(K_c) \quad \text{s.t.} \quad \sum_{c=1}^C K_c \le B_{\text{total}}$$
  4. Within each category, review the top $K_c^*$ items ranked by cost-weighted boundary proximity.

---

## 3. Evaluation Matrix & Experimental Protocols

### 3.1. Review Budget Grid
Evaluate all methods at fixed global budget fractions:
$$B_{\text{frac}} \in \{0.01, 0.02, 0.05, 0.10, 0.15, 0.20\}$$
corresponding to $1\%$ to $20\%$ of total factory production.

### 3.2. Cost Asymmetry Configurations
Ablate across realistic industrial cost ratios:
- **Symmetric Baseline:** $\lambda = 1$ ($c_{\text{FN}} = c_{\text{FP}} = 10, c_{\text{rev}} = 1$)
- **Mild Industrial Asymmetry:** $\lambda = 5$ ($c_{\text{FN}} = 50, c_{\text{FP}} = 10, c_{\text{rev}} = 1$)
- **Standard Industrial Asymmetry:** $\lambda = 20$ ($c_{\text{FN}} = 200, c_{\text{FP}} = 10, c_{\text{rev}} = 1$)
- **Extreme High-Stakes Asymmetry (Aerospace/Pharma):** $\lambda = 100$ ($c_{\text{FN}} = 1000, c_{\text{FP}} = 10, c_{\text{rev}} = 1$)
- **Heterogeneous Line Costs:** Different lines carry different costs (e.g. `capsule` $\lambda = 50$, `bottle` $\lambda = 10$, `metal_nut` $\lambda = 25$).

### 3.3. Human Inspector Models
- **Ideal Human Reviewer:** $p_{\text{human}} = 1.0$ (100% sensitivity, 100% specificity).
- **Realistic Imperfect Human:** $p_{\text{human}} = 0.95$ sensitivity, $0.98$ specificity (simulating inspection fatigue and perceptual limits).

---

## 4. Statistical Verification & Significance Plan

1. **Paired Multi-Category Bootstrap:**
   - Resample entire evaluation sets across all categories simultaneously using $B = 2,000$ paired bootstrap iterations.
   - For every candidate vs. baseline pair, compute empirical distribution of $\Delta \text{MC-ECR}$ and $\Delta \text{Cost}$.
   - Report exact 95% Confidence Intervals for the paired differences: $[\text{CI}_{\text{low}}(\Delta), \text{CI}_{\text{high}}(\Delta)]$.
2. **Non-Parametric Hypothesis Testing:**
   - Execute paired Wilcoxon signed-rank test across bootstrap replicates and budget tiers.
   - Enforce significance threshold $\alpha = 0.05$ with Holm-Bonferroni correction for multiple comparisons.
