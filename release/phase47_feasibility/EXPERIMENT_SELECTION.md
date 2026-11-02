# DefectVision AI — Phase 47: Experiment Selection and Protocol Evaluation

**Document Type:** Strategic Research Design & Experiment Selection Memo  
**Phase:** Phase 47 — Three-Hour Research Feasibility Sprint  
**Author:** Senior Industrial Computer Vision Researcher & Research Integrity Auditor  
**Date:** November 2, 2026  
**Git Baseline Commit:** `20ec56e`  
**Time Limit:** 3 Hours Active Work Budget  
**Workspace:** `C:\Users\surya\Downloads\Mini Project`  
**Target Output:** `release/phase47_feasibility/`  

---

## 1. Executive Context & Research Objective

Following the Phase 46 gate determination ([`FINAL_GO_NO_GO.md`](file:///C:/Users/surya/Downloads/Mini%20Project/release/phase46_independent_validation/FINAL_GO_NO_GO.md)), independent cross-domain generalization was classified as **NOT ESTABLISHED / STOP RULE TRIGGERED** because no eligible, compatible, unexposed evaluation dataset was physically staged on disk without violating dataset quarantines.

The objective of Phase 47 is to identify the **smallest defensible independent validation experiment** that can materially improve DefectVision AI's applied publication prospects in an applied engineering journal (e.g., *IEEE Transactions on Instrumentation and Measurement* or *IEEE Access*), without expanding project scope, without initiating unauthorized downloads, and within a strict 3-hour feasibility planning envelope.

---

## 2. Review of Prior Audit Evidence

A rigorous review of Phase 46 deliverables and forensic exposure records confirms:

1. **MVTec Anomaly Detection (MVTec AD):**
   - 15 categories, 5,354 images.
   - Formally classified as **Category C: Development-Exposed**.
   - Training nominals were used to fit all existing memory banks; 856 evaluation images were iteratively assessed. Disqualified from serving as an independent benchmark.
2. **VisA `capsules` (702 images):**
   - Development-exposed during `visa_development_v2` and `official_test_v1`. Disqualified.
3. **VisA `candle`, `macaroni1`, `macaroni2`, `pcb1` (4,404 images):**
   - Classified as **UNKNOWN / DISPUTED** due to filesystem cataloging and citations in exploratory inspection memos. Disqualified under audit standards.
4. **Chukyo Industrial Dataset (1,200 capsule images):**
   - Quarantined under `BLOCKED_INCOMPLETE_REFERENCE_AUDIT`. Disqualified.
5. **BTAD (2,830 images across 3 products):**
   - Pristine, but large, multi-category, unextracted, and absent from local storage.
6. **Untouched VisA Candidates (7 Categories, 5,715 images):**
   - Printed circuit boards: `pcb2` (1,101), `pcb3` (1,106), `pcb4` (1,105).
   - Aligned / discrete instances: `cashew` (600), `chewinggum` (603), `fryum` (600), `pipe_fryum` (600).
   - Confirmed 100% untouched: zero model weights, feature vectors, or evaluation logs exist in repository history.

### Selection of the Single Target Category: VisA `cashew`
Among the 7 untouched VisA candidates, **`cashew`** is selected as the optimal evaluation cohort for the following methodological reasons:
- **Compact Scale ($N=600$ images):** Comprises exactly 500 nominal images and 100 defective images, minimizing download bandwidth ($\approx 230\text{ MB}$ compressed) and storage overhead.
- **Aligned Single-Instance Geometry:** Unlike multi-instance piles (`macaroni`) or complex planar circuits (`pcb`), `cashew` specimens are centered discrete parts on uniform backgrounds. This directly mirrors industrial parts on conveyor inspection fixtures.
- **Defect Diversity:** Contains real physical surface and structural defects (cracks, burns, mold, mechanical gouges) annotated with pixel-level polygon ground-truth masks.
- **Balanced Test Partition:** Enables a perfectly balanced 1:1 independent test cohort (100 nominal, 100 defective; $N_{\text{test}} = 200$), eliminating class imbalance distortion in standard accuracy and F1 metrics.

---

## 3. Comparative Evaluation of Protocol Options

In accordance with Phase 47 instructions, only two methodological options are evaluated:

```
+------------------------------------+----------------------------------------+----------------------------------------+
| Evaluation Criterion               | Option A: Frozen-Model Direct Transfer | Option B: Nominal Target Registration  |
+------------------------------------+----------------------------------------+----------------------------------------+
| Scientific Validity                | INVALID (Methodologically Fatal)       | HIGH (Standard Peer-Reviewed Protocol) |
| Architecture Compatibility         | INCOMPATIBLE (MVTec classes only)      | 100% COMPATIBLE (Unsupervised Core)    |
| Handling of EfficientNet-B0 v3     | Hallucinates invalid MVTec class logits| Cleanly excluded / documented out-of-scope|
| Compute Requirements               | Minimal (< 1 min CPU)                  | Low (< 2 min CPU for coresetting)      |
| Storage Requirements               | 0 MB additional models                 | ~25 MB target memory bank              |
| Execution Time                     | ~1 minute                              | ~2 minutes                             |
| Relevance to Research Contribution | Misleading (Measures domain distance)  | Directly proves unsupervised transfer  |
+------------------------------------+----------------------------------------+----------------------------------------+
```

### Detailed Evaluation of Option A: Frozen-Model Direct Transfer
- **Mechanism:** Direct inference on VisA `cashew` images using an existing MVTec memory bank (e.g., `hazelnut` or `pill`) and the 15-class EfficientNet-B0 v3 classifier.
- **Fatal Flaw:** PatchCore calculates nearest-neighbor Euclidean distance between patch embeddings and a nominal memory bank:
  $$s(P_i) = \min_{m \in \mathcal{M}} \|P_i - m\|_2$$
  If an unseen cashew image is evaluated against a hazelnut memory bank, every patch embedding represents a domain mismatch, not a manufacturing anomaly. The resulting raw anomaly scores will exceed normal thresholds for virtually 100% of conforming cashew specimens, yielding a catastrophic false alarm rate ($FPR \approx 100\%$).
- **Classifier Breakdown:** EfficientNet-B0 v3 was trained strictly with a 15-class cross-entropy head over MVTec categories. Feeding cashew images into this model produces uncalibrated out-of-distribution softmax probabilities.
- **Verdict:** **DEFINITIVELY REJECTED.** Forcing zero-shot transfer onto unsupported categories violates basic computer vision principles and was explicitly barred in the prompt.

### Detailed Evaluation of Option B: Nominal Target-Domain Registration
- **Mechanism:** Adheres strictly to the canonical unsupervised anomaly detection paradigm established by Roth et al. (CVPR 2022):
  1. The feature extraction backbone (ResNet-18 pretrained on ImageNet-1K) remains **100% frozen** (zero gradient updates, zero fine-tuning).
  2. A target-specific nominal memory bank ($\mathcal{M}_{\text{cashew}}$) is constructed using **only conforming/normal specimens** ($y=0$) from the registration split.
  3. A 10% greedy k-center coreset is selected to compress patch representations.
  4. On an independent held-out nominal calibration cohort ($N=50$, $y=0$), the 99.5th percentile baseline ($\tau_{\text{p99}}$) is computed and frozen.
  5. The independent test partition ($N=200$: 100 nominal, 100 defective) is evaluated with locked weights and thresholds.
  6. EfficientNet-B0 v3 is cleanly documented as an in-domain supervised model that is inactive for unmodeled target categories, isolating the evaluation to the unsupervised core.
- **Scientific Value:** Proves whether DefectVision AI’s non-parametric patch feature pipeline can register and inspect a novel industrial product using fewer than 400 normal specimens, without requiring any defect training samples.
- **Verdict:** **SELECTED AS THE AUTHORITATIVE EXPERIMENTAL PROTOCOL.**

---

## 4. Formal Selection Conclusion

Option B (Nominal-Only Target-Domain Registration on VisA `cashew`) is officially selected. It represents the smallest defensible, mathematically valid, and publication-relevant experiment capable of proving independent generalization.
