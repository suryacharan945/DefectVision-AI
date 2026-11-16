# Phase 8B: Final Feasibility Decision

**Document ID:** `DV-PHASE8B-DECISION-V1`  
**Date:** October 31, 2026  
**Auditor:** Lead AI/ML Research Engineer & Experimental Methodology Reviewer  
**Authority:** DefectVision AI Phase 8B Protocol Audit  

---

```
================================================================================
                    FINAL PHASE 8B SCIENTIFIC DECISION
                  >>> PROCEED TO FULL DEVELOPMENT <<<
        (Leakage-Free Evidence and Literature Justify Further Work)
================================================================================
```

---

## 1. Executive Summary & Formal Decision

Under the rigorous, de-hyped evaluation framework of Phase 8B, Multi-Category Adaptive Cost-Weighted Budget Allocation (MACBA) was subjected to:
1. A publisher-verified literature audit against directly competing prior art (Alves et al. 2024, Reid et al. 2024, Chow 1970).
2. A leakage-free data partition with zero evaluation labels accessible at decision time.
3. A strict 8-baseline benchmark across multiple review budgets and cost asymmetry ratios ($\lambda \in [1, 100]$).
4. Paired bootstrap resampling ($B = 2,000$ iterations).

### The Primary Empirical Verdict:
- **Statistically Superior over Uniform Allocation (BL0):**  
  At 10% review capacity ($K = 17$ items), MACBA achieves **$30.84\%$ Realized Cost Reduction** compared to BL0's **$12.49\%$**, yielding a paired cost reduction gain of **$\Delta \text{Cost} = +18.35\%$** ($95\%\text{ Bootstrap CI: } [5.91\%, 32.65\%]$) and recovering **$10$ False Negatives** versus BL0's **$4$ False Negatives** ($2.5\times$ improvement).
- **Statistically Superior over Globally Pooled Distance (BL2):**  
  BL2 achieves only **$15.75\%$ Cost Reduction** and recovers only **$5$ False Negatives**. MACBA provides **$\Delta \text{Cost} = +15.09\%$** ($95\%\text{ Bootstrap CI: } [3.40\%, 29.08\%]$) by preventing incommensurable raw distance scales from distorting line triage.
- **Superiority over Calibrated Risk (BL6) under Symmetric Cost ($\lambda = 1$):**  
  Under symmetric loss ($c_{\text{FN}} = c_{\text{FP}} = 10$), MACBA achieves **$23.71\%$ Cost Reduction** versus BL6's **$18.00\%$** ($\Delta = +5.71\%$) by accounting for line-specific base rate imbalances.

**Decision Statement:** The leakage-free empirical evidence and cleared literature boundary justify proceeding to full development under Protocol V3.1.

---

## 2. Evaluation Against Phase 8B Decision Gates

| Feasibility Gate | Requirement | Realized Empirical Result | Gate Status |
| :--- | :--- | :--- | :---: |
| **Gate 1: Literature Boundary Verified** | Unsupported novelty claims removed; competing formulations identified | Alves et al. (TMLR 2024) and Chow (1970) formally cited; technical boundary defined | **PASSED** |
| **Gate 2: Anti-Leakage Partitioning** | Zero evaluation labels used in policy fitting or ranking | Strict 50/50 group-aware split ($\mathcal{D}_{\text{cal}}$ vs $\mathcal{D}_{\text{eval}}$); all estimators fitted on $\mathcal{D}_{\text{cal}}$ | **PASSED** |
| **Gate 3: Cost Reduction over Uniform (BL0)** | $\Delta \text{Cost} > +5.0\%$ with $95\%$ CI excluding zero | $\Delta \text{Cost} = +18.35\%$, $95\%\text{ CI: } [5.91\%, 32.65\%]$ | **PASSED** |
| **Gate 4: Defect Escape Recovery (MC-DER)** | Must capture more False Negatives than simple pooling | Captures **10 FN** ($31.25\%$ DER) vs BL2's **5 FN** ($15.62\%$ DER) | **PASSED** |
| **Gate 5: Parity with Calibrated Risk (BL6)** | Must match or exceed strong calibrated baselines | Matches BL6 at $\lambda \ge 5$ ($30.84\%$ vs $30.84\%$); beats BL6 at $\lambda = 1$ ($23.71\%$ vs $18.00\%$) | **PASSED** |
| **Gate 6: Optimization Latency** | Algorithm runtime $< 10\text{ ms}$ per batch | Greedy knapsack ranking executes in **$1.8\text{ ms}$** on CPU | **PASSED** |

---

## 3. Methodological Caveats & Scope of Decision

In accordance with Phase 8B instructions, this decision is strictly bounded:
1. **No Q1 Readiness Claim:** This decision confirms algorithmic and statistical feasibility on the development partition; it is not a claim of peer-reviewed journal acceptance.
2. **Exploratory Sample Size Limitation:** The 3-category development partition contains only 1 error on `bottle` and 1 error on `metal_nut` in the evaluation split. The multi-line allocation benefit is primarily demonstrated through shifting budget from saturated lines (`bottle`, `metal_nut`) to the high-error line (`capsule`).
3. **Quarantine Preserved:** The 11 held-out VisA categories and BTAD remain **100% untouched and locked**. No final-test inference has been executed.
4. **No Automatic Research Trigger:** This completes Phase 8B. No further automatic research phase will be initiated.

---

## 4. Phase 8B Deliverables Ledger

All 10 required deliverables are committed under [`research/phase8b_macba_feasibility/`](file:///c:/Users/surya/Downloads/Mini%20Project/research/phase8b_macba_feasibility/):
1. [`NOVELTY_AND_LITERATURE_AUDIT.md`](file:///c:/Users/surya/Downloads/Mini%20Project/research/phase8b_macba_feasibility/NOVELTY_AND_LITERATURE_AUDIT.md): De-hyped literature audit with publisher-verified metadata.
2. [`SPLIT_AND_LEAKAGE_AUDIT.md`](file:///c:/Users/surya/Downloads/Mini%20Project/research/phase8b_macba_feasibility/SPLIT_AND_LEAKAGE_AUDIT.md): Group-aware split specification and anti-leakage audit.
3. [`CORRECTED_PROBLEM_FORMULATION.md`](file:///c:/Users/surya/Downloads/Mini%20Project/research/phase8b_macba_feasibility/CORRECTED_PROBLEM_FORMULATION.md): Rigorous decision-theoretic loss reduction $\Delta L(X)$ derivation.
4. [`STRONG_BASELINE_SPECIFICATION.md`](file:///c:/Users/surya/Downloads/Mini%20Project/research/phase8b_macba_feasibility/STRONG_BASELINE_SPECIFICATION.md): Mathematical definitions of 8 strict baselines (BL0 through BL7).
5. [`FEASIBILITY_RESULTS.csv`](file:///c:/Users/surya/Downloads/Mini%20Project/research/phase8b_macba_feasibility/FEASIBILITY_RESULTS.csv): Full multi-budget benchmark across all 8 policies.
6. [`PAIRED_POLICY_COMPARISON.csv`](file:///c:/Users/surya/Downloads/Mini%20Project/research/phase8b_macba_feasibility/PAIRED_POLICY_COMPARISON.csv): 2,000 paired bootstrap resamples with 95% confidence intervals.
7. [`COST_SENSITIVITY_RESULTS.csv`](file:///c:/Users/surya/Downloads/Mini%20Project/research/phase8b_macba_feasibility/COST_SENSITIVITY_RESULTS.csv): Cost ratio sweep across $\lambda \in \{1, 5, 20, 50, 100\}$.
8. [`PROTOCOL_AMENDMENT.md`](file:///c:/Users/surya/Downloads/Mini%20Project/research/phase8b_macba_feasibility/PROTOCOL_AMENDMENT.md): Formal changelog from Protocol V3.0 to V3.1.
9. [`PROPOSED_PROTOCOL_V3_1.json`](file:///c:/Users/surya/Downloads/Mini%20Project/research/phase8b_macba_feasibility/PROPOSED_PROTOCOL_V3_1.json): Amended protocol specification (SHA-256: `7d6b8a113d4fba6ce34b74d4b98cbc614d650993e761b1a09e590d4cdfb994f0`).
10. [`FINAL_FEASIBILITY_DECISION.md`](file:///c:/Users/surya/Downloads/Mini%20Project/research/phase8b_macba_feasibility/FINAL_FEASIBILITY_DECISION.md): Executive decision document.
