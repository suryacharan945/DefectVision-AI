# DefectVision AI — Live Demonstration Script (3–5 Minutes)

**Target Audience:** Machine Learning Interviewers, Technical Hiring Managers, Computer Vision Researchers  
**Objective:** Deliver an end-to-end, technically rigorous walkthrough of DefectVision AI `v1.0.0-rc1` demonstrating live inference, quality gating, category routing, anomaly localization, and edge-case handling.

---

## Pre-Demo Checklist & Environment Setup

Verify the live environment before initiating the presentation:
1. **FastAPI Backend:** Running on `http://127.0.0.1:8001` (confirm `curl http://127.0.0.1:8001/health` returns `"status": "ready"` and `"loaded_models": 15`).
2. **React Frontend:** Running on `http://127.0.0.1:5174` (Vite dev server).
3. **Specimen Directory:** Have test images ready from `DefectVisionAI/data/mvtec/` or pre-staged sample folder.

---

## Step-by-Step Demonstration Walkthrough

### Part 1: Architecture Introduction & System Startup (0:00 – 0:45)
- **Speaker Action:** Open the browser to `http://127.0.0.1:5174`.
- **Narration:**
  > "Welcome. This is DefectVision AI, an industrial machine vision platform engineered for unsupervised visual anomaly detection. In modern manufacturing, defects are rare and unbounded, rendering traditional supervised classification impractical. DefectVision AI implements the PatchCore architecture, which models nominal product normality using dense patch feature embeddings and FAISS nearest-neighbor indexing.
  > 
  > Notice the header badge: **'LIVE INFERENCE ACTIVE'** connected to our local FastAPI service on port 8001. All 15 MVTec AD industrial category memory banks and our EfficientNet-B0 category classifier are fully initialized in server memory."
- **Visual Focus:** Point out the green system status indicator, active profile selector, and telemetry bar.

---

### Part 2: Nominal Inspection & Baseline Scoring (0:45 – 1:30)
- **Speaker Action:** Select or upload a nominal bottle image (`bottle/test/good/000.png`). Click **Inspect**.
- **Narration:**
  > "First, let's inspect a pristine, nominal bottle specimen. 
  > 
  > The image passes through our two-stage pipeline in under 120 milliseconds. Notice the telemetry:
  > 1. EfficientNet-B0 instantly identifies the product as 'bottle' with 99.8% confidence.
  > 2. The pipeline dynamically routes the frame to the bottle PatchCore memory bank.
  > 3. ResNet18 extracts 784 patch embeddings, which are queried against the nominal memory bank using FAISS.
  > 
  > The maximum anomaly distance score is 0.82, well below our calibrated decision threshold of 1.50. The system issues a clear **'PASS - NOMINAL'** verdict with a high safety margin."
- **Visual Focus:** Point out the green PASS banner, low anomaly score, and minimal patch activation.

---

### Part 3: Defective Inspection & Dense Heatmap Localization (1:30 – 2:30)
- **Speaker Action:** Upload a defective bottle specimen (`bottle/test/broken_large/000.png`). Click **Inspect**.
- **Narration:**
  > "Now let's submit a defective specimen exhibiting a severe structural fracture.
  > 
  > The anomaly score spikes to 1.94, easily breaching the 1.50 threshold. The system immediately trips a **'FAIL - DEFECT DETECTED'** verdict.
  > 
  > Crucially, DefectVision AI does not just provide a binary label; it provides spatial interpretability. By toggling the Anomaly Heatmap overlay, we observe a dense jet colormap that pinpoints the exact boundary of the glass rupture. This is achieved without ever training on a single defective example—the rupture simply has no matching neighbors in the nominal patch memory bank."
- **Visual Focus:** Toggle the heatmap opacity slider, showing how the anomaly overlay precisely aligns with the physical crack on the bottle neck/body.

---

### Part 4: Quality Gating & Pre-Inference Defense (2:30 – 3:15)
- **Speaker Action:** Upload a blurry or underexposed test image (or simulate camera blur).
- **Narration:**
  > "In high-speed production, camera vibrations, lens smudges, and conveyor lighting failures frequently corrupt captures. Feeding degraded images into deep neural networks produces noisy embeddings and severe false alarms.
  > 
  > DefectVision AI enforces physical quality gating prior to neural feature extraction. Here, an image with Laplacian sharpness variance under 50.0 is instantly rejected with HTTP 422: **'QUALITY_GATE_REJECTED - Motion Blur Detected'**. This prevents garbage-in, garbage-out failures at the edge."
- **Visual Focus:** Highlight the clean error card indicating blur/exposure rejection without crashing or performing redundant inference.

---

### Part 5: Category Consistency & Open-Set Rejection (3:15 – 4:00)
- **Speaker Action:** Set the Active Profile to `bottle_line_01`. Attempt to upload a `cable` or `wood` specimen.
- **Narration:**
  > "Industrial lines are often dedicated to a single SKU. If an operator accidentally places an incorrect part, or if foreign objects enter the line, standard anomaly detectors will flag it as defective because it doesn't match the memory bank, causing line confusion.
  > 
  > DefectVision AI performs cross-validation between the active profile and the EfficientNet-B0 category prediction. The system catches the mismatch and raises **'CATEGORY_MISMATCH_REJECTION'**, alerting the operator that a cable was submitted to a bottle station."
- **Visual Focus:** Show the safety mismatch warning preventing cross-category corruption.

---

### Part 6: Batch Telemetry & Wrap-Up (4:00 – 4:45)
- **Speaker Action:** Switch to the **Batch Inspection** tab, load a batch of 10 mixed specimens, and run batch evaluation.
- **Narration:**
  > "Finally, let's observe batch processing mode. The system streams multi-image inspections, aggregating defect prevalence, latency distributions, and score histograms in real time.
  > 
  > Across the full MVTec AD benchmark of 1,725 specimens, DefectVision AI achieves a **97.15% Macro Image AUROC**, a **98.02% Pixel AUROC**, and **99.94% category recognition accuracy**. 
  > 
  > In conclusion, DefectVision AI bridges theoretical one-class deep learning and resilient industrial machine vision engineering. Thank you, and I welcome your questions."
- **Visual Focus:** Display the batch summary metrics, throughput chart, and final inspection logs.
