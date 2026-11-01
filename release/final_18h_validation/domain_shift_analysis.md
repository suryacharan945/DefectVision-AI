# DefectVision AI — Domain Shift & Transferability Analysis

**Sprint Phase:** Phase 3 Deliverable  
**Timestamp:** 2026-11-01  
**Target Context:** Industrial Surface Anomaly Detection Across Sensor & Factory Shifts

---

## 1. Domain Shift Taxonomy in Industrial Vision

Industrial computer vision models trained in controlled laboratory environments frequently experience severe performance collapse when deployed to factory floors due to distribution shifts. In DefectVision AI, the dual-engine architecture (PatchCore + EfficientNet) exhibits distinct transfer characteristics across five primary domain shift vectors:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        INDUSTRIAL DOMAIN SHIFT VECTORS                 │
├───────────────────────┬────────────────────────┬───────────────────────┤
│ Vector                │ Physical Cause         │ Subsystem Vulnerability│
├───────────────────────┼────────────────────────┼───────────────────────┤
│ 1. Illumination Shift │ Strobe LED degradation │ High (PatchCore)      │
│                       │ Factory ambient light  │ Moderate (EfficientNet)│
├───────────────────────┼────────────────────────┼───────────────────────┤
│ 2. Spatial Misalign   │ Conveyor belt wobble   │ Low (PatchCore patch) │
│                       │ Part rotation jitter   │ Moderate (EfficientNet)│
├───────────────────────┼────────────────────────┼───────────────────────┤
│ 3. Substrate Shift    │ Raw material batches   │ High (PatchCore)      │
│                       │ Ambient oxidation      │ Low (EfficientNet)    │
├───────────────────────┼────────────────────────┼───────────────────────┤
│ 4. Novel Defect Modes │ New machining failure  │ Low (PatchCore OOD)   │
│                       │ Foreign contaminants   │ Fatal (EfficientNet)  │
├───────────────────────┼────────────────────────┼───────────────────────┤
│ 5. Sensor Optic Noise │ Thermal sensor noise   │ Moderate (PatchCore)  │
│                       │ Vibration lens blur    │ Moderate (EfficientNet)│
└───────────────────────┴────────────────────────┴───────────────────────┘
```

---

## 2. In-Depth Subsystem Transfer Analysis

### A. PatchCore Unsupervised Memory Banks:
- **Strengths:** Because PatchCore evaluates patch-level feature distances against a nominal memory bank, it possesses intrinsic open-world defect sensitivity. Novel defect types that never appeared in training are flagged reliably as long as their local features diverge from nominal patches.
- **Vulnerabilities:** PatchCore is sensitive to global photometric shifts. If factory lighting dims by 20% or shifts color temperature, every patch embedding drifts away from the nominal bank, triggering systematic false alarms across all nominal products (elevated FPR).
- **Mitigation Requirement:** Local histogram equalization, adaptive nominal centering, or periodic running baseline recalibration ($\tau_{\text{p99}}$).

### B. EfficientNet-B0 Supervised Classifier:
- **Strengths:** EfficientNet is robust to photometric shifts due to heavy data augmentation (color jitter, brightness/contrast scaling) during training.
- **Vulnerabilities:** Closed-world assumption. Supervised classifiers cannot reliably classify anomaly topologies that fall outside their training defect classes. On completely novel defect types, EfficientNet produces overconfident false negatives ($p_{\text{defective}} \approx 0.05$), failing to flag critical escapes.
- **Mitigation Requirement:** Hybrid fusion with PatchCore (logical OR), ensuring that unsupervised OOD detection catches defect escapes that slip past the classifier.

---

## 3. Transferability Recommendations for Industrial Deployment

1. **Pre-Deployment Calibration Window:** Prior to active line gating, record 50-100 nominal specimens under live factory illumination to establish localized baseline statistics ($\mu_0, \tau_{\text{p99}}$).
2. **Dynamic Illumination Compensation:** Standardize sensor exposure via white-balance calibration targets on conveyor borders.
3. **Dual-Trigger Fallback:** Maintain the logical OR hybrid decision policy so that neither sensor drift nor novel defect geometries create unmonitored defect escapes.
