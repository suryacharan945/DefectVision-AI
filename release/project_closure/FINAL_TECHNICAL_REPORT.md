# DefectVision AI — Final Technical Report

**Project Title:** DefectVision AI: A Dual-Engine Hybrid Architecture for Industrial Visual Anomaly Detection  
**Document Type:** Final Technical and Engineering Closeout Report  
**Date of Completion:** 2026-11-01  
**Baseline Git Commit:** `0ff3c79`  
**Primary Author / Engineering Team:** DefectVision AI Core Research & Development  
**Audited Reference:** `release/final_18h_validation/FINAL_EVIDENCE_AUDIT.md`

---

## 1. Executive Summary

DefectVision AI was developed to address a fundamental dilemma in automated optical inspection (AOI) for manufacturing lines: **unsupervised anomaly detection models** (e.g., PatchCore) offer open-world sensitivity to unseen flaw morphologies but suffer from elevated defect escape rates on subtle textural flaws and cross-category baseline shift; conversely, **supervised classifiers** (e.g., EfficientNet) deliver exceptional specificity and low false alarms on known flaw types but fail silently when presented with novel out-of-distribution (OOD) defects.

To bridge this operational gap, DefectVision AI combines an unsupervised patch-distribution memory bank (PatchCore using a ResNet-18 backbone with FAISS nearest-neighbor coreset indexing) and a lightweight supervised transfer learning classifier (EfficientNet-B0) through a disjunctive decision gate ($\hat{y}_{\text{hybrid}} = \hat{y}_{\text{PC}} \lor \hat{y}_{\text{EffNet}}$), accompanied by a continuous pixel-level localization and severity quantification pipeline.

This report summarizes the final engineering state, audited quantitative performance across an 856-specimen industrial benchmark (15 MVTec AD categories, 49 defect types), hardware latency profiling on multi-core CPU architectures, operational stress testing, comprehensive negative research findings (CPND refutation and MACBA equivalence to cost-weighted ranking), and formal production readiness decisions.

```
================================================================================
                    PROJECT CLOSURE READINESS VERDICTS
================================================================================
1. ENGINEERING PROTOTYPE:                 COMPLETE
2. IN-DOMAIN EVALUATION:                 VERIFIED (Development-Exposed)
3. INDEPENDENT GENERALIZATION:           NOT ESTABLISHED (Quarantined)
4. INDUSTRIAL PILOT:                     CONDITIONAL (Supervised Shadow Only)
5. Q1 THEORETICAL PUBLICATION:           NOT READY (Target Applied Venues)
================================================================================
```

---

## 2. System Architecture & Engineering Implementation

### 2.1 Dual-Engine Detection Pipeline

```
                                [ Input Inspection Frame ]
                                            |
                    +-----------------------+-----------------------+
                    |                                               |
                    v                                               v
        [ Engine 1: Unsupervised ]                      [ Engine 2: Supervised ]
        - Backbone: ResNet-18 (Layers 2+3)              - Backbone: EfficientNet-B0
        - Patch Embedding: 14x14 feature maps           - Pre-trained on ImageNet-1k
        - Index: FAISS L2 Coreset Index                 - Fine-tuned on 15 MVTec Classes
        - Score: Euclidean Nearest-Neighbor ($S$)       - Score: Calibrated Sigmoid ($P$)
                    |                                               |
                    v                                               v
        [ Threshold Gate: $\tau_{\text{PC}}(c)$ ]       [ Threshold Gate: $\tau_{\text{EffNet}}=0.50$ ]
                    |                                               |
                    +-----------------------+-----------------------+
                                            |
                                            v
                            [ Disjunctive Decision Logic ]
                    $\hat{y}_{\text{hybrid}} = \hat{y}_{\text{PC}} \lor \hat{y}_{\text{EffNet}}$
                                            |
                                            v
                    [ Continuous Severity & Localization Engine ]
                    - Dense Anomaly Heatmap (28x28 -> 224x224 Bilinear + Gaussian)
                    - Defect Contour Extraction (Otsu Adaptive Thresholding)
                    - Defect Area Percentage ($A_{\text{pct}}$) & Severity Score ($S \in [0, 100]$)
                                            |
                                            v
                            [ FastAPI JSON + Heatmap Payload ]
```

1. **Unsupervised Engine (PatchCore):**
   - Feature extractor: Pre-trained ResNet-18 backbone tapping mid-level representations (Layer 2 and Layer 3) via adaptive average pooling.
   - Patch dimension: $D = 192$ (reduced via greedy coreset subsampling at a 10% sampling ratio).
   - Distance retrieval: Fast CPU nearest-neighbor search via `faiss.IndexFlatL2`.
   - Category-calibrated decision: Category-specific thresholds $\tau_{\text{PC}}(c)$ derived from nominal validation percentiles ($\mu_0 + 3.0 \sigma_0$).

2. **Supervised Engine (EfficientNet-B0):**
   - Architecture: EfficientNet-B0 fine-tuned with binary cross-entropy on 15 manufacturing categories with data augmentation (random rotation $\pm 15^\circ$, affine scaling, color jitter).
   - Decision threshold: Fixed operating threshold $\tau_{\text{EffNet}} = 0.50$.

3. **Hybrid Decision Fusion:**
   - A specimen is flagged as anomalous if **either** engine triggers:
     $$\hat{y}_{\text{hybrid}} = \mathbb{I}\left(S_{\text{PC}}(x) \ge \tau_{\text{PC}}(c) \;\lor\; P_{\text{EffNet}}(x) \ge \tau_{\text{EffNet}}\right)$$
   - This disjunctive logic reflects the risk asymmetry of industrial quality assurance: defect escapes (false negatives) carry order-of-magnitude higher costs than false alarms (false positives).

4. **Localization and Severity Quantification:**
   - Patch scores are reshaped into an anomaly map ($28 \times 28$), upsampled to image dimensions ($224 \times 224$) via bilinear interpolation, and smoothed with a Gaussian kernel ($\sigma = 4.0$).
   - Defect segmentation masks are extracted via Otsu adaptive thresholding.
   - Multi-factor severity score:
     $$\text{Severity} = \min\left(100.0, \; 60.0 \times \frac{S_{\text{norm}}}{1.0 + S_{\text{norm}}} + 40.0 \times \min(1.0, \; 5.0 \cdot A_{\text{pct}})\right)$$
     Categorized into 4 discrete operational tiers: `NONE`, `LOW`, `MEDIUM`, and `HIGH`.

### 2.2 Software Implementation & API Services

The software prototype is engineered as a modular, production-grade microservice:
- **Backend:** Python 3.12, PyTorch 2.15.0+cpu, FAISS 1.15.1, FastAPI, Uvicorn, Pydantic v2.
- **REST Endpoints:** 29 HTTP endpoints supporting live frame inspection (`/inspect-frame`), batch directory scanning (`/batch-inspect`), model weight verification (`/health`, `/models/status`), threshold reconfiguration, and operational telemetry.
- **Frontend Dashboard:** Modern React / Vite / TypeScript dashboard featuring real-time image inspection, interactive side-by-side defect heatmap overlays, batch inspection progress monitors, and human-in-the-loop review queues.
- **Determinism & Test Coverage:** 22/22 unit tests passing; zero floating-point variance verified between direct model inference and HTTP API round-trips.

---

## 3. Audited Quantitative Evaluation

### 3.1 Dataset Population & Provenance Classification

All reported metrics originate from the primary quantitative benchmark file [`release/final_18h_validation/evaluation_predictions.csv`](file:///c:/Users/surya/Downloads/Mini%20Project/release/final_18h_validation/evaluation_predictions.csv), fully audited and verified in `FINAL_EVIDENCE_AUDIT.md`:
- **Total Specimens:** 856 distinct images across all 15 MVTec AD categories (`bottle`, `cable`, `capsule`, `carpet`, `grid`, `hazelnut`, `leather`, `metal_nut`, `pill`, `screw`, `tile`, `toothbrush`, `transistor`, `wood`, `zipper`).
- **Ground Truth Distribution:** 231 nominal / unblemished images and 625 defective images spanning 49 structural and surface defect morphologies.
- **Duplicate Records:** 0 (100% distinct specimens, 100% agreement between boolean and numeric labels).

```
================================================================================
DATASET PROVENANCE CLASSIFICATION:
  CATEGORY C: DEVELOPMENT-EXPOSED
================================================================================
Audit Findings:
1. Active model weights (EfficientNet v3) and PatchCore memory banks have 0.0%
   overlap with this benchmark set.
2. However, 788 images of this benchmark were included in the historical prototype
   v1 training split during initial exploration.
3. The benchmark was repeatedly evaluated during development and ablation cycles
   (Phases 7B, 7C, 8B, 8C).
4. Consequently, this benchmark CANNOT be claimed as "zero-leakage" or
   "independent held-out". It is strictly an in-domain development benchmark.
================================================================================
```

### 3.2 Audited Confusion Matrices

```
1. PATCHCORE (UNSUPERVISED CORESET ALONE):
   +-----------------------+-----------------------+
   |  True Negative:  220  |  False Positive:  11  |  (FPR = 4.76%)
   +-----------------------+-----------------------+
   |  False Negative: 176  |  True Positive:  449  |  (FNR = 28.16%)
   +-----------------------+-----------------------+

2. EFFICIENTNET-B0 (SUPERVISED CLASSIFIER ALONE):
   +-----------------------+-----------------------+
   |  True Negative:  230  |  False Positive:   1  |  (FPR = 0.43%)
   +-----------------------+-----------------------+
   |  False Negative: 111  |  True Positive:  514  |  (FNR = 17.76%)
   +-----------------------+-----------------------+

3. DEFECTVISION AI HYBRID (DISJUNCTIVE ENSEMBLE):
   +-----------------------+-----------------------+
   |  True Negative:  219  |  False Positive:  12  |  (FPR = 5.19%)
   +-----------------------+-----------------------+
   |  False Negative:  57  |  True Positive:  568  |  (FNR = 9.12%)
   +-----------------------+-----------------------+
```

### 3.3 Audited Performance Metrics

| Evaluation Metric | PatchCore Alone | EfficientNet-B0 Alone | DefectVision AI Hybrid | Net Delta (Hybrid vs Supervised) |
| :--- | :---: | :---: | :---: | :---: |
| **Accuracy** | 78.15% | 86.92% | **91.94%** | **+5.02%** |
| **Balanced Accuracy** | 83.54% | 90.90% | **92.84%** | **+1.94%** |
| **Precision (PPV)** | 97.61% | **99.81%** | 97.93% | -1.88% |
| **Recall / Sensitivity** | 71.84% | 82.24% | **90.88%** | **+8.64% (54 fewer misses)** |
| **Specificity (TNR)** | 95.24% | **99.57%** | 94.81% | -4.76% (11 more false alarms) |
| **F1-Score** | 0.8276 | 0.9018 | **0.9427** | **+0.0409** |
| **False Negative Rate (FNR)** | 28.16% | 17.76% | **9.12%** | **-8.64% (escapes halved)** |
| **False Positive Rate (FPR)** | 4.76% | **0.43%** | 5.19% | +4.76% (12x increase) |
| **AUROC (Continuous Score)** | 0.8159* (0.9373**) | **0.9809** | 0.9608 | -0.0201 |
| **AUPRC (Precision-Recall)** | 0.9266 | **0.9932** | 0.9745 | -0.0187 |

*\*Raw Pooled PatchCore AUROC (0.8159): Arises from evaluating raw Euclidean nearest-neighbor distances across categories with radically disparate distance baselines (e.g., `capsule` mean 0.98 vs `cable` mean 2.18).*  
*\*\*Normalized PatchCore AUROC (0.9373): Computed by standardizing raw distances against category-specific nominal distributions before pooling.*

### 3.4 Rigorous Operating-Point Trade-Off Analysis

A central scientific contribution of this audit is debunking the assumption of unconditional Pareto superiority:

1. **Defect Escape Reduction:**
   - The hybrid architecture achieves its design goal: reducing missed defects.
   - Compared to EfficientNet alone, false negatives drop from **111 to 57** (a **48.6% reduction in escapes**; 54 previously missed defective specimens successfully caught).
   - Compared to PatchCore alone, false negatives drop from **176 to 57** (a **67.6% reduction in escapes**; 119 defect escapes eliminated).

2. **The False Alarm Penalty:**
   - Compared to PatchCore alone, false alarms increase by only 1 (11 to 12 FP).
   - However, compared to EfficientNet alone, false alarms surge from **1 to 12 FP**, representing a **12-fold increase (1200%) in false alarms** (FPR rises from 0.43% to 5.19%).
   - In industrial manufacturing, 12 false alarms on 231 nominal parts means roughly 1 in every 20 good parts is erroneously flagged for manual review or scrap.

3. **Discrimination Curves (AUROC / AUPRC):**
   - EfficientNet-B0 alone achieves superior continuous ranking discrimination (AUROC 0.9809 vs 0.9608; AUPRC 0.9932 vs 0.9745).
   - The hybrid's advantage is **strictly restricted to the operational decision threshold** ($\hat{y}_{\text{PC}} \lor \hat{y}_{\text{EffNet}}$), where it deliberately accepts higher false alarms to guarantee higher defect recall.

---

## 4. Hardware Latency & Operational Profiling

All runtime measurements were benchmarked on a standard 12-thread Intel multi-core CPU workstation without GPU acceleration across 50 warm-up and 100 timed iterations:

### 4.1 Latency Breakdown

| Subsystem Component | Median (ms) | Mean (ms) | p90 (ms) | p95 (ms) |
| :--- | :---: | :---: | :---: | :---: |
| **PatchCore Forward Pass + FAISS L2** | 412.3 ms | 425.8 ms | 512.4 ms | 589.1 ms |
| **EfficientNet-B0 Forward Pass** | 38.3 ms | 41.2 ms | 54.0 ms | 62.7 ms |
| **Combined Dual-Model Forward Pass** | **450.6 ms** | **467.0 ms** | **566.4 ms** | **651.8 ms** |
| **Heatmap & Contour Generation** | 184.2 ms | 192.5 ms | 231.0 ms | 268.4 ms |
| **JSON Serialization & Base64 Encoding** | 46.9 ms | 51.3 ms | 68.2 ms | 81.5 ms |
| **End-to-End API `/inspect-frame`** | **881.7 ms** | **910.8 ms** | **1240.5 ms** | **1455.7 ms** |

### 4.2 Factory Line Throughput Reality

- **Current CPU Capacity:** At ~881.7 ms median API latency, the system processes approximately **1.13 frames per second** (burst capacity up to ~2.2 FPS when bypassing heatmap rendering).
- **Conveyor Belt Feasibility:** Modern high-speed packaging, canning, and stamping lines run at 10 to 30 parts per second (33–100 ms per part). The prototype **cannot support inline gating on high-speed conveyors without GPU acceleration**.
- **GPU Acceleration Projection:** Benchmarks on NVIDIA RTX 4090 / TensorRT fp16 project end-to-end latency below 28 ms (>35 FPS), which would fulfill real-time conveyor demands.

---

## 5. Operational Reliability & Robustness Stress Testing

### 5.1 Boundary & Failure Mode Stress Testing (6/6 Passed)

To confirm operational stability, the system was subjected to 6 adversarial stress suites:
1. **Corrupt / Truncated Image Payloads:** Returns clean HTTP 422 with descriptive error; no server crashes or memory leaks.
2. **Unknown / Unregistered Category:** Gracefully falls back to a global uncalibrated threshold model with an explicit warning flag.
3. **Payload Injection & Path Traversal:** SQL/path injection strings in category headers are sanitized; rejection verified.
4. **Extreme Aspect Ratios (1:16, 16:1):** Bilinear letterboxing handles extreme geometries without tensor shape mismatches.
5. **High-Resolution Payloads (4096 $\times$ 4096):** Memory-capped streaming downsampling prevents out-of-memory (OOM) faults.
6. **Concurrent Burst Requests (10 simultaneous clients):** Thread-safe FAISS CPU inference handles bursts without thread contention or memory corruption.

### 5.2 Environmental & Photometric Perturbations

The system was evaluated under 10 synthetic optical perturbations:
- **Resilient Variations:** The hybrid maintains stable classification accuracy ($\ge 90\%$) under Gaussian blur ($\sigma \le 1.0$), brightness shifts ($\pm 20\%$), contrast variations ($\pm 20\%$), and camera rotation ($\pm 5^\circ$).
- **Vulnerabilities:** Severe Gaussian noise ($\sigma \ge 0.10$) causes high-frequency patch distortion in ResNet-18 Layer 2, causing PatchCore anomaly scores to spike and triggering false alarms on nominal parts. Real factory deployments require controlled telecentric illumination.

---

## 6. Formal Negative Research Findings

A foundational pillar of DefectVision AI's scientific integrity is the full documentation and formal retirement of two speculative algorithmic proposals:

### 6.1 CPND (Confidence-Penalized Neighborhood Density)

- **Hypothesis:** Modulating PatchCore anomaly scores with a local neighborhood density penalty and prediction uncertainty would suppress edge noise and improve defect boundary separation.
- **Empirical Refutation:** In Phase 7C experiments across 5 test categories, CPND failed to yield statistically significant AUROC or F1 improvements over standard boundary-distance scoring. On subtle surface defects (e.g., fine scratches on `transistor`), the density penalty diluted true defect signals, increasing false negatives.
- **Conclusion:** Formally abandoned in Phase 7C.

### 6.2 MACBA (Margin-Calibrated Active Budget Allocation)

- **Hypothesis:** A proprietary active learning review selection algorithm that dynamically allocates human review capacity based on score marginality and calibration confidence.
- **Empirical & Mathematical Finding:** In Phase 8C equivalence gating, MACBA decisions were systematically reconstructed against standard cost-weighted ranking (Baseline BL6). Under identical cost ratios and review budgets, MACBA produced mathematically identical specimen selection rankings to standard cost-sensitive risk minimization. The apparent early differences were traced to inconsistent probability estimators between baselines.
- **Conclusion:** MACBA is mathematically equivalent to conventional cost-sensitive ranking. Formally closed as a novel algorithm proposal in Phase 8C.

---

## 7. Model Provenance & Distribution Compliance

A comprehensive preflight audit was conducted to verify intellectual property and distribution rights:
- **ResNet-18 & EfficientNet-B0 Weights:** Pre-trained weights derived from ImageNet under Apache 2.0 / BSD licenses. Free for academic and research redistribution.
- **Trained Model Checkpoints:** Checkpoints fine-tuned exclusively on authorized public subsets.
- **Dataset Redistribution:** Raw MVTec AD, VisA, BTAD, and Chukyo datasets remain restricted by their original institutional licenses and are **excluded** from public repository commits.
- **Clean-Room Repository:** A pristine, clean-room Git export (`DefectVisionAI-CleanExport`) was compiled, verified free of API tokens, large binary blobs, proprietary datasets, and unverified artifacts.

---

## 8. Final Project Closure Verdicts

Based on the verified audit in `FINAL_EVIDENCE_AUDIT.md`, the engineering and research phase of DefectVision AI is concluded with the following official verdicts:

```
================================================================================
                    FINAL SYSTEM STATUS VERDICTS
================================================================================

1. ENGINEERING PROTOTYPE: COMPLETE
   - Robust, verified, reproducible dual-engine software implementation.
   - 22/22 unit tests passing; 29 operational REST routes; bitwise deterministic.

2. IN-DOMAIN EVALUATION: VERIFIED
   - 856-specimen evaluation audited: 91.94% accuracy, 90.88% recall, 0.9427 F1.
   - Classified as Category C (Development-Exposed). All metrics verified.

3. INDEPENDENT GENERALIZATION: NOT ESTABLISHED
   - 11 VisA categories, BTAD, and Chukyo remain strictly quarantined.
   - Zero out-of-domain cross-dataset generalization claimed or demonstrated.

4. INDUSTRIAL PILOT: CONDITIONAL
   - Supervised Shadow Mode: APPROVED (conditional on 50-specimen on-site baseline
     calibration and human inspection retaining gating authority).
   - Autonomous Live-Line Gating: STRICTLY REJECTED (5.19% false alarm rate,
     9.12% escape rate, and ~880 ms CPU latency preclude autonomous actuation).

5. ACADEMIC PUBLICATION: NOT READY (Q1 THEORETICAL) / CONDITIONAL (APPLIED)
   - Q1 Theoretical Journal (IEEE TPAMI / IJCV): NOT READY (Algorithms refuted).
   - Applied Systems Journal (IEEE TIM / IEEE Access): CONDITIONAL (Positioned as
     an empirical dual-engine case study with transparent negative results).

================================================================================
```

---

## 9. Sign-Off & Archive Authority

**Report Approved By:** DefectVision AI Integrity & Engineering Gate  
**Status:** CLOSED AND ARCHIVED  
**Repository State:** Local Research Repository Frozen at `0ff3c79`; Clean Public Export Synchronized at `e3c3a78`. No further model training or benchmark modifications authorized.
