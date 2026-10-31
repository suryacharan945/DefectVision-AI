# Mathematical & Methodological Audit: Conformal Selective Anomaly Detection (CSAD) & CPND

**Document ID:** `DV-AUDIT-CONFORMAL-VALIDITY-V1`  
**Audit Date:** October 31, 2026  
**Auditor:** Lead AI/ML Research Engineer & Theoretical Methodology Reviewer  
**Scope:** Rigorous evaluation of theoretical assumptions, finite-sample guarantees, exchangeability bounds, and empirical viability of proposed conformal selective review methods  

---

## 1. Executive Summary

Previous proposals for DefectVision AI suggested a novel method named *Calibrated Patch-Neighborhood Dispersion (CPND)* integrated into a *Conformal Selective Anomaly Detection (CSAD)* framework, asserting "provably higher distribution-free error capture guarantees under fixed audit budgets."

This methodological review conducts an exhaustive mathematical interrogation of these claims.

### Core Theoretical Findings:
1. **Defects Violate Exchangeability:** Conformal prediction guarantees valid marginal coverage ($1 - \alpha$) strictly under the assumption of exchangeable observations drawn from the same underlying distribution $P_{\text{normal}}$. Defective specimens represent out-of-distribution (OOD) observations drawn from non-identical, unknown distributions $Q_{\text{defect}} \ne P_{\text{normal}}$. Therefore, **conformal calibration provides NO distribution-free finite-sample guarantees on defect detection, defect escape reduction, or error capture.**
2. **Fixed Review Budgets Invert Conformal Guarantees:** Conformal prediction controls risk by allowing the prediction set size (or rejection volume) to vary dynamically. Under a fixed industrial inspection budget $B \in [0.01, 0.20]$, the review volume is fixed, converting the problem into *selective classification / ranking* (Geifman & El-Yaniv, 2017). Conformal coverage guarantees do not hold under fixed budget truncation without restrictive monotonicity assumptions.
3. **Conformal p-values are Not Posterior Error Probabilities:** A conformal p-value evaluates the probability of observing a non-conformity score as extreme as $s(X)$ under the null hypothesis $H_0: X \sim P_{\text{normal}}$. It does **not** equal the posterior probability that the model's classification is erroneous ($P(\text{error} \mid X)$).
4. **Patch Dispersion vs. Boundary Distance:** Patch-Neighborhood Dispersion (PND) measures the normalized variance of the $K$-nearest neighbor distance profile. If local coreset density varies across the nominal manifold, high dispersion may simply reflect low manifold density rather than defect ambiguity. To be useful, PND must be benchmarked directly against the simpler scalar baseline: distance to decision boundary ($|s(X) - \tau_c|$).

---

## 2. Rigorous Mathematical Deconstruction

### 2.1. Conformal Prediction Formulation in One-Class Anomaly Detection
Let nominal calibration images be denoted by $\mathcal{D}_{\text{cal}} = \{X_1, X_2, \dots, X_n\} \stackrel{\text{i.i.d.}}{\sim} P_{\text{normal}}$.  
Let $s: \mathcal{X} \to \mathbb{R}$ denote a non-conformity scoring function (e.g., PatchCore distance $s(X) = \max_{m \in \mathcal{P}(X)} \min_{v \in \mathcal{M}} \|m - v\|_2$).

For a pre-specified significance level $\alpha \in (0, 1)$, split-conformal calibration defines the decision threshold $\hat{q}_{1-\alpha}$ as the empirical quantile:
$$\hat{q}_{1-\alpha} = \text{Quantile}\left(\frac{\lceil (n + 1)(1 - \alpha) \rceil}{n}, \{s(X_i)\}_{i=1}^n\right)$$

#### Valid Marginal Coverage Guarantee:
If a test sample $X_{n+1}$ is exchangeable with $\mathcal{D}_{\text{cal}}$ (i.e., $X_{n+1} \sim P_{\text{normal}}$), then:
$$\mathbb{P}_{X_{n+1} \sim P_{\text{normal}}}\left(s(X_{n+1}) \le \hat{q}_{1-\alpha}\right) \ge 1 - \alpha$$
This guarantees that the **false alarm rate on normal items is bounded by $\alpha$**.

#### Breakdown on Defective Items (The Exchangeability Failure):
Let $Y_{n+1} \in \{\text{normal}, \text{defective}\}$. If $Y_{n+1} = \text{defective}$, then $X_{n+1} \sim Q_{\text{defect}}$, where $Q_{\text{defect}} \ne P_{\text{normal}}$.
Because $(X_1, \dots, X_n, X_{n+1})$ are **not exchangeable**, the standard conformal theorem provides:
$$\mathbb{P}_{X_{n+1} \sim Q_{\text{defect}}}\left(s(X_{n+1}) > \hat{q}_{1-\alpha}\right) = \text{UNDEFINED / NO DISTRIBUTION-FREE GUARANTEE}$$
The probability of detecting a defect (power) depends entirely on the separation between $P_{\text{normal}}$ and $Q_{\text{defect}}$ in feature space, which cannot be bounded without strong parametric assumptions.

> [!CAUTION]
> **Scientific Mandate:** It is scientifically invalid to claim that conformal prediction provides a "guaranteed error capture rate" or "guaranteed defect escape reduction." Any paper submitted to a Q1 journal making such a claim will be rejected for elementary statistical errors.

---

### 2.2. Human-Review Budget Inversion ($B \le 10\%$)

In practical manufacturing operations, management imposes a hard constraint on manual inspection capacity:
$$\text{Review Budget } B \in (0, 1] \implies \text{Audit exactly } K = \lfloor B \cdot N_{\text{test}} \rfloor \text{ specimens}$$

#### Theoretical Contrast:
| Framework | Parameter Held Fixed | Variable Parameter | Statistical Guarantee |
| :--- | :--- | :--- | :--- |
| **Standard Conformal Prediction** | Nominal Risk $\alpha$ (e.g., $\le 5\%$) | Number of flagged samples $K(\alpha)$ varies with data | Valid finite-sample coverage $1 - \alpha$ on nominals |
| **Selective Classification / Human Audit** | Review Volume $K = \lfloor B \cdot N \rfloor$ | Empirical error capture rate $\text{ECR}(B)$ varies with data | **No distribution-free guarantee** without calibration on known defects |

When budget $B$ is fixed, the system must rank all $N_{\text{test}}$ items by an uncertainty score $u(X)$ and audit the top $K$ items. The success of this strategy is governed entirely by the **ranking concordance** between $u(X)$ and actual model errors:
$$\text{ECR}(B) = \frac{\sum_{i=1}^K \mathbf{1}(X_{(i)} \text{ is an error})}{\text{Total Errors } E_0}$$
This is an empirical ranking problem (AUCCC / AUROC of uncertainty), not a conformal coverage property.

---

### 2.3. Analysis of Patch-Neighborhood Dispersion (PND)

The proposed PND score is formulated as:
$$\text{PND}(X) = \frac{\sigma\left(\{d_{(1)}, d_{(2)}, \dots, d_{(K)}\}\right)}{\mu\left(\{d_{(1)}, d_{(2)}, \dots, d_{(K)}\}\right)}$$
where $d_{(j)} = \|m^* - v_{(j)}\|_2$ are the distances from the maximally anomalous patch $m^*$ to its $K$-nearest neighbors in coreset memory bank $\mathcal{M}$.

#### Failure Modes of Raw Dispersion:
1. **Manifold Sparsity Artifact:** In regions of the nominal manifold where normal training samples were sparse, nearest neighbors are naturally more dispersed. An entirely normal test patch falling in a sparse nominal region will exhibit high PND, causing false alarms in review allocation.
2. **Extreme Defect Cluster Artifact:** An obvious, massive defect will be far from all nominal vectors. The top-$K$ distances may all be large and relatively uniform, yielding a *low* dispersion score. This is desirable for automated classification, but if PND is used directly to detect ambiguity, it will fail to differentiate obvious defects from obvious normals without explicit distance anchoring.
3. **Redundancy with Decision Boundary Distance:** In any deterministic decision rule $s(X) \gtrless \tau_c$, classification errors predominantly concentrate in the boundary band:
   $$\mathcal{B}_\epsilon = \{X : |s(X) - \tau_c| \le \epsilon\}$$
   A simple scalar metric, **Distance-to-Threshold** ($u_{\text{dist}}(X) = \frac{1}{|s(X) - \tau_c| + \epsilon}$), already captures $21.62\%$ of errors at $10\%$ budget on MVTec AD.
   
#### Requirement for PND Utility:
For PND to represent a publishable contribution, it must be formulated as a **joint or residual metric** that conditions on boundary distance:
$$u_{\text{joint}}(X) = f\left(|s(X) - \tau_c|, \text{PND}(X)\right)$$
and it must demonstrate statistically significant improvement over $|s(X) - \tau_c|$ alone across multiple independent industrial categories.

---

## 3. Methodological Comparison Matrix: Selective Review Baselines

| Method | Type | Theoretical Guarantee | Computational Cost | Tested on MVTec AD | Status in Project |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **Uniform Random** | Null Baseline | Expected $\text{ECR} = B$ | $\mathcal{O}(1)$ | $8.11\%$ at $10\%$ budget | Implemented & Verified |
| **Top-Score ($s(X)$)** | Naive Heuristic | None ($\text{ECR} \to 0\%$ for sharp models) | $\mathcal{O}(1)$ | $0.00\%$ at $10\%$ budget | Implemented & Verified |
| **Distance-to-Threshold ($|s(X) - \tau_c|$)** | Boundary Proximity | None (Empirical boundary density) | $\mathcal{O}(1)$ | $21.62\%$ at $10\%$ budget | Implemented & Verified |
| **Supervised Margin ($1 - \|2p - 1\|$)** | Epistemic Margin | Valid only if $p$ is well-calibrated | $\mathcal{O}(1)$ | $91.89\%$ at $10\%$ budget | Implemented (Requires Defect Labels) |
| **Proposed CPND / CSAD** | Unsupervised Neighborhood Geometry | Marginal nominal FPR $\le \alpha$; **No defect capture guarantee** | $\mathcal{O}(K \log M)$ | Unimplemented | **Candidate for Controlled Development Experiments** |

---

## 4. Mandatory Guidelines for Protocol V2

1. **Retract Overclaimed Guarantees:** Replace all references to "distribution-free error capture guarantees" with "empirically evaluated selective review performance under bounded audit budgets."
2. **Clarify Conformal Scope:** State explicitly that conformal calibration on nominal samples guarantees only that the nominal false alarm rate is bounded by $\alpha$, and that error capture on defective samples is an empirical research hypothesis.
3. **Mandate Boundary Baseline Ablation:** CPND cannot be published without a head-to-head ablation against Distance-to-Threshold ($|s(X) - \tau_c|$) using identical memory banks and test samples.
4. **Predefine Evaluation Criteria:** Evaluate selective review using Area Under the Cost-Coverage Curve (AUCCC) and ECR@$B$ across multiple fixed budgets ($B \in \{1\%, 2\%, 5\%, 10\%, 15\%, 20\%\}$).
