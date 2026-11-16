# DefectVision AI: A Dual-Engine Hybrid Architecture for Robust Industrial Surface Defect Inspection — An Empirical Systems Case Study

**Target Venue:** IEEE Transactions on Instrumentation and Measurement (TIM)  
**Authors:** DefectVision AI Engineering & Validation Consortium  

---

## Abstract
Automated visual anomaly detection in industrial manufacturing faces an operational dilemma: unsupervised feature distribution models (e.g. PatchCore) achieve high sensitivity to novel, unannotated defects but suffer from elevated false alarm rates under optical noise, whereas supervised classifiers achieve high precision on canonical defects but fail catastrophically on out-of-distribution anomaly geometries. In this paper, we present **DefectVision AI**, an industrial-grade dual-engine hybrid inspection framework combining unsupervised patch coreset memory banks with supervised convolutional transfer classifiers under a disjunctive union decision policy. Evaluated across 15 manufacturing categories of the MVTec AD benchmark on an audited 856-specimen development-exposed partition (625 defective, 231 nominal), our hybrid architecture slashes defect escapes relative to the supervised classifier alone by **$48.6\%$** (54 fewer missed defects; defect escapes dropped from 111 to 57, recall rose from $82.24\%$ to $90.88\%$), while incurring **11 additional false alarms** (false positive rate rose from $0.43\%$ to $5.19\%$). On standard multi-core CPU hardware without GPU acceleration, the system achieves a median dual-model forward pass latency of **$450.6$ ms** and a median end-to-end HTTP API inspection latency of **$881.7$ ms** ($p95 = 1455.7$ ms). Furthermore, we transparently document negative empirical findings regarding boundary dispersion metrics (CPND) and multi-agent resource allocation (MACBA), establishing that simple cost-sensitive disjunctive rules outperform complex algorithmic extensions. All code, model weights, and determinism verification harnesses are released as open-source assets for reproducible industrial inspection research.

**Index Terms** — Industrial Anomaly Detection, PatchCore, EfficientNet, Surface Defect Inspection, Hybrid Decision Systems, Open-Source Reproducibility, Failure Mode Analysis.

---

## 1. Introduction

Zero-defect manufacturing in modern automated production lines demands continuous optical surface inspection. The fundamental challenge of visual inspection is the extreme class imbalance and open-world defect distribution: nominal products outnumber defective units by $10^3:1$ to $10^5:1$, and defects arise in unpredictable structural forms (cracks, contamination, scratches, foreign inclusions, deformations).

Conventional deep supervised classification requires tens of thousands of annotated defect examples, which are costly or impossible to obtain during new product introductions. Conversely, pure unsupervised anomaly detection models—which model the distribution of normal images using nearest-neighbor memory banks or normalizing flows—frequently trigger false alarms due to harmless environmental variations, such as conveyor vibrations, ambient illumination fluctuations, and benign surface texture grain. In manufacturing environments where the economic penalty of a false negative (shipping a defective safety-critical component to a customer) is orders of magnitude more severe than a false positive (diverting a part for human review), neither paradigm in isolation satisfies operational requirements.

To resolve this trade-off, we present DefectVision AI, featuring:
1. **A Dual-Engine Decision Rule:** Combining a 10% greedy k-center coreset patch memory bank (PatchCore) with a fine-tuned EfficientNet-B0 visual classifier via logical OR disjunction.
2. **Multi-Factor Optical Severity Scoring:** Fusing patch anomaly distance, segmented defect area percentage, and classifier posterior confidence into a calibrated 0–100 severity index.
3. **Rigorous Empirical Verification:** Audited on 856 development-exposed benchmark images across all 15 MVTec AD categories with bitwise-verified reproducible pipelines.

---

## 2. Methodology & Architecture

### 2.1 Feature Extraction and Spatial Fusion
DefectVision AI extracts multiscale representations using an ImageNet-pretrained ResNet-18 backbone with frozen parameters. For an input image $\mathbf{X} \in \mathbb{R}^{3 \times 224 \times 224}$, we harvest feature activations from `layer2` (channel depth 128) and `layer3` (channel depth 256). To preserve localized spatial awareness, each feature tensor undergoes local average pooling ($3 \times 3$ kernel, stride 1, padding 1) and bilinear interpolation to a shared spatial grid of $28 \times 28$ ($g=28$). Channel concatenation yields a fused spatial token tensor $\mathbf{F} \in \mathbb{R}^{784 \times 384}$.

### 2.2 Unsupervised Memory Bank & FAISS Query
During nominal enrollment, patch embeddings from defect-free training images are subsampled via greedy k-center coreset selection at a 10% sampling ratio, forming category memory bank $\mathcal{M} \subset \mathbb{R}^{384}$. During live inspection, query patches $p_i \in \mathbf{F}$ are mapped to their nearest neighbor in $\mathcal{M}$ using FAISS FlatL2:
$$d(p_i) = \min_{m \in \mathcal{M}} \|p_i - m\|_2$$
The image-level raw anomaly score is defined as $S_{\text{raw}} = \max_i d(p_i)$. A specimen is flagged by PatchCore if $S_{\text{raw}} > \tau_{\text{p99}}$, where $\tau_{\text{p99}}$ is the frozen 99.5th percentile nominal calibration score.

### 2.3 Supervised Transfer Classifier & Disjunctive Fusion
Concurrently, the input image is processed by a fine-tuned EfficientNet-B0 classifier ($256 \times 256$ input) yielding defective posterior probability $p_{\text{defective}}$. The final classification rule is the disjunctive union:
$$\hat{y} = \mathbb{I}(S_{\text{raw}} > \tau_{\text{p99}}) \lor \mathbb{I}(p_{\text{defective}} \ge 0.50)$$
This rule ensures that any specimen exhibiting either statistical divergence from nominal patch distributions OR visual features matching known defect signatures is flagged for diversion.

---

## 3. Quantitative Results & The Asymmetric Operating-Point Trade-off

Evaluated across the 856 benchmark images (625 defective, 231 nominal), the empirical results reveal the exact operational trade-off of the hybrid system:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              AUDITED BENCHMARK PERFORMANCE                             │
├───────────────────────────┬──────────┬───────────┬────────┬─────────────┬──────────────┤
│ Metric                    │ PatchCore│ EfficientNet-B0    │ DefectVision AI (Hybrid)   │
├───────────────────────────┼──────────┼───────────┼────────┼─────────────┼──────────────┤
│ Accuracy                  │ 78.15%   │ 86.92%    │        │ **91.94%**  │ (+5.02% gain)│
│ Balanced Accuracy         │ 83.54%   │ 90.90%    │        │ **92.84%**  │ (+1.94% gain)│
│ Defect Precision (PPV)    │ 97.61%   │ **99.81%**│        │ 97.93%      │              │
│ Defect Recall (TPR)       │ 71.84%   │ 82.24%    │        │ **90.88%**  │ (+8.64% gain)│
│ Specificity (TNR)         │ 95.24%   │ **99.57%**│        │ 94.81%      │              │
│ F1-Score                  │ 0.8276   │ 0.9018    │        │ **0.9427**  │ (+0.0409)    │
│ AUROC                     │ 0.8159*  │ **0.9809**│        │ 0.9608      │              │
│ AUPRC                     │ 0.9266   │ **0.9932**│        │ 0.9745      │              │
│ False Positive Rate (FPR) │ 4.76%    │ **0.43%** │        │ 5.19%       │              │
│ False Negative Rate (FNR) │ 28.16%   │ 17.76%    │        │ **9.12%**   │ (-48.6% drop)│
└───────────────────────────┴──────────┴───────────┴────────┴─────────────┴──────────────┘
*Note: PatchCore AUROC is 0.8159 when pooling uncalibrated raw Euclidean distances; category-standardized AUROC is 0.9373.
```

### Confusion Matrices:
- **PatchCore Alone:** $\text{TN}=220, \text{FP}=11, \text{FN}=176, \text{TP}=449$
- **EfficientNet Alone:** $\text{TN}=230, \text{FP}=1, \text{FN}=111, \text{TP}=514$
- **DefectVision AI Hybrid:** $\text{TN}=219, \text{FP}=12, \text{FN}=57, \text{TP}=568$

### Operating-Point Analysis:
The Hybrid is **not** universally superior across all metrics. In fact, EfficientNet-B0 alone achieves superior continuous discrimination (AUROC 0.9809 vs 0.9608; AUPRC 0.9932 vs 0.9745) and superior false-alarm suppression (1 FP vs 12 FP). The hybrid's advantage exists solely at the **fixed decision operating point**, where it achieves **54 fewer missed defects** (slashing defect escapes from 111 to 57) at the cost of **11 additional false alarms** (a 12-fold increase in false positives). In safety-critical manufacturing where defect escape costs vastly exceed inspection diversion costs, this represents an operationally justified trade-off.

---

## 4. Negative Empirical Findings: Lessons from CPND and MACBA

Scientific rigor requires acknowledging what does not work. During the research development cycle, two speculative algorithms were formulated and rigorously tested:
1. **Calibrated Prediction Normalization Dispersion (CPND):** Hypothesized that measuring localized sample dispersion around decision boundaries would yield superior risk estimation. Rigorous ablation in Phase 7C proved CPND added $35\%$ computational latency without statistically significant AUC or F1 gain over baseline distance metrics ($p > 0.05$). The direction was formally terminated.
2. **Multi-Agent Category Budget Allocation (MACBA):** Hypothesized that multi-agent contextual bargaining across product categories would surpass standard inspection prioritization. In Phase 8C, mathematical reconstruction proved that when probability estimators are consistently calibrated, MACBA collapses to standard Neyman-Pearson cost-weighted ranking (BL6 equivalence). 

These findings reinforce our paper's central thesis: in industrial vision, architectural clarity, robust feature fusion, and transparent protocol reporting are superior to artificial algorithmic complexity.

---

## 5. Hardware Latency Profile & Deployment Boundaries

The production system was profiled on a 12-thread consumer CPU across 50 iterations:
- **PatchCore ResNet-18 + FAISS L2:** Mean $= 302.7$ ms, Median (p50) $= 268.1$ ms
- **EfficientNet-B0 Forward Pass:** Mean $= 256.3$ ms, Median (p50) $= 170.1$ ms
- **Direct Dual-Model Total:** Mean $= 559.0$ ms, Median (p50) $= 450.6$ ms (p95: 1173.7 ms)
- **HTTP API `/inspect-frame`:** Mean $= 950.9$ ms, Median (p50) $= 881.7$ ms (p95: 1455.7 ms)
- **Resident RAM Footprint:** 645 MB peak working set.

**Deployment Boundary:** With a median cycle time of ~881.7 ms on CPU (~1.1 to 2.2 parts/sec), the system is suitable for manual/semi-automated inspection stations or asynchronous batch verification. High-speed inline gating (>10 parts/sec) requires dedicated GPU acceleration or TensorRT compilation.

---

## 6. Threats to Validity & Limitations

1. **Development-Exposed Benchmark:** The 856-image benchmark is in-domain and development-exposed via historical prototype ablations. Performance cannot be claimed as zero-leakage or indicative of out-of-domain generalization.
2. **Quarantined Independent Benchmarks:** External datasets (VisA, BTAD, Chukyo) remain unaccessed to preserve blind external validation. Cross-domain transfer remains an open research question.
3. **Photometric Sensitivity:** Additive sensor noise ($\sigma \ge 0.10$) elevates PatchCore anomaly scores (+0.28 shift), requiring optical preprocessing filters on physical factory lines.
