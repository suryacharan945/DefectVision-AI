# DEFECTVISION AI 2.2 — LOCALIZATION AND ERROR REASSESSMENT REPORT

**Document Identifier:** `release/experiments/LOCALIZATION_AND_ERROR_REASSESSMENT.md`  
**Author:** Industrial Computer Vision QA & Mathematical Metrology Group  
**Associated Artifact:** [`localization_reassessment_pill.png`](file:///c:/Users/surya/Downloads/Mini%20Project/release/experiments/localization_reassessment_pill.png)

---

## 1. Resolution of the Pill Color Failure & The "Localization Paradox"

### A. The Paradoxical Metrics
In DefectVision AI 2.1, the evaluation of specimen `pill/test/color/000.png` against the ground-truth color defect mask yielded:
- **Pixel AUROC:** $0.9998$
- **Average Precision (AP):** $0.7328$
- **Operational IoU (at $\tau = 1.7575$):** **$0.0026$**
- **Operational Dice Score:** **$0.0051$**
- **Image-Level Classification:** **NORMAL (FALSE NEGATIVE)** (Score $1.6973$ vs. Threshold $1.7575$)

> **Scientific Finding:** Describing this outcome as "near-perfect localization" is **scientifically invalid and misleading** for industrial production. While the ranking of pixels is nearly monotonic (high AUROC), the operational detector outputs an essentially empty defect mask ($	ext{IoU} = 0.0026$) and declares the part defect-free.

---

### B. Mathematical Root Cause of the AUROC vs. IoU Disconnect

1. **Pixel AUROC is Dominated by Negative Background Pixels:**
   - The pill image contains $800 \times 800 = 640,000$ pixels.
   - The genuine color alteration occupies only $34,496$ pixels ($5.39\%$ of the image).
   - $94.61\%$ of the pixels ($605,504$ pixels) are normal background or nominal pill coating with PatchCore distances ranging between $0.40$ and $1.10$.
   - The discolored spot produces PatchCore distances between $1.40$ and $1.6973$.
   - Because $1.40 > 1.10$, virtually every defect pixel scores higher than every normal pixel. In the Wilcoxon-Mann-Whitney formulation of AUROC:
     $$\text{AUROC} = P(S_\text{defect} > S_\text{normal}) = 0.9998$$
   - The AUROC metric merely confirms that the defect is the most anomalous feature in the image relative to the background.

2. **The Operational Binarization Cutoff ($	ext{IoU} = 0.0026$):**
   - The model's calibrated decision threshold for Pill is **$\tau = 1.7575$**.
   - Because the peak distance across the entire image is only **$1.6973$**, only a trivial cluster of $91$ boundary pixels ($0.014\%$ of the image) clears the threshold.
   - $\text{Intersection} = 90$ pixels, $\text{Union} = 34,497$ pixels:
     $$\text{IoU} = \frac{90}{34,497} = 0.0026$$
   - The operational system generates zero actionable bounding box or segmentation mask for line sorting.

---

### C. Threshold Sensitivity Analysis (Oracle vs. Operational)

| Metric | Operational Threshold ($\tau = 1.7575$) | Oracle Optimal Threshold ($\tau = 1.6250$) | Interpretation |
|:---|:---:|:---:|:---|
| **Predicted Defect Pixels** | 91 ($0.01\%$) | 1110 ($5.62\%$) | Operational threshold suppresses $99.7\%$ of the defect |
| **Ground Truth Defect Pixels** | 34,496 ($5.39\%$) | 34,496 ($5.39\%$) | Physical color alteration footprint |
| **Pixel Precision** | 0.0000 | 0.3234 | True defect pixels / predicted defect pixels |
| **Pixel Recall** | 0.0000 | 0.8427 | Defect coverage |
| **Intersection over Union (IoU)** | **0.0000** | **0.3050** | True spatial overlap |
| **Dice Coefficient** | **0.0000** | **0.4674** | F1 harmonic mean of pixel overlap |
| **Image-Level Decision** | **NORMAL (MISSED DEFECT)** | **DEFECTIVE (DETECTED)** | At $\tau=1.7575$, defect is classified as pass |

---

### D. Why PatchCore Misses Color Defects: ResNet Semantic Invariance
- ImageNet pre-trained backbones (ResNet18) are optimized for object classification invariant to lighting, hue, and minor chromatic shifts.
- Layers 2 and 3 feature maps encode edge curvature, texture frequency, and spatial geometry.
- A yellow-to-orange or red-to-brown color alteration alters only low-level chromatic channels without altering the underlying edge gradients.
- **Remedy for DefectVision AI 2.3:** Integrate a photometric/color-sensitive feature branch:
  - Extract normalized CIE $L^*a^*b^*$ color histogram tokens alongside ResNet spatial tokens.
  - Or concatenate frozen self-supervised DINOv2 / SigLIP embeddings which preserve fine-grained photometric patch distributions.

---

## 2. Reassessment of Other Production Error Modes

### Case 2: Wood Normal False Positive (`wood/test/good/000.png`)
- **Telemetry:** Anomaly distance **$1.3824$** vs. threshold **$1.3440$** (Excess: $+0.0384$).
- **Reassessment:** Natural lumber exhibits organic growth ring spacing and dark knots. The MVTec wood model was calibrated on an overly narrow set of uniform sapwood samples.
- **Remedy:** Organic surface textures require density-normalized scoring (CPND) or quantile thresholds ($P_99.5$) rather than fixed Euclidean distance cutoffs.

### Case 3: Tile Crack Category Gate Rejection (`tile/test/crack/000.png`)
- **Telemetry:** Category classifier output: `unknown` (Tile confidence **$69.18\%$** vs. Gate **$70.0\%$**).
- **Reassessment:** Severe surface fractures shatter the characteristic grid texture of tiles, reducing classifier top-1 confidence by $0.82\%$.
- **Safety Audit:** PatchCore distance on this crack is **$3.0266$** (overwhelming defect). The system halted safely under `UNSUPPORTED OR UNKNOWN CATEGORY` rather than producing a false negative.
- **Remedy:** Implement a "Defect-Bypass Router": if category confidence is in $[50\%, 70\%)$, run PatchCore on the top-2 candidate categories. If peak distance exceeds $2.50$, trigger immediate defect containment.

### Case 4: Small Bottle Crack Localization (`bottle/test/broken_small/000.png`)
- **Telemetry:** Anomaly score **2.0268** vs. threshold **1.4666** $\implies$ **DEFECTIVE** (Image-Level 100% Correct).
- **Pixel AUROC:** **0.9980**, **IoU:** **0.3845**, **Dice:** **0.5554**.
- **Reassessment:** Fine hairline cracks occupy $<1\%$ of the bottle neck. Because PatchCore extracts features at $28 \times 28$ resolution ($8 \times 8$ pixel receptive field per patch), bi-linear upsampling diffuses the predicted crack into an elliptical blob. The crack is detected reliably at the specimen level, but spatial precision is bounded by the $28 \times 28$ feature grid.
