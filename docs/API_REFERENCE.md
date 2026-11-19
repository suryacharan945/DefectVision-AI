# DefectVision AI — REST API Reference

The DefectVision AI backend exposes high-performance REST endpoints for live optical inspection, product adaptation, model analytics, and system monitoring.

Base URL: `http://localhost:8001`

---

## 1. Optical Inspection Endpoints

### `POST /api/optical-inspection/frame`
Executes end-to-end optical inspection on a single frame.

**Form Parameters:**
- `frame` (binary, required): JPEG/PNG encoded image file.
- `operator_override` (string, optional): One of the 15 categories (e.g. `bottle`), or `auto` for autonomous recognition.
- `profile_id` (string, optional): Specific production profile ID (e.g. `bottle_001_station_01`).
- `routing_mode` (string, optional): `benchmark`, `production`, or `universal`.

**Response (200 OK):**
```json
{
  "inspection_id": "insp_01933a01-2a14-7e77-8c10-...",
  "verdict": "NORMAL",
  "conclusion": "NO DEFECT DETECTED",
  "category": "bottle",
  "anomaly_score": 0.6912,
  "calibrated_threshold": 0.8333,
  "foreground_detected": true,
  "foreground_masking_applied": true,
  "foreground_mask_validity": "VALID",
  "foreground_coverage_pct": 34.2,
  "connected_components_count": 1,
  "heatmap_url": "data:image/jpeg;base64,...",
  "inference_latency_ms": 44.5,
  "processing_time_ms": 78.2
}
```

---

## 2. Product Profile & Adaptation Endpoints

### `GET /api/production-profiles`
Returns metadata summaries for all registered production profiles.

### `GET /api/production-profiles/{profile_id}`
Returns the full configuration specification (`profile.json`).

### `GET /api/production-profiles/{profile_id}/analytics`
Returns deep statistical distribution metrics ($p_{50}, p_{90}, p_{99}$), memory-bank vector counts, FAISS dimensions, and SHA-256 artifact hashes.

### `POST /api/production-profiles/adapt`
Builds and registers a new adapted profile from normal reference images.

**Form Parameters:**
- `product_name` (string, required): Human-readable product name.
- `sku` (string, required): Product SKU.
- `category` (string, default: `bottle`): Parent MVTec category.
- `camera_id` (string, default: `CAM-EXT-01`): Camera identifier.
- `lighting_profile` (string, default: `ambient_or_diffuse`): Illumination type.
- `calibration_split_ratio` (float, default: `0.30`): Fraction reserved for threshold calibration.
- `coreset_ratio` (float, default: `0.10`): Memory bank coreset compression ratio.
- `files` (array of binary images, required): At least 2 normal images.

### `POST /api/production-profiles/{profile_id}/activate`
Activates profile for live inspection routing.

### `POST /api/production-profiles/{profile_id}/deactivate`
Deactivates profile (temporarily suspended from routing).

### `POST /api/production-profiles/{profile_id}/archive`
Archives profile and unloads its FAISS index from RAM.

### `PUT /api/production-profiles/{profile_id}`
Updates editable metadata fields (product name, station, lighting, thresholds).

### `POST /api/production-profiles/{profile_id}/evaluate`
Runs empirical batch evaluation on test images with ground-truth labels.

### `DELETE /api/production-profiles/{profile_id}`
Permanently deletes profile files and unloads the model from RAM.

---

## 3. System Health & Readiness Endpoints

### `GET /api/ready` (or `/ready`)
Production readiness probe verifying resident model memory. Returns HTTP 200 when all 15 category models, calibrated thresholds, and FAISS indices are resident in RAM; returns HTTP 503 if any model failed to load.

```json
{
  "status": "ready",
  "process_reachable": true,
  "service": "DefectVision AI — Live Inference Server",
  "backend_version": "3.0.0",
  "model_version": "v1.0.0-rc1",
  "device": "cpu",
  "total_supported_categories": 15,
  "ready_category_models_count": 15,
  "all_required_models_ready": true,
  "thresholds_ready": true,
  "faiss_indexes_loaded": 15,
  "profile_storage_writable": true,
  "model_loading_failures": [],
  "categories_status": {
    "bottle": true, "cable": true, "capsule": true, "carpet": true, "grid": true,
    "hazelnut": true, "leather": true, "metal_nut": true, "pill": true, "screw": true,
    "tile": true, "toothbrush": true, "transistor": true, "wood": true, "zipper": true
  },
  "production_profiles_count": 2,
  "production_profiles": [
    "bottle_001_station_01",
    "bottle_sku_btl_adapt_002"
  ]
}
```

### `GET /api/health` (or `/health`)
Liveness probe indicating process reachability and subsystem status.

---

## 4. Optical Inspection History & Status

### `GET /api/optical-inspection/model-status`
Returns baseline statistics, token counts, and calibrated thresholds across all 15 categories.

### `GET /api/optical-inspection/history`
Returns real-time session inspection records and statistics.

For comprehensive route matrices and integration details, consult [`release/production_upgrade/API_INTEGRATION_REPORT.md`](../release/production_upgrade/API_INTEGRATION_REPORT.md).
