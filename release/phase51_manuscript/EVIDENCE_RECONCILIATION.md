# DefectVision AI — Scientific Evidence Reconciliation Report

**Phase:** Phase 51 — Evidence Reconciliation and Journal Manuscript  
**Role:** Senior Computer Vision Researcher, Scientific Editor, and Research Integrity Auditor  
**Workspace:** `C:\Users\surya\Downloads\Mini Project`  
**Date:** November 2, 2026  
**Primary Source Repositories Audited:**  
- `release/phase49_independent_results/` ([`TEST_PREDICTIONS.csv`](file:///C:/Users/surya/Downloads/Mini%20Project/release/phase49_independent_results/TEST_PREDICTIONS.csv), [`MODEL_REGISTRATION_MANIFEST.json`](file:///C:/Users/surya/Downloads/Mini%20Project/release/phase49_independent_results/MODEL_REGISTRATION_MANIFEST.json), [`ERROR_ANALYSIS.md`](file:///C:/Users/surya/Downloads/Mini%20Project/release/phase49_independent_results/ERROR_ANALYSIS.md), [`INDEPENDENT_EVALUATION.md`](file:///C:/Users/surya/Downloads/Mini%20Project/release/phase49_independent_results/INDEPENDENT_EVALUATION.md))
- `release/final_18h_validation/` ([`FINAL_EVIDENCE_AUDIT.md`](file:///C:/Users/surya/Downloads/Mini%20Project/release/final_18h_validation/FINAL_EVIDENCE_AUDIT.md), [`QUANTITATIVE_EVALUATION.md`](file:///C:/Users/surya/Downloads/Mini%20Project/release/final_18h_validation/QUANTITATIVE_EVALUATION.md))
- `DefectVisionAI/` ([`app.py`](file:///C:/Users/surya/Downloads/Mini%20Project/DefectVisionAI/app.py), [`models/efficientnet_baseline_v3/best_model.pt`](file:///C:/Users/surya/Downloads/Mini%20Project/DefectVisionAI/models/efficientnet_baseline_v3))

---

## 1. Executive Summary of Reconciliation Audit

Prior to drafting the peer-reviewed applied research manuscript, six critical numerical and architectural conflicts between historical documents, Phase 49 experimental artifacts, and Phase 50 audit drafts were audited against the raw primary data.

| # | Discrepancy Topic | Primary Source Artifact | Correct Verifiable Value | Erroneous / Conflicting Text | Cause & Status |
| :- | :--- | :--- | :--- | :--- | :--- |
| **1** | Decision Threshold | `MODEL_REGISTRATION_MANIFEST.json`, `TEST_PREDICTIONS.csv` | **$\tau_{\text{p99}} = 1.745232$** (or $1.7452$) | $\tau_{\text{p99}} = 20.3168$ in Phase 50 text | Drafting hallucination in Phase 50. **RESOLVED.** |
| **2** | Supervised Model Architecture | `DefectVisionAI/app.py`, `best_model.pt`, `FINAL_EVIDENCE_AUDIT.md` | **EfficientNet-B0 v3** ($5.3\text{M}$ params, $16.3\text{ MB}$) | "EfficientNet-B4" in Phase 50 text | Architectural conflation in Phase 50. **RESOLVED.** |
| **3** | MVTec 856 False Negatives | `FINAL_EVIDENCE_AUDIT.md` (lines 71–82) | **EffNet FN: 111 $\to$ Hybrid FN: 57** ($\Delta = -54$ missed defects) | "110 to 56" in earlier notes | Transcription off-by-one. **RESOLVED.** |
| **4** | Cashew Defect Taxonomy | `TEST_PREDICTIONS.csv`, `ERROR_ANALYSIS.md` | **16 Amazon Science categories** (e.g., scratches: 1/15, breakage: 6/6) | Synthetic categories ("20/20 cracks", "score 33.39") | Fabricated taxonomy in Phase 50. **EXPUNGED & RESOLVED.** |
| **5** | Metric Definitions & Pixel AUROC | `run_phase49_cashew_evaluation.py`, `TEST_PREDICTIONS.csv` | **Image AUROC: 0.9237; Pixel AUROC: 0.9930** (all pixels), **0.9877** (defective) | Ambiguity between sampled vs full-census pixel AUROC | Explicitly defined full census vs defect-only. **RESOLVED.** |
| **6** | Confidence Intervals | `INDEPENDENT_EVALUATION.md`, `run_phase49_cashew_evaluation.py` | **Wilson Score** for rates (e.g. [71.2%, 82.7%]), **Bootstrap** for AUROC ([0.885, 0.957]) | Uncertainty over CI calculation method | Verified against mathematical formula. **RESOLVED.** |

---

## 2. In-Depth Reconciliation by Discrepancy

---

### Discrepancy 1: Phase 49 Decision Threshold ($\tau = 1.745232$) vs. Phase 50 Text ($\tau = 20.3168$)

*   **Primary Source:**
    *   [`MODEL_REGISTRATION_MANIFEST.json`](file:///C:/Users/surya/Downloads/Mini%20Project/release/phase49_independent_results/MODEL_REGISTRATION_MANIFEST.json) (line 26): `"threshold_p99": 1.7452315574884418`
    *   [`TEST_PREDICTIONS.csv`](file:///C:/Users/surya/Downloads/Mini%20Project/release/phase49_independent_results/TEST_PREDICTIONS.csv) (Column 6: `decision_threshold`): `1.745232` across all 200 evaluation records.
    *   [`ERROR_ANALYSIS.md`](file:///C:/Users/surya/Downloads/Mini%20Project/release/phase49_independent_results/ERROR_ANALYSIS.md) (line 14): `locked 99.5th percentile nominal calibration threshold (\tau_{\text{p99}} = 1.7452)`.
    *   [`INDEPENDENT_EVALUATION.md`](file:///C:/Users/surya/Downloads/Mini%20Project/release/phase49_independent_results/INDEPENDENT_EVALUATION.md) (line 26): `Calibration Cohort: 50 Nominal Held-Out Specimens (tau_p99 = 1.7452)`.
*   **Correct Value:** $\tau_{\text{p99}} = 1.745232$ (calibrated from the 50 held-out nominal specimens).
*   **Cause of Conflict:** In Phase 50 narrative planning, the placeholder figure `20.3168` was introduced into `CLAIM_EVIDENCE_MATRIX.md` and `MANUSCRIPT_OUTLINE.md` without inspecting the saved manifest. The actual raw anomaly scores output by ResNet-18 layer2+3 patch Euclidean distances range from $1.213$ to $3.850$. A threshold of $20.3168$ would exceed all anomaly scores by an order of magnitude and produce 0% recall.
*   **Documented Correction:** The manuscript will strictly use the verified primary threshold **$\tau_{\text{p99}} = 1.7452$** (or $1.745232$). The erroneous string `20.3168` is permanently discarded.
*   **Validity Impact:** No experimental invalidation. The primary predictions in `TEST_PREDICTIONS.csv` were already generated with $1.745232$.

---

### Discrepancy 2: EfficientNet-B0 v3 versus EfficientNet-B4

*   **Primary Source:**
    *   [`DefectVisionAI/app.py`](file:///C:/Users/surya/Downloads/Mini%20Project/DefectVisionAI/app.py) (lines 101–109): `timm.create_model("efficientnet_b0", pretrained=False, num_classes=2)`
    *   [`DefectVisionAI/models/efficientnet_baseline_v3/best_model.pt`](file:///C:/Users/surya/Downloads/Mini%20Project/DefectVisionAI/models/efficientnet_baseline_v3): $16,336,185\text{ bytes}$, $360$ tensor keys (corresponds exactly to EfficientNet-B0's $5.29\text{M}$ parameters; EfficientNet-B4 would be $\sim 19.3\text{M}$ parameters and $\sim 75\text{ MB}$).
    *   [`FINAL_EVIDENCE_AUDIT.md`](file:///C:/Users/surya/Downloads/Mini%20Project/release/final_18h_validation/FINAL_EVIDENCE_AUDIT.md) (lines 71–86): `EFFICIENTNET-B0 (SUPERVISED ALONE)`.
    *   [`evaluation_protocol.md`](file:///C:/Users/surya/Downloads/Mini%20Project/release/final_18h_validation/evaluation_protocol.md) (line 49): `Model B: EfficientNet-B0 v3 (Supervised Visual Classifier)`.
*   **Correct Value:** **EfficientNet-B0 v3**.
*   **Cause of Conflict:** During Phase 50 audit text drafting, the model was mistakenly referenced as "EfficientNet-B4". EfficientNet-B4 was never trained or used anywhere in the codebase.
*   **Documented Correction:** All occurrences of "EfficientNet-B4" in manuscript blueprints are corrected to **EfficientNet-B0 v3**.
*   **Validity Impact:** Resolved. The actual weights, architecture, and latency metrics reflect EfficientNet-B0 v3.

---

### Discrepancy 3: MVTec False Negatives (111 $\to$ 57 vs. 110 $\to$ 56)

*   **Primary Source:**
    *   [`FINAL_EVIDENCE_AUDIT.md`](file:///C:/Users/surya/Downloads/Mini%20Project/release/final_18h_validation/FINAL_EVIDENCE_AUDIT.md) (lines 71–82):
        *   EfficientNet-B0 Alone: $\text{TN}=230, \text{FP}=1, \text{FN}=111, \text{TP}=514$ (Total: $856$; Defective: $625$, Nominal: $231$). Recall: $514/625 = 82.24\%$.
        *   DefectVision AI Hybrid: $\text{TN}=219, \text{FP}=12, \text{FN}=57, \text{TP}=568$ (Total: $856$; Defective: $625$, Nominal: $231$). Recall: $568/625 = 90.88\%$.
*   **Correct Values:**
    *   EfficientNet-B0 Missed Defects: **$111$** ($\text{FN}=111$, escape rate $17.76\%$).
    *   Hybrid Missed Defects: **$57$** ($\text{FN}=57$, escape rate $9.12\%$).
    *   Net Reduction in Escapes: $111 - 57 = \mathbf{54}$ fewer missed defects.
    *   EfficientNet-B0 False Alarms: **$1$** ($\text{FP}=1$, false alarm rate $0.43\%$).
    *   Hybrid False Alarms: **$12$** ($\text{FP}=12$, false alarm rate $5.19\%$).
    *   Net Increase in False Alarms: $12 - 1 = \mathbf{11}$ additional false alarms.
*   **Cause of Conflict:** A transcription error occurred in early notes where "54 fewer missed defects" was misapplied as $110 - 56 = 54$, and PatchCore's standalone false alarms ($\text{FP}=11$) were confused with the delta ($\Delta = +11$).
*   **Documented Correction:** The manuscript will state: *"On the 856-image MVTec benchmark, the hybrid policy reduced defect escapes from 111 to 57 (catching 54 defects missed by EfficientNet-B0), while increasing false alarms from 1 to 12 (11 additional false alarms)."*
*   **Validity Impact:** Arithmetic and confusion matrix perfectly reconciled.

---

### Discrepancy 4: Cashew Defect-Type Counts vs. Phase 50 Failure-Mode Descriptions

*   **Primary Source:**
    *   [`TEST_PREDICTIONS.csv`](file:///C:/Users/surya/Downloads/Mini%20Project/release/phase49_independent_results/TEST_PREDICTIONS.csv)
    *   [`ERROR_ANALYSIS.md`](file:///C:/Users/surya/Downloads/Mini%20Project/release/phase49_independent_results/ERROR_ANALYSIS.md) (Section 2, lines 26–49)
    *   Official Amazon Science VisA ground-truth annotations (`image_anno.csv`).
*   **Correct Value:** The actual evaluated VisA Cashew defective cohort consists of $100$ specimens divided across $16$ morphology classes:
    *   `middle breakage`: 6 total, 6 TP, 0 FN (100.0% recall)
    *   `stuck together`: 6 total, 6 TP, 0 FN (100.0% recall)
    *   `middle breakage, small holes`: 1 total, 1 TP, 0 FN (100.0% recall)
    *   `middle breakage, same colour spot`: 1 total, 1 TP, 0 FN (100.0% recall)
    *   `different colour spot`: 9 total, 8 TP, 1 FN (88.9% recall)
    *   `small holes`: 20 total, 17 TP, 3 FN (85.0% recall)
    *   `corner or edge breakage`: 14 total, 11 TP, 3 FN (78.6% recall)
    *   `burnt, corner or edge breakage`: 2 total, 1 TP, 1 FN (50.0% recall)
    *   `different colour spot, same colour spot`: 2 total, 1 TP, 1 FN (50.0% recall)
    *   `burnt`: 10 total, 4 TP, 6 FN (40.0% recall)
    *   `small scratches`: 15 total, 1 TP, 14 FN (**6.7% recall, 93.3% escape rate**)
    *   `same colour spot`: 10 total, 0 TP, 10 FN (**0.0% recall, 100.0% escape rate**)
    *   `burnt, different colour spot`: 1 total, 0 TP, 1 FN (0.0% recall)
    *   `different colour spot, small holes`: 1 total, 0 TP, 1 FN (0.0% recall)
    *   `burnt, same colour spot`: 1 total, 0 TP, 1 FN (0.0% recall)
    *   `corner breakage, small scratches`: 1 total, 0 TP, 1 FN (0.0% recall)
    *   **Total:** 100 defective specimens, **57 TP, 43 FN** ($57.0\%$ recall, $43.0\%$ escape rate).
*   **Cause of Conflict:** In Phase 50 drafts, an ad-hoc simplified taxonomy was written ("Coarse cracks 20/20, Severe deformation 16/20, Surface discoloration 11/20, Hairline micro-cracks 6/20, Hairline scratch 4/20") with fabricated score means ($33.39 \pm 3.19$, etc.). This was ungrounded and entirely inconsistent with the actual VisA dataset.
*   **Documented Correction:** All synthetic category labels and fabricated scores are **strictly purged**. The authentic Amazon Science 16-category taxonomy and actual TP/FN counts from `ERROR_ANALYSIS.md` are adopted for the manuscript.
*   **Validity Impact:** The real failure modes (`small scratches` 1/15, `same colour spot` 0/10) provide far stronger, more authentic scientific evidence of the limitations of nearest-neighbor distance on organic surfaces than the synthetic figures.

---

### Discrepancy 5: Image-Level vs. Pixel-Level Metric Definitions and Calculations

*   **Primary Source:**
    *   `scripts/run_phase49_cashew_evaluation.py`
    *   `release/phase50_publication_audit/METRIC_REPRODUCIBILITY_AUDIT.md`
*   **Reconciled Definitions:**
    *   *Image-Level Score ($S_{\text{img}}$):* The maximum value of the smoothed 2D anomaly heatmap: $S_{\text{img}} = \max_{i,j} \mathcal{A}(i,j)$.
    *   *Image-Level AUROC:* Area under ROC curve computed from $S_{\text{img}}$ across 100 nominal and 100 defective test images ($N=200$). Verified value: **$0.9237$**.
    *   *Image-Level AUPRC:* Area under Precision-Recall curve computed from $S_{\text{img}}$. Verified value: **$0.9270$**.
    *   *Pixel-Level Anomaly Map ($\mathcal{A}$):* Multi-scale patch feature distances from ResNet-18 `layer2` and `layer3`, bilinearly interpolated to $224 \times 224$ and smoothed with a Gaussian filter ($\sigma = 4.0$).
    *   *Full-Census Pixel AUROC:* Evaluated across all pixels in the 200 test images ($200 \times 224 \times 224 = 10,035,200\text{ pixels}$) against binarized ground-truth polygon masks ($m > 0$). Verified value: **$0.9930$** ($0.993021$).
    *   *Defect-Only Specimen Pixel AUROC:* Evaluated strictly across pixels of the 100 defective images ($100 \times 224 \times 224 = 5,017,600\text{ pixels}$). Verified value: **$0.9877$** ($0.987703$).
*   **Documented Correction:** Both pixel-level calculations are formally defined in the manuscript methodology to prevent any ambiguity.

---

### Discrepancy 6: Confidence Interval Calculation Methods

*   **Primary Source:** `INDEPENDENT_EVALUATION.md`, `run_phase49_cashew_evaluation.py`.
*   **Reconciliation & Verification:**
    *   *Continuous Metric (Image AUROC):* Evaluated using non-parametric empirical bootstrapping ($B=1,000$ resamples with replacement, seed 42):
        $$\text{AUROC} = 0.9237 \quad [95\%\text{ CI: } 0.8852, 0.9565]$$
    *   *Binary Proportions (Accuracy, Specificity, Recall, Precision):* Evaluated using Wilson score intervals without continuity correction ($z = 1.96$):
        *   Accuracy ($155/200$): $77.50\%$ $[71.22\%, 82.68\%]$
        *   Specificity ($98/100$): $98.00\%$ $[92.96\%, 99.45\%]$
        *   Defect Recall ($57/100$): $57.00\%$ $[47.24\%, 66.24\%]$
        *   Defect Precision ($57/59$): $96.61\%$ $[88.48\%, 99.07\%]$
*   **Documented Correction:** The manuscript will explicitly state: *"Confidence intervals for image-level AUROC were computed via 1,000 empirical bootstrap iterations; confidence intervals for discrete classification rates were computed using Wilson score intervals ($z=1.96$)."*

---

## 3. Audit Determination

All six discrepancies have been rigorously traced to primary source artifacts, explained, and corrected.  
**No discrepancy compromises the empirical integrity of the independent VisA Cashew experiment or the MVTec benchmark.**  
Manuscript drafting is authorized to proceed with frozen, verified numbers.
