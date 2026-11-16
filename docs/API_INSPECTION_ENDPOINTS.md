# DefectVision AI — Optical Inspection REST API Endpoints

DefectVision AI exposes a unified, high-performance REST API powered by FastAPI. Both image-upload and real-time camera inspection modalities share an identical response contract and inference engine.

Base URL: `http://localhost:8000`
Interactive OpenAPI Docs: `http://localhost:8000/docs`

---

## 1. Unified Response Schema

All inspection endpoints (`/predict`, `/api/optical-inspection/inspect-frame`, `/api/inspect-frame`) return the following structured JSON contract:

```json
{
  "inspection_id": "insp_1794846976178_3776ad",
  "mode": "upload",
  "category": "bottle",
  "detected_category": "bottle",
  "category_type": "object",
  "category_confidence": 0.9984,
  "category_status": "RECOGNIZED",
  "recognition_status": "RECOGNIZED",
  "image_quality": {
    "status": "PASSED",
    "metrics": {
      "resolution": "900x900",
      "sharpness": 84.12,
      "brightness": 136.94,
      "contrast": 93.31
    }
  },
  "model_id": "PatchCore-Bottle-MemoryBank",
  "model_selected": "PatchCore-Bottle-MemoryBank",
  "model_version": "v1.0.0",
  "anomaly_score": 1.1420,
  "anomaly_threshold": 1.4666,
  "calibrated_threshold": 1.4666,
  "optimal_threshold": 1.4666,
  "verdict": "NORMAL",
  "conclusion": "NO DEFECT DETECTED",
  "severity_level": "normal",
  "severity_score": 0.0,
  "defect_area_pct": 0.0,
  "confidence_pct": 99.8,
  "predicted_label": "normal",
  "defect_type": "normal",
  "review_reason": null,
  "diagnosis": "Automated optical inspection of the bottle component identified no significant visual anomalies. The peak anomaly score (1.1420) is strictly below the calibrated decision threshold (1.4666). The result reflects the model's learned visual patterns and does not guarantee the absence of all possible defects.",
  "roi_bbox": [182, 45, 536, 810],
  "original_image": "data:image/jpeg;base64,...",
  "heatmap": "data:image/jpeg;base64,...",
  "heatmap_url": "data:image/jpeg;base64,...",
  "annotated_image_url": "data:image/jpeg;base64,...",
  "raw_heatmap": "data:image/jpeg;base64,...",
  "inference_latency_ms": 78.4,
  "processing_time_ms": 78.4
}
```

---

## 2. Core Inspection Endpoints

### 1. Image Upload Inspection
`POST /predict`

Inspects an uploaded image file. By default, automatically detects the category and selects the corresponding PatchCore model.

**Form Parameters:**
- `file` (UploadFile, required): The image binary (PNG, JPEG, WebP).
- `category` (string, optional, default: `"auto"`): Either `"auto"` for automatic category recognition, or an explicit override from the 15 supported categories (`bottle`, `cable`, `capsule`, `carpet`, `grid`, `hazelnut`, `leather`, `metal_nut`, `pill`, `screw`, `tile`, `toothbrush`, `transistor`, `wood`, `zipper`).

**Example: Automatic Inspection via cURL**
```bash
curl -X POST "http://localhost:8000/predict" \
  -F "file=@sample_bottle.png"
```

**Example: Manual Category Override via cURL**
```bash
curl -X POST "http://localhost:8000/predict" \
  -F "file=@sample_bottle.png" \
  -F "category=bottle"
```

---

### 2. Live Camera Frame Inspection
`POST /api/optical-inspection/inspect-frame`

Processes camera frames streamed from edge devices, industrial sensors, or browser webcam video canvases. Performs in-memory decoding with zero disk I/O.

**Form Parameters:**
- `frame` or `file` (UploadFile, required): Raw frame JPEG/PNG buffer.
- `operator_override` (string, optional, default: `"auto"`): Manual category override or `"auto"`.

**Example: Stream Inspection via JavaScript Fetch**
```javascript
const formData = new FormData();
formData.append('frame', imageBlob, 'frame.jpg');
formData.append('operator_override', 'auto');

const response = await fetch('http://localhost:8000/api/optical-inspection/inspect-frame', {
  method: 'POST',
  body: formData
});
const result = await response.json();
console.log(`Verdict: ${result.verdict} | Conclusion: ${result.conclusion}`);
```

---

### 3. Model Registry & Health Status
`GET /api/optical-inspection/model-status`

Returns the operational deployment status, memory-bank readiness, and calibrated thresholds across all 15 categories.

**Response Example:**
```json
{
  "categories": {
    "bottle": {
      "category": "bottle",
      "type": "object",
      "threshold": 1.4666,
      "margin": 0.1173,
      "is_ready": true,
      "status": "READY"
    },
    "cable": { ... }
  },
  "total_categories": 15,
  "all_ready": true,
  "system_timestamp": "2026-11-16T22:30:00"
}
```

---

### 4. Inspection Audit History
`GET /api/optical-inspection/history`

Retrieves real-time inspection history records and session summary statistics from the in-memory ring buffer.

**Query Parameters:**
- `category` (string, default: `"all"`): Filter by category.
- `verdict` (string, default: `"all"`): Filter by verdict (`NORMAL`, `DEFECTIVE`, `REVIEW REQUIRED`, `UNSUPPORTED`).
- `limit` (integer, default: `40`): Maximum records to retrieve.

**Response Example:**
```json
{
  "records": [ ... ],
  "statistics": {
    "total_inspections": 128,
    "verdict_counts": {
      "NORMAL": 94,
      "DEFECTIVE": 26,
      "REVIEW REQUIRED": 7,
      "UNSUPPORTED": 1
    },
    "defect_rate_pct": 20.31,
    "mean_latency_ms": 84.6
  }
}
```

---

### 5. Clear Inspection Audit History
`POST /api/optical-inspection/history/clear`

Resets the in-memory inspection history buffer.

**Response Example:**
```json
{
  "status": "cleared",
  "message": "Optical inspection history cleared successfully."
}
```

---

### 6. Supported Categories & Metadata
`GET /api/optical-inspection/categories`

Returns the list of all 15 supported categories and their configuration metadata (domain type, calibrated threshold, ROI mode).
