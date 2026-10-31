# DefectVision AI — Demonstration & Evaluation Guide

**Document ID:** `DV-DEMO-2026-REL-V1`  
**Date:** October 31, 2026  
**Audience:** Industrial Quality Managers, Research Evaluators, Reviewers, and Engineers  
**System Version:** v1.0.0 (Production Release Candidate)  

---

## 1. Quick-Start Demonstration Setup

DefectVision AI operates in two operational modes:

### Mode A: Full On-Premise Industrial Server (Live PyTorch / FAISS Inference)
```bash
# 1. Start the Python FastAPI backend
cd DefectVisionAI
python app.py
# Backend serves at http://127.0.0.1:8000

# 2. In a separate terminal, start the React frontend
cd ../frontend
npm run dev
# Frontend runs at http://localhost:5173
```

### Mode B: Zero-Server Cloud Edge / Vercel Evaluation
When running on Vercel or without local GPU/PyTorch packages installed:
1. Navigate directly to your deployment URL or run `npm run dev --prefix frontend`.
2. The UI automatically activates the **Client-Side Edge Engine**, utilizing bundled benchmark models and features from the 1,725-specimen MVTec AD test log. Every feature remains fully functional, interactive, and crash-resilient with zero cold-start delay.

---

## 2. Step-by-Step Guided Walkthrough

### Workflow 1: Single-Image Inspection & Heatmap Localization
1. **Navigate to the "Inspect" Tab:** Click **Inspect** in the top navigation bar.
2. **Select an Industrial Category:** Choose a category from the dropdown (e.g. `bottle`, `screw`, or `carpet`).
3. **Upload an Image or Load Specimen:** Drag and drop an industrial test image or click to load a sample.
4. **Examine the Analysis Output:**
   - **Decision Badge:** Displays `NOMINAL (PASS)` in green or `DEFECT DETECTED (REJECT)` in red/amber.
   - **Anomaly Score:** Displays the normalized patch distance and comparison against the calibrated threshold $\tau$.
   - **Severity Level:** Displays the heuristic severity badge (`Minor`, `Moderate`, or `Critical`).
   - **Interactive Heatmap Overlay:** Toggle between original image, heatmap, and split overlay.
   - **Interactive Magnifier Reticle:** Hover over the specimen to inspect microscopic surface scratches under 2.5× optical zoom.
5. **Inspect Model Architecture & Provenance:**
   - Click the **"Model Architecture & Provenance Metadata"** button below the image viewport.
   - Review the active backbone architecture (WideResNet-50 / EfficientNet-B0), ImageNet normalization values ($224 \times 224$), nominal-only training regime, and the 856-specimen leak-free benchmark metrics.

---

### Workflow 2: High-Throughput Batch Inspection & Reporting
1. **Navigate to the "Batch" Tab:** Click **Batch** in the top navigation bar.
2. **Select Target Category:** Choose the relevant product line (e.g. `bottle`).
3. **Queue Batch Images:** Select multiple images from your file dialog (or inspect the pre-loaded 150-specimen batch).
4. **Submit Batch:** Click **Submit Batch**. Observe the live progress bar transition through the queue.
5. **Review Batch Analytics:**
   - **KPI Cards:** Inspected count, overall Defect Rate %, Defective count, and Nominal count.
   - **Severity Distribution Bar:** Color-coded distribution of Critical, Moderate, and Minor items.
   - **Batch Results Table:** Per-image status, predicted label, severity index, and confidence.
6. **Export Inspection Records:**
   - Click **CSV** in the summary card header to download `batch_{id}_results.csv`.
   - Click **JSON** to download the complete structured JSON report.

---

### Workflow 3: Inspection History & Benchmark Browser
1. **Navigate to the "History" Tab:** Click **History** in the top navigation bar.
2. **Filter by Industrial Category:** Use the category dropdown to isolate specific production lines (e.g. `hazelnut` or `metal_nut`).
3. **Filter by Severity Level:** Select `Critical (Score ≥ 70)` to isolate high-risk rejects.
4. **Search by Keyword:** Type `scratch`, `crack`, or `hole` in the search box to find specific defect mechanisms.
5. **Inspect Individual Records:** Click the **Eye Icon** on any row to open the full inspection modal with high-resolution heatmap and root-cause breakdown.
6. **Export Filtered Audit Log:**
   - Click **Export Filtered CSV** in the section header.
   - Verify that the downloaded CSV matches your exact active filters.

---

### Workflow 4: Advanced Assisted Features

#### A. Drift Monitoring (`Drift` Tab)
* Inspect real-time feature distribution shifts over time.
* Review Gaussian symmetric KL divergence and Wasserstein distance curves against the frozen nominal baseline (`step12_drift_log_v3.csv`).
* Check the Automated Drift Alert indicator (Normal vs Alert).

#### B. Defect Similarity Retrieval (`Similarity` Tab)
* Upload a defective part to query the FAISS 512-dimensional embedding space.
* Returns the top-5 most visually and structurally similar historical defects from the archive.

#### C. RAG Defect Copilot (`Copilot` Tab)
* Test the intelligent engineering assistant using natural-language manufacturing queries:
  - *"What are the common causes of contaminated scratches in glass bottles?"*
  - *"How do thermal extruder fluctuations affect cable sheath defects?"*
  - *"Recommend preventive maintenance actions for thread stripping on metal nuts."*
* Observe that the system retrieves verified engineering records and clearly tags suggestions with an engineering disclaimer.

#### D. Live Webcam / Conveyor Inspection (`Webcam` Tab)
* Click **Start Video Stream** to enable camera input (or interactive simulated frame generator).
* Use the calibrated center-crop reticle to frame components as they pass on a simulated conveyor.

---

## 3. Evaluation Checklist for Reviewers

- [x] Single-image inspection renders without console errors.
- [x] Model provenance drawer opens and discloses all 856-image benchmark metrics.
- [x] Batch inspection completes and exports downloadable CSV and JSON.
- [x] History browser correctly filters all 1,725 benchmark images and exports filtered CSV.
- [x] All anomaly scores are labeled as distance metrics, not raw uncalibrated probabilities.
- [x] Severity index is labeled as an operational ranking heuristic.
- [x] RAG copilot gracefully handles empty or edge-case questions.

---
*Prepared by:*  
**DefectVision AI Product & Engineering Team**
