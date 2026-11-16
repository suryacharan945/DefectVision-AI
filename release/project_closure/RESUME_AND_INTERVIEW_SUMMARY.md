# DefectVision AI — Resume & Interview Preparation Summary

**Target Audience:** Machine Learning Engineers, Computer Vision Engineers, Senior AI System Architects  
**Authoritative Reference:** `release/final_18h_validation/FINAL_EVIDENCE_AUDIT.md`  
**Git Baseline:** `0ff3c79`

---

## 1. Resume Bullet Points (Tailored for CVs)

- **Industrial Computer Vision Architecture:** Engineered a dual-engine visual anomaly detection system for manufacturing lines combining an unsupervised patch-memory bank (PatchCore / ResNet-18 + FAISS coreset retrieval) with a supervised transfer learning classifier (EfficientNet-B0), served via an asynchronous FastAPI microservice.
- **Empirical Evaluation & Escape Reduction:** Benchmarked system across 856 industrial inspection specimens spanning 15 MVTec AD categories and 49 defect morphologies, achieving **91.94% accuracy**, **90.88% recall**, and an **F1-score of 0.9427**, reducing defect escapes by **48.6%** (54 fewer missed defects) compared to standalone supervised classification.
- **Audited Trade-Off & Latency Profiling:** Profiled and defended real-world operational trade-offs, quantifying a 12-fold false alarm increase (+11 FPs, 0.43% to 5.19% FPR) in exchange for high-recall defect capture, with end-to-end multi-core CPU latency benchmarked at 881.7 ms median ($p95 = 1455.7$ ms).
- **Scientific Integrity & Empirical Post-Mortems:** Spearheaded evidence integrity audits that formally refuted a proposed algorithmic extension (CPND) and mathematically proved the equivalence of active review logic (MACBA) to standard cost-sensitive decision theory, saving team engineering bandwidth.
- **Production-Grade Microservice & Clean Export:** Built 29 REST endpoints with deterministic inference verification (zero floating-point variance), 22 passing unit tests, and automated boundary stress testing (corrupt payloads, SQL injection, extreme aspect ratios), packaging a clean-room open-source distribution.

---

## 2. The 2-Minute Elevator Pitch ("Tell Me About This Project")

> *"In automated manufacturing inspection, quality teams face a fundamental dilemma. Supervised classifiers like EfficientNet have near-zero false alarms on known defects, but they fail silently when confronted with novel, out-of-distribution flaws. Conversely, unsupervised anomaly models like PatchCore excel at detecting open-world anomalies, but they suffer from higher defect escapes on subtle textures and struggle with cross-category threshold calibration.*
>
> *To solve this, I developed **DefectVision AI**, a dual-engine architecture that combines PatchCore's ResNet-18 patch embeddings indexed in FAISS with a fine-tuned EfficientNet-B0 classifier through a disjunctive decision gate. The system produces continuous defect heatmaps via Gaussian-smoothed patch distances and calculates multi-factor severity scores based on localized defect area.*
>
> *I conducted a comprehensive empirical evaluation on 856 industrial specimens across 15 categories. The hybrid architecture halved defect escapes—catching 54 defective parts that the supervised classifier missed, pushing defect recall from 82.2% to 90.9%. However, I also made sure to report the trade-offs honestly: that extra recall came at the cost of an 11-specimen increase in false alarms (FPR rising from 0.43% to 5.19%), and end-to-end CPU latency averaged ~880 ms, showing that high-speed conveyor lines would require GPU acceleration.*
>
> *Beyond the core system, what I'm most proud of is the scientific rigor: when our team evaluated two proposed novel algorithms—CPND and MACBA—our audits proved that CPND offered no statistically significant gain, and MACBA was mathematically equivalent to standard cost-weighted ranking. We documented these negative findings transparently, frozen the research, and delivered a production-ready, clean-room open-source prototype with full unit test coverage and deterministic inference."*

---

## 3. Key Architecture & Engineering Decisions

| Decision | Why It Was Chosen | Considered Alternatives & Why Rejected |
| :--- | :--- | :--- |
| **ResNet-18 Layers 2+3 for PatchCore** | Captures mid-level structural features and local textures without semantic over-abstraction. Fast forward pass (~412 ms on CPU). | **ResNet-50 / Wide-ResNet-50:** Marginal recall increase (+1.2%) at severe latency penalty (3.5x slower CPU inference). |
| **FAISS L2 with 10% Coreset Subsampling** | Reduces memory footprint and search latency by ~90% while retaining >98% of full nearest-neighbor anomaly representation. | **Full Memory Bank:** Unbounded memory growth, excessive search latency (>1200 ms per image). |
| **EfficientNet-B0 Supervised Companion** | Extremely parameter-efficient (~5.3M params) with high specificity ($99.57\%$) and sub-40ms forward pass. | **Vision Transformer (ViT-B/16):** Excessive inference latency on CPU, prone to data hunger on small defect splits. |
| **Disjunctive Logic ($\hat{y}_{\text{PC}} \lor \hat{y}_{\text{EffNet}}$)** | Prioritizes defect recall; industrial manufacturing heavily penalizes customer defect escapes over internal false alarms. | **Weighted Probability Averaging:** Unsupervised distance scales and supervised sigmoids have mismatched calibrations; averaging diluted true defect signals. |
| **Otsu Thresholding on Smoothed Heatmaps** | Adaptively extracts defect contours without manual pixel threshold tuning across disparate material surfaces. | **Fixed Pixel Threshold:** Fails across categories due to dynamic range variation in raw distance maps. |

---

## 4. Deep-Dive Interview Scenarios & Failure Mode Post-Mortems

### Scenario A: "How did you ensure scientific validity and avoid data leakage?"
- **Answer Structure:**
  1. *Acknowledge the audit:* "We performed a strict manifest-level audit across all historical splits using automated Python scripts (`scripts/audit_data_provenance.py`)."
  2. *Disclose exposure honestly:* "We verified that our active model weights (v3) had 0% sample overlap with the 856-image benchmark. However, we discovered that early prototype v1 training had included 788 of those images, and the benchmark had been evaluated repeatedly during development ablation cycles."
  3. *Classify properly:* "Rather than claiming 'zero-leakage' or 'independent held-out', we formally classified the benchmark as **Category C: Development-Exposed**. Furthermore, we kept all external datasets (11 VisA categories, BTAD, Chukyo) strictly quarantined so no false cross-domain generalization claims could be made."

### Scenario B: "Tell me about a time you killed a feature or hypothesis based on data."
- **Answer Structure:**
  1. *The hypothesis:* "We hypothesized that Confidence-Penalized Neighborhood Density (CPND) would improve defect separation by penalizing sparse memory clusters."
  2. *The experiment:* "We ran rigorous ablations across 5 test categories. The data showed zero statistically significant improvement in AUROC or F1. In fact, on subtle surface scratches, the density penalty actively diluted true defect signals, increasing false negatives."
  3. *The second post-mortem (MACBA):* "Later, our active learning method MACBA appeared to outperform baselines. I reconstructed the decision matrices step-by-step and found that under identical probability estimators and cost ratios, MACBA was mathematically identical to standard cost-weighted ranking (BL6). We killed both initiatives, saved engineering cycles, and documented the negative findings transparently."

### Scenario C: "What were the real-world operational limitations of the system?"
- **Answer Structure:**
  1. *The false alarm trade-off:* "The hybrid caught 54 more defects than EfficientNet alone, but increased false positives by 12x (1 FP to 12 FP). In a high-volume plant, 5.19% false alarms means 1 in 20 good parts diverted, requiring dedicated human review queues."
  2. *Hardware throughput:* "On multi-core CPU, the full API inspection round-trip takes 881.7 ms median. High-speed conveyor lines (10–30 parts/sec) cannot run on CPU; we recommended GPU/TensorRT acceleration or restricting CPU to indexed indexing tables with cycle times $> 1.5$ seconds."
  3. *Optical sensitivity:* "Perturbation tests showed vulnerability to high Gaussian noise ($\sigma \ge 0.10$). We defined an operational protocol mandating enclosed telecentric illumination tunnels to prevent factory lighting drift."

---

## 5. Technical Skills Demonstrated

- **Machine Learning & CV:** PyTorch, Torchvision, PatchCore, EfficientNet-B0, FAISS Coreset Retrieval, Heatmap Generation, Otsu Segmentation, Confusion Matrix Auditing, AUROC/AUPRC.
- **Backend & Systems Engineering:** Python 3.12, FastAPI, Uvicorn, REST API Design, Asynchronous Request Handling, Pydantic v2, Multi-Threading, Latency Profiling.
- **Quality Assurance & Testing:** PyTest (22/22 tests), Adversarial Stress Testing (Payload Ingestion, SQL Injection, Aspect Ratios), Deterministic Floating-Point Auditing.
- **Research Methodology:** Dataset Provenance Auditing, Data Leakage Mitigation, Negative Results Post-Mortems, Threat-to-Validity Analysis, Industrial Protocol Design (SOP).
