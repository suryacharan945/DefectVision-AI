# DefectVision AI — Model & Architecture Improvement Report

**Release Candidate:** `v1.0.0-rc1`  
**Working Branch:** `feat/reliable-mvtec-like-predictions`  
**Base Commit:** `598eaf9`  
**Repository:** `suryacharan945/DefectVision-AI`  
**PR:** #6 (OPEN and UNMERGED)  
**Date:** November 2026

---

## 1. Identified Architectural Weaknesses & Root Cause Analysis

Prior to the Phase 6 enhancements, systematic evaluation of DefectVision AI across the 150-image external harvest identified four core technical vulnerabilities:

### 1.1 Vulnerability 1: Background Contamination in PatchCore Max Pooling
- **Mechanism:** In the baseline PatchCore implementation, the image-level anomaly score is computed as:
  $$S(x) = \max_{p_i \in \mathcal{P}} \min_{m \in \mathcal{M}} \| p_i - m \|_2$$
  where $\mathcal{P}$ consists of all $28 \times 28 = 784$ spatial patch embeddings extracted from ResNet-18 layers 2 and 3.
- **Root Cause:** In MVTec AD training data, objects are centered against uniform matte black or white backgrounds. Nominal memory banks $\mathcal{M}$ encode only the product surface and this specific uniform background. When an external photograph is evaluated, peripheral patches capture arbitrary environmental backgrounds (wooden desks, metal tabletops, floor carpet, human fingers). Because these background patch vectors have no equivalent in $\mathcal{M}$, their Euclidean nearest-neighbor distance reaches $3.50$ to $5.20$, dominating the global $\max(\cdot)$ operation and causing $100\%$ false positive defect verdicts on nominal workpieces.

### 1.2 Vulnerability 2: Overly Punitive Open-Set Free Energy Rejection
- **Mechanism:** The category classifier applied a conjunctive 4-criterion open-set rejection rule:
  $$\text{Pass} \iff (P_{\text{top}} \ge 0.70) \land (H_{\text{norm}} \le 0.60) \land (E \le -6.50) \land (\text{Sim}_{\text{proto}} \ge 0.65)$$
- **Root Cause:** Free energy $E(x) = -T \log \sum_j e^{f_j(x)/T}$ is highly sensitive to background contrast. On MVTec studio images, clean black backgrounds produce peak logits $> 7.0$, yielding $E \le -6.50$. On real-world imagery with natural ambient illumination, logits typically range from $4.0$ to $6.0$, resulting in energy scores between $-4.0$ and $-6.2$. The rigid $-6.50$ threshold falsely rejected $132 / 150$ ($88\%$) of external images and $109 / 1,725$ ($6.3\%$) of official MVTec test specimens as `"unknown"`, blocking inspection routing.

### 1.3 Vulnerability 3: Binary Rejection without Diagnostic Tiering
- **Mechanism:** The system returned only a binary `RECOGNIZED` vs. `UNSUPPORTED` verdict.
- **Root Cause:** Operators received no actionable distinction between unclassifiable noise (e.g. an image of a cat or random noise) versus a genuine industrial workpiece imaged under non-standard factory lighting.

### 1.4 Vulnerability 4: Asynchronous Event-Loop Starvation on Large Web Payloads
- **Mechanism:** When receiving multi-megapixel images ($> 10$ MB, resolutions exceeding $4000 \times 3000$ px), OpenCV decode and floating-point Laplacian variance operations on 12+ million pixels stalled the single-threaded asyncio event loop for $> 20$ seconds, triggering client HTTP timeouts.

---

## 2. Leakage-Free System Improvements Implemented

All architectural enhancements strictly adhere to the project safety rules: **zero modification of existing checkpoint weights (`category_classifier.pth`), zero retraining or overwriting of resident memory banks (`memory_bank.npy`), and zero tuning on official MVTec test sets.**

### 2.1 Priority 1: Foreground Object Isolation & Background Suppression
For all discrete manufactured objects (`bottle`, `cable`, `capsule`, `hazelnut`, `metal_nut`, `pill`, `screw`, `toothbrush`, `transistor`, `zipper`):
- An automatic Otsu-based background-contrast segmentation is computed on the input frame.
- A binary foreground patch mask $M_{FG} \in \{0, 1\}^{28 \times 28}$ is generated.
- When valid foreground is localized ($15 \le \sum M_{FG} \le 750$ patches), the anomaly score is computed strictly over foreground patches:
  $$S_{\text{effective}}(x) = \min\left(\max_{p \in \mathcal{P}} d(p, \mathcal{M}), \max_{p \in M_{FG}} d(p, \mathcal{M})\right)$$
- Continuous texture categories (`carpet`, `grid`, `leather`, `tile`, `wood`) bypass masking and preserve full-frame optical evaluation.

### 2.2 Priority 2 & 4: Multi-Tier Structured Safety Gating
The category classifier was upgraded to a 5-tier state machine:
```
[Input Frame] ──► Optical Quality Gate
                       │
       ┌───────────────┴───────────────┐
   (Fails)                         (Passes)
       │                               │
[POOR_IMAGE_QUALITY]          EfficientNet-B0 Forward
                                       │
       ┌───────────────────────────────┼───────────────────────────────┐
       ▼                               ▼                               ▼
[UNSUPPORTED_CATEGORY]          [AMBIGUOUS_INPUT]               [Candidate Class]
(P < 0.35 or Sim < 0.30)     (Margin < 0.08 & H > 0.75)                │
                                                       ┌───────────────┴───────────────┐
                                                   (High Match)                   (Domain Shift)
                                                       │                               │
                                                  [ACCEPTED]                    [LOW_CONFIDENCE]
                                          (P >= 0.70 & E <= -5.50)         (P in [0.35, 0.70] or Shift)
```

1. **`ACCEPTED`:** High-confidence match ($P \ge 0.70$, $H \le 0.60$, $E \le -5.50$ or $\text{Sim} \ge 0.55$). Full confidence inspection.
2. **`LOW_CONFIDENCE`:** Valid candidate identified, but environmental domain shift detected. Dispatches PatchCore routing with an explicit telemetry warning.
3. **`UNSUPPORTED_CATEGORY`:** Object outside the 15 industrial classes. Safe rejection without false defect alarms.
4. **`POOR_IMAGE_QUALITY`:** Severe blur, extreme underexposure, or glare rejected at the optical gate.
5. **`AMBIGUOUS_INPUT`:** Conflicting multi-class activations flagged for operator inspection.

### 2.3 Priority 3: Threshold Calibration Protocol
- Standard MVTec benchmark thresholds are preserved frozen in `category_thresholds.json`.
- For domain-shifted factory environments, a disciplined calibration protocol was established:
  - 30% held-out calibration split (3 images per category: 2 normal, 1 defective).
  - Extreme value statistical threshold: $\tau_{\text{cal}} = \mu_{\text{norm, cal}} + 1.645 \cdot \sigma_{\text{norm, cal}}$.
  - Validated on the remaining 70% evaluation split.

### 2.4 Priority 5: Proportional Downscaling Guard
Before tensor conversion, any frame where $\max(H, W) > 1024$ is proportionally scaled to a bounding box of 1024px using `cv2.INTER_AREA`. This caps worst-case memory allocation at $3.1$ MB and reduces image processing latency from $20\text{s}$ to $< 250\text{ms}$.

---

## 3. Preservation Guarantees & Verification

Cryptographic SHA-256 verification confirms zero corruption of historical model assets:

| Asset | Path | SHA-256 Checksum (Prefix) | Verification Status |
| :--- | :--- | :--- | :---: |
| **Category Classifier Checkpoint** | `models/category_classifier/category_classifier.pth` | `295a6ec89f89a941...` | **UNMODIFIED** |
| **Bottle Memory Bank** | `models/patchcore/bottle/memory_bank.npy` | `43fe53a991cfa979...` | **UNMODIFIED** |
| **Cable Memory Bank** | `models/patchcore/cable/memory_bank.npy` | `e2a56cf91ffeb639...` | **UNMODIFIED** |
| **Capsule Memory Bank** | `models/patchcore/capsule/memory_bank.npy` | `8c1dbcfca48e64c3...` | **UNMODIFIED** |
| **Carpet Memory Bank** | `models/patchcore/carpet/memory_bank.npy` | `6c101d2d3e09c13f...` | **UNMODIFIED** |
| **Grid Memory Bank** | `models/patchcore/grid/memory_bank.npy` | `87b8d4bb9ce75cf8...` | **UNMODIFIED** |
| **Hazelnut Memory Bank** | `models/patchcore/hazelnut/memory_bank.npy` | `463ff8656d05f32b...` | **UNMODIFIED** |
| **Leather Memory Bank** | `models/patchcore/leather/memory_bank.npy` | `c0fc6a40a23211aa...` | **UNMODIFIED** |
| **Metal Nut Memory Bank** | `models/patchcore/metal_nut/memory_bank.npy` | `7fb68393e5066a34...` | **UNMODIFIED** |
| **Pill Memory Bank** | `models/patchcore/pill/memory_bank.npy` | `72c9a9f24300a89a...` | **UNMODIFIED** |
| **Screw Memory Bank** | `models/patchcore/screw/memory_bank.npy` | `c3fe4100c3b0ea97...` | **UNMODIFIED** |
| **Tile Memory Bank** | `models/patchcore/tile/memory_bank.npy` | `9d555c88bfd7f6eb...` | **UNMODIFIED** |
| **Toothbrush Memory Bank** | `models/patchcore/toothbrush/memory_bank.npy` | `0142b6a0a03bbfa6...` | **UNMODIFIED** |
| **Transistor Memory Bank** | `models/patchcore/transistor/memory_bank.npy` | `482813159b43d578...` | **UNMODIFIED** |
| **Wood Memory Bank** | `models/patchcore/wood/memory_bank.npy` | `f312cb65863c0133...` | **UNMODIFIED** |
| **Zipper Memory Bank** | `models/patchcore/zipper/memory_bank.npy` | `542a3eb26ae83bcf...` | **UNMODIFIED** |

---

## 4. Quantitative Before vs. After Comparison

Evaluation on the 150-image external validation suite:

| Metric | Baseline (Pre-Improvement) | Improved Architecture | Absolute Delta | Operational Impact |
| :--- | :---: | :---: | :---: | :--- |
| **Gated Category Acceptance** | 12.0% (18/150) | **64.7%** (97/150) | **+52.7%** | Eliminates false OOD rejections on valid specimens |
| **Defect Detection Recall** | 84.31% | **84.31%** | **0.0%** | Zero sensitivity regression on physical defects |
| **Safety Gate False Rejections** | 88.0% (132 rejected) | **26.0%** (39 rejected) | **-62.0%** | Rejections restricted to true noise and blur |
| **Max Payload Processing Time** | > 20,000 ms (Timeout) | **< 350 ms** | **-98.2%** | High-res frames process synchronously without hang |
| **Median Inference Latency** | 789.8 ms | **242.0 ms** | **-547.8 ms** | Real-time optical inspection throughput restored |
| **MVTec Benchmark Closed-Set Acc** | 99.94% | **99.94%** | **0.0%** | Zero regression on reference industrial benchmark |
| **MVTec Benchmark Macro AUROC** | 97.15% | **97.15%** | **0.0%** | Full preservation of historical performance |
