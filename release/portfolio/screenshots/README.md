# DefectVision AI — Curated Visual Evidence Inventory

This directory contains verified, production-authentic visual evidence and telemetric plots captured during the rigorous release evaluation of DefectVision AI (`v1.0.0-rc1`).

No synthetic or simulated mockups are present. All images represent genuine inference runs, authentic UI states, or mathematical evaluation plots derived directly from the MVTec Anomaly Detection benchmark dataset and live FastAPI/React execution.

---

## Visual Assets Directory

| Asset File | Dimension / Format | Description & Verification Provenance |
| :--- | :--- | :--- |
| `01_genuine_specimen_raw_bottle_defective.png` | 1024×1024 PNG | Raw input image of an authentic MVTec `bottle` defective specimen (`broken_large` defect type). Unprocessed factory capture. |
| `02_genuine_patchcore_heatmap_defective.png` | 1024×1024 PNG | Dense pixel-level PatchCore anomaly distance heatmap generated via ResNet18 layer2/3 neighborhood embeddings. Deep red highlights localized fracture boundaries. |
| `03_genuine_overlay_defective.png` | 1024×1024 PNG | Composite overlay: raw inspection image fused with the jet colormap anomaly heatmap (alpha=0.5), visually isolating the crack site. |
| `04_genuine_specimen_raw_bottle_nominal.png` | 1024×1024 PNG | Raw input image of a pristine, nominal MVTec `bottle` test specimen (`good` condition). |
| `05_genuine_patchcore_heatmap_nominal.png` | 1024×1024 PNG | Dense PatchCore anomaly heatmap for the nominal bottle. Uniform low Euclidean distance (dark blue / green floor) confirming absence of structural outliers. |
| `06_genuine_overlay_nominal.png` | 1024×1024 PNG | Composite overlay for the nominal bottle specimen confirming zero defect alerts across the structural surface. |
| `07_architecture_and_pipeline_diagram.png` | High-res PNG | End-to-end multi-stage inspection architecture diagram: intake, quality gating, EfficientNet-B0 category classification, PatchCore feature extraction, FAISS search, and UI telemetry. |
| `08_dual_engine_inference_storyboard.png` | High-res PNG | Side-by-side comparative storyboard tracking simultaneous processing of nominal vs. defective specimens across all pipeline stages. |
| `09_synthetic_demo_mode_with_warning.png` | UI Screenshot | Visual proof of the localhost demo fallback banner, verifying that synthetic demo modes are clearly flagged and never silently masquerade as real inference. |
| `10_batch_inspection_telemetry_dashboard.png` | UI Screenshot | Production batch inspection telemetry dashboard displaying aggregate pass/fail rates, latency histograms, and per-specimen score breakdown. |
| `11_confusion_matrices_comparison_plot.png` | Plot PNG | Multi-class category classification confusion matrix (1,724/1,725 correct, 99.94%) contrasted with binary defect classification confusion matrix (86.92% accuracy, 111 escapes). |
| `12_audited_tradeoff_recall_vs_false_alarms.png` | Plot PNG | Empirical ROC and PR curves showing Macro Image AUROC (97.15%), Macro AUPRC (98.98%), and the threshold trade-off between 94.04% defect recall and 24.84% FPR. |
| `13_api_inspection_response_telemetry.png` | Schema / JSON PNG | Verified JSON payload from `POST /api/inspect`, demonstrating authentic latency breakdown, category routing confidence, anomaly score, and base64 heatmap transmission. |
| `14_ui_live_inference_normal_inspection.png` | 1280×800 UI PNG | Real-time frontend inspection screen (`http://127.0.0.1:5174`) evaluating a nominal specimen, showing green "PASS - NOMINAL" status and LIVE INFERENCE ACTIVE badge. |
| `15_ui_live_inference_defective_heatmap.png` | 1280×800 UI PNG | Real-time frontend inspection screen evaluating a defective specimen, showing red "FAIL - DEFECT DETECTED" status, anomaly score 1.94, and interactive heatmap inspection panel. |

---

## Confidentiality & Security Notice

All visual assets have been screened to ensure:
1. No private IP addresses or corporate network domains are exposed (only `http://127.0.0.1` localhost).
2. No local filesystem absolute paths, system usernames, or developer directories are visible.
3. No credentials, tokens, or private customer datasets are included.
