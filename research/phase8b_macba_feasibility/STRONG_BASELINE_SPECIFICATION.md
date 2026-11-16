# Phase 8B: Strong Baseline Specification

**Document ID:** `DV-PHASE8B-BASE-V1`  
**Date:** October 31, 2026  
**Auditor:** Lead AI/ML Research Engineer & Experimental Methodology Reviewer  
**Scope:** Formal Mathematical Specification of the 8 Benchmark Allocation Policies

---

## 1. Baseline Hierarchy Overview

To ensure the proposed method is evaluated against rigorous, competitive benchmarks rather than weak strawmen, we implement a strict 8-level baseline hierarchy:

| Baseline ID | Name | Allocation Logic | Ranking Within Allocated Quota | Key Theoretical Premise |
| :--- | :--- | :--- | :--- | :--- |
| **BL0** | Uniform Category Split | $K_c = \lfloor B / C \rfloor$ | $|S_c(X) - \tau_c|$ ascending | Equal resource distribution across lines. |
| **BL1** | Volume-Proportional | $K_c = \lfloor B \cdot (N_c / N) \rfloor$ | $|S_c(X) - \tau_c|$ ascending | Larger production volume gets larger review budget. |
| **BL2** | Global Pooled Raw Distance | Global pooled sort | $|S_c(X) - \tau_c|$ ascending | Boundary proximity is scale-invariant across lines. |
| **BL3** | Global Category-Normalized Distance | Global pooled sort | $\frac{\|S_c(X) - \tau_c\|}{\tau_c}$ ascending | Resolves threshold scale disparity across lines. |
| **BL4** | Historical Error-Rate Allocation | $K_c \propto \hat{\pi}_c^{\text{cal}}$ | $|S_c(X) - \tau_c|$ ascending | Line error frequency dictates inspection quotas. |
| **BL5** | Calibrated Error-Risk Ranking | Global pooled sort | $\hat{P}(\text{Error} \mid X)$ descending | Probabilistic risk matching across lines. |
| **BL6** | Simple Cost-Weighted Risk | Global pooled sort | $\hat{P}(\text{Error} \mid X) \cdot c_{\text{loss}, c}$ | Ranks by raw expected penalty. |
| **BL7** | Oracle Upper Bound | Global pooled sort | $\mathbb{I}(\text{Error}) \to$ random | Unattainable benchmark ceiling using true evaluation labels. |
| **Proposed** | **MACBA** | Greedy knapsack index | $\frac{\max(\Delta L(X), 0)}{c_{\text{rev}, c}}$ descending | Decision-theoretic expected loss reduction under capacity constraints. |

---

## 2. Mathematical Baseline Definitions

### 2.1. BL0: Uniform Category Allocation
- Review quota for line $c$:
  $$K_c = \left\lfloor \frac{B_{\text{total}}}{C} \right\rfloor$$
- Within category $c$, items are ranked by $|S_c(X) - \tau_c|$ ascending. Remaining fractional budget allocated by alphabetical category tie-breaking.

### 2.2. BL1: Volume-Proportional Allocation
- Review quota for line $c$:
  $$K_c = \left\lfloor B_{\text{total}} \times \frac{N_c}{N_{\text{total}}} \right\rfloor$$
- Within category $c$, items are ranked by $|S_c(X) - \tau_c|$ ascending.

### 2.3. BL2: Globally Pooled Raw Distance
- All specimens from all $C$ lines are pooled into a single global list.
- Ranked strictly by scalar distance $d_{c, i} = |S_{c, i} - \tau_c|$ ascending.
- Top $B_{\text{total}}$ items are audited.

### 2.4. BL3: Globally Pooled Category-Normalized Distance
- Distance normalized by category threshold to account for scale:
  $$d_{\text{norm}}(X_{c, i}) = \frac{|S_{c, i} - \tau_c|}{\tau_c}$$
- Ranked globally by $d_{\text{norm}}$ ascending; top $B_{\text{total}}$ items audited.

### 2.5. BL4: Historical Category Error-Rate Allocation
- Let $\hat{\pi}_c^{\text{cal}} = \frac{\sum_{j \in \mathcal{D}_{\text{cal}, c}} \mathbb{I}(\text{Error}_j)}{N_{\text{cal}, c}}$ be the calibration error frequency.
- Review quota:
  $$K_c = \left\lfloor B_{\text{total}} \times \frac{\max(\hat{\pi}_c^{\text{cal}}, 0.01)}{\sum_{m=1}^C \max(\hat{\pi}_m^{\text{cal}}, 0.01)} \right\rfloor$$
- Within category $c$, items are ranked by $|S_c(X) - \tau_c|$ ascending.

### 2.6. BL5: Calibrated Per-Image Error-Risk Ranking
- For each category $c$, fit a logistic calibration model on calibration split $\mathcal{D}_{\text{cal}}$:
  $$\hat{P}(\text{Error} \mid X) = \frac{1}{1 + \exp\left( -(\alpha_c + \beta_c \cdot |S_c(X) - \tau_c|) \right)}$$
- All items ranked globally by $\hat{P}(\text{Error} \mid X)$ descending.

### 2.7. BL6: Simple Cost-Weighted Error-Risk Ranking
- Let $c_{\text{loss}, c} = c_{\text{FN}, c}$ if $\hat{Y}=0$ else $c_{\text{FP}, c}$.
- Ranked globally by expected loss:
  $$\text{Score}(X) = \hat{P}(\text{Error} \mid X) \cdot c_{\text{loss}, c}$$

### 2.8. BL7: Oracle Allocation (Upper Bound)
- Routes all genuine model errors on the evaluation set ($\mathbb{I}(Y \ne \hat{Y}) = 1$) to human review first.
- Reported strictly as an unattainable theoretical upper bound.

### 2.9. Proposed Method: MACBA
- Evaluates decision-theoretic net loss reduction $\Delta L(X)$ (Section 2 of `CORRECTED_PROBLEM_FORMULATION.md`) incorporating human error rates ($p_{\text{sens}}, p_{\text{spec}}$) and inspection labor cost $c_{\text{rev}, c}$.
- Ranks globally by marginal utility density $r(X) = \frac{\max(\Delta L(X), 0)}{c_{\text{rev}, c}}$ descending.
