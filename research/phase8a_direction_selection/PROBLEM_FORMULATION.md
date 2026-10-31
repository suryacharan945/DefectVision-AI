# Phase 8A: Rigorous Problem Formulation

**Document ID:** `DV-PHASE8A-FORM-V1`  
**Date:** October 31, 2026  
**Auditor:** Lead AI/ML Research Engineer & Experimental Methodology Reviewer  
**Scope:** Mathematical Problem Specification for Multi-Category Budget-Constrained Selective Inspection

---

## 1. System Model & Notation

Consider an industrial manufacturing plant operating $C$ distinct, concurrent production lines (categories) indexed by $c \in \{1, 2, \dots, C\}$.

### 1.1. Specimen Stream & Automated Model
Each line produces a stream of manufactured items. For item $i$ in category $c$:
- Let $X_{c, i} \in \mathcal{X}_c$ denote the specimen image.
- Let $Y_{c, i} \in \{0, 1\}$ denote the true binary state ($0 = \text{nominal/good}$, $1 = \text{defective/anomalous}$).
- The plant deploys a frozen, unsupervised anomaly detection model (e.g. PatchCore) producing scalar anomaly score:
  $$S_{c, i} = f_c(X_{c, i}) \in \mathbb{R}_{\ge 0}$$
- Each category operates an automated decision threshold $\tau_c$, yielding automated binary prediction:
  $$\hat{Y}_{c, i} = \mathbb{I}(S_{c, i} \ge \tau_c)$$

### 1.2. Automated Model Error Structure
On line $c$, the automated model produces two types of errors:
- **False Negative (FN):** $Y_{c, i} = 1 \land \hat{Y}_{c, i} = 0$ (a defective part escapes automated detection).
- **False Positive (FP):** $Y_{c, i} = 0 \land \hat{Y}_{c, i} = 1$ (a normal part is falsely flagged as a defect).

Let $N_c$ be the number of items evaluated on line $c$, with $N_{\text{total}} = \sum_{c=1}^C N_c$.

---

## 2. Selective Inspection Decision & Budget Constraints

### 2.1. Human Review Allocation
The plant maintains a central quality-assurance inspection team.
- For each item $(c, i)$, a selective triage policy outputs a binary routing decision:
  $$A_{c, i} \in \{0, 1\}$$
  where $A_{c, i} = 1$ routes the item to human visual review, and $A_{c, i} = 0$ allows the automated decision $\hat{Y}_{c, i}$ to proceed autonomously to shipping/scrap.
- Let $K_c = \sum_{i=1}^{N_c} A_{c, i}$ be the review budget allocated to line $c$.
- **Hard Global Factory Budget:** The total inspection team capacity across all lines is strictly capped at $B_{\text{total}}$ items:
  $$\sum_{c=1}^C K_c \le B_{\text{total}} = \lfloor B_{\text{frac}} \times N_{\text{total}} \rfloor$$
  where $B_{\text{frac}} \in [0.01, 0.20]$ represents the overall factory review capacity (e.g., $1\%$ to $20\%$).

### 2.2. Human Reviewer Model
When an item is reviewed ($A_{c, i} = 1$), an expert human inspector examines the part:
- **Human Decision:** $\tilde{Y}_{c, i} \in \{0, 1\}$.
- **Realistic Human Imperfection Parameter:** Rather than assuming infallible inspection, the human reviewer has true-positive accuracy $p_{\text{human}} \in [0.90, 1.00]$ (e.g., $95\%$ sensitivity, $98\%$ specificity) due to visual fatigue or ambiguous defect boundaries. The ideal case $p_{\text{human}} = 1.0$ is reported as a primary benchmark ceiling.
- **Post-Review Output:**
  $$Y_{c, i}^{\text{final}} = A_{c, i} \tilde{Y}_{c, i} + (1 - A_{c, i}) \hat{Y}_{c, i}$$

---

## 3. Industrial Financial Risk & Cost Matrix

In real manufacturing, misclassifications carry severely asymmetric economic consequences:
- $c_{\text{FN}, c} > 0$: Cost of a missed defect escaping to downstream customers or high-value assembly (e.g., product recall, warranty claims, structural failure). Typically **very high** (\$100–\$1,000 per escape).
- $c_{\text{FP}, c} > 0$: Cost of a false alarm (e.g., unnecessary manual secondary handling, unnecessary scrap of good parts). Typically **moderate** (\$5–\$20 per incident).
- $c_{\text{rev}, c} > 0$: Labor cost of manual visual inspection (e.g., wages, workstation overhead, throughput delay). Typically **low** (\$1–\$5 per reviewed specimen).

### Cost Ratio Parameterization:
To avoid arbitrary absolute currency units, costs are normalized relative to $c_{\text{rev}, c} = 1$:
$$\lambda_c = \frac{c_{\text{FN}, c}}{c_{\text{FP}, c}} \in \{5, 10, 20, 50, 100\}$$
$$\gamma_c = \frac{c_{\text{FP}, c}}{c_{\text{rev}, c}} \in \{2, 5, 10\}$$

The financial risk incurred on line $c$ under review allocation $\mathbf{A}_c$ is:
$$\text{Cost}_c(\mathbf{A}_c) = \sum_{i=1}^{N_c} \left[ c_{\text{FN}, c} \cdot \mathbb{I}(Y_{c, i} = 1 \land Y_{c, i}^{\text{final}} = 0) + c_{\text{FP}, c} \cdot \mathbb{I}(Y_{c, i} = 0 \land Y_{c, i}^{\text{final}} = 1) + c_{\text{rev}, c} \cdot A_{c, i} \right]$$

---

## 4. Multi-Category Calibration & Score Incommensurability

A foundational mathematical obstacle in multi-category triage is **score incommensurability**:
- Model scores $S_c(X)$ have completely different numerical ranges and threshold locations across categories (e.g., $\tau_{\text{bottle}} = 1.85$ vs. $\tau_{\text{capsule}} = 2.40$).
- Pooling raw scores globally ($\text{score} = S_c(X)$) causes categories with higher numerical ranges to consume 100% of the review budget, regardless of their actual error rate.
- **Conformal Quantile Normalization:** For each category $c$, using the nominal calibration split $\mathcal{D}_{\text{cal}, c}^{\text{norm}}$, we map raw anomaly score $S_c(X)$ to its empirical nominal non-conformity p-value:
  $$u_{c}(X) = \frac{1}{|\mathcal{D}_{\text{cal}, c}| + 1} \sum_{X_j \in \mathcal{D}_{\text{cal}, c}} \mathbb{I}(S_c(X_j) \ge S_c(X))$$
  This maps raw scores across all $C$ categories into a standardized, distribution-free $[0, 1]$ uniform scale under the nominal null hypothesis.

---

## 5. Primary Optimization Objective

The primary objective is to find the allocation vector $\mathbf{K}^* = (K_1^*, \dots, K_C^*)$ and per-category item selections that minimize total factory financial risk subject to the global budget constraint:

$$\min_{\{A_{c, i}\}} \sum_{c=1}^C \text{Cost}_c(\mathbf{A}_c)$$
$$\text{subject to} \quad \sum_{c=1}^C \sum_{i=1}^{N_c} A_{c, i} \le B_{\text{total}}, \quad A_{c, i} \in \{0, 1\}, \quad \sum_{i=1}^{N_c} A_{c, i} \ge K_{\min, c}$$

where $K_{\min, c} \ge 0$ is an optional operational safety floor ensuring no production line is completely unmonitored.

---

## 6. Formal Evaluation Metrics

1. **Multi-Category Error Capture Rate ($\text{MC-ECR}$):**
   $$\text{MC-ECR} = \frac{\sum_{c=1}^C \text{Captured Errors}_c}{\sum_{c=1}^C \text{Base Errors}_c} \times 100\%$$
2. **Multi-Category Defect Escape Reduction ($\text{MC-DER}$):**
   $$\text{MC-DER} = \frac{\sum_{c=1}^C \text{Captured FN}_c}{\sum_{c=1}^C \text{Base FN}_c} \times 100\%$$
3. **Total Financial Risk Reduction ($\Delta \text{Risk}$):**
   $$\Delta \text{Risk} = \frac{\text{Cost}_{\text{no-review}} - \text{Cost}(\mathbf{A}^*)}{\text{Cost}_{\text{no-review}}} \times 100\%$$
4. **Global Error Review Yield:**
   $$\text{Global Yield} = \frac{\sum_{c=1}^C \text{Captured Errors}_c}{B_{\text{total}}} \times 100\%$$
5. **Gini Allocation Equity:**
   Measures whether budget allocation is overly concentrated on a single category or balanced according to marginal error density.
