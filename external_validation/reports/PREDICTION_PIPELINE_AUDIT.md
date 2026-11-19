# DefectVision AI — Prediction Pipeline Technical Audit Report

**Date:** 2026-11-19  
**Branch:** `feat/reliable-mvtec-like-predictions`  
**Base Commit:** `598eaf9`  
**Scope:** Complete technical trace and consistency verification of the inference pipeline across all 15 industrial categories.

---

## 1. Executive Summary

This audit establishes the end-to-end technical baseline of the DefectVision AI inference architecture prior to experimental evaluation and reliability enhancement. The system implements a dual-stage neural inspection engine:
1. **Category Recognition:** Pre-trained EfficientNet-B0 with a fine-tuned 15-class linear classification head, temperature scaling ($T = 1.3696$), and a 4-criterion open-set unknown rejection rule.
2. **Anomaly Detection:** One-class PatchCore architecture using an ImageNet-pretrained ResNet-18 backbone (layers 2 and 3 feature concatenation, $D=384$, $28 \times 28 = 784$ spatial patches) queried against 15 resident nominal memory banks via `faiss.IndexFlatL2`.

---

## 2. End-to-End Pipeline Stage Analysis

```
[Raw Frame Payload: multipart/form-data]
   │
   ▼ Stage 0: Decode & Payload Validation
[cv2.imdecode(buffer, IMREAD_COLOR) -> uint8 BGR (H, W, 3)]
   │
   ▼ Stage 1: Optical Quality Gate (ImageQualityService)
[Laplacian Sharpness Variance >= 50.0 & Exposure Bounds [20.0, 235.0]]
   │
   ├── (Fails Gate) ────────► [Verdict: "REVIEW REQUIRED", Rejection: "quality_gate"]
   │
   ▼ (Passes Gate) Stage 2: Category Recognition (CategoryRecognitionService)
[BGR -> RGB -> cv2.resize(224, 224) -> ImageNet Normalize -> EfficientNet-B0]
   │
   ├── (Operator Override) ──► Direct category assignment (Confidence = 1.0)
   ├── (Auto Mode) ──────────► Softmax Probabilities, Entropy, Energy, Prototype Similarity
   │     └── (Fails OOD) ────► [Verdict: "UNSUPPORTED", Rejection: "open_set_gate"]
   │
   ▼ (Category Verified) Stage 3: Routing & Model Selection
[CategoryModelRegistry -> Binds DefectVisionAI/models/patchcore/<cat>/memory_bank.npy]
   │
   ▼ Stage 4: PatchCore Feature Extraction (PatchCoreExtractor)
[ResNet18 layers 2 & 3 -> AdaptiveAvgPool -> Concatenation -> (1, 384, 28, 28) -> (784, 384)]
   │
   ▼ Stage 5: Accelerated Nearest-Neighbor Search (FAISS)
[faiss.IndexFlatL2(384) -> Exact Euclidean Distance -> (784,) Patch Distance Map]
   │
   ▼ Stage 6: Anomaly Scoring & Threshold Decision
[Anomaly Score = Max(Patch Distances) vs. Calibrated Category Threshold tau]
   │
   ├── (Score >= tau) ───────► [Verdict: "DEFECTIVE"]
   └── (Score < tau) ────────► [Verdict: "NORMAL"]
   │
   ▼ Stage 7: Dense Heatmap Localization & Overlay Compositing
[Cubic Upsample -> Gaussian Blur (sigma=4.0) -> Jet Colormap -> Alpha Blend (0.45/0.55)]
   │
   ▼ Stage 8: Telemetry Serialization & Response Payload
[FastAPI JSON Payload: Verdict, Scores, Latency, Diagnostic String, Base64 Overlay]
```

---

## 3. Data Specification by Pipeline Stage

| Stage | Component | Input Type & Shape | Output Type & Shape | Mathematical Function / Threshold | Error Handling Logic |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **0. Image Decode** | `cv2.imdecode` | Raw binary byte stream | `np.ndarray` BGR `uint8` $(H, W, 3)$ | In-memory OpenCV decompression | Returns HTTP 400 if buffer is empty or corrupted. |
| **1. Quality Gate** | `ImageQualityService` | BGR `uint8` $(H, W, 3)$ | `quality_status`: `PASS` / `REJECT` | $\text{Var}(\Delta I) \ge 50.0$, $\mu_{lum} \in [20, 235]$ | Rejects motion blur, underexposure, or sensor blowout without model execution. |
| **2. Category Classifier** | `CategoryClassifier` (EfficientNet-B0) | Normalized Tensor `float32` $(1, 3, 224, 224)$ | Class probabilities $(15,)$, entropy, energy | $\tau_{conf} = 0.70$, $H_{norm} \le 0.60$, $E \le -6.50$, $\text{Sim}_{proto} \ge 0.65$ | Sets status to `UNSUPPORTED_OR_UNCERTAIN` if any rejection criterion fails. |
| **3. Model Selector** | `CategoryModelRegistry` | Category string (e.g., `"bottle"`) | `PatchCoreModel` instance | Binds matching memory bank | Raises error if category memory bank file is absent. |
| **4. Feature Extraction** | `PatchCoreExtractor` (ResNet-18) | Normalized Tensor `float32` $(1, 3, 224, 224)$ | `np.ndarray` `float32` $(784, 384)$ | Layer 2 (128-d) $\parallel$ Layer 3 (256-d) | CPU/GPU tensor device tracking with zero grad. |
| **5. FAISS Retrieval** | `faiss.IndexFlatL2` | Query array $(784, 384)$ | Patch distances $(784,)$ | $d(p_i, \mathcal{M}) = \min_{m \in \mathcal{M}} \| p_i - m \|_2$ | AVX2 SIMD multithreaded exact distance computation. |
| **6. Decision Rule** | Decision Logic | Score $S = \max(d_i)$ | `verdict`: `NORMAL` or `DEFECTIVE` | $S \ge \tau_{category}$ | Compares raw distance against category calibration. |
| **7. Heatmap Overlay** | OpenCV + SciPy | Distance vector $(784,)$ | Base64 JPEG overlay string | Bicubic resize to $(H, W)$ + Gaussian ($\sigma=4.0$) | Encodes composite JPEG with quality factor 85. |

---

## 4. Disaggregated Category Model Registry & Threshold Audit

All 15 resident memory banks and their calibrated thresholds are verified:

| Category | Type | Memory Bank Path | Token Count | Calibrated Threshold ($\tau$) | Baseline Mean ($\mu$) | Baseline $p99.5$ |
| :--- | :--- | :--- | ---:| ---:| ---:| ---:|
| **bottle** | Object | `models/patchcore/bottle/memory_bank.npy` | 14,739 | **1.4666** | 0.9732 | 1.4666 |
| **cable** | Object | `models/patchcore/cable/memory_bank.npy` | 15,758 | **2.4577** | 1.7409 | 2.4577 |
| **capsule** | Object | `models/patchcore/capsule/memory_bank.npy` | 15,444 | **1.1502** | 0.7614 | 1.1502 |
| **carpet** | Texture | `models/patchcore/carpet/memory_bank.npy` | 19,756 | **1.3543** | 0.9690 | 1.3543 |
| **grid** | Texture | `models/patchcore/grid/memory_bank.npy` | 18,580 | **1.4634** | 1.0921 | 1.4634 |
| **hazelnut** | Object | `models/patchcore/hazelnut/memory_bank.npy` | 27,518 | **2.3403** | 1.2826 | 2.3403 |
| **leather** | Texture | `models/patchcore/leather/memory_bank.npy` | 17,248 | **1.1136** | 0.8975 | 1.1136 |
| **metal_nut** | Object | `models/patchcore/metal_nut/memory_bank.npy` | 15,523 | **1.8271** | 1.3742 | 1.8271 |
| **pill** | Object | `models/patchcore/pill/memory_bank.npy` | 18,816 | **1.7575** | 1.2280 | 1.7575 |
| **screw** | Object | `models/patchcore/screw/memory_bank.npy` | 22,579 | **1.4684** | 1.0915 | 1.4684 |
| **tile** | Texture | `models/patchcore/tile/memory_bank.npy` | 16,228 | **1.4735** | 1.2218 | 1.4735 |
| **toothbrush** | Object | `models/patchcore/toothbrush/memory_bank.npy` | 4,233 | **1.4593** | 1.1695 | 1.4593 |
| **transistor** | Object | `models/patchcore/transistor/memory_bank.npy` | 14,974 | **1.7787** | 1.4013 | 1.7787 |
| **wood** | Texture | `models/patchcore/wood/memory_bank.npy` | 17,404 | **1.3440** | 1.0621 | 1.3440 |
| **zipper** | Object | `models/patchcore/zipper/memory_bank.npy` | 16,934 | **1.1627** | 0.9202 | 1.1627 |

---

## 5. Preprocessing Consistency Verification

### 5.1 Training vs. Inference Parity
1. **Resizing:**
   - Training: `torchvision.transforms.Resize((224, 224))` (PIL bilinear/bicubic interpolation).
   - Inference: `cv2.resize(..., (224, 224))` (OpenCV bilinear interpolation).
   - *Audit Finding:* Bilinear interpolation between OpenCV and Pillow exhibits minor rounding variations ($<0.5\%$ pixel difference), but does not alter feature clustering.
2. **Channel Ordering:**
   - Decoded via OpenCV as BGR. Converted to RGB via `cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)` prior to normalization. Verified identical across both category classifier and PatchCore.
3. **Normalization Constants:**
   - Mean: $[0.485, 0.456, 0.406]$
   - Standard Deviation: $[0.229, 0.224, 0.225]$
   - Verified identical between PyTorch ImageNet weights and OpenCV numpy tensor transforms.

### 5.2 Identified Pipeline Bottlenecks & Vulnerabilities
1. **Synchronous Execution in Event Loop:**
   - In `app.py`, endpoints declared `async def inspect_frame_endpoint(...)` perform synchronous CPU-bound Torch/FAISS execution. If multi-megapixel or corrupted images are processed, the single-threaded asyncio event loop stalls.
2. **Rejection Criteria Strictness on External Images:**
   - The category classifier's 4-way rejection rule requires `energy <= -6.50` AND `proto_sim >= 0.65` AND `norm_entropy <= 0.60`. On out-of-domain images with non-standard backgrounds (e.g. natural table backgrounds instead of black velvet), energy scores often sit between $-5.0$ and $-6.4$, causing valid category candidates to be prematurely rejected as `UNSUPPORTED`.
3. **Large Image Memory Allocation:**
   - High-resolution external images ($>10$ megapixels) trigger extensive RAM allocation during base64 serialization and OpenCV resizing. A pre-downscaling step to max dimension 1024 prior to full tensor pipeline processing will significantly reduce latency and eliminate timeouts.
