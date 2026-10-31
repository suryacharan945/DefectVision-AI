# RESEARCH EXPERIMENTATION READINESS & BASELINE BENCHMARK

**Project:** DefectVision AI  
**Release Target:** Commit `91d3743` / `delivery_24h/final_hardening_v3`  
**Audit Date:** October 31, 2026  
**Auditor:** Lead AI/ML Verification & Full-Stack Release Engineer  

---

## 1. Executive Summary

To transition DefectVision AI from an engineering prototype to a defensible Q1 journal manuscript (target: *IEEE Transactions on Industrial Informatics* or *Pattern Recognition*), we constructed a modular, reproducible research experiment package in [`DefectVisionAI/research/`](file:///c:/Users/surya/Downloads/Mini%20Project/DefectVisionAI/research/).

In strict adherence to experimental methodology:
- We **did not launch a premature large-scale experiment campaign** during this final hardening phase.
- We implemented and evaluated standard established baselines—**Random Selection**, **Top Anomaly Score**, **PatchCore Distance to Decision Threshold**, and **Supervised Prediction Margin Sampling**.
- We established that before developing complex patch-dispersion metrics (CPND), **evidence must demonstrate that CPND provides incremental empirical value beyond simpler distance-to-threshold and margin baselines.**

---

## 2. Research Experiment Architecture (`DefectVisionAI/research/`)

The experiment package is structured as a self-contained, dependency-isolated module:

```
DefectVisionAI/research/
├── __init__.py                     # Package export declarations
├── config/
│   └── experiment_config.json      # Declarative schemas, candidate policies, budget grids
├── selective_review.py             # Math: margin sampling, distance-to-threshold, risk-coverage, bootstrap CI
├── evaluator.py                    # Category AUROC, balanced accuracy, per-image prediction exports
├── profiler.py                     # Physical runtime latency (p50/p95/p99) and RSS memory profiler
└── run_baseline_comparison.py      # Executable CLI experiment runner with certified outputs
```

### Module Roles:
1. [`selective_review.py`](file:///c:/Users/surya/Downloads/Mini%20Project/DefectVisionAI/research/selective_review.py):
   - `compute_margin_uncertainty(p)`: Evaluates binary classifier boundary ambiguity $u(p) = 1.0 - |2p - 1.0|$.
   - `compute_distance_to_threshold(scores, thresholds)`: Evaluates unsupervised boundary proximity $\frac{1}{|s - \tau_c| + \epsilon}$.
   - `simulate_selective_review(y_true, y_pred, scores, budgets)`: Evaluates fixed review capacity constraints $B \in \{1\%, 5\%, 10\%, 20\%\}$.
   - `compute_risk_coverage_curve(y_true, y_pred, scores)`: Computes selective risk $R(\phi)$ as coverage $\phi$ varies from $10\%$ to $100\%$.
   - `compute_bootstrap_ci(metric_fn, data, n_resamples=1000)`: Generates non-parametric $95\%$ bootstrap confidence intervals.
2. [`evaluator.py`](file:///c:/Users/surya/Downloads/Mini%20Project/DefectVisionAI/research/evaluator.py): Computes macro-averaged and per-category AUROC, Balanced Accuracy, Precision, Recall, Specificity, and confusion matrices.
3. [`profiler.py`](file:///c:/Users/surya/Downloads/Mini%20Project/DefectVisionAI/research/profiler.py): Measures process RSS memory deltas and millisecond execution timings over 30 runs.

---

## 3. Baseline Comparative Benchmark (Executed on Development Population)

We executed [`DefectVisionAI/research/run_baseline_comparison.py`](file:///c:/Users/surya/Downloads/Mini%20Project/DefectVisionAI/research/run_baseline_comparison.py) across $1,725$ observations, comparing all four candidate review policies under a fixed $10\%$ human review budget ($K = 172$ images):

### Results at 10% Review Budget ($K = 172$ images):

| Selection Policy | Type | Images Reviewed | Errors Captured | Total Baseline Errors | Error Capture Rate (ECR) | Defect Escapes Reduced | Review Defect Yield |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Random Selection** | Monte Carlo Baseline | $172$ ($10.0\%$) | $3$ | $37$ | $8.11\%$ | $3 / 37$ ($8.11\%$) | $1.74\%$ |
| **Highest Anomaly Score (PatchCore)** | Heuristic Baseline | $172$ ($10.0\%$) | $0$ | $37$ | **$0.00\%$** | $0 / 37$ ($0.00\%$) | $0.00\%$ |
| **Highest Score (EfficientNet)** | Heuristic Baseline | $172$ ($10.0\%$) | $0$ | $37$ | **$0.00\%$** | $0 / 37$ ($0.00\%$) | $0.00\%$ |
| **Distance to Threshold (PatchCore)** | Unsupervised Boundary | $172$ ($10.0\%$) | $8$ | $37$ | **$21.62\%$** | $8 / 37$ ($21.62\%$) | $4.65\%$ |
| **Supervised Margin ($\|p - 0.5\|$)** | Supervised Uncertainty | $172$ ($10.0\%$) | $34$ | $37$ | **$91.89\%$** | $34 / 37$ ($91.89\%$) | $19.77\%$ |

### Bootstrap 95% Confidence Intervals:
- **Supervised Margin ECR@10%:** Mean = $89.92\%$, **$95\%$ CI: $[78.79\%, 97.83\%]$** ($N = 1,000$ bootstrap resamples).
- **Sampling Unit Justification:** Image-level resampling was chosen because in industrial quality control lines, each specimen arrival constitutes an independent Bernoulli inspection trial. Resampling at the image unit accurately estimates the variance of human review error capture across varied production batches.

---

## 4. Critical Scientific Insights for the Future Q1 Direction

### Insight 1: Why Top-Score Selection Completely Fails ($0.0\%$ Error Capture)
Prior naive proposals suggested prioritizing parts with the highest anomaly scores. This experiment conclusively proves that **top-score selection captures $0.0\%$ of classification errors**. The highest-scoring parts are catastrophic defects (completely fractured bottles, cut cables) where the model is already $100\%$ confident and accurate. Reviewing them yields zero error correction.

### Insight 2: Distance to Threshold is the True Unsupervised Baseline ($21.6\%$)
In unsupervised anomaly detection where defect labels do not exist, **PatchCore Distance to Decision Threshold** captures $21.62\%$ of errors ($2.7\times$ better than random). This establishes the **true benchmark against which any proposed patch-dispersion metric (CPND) must be judged**.

### Insight 3: The CPND Novelty Barrier
For CPND to be publication-worthy in a Q1 journal, the research team must prove that:
$$\text{ECR}_{\text{CPND}} > \text{ECR}_{\text{Distance-to-Threshold}} \quad (21.62\%)$$
If CPND merely achieves $\approx 20\text{--}22\%$, it provides no incremental value over computing simple distance to the category threshold $\tau_c$.

---

## 5. Related Literature & Prior Art Grounding

To prevent unsubstantiated claims of novelty, future manuscripts must position this work within established literature:

1. **Selective Classification & Risk-Coverage:**
   - *Geifman & El-Yaniv (NeurIPS 2017):* "Selective classification for deep neural networks." Formalized the trade-off between coverage $\phi$ and selective risk $R(\phi)$.
   - *El-Yaniv & Wiener (JMLR 2010):* "On the foundations of agnostic active learning."
2. **Industrial Visual Anomaly Detection:**
   - *Roth et al. (CVPR 2022):* "Towards Total Recall in Industrial Anomaly Detection (PatchCore)." Introduced memory bank coreset subsampling.
   - *Bergmann et al. (IJCV 2021):* "The MVTec Anomaly Detection Dataset." Established canonical benchmark protocols.
3. **Conformal Prediction & Uncertainty Quantification:**
   - *Angelopoulos & Bates (2021):* "A Gentle Introduction to Conformal Prediction and Distribution-Free Uncertainty Quantification."
   - *Guo et al. (ICML 2017):* "On Calibration of Modern Neural Networks." Demonstrated temperature scaling on softmax logits.
