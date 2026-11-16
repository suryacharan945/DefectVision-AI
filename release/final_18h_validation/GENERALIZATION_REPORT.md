# DefectVision AI — Generalization & Domain Shift Audit Report

**Sprint Phase:** Phase 3 Deliverable  
**Timestamp:** 2026-11-01T23:17:30+05:30  
**Compliance Standard:** Zero-Leakage Independent Generalization Protocol V3  
**Protocol Document:** [independent_test_protocol.md](file:///c:/Users/surya/Downloads/Mini%20Project/release/final_18h_validation/independent_test_protocol.md)  
**Transfer Analysis:** [domain_shift_analysis.md](file:///c:/Users/surya/Downloads/Mini%20Project/release/final_18h_validation/domain_shift_analysis.md)  
**Failure Case Analysis:** [failure_cases.md](file:///c:/Users/surya/Downloads/Mini%20Project/release/final_18h_validation/failure_cases.md)

---

## 1. Independent Benchmark Quarantine Audit

To preserve the scientific integrity of external blind testing, DefectVision AI maintains strict quarantine controls over independent cohorts:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   INDEPENDENT BENCHMARK QUARANTINE STATUS              │
├───────────────────────┬──────────────┬─────────────┬───────────────────┤
│ Benchmark Cohort      │ Total Cohort │ Access Log  │ Current Status    │
├───────────────────────┼──────────────┼─────────────┼───────────────────┤
│ VisA (11 Categories)  │ 11 Products  │ ZERO ACCESS │ STRICT QUARANTINE │
│ BTAD (3 Products)     │ 3 Industrial │ ZERO ACCESS │ STRICT QUARANTINE │
│ Chukyo Metal Screws   │ Fasteners    │ ZERO ACCESS │ STRICT QUARANTINE │
├───────────────────────┼──────────────┼─────────────┼───────────────────┤
│ VisA `candle` & `pcb1`│ 2 Categories │ Dev Exposed │ Quarantined/Doc'd │
└───────────────────────┴──────────────┴─────────────┴───────────────────┘
```

### Formal Independence Finding:
```
================================================================================
INDEPENDENT GENERALIZATION STATUS:
  INDEPENDENT GENERALIZATION: NOT EVALUATED ON UNSEEN DOMAINS / PRESERVED BENCHMARKS
  
RATIONALE:
  In accordance with Sprint Constraint 5, the model was NOT exposed to the
  11 reserved VisA categories, BTAD, or Chukyo. This ensures that when external
  third-party validation is commissioned, the benchmark evaluation remains
  completely uncompromised and leakage-free.
================================================================================
```

---

## 2. In-Domain Category Generalization Findings

While external benchmarks remain quarantined, DefectVision AI was evaluated across 15 structurally diverse manufacturing domains within MVTec AD:
- **Rigid Objects (5):** `bottle`, `capsule`, `metal_nut`, `pill`, `screw`.
- **Flexible / Articulated Objects (5):** `cable`, `hazelnut`, `toothbrush`, `transistor`, `zipper`.
- **Regular & Stochastic Textures (5):** `carpet`, `grid`, `leather`, `tile`, `wood`.

### Transfer Observations:
1. **Geometric vs Texture Transfer:**
   - On stochastic textures (`carpet`, `leather`, `tile`, `wood`), both PatchCore and EfficientNet achieve $>0.93$ F1 score. Texture anomalies disrupt periodic spatial statistics, which is easily detected by convolutional feature maps.
   - On rigid metallic parts (`screw`, `transistor`), subtle mechanical defects (e.g. stripped thread pitch, slightly bent lead) require tighter spatial pooling. The Hybrid architecture resolved this, boosting `screw` F1 from $0.7179$ (PatchCore alone) to **$0.9032$** (Hybrid).
2. **Defect Morphology Invariance:**
   - Evaluated across structural cracks, punctures, cuts, burns, contamination, and foreign inclusions.
   - PatchCore successfully flagged novel OOD contaminations, while EfficientNet accurately identified recurring mechanical breaks.

---

## 3. Generalization Limitations & Operational Boundaries

1. **Illumination Calibration Boundary:**
   Factory lighting shifts exceeding $\pm 30\%$ or significant spectral changes require a nominal baseline update ($\tau_{\text{p99}}$ recalibration over 50 unblemished specimens).
2. **Micro-Defect Resolution Threshold:**
   Defects smaller than $4 \times 4$ pixels at native sensor resolution risk sub-patch feature dilution under the current $28 \times 28$ spatial grid. Inspection lines requiring detection of sub-millimeter defects must implement high-resolution sliding-window tiling ($512 \times 512$ patches).
