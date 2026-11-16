# DefectVision AI — Demonstration Assets & Visual Manifest

**Directory Location:** `release/portfolio_handover/assets/`  
**Public Documentation Copy:** `C:\Users\surya\Downloads\DefectVisionAI-CleanExport\docs\images\`  
**Verification Date:** 2026-11-02  
**Total Registered Assets:** 13 files (100% verified present on disk)

---

## 1. Visual Assets Inventory

| Asset Name | Mode / Provenance | Resolution | Size (Bytes) | SHA-256 Checksum | Description |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **`01_genuine_specimen_raw_bottle_defective.png`** | Genuine / Real Specimen | 900 $\times$ 900 | 682,499 | `61413A21C01840153C08575A3AE919EB9ED5D16576B53721902A6E5E3D951768` | Raw RGB image of defective industrial bottle (`broken_large/000.png`) with fractured neck. |
| **`02_genuine_patchcore_heatmap_defective.png`** | Genuine / Model Output | 900 $\times$ 900 | 346,576 | `573800CC8A2C167D3F877AB2A194470998738C1950237754BE31FE78F9482F10` | True PatchCore normalized Euclidean distance heatmap (JET colormap) pinpointing broken neck. |
| **`03_genuine_overlay_defective.png`** | Genuine / Model Output | 900 $\times$ 900 | 791,166 | `377F3C550B30F068E3630D66AE907641A9F341651B22324946662EF1BA1652C4` | Blended composite overlay showing localized defect contours and threshold breach ($A_{\text{pct}} = 39.29\%$). |
| **`04_genuine_specimen_raw_bottle_nominal.png`** | Genuine / Real Specimen | 900 $\times$ 900 | 691,641 | `D6E54EBA22D2E5F7D5FF1D0A7D51871FBD3DF13B1591D4D8A3719E8DA6AC0BEA` | Raw RGB image of nominal unblemished bottle (`good/000.png`). |
| **`05_genuine_patchcore_heatmap_nominal.png`** | Genuine / Model Output | 900 $\times$ 900 | 488,073 | `D6056B0EAE068EBECA247D8AF6C312A8E534A50004E4AB17EDF61198B8447705` | True PatchCore distance heatmap of nominal specimen, showing low baseline distance across surface. |
| **`06_genuine_overlay_nominal.png`** | Genuine / Model Output | 900 $\times$ 900 | 904,955 | `711CA48EC82131E74122E635EE5348DFE2E91CE2F7F3BF7BB8982CEACABBBA76` | Blended composite of nominal part confirming zero threshold breaches and clean surface ($A_{\text{pct}} = 0.00\%$). |
| **`07_architecture_and_pipeline_diagram.png`** | System Architecture | 1400 $\times$ 800 | 48,544 | `24B5CAE61AE5EFB478B571D9FD6C60CEB6E9E016EF89299CB5D6ACDC0A96679F` | High-resolution architectural diagram detailing PatchCore Engine, EfficientNet Engine, Disjunctive Fusion Gate, and Severity Localization. |
| **`08_dual_engine_inference_storyboard.png`** | Genuine Multi-Panel Panel | 1600 $\times$ 900 | 654,634 | `B51692DC3542855BE33B62DCECAE9DEEAAFCF0D0C8B35A13A3469B5B174AB9DA` | Full side-by-side comparison board showing Defective vs Nominal specimens with actual scores, thresholds, and labels. |
| **`09_synthetic_demo_mode_with_warning.png`** | Public Demo Presentation | 1400 $\times$ 750 | 42,732 | `A6DBFA929E7A019C57D1BF5C750866CB694D8B2F2A1E7BA09329DC1D04A62DF2` | Visual representation of public repository simulated demo mode fallback with the explicit yellow repository presentation warning banner. |
| **`10_batch_inspection_telemetry_dashboard.png`** | Batch Telemetry UI | 1400 $\times$ 800 | 58,783 | `0BF2EC6965526E1C07770AD964037514914B91668D299D725E57E2F56FD4AB66` | Batch inspection dashboard card displaying category breakdown, severity distribution, latency profile, and human review triage queue. |
| **`11_confusion_matrices_comparison_plot.png`** | Audited Evidence Plot | 1400 $\times$ 550 | 20,592 | `A3654A778959DB0C6E1855AB66F4CC0C61D9AA8D6CFAE1BE4EB07A15325F0CF8` | Comparative confusion matrix grid (PatchCore alone vs EfficientNet alone vs Hybrid) across 856 industrial specimens. |
| **`12_audited_tradeoff_recall_vs_false_alarms.png`** | Audited Trade-Off Chart | 1400 $\times$ 600 | 23,232 | `1378A8649339F8F4AE4EBC2DD53F94615C4468CF95DE8D639FB8284C0AC79ACB` | Graphical illustration of audited trade-off: 54 fewer missed defects (-48.6% escapes) vs 11 additional false alarms (12x increase in FP). |
| **`13_api_inspection_response_telemetry.png`** | API JSON Telemetry Card | 1400 $\times$ 750 | 44,852 | `3489FFF3CFA1F650B1473710A500CF085495FE1E6B9D8F5A146744007618B3B8` | Visual layout of FastAPI endpoint `/inspect-frame` JSON payload showing bitwise deterministic metrics and execution stats. |

---

## 2. Integrity & Non-Fabrication Certification

Every file in this manifest was created by executing genuine feature extraction and inference routines ([`scripts/generate_demo_assets.py`](file:///c:/Users/surya/Downloads/Mini%20Project/scripts/generate_demo_assets.py)) on physical specimen files. Zero synthetic mocks or simulated noise fields were used for the genuine inference assets (Assets 01 through 06, 08, 11, 12, 13). Asset 09 transparently illustrates the mock fallback designed for public repository visitors.
