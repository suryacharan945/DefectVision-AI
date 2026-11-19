# DefectVision AI — Key Results and Empirical Limitations

**Milestone:** `v1.0.0-rc1`  
**Dataset:** MVTec Anomaly Detection (15 Industrial Categories, $N=1,725$ Test Specimens)  
**Status:** `RELEASE READY WITH DOCUMENTED METRIC LIMITATIONS`

---

## 1. Executive Metric Summary

The performance of DefectVision AI `v1.0.0-rc1` is characterized by high ranking and localization capability alongside a documented operational false-alarm trade-off:

- **Macro Image AUROC:** **97.15%** (unweighted arithmetic mean across 15 categories)
- **Macro Image AUPRC:** **98.98%**
- **Mean Pixel Localization AUROC:** **98.02%**
- **Category Routing Accuracy (15 Classes):** **99.94%** (1,724 / 1,725 correct)
- **Micro Operational Defect Recall:** **94.04%** (1,183 / 1,258 defects detected; 75 escapes)
- **Micro False Positive Rate (FPR):** **24.84%** (116 / 467 nominal specimens flagged)
- **Micro Operational Precision:** **91.07%** (1,183 / 1,299 alerts are genuine)
- **Micro Operational F1 Score:** **0.9253**
- **Overall Operational Accuracy:** **88.93%** (1,534 / 1,725 correct verdicts at $\tau = 1.50$)

---

## 2. Disaggregated 15-Category Benchmark Performance

To prevent masking weaker categories behind global averages, every category is reported without omission:

| Category | Type | Normal ($N$) | Defect ($N$) | Total ($N$) | Image AUROC | Image AUPRC | FPR (%) | Recall (%) | Precision (%) | F1-Score |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **bottle** | Object | 20 | 63 | 83 | **100.00%** | 100.00% | 0.00% | 100.00% | 100.00% | **1.0000** |
| **cable** | Object | 58 | 92 | 150 | **98.76%** | 99.18% | 3.45% | 90.22% | 97.65% | **0.9379** |
| **capsule** | Object | 23 | 109 | 132 | **94.20%** | 98.48% | 21.74% | 89.91% | 95.15% | **0.9245** |
| **carpet** | Texture | 28 | 89 | 117 | **96.55%** | 99.02% | 3.57% | 86.52% | 98.72% | **0.9222** |
| **grid** | Texture | 21 | 57 | 78 | **95.07%** | 98.33% | 28.57% | 96.49% | 90.16% | **0.9322** |
| **hazelnut** | Object | 40 | 70 | 110 | **100.00%** | 100.00% | 0.00% | 98.57% | 100.00% | **0.9928** |
| **leather** | Texture | 32 | 92 | 124 | **100.00%** | 100.00% | 62.50% | 100.00% | 82.14% | **0.9020** |
| **metal_nut** | Object | 22 | 93 | 115 | **99.56%** | 99.90% | 18.18% | 98.92% | 95.83% | **0.9735** |
| **pill** | Object | 26 | 141 | 167 | **90.96%** | 98.13% | 23.08% | 82.98% | 95.12% | **0.8864** |
| **screw** | Object | 41 | 119 | 160 | **95.80%** | 98.49% | 14.63% | 88.24% | 94.59% | **0.9130** |
| **tile** | Texture | 33 | 84 | 117 | **99.75%** | 99.90% | 66.67% | 100.00% | 79.25% | **0.8842** |
| **toothbrush** | Object | 12 | 30 | 42 | **92.50%** | 96.61% | 75.00% | 100.00% | 76.92% | **0.8696** |
| **transistor** | Object | 60 | 40 | 100 | **99.21%** | 98.69% | 21.67% | 100.00% | 75.47% | **0.8602** |
| **wood** | Texture | 19 | 60 | 79 | **99.65%** | 99.90% | 68.42% | 100.00% | 82.19% | **0.9023** |
| **zipper** | Object | 32 | 119 | 151 | **95.19%** | 98.08% | 28.12% | 99.16% | 92.91% | **0.9593** |
| **Macro Average** | — | **467** | **1,258** | **1,725** | **97.15%** | **98.98%** | **29.04%** | **95.40%** | **90.41%** | **0.9240** |

---

## 3. Analysis of the AUROC vs. False-Positive Rate Disconnect

A central insight from the audit is that **a high AUROC (97.15%) does not guarantee a low operational false alarm rate (24.84%)**:
1. **AUROC is a Threshold-Independent Ranking Metric:** AUROC measures the probability that a randomly chosen defective image scores higher than a randomly chosen nominal image. It evaluates ranking quality across *all* possible decision thresholds.
2. **Fixed Operational Thresholding:** In factory operations, a single fixed decision threshold $\tau$ must be applied. At $\tau = 1.50$, texture categories with organic surface variability (`tile`, `wood`, `leather`) and non-rigid rigid objects (`toothbrush`) exhibit nominal patch distances that cross the threshold, driving category-level FPR up to 60%–75%.
3. **Operational Recommendation:** Factories deploying PatchCore must calibrate **category-specific thresholds** using operational cost matrices (balancing the cost of an escape against the cost of a false line stoppage), rather than applying a global static threshold.

---

## 4. Few-Shot Adaptation Performance

Few-shot enrollment was evaluated on the `bottle` category across 83 held-out test specimens (20 nominal, 63 defective):

```
+---------------------------------------------------------------------------------------------+
| Adaptation Regime   | Threshold Policy               | Recall    | FPR    | F1     | Status  |
+---------------------+--------------------------------+-----------+--------+--------+---------+
| Full Memory Bank    | Frozen baseline (tau = 1.50)   | 100.00%   | 20.00% | 0.9692 | Valid   |
| K = 10 Few-Shot     | Frozen candidate (tau = 1.50)  |  96.83%   |  0.00% | 0.9839 | Valid   |
| K = 20 Few-Shot     | Frozen baseline (tau = 1.50)   | 100.00%   | 20.00% | 0.9692 | Valid   |
| K = 20 Few-Shot     | Post-hoc 1.25x (tau = 1.875)   |  98.41%   |  0.00% | 0.9841 | Ablation|
+---------------------------------------------------------------------------------------------+
```

### Critical Findings:
- At $K=10$, the memory bank successfully covers core structural normality while filtering boundary noise, achieving **96.83% defect recall** (61/63 defects caught) and **0% observed false alarms** (0/20) under frozen $\tau = 1.50$.
- Two defects missed at $K=10$ were subtle hairline contamination streaks that fell below $\tau = 1.50$.
- The $K=20$ post-hoc threshold adjustment ($1.25\times \implies \tau = 1.875$) achieved 98.41% recall and 0% FPR. However, because this multiplier was tuned directly on the test set, it is categorized strictly as an exploratory ablation and excluded from release candidate claims.

---

## 5. Statistical Reliability Limits (Clopper–Pearson & Wilson)

Small evaluation samples can create an illusion of perfection. When 0 false alarms are observed among $n=20$ normal test images ($k=0$):
- **Point Estimate:** $\hat{p} = 0.00\%$
- **Exact Clopper–Pearson 95% Confidence Interval:** $[0.00\%, 16.84\%]$
- **Wilson Score 95% Confidence Interval:** $[0.00\%, 16.11\%]$
- **Rule of Three ($3/n$):** $\frac{3}{20} = 15.00\%$

**Engineering Implication:** The true underlying false alarm rate could be as high as $16.84\%$ despite zero observed errors in a sample of 20 images. To statistically prove that a manufacturing line achieves $\text{FPR} \le 1.0\%$ at $\alpha = 0.05$, a minimum sample size of **$N \ge 300$ independent nominal specimens** without a single error is mathematically mandatory:
$$N \ge \frac{-\ln(0.05)}{0.01} \approx 299.6$$

---

## 6. External Domain Shift & Track B Limitations

During Sprint 2.3 and 2.4, an adaptation experiment on uncalibrated smartphone captures (Track B) was attempted. The experiment revealed:
1. **Severe Specimen Deficit:** Only 1 distinct physical defective unit was available. Repeated image captures of the same physical unit do not constitute independent statistical evidence.
2. **Environmental Domain Shift:** Uncontrolled ambient illumination, variable white balance, and lens distortion cause nominal patch features to shift outside the MVTec-trained manifold, elevating baseline distances.
3. **Formal Release Verdict:** Track B adaptation is formally classified as **UNVALIDATED** and is not certified for production deployment. DefectVision AI `v1.0.0-rc1` is certified strictly for controlled industrial machine vision environments matching the MVTec AD acquisition standard.
