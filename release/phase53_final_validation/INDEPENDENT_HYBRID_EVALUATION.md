# DefectVision AI — Independent Hybrid Evaluation Record

**Phase:** Phase 53 — Final Independent Hybrid Validation and Research Decision  
**Role:** Senior Computer Vision Engineer, Independent ML Evaluator, and Research Integrity Auditor  
**Workspace:** `C:\Users\surya\Downloads\Mini Project`  
**Date:** November 2, 2026  
**Evaluation Status:** **SKIPPED — NO ELIGIBLE INDEPENDENT HYBRID COHORT**  

---

## 1. Formal Non-Execution Justification

Under the governing methodology directive of Phase 53:
> *"Run this step ONLY if Step 1 identifies an eligible cohort... If no eligible independent cohort exists, record: INDEPENDENT HYBRID VALIDATION: BLOCKED — NO ELIGIBLE DATA. Do not substitute the previously development-exposed 856-image MVTec benchmark. Do not use VisA cashew as complete hybrid validation because the existing EfficientNet classifier does not support that category. If no eligible data exists, skip this step entirely."*

In accordance with [`DATA_ELIGIBILITY_AUDIT.md`](file:///C:/Users/surya/Downloads/Mini%20Project/release/phase53_final_validation/DATA_ELIGIBILITY_AUDIT.md), **Step 2 was not executed**. No prediction CSV files or synthetic metrics were generated for this phase.

---

## 2. The Architectural Asymmetry Between Hybrid Components

The inability to execute an independent hybrid evaluation without retraining exposes a fundamental structural reality in industrial visual inspection systems:

```
[Incoming Image (Unseen Domain)]
             |
             +-----------------------------------------+
             |                                         |
             v                                         v
+-----------------------------+           +-----------------------------+
|    Supervised Classifier    |           |  Unsupervised Patch Memory  |
|     (EfficientNet-B0 v3)    |           |          (PatchCore)        |
+-----------------------------+           +-----------------------------+
| Requires labeled defects    |           | Requires nominal samples    |
| for every target category   |           | only for target domain      |
|                             |           |                             |
| Closed-world training       |           | Open-set anomaly detection  |
| (15 MVTec categories only)  |           | (Registered on Cashew)      |
|                             |           |                             |
| STATUS ON VISA CASHEW:      |           | STATUS ON VISA CASHEW:      |
| BLOCKED (Unsupported Class) |           | VERIFIED (Phase 49 AUROC)   |
+-----------------------------+           +-----------------------------+
             |                                         |
             +--------------------+--------------------+
                                  |
                                  v
                    [Dual-Branch Decision Fusion]
                    STATUS: BLOCKED ON CASHEW
```

1.  **Unsupervised PatchCore:** Adaptable to new industrial categories using nominal-only registration. This was independently proven on VisA Cashew in Phase 49 ($0.9237$ image AUROC, $0.9930$ pixel AUROC across 200 specimens).
2.  **Supervised EfficientNet-B0 v3:** Constrained strictly to its training defect classes. Because it was trained on MVTec, evaluating EfficientNet-B0 on VisA Cashew would yield uncalibrated noise ($p_{\text{defect}}$ predictions that do not reflect defect probability).
3.  **Hybrid Fusion (Logical OR):** Because one branch is uncalibrated on out-of-domain categories, the dual-branch hybrid can only function where *both* models have category-specific support. In the current frozen system, this condition is met exclusively on MVTec AD.
4.  **Why MVTec Cannot Be Substituted:** The 856-image MVTec benchmark was accessed during feature engineering, threshold tuning, and architectural validation. While there was zero direct image leakage into the training split, MVTec performance represents **Category C Development-Exposed** validation, not zero-leakage independent generalization.

---

## 3. Summary of Verified Empirical Standing

| Component / Subsystem | Benchmark Dataset | Evaluation Mode | Verified Empirical Status | Authoritative Report |
| :--- | :--- | :--- | :--- | :--- |
| **Standalone PatchCore** | VisA Cashew ($N=200$) | Nominal-Only Target Adaptation | **Independently Validated** ($0.9237$ AUROC, $98\%$ Spec, $57\%$ Recall) | `release/phase49_independent_results/` |
| **Standalone EfficientNet-B0** | MVTec AD ($N=856$) | Supervised Defect Classification | **Development-Exposed Benchmark** ($86.92\%$ Acc, $82.24\%$ Recall, 1 FP) | `release/final_18h_validation/` |
| **Complete Hybrid (OR-logic)** | MVTec AD ($N=856$) | Dual-Branch Fusion | **Development-Exposed Benchmark** ($91.94\%$ Acc, $90.88\%$ Recall, 12 FP) | `release/final_18h_validation/` |
| **Complete Hybrid (OR-logic)** | Unseen External Domain | Out-of-Distribution Independent | **BLOCKED — NO ELIGIBLE DATA** (Requires supervised retraining of EffNet) | This Report |

---

## 4. Research Integrity Audit Finding

*   **Fabricated Independent Predictions:** **None** (zero files created).
*   **Surrogate Substitution:** **None** (MVTec 856 benchmark was not re-badged as independent).
*   **Scientific Conclusion:** A blocked evaluation is the only methodologically defensible finding when dataset-model eligibility requirements cannot be met without retraining.
