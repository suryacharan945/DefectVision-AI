# Calibrated Patch-Neighborhood Dispersion (CPND) Implementation Report

**Document ID:** `DV-REPORT-CPND-IMPL-V1`  
**Date:** October 31, 2026  
**Auditor:** Lead AI/ML Research Engineer & Algorithm Architect  
**Scope:** Architecture, mathematical formulation, numerical stability, and review-budget triage algorithms  
**Source Code:** [`DefectVisionAI/research/cpnd/cpnd_core.py`](file:///c:/Users/surya/Downloads/Mini%20Project/DefectVisionAI/research/cpnd/cpnd_core.py)  

---

## 1. Executive Summary & Algorithmic Purpose

This report documents the implementation of **Patch-Neighborhood Dispersion (PND)** and the **Conformal Selective Anomaly Detection (CSAD)** selective review engine for DefectVision AI.

Prior project proposals asserted that measuring local patch dispersion in nearest-neighbor memory banks could serve as an effective uncertainty signal to prioritize human audit under fixed inspection budgets ($B \le 20\%$). This module provides the executable reference implementation, verifies its mathematical correctness, and isolates its empirical performance from false theoretical claims.

---

## 2. Mathematical Formulation & Architecture

```
+---------------------------------------------------------------------------------------------------------+
|                                      INPUT IMAGE: X (224 x 224 x 3)                                     |
+---------------------------------------------------------------------------------------------------------+
                                                     |
                                                     v (ResNet-18 Layers 1+2+3, Bilinear Fusion)
+---------------------------------------------------------------------------------------------------------+
|                                    DENSE PATCH TENSOR: P(X) in R^(384 x 28 x 28)                         |
|                                         (784 spatial patch embeddings)                                  |
+---------------------------------------------------------------------------------------------------------+
                                                     |
                                                     v (Exact FAISS IndexFlatL2 on Coreset Memory Bank M)
+---------------------------------------------------------------------------------------------------------+
|                                   TOP-K NEAREST NOMINAL NEIGHBORS (k >= 2)                              |
|                              D_sq = ||m_i - v_(j)||^2  -->  d_(j) = sqrt(max(D_sq, 0))                  |
+---------------------------------------------------------------------------------------------------------+
                         |                                                       |
                         v                                                       v
+---------------------------------------------------+   +---------------------------------------------------+
|               ANOMALY SCORE PIPELINE              |   |               DISPERSION PIPELINE                 |
| d_1nn(m_i) = d_(1)(m_i)                           |   | mu_k = (1/K) * sum(d_(j))                         |
| m^* = argmax_i d_1nn(m_i)                         |   | sigma_k = sqrt((1/K) * sum(d_(j) - mu_k)^2)       |
| S(X) = d_1nn(m^*)                                 |   | PND(m_i) = sigma_k / (mu_k + epsilon)             |
+---------------------------------------------------+   +---------------------------------------------------+
                         |                                                       |
                         +---------------------------+---------------------------+
                                                     |
                                                     v
+---------------------------------------------------------------------------------------------------------+
|                                     IMAGE-LEVEL UNCERTAINTY AGGREGATION                                 |
| 1. Boundary Distance (BL2):  u_dist(X) = 1.0 / (|S(X) - tau_c| + eps_b)                                 |
| 2. Anomaly-Argmax PND:       u_pnd(X) = PND(m^*)                                                        |
| 3. Combined Joint Triage:    u_joint(X) = alpha * RankNorm(u_dist) + (1 - alpha) * RankNorm(u_pnd)      |
+---------------------------------------------------------------------------------------------------------+
                                                     |
                                                     v
+---------------------------------------------------------------------------------------------------------+
|                                        FIXED BUDGET TRIAGE (B <= 20%)                                   |
| Audit top K = floor(B * N) items sorted descending by u(X); deterministic alphabetical tie-breaking.   |
+---------------------------------------------------------------------------------------------------------+
```

### 2.1. Feature Extraction Pipeline
- **Backbone Architecture:** ResNet-18 pre-trained on ImageNet-1k, with frozen weights.
- **Layer Fusion:** Multi-scale feature concatenation of Layer 2 (128 channels, stride 8) and Layer 3 (256 channels, stride 16).
- **Spatial Alignment:** Layer 2 and Layer 3 feature maps are locally average-pooled ($3 \times 3$, stride 1) and bilinearly interpolated to a uniform spatial grid of $28 \times 28$, yielding $D = 384$ channels and $P = 784$ spatial patch embeddings per image.

### 2.2. Exact FAISS Neighbor Retrieval
- **Memory Bank:** Nominal coreset patch features $\mathcal{M} = \{v_1, \dots, v_M\} \subset \mathbb{R}^{384}$.
- **Index:** `faiss.IndexFlatL2(384)` guarantees exact Euclidean nearest-neighbor retrieval without quantization distortion.
- **Conversion Safety:** FAISS returns squared L2 distances $D_{(j)} = \|m_i - v_{(j)}\|_2^2$. The implementation safely converts them via:
  $$d_{(j)} = \sqrt{\max\left(D_{(j)}, 0.0\right)}$$
  eliminating floating-point negative zero artifacts.

### 2.3. Patch-Neighborhood Dispersion (PND)
For each patch $m_i$ and its $K$ nearest nominal neighbors $\{d_{(1)}, \dots, d_{(K)}\}$:
$$\mu_K(m_i) = \frac{1}{K} \sum_{j=1}^K d_{(j)}$$
$$\sigma_K(m_i) = \sqrt{\frac{1}{K} \sum_{j=1}^K \left(d_{(j)} - \mu_K(m_i)\right)^2}$$
$$\text{PND}(m_i) = \frac{\sigma_K(m_i)}{\mu_K(m_i) + \epsilon}$$
where $\epsilon = 10^{-7}$ prevents division-by-zero. When an input patch is identical to a memory bank exemplar ($d_{(1)} = \dots = d_{(K)} = 0$), $\sigma_K = 0$, $\mu_K = 0$, yielding a stable, finite $\text{PND} = 0.0$.

### 2.4. Image-Level Aggregation Strategies
Four distinct aggregation functions are supported:
1. **`argmax_score` (Default):** Evaluates dispersion strictly at the maximally anomalous patch $m^* = \arg\max_{m_i} d_{(1)}(m_i)$. This interrogates the geometric stability of the exact spatial location driving the binary decision.
2. **`max_dispersion`:** Computes $\max_{i} \text{PND}(m_i)$ across all 784 patches.
3. **`mean_top5pct`:** Averages dispersion across the top 5% highest-dispersion patches (top 39 patches).
4. **`p99_dispersion`:** Evaluates the 99th percentile of spatial dispersion.

### 2.5. Joint Uncertainty Formulation
Because classification errors concentrate near the category decision threshold $\tau_c$, boundary distance is integrated via non-parametric rank normalization:
$$\bar{u}_{\text{dist}}(X) = \frac{\text{Rank}\left(u_{\text{dist}}(X)\right) - 1}{N - 1} \in [0, 1]$$
$$\bar{u}_{\text{pnd}}(X) = \frac{\text{Rank}\left(u_{\text{pnd}}(X)\right) - 1}{N - 1} \in [0, 1]$$
$$u_{\text{joint}}(X) = \alpha \cdot \bar{u}_{\text{dist}}(X) + (1 - \alpha) \cdot \bar{u}_{\text{pnd}}(X)$$
with default $\alpha = 0.5$.

---

## 3. Review Budget Selection & Determinism

- **Selection Volume:** Exactly $K = \lfloor B \cdot N \rfloor$ images are selected for budget $B \in (0.0, 1.0]$.
- **Deterministic Tie-Breaking:** Two-stage stable sort (first ascending by `image_id`, then descending by uncertainty) guarantees identical selection regardless of operating system, Python version, or execution order.
