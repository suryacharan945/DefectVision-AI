# DefectVision AI — Feature Verification Matrix

**Document ID:** `DV-MATRIX-2026-REL-V1`  
**Date:** October 31, 2026  
**Release Target:** DefectVision AI Production v1.0.0  
**Verification Standard:** ISO/IEC 25010 Software Quality Requirements  

---

## 1. Comprehensive Feature Status Inventory

| Feature Name | Functional Classification | Frontend Component | Backend Endpoint / Script | Verification Evidence | Operational Status |
|:---|:---|:---|:---|:---|:---:|
| **Single-Image Inspection** | Core Production (P0) | `InspectSection.jsx` | `POST /api/inspect` | Tested on bottle, screw, and carpet specimens. Interactive heatmap overlay, zoom reticle, and threshold slider functional. | **VERIFIED** |
| **Model Architecture & Provenance Drawer** | Core Production (P0) | `InspectSection.jsx` | N/A (Embedded provenance spec) | Renders active model backbone, ImageNet normalization, decision threshold derivation, MVTec AD training regime, 856-image benchmark metrics, and disclaimers. | **VERIFIED** |
| **Batch High-Throughput Inspection** | Core Production (P1) | `BatchInspectionSection.jsx` | `POST /api/batch/submit`<br>`GET /api/batch/{id}` | Tested with 150-specimen batch (`batch_inspections/demo_150img_batch/`). Verified real-time progress polling, severity distribution bars, specimen detail view, and CSV/JSON export. | **VERIFIED** |
| **Batch Report CSV & JSON Export** | Core Production (P1) | `BatchInspectionSection.jsx` | Client-side export | Generates downloadable `batch_{id}_results.csv` and `batch_{id}.json` directly from inspection memory. | **VERIFIED** |
| **Inspection History Browser** | Core Production (P0) | `HistoryBrowserSection.jsx` | `GET /api/severity-logs` | Browses all 1,725 scored MVTec AD benchmark test images. Multi-criteria filtering by category (15) and severity (Critical/Moderate/Minor), real-time text search, and specimen inspection modal. | **VERIFIED** |
| **Filtered History CSV Export** | Core Production (P1) | `HistoryBrowserSection.jsx` | Client-side export | One-click button generates `inspection_history_{category}_{timestamp}.csv` containing filtered IDs, labels, severity scores, and defect areas. | **VERIFIED** |
| **Operational Severity Index** | Production Feature (P1) | `SeverityBadge.jsx`<br>`InspectSection.jsx` | `DefectVisionAI/step9_severity.py` | Computes heuristic score ($0-100$) combining normalized peak anomaly distance and percentage of defective surface area. Disclosed as operational triage heuristic. | **VERIFIED** |
| **PatchCore Memory Bank Localization** | Core Production (P0) | `InspectSection.jsx` | `DefectVisionAI/step7_patchcore.py`<br>`models/faiss_index/` | Sub-image defect localization via $1$-NN Euclidean distance to nominal coreset patches. Produces high-resolution anomaly heatmaps. | **VERIFIED** |
| **Grad-CAM Saliency Attribution** | Advanced Feature (P2) | `InspectSection.jsx` | `DefectVisionAI/step4_gradcam.py` | Visual gradient attribution on intermediate convolution layers of EfficientNet-B0. | **VERIFIED** |
| **FAISS Nearest-Neighbor Similarity Retrieval** | Advanced Feature (P2) | `SimilaritySection.jsx` | `POST /api/similar-defects` | Retrieves top-$k$ nearest historical defects across the embedding space for rapid defect taxonomy matching. | **VERIFIED** |
| **Drift Monitoring Dashboard** | Advanced Feature (P2) | `DriftSection.jsx` | `GET /api/drift-status` | Evaluates temporal feature distribution shift via symmetric Gaussian KL divergence and Wasserstein distance against nominal reference baselines (`step12_drift_log_v3.csv`). | **VERIFIED** |
| **RAG Defect Copilot & Assistant** | Advanced Feature (P2) | `RagChatSection.jsx` | `POST /api/chat-rag` | Natural language interface querying verified engineering root-cause records (`models/rag_knowledge_base/defect_knowledge_base.csv`). Includes fallback safety guards. | **VERIFIED** |
| **Active Learning & Uncertainty Triage** | Advanced Feature (P1) | `InspectSection.jsx`<br>`ActiveLearningSection.jsx` | `logs/step11_uncertainty_log.csv` | Identifies borderline predictions near threshold $\tau$. Routes high-uncertainty specimens to human review; demonstrates $48\%$ defect-error capture at $9.7\%$ review budget. | **VERIFIED** |
| **Root-Cause Analysis (RCA) Clustering** | Research / Assistive (P2) | `RcaSection.jsx` | `POST /api/rca-analyze` | Heuristic clustering of defects by geometric shape, texture signature, and manufacturing station correlation. Labeled as assistive guidance. | **VERIFIED** |
| **Live Webcam Streaming Inspection** | Demo Feature (P3) | `WebcamSection.jsx` | Browser `navigator.mediaDevices` | Live video capture with center-crop reticle and frame sampling rate control. Fallback mock frame generator for headless servers. | **VERIFIED** |
| **YOLOv8 Optical Reticle Pre-Crop** | Experimental Prototype (P3) | `WebcamSection.jsx` | Notebook Cells 41–42 | Prototyped for multi-part conveyor object detection. Explicitly demarcated as experimental; not used in standard single-part PatchCore inspection. | **EXPERIMENTAL** |

---

## 2. Feature Classification Definitions

* **Core Production (P0/P1):** Essential industrial inspection workflows that must operate with zero defects, full input validation, and high performance.
* **Advanced Feature (P2):** Higher-level analytical capabilities (drift, similarity, RAG, active learning) providing assistive insights to production engineers.
* **Demo / Assistive Feature (P3):** Auxiliary demonstration workflows (webcam streaming, mock simulations) designed for interactive evaluations.
* **Experimental Prototype:** Exploratory algorithms (e.g. YOLOv8 multi-part bounding boxes) isolated from the primary inspection pipeline to prevent regressions.

---

## 3. UI Component to API Endpoint Mapping

```
[UI SECTION]                    [API ROUTE]                  [BACKEND MODULE / DATA]
InspectSection.jsx        ──►  POST /api/inspect        ──►  PatchCore / ResNet / Fallback JSON
BatchInspectionSection    ──►  POST /api/batch/submit   ──►  Asynchronous Queue Worker
                               GET  /api/batch/{id}     ──►  Batch Status & Results JSON
HistoryBrowserSection     ──►  GET  /api/severity-logs  ──►  1,725-Specimen Benchmark Database
SimilaritySection         ──►  POST /api/similar-defects──►  FAISS Index (512-dim Embeddings)
DriftSection              ──►  GET  /api/drift-status   ──►  Gaussian KL Reference (`drift_v3.csv`)
RagChatSection            ──►  POST /api/chat-rag       ──►  RAG Vector Store (`knowledge_base.csv`)
```

---
*Maintained by:*  
**DefectVision AI Integration & Release Engineering Team**
