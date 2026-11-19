# DEFECTVISION AI — FINAL FILE INVENTORY
**Sprint:** Emergency Release Sprint: v1.0.0-rc1 (72-Hour Project Closure)  
**Date:** 2026-11-19  
**Auditor:** Senior ML Engineer, Computer Vision Research Engineer, QA Lead & Release Manager  

---

## 1. Directory Structure Overview

The repository is organized into distinct functional layers separating backend ML inference, frontend web interface, model storage, validation tests, research experiments, and documentation:

```
DefectVision-AI/
├── DefectVisionAI/            # Core backend application & optical inference engine
│   ├── app.py                 # FastAPI service entrypoint (REST API & routing)
│   ├── src/                   # Core Python packages
│   │   ├── core/              # PatchCore engine, ResNet-18 extractor, FAISS memory banks
│   │   ├── classifier/        # EfficientNet-B0 category recognition model & weights
│   │   ├── triage/            # Universal image intake, quality validation & adaptive router
│   │   └── utils/             # Image normalization, heatmap colormapping & serialization
│   ├── models/                # 15 category PatchCore memory banks, FAISS indexes & thresholds
│   ├── dataset/               # MVTec AD specimen storage & test splits
│   └── outputs/               # Saved inspection heatmaps and batch summaries
├── frontend/                  # React + Vite interactive user interface
│   ├── src/                   # Components, API client, hooks, context & styling
│   │   ├── components/        # Image inspection viewer, camera intake, batch table, metrics
│   │   ├── api/client.js      # Resilient axios API client with localhost fallback detection
│   │   └── App.jsx            # Single-page application entrypoint
│   ├── package.json           # Frontend dependencies & build configuration
│   └── vite.config.js         # Vite dev-server & bundle optimization config
├── tests/                     # 92 unit and integration test specifications
│   ├── test_patchcore.py      # Core anomaly detection & memory bank validation
│   ├── test_classifier.py     # EfficientNet-B0 category classification tests
│   ├── test_quality_gate.py   # Blur, exposure, resolution & OOD rejection tests
│   ├── test_api.py            # FastAPI endpoint contracts & error payloads
│   └── test_adaptation.py     # Reference-adaptive routing & profile tests
├── docs/                      # Technical documentation & guides
├── release/                   # Formal release audits, experiments & publication reports
│   ├── audits/                # Integrity, regression & git verification reports
│   └── experiments/           # Benchmark evaluations, CSV datasets & threshold audits
├── scripts/                   # Auditing, evaluation & maintenance automation scripts
├── requirements.txt           # Python dependency specifications
└── README.md                  # Comprehensive project documentation
```

---

## 2. Production Model Inventory

All 15 industrial category models are fully intact and located in `DefectVisionAI/models/`:

| Category | Model Architecture | Embedding Dim | Memory Bank File | FAISS Index File | Calibrated Anomaly Threshold ($\tau$) |
|---|---|---|---|---|---|
| **bottle** | PatchCore (ResNet-18) | 384 | `bottle_memory_bank.pt` | `bottle_faiss.index` | 1.4541 |
| **cable** | PatchCore (ResNet-18) | 384 | `cable_memory_bank.pt` | `cable_faiss.index` | 1.8320 |
| **capsule** | PatchCore (ResNet-18) | 384 | `capsule_memory_bank.pt` | `capsule_faiss.index` | 1.7650 |
| **carpet** | PatchCore (ResNet-18) | 384 | `carpet_memory_bank.pt` | `carpet_faiss.index` | 1.6210 |
| **grid** | PatchCore (ResNet-18) | 384 | `grid_memory_bank.pt` | `grid_faiss.index` | 1.5420 |
| **hazelnut** | PatchCore (ResNet-18) | 384 | `hazelnut_memory_bank.pt` | `hazelnut_faiss.index` | 1.7100 |
| **leather** | PatchCore (ResNet-18) | 384 | `leather_memory_bank.pt` | `leather_faiss.index` | 1.5890 |
| **metal_nut** | PatchCore (ResNet-18) | 384 | `metal_nut_memory_bank.pt` | `metal_nut_faiss.index` | 1.6940 |
| **pill** | PatchCore (ResNet-18) | 384 | `pill_memory_bank.pt` | `pill_faiss.index` | 1.6880 |
| **screw** | PatchCore (ResNet-18) | 384 | `screw_memory_bank.pt` | `screw_faiss.index` | 1.7450 |
| **tile** | PatchCore (ResNet-18) | 384 | `tile_memory_bank.pt` | `tile_faiss.index` | 1.6320 |
| **toothbrush**| PatchCore (ResNet-18) | 384 | `toothbrush_memory_bank.pt` | `toothbrush_faiss.index`| 1.5120 |
| **transistor**| PatchCore (ResNet-18) | 384 | `transistor_memory_bank.pt` | `transistor_faiss.index`| 1.6740 |
| **wood** | PatchCore (ResNet-18) | 384 | `wood_memory_bank.pt` | `wood_faiss.index` | 1.5980 |
| **zipper** | PatchCore (ResNet-18) | 384 | `zipper_memory_bank.pt` | `zipper_faiss.index` | 1.6420 |
| **classifier**| EfficientNet-B0 v3 | 1280 $\rightarrow$ 15 | `efficientnet_b0_v3.pth` | N/A | Softmax argmax ($p \ge 0.50$) |

---

## 3. Research Experiment & Audit Artifacts

The `release/experiments/` and `release/audits/` directories contain frozen scientific evidence:

1. `release/audits/DEFECTVISION_2_4_EXPERIMENT_PROVENANCE.md`: Execution traceability.
2. `release/audits/DEFECTVISION_2_4_REGRESSION_REPORT.md`: Unit test and build certification.
3. `release/experiments/DEFECTVISION_2_4_FINAL_RESEARCH_DECISION.md`: Executive consensus on 9 research questions.
4. `release/experiments/FEATURE_FUSION_IMPLEMENTATION_AUDIT.md`: Mathematical analysis of 384 vs 3 channel imbalance.
5. `release/experiments/K20_THRESHOLD_SELECTION_AUDIT.md`: Leakage analysis of multiplier 1.20.
6. `release/experiments/KSHOT_THRESHOLD_FINAL_DECISION.md`: Rejection of post-hoc K=20 threshold for production.
7. `release/experiments/SPATIAL_PHOTOMETRIC_ACCEPTANCE_AUDIT.md`: Evaluation of 7 feature-fusion variants.
8. `release/experiments/SPATIAL_PHOTOMETRIC_DATA_AUDIT.md`: Forensic reconciliation of 77 vs 61 specimens.
9. `release/experiments/SPATIAL_PHOTOMETRIC_EXPERIMENT_2_SPECIFICATION.md`: Decoupled dual-stream specification.
10. `release/experiments/STATISTICAL_VALIDITY_AND_CONFIDENCE_INTERVAL_REPORT.md`: Wilson score and Rule-of-Three intervals.
11. `release/experiments/TRACK_B_DATA_COLLECTION_AND_STATISTICAL_PLAN.md`: Protocol for external domain data collection.
12. `release/experiments/k20_frozen_policy_results.csv`: A priori vs. tuned threshold evaluation.
13. `release/experiments/k20_threshold_selection_history.csv`: Sweep of multipliers against test bottles.
14. `release/experiments/spatial_photometric_detailed_acceptance.csv`: Disaggregated performance of fusion variants.
15. `release/experiments/spatial_photometric_partition_manifest.csv`: 107 physical specimen SHA-256 hashes.
16. `release/experiments/spatial_photometric_sample_count_reconciliation.csv`: Explicit specimen reconciliation.
17. `release/experiments/statistical_confidence_intervals.csv`: Confidence bounds across primary metrics.

---

## 4. Security & Hygiene Audit of Files

- **Credentials / API Keys:** Audited. No API tokens, private keys, or passwords exist in tracked files.
- **Git Ignore Hygiene:** `.gitignore` excludes `__pycache__`, `.venv`, `node_modules`, `.env.local`, and local temporary logs.
- **Dataset Storage:** Raw large-scale datasets are kept locally and not committed to git, preserving repository speed and compliance.

---

## 5. Audit Verdict

- **File Inventory:** **COMPLETE, VERIFIED & COMMITTED**
- **Status:** **PASS**
