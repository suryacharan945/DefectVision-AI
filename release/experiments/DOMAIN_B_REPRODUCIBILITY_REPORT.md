# DEFECTVISION AI 2.2 — DOMAIN B REPRODUCIBILITY REPORT

**Evaluation Target:** Reproduction of Domain B (Controlled External Studio Bottles) Adaptation Experiment  
**Audited Models:**
- **Model A:** Original MVTec PatchCore Baseline (Memory bank: 15,680 patches, $\tau = 1.4666$)
- **Model B:** Adapted Profile `bottle_sku_btl_adapt_002` (Memory bank: 392 patches, provisional $\tau = 1.6410$)  
**Specimens Evaluated:** 3 Physical Objects ($N=3$: 2 Nominal, 1 Defective)  
**Evaluation Status:** REPRODUCED WITH METHODOLOGICAL CAVEATS (Exploratory Proof of Feasibility)

---

## 1. Experimental Methodology & Control Verification

### A. Strict Parity Checks
- **Test Image Paths & Hashes:** Identical across both model runs.
- **Preprocessing:** Identical $224 \times 224$ bicubic resize, ImageNet RGB normalization (Mean: $[0.485, 0.456, 0.406]$, Std: $[0.229, 0.224, 0.225]$).
- **Backbone Feature Extractor:** Frozen PyTorch ResNet18 (layers 2 + 3, grid size 28). Both models executed on the same device with 3 warm-up passes.
- **Model Freezing:** Neither model memory bank nor threshold was modified during this experiment.

### B. Critical Lineage & Data Leakage Audit
- **Normal Specimen 1 (`clear bottle.jpg`):** **PRESENT in training set** of `bottle_sku_btl_adapt_002` ($1$ of $5$ training images).
- **Normal Specimen 2 (`clear bottle2.webp`):** **PRESENT in training set** of `bottle_sku_btl_adapt_002` ($1$ of $5$ training images).
- **Defective Specimen (`disordered bottle.webp`):** **STRICTLY HELD-OUT.** Excluded from training and calibration of both models.
> **Scientific Finding:** While the experiment reproduces the reported scores, the performance of `bottle_sku_btl_adapt_002` on the two normal specimens reflects **in-sample memory-bank retrieval (train-set evaluation)** rather than out-of-sample physical generalization. Truly independent target-domain normal bottles do not currently exist in the repository.

---

## 2. Per-Specimen Telemetry & Quantitative Comparison

| Specimen ID | Filename | Ground Truth | Train Overlap? | Model A (Baseline MVTec) | Model B (Adapted `btl_adapt_002`) |
|:---|:---|:---:|:---:|:---:|:---:|
| `EXT-BTL-001` | `clear bottle.jpg` | **NORMAL** | Train in Adapt | Score: **4.7829** (Threshold: 1.4666)<br>Verdict: **DEFECTIVE** (False Alarm)<br>Latency: 156.92 ms | Score: **1.3947** (Threshold: 1.641)<br>Verdict: **NORMAL** (True Neg)<br>Latency: 44.61 ms |
| `EXT-BTL-002` | `clear bottle2.webp` | **NORMAL** | Train in Adapt | Score: **5.1506** (Threshold: 1.4666)<br>Verdict: **DEFECTIVE** (False Alarm)<br>Latency: 153.5 ms | Score: **1.3842** (Threshold: 1.641)<br>Verdict: **NORMAL** (True Neg)<br>Latency: 42.88 ms |
| `EXT-BTL-003` | `disordered bottle.webp` | **DEFECTIVE** | Held-Out | Score: **4.1222** (Threshold: 1.4666)<br>Verdict: **DEFECTIVE** (True Pos)<br>Latency: 164.42 ms | Score: **3.9916** (Threshold: 1.641)<br>Verdict: **DEFECTIVE** (True Pos)<br>Latency: 102.13 ms |

---

## 3. Summary Performance Metrics & Statistical Limits

| Metric | Model A: Baseline MVTec | Model B: Adapted `btl_adapt_002` | Formula / Ratio |
|:---|:---:|:---:|:---|
| **True Positives (TP)** | 1 | 1 | Defective identified as DEFECTIVE |
| **False Positives (FP)** | 2 | 0 | Normal identified as DEFECTIVE |
| **True Negatives (TN)** | 0 | 2 | Normal identified as NORMAL |
| **False Negatives (FN)** | 0 | 0 | Defective identified as NORMAL |
| **Precision** | **0.3333** ($1/3$) | **1.0000** ($1/1$) | $\frac{\text{TP}}{\text{TP} + \text{FP}}$ |
| **Recall (Sensitivity)** | **1.0000** ($1/1$) | **1.0000** ($1/1$) | $\frac{\text{TP}}{\text{TP} + \text{FN}}$ |
| **Specificity** | **0.0000** ($0/2$) | **1.0000** ($2/2$) | $\frac{\text{TN}}{\text{TN} + \text{FP}}$ |
| **F1 Score** | **0.5000** | **1.0000** | $2 \cdot \frac{\text{Prec} \cdot \text{Rec}}{\text{Prec} + \text{Rec}}$ |
| **Accuracy** | **33.3%** ($1/3$) | **100.0%** ($3/3$) | $\frac{\text{TP} + \text{TN}}{N}$ |
| **False Positive Rate (FPR)** | **100.0%** ($2/2$) | **0.0%** ($0/2$) | $\frac{\text{FP}}{\text{FP} + \text{TN}}$ |
| **False Negative Rate (FNR)** | **0.0%** ($0/1$) | **0.0%** ($0/1$) | $\frac{\text{FN}}{\text{FN} + \text{TP}}$ |
| **AUROC** | $0.0000$ | $1.0000$ | Statistically Degenerate ($N=3$) |
| **Average Precision (AUPRC)** | $0.3333$ | $1.0000$ | Statistically Degenerate ($N=3$) |
| **Mean Inference Latency** | 158.28 ms | 63.21 ms | Nearest neighbor search duration |

---

## 4. Scientific Interpretation: What is Proven vs. Unproven

### A. What is Empirically Proven
1. **Baseline MVTec Catastrophic False Alarm Rate Under Studio Lighting:**
   Baseline MVTec yields anomaly distances of **$4.7829$** and **$5.1506$** on normal studio bottles, more than $3.5 \times$ higher than its threshold ($1.4666$). Baseline PatchCore completely fails when transferred across camera and studio environments without adaptation.
2. **Adapted Centroid Retrieval Eliminates Studio Distance Blowup:**
   The adapted model successfully embeds the studio background and lighting into its centroid bank, reducing normal distances from $\sim 5.0$ down to $1.39$ and $1.38$.
3. **Defect Signal Resilience:**
   The physical fracture on `disordered bottle.webp` produces an anomaly distance of **$3.9916$**, exceeding the provisional threshold ($1.6410$) by **$2.43 \times$**. The defect remains easily detectable even with target studio adaptation.

### B. What Remains Scientifically Unproven
1. **Generalization Cannot be Established from $N=3$ Specimens:**
   Reporting "100% precision and recall" on a 3-specimen test containing 2 train-set images is methodologically invalid as a generalization claim.
2. **AUROC and AUPRC are Statistically Meaningless at $N=3$:**
   With only 1 positive and 2 negative samples, a single ordering inversion swings AUROC from $1.00$ to $0.00$.
3. **True False Positive Rate is Unknown:**
   Until independent, unseen nominal studio bottles are captured and evaluated, the true production false alarm rate cannot be reported.

### C. Formal Reproducibility Classification
This result is formally classified as:
**EXPLORATORY EVIDENCE OF PRODUCT-SPECIFIC DOMAIN ADAPTATION.**  
It proves the architectural feasibility of few-shot adaptation to overcome severe camera-shift false alarms, but does not constitute certified proof of production reliability.
