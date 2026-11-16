# Phase 8A: Research Gap Matrix

**Document ID:** `DV-PHASE8A-GAP-V1`  
**Date:** October 31, 2026  
**Auditor:** Lead AI/ML Research Engineer & Experimental Methodology Reviewer  
**Scope:** Systematic Gap Analysis Across Selective Classification, Learning to Defer, and Industrial Anomaly Detection

---

## 1. Systematic Gap Taxonomy

To identify a genuine Q1-journal research gap, we evaluate the interaction between three key research axes:
1. **Model Paradigm:** Supervised Multi-Class vs. Unsupervised One-Class.
2. **Loss Formulation:** Symmetric 0-1 Loss vs. Asymmetric Industrial Loss ($c_{\text{FN}} \gg c_{\text{FP}}$).
3. **Operational Scope:** Single-Task Isolated Evaluation vs. Multi-Category Shared-Budget Inspection.

```
+----------------------------------------------------------------------------------------------------+
|                                    RESEARCH GAP TAXONOMY MAP                                       |
+----------------------------------------------------------------------------------------------------+
|                                  Single-Category / Single-Task     Multi-Category / Multi-Line     |
|                                 +-------------------------------+--------------------------------+ |
| Supervised Multi-Class          | Geifman & El-Yaniv (2017)     | Multi-task Selective Learning  | |
| (Softmax Probabilities)         | Mozannar & Sontag (2020)      | (Rare, mostly medical queues)  | |
|                                 | Charoenphakdee et al. (2021)  |                                | |
|                                 +-------------------------------+--------------------------------+ |
| Unsupervised One-Class          | Isolated per-category tables  | >>> THE DEFECTVISION GAP <<<   | |
| (PatchCore, PaDiM, Distance)    | Roth et al. (PatchCore 2022)  | No published method addresses  | |
|                                 | Bergmann et al. (MVTec 2021)  | shared budget allocation across| |
|                                 | Zou et al. (VisA 2022)        | heterogeneous product lines!   | |
+---------------------------------+-------------------------------+--------------------------------+ |
```

---

## 2. Research Gap Comparison Matrix

| Evaluation Dimension | Gap in Direction A (Cost-Sensitive Single-Line) | Gap in Direction B (Multi-Category Budget Allocation) | Gap in Direction C (Domain Shift Robustness) |
| :--- | :--- | :--- | :--- |
| **Primary Literature Void** | Selective classification theory assumes 0-1 loss; industrial inspection requires $c_{\text{FN}} \gg c_{\text{FP}}$. However, single-line cost curves are well-known in classical decision theory (Chow 1970). | **Virtually 100% of AD benchmark papers report isolated per-category metrics.** No paper formulates how a factory allocates a single quality-control team across $C$ concurrent product lines with non-comparable scores. | Out-of-distribution detection under covariate shift is studied in vision (Hendrycks 2019), but selective triage adaptation is less explored. |
| **Technical Formulation** | Parameterize expected loss $\mathbb{E}[C] = c_{\text{FN}} \text{FN} + c_{\text{FP}} \text{FP} + c_{\text{rev}} K$ and solve for optimal scalar threshold band. | Formulate as a **Constrained Multi-Choice Knapsack / Marginal Utility Allocation Problem**: $\max_{\{K_c\}} \sum_c \Delta \text{Risk}_c(K_c)$ s.t. $\sum_c K_c \le B_{\text{total}}$. | Formulate minimax regret under bounded distributional divergence (Wasserstein or KL ball). |
| **Novelty Level** | Moderate. Theoretical formulation is clean, but boils down to scalar cost-weighted threshold selection on single lines. | **High to Very High.** Bridges industrial computer vision benchmarks with operational research / resource allocation. Directly addresses how manufacturing plants actually operate. | Moderate to High. Highly theoretical, but easily suffers from synthetic corruption artifacts (ImageNet-C style). |
| **Available Development Data** | Fully supported on 330 development images. | **Fully supported on existing multi-category development data** (`bottle`, `capsule`, `metal_nut` with 330 images, distinct baselines, and disparate error densities). | **Weak.** Requires simulated corruptions or unverified external domain splits, introducing artificiality. |
| **Risk of Methodological Rejection** | Medium. Reviewers may argue that single-line cost curves are standard cost-sensitive ROC analysis. | **Low.** Directly addresses the fundamental flaw of macro-averaged benchmark tables; high practical relevance for *IEEE Transactions on Industrial Informatics* (T-II). | High. Reviewers frequently criticize synthetic corruption benchmarks as unrepresentative of true physical drift. |

---

## 3. Key Findings of the Gap Analysis

1. **The Isolated Category Fallacy:** The greatest methodological blind spot in current industrial anomaly detection literature is that researchers evaluate models category-by-category in silos. In reality, a manufacturing plant does not hire a separate human inspector for bottles, another for capsules, and another for metal nuts. A pooled inspection team must allocate hours across all running lines.
2. **The Score Incommensurability Problem:** Raw PatchCore distance scores are non-comparable across categories (e.g. `bottle` normal threshold is $\tau = 1.85$, while `capsule` is $\tau = 2.40$, and feature spaces have completely different intrinsic dimensions and manifold curvatures). Naively pooling raw scores starves low-scale categories and floods high-scale categories with false alarms.
3. **Synergy of A and B:** Candidate Direction B naturally incorporates Candidate A: the objective function of multi-category budget allocation is precisely the **minimization of total multi-line financial risk** where each category carries its specific defect cost $c_{\text{FN}, c}$ and inspection cost $c_{\text{rev}, c}$.
