# Phase 7C: Density-Normalized Patch-Neighborhood Dispersion (CPND) Implementation Report

**Document ID:** `DV-PHASE7C-IMPL-V1`  
**Date:** October 31, 2026  
**Status:** **FROZEN / COMPLETED**  
**Module Location:** `DefectVisionAI/research/cpnd/cpnd_density_norm.py`  
**Contract Reference:** `research/protocols/Q1_EXPERIMENT_PROTOCOL_V2.json`

---

## 1. Executive Motivation: Resolving the Manifold Sparsity Failure Mode

In Phase 7B, experimental evaluation revealed a critical failure mode of raw Patch-Neighborhood Dispersion:
- **The Manifold Sparsity Artifact:** Raw dispersion $U(p) = \frac{\sigma_K(p)}{\mu_K(p) + \epsilon}$ calculates the relative spread of neighbor distances. In low-density peripheral regions of the nominal manifold, normal patches naturally experience non-uniform nearest-neighbor distances. Consequently, completely normal patches in sparse manifold regions produce high raw dispersion, misdirecting human audit budgets to benign items and degrading Error Capture Rate (ECR).
- **The Dilution of Boundary Proximity:** Naively combining boundary distance $|S(X) - \tau_c|$ with uncalibrated raw dispersion diluted the decision-boundary signal, dropping ECR from $29.03\%$ (distance alone) down to $11.29\%$ (joint).

Phase 7C implements a controlled algorithmic revision: **Local-Density-Normalized CPND with Boundary Gating**.

---

## 2. Mathematical & Algorithmic Formulation

### 2.1. Self-Neighbor-Excluded Nominal Reference Precomputation
Let $\mathcal{M} = \{m_1, m_2, \dots, m_M\} \subset \mathbb{R}^D$ be the nominal training coreset for a given category.

To establish what dispersion is "normal" in each local region of feature space without test leakage:
1. For each training vector $m_j \in \mathcal{M}$, query its $k_{\text{ref}} + 1$ nearest neighbors in $\mathcal{M}$ under the Euclidean metric:
   $$D(m_j) = \text{Top-}(k_{\text{ref}}+1) \text{NN}(m_j, \mathcal{M})$$
2. **Self-Neighbor Exclusion:** The 1st nearest neighbor is $m_j$ itself with distance $0.0$. We discard this self-neighbor column, retaining genuine distinct nominal neighbors $\{m_{j_1}, \dots, m_{j_{k_{\text{ref}}}}\}$.
3. Compute the nominal reference dispersion $U_{\text{train}}(m_j)$:
   $$\mu_K(m_j) = \frac{1}{k_{\text{ref}}} \sum_{r=1}^{k_{\text{ref}}} d(m_j, m_{j_r})$$
   $$\sigma_K(m_j) = \sqrt{\frac{1}{k_{\text{ref}}} \sum_{r=1}^{k_{\text{ref}}} (d(m_j, m_{j_r}) - \mu_K(m_j))^2}$$
   $$U_{\text{train}}(m_j) = \frac{\sigma_K(m_j)}{\mu_K(m_j) + \epsilon}$$
   where $\epsilon = 10^{-7}$. Precomputing $U_{\text{train}} \in \mathbb{R}^M$ requires $\sim 2.1$ seconds per category and is frozen.

### 2.2. Query Patch Local Density Normalization
Given a query image $X$ generating patch feature embeddings $\{p_1, \dots, p_P\} \subset \mathbb{R}^D$:
1. For each patch $p_i$, retrieve its $K$ nearest neighbors in $\mathcal{M}$: $\{m_{i_1}, \dots, m_{i_K}\}$ and compute raw patch dispersion:
   $$U(p_i) = \frac{\sigma_K(p_i)}{\mu_K(p_i) + \epsilon}$$
2. Gather the nominal training dispersions of these $K$ neighbors:
   $$\mathbf{u}_{\text{local}}(p_i) = \{U_{\text{train}}(m_{i_1}), U_{\text{train}}(m_{i_2}), \dots, U_{\text{train}}(m_{i_K})\}$$
3. Compute robust local reference statistics:
   $$\text{median}_{\text{local}}(p_i) = \text{median}(\mathbf{u}_{\text{local}}(p_i))$$
   $$\text{MAD}_{\text{local}}(p_i) = \text{median}\left( |\mathbf{u}_{\text{local}}(p_i) - \text{median}_{\text{local}}(p_i)| \right) \times 1.4826$$
4. Construct the Density-Normalized Patch Dispersion:
   $$U_{\text{norm}}(p_i) = \frac{U(p_i) - \text{median}_{\text{local}}(p_i)}{\max(\text{MAD}_{\text{local}}(p_i), 10^{-5})}$$

**Interpretation:** $U_{\text{norm}}(p_i)$ measures how many robust standard deviations the query patch's dispersion deviates from nominal patches in that exact manifold neighborhood. If a patch falls into a sparse nominal region where nominal training patches also exhibit high dispersion, $\text{median}_{\text{local}}$ is correspondingly high, suppressing false uncertainty alarms.

### 2.3. Image-Level Grounding
Following Phase 7B ablation findings (where global max patch aggregation produced $0\%$ ECR due to noise accumulation), dispersion is grounded exclusively in the candidate defect location:
$$p^* = \arg\max_{i \in \{1,\dots,P\}} d(p_i, \mathcal{M})$$
$$S(X) = d(p^*, \mathcal{M})$$
$$U_{\text{norm}}(X) = U_{\text{norm}}(p^*)$$

### 2.4. Boundary-Gated Ranking Policies
Instead of unconstrained linear combination, Phase 7C establishes two disciplined boundary-gated policies parameterized by boundary half-width $\delta$:

1. **Policy D1 — Tiered Boundary Gating (Hard Band):**
   An image belongs to the boundary band if:
   $$\text{InBand}(X) = \mathbb{I}(|S(X) - \tau_c| \le \delta)$$
   - **Tier 1 ($\text{InBand} = 1$):** Prioritized first in human review, ordered by $U_{\text{norm}}(X)$ descending.
   - **Tier 2 ($\text{InBand} = 0$):** Audited only after Tier 1 is exhausted, ordered by $-|S(X) - \tau_c|$ descending.
2. **Policy D2 — Soft Gaussian Boundary Gating:**
   $$U_{\text{gated}}(X) = \exp\left( -\frac{(S(X) - \tau_c)^2}{2\delta^2} \right) \cdot U_{\text{norm}}(X)$$
   Images far from the decision boundary have their dispersion exponentially damped toward zero.

---

## 3. Implementation Verification & Defenses

1. **Self-Neighbor Exclusion:** Enforced via `index.search(memory_bank, ref_k + 1)[:, 1:]`. Verified by unit test `test_self_neighbor_exclusion`.
2. **Zero-Distance Guard:** Exact duplicates or 0-distance neighbors evaluated under `sqrt(max(D_sq, 0.0))` with denominator stabilizer $\epsilon = 10^{-7}$. Verified by unit test `test_zero_distance_stability`.
3. **Deterministic Tie-Breaking:** Two-stage stable sort (first ascending by `image_id`, then descending by uncertainty key). Verified by unit test `test_deterministic_tie_breaking`.
4. **Disambiguated Yield Evaluation:** `evaluate_selective_review` computes both `defect_review_yield` and `error_review_yield` independently. Verified by unit test `test_yield_metrics_disambiguation`.
