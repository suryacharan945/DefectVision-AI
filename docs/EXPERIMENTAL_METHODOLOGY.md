# DefectVision AI — Experimental Methodology & Statistical Protocol
**Release:** v1.0.0-rc1 (Research Prototype)  
**Date:** 2026-11-19  

---

## 1. Evaluation Metrics

DefectVision AI evaluates industrial visual surface inspection performance using standard computer vision and statistical measures:

### 1.1 Anomaly Classification Metrics
- **False Positive Rate (FPR):**
  $$\text{FPR} = \frac{\text{FP}}{\text{FP} + \text{TN}}$$
- **Defect Recall (True Positive Rate):**
  $$\text{Recall} = \frac{\text{TP}}{\text{TP} + \text{FN}}$$
- **Precision:**
  $$\text{Precision} = \frac{\text{TP}}{\text{TP} + \text{FP}}$$
- **F1-Score:**
  $$\text{F1} = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$$
- **Area Under the ROC Curve (AUROC):** Measures threshold-independent classification separability across all possible operating thresholds.

---

## 2. Few-Shot Adaptation Protocol

To investigate model sample efficiency when introducing new SKUs or manufacturing lines, a $K$-shot adaptation protocol was developed ($K \in \{5, 10, 20\}$):

1. **Reference Normal Units ($K$-shot):** $K$ nominal units are sampled without replacement to construct the candidate memory bank $\mathcal{M}_K$.
2. **Independent Calibration Set ($N_{\text{cal}} = 10$):** A strictly disjoint set of 10 nominal units is passed through feature extraction to establish the decision threshold.
3. **A Priori Frozen Threshold Rule:**
   $$\tau_{\text{a\_priori}} = \max_{i \in \text{cal}} s(I_i)$$
   This threshold is established solely on calibration data before any test specimen is inspected.
4. **Evaluation Set ($N_{\text{test}} = 83$):** 20 unseen nominal bottles and 63 genuine defect specimens (broken large, broken small, contamination).

---

## 3. Threshold Leakage Audit Methodology

In research Sprint 2.4, an independent threshold leakage audit was conducted to investigate post-hoc multiplier tuning:

1. **Multiplier Sweep:** Multipliers from $1.00\times$ to $1.25\times$ in increments of $0.05$ were evaluated against test scores:
   $$\tau_m = \max(S_{\text{cal}}) \times m$$
2. **Identification of Leakage:** Multiplier $1.20\times$ ($\tau = 1.7449$) was selected post-hoc because it bridged the gap between the highest normal test bottle ($1.7129$) and the lowest defect bottle ($1.8212$).
3. **Formal Policy:** Any threshold policy derived or adjusted after observing test set scores is formally classified as a **`DEVELOPMENT-SET RESULT`** and prohibited from production deployment.

---

## 4. Statistical Confidence Intervals & The Rule of Three

To prevent overinterpreting zero-error observations on small test cohorts, formal confidence bounds are computed:

### 4.1 Wilson Score Interval for Proportions
For observed success rate $\hat{p} = k / n$:
$$CI_{95\%} = \frac{\hat{p} + \frac{z^2}{2n} \pm z \sqrt{\frac{\hat{p}(1-\hat{p})}{n} + \frac{z^2}{4n^2}}}{1 + \frac{z^2}{n}}$$
where $z = 1.96$ for a two-sided $95\%$ confidence level.

### 4.2 The Rule of Three for Zero Events ($k=0$)
When zero false positives are observed ($k=0$) across $n$ independent normal units, the standard point estimate $\hat{p} = 0\%$ is deceptively precise. The one-sided $95\%$ upper confidence bound is approximated by:
$$p_{\text{upper}} \approx \frac{3}{n}$$
- For $n = 20$ normal test units: $p_{\text{upper}} \approx \frac{3}{20} = \mathbf{15.00\%}$.
- For $n = 26$ normal test units: $p_{\text{upper}} \approx \frac{3}{26} = \mathbf{11.54\%}$.
- To certify an industrial false alarm rate $< 1.0\%$ with $95\%$ confidence:
  $$n \ge \frac{3}{0.01} = \mathbf{300 \text{ independent normal specimens}}.$$
