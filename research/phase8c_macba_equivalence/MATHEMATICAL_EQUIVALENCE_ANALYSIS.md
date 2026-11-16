# Phase 8C Deliverable: Mathematical Equivalence Analysis

**Project:** DefectVision AI — Advanced Quality Inspection Platform  
**Phase:** 8C (MACBA Equivalence & Novelty Gate)  
**Status:** COMPLETE & INDEPENDENTLY VERIFIED  
**Decision Gate Verdict:** STANDARD METHOD EQUIVALENCE  

---

## 1. Executive Summary

This document provides a formal mathematical analysis of the relationship between **Multi-Category Adaptive Cost-Weighted Budget Allocation (MACBA)** and conventional **Cost-Sensitive Bayes Risk Ranking** (Baseline BL6; Chow, 1970; Elkan, 2001; Charoenphakdee et al., 2021).

We evaluate whether MACBA's greedy knapsack formulation over decision-theoretic loss reduction $\Delta L(X)$ represents a genuinely distinct decision algorithm or is mathematically equivalent to conventional cost-weighted error risk ranking under standard operational assumptions.

### Key Analytical Findings:
1. **Mathematical Identity:** Under an additive linear loss function, a fixed review capacity constraint ($w_i = c_{\text{rev}} = 1$), and deterministic tie-breaking, MACBA's marginal utility ratio ordering is **strictly isomorphic** to ranking by expected cost-weighted error risk.
2. **Exact Rank Correlation:** When probability estimates are conditioned on the signed anomaly prediction $\hat{Y}$, the Spearman rank correlation between MACBA's marginal utility and BL6's risk score is **$\rho_s = 1.000000$** across all specimens.
3. **Identical Selection Permutations:** For every review budget $K \in \{1, \dots, N\}$ and cost ratio $\lambda \in \{1, 5, 20, 50, 100\}$, the set of specimens selected for human review by MACBA and properly formulated BL6 is **100.0% identical** ($\mathcal{S}_{\text{MACBA}} \equiv \mathcal{S}_{\text{BL6}}$).
4. **Theoretical Conclusion:** MACBA does not introduce a novel decision algorithm. Framing cost-sensitive classification as a knapsack problem with uniform item weights is a standard reformulation that yields zero algorithmic or operational difference.

---

## 2. Problem Formulation and Notation

Let a specimen be represented by feature representation $X \in \mathcal{X}$ with unobserved true binary label $Y \in \{0, 1\}$, where:
- $Y = 0$: Normal (conforming product)
- $Y = 1$: Defective (non-conforming anomaly)

An automated anomaly detection system computes an anomaly score $S(X) \in \mathbb{R}$ and compares it to a calibrated category decision threshold $\tau_c \in \mathbb{R}$. The automated decision rule is:
$$\hat{Y} = \mathbb{I}(S(X) \ge \tau_c)$$

### 2.1 Automated Decision Loss
Let the cost matrix for automated decisions be defined as:
- Cost of True Negative ($\hat{Y}=0, Y=0$): $0$
- Cost of True Positive ($\hat{Y}=1, Y=1$): $0$
- Cost of False Positive ($\hat{Y}=1, Y=0$, Type I error): $c_{\text{FP}} > 0$
- Cost of False Negative ($\hat{Y}=0, Y=1$, Type II error): $c_{\text{FN}} > 0$

The asymmetric cost ratio is denoted by $\lambda = \frac{c_{\text{FN}}}{c_{\text{FP}}}$. In manufacturing inspection, missed defects carry catastrophic downstream scrap, rework, or recall penalties, so typically $\lambda \gg 1$.

The automated classification loss for an individual specimen is:
$$L_{\text{auto}}(\hat{Y}, Y) = c_{\text{FN}} \cdot \mathbb{I}(\hat{Y}=0, Y=1) + c_{\text{FP}} \cdot \mathbb{I}(\hat{Y}=1, Y=0)$$

### 2.2 Human Review Model
Let $a_i \in \{0, 1\}$ denote the review allocation decision for specimen $i$, where:
- $a_i = 0$: Accept automated decision $\hat{Y}_i$ without review.
- $a_i = 1$: Defer specimen $i$ to a human visual inspector.

A review action incurs a direct human inspection capacity cost $c_{\text{rev}} > 0$. The human inspector exhibits sensitivity $p_{\text{sens}} \in (0, 1]$ and specificity $p_{\text{spec}} \in (0, 1]$. If deferred ($a_i = 1$), the final decision $Y_H$ follows the human inspection outcome:
$$L_{\text{human}}(Y_H, Y) = c_{\text{FN}} \cdot \mathbb{I}(Y_H=0, Y=1) + c_{\text{FP}} \cdot \mathbb{I}(Y_H=1, Y=0) + c_{\text{rev}}$$

Under the standard assumption of expert industrial inspection (adopted in Protocol V3.1 and Phase 8B), human inspection is treated as gold-standard benchmark review ($p_{\text{sens}} = 1.0, p_{\text{spec}} = 1.0$). Therefore:
$$L_{\text{human}}(Y_H, Y) = c_{\text{rev}}$$

---

## 3. Derivation of Expected Loss and Decision Criteria

Let $p_d(X) = P(Y = 1 \mid X)$ denote the true posterior probability of defect given specimen observations.

### 3.1 Expected Automated Loss
Conditioned on observation $X$ and automated decision $\hat{Y}$:
$$\mathbb{E}[L_{\text{auto}} \mid X, \hat{Y}] = \begin{cases} P(Y=1 \mid X) \cdot c_{\text{FN}} = p_d(X) \cdot c_{\text{FN}}, & \text{if } \hat{Y} = 0 \\ P(Y=0 \mid X) \cdot c_{\text{FP}} = (1 - p_d(X)) \cdot c_{\text{FP}}, & \text{if } \hat{Y} = 1 \end{cases}$$

Notice that an automated error occurs if and only if:
- $\hat{Y}=0$ and $Y=1$ (False Negative, with probability $P(\text{Error} \mid X, \hat{Y}=0) = p_d(X)$)
- $\hat{Y}=1$ and $Y=0$ (False Positive, with probability $P(\text{Error} \mid X, \hat{Y}=1) = 1 - p_d(X)$)

Defining the error severity weight as:
$$W(\hat{Y}) = \begin{cases} c_{\text{FN}}, & \text{if } \hat{Y} = 0 \\ c_{\text{FP}}, & \text{if } \hat{Y} = 1 \end{cases}$$
the expected automated loss is simply the cost-weighted error risk:
$$\mathbb{E}[L_{\text{auto}} \mid X, \hat{Y}] = P(\text{Error} \mid X, \hat{Y}) \cdot W(\hat{Y})$$

### 3.2 Expected Review Benefit in MACBA
In MACBA, the expected reduction in loss achieved by deferring specimen $X$ to human inspection is defined as:
$$\Delta L(X) = \mathbb{E}[L_{\text{auto}} \mid X, \hat{Y}] - \mathbb{E}[L_{\text{human}} \mid X]$$

Substituting the expressions from Section 3.1:
$$\Delta L(X) = P(\text{Error} \mid X, \hat{Y}) \cdot W(\hat{Y}) - c_{\text{rev}}$$

Specifically:
$$\Delta L(X) = \begin{cases} p_d(X) \cdot c_{\text{FN}} - c_{\text{rev}}, & \text{if } \hat{Y} = 0 \\ (1 - p_d(X)) \cdot c_{\text{FP}} - c_{\text{rev}}, & \text{if } \hat{Y} = 1 \end{cases}$$

### 3.3 Conventional Cost-Weighted Risk Ranking (BL6)
In conventional cost-sensitive classification and risk-based reject ranking (Baseline BL6; Chow 1970; Elkan 2001), specimens are prioritized according to their expected classification risk:
$$\text{Score}_{\text{BL6}}(X) = \mathbb{E}[L_{\text{auto}} \mid X, \hat{Y}] = P(\text{Error} \mid X, \hat{Y}) \cdot W(\hat{Y})$$

---

## 4. Formal Proof of Equivalence

### Theorem 1 (Equivalence Under Unit Capacity Budget)
*Let $\mathcal{D} = \{X_1, \dots, X_N\}$ be a finite set of evaluated specimens with automated predictions $\hat{Y}_1, \dots, \hat{Y}_N$ and calibrated defect probabilities $\hat{p}_d(X_1), \dots, \hat{p}_d(X_N)$. Let $c_{\text{rev}} > 0$ be a constant review cost, $w_i = 1$ be uniform review capacity weights, and $K \in \{1, \dots, N\}$ be the review quota. Assume identical deterministic tie-breaking. Then:*
1. *The ranking of specimens induced by MACBA's marginal utility ratio $r_i = \frac{\Delta L(X_i)}{w_i}$ is strictly identical to the ranking induced by BL6's risk score $\text{Score}_{\text{BL6}}(X_i)$.*
2. *The greedy selection set $\mathcal{S}_{\text{MACBA}}(K)$ is identical to the top-$K$ risk selection set $\mathcal{S}_{\text{BL6}}(K)$.*

### Proof:
**Step 1: Relation between ranking scores**  
For any specimen $X_i$, its MACBA marginal utility ratio is:
$$r_i = \frac{\Delta L(X_i)}{w_i} = \frac{\Delta L(X_i)}{1} = \Delta L(X_i)$$
From Section 3.2:
$$\Delta L(X_i) = P(\text{Error} \mid X_i, \hat{Y}_i) \cdot W(\hat{Y}_i) - c_{\text{rev}} = \text{Score}_{\text{BL6}}(X_i) - c_{\text{rev}}$$
Therefore, for every specimen $i \in \{1, \dots, N\}$:
$$r_i = \text{Score}_{\text{BL6}}(X_i) - c_{\text{rev}}$$

**Step 2: Preservation of strict total order**  
Consider any pair of specimens $X_i, X_j \in \mathcal{D}$.  
$$r_i > r_j \iff \text{Score}_{\text{BL6}}(X_i) - c_{\text{rev}} > \text{Score}_{\text{BL6}}(X_j) - c_{\text{rev}}$$
Adding the constant scalar $c_{\text{rev}}$ to both sides preserves the inequality:
$$r_i > r_j \iff \text{Score}_{\text{BL6}}(X_i) > \text{Score}_{\text{BL6}}(X_j)$$
Similarly:
$$r_i = r_j \iff \text{Score}_{\text{BL6}}(X_i) = \text{Score}_{\text{BL6}}(X_j)$$

**Step 3: Tie-breaking preservation**  
When $r_i = r_j$, both policies invoke the specified tie-breaker (lexicographical ordering on unique identifier `image_id`). Because the tie condition is identical ($r_i = r_j \iff \text{Score}_{\text{BL6}}(X_i) = \text{Score}_{\text{BL6}}(X_j)$), identical tie-breakers produce identical resolution orders.

**Step 4: Greedy selection identity**  
In the 0-1 Knapsack problem with uniform item weights ($w_i = 1 \ \forall i$), the capacity constraint is $\sum_{i=1}^N a_i \le K$. The greedy algorithm that sorts items in descending order of $r_i$ and selects the top $K$ items achieves the globally optimal solution to the integer program.

Because the sorted permutation of specimens under $r_i$ is identical to the sorted permutation under $\text{Score}_{\text{BL6}}(X_i)$, the set of the top $K$ specimens chosen by MACBA is identical to the set of the top $K$ specimens chosen by BL6:
$$\mathcal{S}_{\text{MACBA}}(K) = \mathcal{S}_{\text{BL6}}(K) \quad \forall K \in \{1, \dots, N\}$$
$\blacksquare$

---

## 5. Non-Unit Capacity and Fractional Knapsack

Consider the generalized case where inspection capacity costs vary by category or specimen ($w_i \ne 1$).

Under general weights $w_i$, MACBA ranks items by the benefit-to-weight ratio:
$$\tilde{r}_i = \frac{\Delta L(X_i)}{w_i} = \frac{\text{Score}_{\text{BL6}}(X_i) - c_{\text{rev}, i}}{w_i}$$
This represents the classic **Dantzig (1957) greedy heuristic** for the linear relaxation of the 0-1 Knapsack Problem.

In cost-sensitive machine learning and medical decision making, when test costs vary, ranking instances by $\frac{\text{Expected Benefit}}{\text{Test Cost}}$ is the standard formulation of cost-sensitive active testing (Greiner et al., 2002; Lizotte et al., 2003; Saar-Tsechansky & Provost, 2007). 

Applying Dantzig's 1957 knapsack heuristic to cost-weighted expected loss does not constitute an algorithmic discovery or novel machine learning method.

---

## 6. Empirical Verification of Equivalence

Using the 174 evaluation specimens from Phase 8B across 5 cost ratios $\lambda \in \{1, 5, 20, 50, 100\}$ and 11 review budgets $K \in \{5, 10, 15, 20, 25, 30, 40, 50, 60, 80, 100\}$, we evaluated the empirical selection correspondence between MACBA and BL6.

| Cost Ratio ($\lambda$) | Evaluated Budgets ($K$) | Score Difference ($\text{Score}_{\text{BL6}} - \Delta L$) | Spearman Rank Corr ($\rho_s$) | Selection Overlap Rate | Cost Reduction Match |
|:---:|:---:|:---:|:---:|:---:|:---:|
| $\mathbf{1}$ | All 11 budgets ($5 \dots 100$) | Exactly $+1.0000$ (constant) | $\mathbf{1.000000}$ | $\mathbf{100.0\%}$ | Exact ($0.0000\%$ diff) |
| $\mathbf{5}$ | All 11 budgets ($5 \dots 100$) | Exactly $+1.0000$ (constant) | $\mathbf{1.000000}$ | $\mathbf{100.0\%}$ | Exact ($0.0000\%$ diff) |
| $\mathbf{20}$ | All 11 budgets ($5 \dots 100$) | Exactly $+1.0000$ (constant) | $\mathbf{1.000000}$ | $\mathbf{100.0\%}$ | Exact ($0.0000\%$ diff) |
| $\mathbf{50}$ | All 11 budgets ($5 \dots 100$) | Exactly $+1.0000$ (constant) | $\mathbf{1.000000}$ | $\mathbf{100.0\%}$ | Exact ($0.0000\%$ diff) |
| $\mathbf{100}$ | All 11 budgets ($5 \dots 100$) | Exactly $+1.0000$ (constant) | $\mathbf{1.000000}$ | $\mathbf{100.0\%}$ | Exact ($0.0000\%$ diff) |

Every single one of the $870$ decision instances in `BL6_MACBA_DECISION_TRACE.csv` confirms Theorem 1 with zero discrepancies.

---

## 7. Conclusion

Under standard industrial inspection settings with unit capacity costs:
1. **MACBA $\equiv$ BL6.**
2. MACBA produces identical allocations, identical cost reductions, and identical error capture rates to conventional cost-sensitive Bayes risk ranking.
3. The claim that MACBA is a novel multi-category budget allocation algorithm cannot be substantiated mathematically or empirically.
