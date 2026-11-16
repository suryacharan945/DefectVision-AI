# DefectVision AI — Public Repository File Manifest & Component Audit

**Document Version:** 1.0.0  
**Audit Date:** November 1, 2026  
**Auditor:** Release Engineering & Repository Hygiene Gatekeeper  
**Target Commit:** `7a4a2d3` / HEAD  
**Total Tracked Files in HEAD:** 5,020  

---

## 1. Executive Summary & Verification Checklist

This document provides a comprehensive structural manifest of all files currently tracked by Git at commit `7a4a2d3`. 

### 1.1 Mandatory Publication Checklist Verification

| Requirement | Audit Standard | Verification Status | Artifact Reference |
|:---|:---|:---:|:---|
| **Permissive License** | Root `LICENSE` present (MIT License) | **VERIFIED** | [`LICENSE`](file:///C:/Users/surya/Downloads/Mini%20Project/LICENSE) |
| **Comprehensive README** | Architecture, quickstart, features, benchmarks | **VERIFIED** | [`README.md`](file:///C:/Users/surya/Downloads/Mini%20Project/README.md) |
| **Installation Guide** | Clean setup for Windows, Linux, macOS | **VERIFIED** | [`REPRODUCIBILITY.md`](file:///C:/Users/surya/Downloads/Mini%20Project/REPRODUCIBILITY.md) & [`CLEAN_INSTALL_VERIFICATION.md`](file:///C:/Users/surya/Downloads/Mini%20Project/release/final_integrity_gate/CLEAN_INSTALL_VERIFICATION.md) |
| **Model & Data Attribution** | Detailed provenance, MVTec/VisA citations | **VERIFIED** | [`DATASET_PROVENANCE.md`](file:///C:/Users/surya/Downloads/Mini%20Project/DATASET_PROVENANCE.md) & [`MODEL_CARD.md`](file:///C:/Users/surya/Downloads/Mini%20Project/MODEL_CARD.md) |
| **Research Limitations** | Operational domain boundaries & risks | **VERIFIED** | [`LIMITATIONS.md`](file:///C:/Users/surya/Downloads/Mini%20Project/LIMITATIONS.md) |
| **Grounded Metrics** | Traceable experimental numbers | **VERIFIED** | [`METRIC_CLAIM_SOURCE_MATRIX.csv`](file:///C:/Users/surya/Downloads/Mini%20Project/release/final_integrity_gate/METRIC_CLAIM_SOURCE_MATRIX.csv) |
| **Redistribution Governance** | Derivative weights audited & labeled | **VERIFIED** | [`MODEL_REDISTRIBUTION_MATRIX.csv`](file:///C:/Users/surya/Downloads/Mini%20Project/release/publication_preflight/MODEL_REDISTRIBUTION_MATRIX.csv) |
| **Zero Leaked Secrets** | Zero API keys, private tokens, passwords | **VERIFIED** | [`SECRET_SCAN_SUMMARY.md`](file:///C:/Users/surya/Downloads/Mini%20Project/release/final_integrity_gate/SECRET_SCAN_SUMMARY.md) |

---

## 2. High-Level Repository Composition

The 5,020 tracked files partition into four distinct functional tiers:

```
Total Tracked Repository Assets (N = 5,020)
|
+--- [ Tier 1: Core Code, Docs & Configs ] ------ 354 files (MIT Application & Governance)
|
+--- [ Tier 2: Precomputed Model Weights ] ------ 151 files (Memory Banks, Checkpoints & FAISS)
|
+--- [ Tier 3: Dataset Masks & Specimen Samples ] - 63 files (33 MVTec Masks + 30 Demo PNGs)
|
+--- [ Tier 4: Offline Evaluation Heatmaps ] ---- 4,452 files (Historical Validation Overlays)
```

### 2.1 File Extension Inventory

| Extension | Count | Description / Role |
|:---|:---:|:---|
| `.png` | 4,555 | Evaluation heatmaps (4,452), sample crops (30), MVTec masks (33), UI assets (40) |
| `.md` | 90 | Architectural guides, research protocols, audit logs, and case studies |
| `.csv` | 77 | Datasets logs, metric sweeps, decision traces, and domain failure knowledge base |
| `.json` | 69 | Protocol specifications, metadata schemas, baseline lookups, and demo batches |
| `.py` | 66 | FastAPI backend (`app.py`), modules (`src/`), test harnesses, and audit scripts |
| `.pt` / `.pth` | 40 | PyTorch model checkpoints (EfficientNet, Autoencoders) |
| `.npz` | 32 | PaDiM Gaussian parameter archives and drift reference distributions |
| `.jsx` / `.js` | 24 | React operator console components, API client, and Three.js 3D viewport |
| `.npy` | 17 | PatchCore coreset memory banks (15 categories) |
| `.faiss` | 15 | FAISS FlatL2 binary index galleries |
| `.flag` | 15 | Pipeline sentinel flags |
| `.svg` / `.css` | 6 | Icons, Tailwind stylesheets |
| Other Configs | 14 | `LICENSE`, `.gitignore`, `package.json`, `requirements.txt`, `start_defectvision.bat` |
| **Total** | **5,020** | **Full Git Tree at HEAD** |

---

## 3. Granular Component Directory Breakdown

### 3.1 Tier 1: Application Source Code & Documentation (354 Files)
* **Root Documentation (11 files):**
  - `README.md`, `ARCHITECTURE.md`, `MODEL_CARD.md`, `DATASET_PROVENANCE.md`, `SECURITY.md`, `LIMITATIONS.md`, `DEMO_GUIDE.md`, `REPRODUCIBILITY.md`, `LICENSE`, `package.json`, `requirements.txt`.
* **Backend Source Code (`DefectVisionAI/src/` & `DefectVisionAI/`, 22 files):**
  - `app.py`: FastAPI server with live inference routing, batch processing, and RAG copilot.
  - `src/patchcore.py`: Unsupervised feature extraction and nearest-neighbor distance scoring.
  - `src/severity.py`: Multi-factor severity score and ASTM/ISO grade bucketing.
  - `src/similarity.py`: FAISS-CPU similarity search and nearest exemplar gallery retrieval.
  - `src/rag_assistant.py`: Semantic failure analysis and engineering recommendations.
  - `src/batch_inspection.py`: Asynchronous production lot worker and escape rate estimation.
* **Frontend Web Console (`frontend/src/`, 36 files):**
  - React 19 operator console with Tailwind CSS v4, Lucide icons, and Three.js 3D canvas.
  - `frontend/src/api/client.js`: Unified API client supporting live inference and transparent client-side demo simulation.
  - `frontend/src/data/`: Static fallback inspection batches and severity audit logs.
* **Verification & Test Harnesses (`tests/` & `scripts/`, 45 files):**
  - 22 Python unit tests (`tests/test_cpnd.py`, `tests/test_density_norm_cpnd.py`, `tests/test_vision_reports.py`).
  - End-to-end integration and safety test scripts (`scripts/`).
* **Research Documentation & Protocol Audits (`research/`, 160 files):**
  - Prospective experiment protocols (`Q1_EXPERIMENT_PROTOCOL_V1.json`, `V2.json`).
  - Phase 7A VisA exposure audit and conformal review.
  - Phase 7B/7C CPND implementation and density-normalization stop decision.
  - Phase 8A/8B/8C MACBA knapsack problem formulation and Chow (1970) equivalence proof.
  - Phase 9A research reset and publication path assessment.
* **Release Governance Suites (`release/`, 20 files):**
  - `release/open_source_readiness/`: Technical case study, interview guide, release checklist.
  - `release/final_integrity_gate/`: Reconciled exposure matrix, metric source matrix, test reclassification.
  - `release/publication_preflight/`: Redistribution matrix, Git history audit, tag audit.

### 3.2 Tier 2: Model Artifacts Tracked in Git (`DefectVisionAI/models/`, 151 Files)
* **PatchCore Memory Banks (15 files):** `models/patchcore/<category>/memory_bank.npy` (6.5MB–42.3MB).
* **PaDiM Models (16 files):** `models/padim/<category>/padim_model.npz` (30.2MB each) + `padim_model.npz` (28.1MB).
* **Autoencoder Baselines (30 files):** `models/autoencoder/<category>/{best_model.pt, last_checkpoint.pt}`.
* **EfficientNet Checkpoints (7 files):** `models/efficientnet_baseline*/{best_model.pt, last_checkpoint.pt}`, `checkpoint.pth`.
* **FAISS Indexes (15 files):** `models/faiss_index/<category>/index.faiss`.
* **Drift Distributions (16 files):** `models/drift_reference/<category>_reference.npz`, `efficientnet_normal_distribution.npz`.
* **Metadata & Configs (52 files):** `models/faiss_index/<category>/metadata.json`, `models/rag_knowledge_base/defect_knowledge_base.csv`, `padim_threshold.json`, `training_history.csv`, `DONE.flag`.

### 3.3 Tier 3: Dataset Masks & Specimen Samples (63 Files)
* **MVTec Ground Truth Masks (33 files):** `DefectVisionAI/dataset/raw/mvtec/bottle/ground_truth/{broken_large, broken_small}/*_mask.png`.
* **Backend Sample Images (15 files):** `DefectVisionAI/outputs/similarity_search_samples/<category>_similarity_demo.png`.
* **Frontend Sample Images (15 files):** `frontend/public/outputs/similarity_search_samples/<category>_similarity_demo.png`.

### 3.4 Tier 4: Offline Evaluation Heatmaps (`DefectVisionAI/outputs/`, 4,452 Files)
* `autoencoder_heatmaps/`: 1,723 PNG files.
* `padim_heatmaps/`: 1,693 PNG files.
* `gradcam/`: 815 PNG files.
* `patchcore_heatmaps/`: 221 PNG files.
* Performance summary plots & active learning charts: 7 PNG files.

---

## 4. Manifest Integrity Verdict

The repository manifest confirms that all source code, unit tests, frontend assets, governance documentation, and empirical audit data are fully tracked and synchronized. 

The public repository file manifest is **COMPLETE & ACCURATE**.
