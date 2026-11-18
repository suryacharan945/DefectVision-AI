# DEFECTVISION AI 2.2 — SCIENTIFIC CLAIMS & POSITIONING AUDIT

**Document Identifier:** `release/audits/DEFECTVISION_2_2_CLAIMS_AUDIT.md`  
**Author:** Software Release Auditor & Scientific Integrity Reviewer  
**Audited Baseline:** DefectVision AI 2.2 (Commit `73a06a6` + 2.2 Reassessment)  

---

## 1. Executive Positioning Statement

### Permitted Official Positioning:
> **"DefectVision AI is a benchmark-evaluated industrial anomaly-detection research prototype with experimental few-shot product adaptation and domain-aware image intake."**

### Prohibited Overstatements:
- ❌ *"Universally reliable anomaly detection across any manufacturing environment."*
- ❌ *"Factory-proven 100% precision and recall on physical production lines."*
- ❌ *"Near-perfect defect localization across all defect types."*
- ❌ *"Zero false alarms guaranteed by statistical calibration."*

---

## 2. Comprehensive Claims Classification Matrix

| Domain / Claim Area | Specific Claim | Empirical Supporting Evidence | Evidence Limitations | Permitted Technical Wording |
|:---|:---|:---|:---|:---|
| **1. MVTec AD Benchmark Performance** | Achieves high anomaly detection accuracy across 15 standard industrial categories. | Tested across all 15 MVTec AD object and texture categories. Resident PatchCore models achieve $>0.98$ AUROC on standard test splits. | MVTec AD is a clean, curated benchmark with uniform lighting, centered objects, and zero background clutter. | *"Achieves high benchmark AUROC ($>0.98$) on standardized MVTec AD laboratory datasets under controlled lighting."* |
| **2. External Studio Bottle Feasibility** | Baseline MVTec fails on studio bottles; adapted memory bank accommodates studio background. | Baseline PatchCore scored $4.78$ and $5.15$ on nominal studio bottles (100% false alarms). Adapted bank reduced nominal scores to $1.39$ and $1.38$. | Evaluated on only $N=3$ physical specimens. The 2 nominal test bottles were included in the training set of the adapted profile. | *"Provides exploratory feasibility proof that few-shot centroid adaptation prevents baseline distance blowup under studio lighting."* |
| **3. Few-Shot Product Adaptation** | $K=5$ normal reference images are sufficient to construct an operational memory bank. | Systematic scaling experiment across $K \in \{1, 3, 5, 10, 20\}$ on 83 genuine test specimens showed AUROC plateaus at $K=5$ ($0.9937$). | Evaluated using MVTec test specimens. Performance on novel unconstrained geometries or varying optical angles remains unproven. | *"Demonstrates high sample efficiency on uniform objects, reaching near-optimal AUROC with $K \ge 5$ normal reference frames."* |
| **4. Synthetic Station Robustness** | Station 01 profile tolerates spatial and brightness conveyor jitter. | 48 synthetic jitter frames evaluated across nominal and broken seeds; 100% accuracy on strictly held-out jitter splits. | All 48 images derive algorithmically from only 2 physical specimens. Does not prove generalization to physical conveyor belts. | *"Demonstrates algorithmic tolerance to mathematical affine jitter ($[-3^\circ, 3^\circ]$) and sensor noise on synthetic benchmark rigs."* |
| **5. Universal Image Intake** | Preprocessing diagnostics classify domains and detect foreground boundaries. | Unit tests and API endpoints correctly detect bounding boxes and flag unsuitable blank or blurred frames. | Best-effort triage routing cannot guarantee zero false positives when presented with uncalibrated external cameras. | *"Features domain-aware image intake that performs automated optical quality gating and foreground extraction prior to inference."* |
| **6. Out-of-Distribution (OOD) Rejection** | Rejects non-industrial objects (e.g., ceiling fans, noise) without running PatchCore. | 15/15 synthetic noise and OOD specimens halted at category gate as `UNSUPPORTED OR UNKNOWN CATEGORY` ($100\%$ rejection). | Tested on extreme OOD images. Borderline objects resembling supported classes with confidence near 70% may require manual review. | *"Safely halts inspection on out-of-distribution or unrecognized objects when category confidence falls below 70%."* |
| **7. Defect Localization & Explainability** | Generates pixel-level heatmaps highlighting anomaly locations. | High Pixel AUROC ($>0.99$) on large fractures, punctures, and contaminations on bottle and cable specimens. | **The Localization Paradox:** High AUROC does not guarantee operational IoU. On Pill Color, Pixel AUROC is $0.9992$ while IoU is $0.0000$ due to threshold cutoff. Small cracks suffer from spatial diffusion ($28 \times 28$ grid). | *"Produces spatial heatmaps that indicate relative anomaly intensity; fine micro-cracks and color shifts exhibit spatial diffusion or threshold clipping."* |
| **8. Real Factory Validation** | System is ready for direct deployment on operational factory lines. | None. No operational telemetry, multi-shift drift data, or physical PLC integration exists. | The system has never run on a live, continuous production line with moving conveyors, vibration, and thermal drift. | **PROHIBITED.** Must state: *"Prototype system evaluated under laboratory and simulated conditions; requires physical on-site pilot calibration prior to production deployment."* |

---

## 3. Disclosed Limitations & Boundary Conditions

1. **Physical Sample Scarcity in Domain B:**
   The repository currently contains only 3 physical external studio specimens. Independent in-domain generalization cannot be certified without completing the proposed 55-specimen data collection protocol.
2. **Semantic Invariance to Color:**
   ImageNet-pretrained ResNet18 layers 2+3 suppress pure chromatic shifts, resulting in missed defects on color alterations (Pill Case 1).
3. **Threshold Calibration Power:**
   Provisional thresholds calibrated on $N \le 5$ frames carry wide statistical confidence intervals ($[1.93, 3.05]$) and cannot guarantee false alarm rates below $1\%$.
4. **Destructive Nature of Optical Enhancers:**
   CLAHE contrast enhancement amplifies sensor noise, causing a $100\%$ false positive rate on target camera frames.
