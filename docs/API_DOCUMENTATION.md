# DefectVision AI — REST API Documentation
**Release:** v1.0.0-rc1 (Research Prototype)  
**Date:** 2026-11-19  

---

## 1. Overview & Base URL

The DefectVision AI inspection service exposes a REST API via FastAPI for automated inspection, batch scoring, model health telemetry, and profile management.

- **Base URL:** `http://127.0.0.1:8001`
- **Default Port:** `8001`
- **Content Types:** `application/json`, `multipart/form-data`

---

## 2. API Endpoints

### 2.1 Health Check
- **Endpoint:** `GET /health` or `GET /api/health`
- **Description:** Verifies service availability, resident memory banks, and model readiness.
- **Response (200 OK):**
```json
{
  "status": "ready",
  "process_reachable": true,
  "service": "DefectVision AI — Live Inference Server",
  "version": "3.0.0",
  "device": "cpu",
  "total_categories": 15,
  "ready_category_models_count": 15,
  "all_required_models_ready": true,
  "thresholds_ready": true,
  "categories": ["bottle", "cable", "capsule", "..."],
  "production_profiles": ["bottle_001_station_01", "bottle_sku_btl_adapt_002"]
}
```

---

### 2.2 Model Status
- **Endpoint:** `GET /api/optical-inspection/model-status`
- **Description:** Returns detailed loading status and calibration statistics for each of the 15 category models.
- **Response (200 OK):**
```json
{
  "categories": {
    "bottle": {
      "is_ready": true,
      "status": "READY",
      "category_type": "object",
      "calibrated_threshold": 1.4666,
      "baseline_mean": 0.9732,
      "baseline_p99": 1.4348,
      "tokens": 14739
    }
  },
  "total_categories": 15,
  "all_ready": true
}
```

---

### 2.3 Inspect Single Frame
- **Endpoint:** `POST /api/inspect-frame`
- **Description:** Submits a single image for quality verification, patch feature extraction, anomaly scoring, and heatmap rendering.
- **Request Format:** `multipart/form-data`
  - `file`: Raw image binary (PNG, JPEG, WebP)
  - `category`: Target category (optional; defaults to auto-routing)
  - `profile_id`: Specific production profile ID (optional)
- **Response (200 OK):**
```json
{
  "inspection_id": "insp_20261119_140516",
  "inference_executed": true,
  "heatmap_generated": true,
  "category": "bottle",
  "detected_category": "bottle",
  "category_type": "object",
  "anomaly_score": 1.2869,
  "anomaly_threshold": 1.4666,
  "verdict": "NORMAL",
  "conclusion": "NO DEFECT DETECTED",
  "defect_area_pct": 0.0,
  "confidence_pct": 98.4,
  "heatmap_base64": "data:image/png;base64,iVBORw0KGgo...",
  "inference_latency_ms": 114.2
}
```

---

### 2.4 Auto-Routing Prediction
- **Endpoint:** `POST /predict`
- **Description:** Automatically classifies the incoming specimen via EfficientNet-B0 and executes category-specific PatchCore anomaly scoring.
- **Request Format:** `multipart/form-data` (`file` binary)
- **Response (200 OK):** Contains `predicted_category`, `category_confidence`, `anomaly_score`, `verdict`, and `heatmap_base64`.

---

### 2.5 Batch Inspection
- **Endpoint:** `POST /batch`
- **Description:** Queues multiple specimen images for asynchronous inspection.
- **Request Format:** `multipart/form-data`
  - `files`: Array of image files
  - `category`: Product category
- **Response (200 OK):**
```json
{
  "batch_id": "batch_20261119_141014",
  "status": "QUEUED",
  "submitted_count": 10
}
```
- **Check Status:** `GET /batch/{batch_id}/status`

---

### 2.6 Production Profiles
- **Endpoint:** `GET /api/production-profiles`
- **Description:** Lists all active production and adapted profiles.
- **Endpoint:** `GET /api/production-profiles/{profile_id}`
- **Description:** Retrieves metadata, memory bank parameters, and calibrated threshold for a specific profile.

---

### 2.7 Inspection Audit History
- **Endpoint:** `GET /api/optical-inspection/history`
- **Description:** Retrieves the recent session inspection ring-buffer entries.
- **Endpoint:** `POST /api/optical-inspection/history/clear`
- **Description:** Clears the active session inspection log.

---

## 3. Error Handling & Status Codes

| Code | Status | Description |
|---|---|---|
| `200` | OK | Successful inspection or query. |
| `400` | Bad Request | Corrupted image file or unsupported image encoding. |
| `422` | Unprocessable Entity | Missing required multipart fields or invalid category name. |
| `503` | Service Unavailable | Resident models not loaded or memory bank unavailable. |
