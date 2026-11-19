# DefectVision AI — System Architecture Specification
**Release:** v1.0.0-rc1 (Research Prototype)  
**Date:** 2026-11-19  

---

## 1. Architectural Overview

DefectVision AI is an industrial visual anomaly inspection platform designed for zero-click multi-category surface inspection. The architecture integrates deep feature extraction, memory-bank density estimation, temperature-calibrated category recognition, and optical quality gating into a synchronous REST API and React single-page application.

```
                           +------------------------------------------+
                           |           User Interface (React)         |
                           |  - Drag & Drop Image Inspection Viewport |
                           |  - Interactive Heatmap Alpha Slider      |
                           |  - Production Profile Selector & Manager |
                           |  - Audit Ring-Buffer Telemetry History   |
                           +--------------------+---------------------+
                                                |
                                                | HTTP / REST (Multipart)
                                                v
                           +------------------------------------------+
                           |          FastAPI Inspection Service      |
                           +--------------------+---------------------+
                                                |
          +-------------------------------------+-------------------------------------+
          |                                     |                                     |
          v                                     v                                     v
+--------------------+               +--------------------+               +--------------------+
|  Optical Quality   |               |   Classification   |               |   PatchCore Core   |
|       Gate         |               |   & Routing Engine |               |   Anomaly Engine   |
+--------------------+               +--------------------+               +--------------------+
| - Laplacian Blur   |               | - EfficientNet-B0  |               | - ResNet-18        |
| - Lum Range Check  |               | - Calibrated Temp  |               |   (Layers 2 & 3)   |
| - Contrast Gating  |               | - Shannon Entropy  |               | - FAISS k-NN Index |
|                    |               | - OOD Gatekeeper   |               | - Score Heatmap    |
+--------------------+               +--------------------+               +--------------------+
```

---

## 2. Component Subsystems

### 2.1 Optical Image Quality Gate
Prior to neural computation, incoming specimen frames pass through a low-latency classical computer vision filter to prevent false positives caused by optical degradation:
- **Sharpness Metric:** Evaluates the variance of the Laplacian operator:
  $$\text{Var}(\nabla^2 I) \ge 25.0$$
  Frames failing this threshold are flagged as motion-blurred or out-of-focus.
- **Exposure Metric:** Computes global mean luminance $\mu_L \in [30, 240]$ and contrast $\sigma_L \ge 15.0$ to intercept underexposed, overexposed, or solid-color degenerate frames.
- **Handling:** Triggers `verdict: "REVIEW REQUIRED"` with explanation `"Quality Gate Failure"`.

### 2.2 Category Recognition & OOD Rejection (EfficientNet-B0)
When inspection runs in automatic mode (`mode="auto"`), the image is routed to a trained EfficientNet-B0 classifier:
- **Architecture:** EfficientNet-B0 backbone with feature dimension 1280, projecting to 15 MVTec AD category logits.
- **Temperature Scaling:** Softmax probabilities are calibrated using temperature $T = 1.3696$ to prevent overconfident misclassifications on out-of-distribution (OOD) images.
- **Shannon Entropy Gating:**
  $$H_{\text{norm}}(p) = -\frac{1}{\ln(15)} \sum_{c=1}^{15} p_c \ln(p_c)$$
  If $H_{\text{norm}} \ge 0.65$ or top confidence $p_{\max} < 0.70$, the specimen is classified as `UNSUPPORTED`.

### 2.3 PatchCore Anomaly Detection Engine
Anomaly localization and specimen-level scoring use the PatchCore memory-bank methodology:
- **Backbone Extractor:** Pre-trained ResNet-18, extracting mid-level feature representations from Layer 2 (stride 8) and Layer 3 (stride 16).
- **Patch Embedding:** Features are locally aggregated via average pooling ($3 \times 3$ kernel, stride 1) and concatenated to yield an embedding $\mathbf{f}_p \in \mathbb{R}^{384}$.
- **Coreset Memory Banks:** Each of the 15 categories maintains a greedy coreset-subsampled memory bank $\mathcal{M}_c$ stored as a contiguous numpy array and wrapped by a FAISS `IndexFlatL2` structure for fast neighbor lookup.
- **Anomaly Score:**
  $$s(I) = \max_{p \in \mathcal{P}} \min_{\mathbf{m} \in \mathcal{M}_c} \|\mathbf{f}_p - \mathbf{m}\|_2$$
- **Heatmap Reconstruction:** Local patch anomaly scores are mapped back to spatial coordinates, bi-linearly upsampled to $224 \times 224$, Gaussian smoothed ($\sigma = 4.0$), normalized to $[0, 1]$, and encoded as base64 JET colormaps.

---

## 3. Decision Boundary Engine

Each category uses a calibrated threshold $\tau_c$ derived from nominal training distributions:
1. **NORMAL (`NO DEFECT DETECTED`):** Score $s \le \tau_c \times 0.92$.
2. **DEFECTIVE (`POSSIBLE DEFECT DETECTED`):** Score $s \ge \tau_c \times 1.08$.
3. **REVIEW REQUIRED (`MANUAL INSPECTION REQUIRED`):** Borderline anomaly score within the $\pm 8\%$ guard band ($0.92 \tau_c < s < 1.08 \tau_c$) OR quality gate failure.
4. **UNSUPPORTED (`UNSUPPORTED OR UNKNOWN CATEGORY`):** Classifier confidence $< 0.70$ or entropy $\ge 0.65$.

---

## 4. Concurrency & Performance Profile

- **Threading Model:** FastAPI with asynchronous event loops for I/O; CPU-bound PyTorch operations execute in a thread pool with OpenMP locks isolated.
- **Memory Footprint:** Resident memory across all 15 PatchCore memory banks, FAISS indexes, and ResNet-18 weights consumes $\approx 1.8 \text{ GB}$ RAM.
- **Latency Targets:**
  - Image decode & quality gate: $8 - 15 \text{ ms}$
  - Category classification: $15 - 25 \text{ ms}$
  - PatchCore feature extraction: $60 - 95 \text{ ms}$
  - FAISS $k$-NN query & heatmap generation: $20 - 35 \text{ ms}$
  - **Total Pipeline Latency:** $\approx 110 - 165 \text{ ms}$ (CPU, multi-core).
