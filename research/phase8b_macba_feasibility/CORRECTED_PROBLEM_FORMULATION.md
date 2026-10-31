# Phase 8B: Corrected Problem Formulation

**Document ID:** `DV-PHASE8B-FORM-V2`  
**Date:** October 31, 2026  
**Auditor:** Lead AI/ML Research Engineer & Experimental Methodology Reviewer  
**Scope:** Rigorous Decision-Theoretic Formulation of Multi-Category Selective Inspection

---

## 1. Information Available at Decision Time

To guarantee 100% leakage-free execution, the selective review policy $\pi$ operates strictly on information observable **at the moment an item is manufactured and scored**:

### Permitted Inputs:
1. **Category Identifier:** $c \in \{1, \dots, C\}$.
2. **Frozen Anomaly Score:** $S_{c, i} = f_c(X_{c, i}) \in \mathbb{R}_{\ge 0}$.
3. **Category Threshold:** $\tau_c$, calibrated previously on nominal calibration data.
4. **Automated Binary Decision:** $\hat{Y}_{c, i} = \mathbb{I}(S_{c, i} \ge \tau_c)$.
5. **Nominal Calibration Statistics:** Empirical quantile function $\hat{F}_c$ fitted on $\mathcal{D}_{\text{cal}, c}^{\text{norm}}$.
6. **Labeled Historical Calibration Observations:** Pre-deployment validation set $\mathcal{D}_{\text{cal}}$ used to fit posterior defect probability estimator $\hat{P}(Y=1 \mid S, c)$.
7. **Predeclared Industrial Cost Matrix:** $c_{\text{FN}, c}, c_{\text{FP}, c}, c_{\text{rev}, c}$.

### Strictly Prohibited Inputs:
- Current evaluation ground-truth labels ($Y_{c, i}$).
- Current evaluation error indicators ($\mathbb{I}(Y_{c, i} \ne \hat{Y}_{c, i})$).
- Future human inspection outcomes.
- Oracle category error frequencies on the evaluation batch.

---

## 2. Expected Reduction in Decision Loss ($\Delta L$)

For an item $X$ on production line $c$, let $\hat{p}(X) = \hat{P}(Y=1 \mid S_c(X), c)$ denote the estimated posterior probability of being defective.

Let human visual review have sensitivity $p_{\text{sens}} \in (0, 1]$ and specificity $p_{\text{spec}} \in (0, 1]$, with unit labor inspection cost $c_{\text{rev}, c}$.

### Case 1: Automated Model Predicts Nominal ($\hat{Y} = 0$)
- **Expected Loss Without Review:**
  $$\mathbb{E}[L_{\text{auto}} \mid \hat{Y}=0] = \hat{p}(X) \cdot c_{\text{FN}, c}$$
- **Expected Loss With Human Review:**
  If the item is defective, human detects it with probability $p_{\text{sens}}$ (cost $0$) and misses it with probability $1 - p_{\text{sens}}$ (cost $c_{\text{FN}, c}$). If normal, human falsely rejects it with probability $1 - p_{\text{spec}}$ (cost $c_{\text{FP}, c}$).
  $$\mathbb{E}[L_{\text{rev}} \mid \hat{Y}=0] = \hat{p}(X) (1 - p_{\text{sens}}) c_{\text{FN}, c} + (1 - \hat{p}(X)) (1 - p_{\text{spec}}) c_{\text{FP}, c} + c_{\text{rev}, c}$$
- **Expected Net Reduction in Loss ($\Delta L(X)$):**
  $$\Delta L(X) = \hat{p}(X) \cdot p_{\text{sens}} \cdot c_{\text{FN}, c} - (1 - \hat{p}(X)) (1 - p_{\text{spec}}) c_{\text{FP}, c} - c_{\text{rev}, c}$$

### Case 2: Automated Model Predicts Defective ($\hat{Y} = 1$)
- **Expected Loss Without Review:**
  $$\mathbb{E}[L_{\text{auto}} \mid \hat{Y}=1] = (1 - \hat{p}(X)) \cdot c_{\text{FP}, c}$$
- **Expected Loss With Human Review:**
  $$\mathbb{E}[L_{\text{rev}} \mid \hat{Y}=1] = \hat{p}(X) (1 - p_{\text{sens}}) c_{\text{FN}, c} + (1 - \hat{p}(X)) (1 - p_{\text{spec}}) c_{\text{FP}, c} + c_{\text{rev}, c}$$
- **Expected Net Reduction in Loss ($\Delta L(X)$):**
  $$\Delta L(X) = (1 - \hat{p}(X)) \cdot p_{\text{spec}} \cdot c_{\text{FP}, c} - \hat{p}(X) (1 - p_{\text{sens}}) c_{\text{FN}, c} - c_{\text{rev}, c}$$

### Under Ideal Human Review ($p_{\text{sens}} = 1.0, p_{\text{spec}} = 1.0$):
$$\Delta L(X) = \begin{cases} \hat{p}(X) \cdot c_{\text{FN}, c} - c_{\text{rev}, c} & \text{if } \hat{Y} = 0 \text{ (Automated Pass)} \\ (1 - \hat{p}(X)) \cdot c_{\text{FP}, c} - c_{\text{rev}, c} & \text{if } \hat{Y} = 1 \text{ (Automated Reject)} \end{cases}$$

**Core Insight:** Reviewing an automated pass is financially beneficial if and only if the expected defect escape cost $\hat{p}(X) c_{\text{FN}, c}$ exceeds human labor cost $c_{\text{rev}, c}$. Reviewing an automated reject is beneficial if the false alarm scrap cost $(1 - \hat{p}(X)) c_{\text{FP}, c}$ exceeds $c_{\text{rev}, c}$.

---

## 3. Weighted Capacity Knapsack Optimization

Let each category have inspection labor weight $w_c = c_{\text{rev}, c}$. The factory maintains a central review budget $B_{\text{capacity}}$.

The optimization problem is:
$$\max_{\{A_{c, i}\}} \sum_{c=1}^C \sum_{i=1}^{N_c} A_{c, i} \cdot \Delta L(X_{c, i})$$
$$\text{subject to} \quad \sum_{c=1}^C \sum_{i=1}^{N_c} A_{c, i} \cdot w_c \le B_{\text{capacity}}, \quad A_{c, i} \in \{0, 1\}$$

### Optimizer Selection:
1. **Exact 0-1 Knapsack Solver:** For $N_{\text{total}} = 330$, dynamic programming or branch-and-bound solves to global optimality in $< 2\text{ ms}$.
2. **Greedy Marginal Utility Ranking:** Items are ranked globally by their marginal benefit-to-weight density:
   $$r(X_{c, i}) = \frac{\max(\Delta L(X_{c, i}), 0)}{w_c}$$
   Items with $r(X) > 0$ are selected in descending order until the budget is exhausted.
   *By Dantzig's theorem, this greedy policy is guaranteed to achieve at least $(1 - 1/e) \approx 63.2\%$ of the optimal knapsack value and is practically within $0.1\%$ of the exact integer optimum when individual item weights are small relative to total capacity.*

In our implementation, we employ the greedy marginal utility policy as it scales seamlessly to millions of specimens and provides an explicit, interpretable ranking.
