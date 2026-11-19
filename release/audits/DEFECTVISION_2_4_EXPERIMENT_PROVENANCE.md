# DEFECTVISION AI 2.4 — EXPERIMENT & REPOSITORY PROVENANCE AUDIT

**Document Identifier:** `release/audits/DEFECTVISION_2_4_EXPERIMENT_PROVENANCE.md`  
**Audited Branch:** `fix/localhost-live-inference-restoration`  
**Audited Baseline HEAD Commit:** `e0c8078`  
**Upstream Tracking:** `origin/fix/localhost-live-inference-restoration` (Synchronized)  
**Pull Request Status:** PR #6 (OPEN & UNMERGED)  
**Audit Scope:** Verification of execution logs, exact commands, commit history, and artifact provenance across Sprints 2.2, 2.3, and 2.4.  

---

## 1. Repository State & Synchronization Verification

| Parameter | Observed State | Compliance Status |
|:---|:---|:---:|
| **Active Branch** | `fix/localhost-live-inference-restoration` | COMPLIANT |
| **Commit Range** | `423cdf1` $\rightarrow$ `e0c8078` | VERIFIED |
| **Remote Tracking** | `origin/fix/localhost-live-inference-restoration` | UP TO DATE |
| **Pull Request** | PR #6 (`https://github.com/suryacharan945/DefectVision-AI/pull/6`) | OPEN & UNMERGED |
| **Working Tree** | Clean tracked tree. Legacy mask deletions inside NTFS junction `DefectVisionAI/dataset/raw/mvtec` mapped to persistent external storage `G:\My Drive\DefectVisionAI\dataset\raw\mvtec` | AUDITED & VERIFIED |
| **Live Localhost Services** | FastAPI Backend (`http://127.0.0.1:8001`) & Vite Frontend (`http://127.0.0.1:5174`) active | ACTIVE |

---

## 2. Exhaustive Experiment Execution & Artifact Provenance

Every experimental script executed across the sprint cycle has been forensically audited for command line invocation, exit code, execution environment, and output artifacts:

| Experiment / Script | Exact Command Line Executed | Hardware / Environment | Exit Code | Verified Output Artifacts | Classification |
|:---|:---|:---:|:---:|:---|:---:|
| **Sample Efficiency Benchmark** | `.\.venv\Scripts\python scripts/run_few_shot_sample_efficiency.py` | CPU (Host Intel/AMD), PyTorch 2.4, FAISS 1.8 | **0 (SUCCESS)** | [few_shot_sample_efficiency.csv](file:///c:/Users/surya/Downloads/Mini%20Project/release/experiments/few_shot_sample_efficiency.csv)<br>[few_shot_efficiency_curves.png](file:///c:/Users/surya/Downloads/Mini%20Project/release/experiments/few_shot_efficiency_curves.png) | `INDEPENDENTLY REPRODUCED` |
| **K-Shot Provenance Audit** | `.\.venv\Scripts\python scripts/audit_kshot_experiment.py` | CPU, Python 3.12, SHA-256 Hasher | **0 (SUCCESS)** | [kshot_partition_manifest.csv](file:///c:/Users/surya/Downloads/Mini%20Project/release/experiments/kshot_partition_manifest.csv)<br>[kshot_per_image_predictions.csv](file:///c:/Users/surya/Downloads/Mini%20Project/release/experiments/kshot_per_image_predictions.csv)<br>[kshot_reproduced_metrics.csv](file:///c:/Users/surya/Downloads/Mini%20Project/release/experiments/kshot_reproduced_metrics.csv) | `INDEPENDENTLY REPRODUCED` |
| **Threshold Calibration Matrix** | `.\.venv\Scripts\python scripts/validate_kshot_thresholds.py` | CPU, NumPy 1.26, Scikit-Learn | **0 (SUCCESS)** | [kshot_threshold_comparison.csv](file:///c:/Users/surya/Downloads/Mini%20Project/release/experiments/kshot_threshold_comparison.csv)<br>[KSHOT_THRESHOLD_VALIDATION.md](file:///c:/Users/surya/Downloads/Mini%20Project/release/experiments/KSHOT_THRESHOLD_VALIDATION.md) | `DEVELOPMENT-SET RESULT` (Post-Hoc Selected) |
| **Latency Benchmark Suite** | `.\.venv\Scripts\python scripts/reconcile_inference_latency.py` | CPU, OpenCV 4.10, 50 Iterations | **0 (SUCCESS)** | [inference_latency_breakdown.csv](file:///c:/Users/surya/Downloads/Mini%20Project/release/experiments/inference_latency_breakdown.csv)<br>[INFERENCE_LATENCY_RECONCILIATION.md](file:///c:/Users/surya/Downloads/Mini%20Project/release/experiments/INFERENCE_LATENCY_RECONCILIATION.md) | `INDEPENDENTLY REPRODUCED` |
| **Photometric Feature Fusion** | `.\.venv\Scripts\python scripts/run_spatial_photometric_experiment.py` | CPU, PyTorch ResNet18 + CIE Lab (7 variants) | **0 (SUCCESS)** | [spatial_photometric_metrics.csv](file:///c:/Users/surya/Downloads/Mini%20Project/release/experiments/spatial_photometric_metrics.csv)<br>[spatial_photometric_localization_comparison.png](file:///c:/Users/surya/Downloads/Mini%20Project/release/experiments/spatial_photometric_localization_comparison.png)<br>[SPATIAL_PHOTOMETRIC_RESEARCH_REPORT.md](file:///c:/Users/surya/Downloads/Mini%20Project/release/experiments/SPATIAL_PHOTOMETRIC_RESEARCH_REPORT.md) | `REPRODUCED WITH LIMITATIONS` (Sample Count Mislabel) |
| **Sprint 2.4 Audit Suite** | `.\.venv\Scripts\python scripts/audit_sprint_2_4.py` | CPU, 107 Specimen Cryptographic Audit | **0 (SUCCESS)** | [k20_threshold_selection_history.csv](file:///c:/Users/surya/Downloads/Mini%20Project/release/experiments/k20_threshold_selection_history.csv)<br>[k20_frozen_policy_results.csv](file:///c:/Users/surya/Downloads/Mini%20Project/release/experiments/k20_frozen_policy_results.csv)<br>[spatial_photometric_partition_manifest.csv](file:///c:/Users/surya/Downloads/Mini%20Project/release/experiments/spatial_photometric_partition_manifest.csv)<br>[spatial_photometric_sample_count_reconciliation.csv](file:///c:/Users/surya/Downloads/Mini%20Project/release/experiments/spatial_photometric_sample_count_reconciliation.csv)<br>[spatial_photometric_detailed_acceptance.csv](file:///c:/Users/surya/Downloads/Mini%20Project/release/experiments/spatial_photometric_detailed_acceptance.csv)<br>[statistical_confidence_intervals.csv](file:///c:/Users/surya/Downloads/Mini%20Project/release/experiments/statistical_confidence_intervals.csv) | `INDEPENDENTLY REPRODUCED` |

---

## 3. Discrepancy Findings Identified for Resolution

1. **Threshold Selection Independence Violation:** The transition from $\tau = 1.5541$ (FPR 20.0%) to $\tau = 1.7449$ (FPR 0.0%) was driven by post-hoc grid search over final-test predictions, requiring formal reclassification as a development-set finding.
2. **Pill Specimen Count Typography:** Sprint 2.3 reported 77 total specimens but listed $26 + 15 + 20 = 61$. The physical directory contains 26 normal, 25 color, and 26 crack specimens ($26 + 25 + 26 = 77$). The evaluation was conducted on all 77 genuine specimens; the discrepancy was purely typographical in the console string and markdown text.
3. **Acceptance Criteria Failure:** Fusing CIE Lab color with ResNet18 spatial features failed to meet the operational targets ($\ge 85\%$ color recall, $\ge 95\%$ crack recall), reaching at best $24.0\%$ color recall and $11.5\%-19.2\%$ crack recall due to channel dimension dominance and few-shot threshold elevation.
