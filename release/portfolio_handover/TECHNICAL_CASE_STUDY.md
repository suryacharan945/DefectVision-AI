# DefectVision AI: Engineering a Dual-Engine Visual Anomaly Detection Platform

**Author:** Surya Charan  
**Role:** Machine Learning System Architect & Lead Engineer  
**Project Classification:** Applied Computer Vision Research & Industrial Microservice Prototype  
**Audited Baseline Reference:** `release/final_18h_validation/FINAL_EVIDENCE_AUDIT.md`  
**Open-Source Release Repository:** [DefectVisionAI-OpenSource](https://github.com/suryacharan945/DefectVisionAI-OpenSource)

---

## 1. Problem Statement: The Industrial Inspection Dilemma

In modern automated manufacturing lines, optical surface inspection is critical for zero-defect production. However, quality engineering teams face a fundamental operational dilemma when deploying computer vision:

1. **The Blind Spots of Supervised Learning:** Standard supervised deep learning classifiers (e.g., EfficientNet, ResNet) achieve exceptional specificity on known defect types, but require thousands of labeled defect examples. In reality, defect occurrences in manufacturing are rare ($<0.1\%$) and open-world—flaws manifest in unpredictable morphologies (hairline cracks, pinprick punctures, foreign material inclusions, optical staining). When a novel defect geometry appears, supervised classifiers fail silently, passing defective parts downstream to customers.
2. **The Escapes and Drift of Unsupervised Models:** Unsupervised memory-bank approaches (e.g., PatchCore) solve the open-world problem by modeling only the distribution of nominal (healthy) patches. However, they suffer from elevated defect escape rates on subtle textural blemishes, and their raw Euclidean distance baselines vary drastically across different product categories (e.g., mean distance $\approx 0.98$ on `capsule` vs $2.18$ on `cable`), making cross-category deployment notoriously difficult.

**DefectVision AI** was engineered to solve this dilemma by fusing an unsupervised patch coreset memory bank with a supervised transfer learning classifier under a risk-asymmetric decision policy.

---

## 2. System Architecture & Engineering Implementation

```
                                [ Input Specimen Frame (224x224) ]
                                                |
                        +-----------------------+-----------------------+
                        |                                               |
                        v                                               v
            [ Engine 1: Unsupervised ]                      [ Engine 2: Supervised ]
            - Backbone: ResNet-18 (Layers 2+3)              - Backbone: EfficientNet-B0
            - Memory Bank: FAISS IndexFlatL2                - Fine-tuned on 15 Classes
            - Score: Nearest-Neighbor Distance (S_PC)       - Score: Calibrated Sigmoid (P_EffNet)
            - Gate: tau_PC(c) per Category                  - Gate: Fixed 0.50 Threshold
                        |                                               |
                        +-----------------------+-----------------------+
                                                |
                                                v
                                [ Disjunctive Decision Logic ]
                         y_hybrid = [ S_PC >= tau_PC(c) ]  OR  [ P_EffNet >= 0.50 ]
                                                |
                                                v
                        [ Continuous Severity & Localization Engine ]
                        - Bilinear Upsampling (28x28 -> 224x224) + Gaussian Smoothing (sigma=4.0)
                        - Otsu Adaptive Contour Segmentation -> Defect Area Percentage (A_pct)
                        - Multi-Factor Severity Score: S in [0, 100] (None, Low, Medium, High)
                                                |
                                                v
                                [ FastAPI JSON + Heatmap Telemetry ]
```

### Component 1: Unsupervised Deep Patch Embedding (PatchCore)
- **Feature Extractor:** We tapped mid-level representations from a pre-trained ResNet-18 backbone (Layers 2 and 3), fusing localized texture ($1/4$ resolution) with structural geometry ($1/8$ resolution) into a 192-dimensional patch representation.
- **Coreset Reduction:** To enable real-time inference on edge CPUs without GPU memory bloat, we applied greedy minimax coreset subsampling at a 10% ratio, reducing the memory bank to approximately 20,000 representative nominal patch embeddings per category.
- **Nearest-Neighbor Retrieval:** Patch embeddings are indexed via `faiss.IndexFlatL2` on contiguous C-ordered NumPy memory arrays for deterministic Euclidean distance calculation.

### Component 2: Supervised Companion Classifier (EfficientNet-B0)
- **Architecture:** Lightweight EfficientNet-B0 fine-tuned on 15 industrial classes with data augmentation (affine rotations, random scaling, color jitter).
- **Role:** Delivers high specificity ($99.57\%$) and sub-40ms execution, providing instantaneous detection of gross structural deformities (e.g., fractured bottle necks, crushed capacitors).

### Component 3: Disjunctive Decision Fusion
- An inspection frame is flagged as defective if **either** engine triggers:
  $$\hat{y}_{\text{hybrid}} = \mathbb{I}\left(S_{\text{PC}}(x) \ge \tau_{\text{PC}}(c) \;\lor\; P_{\text{EffNet}}(x) \ge 0.50\right)$$
- This disjunctive policy reflects the core economic asymmetry of factory quality control: defect escapes (false negatives) lead to catastrophic warranty claims and customer churn, whereas false alarms (false positives) simply route a part to manual review.

### Component 4: Continuous Localization & Multi-Factor Severity
- Patch distances ($28 \times 28$) are upsampled to input image dimensions ($224 \times 224$) via bilinear interpolation and smoothed with a Gaussian spatial filter ($\sigma = 4.0$).
- Defect boundaries are extracted using Otsu adaptive thresholding.
- The system computes an automated multi-factor severity index:
  $$\text{Severity} = \min\left(100.0, \; 60.0 \times \frac{S_{\text{norm}}}{1.0 + S_{\text{norm}}} + 40.0 \times \min(1.0, \; 5.0 \cdot A_{\text{pct}})\right)$$
  categorizing parts into `NONE`, `LOW`, `MEDIUM`, and `HIGH`.

---

## 3. Audited Quantitative Findings across 856 Specimens

The system was evaluated across an audited benchmark of **856 industrial specimens** (625 defective, 231 nominal across 15 MVTec AD categories, 49 defect morphologies).

### 3.1 Audited Metrics Summary

| Metric | PatchCore (Unsupervised) | EfficientNet-B0 (Supervised) | DefectVision AI Hybrid | Net Impact (Hybrid vs EfficientNet) |
| :--- | :---: | :---: | :---: | :---: |
| **Accuracy** | 78.15% | 86.92% | **91.94%** | **+5.02%** |
| **Defect Recall (Sensitivity)** | 71.84% | 82.24% | **90.88%** | **+8.64% (54 fewer misses)** |
| **Specificity (TNR)** | 95.24% | **99.57%** | 94.81% | -4.76% (11 more false alarms) |
| **F1-Score** | 0.8276 | 0.9018 | **0.9427** | **+0.0409** |
| **Defect Escapes (FN / 625)** | 176 | 111 | **57** | **-48.6% drop in escapes** |
| **False Alarms (FP / 231)** | 11 | **1** | 12 | **+11 FP (12x increase)** |
| **AUROC (Continuous Score)** | 0.8159* (0.9373**) | **0.9809** | 0.9608 | -0.0201 |
| **AUPRC (Precision-Recall)** | 0.9266 | **0.9932** | 0.9745 | -0.0187 |

*\*Raw Pooled PatchCore AUROC: 0.8159 (depressed due to cross-category Euclidean baseline shift).*  
*\*\*Category-Normalized PatchCore AUROC: 0.9373 (standardized per-category).*

### 3.2 The Audited Trade-Off
A core finding of this project is the rejection of simplistic "Pareto dominance" claims:
- **The Defect Escape Gain:** The hybrid successfully cut missed defects from 111 down to 57—a **48.6% relative escape reduction**, capturing 54 defective parts that the supervised classifier missed entirely.
- **The False Alarm Cost:** However, false alarms surged from 1 to 12—a **12-fold increase (1200%)**, raising the false positive rate from $0.43\%$ to $5.19\%$.
- **Continuous vs Discrete:** EfficientNet alone has higher continuous ranking discrimination (AUROC 0.9809 vs 0.9608). The Hybrid's advantage exists strictly at the **fixed operational decision threshold**, prioritizing recall over specificity.

---

## 4. Hardware Latency Profile & Throughput

All benchmarks were recorded on a standard 12-thread Intel multi-core CPU workstation without GPU acceleration across 100 timed iterations:
- **PatchCore Feature Extraction + FAISS L2:** 412.3 ms median
- **EfficientNet-B0 Forward Pass:** 38.3 ms median
- **Combined Dual-Model Forward Pass:** **450.6 ms median** (p95: 651.8 ms)
- **Heatmap Generation & Contour Extraction:** 184.2 ms median
- **FastAPI End-to-End API (`/inspect-frame`):** **881.7 ms median** (p95: 1455.7 ms)

**Operational Takeaway:** Sustaining ~1.1 to 2.2 inspections per second, CPU inference is viable for indexed indexing tables or manual review stations. Real-time conveyor belt sorting (>10 FPS) requires GPU acceleration or TensorRT compilation.

---

## 5. The Value of Negative Findings: CPND and MACBA

A key demonstration of scientific integrity in this project was the rigorous evaluation and formal retirement of two proposed algorithms:

1. **CPND (Confidence-Penalized Neighborhood Density):** Formulated to suppress edge noise by penalizing anomaly scores based on local neighborhood density. Rigorous ablations across 5 categories showed zero statistically significant gain in AUROC or F1 ($p > 0.05$) while adding 35% latency. On subtle scratches, density penalties actively suppressed true defect patches, worsening false negatives. Formally abandoned in Phase 7C.
2. **MACBA (Margin-Calibrated Active Budget Allocation):** Formulated as a proprietary active review triage algorithm. In Phase 8C, mathematical reconstruction against standard cost-weighted ranking (Baseline BL6) proved that under identical cost ratios and probability calibration, MACBA produces identical rankings to classical decision-theoretic risk minimization. Formally retired in Phase 8C.

Transparently documenting these negative results prevented unnecessary architectural complexity and redirected engineering bandwidth to robust system hardening.

---

## 6. Software Engineering & Microservice Architecture

The production-grade microservice was engineered using Python 3.12, FastAPI, Uvicorn, and React 19:
- **29 REST Endpoints:** Live inspection, batch lot processing, threshold reconfiguration, FAISS similarity search, and RAG-based root-cause defect analysis.
- **Bitwise Numerical Determinism:** Verified zero floating-point variance (variance = 0.000000) across 5 consecutive inference passes.
- **Boundary Stress Testing:** Passed 6/6 adversarial test suites (corrupt payloads, SQL injection, extreme 1:16 aspect ratios, 4096x4096 streaming, burst traffic).
- **Public Simulated Demo Mode:** Engineered a clean-room repository where visitors can explore the full UI, batch queues, and API routes out-of-the-box with an explicit yellow warning banner, without downloading 2.5 GB of restricted dataset files.

---

## 7. Conclusions & Industrial Readiness

DefectVision AI concludes with five definitive readiness determinations:
1. **Engineering Prototype:** COMPLETE (Robust, verified, deterministic microservice).
2. **In-Domain Evaluation:** VERIFIED (91.94% accuracy on Category C development-exposed benchmark).
3. **Independent Generalization:** NOT ESTABLISHED (External VisA, BTAD, and Chukyo benchmarks quarantined).
4. **Industrial Pilot:** CONDITIONAL (Approved for supervised shadow logging; autonomous live-line gating strictly prohibited due to 5.19% false alarm rate and ~880 ms CPU latency).
5. **Academic Publication:** CONDITIONAL for applied engineering journals (*IEEE TIM*, *IEEE Access*); NOT READY for theoretical algorithm journals (*IEEE TPAMI*).
