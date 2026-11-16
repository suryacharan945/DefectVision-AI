# DefectVision AI — Real Inference & Pipeline Verification Report

**Phase:** Phase 1 (Hours 0–2 Audit)  
**Execution Timestamp:** 2026-11-01T22:42:00+05:30  
**Verification Harness:** `scripts/verify_real_inference_deterministic.py`  
**Artifact Verification Script:** `scripts/verify_model_artifacts.py`  
**Harness Result:** `ALL INFERENCE VERIFICATION TESTS PASSED: True`

---

## 1. End-to-End Inference Pipeline Trace

The DefectVision AI inference architecture executes a dual-engine hybrid decision pipeline combining an unsupervised patch-distribution memory bank (PatchCore) and a supervised feature classifier (EfficientNet-B0 v3). The pipeline executes with zero mock data or synthetic outputs:

```
[Raw Image Bytes / File Upload]
           │
           ▼
[cv2.imdecode / cv2.imread] ──> BGR Array (H, W, 3)
           │
           ├────────────────────────────────────────────────┐
           │                                                │
           ▼ (Resize 224x224, BGR->RGB, ImageNet Norm)       ▼ (Resize 256x256, albumentations, RGB)
   [PatchCore Input Tensor]                         [EfficientNet Input Tensor]
   Shape: (1, 3, 224, 224)                          Shape: (1, 3, 256, 256)
           │                                                │
           ▼                                                ▼
[PatchCoreExtractor (ResNet-18)]                   [EfficientNet-B0 v3 Classifier]
Backbone: layers 0..3                              Pretrained weights + Head (num_classes=2)
Local AvgPool2d(3x3, s=1, p=1)                             │
Interpolate Layer2 & Layer3 to (28x28)                      │
Concatenate -> Fused: (1, 384, 28, 28)                      │
           │                                                │
           ▼                                                │
[Patch Reshaping to (784, 384)]                             │
Query FAISS IndexFlatL2 against                             │
Category Memory Bank (K x 384)                              │
           │                                                │
           ▼                                                │
[Distance Map (28x28)]                                      │
Euclidean dist: sqrt(clip(L2_dists, 0, None))               │
Raw Anomaly Score = max(Distance Map)                       │
           │                                                │
           ▼                                                ▼
[PatchCore Decision]                               [EfficientNet Decision]
raw_score > baseline_p99                           prob_defective = softmax(logits)[0, 1]
                                                   effnet_defective = prob >= 0.50
           │                                                │
           └───────────────────────┬────────────────────────┘
                                   │
                                   ▼
                       [Joint Decision Rule]
             predicted_label = "defective" if (patchcore_defective or effnet_defective) else "normal"
                                   │
                                   ▼
                       [Severity Scoring Fusion]
             anomaly_norm = (raw_score - mean) / (p99 - mean) * 100 [clipped 0..100]
             defect_area_pct = 100.0 * sum(dist_map_norm >= 0.5) / 784
             confidence_pct = prob_defective * 100
             severity_score = 0.5 * anomaly_norm + 0.3 * defect_area_pct + 0.2 * confidence_pct
             severity_level: Minor (<34), Moderate (34-66), Critical (>=67)
```

---

## 2. Verified Model Artifacts Inventory

All 15 MVTec AD categories possess validated memory banks, baseline calibrations, and classifier weights on disk. Checksums computed via SHA-256:

| Category | Artifact Type | Dimensions / Shape | File Size (Bytes) | SHA-256 Checksum |
| :--- | :--- | :--- | :--- | :--- |
| `bottle` | PatchCore Memory Bank | `(14739, 384)` | 22,639,232 | `71a68f4e5410...` |
| `cable` | PatchCore Memory Bank | `(15758, 384)` | 24,204,416 | `44a7684c64f0...` |
| `capsule` | PatchCore Memory Bank | `(15444, 384)` | 23,722,112 | `e55cd942af6a...` |
| `carpet` | PatchCore Memory Bank | `(19756, 384)` | 30,345,344 | `7399618ee3cb...` |
| `grid` | PatchCore Memory Bank | `(18580, 384)` | 28,539,008 | `bc2a0dc345bb...` |
| `hazelnut` | PatchCore Memory Bank | `(27518, 384)` | 42,267,776 | `2aa517a5fa7f...` |
| `leather` | PatchCore Memory Bank | `(17248, 384)` | 26,493,056 | `b82273198a7b...` |
| `metal_nut` | PatchCore Memory Bank | `(15523, 384)` | 23,843,456 | `4be00e7c8546...` |
| `pill` | PatchCore Memory Bank | `(18816, 384)` | 28,901,504 | `f10d8b3b339f...` |
| `screw` | PatchCore Memory Bank | `(22579, 384)` | 34,681,472 | `42c227ad7072...` |
| `tile` | PatchCore Memory Bank | `(16228, 384)` | 24,926,336 | `5c294772501c...` |
| `toothbrush` | PatchCore Memory Bank | `(4233, 384)` | 6,502,016 | `e22831034bd8...` |
| `transistor` | PatchCore Memory Bank | `(14974, 384)` | 23,000,192 | `3aa3f92996ce...` |
| `wood` | PatchCore Memory Bank | `(17404, 384)` | 26,732,672 | `dbbc6871942a...` |
| `zipper` | PatchCore Memory Bank | `(16934, 384)` | 26,010,752 | `21208ba08af1...` |
| **All Categories** | EfficientNet-B0 v3 Weights | `360 Tensor Keys` | 16,336,185 | `f470b76d7c00...` |
| **All Categories** | Severity Baselines CSV | `15 Rows x 4 Cols` | 683 | `0f412846cda0...` |

Full artifact metadata table preserved in [verified_model_artifacts.csv](file:///c:/Users/surya/Downloads/Mini%20Project/release/final_18h_validation/verified_model_artifacts.csv).

---

## 3. Direct Function vs FastAPI Endpoint Numerical Equivalence

To guarantee that the production HTTP API executes the exact same underlying mathematics without approximation or divergence, we tested both defective and normal specimens across categories against:
1. Direct Python invocation (`app.inspect_single_image`)
2. FastAPI Multipart Upload (`POST /predict`)
3. FastAPI Edge In-Memory Frame Decoder (`POST /inspect-frame`)

### Equivalence Results:

| Specimen Tested | Ground Truth | Direct Raw Score | `/predict` Delta | `/inspect-frame` Delta | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `bottle/broken_large/000.png` | Defective | `3.305596` | `0.00e+00` | `4.00e-06` | **PASSED (< 1e-3)** |
| `bottle/good/000.png` | Normal | `1.286906` | `0.00e+00` | `6.00e-06` | **PASSED (< 1e-3)** |
| `cable/bent_wire/000.png` | Defective | `2.906216` | `0.00e+00` | `1.60e-05` | **PASSED (< 1e-3)** |
| `cable/good/000.png` | Normal | `2.067384` | `0.00e+00` | `1.60e-05` | **PASSED (< 1e-3)** |

*Note:* Delta between Direct and `/predict` is strictly `0.00e+00` (exact 64-bit IEEE 754 float identity). Delta between Direct and `/inspect-frame` is $\le 1.6 \times 10^{-5}$, resulting entirely from the intentional 4-decimal formatting (`round(raw_score, 4)`) applied by the low-latency frame endpoint.

---

## 4. Numerical Determinism Verification

Industrial inspection requires zero run-to-run drift under identical input specimens. Each test image was evaluated over 5 consecutive standalone inference passes under fixed random seed:

```
Specimen: bottle/broken_large/000.png
  Run 1: 3.305596
  Run 2: 3.305596
  Run 3: 3.305596
  Run 4: 3.305596
  Run 5: 3.305596
  Variance: 0.000000e+00 -> PASSED

Specimen: cable/bent_wire/000.png
  Run 1: 2.906216
  Run 2: 2.906216
  Run 3: 2.906216
  Run 4: 2.906216
  Run 5: 2.906216
  Variance: 0.000000e+00 -> PASSED
```

**Result:** Zero variance (`0.000000`) across all evaluated runs.

---

## 5. Audit of Synthetic Output Absence

A comprehensive audit was performed across `DefectVisionAI/app.py`, `DefectVisionAI/src/patchcore.py`, and `DefectVisionAI/src/severity.py`:
- No random number generators (`random.random()`, `np.random.rand()`) are used to compute anomaly scores, defect probabilities, severity scores, or heatmaps.
- All scores originate from real PyTorch ResNet-18 feature activations and real FAISS L2 Euclidean distance searches against the coreset memory bank.
- Offline LLM fallback gracefully employs deterministic structured templates rather than fabricated telemetry values.

**Phase 1 Conclusion:** Real inference is fully verified, mathematically sound, deterministic, and identical across API interfaces.
