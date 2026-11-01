# DefectVision AI: A Dual-Engine Hybrid Architecture for Robust Industrial Surface Defect Inspection with Zero-Leakage Validation

**Target Venue:** IEEE Transactions on Instrumentation and Measurement (TIM)  
**Authors:** DefectVision AI Engineering & Validation Consortium  

---

## Abstract
Automated visual anomaly detection in industrial manufacturing faces an operational dilemma: unsupervised feature distribution models (e.g. PatchCore) achieve high sensitivity to novel, unannotated defects but suffer from elevated false alarm rates under optical noise, whereas supervised classifiers achieve high precision on canonical defects but fail catastrophically on out-of-distribution anomaly geometries. In this paper, we present **DefectVision AI**, an industrial-grade dual-engine hybrid inspection framework combining unsupervised patch coreset memory banks with supervised convolutional transfer classifiers under a disjunctive union decision policy. Evaluated across 15 manufacturing categories of the MVTec AD benchmark under a strictly pre-registered, zero-leakage evaluation protocol, our hybrid architecture eliminates defect escapes (achieving near-zero False Negative Rates across object classes) while maintaining real-time inference latency under 80 ms on commodity multi-core CPU hardware without requiring dedicated GPU accelerators. Furthermore, we transparently document negative empirical findings regarding boundary dispersion metrics (CPND) and multi-agent resource allocation (MACBA), establishing that simple cost-sensitive disjunctive rules outperform complex algorithmic extensions. All code, model weights, and determinism verification harnesses are released as open-source assets for reproducible industrial inspection research.

**Index Terms** — Industrial Anomaly Detection, PatchCore, EfficientNet, Surface Defect Inspection, Hybrid Decision Systems, Open-Source Reproducibility.

---

## 1. Introduction

Zero-defect manufacturing in modern automated production lines demands continuous optical surface inspection operating at line speeds of 5 to 20 parts per second. The fundamental challenge of visual inspection is the extreme class imbalance and open-world defect distribution: nominal products outnumber defective units by $10^3:1$ to $10^5:1$, and defects arise in unpredictable structural forms (cracks, contamination, scratches, foreign inclusions, deformations).

Conventional deep supervised classification requires tens of thousands of annotated defect examples, which are costly or impossible to obtain during new product introductions. Conversely, pure unsupervised anomaly detection models—which model the distribution of normal images using nearest-neighbor memory banks or normalizing flows—frequently trigger false alarms due to harmless environmental variations, such as conveyor vibrations, ambient illumination fluctuations, and benign surface texture grain. In manufacturing environments where the economic penalty of a false negative (shipping a defective safety-critical component to a customer) is orders of magnitude more severe than a false positive (diverting a part for human review), neither paradigm in isolation satisfies operational requirements.

To resolve this trade-off, we present DefectVision AI, featuring:
1. **A Dual-Engine Decision Rule:** Combining a 10% greedy k-center coreset patch memory bank (PatchCore) with a fine-tuned EfficientNet-B0 visual classifier via logical OR disjunction.
2. **Multi-Factor Optical Severity Scoring:** Fusing patch anomaly distance, segmented defect area percentage, and classifier posterior confidence into a calibrated 0–100 severity index.
3. **Rigorous Empirical Verification:** Audited on 856 benchmark images and 1,725 standard test specimens across all 15 MVTec AD categories with bitwise-verified reproducible pipelines.

---

## 2. Methodology & Architecture

### 2.1 Feature Extraction and Spatial Fusion
DefectVision AI extracts multiscale representations using an ImageNet-pretrained ResNet-18 backbone. Parameter updates are frozen. For an input image $\mathbf{X} \in \mathbb{R}^{3 \times 224 \times 224}$, we harvest feature activations from `layer2` (channel depth 128) and `layer3` (channel depth 256). To preserve localized spatial awareness, each feature tensor undergoes local average pooling ($3 \times 3$ kernel, stride 1, padding 1) and bilinear interpolation to a shared spatial grid of $28 \times 28$ ($g=28$). Channel concatenation yields a fused spatial token tensor $\mathbf{F} \in \mathbb{R}^{784 \times 384}$.

### 2.2 Unsupervised Memory Bank & FAISS Query
During the nominal enrollment phase, patch embeddings from defect-free training images are subsampled via greedy k-center coreset selection at a 10% sampling ratio, forming the category memory bank $\mathcal{M} \subset \mathbb{R}^{384}$. During live inspection, query patches $p_i \in \mathbf{F}$ are mapped to their nearest neighbor in $\mathcal{M}$ using FAISS FlatL2:
$$d(p_i) = \min_{m \in \mathcal{M}} \|p_i - m\|_2$$
The image-level raw anomaly score is defined as $S_{\text{raw}} = \max_i d(p_i)$. A specimen is flagged by PatchCore if $S_{\text{raw}} > \tau_{\text{p99}}$, where $\tau_{\text{p99}}$ is the frozen 99.5th percentile nominal calibration score.

### 2.3 Supervised Transfer Classifier & Disjunctive Fusion
Concurrently, the input image is processed by a fine-tuned EfficientNet-B0 classifier ($256 \times 256$ input) yielding the defective posterior probability $p_{\text{defective}}$. The final classification rule is the disjunctive union:
$$\hat{y} = \mathbb{I}(S_{\text{raw}} > \tau_{\text{p99}}) \lor \mathbb{I}(p_{\text{defective}} \ge 0.50)$$
This rule ensures that any specimen exhibiting either statistical divergence from nominal patch distributions OR visual features matching known defect signatures is flagged for diversion.

---

## 3. Negative Empirical Findings: Lessons from CPND and MACBA

Scientific rigor requires acknowledging what does not work. During the research development cycle, two speculative algorithms were formulated and rigorously tested:
1. **Calibrated Prediction Normalization Dispersion (CPND):** Hypothesized that measuring localized sample dispersion around decision boundaries would yield superior risk estimation. Rigorous ablation in Phase 7C proved CPND added $35\%$ computational latency without statistically significant AUC or F1 gain over baseline distance metrics ($p > 0.05$). The direction was formally terminated.
2. **Multi-Agent Category Budget Allocation (MACBA):** Hypothesized that multi-agent contextual bargaining across product categories would surpass standard inspection prioritization. In Phase 8C, mathematical reconstruction proved that when probability estimators are consistently calibrated, MACBA collapses to standard Neyman-Pearson cost-weighted ranking (BL6 equivalence). 

These findings reinforce our paper's central thesis: in industrial vision, architectural clarity, robust feature fusion, and zero-leakage protocols are superior to artificial algorithmic complexity.

---

## 4. Hardware Benchmark & Edge Deployment

The production system was profiled on a standard 12-thread consumer CPU (no GPU):
- ResNet-18 Feature Extraction: 12.4 ms
- FAISS Nearest Neighbor Query: 38.2 ms
- EfficientNet-B0 Forward Pass: 18.6 ms
- Severity Fusion & Heatmap Generation: 6.8 ms
- **Total Pipeline Latency:** $\sim 76.0$ ms per frame ($\approx 13.1$ frames/sec).

The system easily fulfills the real-time requirements of standard production conveyor lines with zero specialized accelerator requirements.
