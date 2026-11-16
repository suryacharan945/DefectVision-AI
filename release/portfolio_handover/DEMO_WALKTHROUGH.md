# DefectVision AI — Demonstration Walkthrough Script & Storyboard

**Duration:** 2 minutes 45 seconds (165 seconds)  
**Target Format:** Video Recording / Live Interactive Demonstration  
**Target Audience:** Machine Learning Engineers, Technical Recruiters, Industrial Quality Automation Leads  
**Accompanying Visual Assets:** `release/portfolio_handover/assets/`

---

## Storyboard Overview & Timeline

| Scene | Time | Scene Title | Key Visual Asset / On-Screen Content | Narration Focus |
| :---: | :---: | :--- | :--- | :--- |
| **1** | 0:00–0:25 | **The Industrial Inspection Dilemma** | Architecture Diagram (`07_architecture_and_pipeline_diagram.png`) | Problem definition: Unsupervised escapes vs Supervised blind spots |
| **2** | 0:25–0:55 | **Genuine Inference on Defective Specimen** | Real Defective Bottle & Heatmap (`01_...png`, `02_...png`, `03_...png`) | Live inspection, ResNet-18 + FAISS coreset score, EfficientNet confidence, Otsu contour |
| **3** | 0:55–1:20 | **Genuine Inference on Nominal Specimen** | Real Nominal Bottle & Clean Overlay (`04_...png`, `05_...png`, `06_...png`) | Specificity verification, low background distances, zero false alarms on pristine part |
| **4** | 1:20–1:45 | **Disjunctive Fusion & Audited Trade-Off** | Confusion Matrices & Trade-Off Charts (`11_...png`, `12_...png`) | 54 fewer misses (-48.6% escapes) vs 11 additional false alarms (+1200% FPR) |
| **5** | 1:45–2:10 | **Batch Inspection & Selective Triage Console** | Batch Telemetry Dashboard (`10_...png`) | Multi-specimen lot processing, severity categorization, risk-priority queue |
| **6** | 2:10–2:30 | **Public Repository Synthetic Demo Mode** | Synthetic Warning Visual (`09_...png`) | Public repository mock fallback with explicit demo warning banner |
| **7** | 2:30–2:45 | **Hardware Latency, Limitations & Wrap-Up** | API Telemetry Payload Card (`13_...png`) | Multi-core CPU latency (881.7 ms median), open-source release, conclusion |

---

## Detailed Scene-by-Scene Script

### Scene 1: The Industrial Inspection Dilemma (0:00 – 0:25)
- **Visual Cue:** Full-screen render of `07_architecture_and_pipeline_diagram.png`. Cursor highlights Engine 1 (PatchCore), Engine 2 (EfficientNet), and the central Disjunctive Fusion Gate.
- **Narration:**  
  *"In automated factory inspection, quality engineering faces a persistent dilemma: unsupervised models like PatchCore can detect novel, unseen defects, but they miss subtle textures and suffer from cross-category threshold drift. Meanwhile, supervised classifiers like EfficientNet have near-zero false alarms, but they fail completely on novel anomaly shapes.*  
  *DefectVision AI solves this with a dual-engine architecture. We combine a ResNet-18 patch coreset indexed in FAISS with a fine-tuned EfficientNet-B0 classifier through an asymmetric disjunctive decision gate—deliberately prioritizing defect recall to prevent escapes from reaching customers."*

---

### Scene 2: Genuine Inference on a Defective Specimen (0:25 – 0:55)
- **Visual Cue:** Transition to storyboard panel `08_dual_engine_inference_storyboard.png` (Top Row). Display raw defective bottle image (`broken_large/000.png`), live PatchCore distance heatmap (`02_...png`), and localized defect overlay (`03_...png`).
- **Narration:**  
  *"Here is genuine inference running live on an industrial specimen—a glass bottle with a fractured neck.  
  Engine 1 extracts patch embeddings from ResNet Layers 2 and 3, querying a FAISS L2 coreset index. It returns an anomaly distance of 3.3056 against a nominal category threshold of 1.4138—a clear breach.  
  Engine 2's EfficientNet classifier independently evaluates the frame, outputting a 99.99% defect probability.  
  The disjunctive gate flags the part as defective. Our localization engine upsamples the patch scores with Gaussian smoothing, applies Otsu adaptive segmentation, and calculates a defect area of 39.29%, assigning an overall severity score of 81.8—classified as Critical."*

---

### Scene 3: Genuine Inference on a Nominal Specimen (0:55 – 1:20)
- **Visual Cue:** Storyboard panel `08_dual_engine_inference_storyboard.png` (Bottom Row). Display raw nominal bottle (`good/000.png`), nominal distance heatmap (`05_...png`), and clean surface overlay (`06_...png`).
- **Narration:**  
  *"Now let's verify specificity on a nominal, unblemished specimen.  
  The PatchCore anomaly score drops to 1.2869, well below the 1.4138 threshold. The distance heatmap confirms low residual background noise across the bottle body. EfficientNet outputs an anomaly probability below 0.01%.  
  Both engines agree: the part is classified as Normal, with zero false alarms and severity level None.  
  Crucially, across 5 consecutive deterministic inference runs, the maximum score variance is exactly 0.000000—verifying bitwise numerical reproducibility."*

---

### Scene 4: Disjunctive Fusion & The Audited Trade-Off (1:20 – 1:45)
- **Visual Cue:** Display `11_confusion_matrices_comparison_plot.png` and `12_audited_tradeoff_recall_vs_false_alarms.png`. Highlight the 54 fewer misses and the 11 additional false alarms.
- **Narration:**  
  *"We audited our dual-engine architecture across 856 specimens spanning 15 manufacturing categories.  
  Here is the unvarnished scientific reality: the hybrid is not an omni-superior model. Compared to EfficientNet alone, our hybrid cuts defect escapes from 111 down to 57—a 48.6% reduction in missed defects, capturing 54 additional flawed parts.  
  However, that recall comes with a concrete price: false positives increase from 1 to 12—a 12-fold increase in false alarms, raising the false positive rate from 0.43% to 5.19%. In manufacturing, this trade-off is operationally justified because missing a critical defect carries catastrophic warranty costs compared to manually re-inspecting borderline parts."*

---

### Scene 5: Batch Inspection & Selective Triage Console (1:45 – 2:10)
- **Visual Cue:** Display `10_batch_inspection_telemetry_dashboard.png`. Highlight lot defect distribution, severity breakdown, and the human review priority queue.
- **Narration:**  
  *"For production lines, DefectVision AI includes an asynchronous batch inspection worker. The system processes entire production lots, generating lot-level defect rates, severity distributions, and a decision-theoretic review triage queue.  
  Instead of inspecting parts randomly or relying on naive confidence thresholds, our triage engine ranks borderline specimens by expected economic loss reduction, ensuring quality inspectors focus their limited time on the highest-risk parts."*

---

### Scene 6: Public Repository Synthetic Demo Mode (2:10 – 2:30)
- **Visual Cue:** Display `09_synthetic_demo_mode_with_warning.png`. Zoom in on the yellow demo mode warning banner.
- **Narration:**  
  *"To enable open-source reproducibility without redistributing restricted multi-gigabyte industrial datasets, our clean public repository features a transparent Simulated Demo Mode.  
  When model checkpoints are omitted, the application falls back to a deterministic proxy calculation, clearly displaying this yellow warning banner. Users can explore the full UI, inspect API schemas, and test batch queues immediately upon cloning, with instructions to plug in authorized checkpoints for production inference."*

---

### Scene 7: Hardware Latency, Limitations & Conclusion (2:30 – 2:45)
- **Visual Cue:** Display `13_api_inspection_response_telemetry.png` showing the full FastAPI JSON response and runtime stats.
- **Narration:**  
  *"On a standard 12-thread CPU, our dual-model forward pass takes 450.6 ms, and the full FastAPI round-trip averages 881.7 ms. This supports 1 to 2 inspections per second for indexing lines or manual review stations, while high-speed conveyors will require GPU acceleration.  
  DefectVision AI is released under the MIT license with complete unit tests, reproducible manifests, and transparent negative research findings. Thank you."*
