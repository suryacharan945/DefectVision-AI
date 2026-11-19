# DefectVision AI — API Integration & Route Matrix Report

**Document Version:** 3.0.0  
**Date:** November 2026  
**Service:** Persistent FastAPI Inference Server (`DefectVisionAI/app.py`)  
**Specification:** Full-Stack API Contract & Operational Verification  

---

## 1. Architectural Route Contract

All endpoints support dual routing: canonical routes prefixed with `/api/` (standardized for reverse proxies, API gateways, and frontend CDNs) alongside legacy non-prefixed routes for backward compatibility.

| Canonical Endpoint | Legacy Alias | HTTP Method | Auth / Access | Resident Subsystem |
| :--- | :--- | :--- | :--- | :--- |
| `/api/ready` | `/ready` | `GET` | Public | System Health Monitor |
| `/api/health` | `/health` | `GET` | Public | System Health Monitor |
| `/api/predict` | `/predict` | `POST` | Public | Optical Engine / PatchCore / EffNet |
| `/api/batch` | `/batch` | `POST` | Public | Batch Optical Inspector |
| `/api/optical-inspection/inspect-frame` | `/optical-inspection/inspect-frame` | `POST` | Public | Real-Time Video Engine |
| `/api/optical-inspection/model-status` | `/optical-inspection/model-status` | `GET` | Public | 15-Category Baseline Engine |
| `/api/optical-inspection/history` | `/optical-inspection/history` | `GET` | Public | Telemetry History Service |
| `/api/optical-inspection/history/clear` | `/optical-inspection/history/clear` | `POST` | Public | Telemetry History Service |
| `/api/production-profiles` | `/production-profiles` | `GET` | Public | Production Profile Service |
| `/api/production-profiles/{profile_id}` | `/production-profiles/{profile_id}` | `GET` | Public | Production Profile Service |
| `/api/production-profiles/adapt` | `/production-profiles/adapt` | `POST` | Public | Few-Shot Adaptation Engine |
| `/api/production-profiles/{id}/activate` | `/production-profiles/{id}/activate` | `POST` | Public | Production Profile Service |
| `/api/production-profiles/{id}/deactivate` | `/production-profiles/{id}/deactivate` | `POST` | Public | Production Profile Service |
| `/api/production-profiles/{id}/archive` | `/production-profiles/{id}/archive` | `POST` | Public | Production Profile Service |
| `/api/production-profiles/{id}/evaluate` | `/production-profiles/{id}/evaluate` | `POST` | Public | Profile Evaluation Suite |
| `/api/production-profiles/{id}/update-references` | `/production-profiles/{id}/update-references` | `POST` | Public | Dynamic Coreset Updater |
| `/api/models/comparison` | `/models/comparison` | `GET` | Public | Analytics & Model Benchmarks |
| `/api/reports/summary` | `/reports/summary` | `GET` | Public | Validation Metrics Exporter |

---

## 2. Core Endpoint Schemas

### 2.1 Readiness Probe: `GET /api/ready`

**Request:** `GET http://127.0.0.1:8001/api/ready`  
**HTTP Status:** `200 OK` (when operational) or `503 Service Unavailable` (if any category model failed)  
**Response Payload:**
```json
{
  "status": "ready",
  "process_reachable": true,
  "service": "DefectVision AI — Live Inference Server",
  "version": "3.0.0",
  "backend_version": "3.0.0",
  "model_version": "v1.0.0-rc1",
  "device": "cpu",
  "optical_engine_initialized": true,
  "optical_engine_ready": true,
  "classifier_ready": true,
  "total_categories": 15,
  "total_supported_categories": 15,
  "ready_category_models_count": 15,
  "all_required_models_ready": true,
  "thresholds_ready": true,
  "faiss_indexes_loaded": 15,
  "profile_storage_writable": true,
  "model_loading_failures": [],
  "categories": [
    "bottle", "cable", "capsule", "carpet", "grid",
    "hazelnut", "leather", "metal_nut", "pill", "screw",
    "tile", "toothbrush", "transistor", "wood", "zipper"
  ],
  "categories_status": {
    "bottle": true, "cable": true, "capsule": true, "carpet": true, "grid": true,
    "hazelnut": true, "leather": true, "metal_nut": true, "pill": true, "screw": true,
    "tile": true, "toothbrush": true, "transistor": true, "wood": true, "zipper": true
  },
  "production_profiles_count": 2,
  "production_profiles": [
    "bottle_001_station_01",
    "bottle_sku_btl_adapt_002"
  ],
  "llm_loaded": false,
  "engine_error": null,
  "timestamp": "2026-11-19T16:06:28.113640+00:00"
}
```

---

### 2.2 Live Optical Frame Inspection: `POST /api/optical-inspection/inspect-frame`

**Request:** `multipart/form-data`
- `file`: Raw image binary (JPEG/PNG)
- `category`: Category name (e.g., `"bottle"`) or `"auto"`
- `profile_id` (optional): Production profile identifier (e.g., `"bottle_001_station_01"`)

**Response Payload (Nominal Normal Specimen):**
```json
{
  "verdict": "NORMAL",
  "anomaly_score": 1.1245,
  "decision_threshold": 1.4666,
  "detected_category": "bottle",
  "category_type": "object",
  "quality_gate": {
    "passed": true,
    "blur_score": 384.2,
    "exposure_mean": 128.4,
    "rejection_stage": null
  },
  "roi_coordinates": [120, 80, 480, 560],
  "masking_applied": true,
  "foreground_ratio": 0.42,
  "defect_area_percentage": 0.0,
  "confidence_percentage": 94.8,
  "heatmap_base64": null,
  "processing_latency_ms": 78.4,
  "inspection_id": "insp_1795102179930",
  "timestamp": "2026-11-19T16:08:20.124500Z"
}
```

**Response Payload (Optical Quality Gate Failure — Defocused / Underexposed):**
```json
{
  "verdict": "REVIEW REQUIRED",
  "anomaly_score": null,
  "decision_threshold": 1.4666,
  "detected_category": "bottle",
  "category_type": "object",
  "quality_gate": {
    "passed": false,
    "blur_score": 42.1,
    "blur_threshold": 100.0,
    "exposure_mean": 18.2,
    "rejection_stage": "blur_check",
    "rejection_reason": "Specimen blurred: Laplacian variance (42.1) below minimum sharpness threshold (100.0)."
  },
  "roi_coordinates": null,
  "masking_applied": false,
  "defect_area_percentage": 0.0,
  "confidence_percentage": 0.0,
  "heatmap_base64": null,
  "processing_latency_ms": 14.2,
  "inspection_id": "insp_1795102181044",
  "timestamp": "2026-11-19T16:08:21.044100Z"
}
```

---

### 2.3 Production Profile Adaptation: `POST /api/production-profiles/adapt`

**Purpose:** Executes few-shot PatchCore adaptation on user-uploaded normal reference specimens.  
**Request:** `multipart/form-data`
- `reference_files`: 5-25 normal specimen images
- `product_name`: Clear Glass Bottle 500ml
- `sku`: SKU-BTL-002
- `category`: bottle
- `target_far`: 0.01

**Operational Contract:**
- Validates minimum normal specimen count ($K \ge 5$).
- Executes greedy k-Center Coreset selection ($M \le 2000$ patch vectors).
- Generates provisional calibrated threshold from held-out normal calibration split.
- Writes cryptographic SHA-256 hashes to `manifest.json`.
- Disclaims provisional status if sample size is insufficient for certified FAR.
