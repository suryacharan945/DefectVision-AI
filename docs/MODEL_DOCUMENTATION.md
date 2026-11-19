# DefectVision AI — Model Architecture & Checkpoint Documentation
**Release:** v1.0.0-rc1 (Research Prototype)  
**Date:** 2026-11-19  

---

## 1. Primary Inspection Engine: PatchCore ResNet-18

The core visual anomaly detection framework is based on PatchCore (Roth et al., 2022), leveraging localized neighbourhood-aware patch representations.

### 1.1 Feature Extractor Architecture
- **Backbone Network:** ResNet-18 (pre-trained on ImageNet-1k).
- **Target Layers:**
  - `layer2`: Channel depth 128, spatial stride 8 relative to input.
  - `layer3`: Channel depth 256, spatial stride 16 relative to input.
- **Aggregation:** Feature maps from `layer2` and `layer3` are bilinearly aligned to a common spatial grid ($28 \times 28$), smoothed with $3 \times 3$ average pooling (stride 1, padding 1), and concatenated channel-wise:
  $$D_{\text{patch}} = 128 + 256 = \mathbf{384}$$
- **Receptive Field:** Each patch embedding captures an effective spatial context of $\approx 40 \times 40$ pixels on a $224 \times 224$ input image.

### 1.2 Memory Bank & Coreset Optimization
- **Raw Patch Generation:** A single $224 \times 224$ training image yields $28 \times 28 = 784$ patch embeddings. A nominal training set of $N=200$ images yields $\approx 156,800$ vectors.
- **Coreset Reduction:** A greedy iterative facility-location selection algorithm reduces the token population by $\approx 90\%$, maintaining high coverage of the nominal patch manifold while ensuring real-time $k$-NN search.
- **Index Engine:** FAISS (Facebook AI Similarity Search) CPU implementation using `IndexFlatL2`.

---

## 2. Category-Specific Memory Banks & Thresholds

The table below documents the verified model parameters across all 15 MVTec AD categories, loaded from `DefectVisionAI/models/patchcore/category_thresholds.json`:

| Category | Type | Memory Bank File | Disk Size | Stored Tokens | Embedding Dim | Calibrated Threshold ($\tau$) | Baseline Mean ($\mu$) | Baseline P99 |
|---|---|---|---:|---:|---:|---:|---:|---:|
| **bottle** | Object | `bottle/memory_bank.npy` | 22.6 MB | 14,739 | 384 | 1.4666 | 0.9732 | 1.4348 |
| **cable** | Object | `cable/memory_bank.npy` | 24.2 MB | 15,758 | 384 | 2.4577 | 1.7409 | 2.4556 |
| **capsule** | Object | `capsule/memory_bank.npy` | 23.7 MB | 15,444 | 384 | 1.1502 | 0.7614 | 1.1124 |
| **carpet** | Texture | `carpet/memory_bank.npy` | 30.3 MB | 19,756 | 384 | 1.3543 | 0.9690 | 1.2974 |
| **grid** | Texture | `grid/memory_bank.npy` | 28.5 MB | 18,580 | 384 | 1.4634 | 1.0921 | 1.4592 |
| **hazelnut** | Object | `hazelnut/memory_bank.npy` | 42.3 MB | 27,518 | 384 | 2.3403 | 1.2826 | 2.2507 |
| **leather** | Texture | `leather/memory_bank.npy` | 26.5 MB | 17,248 | 384 | 1.1136 | 0.8975 | 1.0973 |
| **metal_nut** | Object | `metal_nut/memory_bank.npy` | 23.8 MB | 15,523 | 384 | 1.8271 | 1.3742 | 1.7745 |
| **pill** | Object | `pill/memory_bank.npy` | 28.9 MB | 18,816 | 384 | 1.7575 | 1.2280 | 1.7478 |
| **screw** | Object | `screw/memory_bank.npy` | 34.7 MB | 22,579 | 384 | 1.4684 | 1.0915 | 1.4636 |
| **tile** | Texture | `tile/memory_bank.npy` | 24.9 MB | 16,228 | 384 | 1.4735 | 1.2218 | 1.4723 |
| **toothbrush** | Object | `toothbrush/memory_bank.npy` | 6.5 MB | 4,233 | 384 | 1.4593 | 1.1695 | 1.4410 |
| **transistor** | Object | `transistor/memory_bank.npy` | 23.0 MB | 14,974 | 384 | 1.7787 | 1.4013 | 1.7582 |
| **wood** | Texture | `wood/memory_bank.npy` | 26.7 MB | 17,404 | 384 | 1.3440 | 1.0621 | 1.3371 |
| **zipper** | Object | `zipper/memory_bank.npy` | 26.0 MB | 16,934 | 384 | 1.1627 | 0.9202 | 1.1625 |

---

## 3. Auxiliary Classifier: EfficientNet-B0 v3

- **Checkpoint File:** `DefectVisionAI/models/efficientnet_baseline_v3/best_model.pt`
- **Architecture:** `timm.create_model("efficientnet_b0", pretrained=False, num_classes=2)`
- **Parameter Count:** $\approx 4.0 \text{ M}$ parameters
- **Input Preprocessing:** Normalization via ImageNet constants ($\mu = [0.485, 0.456, 0.406]$, $\sigma = [0.229, 0.224, 0.225]$).
- **Temperature Scaling Parameter:** $T = 1.3696$ (fitted via negative log-likelihood minimization on nominal holdout sets).

---

## 4. Heatmap Interpolation and Colormapping

When an image is scored by PatchCore, the nearest-neighbour distances $d(p)$ for all $28 \times 28$ patch coordinates form a coarse 2D anomaly map:
1. **Bilinear Upsampling:** Scaled from $28 \times 28$ to the target frame dimension ($224 \times 224$).
2. **Gaussian Smoothing:** Applied with a Gaussian filter kernel ($\sigma = 4.0$) to reduce patch-boundary artifacts.
3. **Min-Max Contrast Scaling:** Scaled dynamically to $[0, 1]$ relative to the calibrated anomaly threshold.
4. **Colormap:** Converted to an OpenCV `cv2.COLORMAP_JET` false-color image and alpha-blended with the original input at $40\%$ opacity.
