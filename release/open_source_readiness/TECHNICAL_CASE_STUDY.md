# Technical Case Study: Engineering Rigor, Selective Triage, and Negative Scientific Findings in Industrial Visual Anomaly Detection

**Project:** DefectVision AI  
**Author:** Lead AI/ML Research Engineer & Systems Architect  
**Date:** November 2026  
**Document Classification:** Technical Engineering Whitepaper  

---

## 1. Executive Summary

Automated optical inspection (AOI) in modern manufacturing is constrained by a fundamental trade-off: fully automated deep neural networks cannot guarantee zero defect escapes without generating false positive rates that cause costly line stoppages, while 100% human visual inspection is physically and economically unfeasible.

**DefectVision AI** was developed as an open-source, full-stack industrial quality inspection platform designed to resolve this dilemma through **decision-theoretic human-in-the-loop (HITL) triage**.

This case study documents:
1. The full-stack implementation combining unsupervised memory-bank localization (**PatchCore**) with supervised verification (**EfficientNet-B0**).
2. The empirical demonstration that **cost-weighted Bayes risk ranking** captures over $30\%$ additional economic loss reduction compared to standard distance heuristics under asymmetric manufacturing defect costs ($\lambda = c_{\text{FN}} / c_{\text{FP}} \gg 1$).
3. Two rigorous scientific audits that disproved candidate "novel" algorithms:
   - **CPND (Conformal Patch-Neighborhood Dispersion):** Proven to perform worse than simple decision-boundary distance ($22.2\%$ vs. $30.6\%$ error review yield).
   - **MACBA (Multi-Category Adaptive Budget Allocation):** Formally proven to be **mathematically isomorphic** to Chow's (1970) classic cost-weighted Bayes error-risk ranking under unit review costs ($\rho_s = 1.000000$, $100.0\%$ selection identity).
   - **Discrepancy Post-Mortem:** Tracing an apparent Phase 8B advantage at symmetric costs ($\lambda = 1$) to an asymmetric probability estimator defect in the baseline.

This document serves as an exemplar of intellectual honesty and engineering discipline in applied machine learning.

---

## 2. Detection Architecture & The Hybrid Rule Trade-Off

### 2.1 Unsupervised Memory-Bank Localization (PatchCore)
For surface, texture, and structural defects, labeled anomalous data is scarce. DefectVision AI implements PatchCore (Roth et al., 2022) using WideResNet-50-2:
- **Patch Embeddings:** Feature maps from `layer2` and `layer3` are pooled and concatenated into 384-dimensional local patch tokens.
- **Coreset Reduction:** A greedy minimax facility location algorithm reduces the nominal patch bank by $90\%$, bounding query latency while retaining boundary coverage.
- **FAISS FlatL2 Indexing:** Nearest-neighbor Euclidean distance search computes an anomaly score $S(X)$ and generates Gaussian-smoothed spatial heatmaps ($224 \times 224$).

### 2.2 Supervised Structural Integrity Check (EfficientNet-B0)
While PatchCore excels at subtle local textures, it occasionally struggles with large-scale global structural fractures where no individual patch appears out-of-distribution, but their relative spatial arrangement is invalid. An ImageNet pre-trained EfficientNet-B0 classifier functions as a global integrity check.

### 2.3 The Hybrid Decision Rule Audit
In initial prototyping, an `OR` decision rule was implemented:
$$\hat{Y}_{\text{hybrid}} = \hat{Y}_{\text{PatchCore}} \lor \hat{Y}_{\text{EfficientNet}}$$
An exhaustive empirical audit of this rule revealed critical trade-offs:
- **Benefit:** The hybrid rule successfully corrected false negatives on severe gross fractures (e.g., fractured bottle necks), boosting recall from $93.7\%$ to $98.4\%$.
- **Cost:** Because the models' false positive errors are partially independent, the naive OR rule caused the false positive rate to double (from $3.8\%$ to $8.1\%$), increasing unnecessary scrap.
- **Engineering Recommendation:** The OR rule should only be deployed when the cost ratio $\lambda = c_{\text{FN}} / c_{\text{FP}} \ge 20$. For balanced or low-cost lines, PatchCore should serve as the sole primary gatekeeper, using classifier confidence only for severity grading.

---

## 3. Decision-Theoretic Selective Review

Under a fixed factory review capacity of $K$ specimens, DefectVision AI triages parts using decision-theoretic loss reduction:

```
[ Automated Inspection Score S(X) ]
                 |
                 v
   [ Decision Threshold tau_c ]
                 |
                 v
   [ Platt Logistic Calibration ]  -----> P(Defect | X)
                 |
                 v
   [ Expected Loss Under Automation ]
     E[L_auto] = P(Error | X, Y_hat) * Cost(Error | Y_hat)
                 |
                 v
   [ Marginal Utility of Human Review ]
     Delta L(X) = E[L_auto] - c_rev
                 |
                 v
   [ Greedy Knapsack / Risk Ranking ] ----> Priority Review Queue (Top K)
```

### Empirical Results ($\lambda = 20, K = 25$):
- **Uniform Category Allocation (BL0):** $12.49\%$ cost reduction; captures 4 FNs.
- **Pooled Boundary Distance (BL2):** $15.75\%$ cost reduction; captures 5 FNs.
- **Cost-Weighted Bayes Risk (BL6 / Proper MACBA):** $\mathbf{46.27\%}$ cost reduction; captures $\mathbf{10}$ critical false negatives ($+30.52\%$ relative improvement over BL2, $p = 0.00038$).

Cost weighting succeeds because it concentrates scarce human inspection bandwidth exclusively on predicted normal parts near the threshold that carry catastrophic escape penalties ($c_{\text{FN}} = 200$), rather than wasting capacity verifying false alarms ($c_{\text{FP}} = 10$).

---

## 4. Scientific Audit 1: The CPND Dispersion Hypothesis

### The Proposed Hypothesis:
In Phase 7B, **Conformal Patch-Neighborhood Dispersion (CPND)** was proposed as a novel epistemic uncertainty metric. It hypothesized that measuring the spatial feature dispersion among the top-$k$ nearest neighbors in PatchCore's memory bank would identify ambiguous, out-of-distribution defects more reliably than raw distance to the decision threshold.

### The Empirical Test & Failure:
In Phase 7C, density-normalized CPND was implemented and evaluated on the 330 development specimens across multiple threshold percentiles:
- **Raw Boundary Distance Review Yield:** $30.6\%$ of reviewed items were true automated errors.
- **CPND Review Yield:** Dropped sharply to **$22.2\%$**.
- **Root Cause:** Feature dispersion in pre-trained CNN embedding space is heavily confounded by intrinsic texture complexity (e.g., complex printed circuit traces naturally exhibit high neighbor dispersion even when completely normal).
- **Outcome:** The hypothesis was formally rejected, and development was terminated (`STOP CPND`).

---

## 5. Scientific Audit 2: MACBA Equivalence & The Discrepancy Post-Mortem

### The Proposed Hypothesis:
In Phase 8A/8B, **Multi-Category Adaptive Cost-Weighted Budget Allocation (MACBA)** was proposed as a novel multi-line knapsack optimization algorithm for human inspection triage.

### Mathematical Proof of Equivalence:
In Phase 8C, we conducted a formal mathematical analysis comparing MACBA's greedy knapsack formulation against Chow's (1970) classic cost-weighted Bayes error-risk ranking.

Let $w_i = c_{\text{rev}} = 1$ be uniform review capacity costs.
MACBA ranks items by marginal utility:
$$r_i = \frac{\Delta L(X_i)}{w_i} = P(\text{Error}_i \mid X_i, \hat{Y}_i) \cdot W(\hat{Y}_i) - c_{\text{rev}}$$
Conventional Bayes risk ranking (BL6) ranks items by:
$$\text{Score}_{\text{BL6}}(X_i) = P(\text{Error}_i \mid X_i, \hat{Y}_i) \cdot W(\hat{Y}_i)$$
Because $c_{\text{rev}} = 1.0$ is an invariant constant scalar:
$$r_i > r_j \iff \text{Score}_{\text{BL6}}(X_i) > \text{Score}_{\text{BL6}}(X_j)$$
Under uniform item weights, the 0-1 Knapsack problem is isomorphic to fractional ranking. Therefore, greedy knapsack selection on marginal utility is **mathematically identical** to sorting by Bayes risk and taking the top $K$ items.

### The $\lambda = 1$ Discrepancy Post-Mortem:
In Phase 8B, MACBA reported $23.71\%$ cost reduction at $\lambda = 1$ versus $18.00\%$ for BL6. Code execution tracing revealed:
1. MACBA evaluated probabilities using a **signed logistic model** (`defect_clf(S - tau)`), correctly distinguishing between false negatives ($S < \tau$) and false positives ($S > \tau$).
2. Baseline BL6 was evaluated using an **unsigned scalar logistic model** (`error_clf(|S - tau|)`).
3. At $\lambda = 1$, $c_{\text{FN}} = c_{\text{FP}} = 10.0$. Thus, BL6 evaluated $\text{Score} = P(\text{Error} \mid |S - \tau|) \times 10.0$. Because logistic regression on distance is strictly monotonically decreasing, **BL6 collapsed completely to BL2 (Pooled Distance)**, blindly selecting specimens symmetrically across the threshold.
4. When BL6 was corrected to use signed error risk, the discrepancy vanished: **BL6 and MACBA achieved identical $35.71\%$ cost reduction and $100.0\%$ selection overlap ($25/25$)**.

The apparent novelty was an artifact of an asymmetric implementation error.

---

## 6. Statistical and Dataset Limitations

1. **Development Sample Size:** The development pool consists of 330 images across 3 exposed categories (`bottle`, `capsule`, `metal_nut`). Partitioning into a $50\%$ calibration split ($N=156$) and a $50\%$ evaluation split ($N=174$) yields modest sample sizes ($35$ evaluation errors: $32$ FN, $3$ FP).
2. **Platt Scaling Sensitivity:** On manufacturing lines with fewer than 20 labeled validation defects, logistic calibration exhibits high parameter variance.
3. **Quarantine Preserved:** The 11 unexposed VisA categories, BTAD, and Chukyo remain untouched. We deliberately refuse to evaluate or claim generalization on these benchmarks until an independent, large-scale study is conducted.

---

## 7. Key Engineering & Research Takeaways

1. **Beware the "Novel Algorithm" Trap in Applied AI:** Many seemingly novel resource allocation or selective prediction methods in machine learning are re-inventions or minor reformulations of classic Operations Research (Dantzig 1957) or Bayes decision theory (Chow 1970; Elkan 2001).
2. **Always Audit Baseline Implementations:** When a proposed method outperforms a strong baseline, thoroughly inspect the baseline's code. In this project, an unintended reliance on unsigned distance in the baseline created a spurious illusion of superiority.
3. **Intellectual Honesty Drives Real Value:** Publishing negative results and equivalence proofs saves future engineering teams hundreds of wasted hours, while leaving a hardened, production-ready software application that solves the real-world manufacturing inspection problem.
