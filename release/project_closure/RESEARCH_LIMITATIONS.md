# DefectVision AI — Research Limitations and Threats to Validity

**Document Type:** Formal Threats to Validity & Technical Constraints  
**Version:** 1.0.0 (Project Closure Baseline)  
**Date:** 2026-11-01  
**Audited Reference:** `release/final_18h_validation/FINAL_EVIDENCE_AUDIT.md`

---

## 1. Overview

Transparent disclosure of methodological limitations, dataset constraints, and algorithmic boundaries is essential for sound scientific practice and safe industrial deployment. This document catalogs all identified threats to internal validity, external validity, construct validity, and operational feasibility for the DefectVision AI dual-engine system.

---

## 2. Threats to Internal Validity (Dataset & Provenance)

### 2.1 Benchmark Classification: Category C (Development-Exposed)
- **Nature of Limitation:** The primary 856-specimen evaluation set (`benchmark_test_v2.csv`) cannot be characterized as an independent, held-out, or "zero-leakage" benchmark.
- **Evidence of Exposure:**
  1. In the initial project phase (prototype v1), 788 of these images were included in the supervised training pool before clean split stratification was enacted in v3.
  2. The benchmark was accessed iteratively during algorithm development, ablation studies, and baseline comparison experiments in Phases 7B, 7C, 8B, and 8C.
- **Scientific Impact:** Performance metrics (91.94% accuracy, 90.88% recall) may reflect mild in-domain over-fitting and hyperparameter tuning to the idiosyncrasies of this specific sample pool rather than true out-of-sample generalization.

### 2.2 Quarantined External Benchmarks & Zero Cross-Dataset Generalization
- **Nature of Limitation:** To protect the integrity of future research, external industrial benchmarks—specifically the 11 reserved VisA categories, BTAD (BeanTech Anomaly Detection), and Chukyo datasets—were strictly quarantined and never accessed for evaluation.
- **Scientific Impact:** **Zero cross-dataset or cross-facility generalization has been demonstrated.** The system's performance on MVTec AD textures and objects provides no empirical guarantee of performance on different manufacturing domains, different optical geometries, or different surface finishes.

---

## 3. Threats to Construct Validity (Algorithmic & Mathematical)

### 3.1 Sub-Patch Micro-Defect Dilution
- **Algorithmic Mechanism:** PatchCore extracts feature representations from ResNet-18 Layers 2 and 3 via adaptive average pooling. The effective receptive field of these patch embeddings spans approximately $32 \times 32$ to $64 \times 64$ pixels in input space.
- **Failure Mode:** Microscopic defects (e.g., hairline cracks $< 2$ pixels wide, pinprick punctures, or faint surface micro-abrasions) contribute only a tiny fraction of the patch volume. The deep convolutional activations are dominated by surrounding nominal background texture, diluting the defect signal and yielding low nearest-neighbor distance scores ($S < \tau$).
- **Evidence:** 57 defect escapes in the audited benchmark, heavily concentrated in categories with fine structural anomalies (`screw` thread imperfections, `cable` microscopic cuts, `grid` wire thinning).

### 3.2 Cross-Category Baseline Scale Disparities
- **Algorithmic Mechanism:** Raw Euclidean distance in deep feature space is highly sensitive to nominal feature density. Categories with rigid geometry and uniform texture exhibit dense nominal clusters and low nearest-neighbor distances (e.g., `capsule` nominal mean distance $\approx 0.98$). Conversely, complex flexible objects exhibit broad, dispersed nominal clusters (e.g., `cable` nominal mean distance $\approx 2.18$).
- **Failure Mode:** Pooling raw Euclidean distance scores across categories without per-category normalization compresses the global AUROC to 0.8159. A single global distance threshold is mathematically invalid and causes catastrophic failure (either 100% false alarms on `cable` or 0% detection on `capsule`).
- **Required Mitigation:** Every manufacturing category requires distinct baseline calibration parameters ($\mu_0, \sigma_0, \tau_c$) computed from nominal factory samples.

### 3.3 Negative Algorithmic Findings (CPND and MACBA)
- **CPND Abandonment:** The proposed Confidence-Penalized Neighborhood Density (CPND) algorithm failed to show statistically significant separation gains over standard boundary-distance scoring. On subtle surface defects, density penalties actively penalized borderline defects, worsening false negatives.
- **MACBA Equivalence:** Margin-Calibrated Active Budget Allocation (MACBA) was proven mathematically and empirically equivalent to standard cost-weighted ranking (BL6). Under identical cost ratios, both algorithms produce identical sample rankings. The apparent initial superiority was an artifact of disparate probability estimators.

---

## 4. Threats to External & Operational Validity (Hardware & Environment)

### 4.1 Photometric & Environmental Sensitivity
- **Perturbation Testing:** Synthetic stress testing revealed high vulnerability to high-frequency Gaussian noise ($\sigma \ge 0.10$). High-frequency noise alters the local texture distribution, causing ResNet Layer 2 patch vectors to drift outside nominal FAISS clusters, triggering false alarms on unblemished parts.
- **Factory Reality:** Real industrial environments suffer from optical dust, vibration, flicker, and ambient light variation. Without controlled telecentric lighting, enclosed inspection tunnels, and anti-vibration camera mounting, false alarm rates will degrade significantly beyond the measured 5.19%.

### 4.2 False Alarm Penalty and Human Capacity Limits
- **Operational Reality:** The hybrid decision logic ($\hat{y}_{\text{PC}} \lor \hat{y}_{\text{EffNet}}$) incurs a **12-fold increase in false alarms** compared to the supervised classifier (FPR rising from 0.43% to 5.19%).
- **Economic Consequence:** In a plant producing 10,000 parts per day, 519 nominal parts would be erroneously flagged daily. If human reviewers are assigned to verify flagged specimens, this false alarm volume risks overwhelming review staff, causing review fatigue, bottlenecking lines, or inducing accidental approval of true defects.

### 4.3 Runtime Throughput on CPU vs High-Speed Conveyors
- **Measured Latency:** Multi-core CPU median API round-trip is **881.7 ms** (p95: **1455.7 ms**), corresponding to **~1.13 frames per second**.
- **Conveyor Incompatibility:** Typical manufacturing lines operate at speeds between 5 and 30 parts per second (33–200 ms per part). Deploying this system on CPU hardware for inline gating would cause immediate line blockage. Real-time conveyor deployment strictly requires dedicated GPU hardware acceleration (e.g., NVIDIA Jetson / RTX with TensorRT optimization).

---

## 5. Summary Matrix of Limitations & Mitigations

| Identified Threat / Limitation | Severity | Current Status | Required Industrial Mitigation |
| :--- | :---: | :---: | :--- |
| **Development-Exposed Benchmark** | Moderate | Audited & Disclosed | Conduct independent on-site shadow validation before line commissioning. |
| **Quarantined External Benchmarks** | High | Maintained | Zero cross-facility claims; calibrate models per specific factory line. |
| **Sub-Patch Micro-Defects** | High | Algorithmic Limit | Complement with high-magnification optical zoom or multi-resolution backbones. |
| **Cross-Category Scale Shift** | Critical | Mitigated in Code | Enforce mandatory 50-specimen nominal baseline calibration per SKU. |
| **Photometric Noise Vulnerability** | High | Empirical Finding | Mandate sealed telecentric lighting and polarized illumination enclosures. |
| **5.19% False Alarm Rate** | High | Audited Trade-off | Deploy only in supervised shadow mode with dedicated human review queues. |
| **CPU Latency (~880 ms)** | Critical | Hardware Bound | Restrict CPU to slow/indexing lines ($>1.5$ s/part) or deploy GPU / TensorRT. |
