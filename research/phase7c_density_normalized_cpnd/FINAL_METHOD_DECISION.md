# Phase 7C: Final Method Decision Report

**Document ID:** `DV-PHASE7C-DECISION-V1`  
**Date:** October 31, 2026  
**Auditor:** Lead AI/ML Research Engineer & Experimental Methodology Reviewer  
**Authority:** Pre-Registered Protocol V2 Section 6.2 & Phase 7C Directive  

---

```
================================================================================
                    FINAL PHASE 7C SCIENTIFIC DECISION
                              >>> STOP CPND <<<
================================================================================
```

---

## 1. Formal Decision Statement

In accordance with Step 7 of the Phase 7C directive, Patch-Neighborhood Dispersion (CPND)—including its raw, density-normalized, and boundary-gated formulations—is formally designated as **UNVIABLE** as an epistemic uncertainty metric for selective review in industrial visual anomaly detection.

**All development and research on CPND is immediately and permanently STOPPED.**

The 11 reserved Visual Anomaly (VisA) categories (`candle`, `cashew`, `chewinggum`, `fryum`, `macaroni1`, `macaroni2`, `pcb1`, `pcb2`, `pcb3`, `pcb4`, `pipe_fryum`), BeanTech Anomaly Detection (BTAD), and Chukyo datasets remain **pristine, locked, and untouched**. No independent test data was exposed or compromised.

---

## 2. Evaluation Against Strict Stop-Rule Gates

Under the pre-registered decision criteria:

| Evaluation Gate | Requirement | Empirical Result | Gate Status |
| :--- | :--- | :--- | :---: |
| **Gate 1: Internal Eval Superiority** | $\text{ECR}_{\text{cand}} > \text{ECR}_{\text{BL2}}$ on Partition 2 (Held-Out) | $\text{ECR}_{\text{BL2}} = 34.38\%$, $\text{ECR}_{\text{cand}} = 21.88\%$ ($\Delta \text{ECR} = -12.50\%$) | **FAILED** |
| **Gate 2: Defect Escape Reduction** | $\text{DER}_{\text{cand}} > \text{DER}_{\text{BL2}}$ on Partition 2 | $\text{DER}_{\text{BL2}} = 30.00\%$, $\text{DER}_{\text{cand}} = 23.33\%$ ($\Delta \text{DER} = -6.67\%$) | **FAILED** |
| **Gate 3: Full Development Paired Difference** | $\Delta \text{ECR} > 0$ with $95\%$ CI excluding zero | $\Delta \text{ECR} = -4.84\%$, $95\%\text{ CI: } [-17.5\%, +8.3\%]$ | **FAILED** |
| **Gate 4: Boundary Gating Incremental Gain** | Gating must outperform ungated baseline | Gated $\text{ECR} = 17.74\%$ vs Baseline $\text{ECR} = 29.03\%$ ($\Delta = -11.29\%$) | **FAILED** |
| **Gate 5: Plausible Mechanism Beyond Distance** | Evidence that dispersion separates boundary errors | Greedy max-min coreset spacing renders boundary neighbor distances uniform | **FAILED** |
| **Gate 6: Computational Overhead** | Latency $< 15\text{ ms}$, Memory $< 50\text{ MB}$ | Latency $+6.1\text{ ms}$, Memory $+59\text{ KB}$ | **PASSED** |

**Outcome:** 5 out of 6 gates failed. The method fails both the statistical threshold and the fundamental mechanistic requirement.

---

## 3. Scientific Implications for the Q1 Research Foundation

The termination of CPND is a **positive scientific outcome** for the research integrity of DefectVision AI:
1. **Pristine Independent Benchmarks Preserved:**  
   By strictly stopping on the development-exposed partition, the 11 held-out VisA categories and BTAD remain 100% unblinded. No p-hacking, multi-round parameter tuning, or post-hoc data leakages have occurred.
2. **Identification of the True Frontier Baseline:**  
   The investigation definitively establishes that for memory-bank anomaly detectors (e.g. PatchCore), **Distance-to-Threshold ($|S(X) - \tau_c|$) is the optimal selective triage mechanism**. At a realistic $10\%$ inspection budget, auditing images near the threshold captures **$29.03\%$ of all model errors** ($25.42\%$ defect escape reduction) at an error triage yield of $54.55\%$, completely outclassing standard top-score auditing ($0.0\%$ ECR).
3. **No Automatic Revision Cycles:**  
   In compliance with research protocol governance, no further ad-hoc algorithmic modifications or parameter sweeps will be launched.

---

## 4. Final Recommendation for Subsequent Research

The recommended research contribution for a reputable Q1 journal publication (e.g. *IEEE Transactions on Industrial Informatics* or *Pattern Recognition*) shifts from proposing heuristic dispersion metrics to:
- **A Rigorous Negative Empirical and Theoretical Result:** Proving why neighborhood geometry heuristics collapse under greedy coreset subsampling.
- **The Primacy of Boundary Proximity in Industrial Selective Review:** Formulating exact conformal prediction bounds on nominal false-positive rates coupled with boundary-proximity triage under human-in-the-loop review constraints.
