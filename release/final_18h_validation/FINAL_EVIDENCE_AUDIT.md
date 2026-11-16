# DefectVision AI — Final Evidence Integrity Audit Report

**Audit Type:** Read-Only Scientific & Operational Integrity Gate  
**Execution Timestamp:** 2026-11-01T23:42:00+05:30  
**Audit Baseline Commit:** `0ff3c79`  
**Primary Evidence Inspected:**
- `release/final_18h_validation/evaluation_predictions.csv` (856 records)
- `release/final_18h_validation/evaluation_metrics.csv`
- `release/final_18h_validation/per_category_metrics.csv`
- `release/final_18h_validation/confusion_matrices.json`
- `release/final_18h_validation/QUANTITATIVE_EVALUATION.md`
- `release/final_18h_validation/PAPER_DRAFT.md`
- Original split manifests in `G:/My Drive/DefectVisionAI/dataset/splits/`
- Calibration baselines in `DefectVisionAI/reports/step9_severity_baselines.csv`

---

## Executive Summary & Readiness Decisions

```
================================================================================
                    FINAL READINESS AUDIT VERDICTS
================================================================================
1. SOFTWARE PROTOTYPE:                 GO
2. REAL-INFERENCE VALIDITY:            GO
3. INDEPENDENT GENERALIZATION:         NO-GO
4. CONTROLLED INDUSTRIAL PILOT:
   - A. Offline / Supervised Shadow:   CONDITIONAL GO
   - B. Autonomous Live-Line Gating:   NO-GO
5. APPLIED JOURNAL MANUSCRIPT:         CONDITIONAL GO
6. Q1 THEORETICAL JOURNAL SUBMISSION:  NO-GO
================================================================================
```

---

## Discrepancy Table

| Audit Area | Claimed / Initial Reporting | Audited Reality & Verification | Impact / Required Correction |
| :--- | :--- | :--- | :--- |
| **Dataset Provenance** | "Zero-leakage, independently held-out benchmark" | Benchmark set (`benchmark_test_v2.csv`) was repeatedly evaluated in development (Phases 7B, 7C, 8B, 8C); early prototype v1 training split had 788 overlapping images | **Reclassify from "Independent Held-Out" to "Development-Exposed (Class C)".** Remove all zero-leakage claims. |
| **Comparative Superiority** | "Hybrid achieves Pareto superiority across all metrics" | EfficientNet alone achieves higher AUROC (0.9809 vs 0.9608), higher AUPRC (0.9932 vs 0.9745), and far lower False Alarms (1 FP vs 12 FP) | **Reframe Hybrid as an asymmetric operating point.** Hybrid prioritizes defect escape reduction (Recall: 90.88% vs 82.24%) at the cost of a 12x increase in false alarms. |
| **False Alarm Impact** | "Negligible false-alarm penalty (+1 FP)" | True only relative to PatchCore (11 FP -> 12 FP). Relative to EfficientNet (1 FP), false alarms increased by **1200% (12x increase)** | **Disclose false alarm penalty accurately.** False positive rate rose from 0.43% to 5.19%. |
| **PatchCore Pooled AUROC** | Reported PatchCore AUROC: `0.8159` | Pooling unnormalized raw Euclidean distances across categories with disparate baselines depresses AUROC; category-normalized AUROC is `0.9373` | **Document dual AUROC.** Note that cross-category unnormalized distance pooling causes artificial AUROC compression. |
| **Hardware Latency** | "Sub-80ms real-time throughput on CPU" | Component forward pass is ~450 ms; full API round-trip median is **881.7 ms** (p95: 1455.7 ms) on multi-core CPU without GPU | **Correct throughput claims.** System delivers 1.1–2.2 FPS on CPU; sub-80ms requires dedicated GPU or TensorRT compilation. |
| **Record Integrity** | Exactly 856 specimens, 625 defect / 231 normal | **Verified.** Exactly 856 distinct filepaths, 0 duplicates, 625 defect, 231 normal, 0 label discrepancies | **CONFIRMED 100% INTACT.** |

---

## Task 1 — Recompute Metrics from Saved Predictions

The evaluation predictions file [`release/final_18h_validation/evaluation_predictions.csv`](file:///c:/Users/surya/Downloads/Mini%20Project/release/final_18h_validation/evaluation_predictions.csv) was loaded and audited via `scripts/audit_evaluation_predictions.py`.

### 1.1 Dataset Population Audit:
- **Total Rows:** 856
- **Distinct Filepaths:** 856 (0 duplicate records detected)
- **Ground Truth Distribution:**
  - Nominal / Unblemished (`is_normal == True`, `ground_truth == 0`): **231**
  - Defective / Anomalous (`is_normal == False`, `ground_truth == 1`): **625**
- **Label Consistency:** 100% agreement between boolean `is_normal` and numeric `ground_truth` (0 inconsistent records).
- **Defect Morphologies:** 49 distinct defect sub-types evaluated across 15 categories.

### 1.2 Recomputed Confusion Matrices:
```
1. PATCHCORE (UNSUPERVISED ALONE):
   - True Negatives (TN):   220
   - False Positives (FP):  11  (False Alarm Rate: 4.76%)
   - False Negatives (FN):  176 (Defect Escape Rate: 28.16%)
   - True Positives (TP):   449

2. EFFICIENTNET-B0 (SUPERVISED ALONE):
   - True Negatives (TN):   230
   - False Positives (FP):  1   (False Alarm Rate: 0.43%)
   - False Negatives (FN):  111 (Defect Escape Rate: 17.76%)
   - True Positives (TP):   514

3. DEFECTVISION AI HYBRID (DISJUNCTIVE UNION):
   - True Negatives (TN):   219
   - False Positives (FP):  12  (False Alarm Rate: 5.19%)
   - False Negatives (FN):  57  (Defect Escape Rate: 9.12%)
   - True Positives (TP):   568
```

### 1.3 Recomputed Quantitative Metrics:

| Metric | PatchCore (Unsupervised) | EfficientNet-B0 (Supervised) | DefectVision AI Hybrid | Verification vs Manuscript Tables |
| :--- | :--- | :--- | :--- | :--- |
| **Accuracy** | 78.1542% | 86.9159% | **91.9393%** | Exact match (rounded to 4 decimal places) |
| **Balanced Accuracy** | 83.5390% | 90.9035% | **92.8426%** | Exact match |
| **Precision (PPV)** | 97.6087% | **99.8058%** | 97.9310% | Exact match |
| **Recall / Sensitivity** | 71.8400% | 82.2400% | **90.8800%** | Exact match |
| **Specificity (TNR)** | 95.2381% | **99.5671%** | 94.8052% | Exact match |
| **F1-Score** | 0.827650 | 0.901754 | **0.942739** | Exact match |
| **False Positive Rate (FPR)** | 4.7619% | **0.4329%** | 5.1948% | Exact match |
| **False Negative Rate (FNR)** | 28.1600% | 17.7600% | **9.1200%** | Exact match |
| **AUROC (Image-Level)** | 0.815917* | **0.980873** | 0.960797 | Exact match |
| **AUPRC (Image-Level)** | 0.926644 | **0.993184** | 0.974487 | Exact match |

*\*Note on PatchCore AUROC:* The reported AUROC of 0.8159 reflects pooling raw unnormalized Euclidean distances across categories with different baseline scales (e.g. `capsule` mean 0.98 vs `cable` mean 2.18). When evaluating PatchCore using category-standardized anomaly scores ($\tilde{S}_{\text{norm}}$), the pooled AUROC is **0.9373**.

---

## Task 2 — Evaluation Independence & Provenance Audit

To determine whether the evaluation population is genuinely independent, an overlap audit was conducted against all historical training, validation, and calibration splits:

### 2.1 Manifest Overlap Analysis:
- `train_split.csv` (Nominal Training Split, 3,262 images): **0 overlap (0.0%)**
- `val_split.csv` (Nominal Validation Split, 367 images): **0 overlap (0.0%)**
- `supervised_train_split_v3.csv` (EfficientNet v3 Training, 3,499 images): **0 overlap (0.0%)**
- `supervised_val_split_v3.csv` (EfficientNet v3 Validation, 632 images): **0 overlap (0.0%)**
- `supervised_train_split.csv` (Historical Prototype v1 Training, 3,737 images): **788 overlapping images**

### 2.2 Provenance & Leakage Assessment:
1. **Model Weights Provenance:** The active EfficientNet checkpoint (`efficientnet_baseline_v3/best_model.pt`) was trained on v3 splits and has zero image overlap with `benchmark_test_v2.csv`.
2. **Threshold Calibration Provenance:** The 15 category thresholds in `step9_severity_baselines.csv` were established on small nominal calibration sets (`n_normal_samples` ranging from 12 to 60) and do not include test defect images.
3. **Development Exposure:** `benchmark_test_v2.csv` was repeatedly accessed and evaluated during Phase 7B, 7C, 8B, and 8C experiments for benchmarking CPND, MACBA, and BL baselines. In early project phases (v1), 788 of its images were included in the supervised training pool.

### 2.3 Formal Provenance Classification:
```
================================================================================
EVALUATION BENCHMARK CLASSIFICATION:
  CATEGORY C: DEVELOPMENT-EXPOSED
  
RATIONALE:
  While the final v3 weights and PatchCore memory banks have zero direct sample
  overlap with benchmark_test_v2.csv, this test split was repeatedly evaluated
  during algorithm development and ablation phases. It cannot be characterized
  as an independent held-out benchmark or described as "zero-leakage".
================================================================================
```

---

## Task 3 — Evaluation Process & Output Completion Audit

1. **Process Execution:**
   - The primary benchmark evaluation script (`scripts/run_quantitative_evaluation.py`) completed its execution on the primary benchmark partition (`benchmark_test_v2.csv`) and successfully output all 856 prediction records to `release/final_18h_validation/evaluation_predictions.csv`.
   - The secondary evaluation on the full MVTec test set (1,725 specimens) continues as an optional supplementary task in the background without affecting the primary benchmark artifacts.
2. **Output Completeness:**
   - All 856 rows contain complete, non-null values for: `filepath`, `category`, `defect_type`, `is_normal`, `ground_truth`, `patchcore_raw_score`, `patchcore_threshold`, `patchcore_pred`, `effnet_prob`, `effnet_pred`, `hybrid_pred`, `anomaly_norm`, `defect_area_pct`, `confidence_pct`, `severity_score`, and `severity_level`.
   - No truncated records, NaN floats, or missing categories were found.

---

## Task 4 — Comparative Operating-Point Analysis

The comparative analysis between the DefectVision AI Hybrid and the two constituent baselines must be reported with strict scientific balance:

### 4.1 The Defect Escape vs False Alarm Trade-Off:
- **Missed Defect Reduction:**
  - vs PatchCore alone: Escapes reduced from **176 to 57** (119 defects caught, a **67.6% reduction in escapes**).
  - vs EfficientNet alone: Escapes reduced from **111 to 57** (54 defects caught, a **48.6% reduction in escapes**).
- **False Alarm Increase:**
  - vs PatchCore alone: False alarms increased by **+1** (from 11 to 12 FP; FPR increased by $+0.43\%$).
  - vs EfficientNet alone: False alarms increased by **+11** (from 1 to 12 FP; FPR increased from $0.43\%$ to $5.19\%$, a **12-fold increase in false alarms**).

### 4.2 Threshold-Free Discrimination (AUROC / AUPRC):
- EfficientNet-B0 supervised classifier alone achieves the highest AUROC (**0.9809**) and highest AUPRC (**0.9932**).
- DefectVision AI Hybrid achieves AUROC **0.9608** and AUPRC **0.9745**.
- **Scientific Takeaway:** The Hybrid is **not** universally superior across all metrics. The supervised classifier has superior continuous probability calibration and superior false-alarm rejection. The Hybrid's advantage exists specifically at the **fixed decision operating point** ($\hat{y}_{\text{PC}} \lor \hat{y}_{\text{EffNet}}$), where it deliberately sacrifices specificity (dropping from 99.57% to 94.81%) to capture open-world defects that the classifier misses.

### 4.3 Runtime Latency Reality:
- On a 12-thread CPU, median dual-model forward pass requires **450.6 ms**, and full HTTP frame inspection averages **881.7 ms** (p95: 1455.7 ms).
- The system achieves approximately **1.1 to 2.2 parts per second** on CPU.
- Any claim of "sub-80ms real-time conveyor speed" is **unsupported on CPU** and requires GPU hardware acceleration or TensorRT compilation.

---

## Task 5 — Detailed Readiness Decisions

### 1. Software Prototype: `GO`
- **Assessment:** 22/22 unit tests passing, 29 FastAPI routes operational, bitwise exact float identity between direct models and HTTP API, verified numerical determinism (variance = 0.000000), 6/6 reliability stress tests passed, robust headless fallbacks.
- **Verdict:** Fully approved as a research prototype.

### 2. Real-Inference Validity: `GO`
- **Assessment:** 100% genuine deep neural network inference (ResNet-18 patch extraction + FAISS coreset retrieval + EfficientNet-B0 v3 classification). Zero synthetic scoring, mock data, or heuristic bypasses detected.
- **Verdict:** Fully approved as mathematically and empirically valid inference.

### 3. Independent Generalization: `NO-GO`
- **Assessment:** Held-out independent benchmarks (11 reserved VisA categories, BTAD, Chukyo) remain quarantined and unaccessed. The MVTec AD evaluation population is development-exposed. Zero cross-domain empirical evidence exists.
- **Verdict:** Claims of generalization beyond in-domain MVTec AD are not approved.

### 4. Controlled Industrial Pilot:
- **A. Offline / Supervised Shadow Feasibility Test: `CONDITIONAL GO`**
  - **Assessment:** Viable for parallel shadow logging alongside human quality inspectors where human inspection retains gating authority.
  - **Prerequisites for Launch:**
    1. Pre-deployment recording of 50 nominal specimens under live factory illumination to establish localized calibration parameters ($\mu_0, \tau_{\text{p99}}$).
    2. Operational logging of false alarm rates in shadow mode for 2 weeks.
    3. Inspection lines where cycle time exceeds 1.5 seconds per specimen (to accommodate CPU latency).
- **B. Autonomous Live-Line Gating: `NO-GO`**
  - **Assessment:** The system is **NOT ready** for autonomous conveyor pass/reject sorting. A 5.19% false alarm rate (diverting 1 in 20 good parts) would overwhelm factory rework stations, a 9.12% defect escape rate (57 missed defects) poses safety liability on critical parts, and CPU latency (~880 ms) is too slow for standard 10–20 Hz conveyor lines.
  - **Verdict:** Autonomous deployment strictly rejected.

### 5. Applied Journal Manuscript (IEEE TIM / IEEE Access): `CONDITIONAL GO`
- **Assessment:** The empirical study provides genuine engineering value as an applied dual-engine case study comparing unsupervised coreset retrieval with supervised transfer learning, accompanied by transparent negative results (CPND/MACBA) and open-source reproducibility.
- **Mandatory Revisions Before Submission:**
  1. Remove all claims of "zero-leakage" or "independently held-out benchmark"; accurately describe MVTec AD as a development-exposed in-domain benchmark.
  2. Disclose the 12x increase in false alarms relative to the supervised classifier alone.
  3. Reframe the hybrid architecture as an asymmetric recall-prioritizing operating point rather than a universally superior model.
  4. Correct latency claims to reflect realistic CPU throughput (1.1–2.2 FPS).

### 6. Q1 Theoretical Journal Submission (IEEE TPAMI / IJCV): `NO-GO`
- **Assessment:** CPND demonstrated zero gain over boundary distance and was formally abandoned in Phase 7C. MACBA was proven mathematically equivalent to cost-weighted ranking (BL6) in Phase 8C. There is no novel mathematical algorithm to support a theoretical Q1 computer vision submission.
- **Verdict:** Terminated. Do not pursue theoretical algorithm submissions.

---

## Audit Sign-Off

**Auditor:** DefectVision AI Evidence Integrity Gate  
**Final Status:** AUDIT COMPLETED — NO MODIFICATIONS MADE TO ORIGINAL BENCHMARK DATA OR PUBLIC REPO.
