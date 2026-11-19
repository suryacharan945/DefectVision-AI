# DEFECTVISION AI 2.4 — K-SHOT THRESHOLD FINAL DECISION GATE

**Document Identifier:** `release/experiments/KSHOT_THRESHOLD_FINAL_DECISION.md`  
**Governing Sprint:** Sprint 2.4  
**Audit Finding:** [K20_THRESHOLD_SELECTION_AUDIT.md](file:///c:/Users/surya/Downloads/Mini%20Project/release/experiments/K20_THRESHOLD_SELECTION_AUDIT.md)  
**Related Manifest:** [k20_frozen_policy_results.csv](file:///c:/Users/surya/Downloads/Mini%20Project/release/experiments/k20_frozen_policy_results.csv)  

---

## 1. Comparative Analysis: K=10 vs. K=20 Under Frozen Policies

A critical revelation of the Sprint 2.4 audit is that when evaluated strictly under **a priori frozen threshold policies** (before test set inspection), **K=10 outperforms K=20 in operational reliability**:

| Profile Bank Size | Frozen Policy Formula | Calibrated $\tau$ | Observed Test FPR | Specificity | Defect Recall | F1 Score | Leakage Status |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **K=10** (784 patches) | $\max(\text{calib}) + 0.10$ | 2.1230 | **0.0%** (0/20) | **100.0%** | **96.8%** (61/63) | **0.9839** | `FROZEN INDEPENDENT EVALUATION` |
| **K=20** (1,568 patches) | $\max(\text{calib}) + 0.10$ | 1.5541 | **20.0%** (4/20) | **80.0%** | **100.0%** (63/63) | **0.9692** | `FROZEN INDEPENDENT EVALUATION` |
| **K=20** (1,568 patches) | $\max(\text{calib}) \times 1.20$ | 1.7449 | **0.0%** (0/20)* | **100.0%** | **100.0%** (63/63) | **1.0000** | `DEVELOPMENT-SET RESULT` (Post-Hoc) |

*\*Note: Multiplier 1.20 was fitted directly to the test score distribution.*

### Why K=10 Outperforms K=20 Operationally
1. **Distance Scale Stability:** At $K=10$, calibration scores have not yet suffered extreme distance compression ($\max = 2.0230$, mean $= 1.5243$). The $+0.10$ buffer provided adequate coverage for the natural variation of test normals.
2. **Zero False Alarms A Priori:** Without any tuning, $K=10$ produced **zero false alarms** on the 20 unseen test normal bottles, while correctly catching 61 out of 63 defects (96.8% recall).
3. **Over-Tightening at K=20:** At $K=20$, memory bank density forces nearest-neighbor distances down. With only 10 calibration specimens, the sample maximum severely underestimates the true 99th percentile of normal variation, making $K=20$ fragile to false alarms unless large multiplicative buffers are applied.

---

## 2. Formal Production Decision

1. **Recommended Primary Profile:** **K=10** is designated as the officially validated few-shot profile for MVTec bottle inspection.
2. **K=20 Reclassification:** The claim of *"100% recall and 0% FPR at K=20"* is officially reclassified as a **`DEVELOPMENT-SET RESULT`**. It must not be cited in academic publications or customer specifications as an independently verified test result.
3. **Calibration Gate Enforcement:**
   - Any profile with $K \ge 20$ must be calibrated on at least **$N_{\text{calib}} \ge 20$ physically independent specimens** to ensure statistical coverage of the normal distribution tail.
   - Fixed additive buffers ($\max + \Delta$) are permanently deprecated.
