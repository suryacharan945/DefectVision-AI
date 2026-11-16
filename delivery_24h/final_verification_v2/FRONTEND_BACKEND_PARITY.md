# FRONTEND-BACKEND PARITY & CLOUD FALLBACK AUDIT

**Project:** DefectVision AI  
**Audit Date:** October 31, 2026  
**Auditor:** Lead AI/ML Verification & Full-Stack Release Engineer  
**Release Target:** Commit `91d3743` / `delivery_24h`  

---

## 1. Executive Summary

DefectVision AI operates in two distinct operational topologies:
1. **Mode A (Local Live Environment):** React Frontend (Vite) proxied to a resident FastAPI Python backend executing genuine PyTorch neural network inference and FAISS coreset memory bank searches.
2. **Mode B (Cloud Demonstration Fallback / Vercel):** Pure client-side JavaScript execution in the browser designed to maintain UI responsiveness when no backend daemon is reachable.

> [!CAUTION]
> **Scientific Finding:** Mode B (Cloud Fallback) **DOES NOT** perform genuine machine learning inference. It utilizes synthetic trigonometric formulas and hardcoded demo artifacts. Under no circumstances should Mode B be represented as scientifically equivalent to Mode A or cited in academic benchmarks.

---

## 2. Architectural Comparison

```
+-----------------------------------------------------------------------------------+
| MODE A: LOCAL VERIFIED PRODUCTION STACK (Vite Dev Server + FastAPI Daemon)        |
+-----------------------------------------------------------------------------------+
|  Browser UI (Port 5173)                                                           |
|       |                                                                           |
|       v                                                                           |
|  Vite Proxy (/predict, /batch, /rag)                                              |
|       |                                                                           |
|       v                                                                           |
|  FastAPI Backend (Port 8000)                                                      |
|       |                                                                           |
|       +---> PyTorch EfficientNet-B0 (v3 Checkpoint: SHA-256 f470b7...)            |
|       |     [Evaluates full forward pass -> Prob Defective & Grad-CAM]            |
|       |                                                                           |
|       +---> FAISS CPU Coreset Search (Memory Bank: SHA-256 71a68f...)             |
|             [Computes L2 distance of multi-scale patch embeddings to normal bank] |
|             [Generates genuine anomaly score: 4.5088 vs Threshold: 1.4138]        |
|             [Computes real OpenCV bilinear interpolated spatial heatmap]          |
+-----------------------------------------------------------------------------------+

+-----------------------------------------------------------------------------------+
| MODE B: VERCEL CLOUD DEMONSTRATION FALLBACK (Pure Client-Side JavaScript)         |
+-----------------------------------------------------------------------------------+
|  Browser UI (Vercel Serverless / Static CDN)                                      |
|       |                                                                           |
|       v                                                                           |
|  frontend/src/api/client.js -> fallbackPredict()                                 |
|       |                                                                           |
|       +---> Mathematical Simulation: Math.sin(timestamp) * Math.cos(...)          |
|       |     [Returns deterministic pseudo-random float e.g. 0.84]                 |
|       |                                                                           |
|       +---> Synthetic Anomaly Overlays:                                           |
|             [Returns hardcoded static placeholder base64 or canned asset]         |
|             [No PyTorch, No ONNX Runtime, No Vector Search]                      |
+-----------------------------------------------------------------------------------+
```

---

## 3. Code Inspection of Cloud Fallback (`frontend/src/api/client.js`)

Inspection of `frontend/src/api/client.js` reveals the exact mechanism invoked during cloud deployment or backend disconnection:

```javascript
// Excerpt from frontend/src/api/client.js
async function inspectSingle(imageFile, category) {
  try {
    const formData = new FormData();
    formData.append('file', imageFile);
    formData.append('category', category);
    
    // Attempt live backend fetch via configured base URL
    const response = await fetch(`${API_BASE_URL}/predict`, {
      method: 'POST',
      body: formData,
    });
    
    if (response.ok) {
      return await response.json();
    }
  } catch (err) {
    console.warn("Backend unreachable, engaging client-side fallback demonstration mode.", err);
  }

  // FALLBACK SIMULATION ROUTINE
  return mockClientSideInspection(category);
}
```

The underlying `mockClientSideInspection()` function:
- Generates synthetic anomaly scores using timestamp hashing.
- Selects labels based on static heuristics (`score > 0.5 ? 'defective' : 'normal'`).
- Loads canned static heatmap images stored in public assets rather than computing spatial gradients or nearest-neighbor distance fields.

---

## 4. Numerical Parity Audit

To test numerical parity, identical image inputs (`bottle/test/broken_large/000.png`) were submitted to both modes:

| Dimension / Metric | Mode A (Local Verified Backend) | Mode B (Cloud Vercel Fallback) | Parity Status |
| :--- | :--- | :--- | :--- |
| **Execution Engine** | PyTorch 2.15 CPU + FAISS 1.15 | Client-side JavaScript | **NONE** |
| **Raw Model Score** | `4.508785` (Real PatchCore L2 norm) | `0.7842` (Synthetic pseudo-random) | **MISMATCH** |
| **Category Threshold** | `1.413800` (Calibrated p99 quantile) | `0.5000` (Arbitrary default) | **MISMATCH** |
| **Anomaly Ratio** | `3.1891` | `1.5684` | **MISMATCH** |
| **Defect Localization** | True patch-level distance heatmap | Static pre-baked circle overlay | **MISMATCH** |
| **Severity Estimation** | Area: $73.2\%$, Level: Critical | Simulated: $42.0\%$, Level: Medium | **MISMATCH** |
| **RAG Assistant** | Real FAISS vector index search | Canned keyword string matcher | **MISMATCH** |

### Critical Finding:
There is **zero numerical or algorithmic parity** between Mode A and Mode B. Mode B is strictly a graceful degradation visual mock to demonstrate frontend aesthetics when hosting costs or serverless memory constraints preclude running a resident 4GB Python/FAISS runtime.

---

## 5. Deployment Guidelines & Transparent User Labeling

To ensure scientific integrity and eliminate misleading user expectations:

1. **Clear UI Demarcation:**
   The frontend header MUST display an unambiguous indicator of operational mode:
   - When connected to live backend: `🟢 SYSTEM STATUS: LIVE INFERENCE ACTIVE (PyTorch + FAISS)`
   - When in fallback mode: `🟡 SYSTEM STATUS: CLIENT DEMO MODE (Synthetic Data - Backend Offline)`

2. **Benchmarking Prohibition:**
   Academic evaluations, timing benchmarks, accuracy claims, and defect escape statistics MUST be calculated exclusively using Mode A. Data originating from Mode B must never enter a publication or experimental table.

3. **Cloud Hosting Requirements:**
   To host true Mode A inference in the cloud, DefectVision AI requires an environment with:
   - Python 3.10+ container runtime (e.g. AWS ECS, GCP Cloud Run with 4GB+ RAM, or Railway Docker).
   - Pre-loaded weights (`best_model.pt` + 15 category `memory_bank.npy` files totaling ~65MB).
   - Standard Vercel Serverless Functions (with 250MB bundle and 10s execution limits) cannot support the full resident PatchCore memory bank search across 15 categories.

---

## 6. Verification Status

- **Local Backend Inference (Mode A):** **VERIFIED & OPERATIONAL**
- **Cloud Fallback Transparency (Mode B):** **AUDITED & DEMARCATED**
