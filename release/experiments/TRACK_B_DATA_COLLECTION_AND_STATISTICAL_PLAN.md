# DEFECTVISION AI 2.4 — TRACK B DATA COLLECTION & STATISTICAL PLAN

**Document Identifier:** `release/experiments/TRACK_B_DATA_COLLECTION_AND_STATISTICAL_PLAN.md`  
**Track Status:** `BLOCKED — DATA REQUIRED`  
**Governing Standard:** Industrial AI Verification (ISO/IEC 25059 / Good Machine Learning Practice)  
**Related Requirements:** [EXTERNAL_DOMAIN_DATA_REQUIREMENTS.csv](file:///c:/Users/surya/Downloads/Mini%20Project/release/experiments/EXTERNAL_DOMAIN_DATA_REQUIREMENTS.csv)  

---

## 1. Executive Status & Scientific Boundary

Track B evaluates **external-domain factory adaptation** (transfer from laboratory benchmark settings to operational manufacturing conveyor lines).

As established in Sprints 2.2 through 2.4, **Track B remains formally BLOCKED**.
Existing external assets (Station 01 and Domain B Studio) consist of only 2–3 physical specimens captured across synthetic variations or studio setups. Claiming factory adaptation from studio photographs is scientifically invalid.

This document defines the formal physical acquisition protocol and statistical sizing required to unblock Track B.

---

## 2. Standardized Physical Acquisition Protocol

Every physical capture submitted to Track B must be tagged with the 12-parameter metadata schema:

| Schema Field | Parameter Name | Technical Specification / Standard | Example Value |
|:---|:---|:---|:---|
| **01** | `specimen_id` | Globally unique hardware unit serial number | `FACT-BTL-2026-UNIT-042` |
| **02** | `ground_truth` | Binary label (`normal` or `defective`) | `defective` |
| **03** | `defect_type` | Standardized defect morphology category | `mouth_chipped` |
| **04** | `session_id` | Acquisition date, time, and factory shift identifier | `SESS-20261120-SHIFT-A` |
| **05** | `camera_model` | Industrial machine vision sensor & interface | `Basler ace2 Basic (Sony IMX546, 8.1MP)` |
| **06** | `lens_focal` | Optical focal length, aperture, and mount | `Kowa 16mm C-Mount Lens, f/4.0 fixed` |
| **07** | `lighting_condition`| Illumination hardware and calibrated lux level | `CCS White LED Diffuse Ring Light, 420 lux` |
| **08** | `exposure_settings`| Sensor exposure time, gain, and white balance | `Exposure: 2,000 µs, Gain: 0 dB, Manual WB` |
| **09** | `viewpoint_pose` | Standoff distance and rotational orientation | `Standoff: 22.0 cm, In-plane angle: +12°` |
| **10** | `product_batch` | Raw material batch and manufacturing run ID | `LOT-GLS-2026-NOV-B04` |
| **11** | `annotation_mask` | 1-bit pixel-level binary ground truth mask path | `masks/FACT-BTL-2026-UNIT-042_mask.png` |
| **12** | `dataset_partition`| Strict four-way split designation | `held_out_test` |

---

## 3. Four-Way Dataset Partitioning Plan

To prevent the evaluation leakage documented in Sprint 2.3, physical specimens must be strictly assigned to non-overlapping partitions:

| Partition Role | Minimum Unique Physical Units | Allocation Ratio | Permitted Usage | Leakage Rule |
|:---|:---:|:---:|:---|:---|
| **Training Reference Bank** | 30 Normal Units | 30% | Populate few-shot coreset memory banks. | Zero defect exposure. |
| **Threshold Calibration Pool**| 20 Normal Units | 20% | Estimate statistical baseline distribution and noise scale. | Zero bank fitting exposure. |
| **Validation Tuning Set** | 20 Normals + 20 Defects | 20% | Tune feature weights ($\lambda$), evaluate fusion rules, select operating cutoffs. | Isolated from test set. |
| **Held-Out Final Test Set** | **30 Normals + 30 Defects** | 30% | **Single-pass final release evaluation under frozen parameters.** | **Zero parameter updates.** |
| **Total Inventory Required** | **150 Unique Physical Units** | 100% | Full Track B Factory Acceptance Testing | Cryptographically verified |

---

## 4. Statistical Limitations of the 30/20/30 Plan & High-Speed Sizing

### 4.1 Statistical Resolution of $N=30$ Test Normals
A held-out test set of $N=30$ normal specimens provides a discrete measurement resolution of:
$$\Delta p = \frac{1}{30} = 3.33\%$$
Even if **zero false positives** are observed across all 30 specimens ($0 / 30$), the exact Clopper-Pearson 95% confidence interval is:
$$\text{FPR}_{95\%} \in [0.0\%, 9.5\%]$$
By the Rule-of-Three, $3/30 = 10.0\%$. Therefore, a 30-sample test set **cannot validate an FPR below 5% or 1%**. It can only prove that the false alarm rate is below $\sim 10\%$.

### 4.2 Required Sizing for Industrial $<1\%$ False Alarm Guarantees
If customer service level agreements (SLAs) or production requirements demand a statistically proven false alarm rate below $1.0\%$ at $95\%$ confidence:
$$N_{\text{normal}} \ge \frac{3}{\text{FPR}_{\text{target}}} = \frac{3}{0.01} = \mathbf{300\text{ unique physical normal units}}$$

### 4.3 Conclusion
- The initial 150-specimen collection plan unblocks Track B for **feasibility and development gating**.
- **Production release sign-off** requires a supplemental run of $\ge 300$ continuous in-line factory specimens.
