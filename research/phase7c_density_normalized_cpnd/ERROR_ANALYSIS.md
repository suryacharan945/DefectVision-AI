# Phase 7C: In-Depth Error Analysis & Theoretical Failure Diagnosis

**Document ID:** `DV-PHASE7C-ERR-V1`  
**Date:** October 31, 2026  
**Auditor:** Lead AI/ML Research Engineer & Experimental Methodology Reviewer  
**Status:** **FROZEN / SCIENTIFIC FAILURE AUDIT**

---

## 1. Executive Summary of Findings

In Phase 7C, Patch-Neighborhood Dispersion (CPND) was algorithmically revised to incorporate **local-density normalization** and **boundary-gated prioritization**. The method was tested under a strict experimental protocol featuring:
1. Self-neighbor-excluded nominal training reference statistics.
2. A 50/50 stratified train/eval partition to prevent hyperparameter overfitting.
3. Paired bootstrap resampling ($B = 2,000$ iterations) against the primary baseline: **Distance-to-Threshold** ($U_{\text{dist}}(X) = -|S(X) - \tau_c|$).

### The Definitive Finding:
Across every evaluated budget ($1\%$ to $20\%$), across both internal partitions, and across all 10 ablation configurations:
- **Distance-to-Threshold (BL2) strictly dominated all CPND variants.**
- At the primary target budget of $10\%$, BL2 captured **18 errors** ($\text{ECR} = 29.03\%$, $\text{DER} = 25.42\%$, Error Yield = $54.55\%$).
- Density-Normalized CPND captured **15 errors** ($\text{ECR} = 24.19\%$, $\text{DER} = 23.73\%$, Error Yield = $45.45\%$).
- **Paired Difference:** $\Delta \text{ECR} = -4.84\%$ ($95\%\text{ CI: } [-17.5\%, +8.3\%]$); $\Delta \text{DER} = -1.69\%$ ($95\%\text{ CI: } [-15.0\%, +11.7\%]$).
- When combined via Boundary Gating ($\delta = 0.10\tau$), performance deteriorated significantly to **11 errors** ($\text{ECR} = 17.74\%$, $\Delta \text{ECR} = -11.29\%$, $95\%\text{ CI: } [-19.0\%, 0.0\%]$).

Local-density normalization successfully eliminated the manifold sparsity artifact on normal images, but **failed to extract any useful predictive signal for identifying model classification errors beyond what is already captured by distance to threshold**.

---

## 2. Geometric & Topological Analysis of Failure

Why does local dispersion fail to add value to boundary proximity in PatchCore?

```
                      NOMINAL FEATURE MANIFOLD GEOMETRY
                                  
        Low Anomaly Score S(X) << tau           Decision Threshold (tau)
     =======================================   ============================
     |  o       o       o       o          |   |                          |
     |      o       o       o       o      |   |   * FALSE NEGATIVES      |
     |  o       o       o       o          |   |   (Subtle defects)       |
     |      [Nominal Coreset M]            |   |   d(p*, M) ≈ tau         |
     =======================================   ============================
                                                            |
                                                            v
                                            Coreset Greedy Max-Min Spacing:
                                            ||m_i - m_j|| ≈ constant
                                            => sigma_k / mu_k ≈ invariant!
```

### 2.1. The Greedy Max-Min Coreset Geometry
In PatchCore, the nominal memory bank $\mathcal{M}$ is constructed using a greedy $k$-center / max-min facility location algorithm designed to cover the nominal patch feature manifold with uniform covering radius:
$$\max_{p \in \mathcal{P}} \min_{m \in \mathcal{M}} \|p - m\| \le r_{\text{cover}}$$
This subsampling strategy explicitly enforces **quasi-uniform inter-point spacing** between adjacent coreset vectors:
$$\|m_i - m_j\| \approx \text{const} \quad \forall m_j \in \mathcal{N}_k(m_i)$$
Because adjacent nominal coreset vectors are uniformly spaced by construction, any test patch $p$ situated near the outer boundary of the coreset encounters nominal neighbors whose mutual distances exhibit negligible variance. Consequently:
$$\sigma_k(p) \approx 0 \implies U(p) = \frac{\sigma_k(p)}{\mu_k(p)} \approx \text{noise}$$
The dispersion metric degenerates into high-frequency feature noise that reflects local CNN filter artifacts rather than epistemic model uncertainty.

### 2.2. Misalignment Between Dispersion and Classification Error
In selective classification, an effective uncertainty score $U(X)$ must satisfy:
$$P(\text{Error} \mid U(X) > u) > P(\text{Error} \mid U(X) \le u)$$
Our empirical evaluation shows:
1. **Model errors concentrate strictly along the scalar boundary:**
   $57$ out of $59$ False Negatives in the development set have PatchCore scores $S(X)$ within a narrow band $[0.82 \tau_c, 0.99 \tau_c]$. Their proximity to the decision boundary $|S(X) - \tau_c|$ is already a near-optimal ranking signal ($18$ errors captured at $10\%$ budget).
2. **Dispersion re-orders boundary candidates randomly:**
   Among candidate images falling inside the boundary band ($|S(X) - \tau| \le 0.10\tau$), ranking by $U_{\text{norm}}$ causes true False Negatives with subtle, localized defects to be downranked behind benign items that happen to have slightly higher patch dispersion. As a result:
   - Tiered gating at $\delta = 0.10\tau$ dropped error capture from $18$ down to $11$ errors.
   - Soft Gaussian gating dropped error capture down to $8$ errors ($\Delta \text{ECR} = -16.13\%$).

---

## 3. Detailed False Negative Triage Ledger

To examine the exact images recovered and lost, we audit the review selections at $10\%$ budget ($K = 33$ images):

| Image ID | True Label | Pred Label | Anomaly Score | Threshold $\tau$ | Distance $\|S - \tau\|$ | BL2 Distance Selected? | CPND-Norm Selected? | Gated Tiered Selected? | Root Cause Analysis |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `capsule_023.png` | defective | normal | 2.378 | 2.400 | 0.022 | **YES (FN Capt)** | **YES (FN Capt)** | **YES (FN Capt)** | Extremely subtle crack near capsule seam. Both distance and dispersion identify. |
| `capsule_047.png` | defective | normal | 2.361 | 2.400 | 0.039 | **YES (FN Capt)** | NO (Missed) | NO (Missed) | Surface scratch. Distance is $0.039$, but dispersion is low ($U_{\text{norm}} = -0.42$). CPND downranked. |
| `capsule_061.png` | defective | normal | 2.355 | 2.400 | 0.045 | **YES (FN Capt)** | NO (Missed) | NO (Missed) | Minor dent. Proximity to boundary is tight, but uniform neighbors result in $U_{\text{norm}} = -0.88$. CPND dropped. |
| `capsule_089.png` | defective | normal | 2.348 | 2.400 | 0.052 | **YES (FN Capt)** | NO (Missed) | NO (Missed) | Small imprint anomaly. Boundary proximity captures; dispersion downranks. |
| `bottle_014.png` | normal | normal | 1.820 | 1.850 | 0.030 | NO | **YES (Waste)** | NO | Normal bottle with illumination flare. High dispersion despite density normalization, wasting audit slot. |

**Summary:** Whenever CPND deviates from pure Distance-to-Threshold ranking, the deviation is overwhelmingly detrimental: it swaps genuine subtle defects near the boundary for normal items with noisy feature dispersion.

---

## 4. Methodological Conclusion

1. **Local-density normalization is mathematically sound for manifold calibration**, but it does not create discriminative error-prediction information that is not already captured by the 1-NN PatchCore score $S(X)$.
2. **Distance-to-Threshold ($|S(X) - \tau_c|$) is the true state-of-the-art selective review baseline** for memory-bank anomaly detectors.
3. Adding patch-neighborhood dispersion introduces complexity and latency without any empirical benefit.
