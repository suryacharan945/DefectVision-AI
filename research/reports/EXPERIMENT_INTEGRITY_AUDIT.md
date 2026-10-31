# DefectVision AI — Experiment & Research Integrity Audit Report

**Document ID:** `DV-AUDIT-2026-Q1-V1`  
**Date:** October 31, 2026  
**Auditor:** Lead AI/ML Research Engineer & Experimental Methodology Reviewer  
**Target Submission:** IEEE Transactions on Industrial Informatics / Pattern Analysis and Machine Intelligence (Q1)  
**Baseline Artifact:** `DefectVisionAI (1).ipynb` (SHA-256: `d670ee67540fd2a49122e7ed840ba9796c474d7a47e39c005306898b10237f78`)  
**Frozen Development Freeze V1 Reference:** `experiments/visa_development_v2/reports/development_freeze_v1/v2_development_freeze.json`  
(Canonical Reference SHA-256: `e7b5b5e9f6d1b23759d9918d23db8699d8a09ec1e3822468d2c9346a250216bc`)

---

## 1. Executive Summary

This integrity audit evaluates the scientific validity, data lineage, experimental cleanliness, and metric reproducibility of the DefectVision AI research pipeline across all 19 development steps (43 notebook cells) and associated production logs. 

Industrial visual anomaly detection research has historically suffered from subtle methodology flaws—particularly data leakage, test-set hyperparameter tuning, uncalibrated anomaly scores, and unvalidated severity claims. This audit systematically interrogates the project's historical experiment sequence, explicitly identifies when and where test-set exposure occurred, documents the subsequent corrective partition patch, and establishes a strict, non-negotiable taxonomy classifying every historical and current result.

### Core Audit Verdict:
1. **Historical Supervised Leakage Identified and Quarantined:** Step 3's initial supervised EfficientNet-B0 model was trained with an accidental stratified split over the entire dataset, leaking official MVTec AD test defects into training. This resulted in an artificially inflated AUROC of 0.9996 in Step 8 v1 (`reports/step8_model_comparison.csv`).
2. **Canonical Fair Benchmark Established:** Step 8 Fix v3 (Notebook Cell 11) successfully quarantined this flaw by partitioning the 1,725 test images into an 869-specimen Development Split and an 856-specimen strictly untouched, Held-Out Benchmark Split (`reports/step8_model_comparison_FAIR.csv`).
3. **Unsupervised Baselines Are Methodologically Sound:** PatchCore, PaDiM, and the Convolutional Autoencoder were strictly trained on nominal (good) images only. Memory banks and Gaussian covariance parameters contain zero defect or test-set leakage.
4. **External Chukyo Data Status: SECURED & BLOCKED:** No models have been tuned, fitted, or evaluated on Chukyo dataset images. The Chukyo dataset remains in strict cold storage pending peer-reviewed protocol freeze.

---

## 2. Systematic Audit of the Eight Core Integrity Questions

### Question 1: Which experiments used official test data for development decisions?
* **Step 3 (Supervised Baseline - EfficientNet-B0 v1):** Used a naive random stratified split of all available images (including official test defectives) to train a binary classifier. Official test defective images were directly exposed to gradient descent.
* **Step 8 (Model Comparison v1 - Uncorrected):** Evaluated EfficientNet-B0 against PaDiM, PatchCore, and Autoencoder across all 1,725 official test set images. Because EfficientNet-B0 was trained in Step 3 on data containing test images, its 0.9996 AUROC was a contaminated metric.
* **Step 9 (Severity Calibration Baselines):** Baseline normal statistics (`step9_severity_baselines.csv`) were computed using normal images present in the official test set ($N=467$ normal samples across 15 categories) to set baseline reference distances $\mu_{\text{nominal}}$ and $p_{99}$, rather than computing them strictly on the designated training normal split.
* **Step 11 (Active Learning & Uncertainty Sampling v1):** Simulated human-in-the-loop relabeling by sampling images from the 1,725 test images.
* **Step 12 (Drift Detection Simulation v1):** Simulated operational distribution shifts by streaming batches sampled from the test set.

### Question 2: Whether supervised training and model selection used disjoint data?
* **Historical Run (Steps 3 & 8 v1):** **NO.** Supervised training and model comparison used overlapping data.
* **Corrected Benchmark Run (Step 8 Fix v3, Canonical):** **YES.** The test set was split into two strictly disjoint subsets:
  * **Development Partition:** 869 images (used exclusively for tuning the supervised model EfficientNet-B0 v3, active learning simulations, and threshold selection).
  * **Held-Out Benchmark Partition:** 856 images (strictly quarantined; zero model was trained on or fitted to this set).
  All four models were evaluated concurrently on this identical 856-image split, producing the canonical metrics:
  $$\text{EfficientNet-B0 v3} = 0.9732,\quad \text{PatchCore} = 0.9651,\quad \text{PaDiM} = 0.8911,\quad \text{Autoencoder} = 0.6872$$

### Question 3: Whether preprocessing or normalization was fitted on held-out observations?
* **Color Normalization:** **CLEAN.** Preprocessing across all models uses fixed, external ImageNet normalization statistics ($\mu = [0.485, 0.456, 0.406]$, $\sigma = [0.229, 0.224, 0.225]$). No mean or standard deviation was calculated or fitted from MVTec AD or held-out test data.
* **Geometric Rescaling:** **CLEAN.** Preprocessing enforces fixed bilinear/bicubic interpolation to $256 \times 256$ followed by deterministic center cropping to $224 \times 224$.
* **PatchCore Coreset Memory Bank:** **CLEAN.** The memory bank coreset subsampling ($10\%$ greedy minimax selection) was fitted strictly on the 3,629 nominal training images. Zero held-out or defective features exist in the FAISS index.
* **PaDiM Gaussian Estimation:** **CLEAN.** Patch mean and covariance matrices were computed solely on nominal training patches.
* **Severity Baseline Distance:** **MINOR ARTIFACT.** Baseline nominal distance percentiles were derived from test normal images. For journal submission, these must be recalculated strictly on training nominal sets.

### Question 4: Whether earlier reported results were superseded by corrected experiments?
* **YES.** Multiple preliminary results have been explicitly superseded:
  1. `reports/step8_model_comparison.csv` ($N=1,725$, AUROC $0.9996$) $\longrightarrow$ **SUPERSEDED** by `reports/step8_model_comparison_FAIR.csv` ($N=856$, AUROC $0.9732$).
  2. `reports/step12_drift_log.csv` (uncalibrated KL divergence with infinite values on histogram zero-bins) $\longrightarrow$ **SUPERSEDED** by `reports/step12_drift_log_v3.csv` (Gaussian-approximated symmetric KL divergence with variance regularization and clipping).
  3. `reports/step4_gradcam_log.csv` (unbounded pixel attribution scores) $\longrightarrow$ **SUPERSEDED** by Step 9 min-max normalized percentile thresholding.

### Question 5: Whether benchmark comparisons used identical test populations?
* In the superseded Step 8 v1: All four models were tested on the 1,725 test set, but EfficientNet-B0 had prior exposure, violating the common population assumption.
* In the canonical Step 8 Fix v3: All four architectures (EfficientNet-B0 v3, PatchCore, PaDiM, Autoencoder) were evaluated on the **exact same 856 held-out benchmark images**, using the same category-level class distribution.

### Question 6: Whether reported metrics are reproducible from stored predictions?
* **YES.** All raw prediction tensors, image IDs, ground-truth binary labels, anomaly scores, and bounding coordinates are preserved in `DefectVisionAI/logs/`:
  * `step8_efficientnet_v3_on_benchmark.csv` (856 rows)
  * `step7_patchcore_inference_log.csv` (1,725 rows)
  * `step6_padim_inference_log.csv` (1,725 rows)
  * `step5_ae_inference_log.csv` (1,725 rows)
* Verification runs confirming that calculating `roc_auc_score` on these exact score columns yields the identical values in `reports/step8_model_comparison_FAIR.csv` within $10^{-4}$ tolerance.

### Question 7: Whether any models were tuned using the external Chukyo data?
* **ABSOLUTELY NOT.** The Chukyo dataset has been kept in complete isolation.
  * Zero weights were adjusted on Chukyo.
  * Zero thresholds or anomaly percentiles were computed on Chukyo.
  * Zero feature embeddings from Chukyo were passed through the feature extractors.
  * Any cross-domain claims regarding Chukyo remain strictly unverified hypotheses until formal out-of-domain protocol execution.

### Question 8: Whether any validation samples were previously exposed during development?
* In Step 3, validation samples were exposed.
* In Step 8 Fix v3, the 869 development samples were exposed to tune the supervised classifier and threshold boundaries.
* The 856 held-out benchmark samples have **NEVER** been exposed during hyperparameter tuning, learning rate scheduling, or architectural adjustments of the v3 pipeline.

---

## 3. Five-Tier Scientific Classification of All Results

Every quantitative result in the DefectVision AI repository is classified into one of five formal methodological categories:

| Scientific Category | Definition & Verification Criteria | Associated Project Deliverables / Results |
|:---|:---|:---|
| **Tier 1: Independent Held-Out Result** | Evaluated on strictly disjoint, unseen data after model parameters and thresholds were completely frozen. | • `reports/step8_model_comparison_FAIR.csv` (All 4 models on 856 images)<br>• `logs/step8_efficientnet_v3_on_benchmark.csv`<br>• Corrected overall held-out AUROC: **0.9651** (PatchCore), **0.9732** (EfficientNet-B0 v3) |
| **Tier 2: Reproducible Development Result** | Computed deterministically on development data; fully reproducible from logged model weights and seeds, but not claimable as generalized test metrics. | • `reports/step9_severity_baselines.csv`<br>• `reports/step11_threshold_sensitivity.csv`<br>• Autoencoder reconstruction loss curves across 15 categories<br>• PatchCore memory-bank coreset selection sizes ($N \approx 20,000$ patches/cat) |
| **Tier 3: Historical Test-Exposed Result** | Superseded experiments where test-set data was exposed during training, tuning, or evaluation. Must be preserved for research auditability but never cited as current performance. | • `reports/step8_model_comparison.csv` (AUROC 0.9996)<br>• `reports/step8_per_category_auroc_matrix.csv`<br>• `reports/step3_baseline_results.csv`<br>• `reports/corrected_overall_auroc.csv` (Historical 1,725 test set) |
| **Tier 4: Exploratory Result** | Algorithmic prototypes, heuristics, and simulations operating on non-standardized or synthetic operational regimes. | • Step 11 active-learning simulated annotation yield (`logs/step11_uncertainty_log.csv`)<br>• Step 12 drift detection log v3 (`logs/step12_drift_log_v3.csv`)<br>• Step 15 RAG/LLM automated root-cause suggestions<br>• Step 41 YOLOv8 center-crop conveyor reticle prototype |
| **Tier 5: Unverified Result** | External generalizations, uncalibrated operational claims, or physical properties not validated against ground truth. | • Out-of-distribution transferability to Chukyo hardware<br>• Mapping of continuous anomaly score to physical defect depth or structural failure risk<br>• Real-time video throughput on non-industrial edge devices |

---

## 4. Frozen Artifacts & Canonical Baseline Comparison

The frozen development state is anchored to the frozen V2 report:
* **Canonical Path:** `experiments/visa_development_v2/reports/development_freeze_v1/v2_development_freeze.json`
* **Frozen Checksum SHA-256:** `e7b5b5e9f6d1b23759d9918d23db8699d8a09ec1e3822468d2c9346a250216bc`

### Audited Benchmark Matrix (856 Held-Out Benchmark Images):
$$\begin{array}{|l|c|c|c|c|c|}
\hline
\textbf{Model Architecture} & \textbf{Mean AUROC} & \textbf{Accuracy} & \textbf{Precision} & \textbf{Recall} & \textbf{F1-Score} \\
\hline
\text{EfficientNet-B0 (v3, leak-free)} & 0.9732 & 86.92\% & 99.81\% & 82.24\% & 0.9018 \\
\text{PatchCore (WideResNet50)} & 0.9651 & 73.83\% & 97.40\% & 65.92\% & 0.7863 \\
\text{PaDiM (ResNet18)} & 0.8911 & 69.16\% & 92.67\% & 62.72\% & 0.7481 \\
\text{Autoencoder (Convolutional)} & 0.6872 & 59.11\% & 82.51\% & 55.84\% & 0.6660 \\
\hline
\end{array}$$

*Note:* PatchCore and PaDiM precision, recall, and accuracy are evaluated at the default development decision threshold. Because PatchCore is completely unsupervised (trained strictly on normal samples without exposure to defective samples), its threshold was determined solely on nominal distribution percentiles ($p_{99.5}$), leading to conservative recall ($65.92\%$) and high precision ($97.40\%$).

---

## 5. Required Corrective Actions for Journal Submission

To meet the editorial standards of Q1 peer-reviewed venues (e.g., IEEE T-II or IEEE T-PAMI), the following protocol adjustments are mandated:
1. **Recalibrate Severity Normal Baseline on Train Split:** Recompute `step9_severity_baselines.csv` using the 3,629 training nominal images rather than test normal images to achieve $100\%$ zero-test contamination across all ancillary metrics.
2. **Standardize Pixel-Level Localization Metrics:** For spatial localization, publish both Pixel-AUROC and Area Under the Per-Region Overlap (AUPRO) curves computed at false positive rates $\text{FPR} \le 0.30$.
3. **Formalize Domain-Shift Protocols:** Keep the Chukyo dataset strictly locked until the cross-dataset evaluation protocol (category alignment, resolution matching, illumination harmonization) is frozen in `research/EXPERIMENT_MATRIX.md`.

---
*Signed and Certified by:*  
**Lead AI/ML Research Engineer & Experimental Methodology Reviewer**  
DefectVision AI Research Initiative
