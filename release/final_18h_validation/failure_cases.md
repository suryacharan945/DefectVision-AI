# DefectVision AI — Failure Case & Edge Case Analysis

**Sprint Phase:** Phase 3 Deliverable  
**Timestamp:** 2026-11-01  
**Category Focus:** False Alarms (Type I) and Defect Escapes (Type II) in Industrial AD

---

## 1. Failure Mode Taxonomy

Every machine vision inspection model encounters failure modes dictated by sensor physics, feature pooling resolutions, and distribution boundaries. In DefectVision AI, the empirical error modes fall into four distinct categories:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        FAILURE MODE TAXONOMY                           │
├─────────────────────┬───────────────────────────┬──────────────────────┤
│ Failure Class       │ Example Manifestation     │ Root Mechanism       │
├─────────────────────┼───────────────────────────┼──────────────────────┤
│ 1. Sub-Patch Dilution│ Tiny pinhole on `pill`   │ Feature averaging    │
│    (Defect Escape)  │ Micro-scratch on `cable`  │ over 8x8 px receptive│
├─────────────────────┼───────────────────────────┼──────────────────────┤
│ 2. Natural Variance │ Wood knot pattern         │ Incomplete coreset   │
│    (False Alarm)    │ Natural leather grain     │ coverage of nominals │
├─────────────────────┼───────────────────────────┼──────────────────────┤
│ 3. Specular Glare   │ Glossy bottle highlight   │ L2 feature distance  │
│    (False Alarm)    │ Metallic nut reflection   │ spike on saturation  │
├─────────────────────┼───────────────────────────┼──────────────────────┤
│ 4. Symmetric Blend  │ Bent transistor lead      │ Lead blends into     │
│    (Defect Escape)  │ Thread pitch deformity    │ background shadow    │
└─────────────────────┴───────────────────────────┴──────────────────────┘
```

---

## 2. In-Depth Case Studies

### Case Study A: Sub-Patch Defect Dilution (Pill / Capsule)
- **Observation:** Certain microscopic pinholes or hairline cracks on capsule coatings produce relatively low PatchCore anomaly scores ($S \approx 1.25$ vs threshold $1.55$).
- **Mechanism:** ResNet-18 feature extraction operates on a downsampled grid ($28 \times 28$ spatial resolution). A defect spanning $2 \times 2$ pixels at input resolution ($224 \times 224$) contributes less than $5\%$ of the receptive field of a patch token. The subsequent $3 \times 3$ average pooling further dilutes the anomalous activation with surrounding nominal tissue.
- **Remediation Strategy:** Multi-scale feature extraction incorporating `layer1` tokens (grid $56 \times 56$) or high-resolution tiling/sliding-window crops ($512 \times 512$).

### Case Study B: Specular Glare & Metallic Reflections (Bottle / Metal Nut)
- **Observation:** Nominal metal nuts or glass bottles subjected to directional lighting occasionally register anomaly scores slightly above the p99 threshold ($S \approx 1.98$ vs threshold $1.95$).
- **Mechanism:** Deep convolutional backbones pretrained on ImageNet encode high-contrast glare as high-frequency edge textures divergent from diffuse nominal reflections.
- **Remediation Strategy:** Cross-polarization illumination hardware on production lines, and polarizing lens filters to eliminate specular hot spots.

### Case Study C: Texture Grain Variability (Wood / Carpet)
- **Observation:** Organic textures naturally exhibit greater intra-class nominal variance than rigid manufactured parts.
- **Mechanism:** A 10% coreset budget may select insufficient representatives of rare nominal grain swirls, leading the model to treat benign natural variations as structural anomalies.
- **Remediation Strategy:** Adaptive coreset sampling ratio (e.g. 20% for stochastic textures like `wood` and `carpet`, vs 5% for rigid geometric objects like `screw` and `bottle`).
