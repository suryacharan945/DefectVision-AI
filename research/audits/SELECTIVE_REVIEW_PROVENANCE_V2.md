# SELECTIVE REVIEW METRIC PROVENANCE & POPULATION AUDIT (V2)

**Document ID:** `research/audits/SELECTIVE_REVIEW_PROVENANCE_V2.md`  
**Audit Date:** October 31, 2026  
**Auditor:** Lead AI/ML Verification & Research Integrity Engineer  
**Status:** Certified Forensic Reconciliation  

---

## 1. Executive Summary: The 37-Error vs. 127-Error Mystery Resolved

Prior documentation presented two conflicting error baselines for selective human review on the MVTec AD test set ($N = 1,725$ images):
- **Analysis 1 (Step 11):** Reported $127$ total errors, with selective review capturing $61$ errors ($48.0\%$) at a $9.7\%$ review budget ($\tau \ge 0.10$).
- **Analysis 2 (Step 8 v3 / Research Suite):** Reported $37$ total errors, with selective review capturing $34$ errors ($91.9\%$) at a $10.0\%$ review budget ($K = 172$).

### Forensic Verdict:
The two analyses evaluated **two different model checkpoint generations** on the same $1,725$-image image population:
1. **The 127-error baseline** was generated in **Notebook Step 11** by the **early unrefined EfficientNet-B0 v1 baseline** evaluated prior to hyperparameter optimization (Accuracy: $92.64\%$, Recall: $89.98\%$, $126$ False Negatives, $1$ False Positive).
2. **The 37-error baseline** was generated in **Notebook Step 8 v3** by the final fine-tuned **EfficientNet-B0 v3 model** (`best_model.pt`, SHA-256: `f470b7...`), which incorporated data augmentations and unfreezing (Accuracy: $97.86\%$, Recall: $97.06\%$, $37$ False Negatives, $0$ False Positives).

> [!CAUTION]
> **Scientific Finding:** Comparing the $48.0\%$ error capture rate from the v1 baseline against the $37$-error v3 baseline or PatchCore as if they were evaluated on the same predictions constitutes a **methodological violation (incompatible prediction populations)**. Both experiments are valid for their respective checkpoints, but they must be reported in distinct provenance ledgers.

---

## 2. Forensic Trace of Evaluation Populations & Checkpoints

```
[MVTec AD Official Test Population: N = 1,725 images (1,258 Defective, 467 Normal)]
                                     |
       +-----------------------------+-----------------------------+
       |                                                           |
       v                                                           v
[POPULATION A: Step 11 Uncertainty Log]         [POPULATION B: Step 8 v3 Common Test Log]
- Model: EfficientNet-B0 (Early v1 Baseline)    - Model: EfficientNet-B0 (v3 Checkpoint)
- Checkpoint: Early unrefined weights           - Checkpoint: best_model.pt (SHA-256: f470b7...)
- Artifact: logs/step11_uncertainty_log.csv     - Artifact: logs/step8_efficientnet_on_common_testset.csv
- Artifact SHA-256: ba6f1b4169a6b18be...        - Artifact SHA-256: a57cd507ef65ce8da...
- Total Errors: 127 (FN=126, FP=1)              - Total Errors: 37 (FN=37, FP=0)
- Model Accuracy: 92.64%                        - Model Accuracy: 97.86%
- Model Recall: 89.98%                          - Model Recall: 97.06%
```

---

## 3. Comprehensive Provenance Ledger: Population by Population

### Ledger Entry 1: Population A (Step 11 Early v1 Baseline)

| Parameter | Recorded Value / Metadata |
| :--- | :--- |
| **Dataset & Split** | MVTec AD Official Test Split ($15$ Categories) |
| **Prediction Artifact** | `DefectVisionAI/logs/step11_uncertainty_log.csv` |
| **Artifact SHA-256** | `ba6f1b4169a6b18be1a0b82133ae1988007374f2108988c53be06d153cec80fc` |
| **Summary Report Artifact**| `DefectVisionAI/reports/step11_threshold_sensitivity.csv` (SHA-256: `5cf37a08...`) |
| **Model Evaluated** | EfficientNet-B0 v1 (Early PyTorch checkpoint, Step 11) |
| **Total Evaluated Images** | $1,725$ |
| **Ground Truth Distribution**| Defective: $1,258$, Normal: $467$ |
| **Baseline Accuracy** | $92.64\%$ ($1,598 / 1,725$) |
| **Baseline Error Count ($E_0$)**| **$127$ Total Errors** |
| **Error Composition** | False Negatives ($\text{FN}_0$): $126$, False Positives ($\text{FP}_0$): $1$ |
| **Selection Algorithm** | Supervised Margin Uncertainty: $u(p) = 1.0 - \|2p - 1.0\|$ |
| **Selection Mode 1 (Threshold)**| Score-threshold filter: $u(p) \ge 0.10$ |
| **Threshold Flagged Images** | $168$ ($9.74\%$ of dataset) |
| **Threshold Errors Captured**| $61 / 127$ (**$48.03\%$ Error Capture Rate**) |
| **Threshold Escapes Captured**| $60 / 126$ (**$47.62\%$ Defect Escape Reduction**) |
| **Selection Mode 2 (Budget)** | Fixed Review Budget $B = 10.0\%$ (Top $K = 172$ ranked by $u$) |
| **Fixed Budget Errors Captured**| $64 / 127$ (**$50.39\%$ Error Capture Rate**) |
| **Fixed Budget Escapes Captured**| $63 / 126$ (**$50.00\%$ Defect Escape Reduction**) |
| **Random Seed** | Stratified split seed: `42` |

---

### Ledger Entry 2: Population B (Step 8 v3 Production Model)

| Parameter | Recorded Value / Metadata |
| :--- | :--- |
| **Dataset & Split** | MVTec AD Official Test Split ($15$ Categories) |
| **Prediction Artifact** | `DefectVisionAI/logs/step8_efficientnet_on_common_testset.csv` |
| **Artifact SHA-256** | `a57cd507ef65ce8da77ce4cfc95647a8c0d865d59ebaca8425b3d6f5e0483ad1` |
| **Model Checkpoint** | `DefectVisionAI/models/efficientnet_baseline_v3/best_model.pt` |
| **Checkpoint SHA-256** | `f470b76d7c00df5be88236d552b3406256a60ee2c27fca361b981fce88902ba8` |
| **Total Evaluated Images** | $1,725$ |
| **Ground Truth Distribution**| Defective: $1,258$, Normal: $467$ |
| **Baseline Accuracy** | $97.86\%$ ($1,688 / 1,725$) |
| **Baseline Error Count ($E_0$)**| **$37$ Total Errors** |
| **Error Composition** | False Negatives ($\text{FN}_0$): $37$, False Positives ($\text{FP}_0$): $0$ |
| **Selection Algorithm** | Supervised Margin Uncertainty: $u(p) = 1.0 - \|2p - 1.0\|$ |
| **Selection Mode (Budget)** | Fixed Review Budget $B = 10.0\%$ (Top $K = 172$ ranked by $u$) |
| **Fixed Budget Errors Captured**| $34 / 37$ (**$91.89\%$ Error Capture Rate**) |
| **Fixed Budget Escapes Captured**| $34 / 37$ (**$91.89\%$ Defect Escape Reduction**) |
| **Bootstrap 95% CI (1,000 runs)**| Mean: $89.92\%$, CI: $[78.79\%, 97.83\%]$ |
| **PatchCore Distance Baseline** | Distance to Threshold captures $8 / 37$ (**$21.62\%$ ECR**) |
| **Random Selection Baseline** | Uniform Random captures $3 / 37$ (**$8.11\%$ ECR**) |
| **Random Seed** | Default RNG seed: `42` |

---

### Ledger Entry 3: Population C (Step 8 v3 on 856-Image Benchmark Partition)

| Parameter | Recorded Value / Metadata |
| :--- | :--- |
| **Dataset & Split** | MVTec AD Disjoint Benchmark Partition ($N = 856$) |
| **Prediction Artifact** | `DefectVisionAI/logs/step8_efficientnet_v3_on_benchmark.csv` |
| **Artifact SHA-256** | `31a2551e7ed6e637466d9eb5ed54777ccb93ff9783f0f6c61aaf13b6e295f655` |
| **Model Checkpoint** | `DefectVisionAI/models/efficientnet_baseline_v3/best_model.pt` (`f470b7...`) |
| **Total Evaluated Images** | $856$ |
| **Ground Truth Distribution**| Defective: $625$, Normal: $231$ (or $640$ Defective, $216$ Normal in Step 8 v3) |
| **Baseline Accuracy** | $86.92\%$ ($744 / 856$) |
| **Baseline Error Count ($E_0$)**| **$112$ Errors** ($111$ FN, $1$ FP) |
| **Macro-Category AUROC** | $0.9732$ (Exact verified value) |
| **Pooled AUROC** | $0.9809$ |
| **Methodological Status** | Disjoint development-evaluated partition; previously exposed in Step 8 v1 |

---

## 4. Synthesis & Scientific Guidelines for Publication

1. **Never Mix Populations:**
   - When discussing the historical $48.0\%$ error capture at $\tau \ge 0.10$, explicitly cite:  
     `"Evaluated on early EfficientNet-B0 v1 baseline (127 errors across 1,725 images, artifact ba6f1b...)"`.
   - When discussing the $91.89\%$ error capture at $10\%$ budget, explicitly cite:  
     `"Evaluated on fine-tuned EfficientNet-B0 v3 (37 errors across 1,725 images, artifact a57cd5...)"`.
2. **Denominators Must Be Declared:**
   Every selective review table must state:
   - Total population ($N$)
   - Total base errors ($E_0$)
   - Base false negatives ($\text{FN}_0$)
   - Exact review budget ($B$) and count ($K$)
3. **CPND Remains Proposed:**
   Neither Population A, Population B, nor Population C evaluated Calibrated Patch-Neighborhood Dispersion (CPND). CPND remains an unwritten algorithm. Any future paper must implement CPND and evaluate it strictly on an unexposed test set against the verified $21.62\%$ distance-to-threshold baseline.
