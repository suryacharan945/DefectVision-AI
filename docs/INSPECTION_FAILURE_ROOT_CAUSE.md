# DefectVision AI — Comprehensive Root Cause Analysis of Inspection Failures

**Document Status:** Complete & Verified  
**Affected Branch:** `feature/realtime-category-inspection`  
**Reference Cases:** Case A (Normal Bottle False Critical Alarm) & Case B (Ceiling Fan Incorrect Recognition)

---

## 1. Executive Summary

A critical diagnostic audit of the DefectVision AI application was conducted to isolate and eliminate two verified production anomalies:
1. **Case A (False Critical Defect on Nominal Bottle):** A pristine, defect-free transparent bottle was classified as `DEFECTIVE` with semantic description `"Sidewall Structural Fracture"`, severity `"Critical (94.0)"`, confidence `99.7%`, defect area `5.6%`, and a PatchCore heatmap showing repeated circular artifacts.
2. **Case B (Ceiling Fan Misclassified as Bottle):** Pointing a live camera at a non-industrial object (ceiling fan) routed the frame to `PatchCore-Bottle-MemoryBank`, returning `DEFECTIVE`, severity `"Critical (86.4)"`, and anomaly score `0.835`, instead of rejecting the item as unsupported.

Our investigation revealed a **compound failure architecture** operating simultaneously at three decoupled layers:
1. **Frontend Proxy Routing Failure:** `frontend/vite.config.js` stripped the `/api` prefix from incoming `/api/optical-inspection/inspect-frame` requests. Because FastAPI endpoints were registered with `/api/...`, calls returned `404 Not Found`.
2. **Deceptive Client-Side Fallback Simulation:** In `frontend/src/api/client.js`, catch blocks caught the 404 response and served synthetic hardcoded mock dictionaries that fabricated `"Sidewall Structural Fracture"`, `severityScore: 94.0` / `86.4`, and injected a static circular pattern sample image (`bottle_similarity_demo.png`).
3. **Flawed Anomaly Normalization in Core Backend:** Even when the backend was called directly, PatchCore distance maps were self-normalized using `(m - m.min()) / m.max()`. Normal background noise on a pristine bottle was scaled to 1.0 (bright red), driving defect area to **75.77%** and inflating severity score to **76.69**. Furthermore, standard Softmax classification lacked feature prototype and energy constraints, permitting out-of-distribution inputs to falsely enter category models.

---

## 2. Case A: Detailed Root Cause Analysis

### 2.1 The Frontend Trigger: Vite Proxy 404 and Deceptive Fallback
In `frontend/vite.config.js`:
```javascript
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''), // Stripped /api!
      },
```
When `api.predict(file)` or `api.inspectOpticalFrame(blob)` called `/api/optical-inspection/inspect-frame`:
- Vite forwarded the request to `http://127.0.0.1:8000/optical-inspection/inspect-frame`.
- FastAPI had only registered `@app.post("/api/optical-inspection/inspect-frame")`.
- The request immediately failed with HTTP 404.

In `frontend/src/api/client.js` (lines 40-56 and 193-224):
```javascript
const defaultDefectTypes = {
  bottle: 'Sidewall Structural Fracture', // Hardcoded physical claim
  cable: 'Deformed Core Wire',
  ...
};
...
const defectType = defaultDefectTypes[cat] || 'Surface Anomaly';
const anomalyScore = Math.min(0.95, Math.max(0.65, 0.78 + (Math.cos(cat.length) * 0.12)));
const severityScore = Math.min(96, Math.max(72, Math.round(anomalyScore * 105))); // Evaluates to 94.0!
const confidence = 98.6 + Math.round(Math.random() * 12) / 10;                     // Evaluates to 99.7%!
const defectArea = (3.5 + Math.round(Math.random() * 45) / 10).toFixed(1);          // Evaluates to 5.6%!
const sampleImgUrl = `/outputs/similarity_search_samples/${cat}_similarity_demo.png`;
```
This hardcoded simulation produced the exact symptom reported in Case A:
- Category: Bottle
- Verdict: Defective Specimen
- Defect: Sidewall Structural Fracture
- Severity: Critical (94.0)
- Confidence: 99.7%
- Defect Area: 5.6%
- Heatmap: `/outputs/similarity_search_samples/bottle_similarity_demo.png` (which contains static circular rings).

### 2.2 The Backend Flaw: Local Min-Max Distance Normalization
When the real backend was executed on `bottle/test/good/000.png`:
```
PatchCore distances across 28x28 grid:
min: 0.0278, max: 1.2869, mean: 0.7587, calibrated_threshold: 1.4666
```
Because `max (1.2869) < calibrated_threshold (1.4666)`, the specimen was **100% nominal**. Not a single patch was defective.

However, `src/patchcore.py` executed:
```python
def normalize_map(m):
    m = m - m.min()
    if m.max() > 0:
        m = m / m.max()
    return m
```
This forced the distance map to stretch locally over $[0.0, 1.0]$. The median patch score (0.81) scaled to:
$$\frac{0.8103 - 0.0278}{1.2869 - 0.0278} = 0.621$$
In `src/camera_service.py:361`:
```python
defect_area_pct = float(100.0 * (dist_map_norm >= 0.5).sum() / dist_map_norm.size)
```
Because $0.621 > 0.5$, normal background noise was classified as anomalous surface area, falsely reporting **75.77% defect area** on a pristine bottle!

Furthermore, `src/severity.py` fused category classification confidence into defect severity:
```python
score = (0.5 * anomaly_norm) + (0.3 * defect_area_pct) + (0.2 * confidence_pct)
```
With `defect_area_pct = 75.77` and `confidence_pct = 99.2%`, the severity score was pushed to **76.69**, classifying a nominal bottle as Critical!

---

## 3. Case B: Detailed Root Cause Analysis

### 3.1 Unbounded Default in Camera Stream Simulation
In `frontend/src/pages/LiveStreamInspector.jsx:307`:
```javascript
if (!frameBlob) {
  const sampleRes = await fetch(`/outputs/similarity_search_samples/bottle_similarity_demo.png`);
  if (sampleRes.ok) {
    frameBlob = await sampleRes.blob(); // Injected bottle image if camera was dark/unreadable!
  }
}
```
And in `frontend/src/api/client.js:658-678`:
```javascript
const cat = String(category || 'bottle').toLowerCase();
return {
  verdict: 'DEFECTIVE',
  detected_category: cat, // Evaluated to 'bottle'
  model_selected: 'PatchCore-Bottle-MemoryBank',
  severity_level: 'Critical',
  severity_score: 86.4,   // Exact match to Case B!
  anomaly_score: 0.835,   // Exact match to Case B!
  heatmap_base64: sampleImgUrl
};
```
When live camera stream inspection failed to resolve or reached the catch block, it defaulted to `bottle`, emitting `PatchCore-Bottle-MemoryBank`, `Critical (86.4)`, and `0.835`.

### 3.2 Deep Classifier Softmax Overconfidence on OOD Inputs
In deep neural networks trained with cross-entropy loss, softmax probability distributions often collapse onto an arbitrary known class when exposed to out-of-distribution inputs (e.g., ceiling fan, chairs, uniform colors, noise).

In our baseline evaluation:
- Random uniform noise produced a leather softmax probability of **0.748**.
- Uniform solid black produced a leather softmax probability of **0.915**.
- Uniform solid white produced a leather softmax probability of **0.823**.

Because the classifier only checked `top_prob >= 0.70` and `entropy < 0.65`, unconstrained softmax allowed non-industrial and arbitrary objects to pass through into category-specific PatchCore memory banks!

---

## 4. Architectural Remediation Summary

| Component | Defect Mechanism | Permanent Resolution |
| :--- | :--- | :--- |
| `frontend/vite.config.js` | Path rewrite stripped `/api`, triggering 404 | Removed `/api` rewrite; added dual backend route decorators in `app.py`. |
| `frontend/src/api/client.js` | Hardcoded `"Sidewall Structural Fracture"`, `94.0`, `86.4` | Removed fake defect dictionary and misleading fallbacks; replaced with honest offline telemetry. |
| `frontend/src/pages/LiveStreamInspector.jsx` | Injected `bottle_similarity_demo.png` on null frame | Removed fallback fetch; cleanly raises camera acquisition errors. |
| `src/patchcore.py` | Local min-max normalization inflated noise to red | Implemented `calibrate_score_map` anchored to category calibrated threshold $\tau$. |
| `src/camera_service.py` | `dist_map_norm >= 0.5` reported 75.77% defect area | Defect area now counted strictly where smoothed distance $\ge \tau$. Normal bottles report 0.00%. |
| `src/severity.py` | Confidence added 20 points to severity | Decoupled classification confidence from severity; normal specimens strictly return 0.0 severity. |
| `src/category_classifier.py` | Softmax overconfidence on OOD objects | Implemented 4-criterion OOD gating: Softmax, Shannon Entropy, Free Energy ($E \le -6.50$), Prototype Cosine Similarity ($\ge 0.65$). |
