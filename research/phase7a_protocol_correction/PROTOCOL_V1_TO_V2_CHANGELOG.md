# Pre-Registration Protocol Changelog: V1.0.0 to V2.0.0

**Document ID:** `DV-PROTOCOL-CHANGELOG-V1-TO-V2`  
**Date:** October 31, 2026  
**Auditor:** Lead AI/ML Research Engineer & Experimental Methodology Reviewer  
**Prior Frozen Artifact:** `research/protocols/Q1_EXPERIMENT_PROTOCOL_V1.json` (SHA-256: `e3cfed296037ba59e5cc371f8ae7815884e7ea3cdfd7a10b0d18fd4c4e9fae6d`)  
**Revised Frozen Artifact:** `research/protocols/Q1_EXPERIMENT_PROTOCOL_V2.json` (SHA-256: `effd05679ceb637073b6e7081633f2f51ebf2deaece0010041d33b8b07d19ab1`)  

---

## 1. Executive Summary of Protocol Revisions

Protocol V2 amends and corrects critical scientific, theoretical, and data-lineage inaccuracies identified in Protocol V1 during the Phase 7A integrity audit. Protocol V1 remains permanently preserved in the repository for provenance auditability.

---

## 2. Itemized Changelog Matrix

| Section | Protocol V1 (Superseded) | Protocol V2 (Adopted & Frozen) | Methodological Rationale |
| :--- | :--- | :--- | :--- |
| **VisA Dataset Qualification** | Claimed entire VisA dataset ($10,821$ images, $12$ categories) was "UNTOUCHED (0 prior executions)". | Segregated VisA into: <br>1. `capsules` ($702$ images) $\to$ **Development / Ablation Suite**.<br>2. 11 remaining categories ($10,119$ images) $\to$ **Untouched Held-Out Benchmark**. | Forensic audit revealed that VisA `capsules` underwent model fitting, threshold calibration, and test evaluation in Google Drive experiments (`visa_development_v2` and `visa_independent_validation_v1`). |
| **Conformal Guarantees on Defect Escape** | Claimed split conformal prediction provides "distribution-free finite-sample defect escape guarantees: $\mathbb{P}(\text{Escape} > \alpha) \le \delta$". | Replaced with mathematically accurate statement: Conformal calibration on nominal samples guarantees only that nominal $\text{FPR} \le \alpha$. **No distribution-free error capture guarantee exists for defects** because defects violate exchangeability ($Q_{\text{defect}} \ne P_{\text{normal}}$). | Eliminates false statistical claims regarding distribution-free defect capture that would cause immediate peer review rejection. |
| **Human Review Budget Constraints** | Conflated variable-set conformal prediction with fixed-budget review triage. | Formally distinguished conformal risk control from selective classification under fixed budgets ($B \le 20\%$). Review effectiveness is governed by uncertainty-error ranking concordance. | In manufacturing, review volume $K = \lfloor B \cdot N \rfloor$ is fixed by labor capacity, inverting standard conformal prediction into an empirical ranking problem. |
| **Publication Success Criterion** | Implicitly relied on achieving a static threshold ($\ge 35\%$ ECR). | Defined formal non-parametric hypothesis testing: CPND must achieve statistically significant superiority over Distance-to-Threshold (BL2) via two-tailed paired Wilcoxon signed-rank test ($p < 0.05$) with Holm-Bonferroni correction. | Replaces arbitrary numerical thresholds with statistically rigorous hypothesis testing. |
| **Ablation & Joint Formulation** | Treated CPND as an independent standalone triage metric. | Mandated ablation of CPND against Distance-to-Threshold (BL2) and introduced joint evaluation: $u_{\text{joint}}(X) = \alpha u_{\text{BL2}}(X) + (1 - \alpha) u_{\text{CPND}}(X)$. | Patch dispersion alone fails to capture boundary proximity; it must be proven beneficial beyond scalar decision distance. |
| **Negative Result / Stopping Protocol** | Lacked an explicit failure reporting protocol. | Explicitly codified that if CPND fails to outperform BL2 ($p \ge 0.05$), the outcome will be published as a definitive negative result regarding patch-space dispersion heuristics. | Prevents post-hoc data dredging or cherry-picking of hyperparameters. |

---

## 3. Cryptographic Verification Sign-Off

- **Protocol V1 Frozen Hash:** `e3cfed296037ba59e5cc371f8ae7815884e7ea3cdfd7a10b0d18fd4c4e9fae6d`
- **Protocol V2 Frozen Hash:** `effd05679ceb637073b6e7081633f2f51ebf2deaece0010041d33b8b07d19ab1`
- **Integrity Status:** Protocol V2 is formally locked. No external test images have been exposed during this revision.
