# DEFECTVISION AI 2.2 — NEXT RESEARCH SPRINT SPECIFICATION

## Research Agenda: Advancing Few-Shot Industrial Adaptation & Anomaly Localization

**Document Identifier:** `release/experiments/NEXT_RESEARCH_SPRINT.md`  
**Author:** Industrial Computer Vision Research & MLOps Engineering Team  
**Baseline Evaluated:** DefectVision AI 2.1 (Commit `0668bb5` + Audit Corrections)  
**Target Milestone:** DefectVision AI 2.2 Research Architecture  

---

## 1. Executive Summary & Research Motivation

The DefectVision AI 2.1 scientific audit demonstrated that few-shot memory bank adaptation provides genuine, quantifiable benefits when transitioning from benchmark datasets (MVTec AD) to target imaging domains (e.g., Domain B External Studio Bottles, where Baseline MVTec exhibited a 100% False Positive Rate, while adapted profile `bottle_sku_btl_adapt_002` achieved 100% precision, recall, and F1).

However, the audit also identified critical architectural boundaries and failure modes in the current PatchCore implementation:
1. **Semantic Invariance Over-Suppression (The Pill Color Failure):** Deep layers of ImageNet-pretrained ResNet18 (layers 2 and 3) exhibit rotational, illumination, and color invariance. A contaminated/color-altered pill achieved a PatchCore distance of 1.6973 vs. threshold 1.7575 (under by 0.0602), failing image-level detection despite near-perfect pixel localization (AUROC 0.9998).
2. **Small-Sample Calibration Variance ($N=2$ to $N=5$):** Under $N=2$ calibration images, bootstrap 95% confidence intervals on threshold percentiles span $[1.9315, 3.0528]$, creating severe risk of either false alarms or missed defects in production.
3. **High-Frequency Preprocessing Disruption:** Optical enhancement via CLAHE resulted in a 100% False Positive Rate by amplifying background camera sensor noise into the ResNet receptive field.
4. **Logical & Structural Anomaly Inability:** PatchCore relies strictly on local patch embeddings and cannot detect global count, ordering, or structural relationship defects (e.g., missing pill in blister pack, wrong component sequence).

DefectVision AI 2.2 is formulated to address these fundamental challenges through six targeted research workstreams.

---

## 2. Research Workstreams for DefectVision AI 2.2

### Workstream 1: Dual-Branch Vision Foundation Models for Color & Texture Preservation (Solving Case 1)

#### Hypothesis
Augmenting ResNet18 with a frozen self-supervised foundation model (DINOv2-small or SigLIP) sensitive to fine-grained photometric and surface color representations will prevent color-only anomalies from being masked by semantic invariance.

#### Proposed Architecture
- **Primary Spatial Branch:** ResNet18 (Layers 2 & 3), capturing $28 \times 28$ patch embeddings with spatial structure.
- **Photometric / Color-Sensitive Branch:** DINOv2 (`dinov2_vits14`), extracting patch tokens at layer 9 (before high-level abstraction).
- **Cross-Attention Fusion:** Fuse spatial and photometric feature vectors via projection layer or weighted concatenation:
  $$z_{\text{fused}} = \left[ \alpha \cdot \frac{z_{\text{ResNet}}}{\|z_{\text{ResNet}}\|_2} \;\|\; (1-\alpha) \cdot \frac{z_{\text{DINO}}}{\|z_{\text{DINO}}\|_2} \right]$$
- **Expected Outcome:** Resolves the Pill Color FN (Case 1) by elevating the anomaly distance above the nominal threshold without retraining the underlying backbone.

---

### Workstream 2: Multi-Scale PatchCore Memory Banks (Hierarchical Receptive Fields)

#### Hypothesis
Concatenating Layer 2 ($56 \times 56$) and Layer 3 ($28 \times 28$) into a single memory bank enforces a uniform spatial resolution via bi-linear interpolation, which dilutes high-resolution boundary anomalies (e.g., small cracks). Maintaining decoupled hierarchical memory banks will improve Small-Defect IoU.

#### Proposed Architecture
- **Scale 1 (Micro-Defect Bank):** Layer 2 features ($D=128$, spatial grid $56 \times 56$). Sensitive to fine cracks, micro-punctures, and hair contaminants.
- **Scale 2 (Macro-Defect Bank):** Layer 3 features ($D=256$, spatial grid $28 \times 28$). Sensitive to structural deformities, missing caps, and massive breaks.
- **Decoupled Scoring:**
  $$s_{\text{hierarchical}} = \max \left( w_1 \cdot s_{\text{scale1}}, \; w_2 \cdot s_{\text{scale2}} \right)$$
- **Expected Outcome:** Improves IoU on `broken_small` defects from 0.1422 to $>0.45$ by preventing fine-scale spatial averaging.

---

### Workstream 3: Extreme Value Theory (EVT) for Few-Shot Threshold Calibration

#### Hypothesis
Empirical percentile estimation ($P_{99}$ or $P_{95}$) is mathematically unstable when sample size $N < 20$. Fitting a Generalized Extreme Value (GEV) or Weibull tail distribution to the patch-level distances allows statistically rigorous threshold determination with guaranteed False Positive Rate bounds.

#### Proposed Methodology
1. Extract peak anomaly scores $S = \{s_1, \dots, s_N\}$ from $N$ available normal calibration specimens ($N \in [5, 15]$).
2. Fit a 2-parameter Weibull tail distribution to the peak scores:
   $$F(s) = 1 - \exp\left( - \left(\frac{s}{\lambda}\right)^k \right)$$
3. Compute the target threshold $\tau$ at a prescribed industrial risk level (e.g., $\alpha = 0.001$):
   $$\tau = \lambda \left( -\ln(\alpha) \right)^{1/k}$$
4. Implement automatic power-warning flags: if $N < 10$, output statistical uncertainty intervals in the telemetry UI.
- **Expected Outcome:** Replaces heuristic margin multipliers ($1.15 \times$) with mathematically proven false alarm limits.

---

### Workstream 4: Domain Divergence-Aware Dynamic Coreset Selection (Wasserstein Subsampling)

#### Hypothesis
Random greedy $K$-Center coreset selection assumes an isotropic distribution of normal patches. When adapting to a target environment with directional lighting or lens flare, greedy selection over-samples outlier lighting artifacts.

#### Proposed Methodology
- Compute the Wasserstein distance (Earth Mover's Distance) between the source domain feature distribution $\mathcal{P}_{\text{source}}$ and the few-shot target domain patches $\mathcal{P}_{\text{target}}$.
- Weight patch importance by domain density ratio:
  $$w_i = \frac{p_{\text{target}}(z_i)}{p_{\text{source}}(z_i) + \epsilon}$$
- Execute density-weighted coreset subsampling, retaining nominal variation while suppressing camera noise spikes.
- **Expected Outcome:** Reduces coreset memory size by 40% while eliminating the false positive alarms induced by lighting shifts.

---

### Workstream 5: Self-Supervised Synthetic Defect Augmentation (CutPaste & Surface Jitter)

#### Hypothesis
Training memory banks strictly on normal data leaves the decision boundary unbounded in orthogonal directions. Injecting self-supervised synthetic anomalies (CutPaste, Perlin noise texture blending) on target normal images will allow discriminative calibration of profile boundaries.

#### Proposed Methodology
1. Take $N=5$ target normal images.
2. Synthesize pseudo-anomalies:
   - CutPaste (rectangular patch swap with color jitter).
   - Perlin noise surface perturbation (simulating abrasions, scratches).
3. Evaluate whether nominal threshold $\tau$ successfully segregates all synthetic anomalies while accepting raw normal samples.
4. Auto-tune threshold $\tau$ to maximize the margin $\Delta = \min(s_{\text{synthetic}}) - \max(s_{\text{normal}})$.
- **Expected Outcome:** Provides automated threshold verification without requiring real defective production specimens.

---

### Workstream 6: MVTec AD 2 & Logical Anomaly Integration (Structural Verification)

#### Hypothesis
Industrial products frequently suffer from logical anomalies (e.g., correct bottle, correct cap, but missing seal or wrong fluid level). PatchCore cannot detect missing items if the remaining background matches nominal patches.

#### Proposed Architecture
- **Stage 1 (Local Surface Anomalies):** DefectVision 2.1 PatchCore pipeline for scratches, dents, and contaminations.
- **Stage 2 (Global Composition Verification):** Vision-Language / Zero-Shot Object Detector (Grounding DINO or YOLO-World) validating component topology:
  $$\text{Checklist: } \{\text{cap: present, liquid\_level: [0.75, 0.85], label: aligned}\}$$
- **Fusion:** Final verdict is DEFECTIVE if either Stage 1 detects a surface defect OR Stage 2 detects a structural violation.
- **Expected Outcome:** Complete compliance with the MVTec LOCO AD (Logical Constraints) benchmark.

---

## 3. Implementation Roadmap & Timeline

| Phase | Milestone | Duration | Key Deliverable |
|:---|:---|:---|:---|
| **Phase 1** | Foundation Model Dual-Branch (DINOv2 + ResNet) | 2 Weeks | ResNet+DINOv2 extractor; verification on Pill Color |
| **Phase 2** | Extreme Value Theory (EVT) Calibration Engine | 1 Week | `src/evt_calibration.py` with Weibull fitting & CI bounds |
| **Phase 3** | Hierarchical Multi-Scale PatchCore Memory Banks | 2 Weeks | Decoupled L2/L3 banks; evaluated on MVTec fine cracks |
| **Phase 4** | Synthetic Defect Calibration (CutPaste Auto-Tuning) | 2 Weeks | Automated threshold optimizer via pseudo-anomalies |
| **Phase 5** | MVTec LOCO AD Structural Verification Prototype | 3 Weeks | Dual-stage surface + logical inspection engine |
| **Phase 6** | End-to-End Production Hardening & Benchmarking | 2 Weeks | Full 15-category MVTec AD + LOCO evaluation report |

---

## 4. Scientific Conclusion & Recommendation

The DefectVision AI 2.1 architecture establishes a solid, verified foundation for few-shot adaptation in controlled industrial settings. Moving to DefectVision AI 2.2 will systematically eliminate the remaining edge cases (semantic color invariance and small-sample threshold instability), providing a commercially viable, research-grade inspection system.
