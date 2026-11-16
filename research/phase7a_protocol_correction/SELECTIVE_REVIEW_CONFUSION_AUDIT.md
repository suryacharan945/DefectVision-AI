# Forensic Confusion Matrix Audit: 1,725-Image Evaluation

**Document ID:** `DV-AUDIT-CONFUSION-MATRIX-V1`  
**Audit Date:** October 31, 2026  
**Auditor:** Lead AI/ML Research Engineer & Experimental Methodology Reviewer  
**Scope:** Numerical reconciliation of conflicting confusion matrix breakdowns across historical logs and release reports  

---

## 1. Executive Summary & Core Discrepancy Resolution

This audit investigates the conflicting error compositions reported for the 1,725-image MVTec AD evaluation:
- **Prior Verified Audit:** Total errors = $127$, False Negatives = $126$, False Positives = $1$.
- **Subsequent Textual Summary:** Total errors = $127$, False Negatives = $68$, False Positives = $59$.

### Formal Forensic Verdict:
1. **The physical prediction artifact definitively contains $\mathbf{FN = 126}$ and $\mathbf{FP = 1}$.**  
   Direct execution of `scripts/calculate_exact_cm.py` on the immutable log file [`DefectVisionAI/logs/step11_uncertainty_log.csv`](file:///c:/Users/surya/Downloads/Mini%20Project/DefectVisionAI/logs/step11_uncertainty_log.csv) (SHA-256: `ba6f1b4169a6b18be1a0b82133ae1988007374f2108988c53be06d153cec80fc`) yields:
   $$\text{TP} = 1,132, \quad \text{TN} = 466, \quad \mathbf{FP = 1}, \quad \mathbf{FN = 126}$$
   $$\text{Total Errors} = \text{FP} + \text{FN} = 1 + 126 = 127$$
   $$\text{Accuracy} = \frac{1,132 + 466}{1,725} = 92.6377\%$$
   $$\text{Precision} = \frac{1,132}{1,133} = 99.9117\%, \quad \text{Recall} = \frac{1,132}{1,258} = 89.9841\%$$

2. **The "68 FN / 59 FP" breakdown was an unverified textual artifact.**  
   An exhaustive parametric grid search across all 19 log files and probability thresholds confirmed that no combination of predictions or decision thresholds in the repository produces $68$ false negatives and $59$ false positives. That breakdown was erroneously introduced into an intermediate conversational summary.

---

## 2. Reconstructed Confusion Matrices by Model Checkpoint

Below is the verified, zero-assumption reconstruction of each model evaluation on the MVTec AD evaluation populations:

### Experiment 1: Early EfficientNet-B0 v1 (Active Learning & Uncertainty Population)
- **Log Artifact:** `DefectVisionAI/logs/step11_uncertainty_log.csv`
- **Artifact SHA-256:** `ba6f1b4169a6b18be1a0b82133ae1988007374f2108988c53be06d153cec80fc`
- **Model Checkpoint:** Early EfficientNet-B0 (Binary classification head, Step 11 execution)
- **Population:** 1,725 images (1,258 Defective, 467 Normal)
- **Decision Rule:** `predicted_label = "defective" if prob_defective >= 0.50 else "normal"`

$$\begin{array}{|c|c|c|c|}
\hline
\textbf{N = 1,725} & \textbf{Pred: Defective} & \textbf{Pred: Normal} & \textbf{Total} \\
\hline
\textbf{True: Defective} & \text{TP} = 1,132 & \text{FN} = 126 & 1,258 \\
\hline
\textbf{True: Normal} & \text{FP} = 1 & \text{TN} = 466 & 467 \\
\hline
\textbf{Total} & 1,133 & 592 & 1,725 \\
\hline
\end{array}$$

- **Performance Metrics:**
  - **Accuracy:** $92.6377\%$ ($1,598 / 1,725$)
  - **Precision:** $99.9117\%$ ($1,132 / 1,133$)
  - **Recall:** $89.9841\%$ ($1,132 / 1,258$)
  - **Specificity:** $99.7859\%$ ($466 / 467$)
  - **Total Errors ($E_0$):** $127$ ($126$ Defect Escapes, $1$ False Alarm)
- **Selective Review Results (Margin Uncertainty $u(p) = 1 - |2p - 1|$):**
  - **Threshold Filtering ($\tau \ge 0.10$):** Flags $168$ images ($9.74\%$ of dataset).
    - Errors Captured: $61 / 127$ (**$48.03\%$ Error Capture Rate**).
    - Defect Escapes Captured: $60 / 126$ (**$47.62\%$ Defect Escape Reduction**).
    - False Alarms Captured: $1 / 1$ (**$100.0\%$ False Positive Capture**).
  - **Budget Bounded ($B = 10.0\%$, Top $K = 172$):**
    - Errors Captured: $64 / 127$ (**$50.39\%$ Error Capture Rate**).
    - Defect Escapes Captured: $63 / 126$ (**$50.00\%$ Defect Escape Reduction**).

---

### Experiment 2: Fine-Tuned EfficientNet-B0 v3 (Common Testset Benchmark)
- **Log Artifact:** `DefectVisionAI/logs/step8_efficientnet_on_common_testset.csv`
- **Artifact SHA-256:** `a57cd507ef65ce8da77ce4cfc95647a8c0d865d59ebaca8425b3d6f5e0483ad1`
- **Model Checkpoint:** `DefectVisionAI/models/efficientnet_baseline_v3/best_model.pt`
- **Checkpoint SHA-256:** `f470b76d7c00df5be88236d552b3406256a60ee2c27fca361b981fce88902ba8`
- **Population:** 1,725 images (1,258 Defective, 467 Normal)
- **Decision Rule:** `predicted_label = "defective" if prob_defective >= 0.50 else "normal"`

$$\begin{array}{|c|c|c|c|}
\hline
\textbf{N = 1,725} & \textbf{Pred: Defective} & \textbf{Pred: Normal} & \textbf{Total} \\
\hline
\textbf{True: Defective} & \text{TP} = 1,221 & \text{FN} = 37 & 1,258 \\
\hline
\textbf{True: Normal} & \text{FP} = 0 & \text{TN} = 467 & 467 \\
\hline
\textbf{Total} & 1,221 & 504 & 1,725 \\
\hline
\end{array}$$

- **Performance Metrics:**
  - **Accuracy:** $97.8551\%$ ($1,688 / 1,725$)
  - **Precision:** $100.0000\%$ ($1,221 / 1,221$)
  - **Recall:** $97.0588\%$ ($1,221 / 1,258$)
  - **Specificity:** $100.0000\%$ ($467 / 467$)
  - **Total Errors ($E_0$):** $37$ ($37$ Defect Escapes, $0$ False Alarms)
- **Selective Review Results (Fixed Budget $B = 10.0\%$, Top $K = 172$):**
  - **Supervised Margin Uncertainty ($1 - |2p - 1|$):** Captures $34 / 37$ errors (**$91.89\%$ ECR**, $95\%\text{ CI: }[78.79\%, 97.83\%]$).
  - **PatchCore Distance to Category Threshold ($|s - \tau_c|$):** Captures $8 / 37$ errors (**$21.62\%$ ECR**).
  - **Uniform Random Baseline:** Captures $3 / 37$ errors (**$8.11\%$ ECR**).

---

### Experiment 3: Fine-Tuned EfficientNet-B0 v3 (856-Image Benchmark Split)
- **Log Artifact:** `DefectVisionAI/logs/step8_efficientnet_v3_on_benchmark.csv`
- **Model Checkpoint:** `DefectVisionAI/models/efficientnet_baseline_v3/best_model.pt`
- **Population:** 856 images (625 Defective, 231 Normal)
- **Reported in:** `DefectVisionAI/reports/step8_model_comparison_FAIR.csv`

$$\begin{array}{|c|c|c|c|}
\hline
\textbf{N = 856} & \textbf{Pred: Defective} & \textbf{Pred: Normal} & \textbf{Total} \\
\hline
\textbf{True: Defective} & \text{TP} = 514 & \text{FN} = 111 & 625 \\
\hline
\textbf{True: Normal} & \text{FP} = 1 & \text{TN} = 230 & 231 \\
\hline
\textbf{Total} & 515 & 341 & 856 \\
\hline
\end{array}$$

- **Performance Metrics:**
  - **Accuracy:** $86.9159\%$ ($744 / 856$)
  - **Precision:** $99.8058\%$ ($514 / 515$)
  - **Recall:** $82.2400\%$ ($514 / 625$)
  - **Specificity:** $99.5671\%$ ($230 / 231$)
  - **Total Errors ($E_0$):** $112$ ($111$ Defect Escapes, $1$ False Alarm)

---

### Experiment 4: PatchCore (Nominal-Only Unsupervised, 1,725 Images)
- **Log Artifact:** `DefectVisionAI/logs/step7_patchcore_inference_log.csv`
- **Population:** 1,725 images (1,258 Defective, 467 Normal)
- **Reported Metrics in `step8_model_comparison.csv`:**
  - AUROC: $0.9715$, Accuracy: $74.90\%$, Precision: $98.02\%$, Recall: $66.93\%$, F1: $0.7955$.
- **Reconstructed Confusion Matrix (at reported default decision thresholds):**

$$\begin{array}{|c|c|c|c|}
\hline
\textbf{N = 1,725} & \textbf{Pred: Defective} & \textbf{Pred: Normal} & \textbf{Total} \\
\hline
\textbf{True: Defective} & \text{TP} = 842 & \text{FN} = 416 & 1,258 \\
\hline
\textbf{True: Normal} & \text{FP} = 17 & \text{TN} = 450 & 467 \\
\hline
\textbf{Total} & 859 & 866 & 1,725 \\
\hline
\end{array}$$

- **Total Errors:** $416 + 17 = 433$ errors.
- **Accuracy:** $\frac{842 + 450}{1,725} = 74.8986\%$.
- **Precision:** $\frac{842}{859} = 98.0210\%$.
- **Recall:** $\frac{842}{1,258} = 66.9316\%$.

---

## 3. Comparative Summary Table

| Metric | Exp 1: Baseline v1 (`step11`) | Exp 2: Fine-Tuned v3 (`step8_common`) | Exp 3: Fine-Tuned v3 (`step8_benchmark`) | Exp 4: PatchCore (`step7`) |
| :--- | :---: | :---: | :---: | :---: |
| **Population ($N$)** | 1,725 | 1,725 | 856 | 1,725 |
| **True Defective / Normal** | 1,258 / 467 | 1,258 / 467 | 625 / 231 | 1,258 / 467 |
| **True Positives (TP)** | 1,132 | 1,221 | 514 | 842 |
| **True Negatives (TN)** | 466 | 467 | 230 | 450 |
| **False Positives (FP)** | **1** | **0** | **1** | **17** |
| **False Negatives (FN)** | **126** | **37** | **111** | **416** |
| **Total Errors** | **127** | **37** | **112** | **433** |
| **Accuracy** | 92.64% | 97.86% | 86.92% | 74.90% |
| **Precision** | 99.91% | 100.00% | 99.81% | 98.02% |
| **Recall** | 89.98% | 97.06% | 82.24% | 66.93% |
| **10% Review ECR** | **48.03%** ($\tau \ge 0.1$) | **91.89%** (Margin) | N/A | **21.62%** ($|s - \tau|$) |

---

## 4. Audit Conclusions

1. **Definitive Provenance:** The 127-error baseline belongs strictly to the early EfficientNet-B0 v1 model in Step 11, with exactly **126 False Negatives and 1 False Positive**.
2. **Error Hallucination Clarification:** The "68 FN / 59 FP" breakdown is mathematically refuted by the raw log data and is formally retracted from project records.
3. **No Cross-Population Mixing:** The 37 errors ($37$ FN, $0$ FP) of the fine-tuned v3 model must never be directly compared with the 127 errors ($126$ FN, $1$ FP) of the v1 model without explicitly stating they represent different checkpoint iterations.
