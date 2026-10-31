# Phase 8A: Candidate Research Direction Comparison

**Document ID:** `DV-PHASE8A-COMP-V1`  
**Date:** October 31, 2026  
**Auditor:** Lead AI/ML Research Engineer & Experimental Methodology Reviewer  

---

## 1. Candidate Direction Definitions

### Candidate Direction A:
**Cost-Sensitive Selective Inspection with Explicit Asymmetric Consequences**
- *Focus:* Optimize human review triage for a single production line under explicit financial penalties for missed defects ($c_{\text{FN}}$), false alarms ($c_{\text{FP}}$), and human audit labor ($c_{\text{rev}}$), where $c_{\text{FN}} \gg c_{\text{FP}} > c_{\text{rev}}$.
- *Core Mechanism:* Cost-weighted risk-coverage trade-off curves and optimal triage band selection without defect training data.

### Candidate Direction B:
**Category-Aware Review-Budget Allocation Across Multiple Industrial Product Types**
- *Focus:* Solve the shared-workforce factory inspection problem: given $C$ heterogeneous production lines (different products, baseline error rates, score distributions, and defect costs) and a global plant human review budget $B_{\text{total}} = \sum_c K_c \le B$, determine the optimal allocation vector $\mathbf{K}^* = (K_1^*, \dots, K_C^*)$.
- *Core Mechanism:* Multi-category resource allocation via marginal utility knapsack optimization and multi-task conformal calibration, resolving score incommensurability across categories.

### Candidate Direction C:
**Robust Inspection Allocation Under Distributional and Domain Shift**
- *Focus:* Design triage policies that remain stable when sensor drift, lighting variations, or camera position shifts degrade the nominal feature distribution.
- *Core Mechanism:* Minimax risk control under bounded Wasserstein/distributional uncertainty balls.

---

## 2. Systematic Evaluation Across the 9 Pre-Registered Criteria

| Evaluation Criterion | Candidate Direction A (Cost-Sensitive Single-Line) | Candidate Direction B (Multi-Category Budget Allocation) | Candidate Direction C (Domain Shift Robustness) |
| :--- | :--- | :--- | :--- |
| **1. Actual Novelty Gap** | **Moderate.** While asymmetric costs in one-class AD are rarely evaluated, scalar cost-weighted thresholding is well-studied in classical decision theory (Chow 1970). | **Very High.** No published work in CVPR/ECCV/IJCV or IEEE T-II addresses how to partition a shared factory review budget across concurrent, heterogeneous AD lines. | **Moderate.** Covariate shift is heavily studied in general ML, but specific triage formulations in industrial AD are niche. |
| **2. Technical Complexity** | **Low to Moderate.** Parameterized scalar search over decision margins for a single ROC curve. | **Moderate to High.** Formulated as a constrained resource allocation / knapsack problem with non-convex empirical risk curves and calibration scaling. | **Very High.** Requires distributional uncertainty set modeling, minimax optimization, or perturbation bounds. |
| **3. Available Development Data** | **High.** Fully supported by the 330 development images in `dev_extracted_scores.csv`. | **High.** Perfect alignment with the 3 development categories (`bottle`, `capsule`, `metal_nut` with 83, 132, 115 images and disparate error rates: 1.2%, 43.9%, 2.6%). | **Low.** Current development data has zero natural physical domain shifts; requires artificial synthetic perturbations. |
| **4. Need for Labeled Calibration Data** | **Moderate.** Requires a small set of validation errors or defect priors $\pi_c$ to calibrate cost curves. | **Low to Moderate.** Operates using nominal calibration sets (readily available) to align quantile score scales, plus empirical error priors. | **High.** Requires domain-shifted validation splits to estimate shift bounds without test leakage. |
| **5. Generalization Potential** | **Moderate.** Evaluated category by category; each line is solved independently. | **Extremely High.** Directly evaluates across all 11 held-out VisA categories in a realistic factory-wide simulation. | **Moderate.** Risk of overfitting to specific synthetic perturbation types (e.g. Gaussian noise). |
| **6. Compute & Storage Requirements** | **Minimal.** Fractions of a millisecond on pre-extracted scalar scores. | **Minimal.** Integer knapsack or convex resource allocation solves in $< 5\text{ ms}$ on scalar score tables. | **High.** May require re-running inference across multiple corrupted image sets. |
| **7. Required Baselines** | Random, Top-Score, Distance-to-Threshold, Fixed Cost-Weighted Threshold. | **Strong & Realistic:**<br>1. Uniform Allocation ($K_c = B/C$)<br>2. Global Pooled Score Triage (Naive)<br>3. Global Pooled Distance Triage<br>4. Volume-Proportional Allocation<br>5. Defect-Prior-Proportional Allocation. | Standard empirical risk minimization under corruptions, robust thresholding. |
| **8. Ablation Feasibility** | **High.** Ablate cost ratios $c_{\text{FN}}/c_{\text{FP}} \in \{5, 10, 20, 50, 100\}$. | **Very High.** Ablate budget levels ($1\%$ to $20\%$), cost homogeneity vs heterogeneity, quantile vs marginal gain allocation, known vs estimated priors. | **Low.** Difficult to define non-arbitrary shift intensities. |
| **9. Research Risk** | **Medium.** Reviewers may dismiss it as a standard cost-parameter sweep on existing ROC curves. | **Low.** Highly defensible, mathematically grounded, and solves an undeniable real-world industry problem. Excellent fit for *IEEE Transactions on Industrial Informatics*. | **High.** Reviewers frequently reject papers relying on artificial synthetic corruptions for industrial validation. |

---

## 3. Comparative Synthesis & Ranking

1. **Direction B (Multi-Category Budget Allocation) ranks #1:**
   - Possesses the strongest and most distinct literature gap (resolving the "isolated category fallacy" of all existing benchmarks).
   - Can seamlessly integrate Candidate A's cost-sensitivity as a category-specific cost matrix ($c_{\text{FN}, c}, c_{\text{FP}, c}, c_{\text{rev}, c}$).
   - 100% executable on frozen scalar prediction tables without retraining or downloading external data.
   - Ideal alignment with the 11 untouched VisA categories when the protocol is eventually unblinded.
2. **Direction A (Cost-Sensitive Single-Line) ranks #2:**
   - Feasible, but on its own lacks sufficient novelty for a top-tier Q1 journal because single-line cost curves are well-known. Best utilized as an integral component within Direction B.
3. **Direction C (Domain Shift Robustness) ranks #3:**
   - Rejected due to severe data limitations (no real multi-domain industrial datasets available locally) and high risk of artificiality.

---

## 4. Recommendation Preview

**Direction B (Category-Aware Review-Budget Allocation Across Multiple Industrial Product Types)** is unequivocally recommended as the sole viable, high-novelty research direction.
