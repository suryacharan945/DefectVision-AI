# DEFECTVISION AI 2.2 — ARTIFACT REPRODUCIBILITY & METRIC AUDIT

**Document Identifier:** `release/audits/DEFECTVISION_2_2_ARTIFACT_REPRODUCIBILITY_AUDIT.md`  
**Execution Timestamp:** 2026-11-19T01:31:00+05:30  
**Repository:** `suryacharan945/DefectVision-AI`  
**Active Branch:** `fix/localhost-live-inference-restoration`  
**Audited HEAD Commit:** `73a06a66ee3750b25f7c11c9ded2522ecce4a7ca`  
**PR Reference:** PR #6 (Open, Unmerged)  

---

## 1. Repository & Branch Verification

| Parameter | Observed State | Compliance Status |
|:---|:---|:---|
| **Active Branch** | `fix/localhost-live-inference-restoration` | COMPLIANT (PR #6 branch maintained) |
| **Remote Tracking** | `origin/fix/localhost-live-inference-restoration` | COMPLIANT (Up-to-date with remote) |
| **HEAD Commit** | `73a06a66ee3750b25f7c11c9ded2522ecce4a7ca` | VERIFIED |
| **Working Tree** | Clean tracked tree; untracked legacy reports preserved | COMPLIANT |
| **PR #6 Status** | Open and Unmerged | STRICTLY COMPLIANT |

---

## 2. Inspection of Commit `73a06a6` Changes

Commit `73a06a6` introduced 40 files (+6959 / -1 lines):
1. **Core Service Contract Fix:** In `DefectVisionAI/src/camera_service.py`, restored `CONCLUSION_MAP["UNSUPPORTED"]` from `"REFERENCE PROFILE REQUIRED"` to `"UNSUPPORTED OR UNKNOWN CATEGORY"`. This resolved 4 unit test failures in benchmark mode while preserving the `"REFERENCE PROFILE REQUIRED"` response in universal intake mode at line 291.
2. **Audit & Validation Artifacts:** Authored 11 documentation reports, manifests, and CSV logs under `release/audits/` and `release/experiments/`.
3. **Execution Scripts:** Added 7 Python evaluation and audit scripts under `scripts/`.
4. **Visual Artifacts:** Generated confusion matrices, 4-panel localization comparisons, and error diagnostic heatmaps.

---

## 3. Comprehensive Inspection of Artifacts & Generating Scripts

| Artifact File | Generating Script | File Size | Primary Purpose | Inspection Finding |
|:---|:---|:---:|:---|:---|
| `DEFECTVISION_2_1_IMPLEMENTATION_AUDIT.md` | Manual / Audit | 9,845 B | Implementation review of 2.0 adaptation | Identified Domain D synthetic leakage & profile mismatch. |
| `DEFECTVISION_2_1_REGRESSION_REPORT.md` | `python -m unittest` | 7,078 B | Python & Vite test execution telemetry | Verified 92/92 tests pass, build 0 errors. |
| `dataset_manifest.json` | `scripts/build_dataset_manifest.py` | 205,328 B | 218 specimen provenance & SHA-256 | Validated 0 hash collisions, identified 48 synthetic station images. |
| `dataset_integrity_report.md` | `scripts/build_dataset_manifest.py` | 3,972 B | Split integrity summary | Documented physical vs. synthetic distribution. |
| `threshold_calibration_report.md` | `scripts/audit_threshold_calibration.py` | 4,936 B | Score distribution across 30 nominals | Evaluated P90, P95, P99 on 30 nominal bottles. |
| `baseline_vs_adaptation.csv` | `scripts/benchmark_baseline_vs_adaptation.py` | 6,059 B | Per-sample scores & verdicts (27 rows) | Ground-truth machine-readable evaluation record. |
| `BASELINE_VS_ADAPTATION_REPORT.md` | `scripts/benchmark_baseline_vs_adaptation.py` | 8,644 B | Markdown summary of 4-domain test | Discrepancy identified between CSV and markdown table. |
| `ERROR_ANALYSIS_REPORT.md` | `scripts/investigate_model_errors.py` | 4,890 B | Root-cause analysis of 3 edge cases | Pill color FN, Wood FP, Tile crack gate rejection. |
| `LOCALIZATION_EXPLAINABILITY_REPORT.md` | `scripts/evaluate_localization.py` | 3,309 B | Pixel AUROC, AP, and IoU | Pill color paradox: AUROC 0.9998 vs. IoU 0.0026. |
| `OOD_ROBUSTNESS_REPORT.md` | `scripts/evaluate_ood_robustness.py` | 3,887 B | In-distribution vs. OOD noise suite | 100% clean accuracy, 100% OOD rejection. |
| `ABLATION_STUDY.md` | `scripts/run_ablation_study.py` | 3,170 B | 5 architectural configurations (N=12) | Adapted standalone peak F1 (0.9231); CLAHE causes 100% FP. |

---

## 4. Metric Reproduction from Underlying Raw CSV Data

Direct execution of `scripts/reproduce_audit_metrics.py` against `release/experiments/baseline_vs_adaptation.csv` yielded the following verified empirical confusion matrices and performance metrics:

### 4.1 Domain A: MVTec AD Benchmark ($N=10$, 5 Normal, 5 Defective)
- **Baseline MVTec Model ($\tau = 1.4666$):**
  - $\text{TP}=5, \text{FP}=0, \text{TN}=5, \text{FN}=0$
  - $\text{Precision} = 5/5 = 1.0000$, $\text{Recall} = 5/5 = 1.0000$, $\text{Specificity} = 5/5 = 1.0000$, $\text{F1} = 1.0000$, $\text{Accuracy} = 100.0\%$, $\text{FPR} = 0.0\%$.
- **Station 01 Model ($\tau = 0.8333$):**
  - $\text{TP}=5, \text{FP}=5, \text{TN}=0, \text{FN}=0$
  - $\text{Precision} = 5/10 = 0.5000$, $\text{Recall} = 5/5 = 1.0000$, $\text{Specificity} = 0/5 = 0.0000$, $\text{F1} = 0.6667$, $\text{Accuracy} = 50.0\%$, $\text{FPR} = 100.0\%$.
- **Adapted Profile `btl_adapt_002` ($\tau = 1.6410$):**
  - $\text{TP}=5, \text{FP}=4, \text{TN}=1, \text{FN}=0$
  - $\text{Precision} = 5/9 = 0.5556$, $\text{Recall} = 5/5 = 1.0000$, $\text{Specificity} = 1/5 = 0.2000$, $\text{F1} = 0.7143$, $\text{Accuracy} = 60.0\%$, $\text{FPR} = 80.0\%$.
  > **Audit Note:** The markdown summary `BASELINE_VS_ADAPTATION_REPORT.md` previously quoted $\text{F1}=0.9091$ for Adapted on Domain A based on an earlier run with $\text{FP}=1$. The actual raw CSV record contains $\text{FP}=4$ and $\text{F1}=0.7143$. This demonstrates that the adapted studio profile significantly over-rejects MVTec benchmark bottles ($\text{FPR}=80.0\%$).

### 4.2 Domain B: Controlled External Studio Bottles ($N=3$, 2 Normal, 1 Defective)
- **Baseline MVTec Model ($\tau = 1.4666$):**
  - Scores: Normal 1 (`clear bottle.jpg`): $4.7829$, Normal 2 (`clear bottle2.webp`): $5.1506$, Defective (`disordered bottle.webp`): $4.1222$.
  - All 3 images score far above $1.4666$.
  - $\text{TP}=1, \text{FP}=2, \text{TN}=0, \text{FN}=0$.
  - $\text{Precision} = 1/3 = 0.3333$, $\text{Recall} = 1/1 = 1.0000$, $\text{Specificity} = 0/2 = 0.0000$, $\text{F1} = 0.5000$, $\text{Accuracy} = 33.3\%$, $\text{FPR} = 100.0\%$.
- **Adapted Profile `btl_adapt_002` ($\tau = 1.6410$):**
  - Scores: Normal 1: $1.3947$ (NORMAL), Normal 2: $1.3842$ (NORMAL), Defective: $3.9916$ (DEFECTIVE).
  - $\text{TP}=1, \text{FP}=0, \text{TN}=2, \text{FN}=0$.
  - $\text{Precision} = 1/1 = 1.0000$, $\text{Recall} = 1/1 = 1.0000$, $\text{Specificity} = 2/2 = 1.0000$, $\text{F1} = 1.0000$, $\text{Accuracy} = 100.0\%$, $\text{FPR} = 0.0\%$.
  > **Critical Audit Finding:** The metric reproduction confirmed the scores in the CSV. However, as audited in Section 4 of Phase 2, `clear bottle.jpg` and `clear bottle2.webp` were **in the training set** used to build `bottle_sku_btl_adapt_002`. Thus, Domain B normal performance represents train-set reconstruction, not independent generalization.

### 4.3 Domain C: Smartphone & Handheld Photos ($N=4$, 2 Normal, 2 Defective)
- **Baseline MVTec Model:** $\text{TP}=2, \text{FP}=0, \text{TN}=2, \text{FN}=0 \implies \text{F1}=1.0000$.
- **Station 01 Model:** $\text{TP}=2, \text{FP}=2, \text{TN}=0, \text{FN}=0 \implies \text{F1}=0.6667$.
- **Adapted Profile `btl_adapt_002`:** $\text{TP}=2, \text{FP}=2, \text{TN}=0, \text{FN}=0 \implies \text{F1}=0.6667$.

### 4.4 Domain D: Factory-Style Stationary Jitter ($N=10$, 5 Normal, 5 Defective)
- **Baseline MVTec Model:** $\text{TP}=5, \text{FP}=0, \text{TN}=5, \text{FN}=0 \implies \text{F1}=1.0000$.
- **Station 01 Model:** $\text{TP}=5, \text{FP}=5, \text{TN}=0, \text{FN}=0 \implies \text{F1}=0.6667$ (Threshold $0.8333$ fails on normal variance).
- **Adapted Profile `btl_adapt_002`:** $\text{TP}=5, \text{FP}=0, \text{TN}=5, \text{FN}=0 \implies \text{F1}=1.0000$.

---

## 5. Artifact Reproducibility Summary

1. **Raw CSV Source of Truth:** `release/experiments/baseline_vs_adaptation.csv` is fully verified and mathematically consistent with the confusion counts.
2. **Discrepancy Remediation:** Previous narrative claims describing Adapted Profile performance on Domain A as $0.9091$ F1 have been corrected to the verified CSV figure of **$0.7143$ F1**.
3. **Reproducibility Verdict:** All core calculation logic is reproducible from raw code and data, with zero synthetic mocking or hardcoded fakes.
