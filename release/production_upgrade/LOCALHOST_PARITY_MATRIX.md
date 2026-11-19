# DefectVision AI — Localhost Functionality Parity Matrix

**Document Version:** 3.0.0  
**Date:** November 2026  
**Auditor:** ML Operations & Lead Systems Engineer  
**Reference Implementation:** Working Localhost Application (`http://127.0.0.1:5173` & `http://127.0.0.1:8001`)  
**Target Environment:** Public Production (`https://defectvision-ai.vercel.app/` + Persistent FastAPI Backend)  

---

## 1. System Overview & Parity Principles

DefectVision AI delivers a comprehensive, zero-leakage, few-shot industrial surface inspection platform across 15 MVTec AD manufacturing categories.

To ensure total transparency, all data presented in the user interface is tagged with one of three explicit provenance states:
1. **`LIVE_API`:** Dynamic prediction, heatmap, score, or profile generated in real time by the running FastAPI backend and resident PyTorch/FAISS inference models.
2. **`BENCHMARK_ARTIFACT`:** Static, peer-audited MVTec AD research benchmark artifacts (e.g. 15-category AUROC matrix, historical baseline distributions).
3. **`DEMO_FIXTURE`:** Explicit client-side demonstration data utilized strictly when Demo Mode is explicitly engaged or backend is offline.

---

## 2. Page-by-Page Parity Matrix

| Page / Section | Feature / Workflow | Primary Endpoint Called | Data Provenance | Remote Backend Support | Parity Status | Hardware / Browser Nuance |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Specimen Inspection** (`#inspect`) | Drag-and-drop file upload, autonomous category classification, anomaly score, calibrated threshold ($\tau \pm 8\%$), dual-pane heatmap view | `POST /api/predict`<br/>`POST /api/explain` | `LIVE_API` | Full Support | **100% PARITY** | Standard HTML5 file input. Works identically locally and remotely. |
| **Specimen Inspection** (`#inspect`) | 1-click curated specimen presets across 15 categories | `GET /api/samples/presets` | `LIVE_API` (fallback: `BENCHMARK_ARTIFACT`) | Full Support | **100% PARITY** | Images pre-packaged in static bundle for instant preview. |
| **Product Profiles** (`#profiles`) | List active and adapted manufacturing inspection stations | `GET /api/production-profiles` | `LIVE_API` | Full Support | **100% PARITY** | Profiles persist in `DEFECTVISION_DATA_DIR` across container restarts. |
| **Product Profiles** (`#profiles`) | Register new SKU and adapt PatchCore via few-shot normal specimens ($K=5..20$) | `POST /api/production-profiles/adapt` | `LIVE_API` | Full Support | **100% PARITY** | Uploads $K$ images, computes greedy coreset, extracts ResNet-18 features. |
| **Product Profiles** (`#profiles`) | Hold-out validation split evaluation (Confusion Matrix, FPR, Recall) | `POST /api/production-profiles/{id}/evaluate` | `LIVE_API` | Full Support | **100% PARITY** | Evaluates test split against calibrated decision threshold. |
| **Product Profiles** (`#profiles`) | Station activation, deactivation, and archiving | `POST /api/production-profiles/{id}/activate`<br/>`POST .../deactivate`<br/>`POST .../archive` | `LIVE_API` | Full Support | **100% PARITY** | Updates profile status and unloads/reloads resident models in RAM. |
| **Product Profiles** (`#profiles`) | Deep telemetry & score distribution analytics ($p_{50}, p_{99}$, SHA-256) | `GET /api/production-profiles/{id}/analytics` | `LIVE_API` | Full Support | **100% PARITY** | Returns vector count, memory bank bytes, and manifest hash. |
| **Live Optical Stream** (`#live`) | Real-time video frame acquisition, optical quality gating, reticle tracking | `POST /api/optical-inspection/inspect-frame` | `LIVE_API` | Full Support | **PARITY WITH BROWSER PERMISSION** | **Browser Camera Note:** Camera feed requires user-granted `navigator.mediaDevices.getUserMedia` permission over HTTPS. Server-side USB framegrabbers require browser bridge. |
| **Live Optical Stream** (`#live`) | 15-Category model readiness and baseline threshold matrix | `GET /api/optical-inspection/model-status` | `LIVE_API` | Full Support | **100% PARITY** | Probes all 15 category memory banks and baseline statistics. |
| **Live Optical Stream** (`#live`) | Optical inspection session history and verdict statistics | `GET /api/optical-inspection/history`<br/>`POST /api/optical-inspection/history/clear` | `LIVE_API` | Full Support | **100% PARITY** | Real-time ring buffer with persistent JSONL export. |
| **Models Leaderboard** (`#models`) | 4-model comparison matrix (PatchCore vs PaDiM vs AutoEncoder vs FastFlow) | `GET /api/models/comparison`<br/>`GET /api/reports/auroc-matrix` | `BENCHMARK_ARTIFACT` (seeded) / `LIVE_API` | Full Support | **100% PARITY** | Reflects frozen MVTec AD benchmark evaluation ($N=1,725$). |
| **History Browser** (`#history`) | Filterable inspection logs across categories, severity, and verdicts | `GET /api/severity/logs` | `BENCHMARK_ARTIFACT` / `LIVE_API` | Full Support | **100% PARITY** | Paged browser with full search, sorting, and CSV download. |
| **Batch Processing** (`#batch`) | Multi-image batch submission and asynchronous queue polling | `POST /api/batch`<br/>`GET /api/batch/{id}/status`<br/>`GET /api/batch/list` | `LIVE_API` | Full Support | **100% PARITY** | Background workers process batch images and persist `batch_report.json`. |
| **Similarity Explorer** (`#similarity`) | FAISS k-NN nearest-neighbor image retrieval from category gallery | `POST /api/similarity`<br/>`GET /api/similarity/category/{cat}` | `LIVE_API` | Full Support | **100% PARITY** | Queries 384-dimensional EfficientNet embeddings in FAISS `IndexFlatL2`. |
| **RAG Defect Copilot** (`#rag`) | Natural language Q&A and defect triage guidance | `POST /api/rag/ask`<br/>`GET /api/rag/entries` | `LIVE_API` | Full Support | **100% PARITY** | Semantic retrieval using `all-MiniLM-L6-v2` embedding model. |
| **Ask the Data** (`#dashboard`) | Conversational dashboard telemetry queries | `POST /api/dashboard/ask` | `LIVE_API` | Full Support | **100% PARITY** | Natural language queries over inspection database. |
| **Drift Monitor** (`#drift`) | Feature and luminance drift tracking over shifts | `GET /api/drift` | `BENCHMARK_ARTIFACT` / `LIVE_API` | Full Support | **100% PARITY** | Compares baseline distributions against operational inspection window. |
| **RCA & Active Learning** (`#rca`) | Root cause analysis and threshold sensitivity calibration | `POST /api/rca/ask`<br/>`GET /api/active-learning/sensitivity` | `LIVE_API` | Full Support | **100% PARITY** | Simulates FAR/FRR tradeoffs across user-adjusted decision margins. |

---

## 3. Browser & Camera Hardware Nuance

In a local desktop setup, a user might run Python directly interfacing with a USB industrial framegrabber (e.g. via OpenCV `cv2.VideoCapture(0)`).  
In a public cloud architecture:
1. **HTTPS Security Gate:** Browsers strictly block webcam access unless served over secure HTTPS or localhost. The production domain `https://defectvision-ai.vercel.app/` satisfies this requirement.
2. **Client-Side Frame Encoding:** The video stream is captured in the client browser canvas via `navigator.mediaDevices.getUserMedia()`, compressed to JPEG blobs, and transmitted via HTTP POST to `/api/optical-inspection/inspect-frame` at up to 15-30 FPS.
3. **No Direct Server USB Access:** The cloud backend server cannot physically connect to the user's laptop camera. All frame acquisition is mediated by the browser's MediaDevices API. This is the correct, secure, standard production architecture.
