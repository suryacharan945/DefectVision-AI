# Phase 8B: Protocol Amendment Ledger (V3.0 to V3.1)

**Document ID:** `DV-PHASE8B-AMEND-V1`  
**Date:** October 31, 2026  
**Auditor:** Lead AI/ML Research Engineer & Experimental Methodology Reviewer  
**Superseded Protocol:** `research/phase8a_direction_selection/PROPOSED_PROTOCOL_V3.json` (SHA-256: `5bb502a3a5f97b5e408544c4fa5a93ddbb1e3b5df5b56dcfa2cf91da71d87178`)  
**Amended Protocol:** `research/phase8b_macba_feasibility/PROPOSED_PROTOCOL_V3_1.json` (SHA-256: `7d6b8a113d4fba6ce34b74d4b98cbc614d650993e761b1a09e590d4cdfb994f0`)

---

## 1. Summary of Protocol Corrections

In response to Phase 8B audit requirements, Protocol V3 was corrected and amended to version 3.1:

| Protocol Section | Original Version 3.0 | Amended Version 3.1 | Justification |
| :--- | :--- | :--- | :--- |
| **Novelty Claim Positioning** | Claimed "unprecedented factory allocation novelty" and "first multi-task selective triage framework." | Explicitly acknowledges foundational literature in cost-sensitive reject options (Chow 1970) and capacity-constrained deferral (Alves et al. 2024, Reid et al. 2024). Positioned strictly as the first study on non-parametric visual anomaly detectors. | Scientific modesty and protection against reviewer rejection. |
| **Baseline Hierarchy** | 5 baselines with heuristic category allocation and simple ranking. | **Expanded to 8 strict baselines (BL0 through BL7)** including calibrated per-image risk (BL5) and cost-weighted risk (BL6). | Ensures MACBA is benchmarked against strong probabilistic baselines, not weak strawmen. |
| **Mathematical Loss Formulation** | Generic knapsack gain $\Delta \text{Cost}_c(k)$. | Rigorously derived **decision-theoretic expected loss reduction $\Delta L(X)$** under explicit human reviewer sensitivity ($p_{\text{sens}}$) and specificity ($p_{\text{spec}}$). | Eliminates ad-hoc heuristic scoring; grounds policy in Bayesian decision theory. |
| **Anti-Leakage Partitioning** | Informal 50/50 partition. | Formal **group-aware calibration ($\mathcal{D}_{\text{cal}}$) and internal evaluation ($\mathcal{D}_{\text{eval}}$) split**; prohibits use of evaluation labels in any allocation policy. | Guarantees 100% leakage-free execution. |
| **Development Data Status** | Treated as general multi-line development suite. | Formally labeled as an **EXPLORATORY FEASIBILITY STUDY** due to small error sample size in `bottle` (1 error) and `metal_nut` (3 errors). | Methodological transparency. |
| **Stopping Rules** | Required $+5.0\%$ MC-ECR over BL0. | Requires $+5.0\%$ Realized Cost Reduction over BL0, superiority over BL2, and optimization latency $< 10\text{ ms}$. | Aligns with financial decision-making metrics. |

---

## 2. Cryptographic Checksum Ledger

- **`PROPOSED_PROTOCOL_V3.json`:**  
  `5bb502a3a5f97b5e408544c4fa5a93ddbb1e3b5df5b56dcfa2cf91da71d87178` (Preserved intact in `research/phase8a_direction_selection/`)
- **`PROPOSED_PROTOCOL_V3_1.json`:**  
  `7d6b8a113d4fba6ce34b74d4b98cbc614d650993e761b1a09e590d4cdfb994f0` (Preserved in `research/phase8b_macba_feasibility/`)
