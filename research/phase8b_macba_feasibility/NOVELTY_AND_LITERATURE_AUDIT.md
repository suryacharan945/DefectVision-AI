# Phase 8B: Novelty & Literature Audit

**Document ID:** `DV-PHASE8B-LIT-AUDIT-V1`  
**Date:** October 31, 2026  
**Auditor:** Lead AI/ML Research Engineer & Experimental Methodology Reviewer  
**Scope:** Rigorous Novelty De-Hyping, Competing Paper Analysis, and Publisher-Verified Metadata

---

## 1. De-Hyping and Objective Re-Assessment

In Phase 8A, preliminary assessment labeled Candidate Direction B as having "very high novelty" and "low rejection risk." In accordance with scientific peer-review standards, this audit **removes all promotional language** and critically benchmarks the proposal against closely related prior art in:
1. Workload-constrained learning to defer.
2. Cost-sensitive reject options.
3. Multi-group resource allocation.
4. Active learning under bounded labeling budgets.

### The Realistic Research Positioning:
- **What is NOT Novel:**
  - Cost-sensitive selective classification is not novel; it traces back to C. K. Chow (1970) and Charoenphakdee et al. (ICML 2021).
  - Deferring decisions under human workload/capacity constraints is not novel; Alves et al. (TMLR 2024) and Reid et al. (2024) specifically study capacity-constrained deferral.
  - Multi-choice knapsack optimization and marginal gain allocation are well-established operational research tools.
- **What IS Defensible as a Focused Technical Contribution:**
  - In unsupervised visual anomaly detection, non-parametric nearest-neighbor detectors (PatchCore, PaDiM) produce scalar distances that lack class-posterior probability calibration and possess incommensurable scales across different visual manifolds.
  - While existing AD benchmarks (MVTec, VisA) evaluate categories in isolation, no published work has benchmarked multi-product inspection allocation where a single human audit capacity must be partitioned across concurrent production lines using only nominal calibration data.
  - The technical contribution is therefore an **empirical and methodological framework for multi-category inspection triage on frozen distance-based anomaly detectors**, evaluated against strong calibrated baselines.

---

## 2. Competing Literature & Mathematical Precedents

Below, we audit the directly competing literature, identifying the closest mathematical formulation and baseline for each paper:

### 2.1. Cost-Sensitive Learning to Defer to Multiple Experts with Workload Constraints
- **Authors:** Jean V. Alves, Diogo Leitão, Sérgio Jesus, Marco O. P. Sampaio, Javier Liébana, Pedro Saleiro, Mário A. T. Figueiredo, Pedro Bizarro
- **Publication:** *Transactions on Machine Learning Research (TMLR)*, 2024.
- **Publisher Link:** Published in TMLR (ISSN 2835-8856); Preprint: [arXiv:2403.06906](https://arxiv.org/abs/2403.06906) [cs.LG].
- **Closest Mathematical Formulation:**
  $$\min_{g, m_1, \dots, m_K} \mathbb{E}\left[ L_{\text{cost}}(y, \hat{y}) \right] \quad \text{s.t.} \quad \mathbb{P}(\text{defer to expert } k) \le W_k$$
  where $W_k$ is the human reviewer's workload capacity constraint.
- **Closest Baseline:** Softmax thresholding with proportional quota clipping.
- **Key Differences from Our Work:**
  - Alves et al. assume supervised multiclass tabular/vision models trained end-to-end with paired historical human decisions.
  - Our setting operates on frozen, unsupervised nearest-neighbor one-class anomaly detectors without defect training samples or historical human decision logs.

### 2.2. Online Decision Deferral under Budget Constraints
- **Authors:** Mirabel Reid, Tom Sühr, Claire Vernade, Samira Samadi
- **Publication:** arXiv preprint `arXiv:2409.20489` [cs.LG], 2024.
- **Closest Mathematical Formulation:** Contextual bandit formulation where deferral to a human consumes budget $b_t \le B$ under partial feedback.
- **Closest Baseline:** Greedy cost-to-go index heuristic.
- **Key Differences from Our Work:**
  - Focuses on sequential online bandit regret minimization under partial feedback.
  - Our setting focuses on offline batch-level factory triage where full automated scores for a production run are observable prior to human shift allocation.

### 2.3. On Optimum Recognition Error and Reject Tradeoff
- **Authors:** C. K. Chow
- **Publication:** *IEEE Transactions on Information Theory*, Vol. 16, No. 1, pp. 41–46, 1970.
- **Publisher DOI:** [10.1109/TIT.1970.1054406](https://doi.org/10.1109/TIT.1970.1054406)
- **Closest Mathematical Formulation:** Reject rule based on maximum posterior probability: reject if $\max_k P(Y=k \mid x) < 1 - w_0$, where $w_0$ is the rejection cost.
- **Closest Baseline:** Optimal Bayes classifier with constant rejection threshold.
- **Key Differences from Our Work:**
  - Requires exact knowledge of the posterior distribution $P(Y=k \mid x)$. In one-class visual anomaly detection, no posterior defect probability exists; only non-parametric nearest-neighbor distance $d(p^*, \mathcal{M})$ is available.

### 2.4. A Neyman-Pearson Approach to Statistical Learning
- **Authors:** Clayton Scott, Robert Nowak
- **Publication:** *IEEE Transactions on Information Theory*, Vol. 51, No. 11, pp. 3806–3819, 2005.
- **Publisher DOI:** [10.1109/TIT.2005.859286](https://doi.org/10.1109/TIT.2005.859286)
- **Closest Mathematical Formulation:**
  $$\min_f \mathbb{P}(f(X) = 0 \mid Y = 1) \quad \text{s.t.} \quad \mathbb{P}(f(X) = 1 \mid Y = 0) \le \alpha$$
- **Closest Baseline:** Empirical risk minimization with constrained Lagrange multiplier.
- **Key Differences from Our Work:**
  - Focuses on bounding Type I error (false alarms) in single-task binary classification.
  - Our work balances multiple heterogeneous categories competing for a shared human inspection budget $B$.

---

## 3. Verified Bibliographic Audit Table

| Reference Citation | Venue & Year | Publisher Record / Formal Status | Exact DOI / Persistent Identifier |
| :--- | :--- | :--- | :--- |
| **Alves et al.** | TMLR 2024 | Published Journal Paper | `arXiv:2403.06906` / TMLR 2024 |
| **Reid et al.** | arXiv 2024 | Working Preprint | `10.48550/arXiv.2409.20489` |
| **Chow** | IEEE Trans. Inf. Theory 1970 | Published Journal Paper | `10.1109/TIT.1970.1054406` |
| **Scott & Nowak** | IEEE Trans. Inf. Theory 2005 | Published Journal Paper | `10.1109/TIT.2005.859286` |
| **Charoenphakdee et al.** | ICML 2021 | Conference Proceedings (PMLR v139) | `10.48550/arXiv.2010.11748` |
| **Hendrickx et al.** | Machine Learning 2024 | Published Journal Paper (Springer) | `10.1007/s10994-024-06534-x` |
| **Geifman & El-Yaniv** | NeurIPS 2017 | Conference Proceedings | `10.48550/arXiv.1705.08500` |
| **Roth et al.** | CVPR 2022 | Conference Proceedings (IEEE/CVF) | `10.1109/CVPR52688.2022.01392` |
| **Bergmann et al.** | IJCV 2021 | Published Journal Paper (Springer) | `10.1007/s11263-020-01400-4` |
| **Zou et al.** | ECCV 2022 | Conference Proceedings (Springer) | `10.1007/978-3-031-20056-4_23` |

---

## 4. Novelty Boundary Definition

To prevent reviewer pushback and maintain scientific defensibility:
1. **Do not claim to have invented budget-constrained deferral:** Acknowledge Alves et al. (2024) and Reid et al. (2024).
2. **Do not claim to have invented cost-sensitive rejection:** Acknowledge Chow (1970) and Charoenphakdee et al. (2021).
3. **State the specific, verifiable novelty:**
   - First systematic empirical study of **multi-line resource allocation for frozen nearest-neighbor anomaly detectors** under shared human audit ceilings.
   - Demonstration of how **conformal calibration and marginal expected loss reduction** resolve the score incommensurability failure of raw pooling across heterogeneous visual manifolds.
   - Rigorous benchmarking against strong, simple calibrated baselines (not just strawmen).
