# DefectVision AI — Phase 7A Final Decision & Research Governance Report

**Document ID:** `DV-DECISION-PHASE7A-FINAL`  
**Date:** October 31, 2026  
**Auditor:** Lead AI/ML Research Engineer & Experimental Methodology Reviewer  
**Release Anchor:** `v1.0.0-research-prototype` (Commit `78ecd20`)  
**Protocol V2 Anchor:** `research/protocols/Q1_EXPERIMENT_PROTOCOL_V2.json`  
(SHA-256: `effd05679ceb637073b6e7081633f2f51ebf2deaece0010041d33b8b07d19ab1`)  

---

## 1. Formal Executive Decision

# **VERDICT: READY FOR CONTROLLED DEVELOPMENT EXPERIMENTS**

Phase 7A has successfully resolved all data exposure ambiguities, reconciled conflicting historical confusion matrices, eliminated invalid theoretical claims regarding conformal guarantees on out-of-distribution defects, and established a cryptographically frozen, methodologically sound experiment protocol (Protocol V2).

The project is now formally authorized to proceed to **Phase 7B: Controlled Development Experiments** (implementing and evaluating selective review baselines and candidate CPND algorithms strictly on designated development partitions).

> [!IMPORTANT]
> **Boundary Condition:** The project is **NOT** authorized to execute final-test inference on independent datasets. Final evaluation on the 11 untouched VisA categories and BTAD remains strictly quarantined behind Gate 3 until development algorithms, hyperparameters, and decision rules are completely frozen.

---

## 2. Summary of Phase 7A Audit Resolutions

```
+---------------------------------------------------------------------------------------------------------+
|                                    PHASE 7A AUDIT RESOLUTION SUMMARY                                     |
+---------------------------------------------------------------------------------------------------------+
| 1. VisA Exposure Corrected:                                                                             |
|    - VisA "capsules" (702 images) is strictly DEVELOPMENT-EXPOSED (v1 test + v2 normal development).    |
|    - 11 VisA categories (10,119 images) are POTENTIALLY INDEPENDENT (zero training or evaluation).      |
+---------------------------------------------------------------------------------------------------------+
                                                     |
                                                     v
+---------------------------------------------------------------------------------------------------------+
| 2. Confusion Matrices Reconciled:                                                                       |
|    - step11_uncertainty_log.csv: TP=1,132, TN=466, FP=1, FN=126 (Total Errors = 127).                   |
|    - "68 FN / 59 FP" refuted as an unverified conversational artifact and formally retracted.           |
|    - step8_efficientnet_on_common_testset.csv: TP=1,221, TN=467, FP=0, FN=37 (Total Errors = 37).      |
+---------------------------------------------------------------------------------------------------------+
                                                     |
                                                     v
+---------------------------------------------------------------------------------------------------------+
| 3. Conformal Mathematics Audited:                                                                       |
|    - Out-of-distribution defects violate exchangeability: NO distribution-free error capture guarantees.|
|    - Conformal calibration provides valid control strictly over nominal False Positive Rate (FPR <= a).|
|    - Fixed audit budgets (B <= 20%) convert the problem into empirical selective classification.        |
+---------------------------------------------------------------------------------------------------------+
                                                     |
                                                     v
+---------------------------------------------------------------------------------------------------------+
| 4. Protocol V2 Pre-Registered & Frozen:                                                                 |
|    - Replaces Protocol V1 (SHA-256: e3cfed29...); Protocol V2 SHA-256: effd0567...                     |
|    - Replaces static 35% target with two-tailed paired Wilcoxon signed-rank testing (p < 0.05).         |
|    - Mandates head-to-head ablation against Distance-to-Threshold (|S(X) - tau_c|).                    |
+---------------------------------------------------------------------------------------------------------+
                                                     |
                                                     v
+---------------------------------------------------------------------------------------------------------+
| 5. Dataset Acquisition Strategy Defined:                                                                |
|    - Zero downloads authorized in Phase 7A; local Windows disk preserved.                               |
|    - Target independent benchmarks: VisA 11 categories (10,119 images) and BTAD (2,830 images).         |
|    - Execution target: Cloud-native Google Colab / Google Drive storage pipeline.                       |
+---------------------------------------------------------------------------------------------------------+
```

---

## 3. Scope of Authorized Next Work (Phase 7B)

Under the verdict **READY FOR CONTROLLED DEVELOPMENT EXPERIMENTS**, the following actions are authorized:

1. **Development Data Boundary:**
   - Permitted development datasets:
     - MVTec Anomaly Detection (all 15 categories, 5,354 images).
     - VisA `capsules` development partition (461 fit, 40 calibration, 41 validation).
   - Prohibited datasets:
     - VisA 11 untouched categories (**QUARANTINED**).
     - BTAD (**QUARANTINED**).
     - Chukyo (**PERMANENTLY BLOCKED**).

2. **Authorized Algorithmic Implementations:**
   - Baseline 0: Uniform Random Audit.
   - Baseline 1: Top Anomaly Score Audit.
   - Baseline 2: Distance-to-Threshold Audit ($u_{\text{dist}}(X) = \frac{1}{|S(X) - \tau_c| + \epsilon}$).
   - Baseline 3: Supervised Prediction Margin ($1 - |2p - 1|$).
   - Candidate Algorithm: Calibrated Patch-Neighborhood Dispersion (CPND) and its joint formulation with Baseline 2 ($u_{\text{joint}}(X)$).

3. **Required Development Milestones Before Phase 7C:**
   - Execute baseline suite across all 15 MVTec AD categories on the 869-image development split.
   - Validate whether CPND adds measurable error-capture lift over Baseline 2 on development data.
   - Lock all hyperparameters ($k$, coreset ratio, weighting $\alpha$) into a frozen configuration before requesting authorization for independent held-out evaluation.
