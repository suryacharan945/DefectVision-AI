# DefectVision AI — Project Overview

**Milestone:** `v1.0.0-rc1` — Benchmark-Evaluated Industrial Anomaly Detection Research Prototype  
**Repository:** [DefectVision-AI](https://github.com/suryacharan945/DefectVision-AI)  
**Pull Request:** [#6](https://github.com/suryacharan945/DefectVision-AI/pull/6) (`fix/localhost-live-inference-restoration`)  
**Status:** `RELEASE READY WITH DOCUMENTED METRIC LIMITATIONS`

---

## 1. Industrial Problem Context

In automated discrete manufacturing and high-throughput production lines (e.g., semiconductor fabrication, pharmaceutical packaging, metal stamping, food packaging), product quality inspection is mission-critical. Traditional quality assurance relies heavily on:
1. **Manual Human Visual Inspection:** Highly prone to operator fatigue, cognitive drift, subjective grading inconsistencies, and severe throughput bottlenecks (often limited to 1–2 parts per second with error rates climbing past 15% after 20 minutes of continuous inspection).
2. **Rule-Based Machine Vision:** Traditional edge detection, blob analysis, and template matching fail when confronted with subtle surface variations, organic textures (wood, leather), non-rigid alignment shifts, and specular reflections on curved surfaces.

A single defect escape to end consumers can trigger catastrophic recalls, warranty claims, regulatory fines, and reputational damage. Conversely, excessive false-alarm rates (false positives) unnecessarily halt assembly lines, divert operator attention, and waste functional product.

---

## 2. Motivation: The Supervised Learning Fallacy in Manufacturing

The standard machine learning instinct is to train a multi-class or binary supervised classifier (e.g., ResNet, EfficientNet, YOLO) on labeled images of defects ("scratch", "dent", "contamination", "crack"). In real-world factory deployments, this approach breaks down for three fundamental reasons:

1. **Extreme Class Imbalance:** Nominal ("good") parts represent >99.9% of actual manufacturing yields. Defect occurrences are rare outliers (often <0.1% or parts-per-million), making it economically and logistically prohibitive to assemble balanced, representative defect training sets.
2. **Unbounded Defect Taxonomy (The "Open World" Problem):** Supervised classifiers can only detect defect types present in their training set. In practice, real manufacturing defects are unconstrained: an unexpected chemical contaminant, machine tooling wear, temperature fluctuation, or foreign object produces defect morphologies never previously seen. A supervised model frequently classifies novel defects as nominal with high confidence.
3. **Severe Cost of Defect Annotation:** Pixel-level bounding-box or segmentation annotation across dozens of part SKUs requires domain experts and hundreds of labor hours, delaying new product introductions (NPI) from days to months.

---

## 3. The Solution: Unsupervised Anomaly Detection via PatchCore

DefectVision AI adopts an **unsupervised, cold-start one-class representation paradigm**. Rather than learning what a defect looks like, the system learns what **normality** looks like exclusively from nominal ("golden") specimens.

DefectVision AI implements the **PatchCore** architecture (Roth et al., 2022) coupled with an upstream **EfficientNet-B0** category routing engine:
- **Patch-Level Feature Hierarchy:** Instead of compressing an entire product into a single global embedding (which averages out small local anomalies), PatchCore extracts localized mid-level feature vectors from intermediate convolutional layers (ResNet18 `layer2` and `layer3`).
- **Nominal Memory Bank:** During cold-start enrollment, high-dimensional patch embeddings from nominal specimens are pooled into a memory bank. A greedy coreset subsampling mechanism (or full-index preservation) retains maximum geometric diversity of nominal feature space while maintaining rapid query times.
- **Nearest-Neighbor Anomaly Scoring:** At inference time, each patch embedding from an incoming test specimen is compared against the nominal memory bank using accelerated Euclidean distance search via **FAISS** (Facebook AI Similarity Search). The anomaly score of an image is governed by its most outlying patch embedding, and dense distance scores are spatially mapped into an interpretable anomaly localization heatmap.

---

## 4. Benchmark Dataset & Supported Categories

DefectVision AI is rigorously evaluated on the industry-standard **MVTec Anomaly Detection (MVTec AD)** benchmark, covering 15 complex industrial categories:

| Category Type | Categories | Primary Anomaly Challenges |
| :--- | :--- | :--- |
| **Textures (5)** | `carpet`, `grid`, `leather`, `tile`, `wood` | Repeating spatial patterns, natural texture stochasticity, structural weaves, color gradations. |
| **Rigid Objects (10)** | `bottle`, `cable`, `capsule`, `hazelnut`, `metal_nut`, `pill`, `screw`, `toothbrush`, `transistor`, `zipper` | Specular reflection, 3D orientation shifts, internal component defects, structural fractures, contamination. |

The dataset comprises **5,354 high-resolution images** (3,629 nominal training images, 1,725 testing images split into 467 nominal and 1,258 defective specimens across 73 distinct defect types).

---

## 5. Technology Stack

DefectVision AI is engineered as an enterprise-grade, microservice-ready research platform:

- **Machine Learning Core:**
  - `PyTorch 2.x` & `Torchvision`: ResNet18 feature extractor with customized pooling hooks.
  - `FAISS-CPU`: Highly optimized $L_2$ vector indexing for millisecond-scale nearest-neighbor search.
  - `Timm` / `PyTorch`: Pre-trained EfficientNet-B0 fine-tuned for 15-class SKU identification.
  - `NumPy` & `SciPy`: Scientific array operations, Gaussian kernel smoothing, statistical distribution fitting.
  - `OpenCV`: Multi-scale image processing, CLAHE equalization, Laplacian blur quantification, exposure histogram analysis.
- **Backend Service:**
  - `FastAPI`: High-performance asynchronous REST API framework.
  - `Pydantic v2`: Strict schema validation, request/response models, and telemetry tracking.
  - `Uvicorn`: Production ASGI web server running on port 8001.
- **Frontend Dashboard:**
  - `React 18` & `Vite`: High-speed reactive user interface with sub-10ms DOM updates.
  - `Tailwind CSS`: Modern, clean industrial dark/light monitoring interface.
  - `Lucide React`: Operational iconography.
  - `Canvas API`: Client-side real-time rendering of PatchCore anomaly overlays with adjustable opacity.

---

## 6. Major System Capabilities

1. **Universal Image Intake & Quality Gating:**
   - Evaluates incoming frames before inference for physical capture defects.
   - Rejects severe blur (Laplacian variance $< 50.0$) and improper exposure (underexposure $< 20.0$, overexposure $> 235.0$).
2. **Automated Category Recognition & Open-Set Rejection:**
   - Classifies incoming specimens into 15 industrial SKUs with **99.94% accuracy** (1,724/1,725 test images).
   - Flags out-of-distribution or ambiguous inputs using softmax entropy gating ($H > 0.85$).
3. **Sub-Second Dense Anomaly Localization:**
   - Computes localized anomaly heatmaps revealing exact defect locations, dimensions, and intensities without requiring pixel-level training masks.
4. **Few-Shot SKU Adaptation Engine:**
   - Enables cold-start onboarding of new product lines using only $K=10$ or $K=20$ nominal reference specimens.
5. **Interactive Operations Dashboard:**
   - Provides live camera / file upload, single-part and batch evaluation modes, telemetry inspection (latency, scores, threshold margins), and verifiable backend connectivity indicators.

---

## 7. Current Technical Limitations

Honesty and empirical precision are paramount. DefectVision AI `v1.0.0-rc1` operates under clearly documented constraints:
- **Macro Image AUROC:** 97.15% across all 15 benchmark categories (Pixel AUROC: 98.02%, Macro AUPRC: 98.98%).
- **Operational False-Alarm Rate:** At the default operational threshold ($1.50$), the system achieves $94.04\%$ micro defect recall with a $24.84\%$ false-positive rate across benchmark test images. Rigid-object alignment variations (e.g., `screw`, `capsule`, `transistor`) contribute to elevated false alarms.
- **Sample-Efficiency Statistical Bounds:** Zero observed false alarms on small validation sets ($k=0, n=20$) yields an exact Clopper–Pearson 95% confidence interval upper bound of **16.84%** (Wilson score: 16.11%). Sub-1% false alarm guarantees require $N \ge 300$ independent nominal validation captures.
- **External Domain Shift (Track B):** Generalization to uncalibrated smartphone captures or external lighting environments remains blocked due to insufficient physical defect specimens ($n=1$ physical defect specimen available for Track B).
