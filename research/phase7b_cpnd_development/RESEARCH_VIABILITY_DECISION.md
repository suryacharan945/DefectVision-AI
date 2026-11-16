# DefectVision AI — Phase 7B Research Viability Decision

**Document ID:** `DV-DECISION-RESEARCH-VIABILITY-V1`  
**Date:** October 31, 2026  
**Auditor:** Lead AI/ML Research Engineer & Experimental Methodology Reviewer  
**Release Anchor:** `v1.0.0-research-prototype` (Commit `78ecd20`)  
**Protocol Anchor:** `research/protocols/Q1_EXPERIMENT_PROTOCOL_V2.json`  
(SHA-256: `effd05679ceb637073b6e7081633f2f51ebf2deaece0010041d33b8b07d19ab1`)  

---

## 1. Formal Research Recommendation

# **FINAL RECOMMENDATION: REVISE METHOD**

*(Technically sound engineering implementation, but insufficient development performance to justify unblinding the independent held-out benchmark in its current formulation.)*

### Core Justification:
1. **Engineering Implementation Certified:** The CPND module ([`DefectVisionAI/research/cpnd/cpnd_core.py`](file:///c:/Users/surya/Downloads/Mini%20Project/DefectVisionAI/research/cpnd/cpnd_core.py)) is computationally robust, stable, deterministic, and passes all 12 unit and integration tests.
2. **Empirical Reality on Development Data:**  
   - **Baseline 1 (Top Anomaly Score):** Completely collapses ($\text{ECR} \le 1.5\%$) because severe defects with high anomaly scores are already correctly identified by the automated model.
   - **Baseline 2 (Distance-to-Threshold):** Serves as the dominant error capture mechanism ($\text{ECR} = 12\% - 24\%$ at budgets $B \in [0.10, 0.20]$), capturing borderline defect escapes.
   - **Raw Patch Dispersion (PND):** Suffer from the **manifold sparsity failure mode**. Normal patches in sparse peripheral regions of the nominal coreset produce high dispersion, misallocating audit budget to unambiguous normal items.
   - **Joint Boundary + Dispersion:** While combining PND with boundary distance ($u_{\text{joint}}$) prevents total collapse, it provides only modest incremental lift ($\sim 1\% - 2\%$ delta) over scalar boundary distance alone, which does not meet the pre-registered threshold for burning the untouched VisA benchmark.
3. **Strategic Research Imperative:** Exposing the untouched 11 VisA categories (10,119 images) to the current unregularized PND formulation would result in an underwhelming experimental outcome. The method must be revised to incorporate **local manifold density weighting** and **boundary conditioning** before any independent evaluation is authorized.

---

## 2. Detailed Performance & Scientific Evaluation

```
+---------------------------------------------------------------------------------------------------------+
|                                  SELECTIVE REVIEW PERFORMANCE AT B = 10%                                |
+---------------------------------------------------------------------------------------------------------+
| Policy / Method                  | Error Capture Rate | Defect Escape Red. | Primary Mechanism          |
+----------------------------------+--------------------+--------------------+----------------------------+
| 1. Uniform Random Audit (BL0)    |       7.5% - 8.1%  |        7.9% - 8.1% | Stochastic Baseline        |
| 2. Top Anomaly Score (BL1)       |       0.0% - 1.5%  |        0.0% - 1.5% | FAILS (Obvious Defects)    |
| 3. Distance-to-Threshold (BL2)   |      11.9% - 21.6% |        7.9% - 21.6% | BOUNDARY PROXIMITY         |
| 4. Raw PND Only (CPND-Raw)       |       4.5% - 6.8%  |        3.2% - 5.5% | Distorted by Sparsity      |
| 5. Calibrated PND (CPND-Calib)   |       6.0% - 8.2%  |        4.8% - 7.1% | Normal-only Quantile       |
| 6. Joint Boundary + PND          |      12.5% - 22.8% |        8.5% - 22.4% | Modest lift over BL2       |
+---------------------------------------------------------------------------------------------------------+
| Reference: Supervised Margin     |      91.9%         |       90.9%        | Oracle (Requires Labels)   |
+---------------------------------------------------------------------------------------------------------+
```

---

## 3. Why Proceeding to Independent Evaluation is Blocked

Under the governance rules of Protocol V2:
- The untouched 11 VisA categories (10,119 images) and BTAD (2,830 images) represent our **single, non-renewable asset** for establishing authentic external validity in a Q1 journal (*IEEE Transactions on Industrial Informatics* or *Pattern Recognition*).
- An unblinded test can be run **exactly once**.
- Development evidence conclusively demonstrates that raw patch dispersion is confounded by nominal coreset sparsity. Proceeding to independent evaluation today would confirm on VisA what we already know on MVTec: that scalar boundary distance ($|S(X) - \tau_c|$) does the heavy lifting, while raw PND adds negligible statistical value.

---

## 4. Required Algorithmic Revisions for Protocol V3

To convert CPND into a genuinely publishable contribution, the following algorithmic modifications are mandated:

1. **Local Density Regularization:**  
   Replace raw distance standard deviation with a density-normalized relative dispersion:
   $$\text{PND}_{\text{dense}}(m) = \frac{\sigma_K(m)}{\mu_K(m) \cdot \hat{\rho}_K(m)}$$
   where $\hat{\rho}_K(m)$ is the local nominal point density estimated from the $K$-nearest neighbor radius.
2. **Boundary-Band Gating:**  
   Apply dispersion scoring strictly as a secondary ranking feature within the boundary confidence band $\mathcal{B}_\delta = \{X : |S(X) - \tau_c| \le \delta\}$, setting dispersion uncertainty to zero outside the band.
3. **Controlled Re-Evaluation on VisA Capsules:**  
   Validate the revised $\text{PND}_{\text{dense}}$ formulation on the authorized development partition (VisA `capsules` + MVTec `capsule`) to demonstrate a statistically significant $+5.0\%$ ECR lift over Distance-to-Threshold before requesting independent evaluation authorization.
