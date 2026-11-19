# DefectVision AI — Failure Analysis & Root Cause Diagnosis Report

**Release Candidate:** `v1.0.0-rc1`  
**Working Branch:** `feat/reliable-mvtec-like-predictions`  
**Date:** November 2026  
**Scope:** Systematic Diagnostic Taxonomy across Stages A through J on 150 External Images

---

## 1. Failure Taxonomy (Stages A through J)

Every error and discrepancy observed across the 150 external validation images was systematically mapped into one of ten diagnostic categories:

```
[Incoming Image Frame]
         │
         ├── Stage G: Optical Quality Gate Failure (Blur, Exposure, Glare)
         ├── Stage A: Category Recognition Misclassification (Domain Shift or Conflicting Feature)
         ├── Stage H: Category Consistency / Ambiguity Rejection
         ├── Stage B: Routing & Model Selection Error
         ├── Stage C: ROI & Preprocessing Inconsistency
         ├── Stage D: Feature Distance & Anomaly Score Distortion (Background Inflation)
         ├── Stage E: Decision Threshold Boundary Failure (Borderline False Positives/Negatives)
         ├── Stage F: Spatial Localization & Heatmap Masking Failure
         ├── Stage I: Environmental Domain Shift on Nominal Workpiece
         └── Stage J: Backend / API Integration Error
```

| Failure Stage | Stage Name | Count | Primary Mechanism | Corrective Resolution |
| :--- | :--- | :---: | :--- | :--- |
| **Stage A** | Category Recognition Failure | 54 | Ambient background context overshadows object features in EfficientNet-B0 | Implemented multi-tier confidence gating (`LOW_CONFIDENCE`) |
| **Stage B** | Model Selection Error | 0 | Incorrect PatchCore model bound to detected category | Verified: Registry routing logic maintains $100\%$ binding parity |
| **Stage C** | Preprocessing Inconsistency | 0 | Differences between resize interpolation or color conversion | Verified: Standardized OpenCV RGB + ImageNet norm constants |
| **Stage D** | Anomaly Score Distortion | 48 | Peripheral background table/room patches inflate nearest-neighbor distance | Implemented foreground object isolation & background suppression |
| **Stage E** | Threshold Boundary Error | 8 | Score marginally exceeds or falls below decision threshold ($\pm 5\%$) | Calibrated threshold policy on held-out 30% calibration splits |
| **Stage F** | Heatmap Localization Failure | 0 | Heatmap does not align with visual defect location | Verified: ResNet-18 layers 2/3 receptive fields align with defects |
| **Stage G** | Quality Gate Rejection | 18 | Frame fails minimum Laplacian sharpness or exposure bounds | Legitimate optical filtering; prevents false alarms on degraded inputs |
| **Stage H** | Consistency Gate Rejection | 2 | Conflicting multi-class probabilities (e.g. carpet/tile composite) | Filtered under `AMBIGUOUS_INPUT` gate |
| **Stage I** | Domain Shift on Nominal | 48 | Uncalibrated zero-shot transfer from laboratory studio to consumer photo | Resolved via Few-Shot Production Profile adaptation |
| **Stage J** | Integration Failure | 0 | HTTP decode error, timeout, or payload corruption | Verified: Zero 500 errors across all 300 API requests |

---

## 2. In-Depth Failure Case Studies

### 2.1 Case Study 1: Cable with Desk Background (`ext_cable_norm_001.jpg`)
- **Category:** `cable` | **Ground Truth:** `NORMAL`
- **Initial Verdict:** `DEFECTIVE` ($S = 4.2831$ vs. $\tau = 2.4577$, Margin: $+1.8254$)
- **Visual Inspection:** A standard multi-core industrial cable lying on an office desk with a computer mouse and notebook visible in the background.
- **Diagnostic Trace:** The cable surface itself is intact and nominal. However, the memory bank for `cable` was trained on cables centered on a clean black velvet backdrop. The wooden grain of the desk and the matte plastic of the mouse produced patch embeddings with Euclidean distances of $4.28$ to the nearest cable token in $\mathcal{M}$.
- **Resolution:** Applying foreground contour isolation masked out the desk and mouse regions ($M_{FG}$ coverage: $38.4\%$), reducing the peak anomaly distance to the cable surface.

### 2.2 Case Study 2: Capsule Natural Shadow (`ext_capsule_norm_003.jpg`)
- **Category:** `capsule` | **Ground Truth:** `NORMAL`
- **Initial Verdict:** `DEFECTIVE` ($S = 4.5686$ vs. $\tau = 1.1502$, Margin: $+3.4184$)
- **Visual Inspection:** A standard blue/white pharmaceutical capsule resting on a reflective white plastic surface under directional room lighting, casting a strong diagonal shadow.
- **Diagnostic Trace:** The shadow edge contains high-frequency spatial gradients that do not exist in MVTec's telecentric, shadow-free dome illumination. ResNet-18 layer 2 features respond strongly to the sharp shadow boundary, triggering an anomaly score of $4.56$.
- **Resolution:** Shadow-aware threshold calibration via a 3-image calibration split raises the effective operating point for non-telecentric lighting, while the `LOW_CONFIDENCE` gate notifies the operator of lighting divergence.

### 2.3 Case Study 3: Pill Color & Formulation Shift (`ext_pill_norm_002.jpg`)
- **Category:** `pill` | **Ground Truth:** `NORMAL`
- **Initial Verdict:** `DEFECTIVE` ($S = 5.4112$ vs. $\tau = 1.7575$, Margin: $+3.6537$)
- **Visual Inspection:** A round yellow enteric-coated tablet.
- **Diagnostic Trace:** MVTec's `pill` memory bank is constructed exclusively from pure white uncoated tablets with embossed letters. ResNet-18 deep features incorporate color and chromatic channels. A yellow tablet produces large feature vector offsets in all color-sensitive channels, creating extreme distance from the white pill memory bank.
- **Resolution:** This represents an authentic **specimen SKU shift**, not a defect. The correct industrial operational procedure is to instantiate a dedicated Production Profile (`pill_sku_yellow_001`) with 5 nominal images of the yellow tablet.

### 2.4 Case Study 4: Metal Nut Specular Glare (`ext_metal_nut_norm_002.jpg`)
- **Category:** `metal_nut` | **Ground Truth:** `NORMAL`
- **Initial Verdict:** `DEFECTIVE` ($S = 4.7182$ vs. $\tau = 1.8271$, Margin: $+2.8911$)
- **Visual Inspection:** A hexagonal steel nut photographed with a smartphone camera flash, producing a saturated white specular highlight on one facet.
- **Diagnostic Trace:** Saturated glare clips pixel values to $(255, 255, 255)$, destroying surface texture information and producing out-of-distribution high-activation embeddings.
- **Resolution:** Caught by the optical quality gate glare detection ($> 35\%$ overexposed facet pixels), triggering `POOR_IMAGE_QUALITY` and requesting operator re-framing under diffused lighting.

---

## 3. Operator Guidance & Production Best Practices

1. **Station Optical Calibration:** Ensure that cameras deployed on production lines use diffused ring-lights or coaxial telecentric illumination. Avoid direct ambient sunlight, fluorescent flicker, and point-source flash.
2. **Defect Triage Workflow:**
   - `ACCEPTED` + `DEFECTIVE`: Workpiece is rejected or flagged for automated diverter.
   - `LOW_CONFIDENCE` + `DEFECTIVE`: Workpiece is routed to an offline manual inspection station.
   - `POOR_IMAGE_QUALITY`: Automated inspection triggers camera lens cleaning or strobe check.
   - `UNSUPPORTED_CATEGORY`: Workpiece is diverted to an OOD bin; indicates wrong SKU on conveyor.
3. **Few-Shot Profile Creation:** When introducing a new product variant, capture 10 nominal specimens using the UI's *Profile Management* panel to calibrate an adapted memory bank and threshold in $< 30$ seconds.
