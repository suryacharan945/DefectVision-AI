# DEFECTVISION AI — FINAL STATISTICAL INTERVAL AUDIT
**Sprint:** Post-Release Evidence & Metric Verification Audit (v1.0.0-rc1)  
**Date:** 2026-11-19  
**Auditor:** Senior ML Engineer, Computer Vision Research Engineer, QA Lead & Release Manager  

---

## 1. Executive Summary & Objective

This audit investigates the statistical methodology used to compute confidence intervals on zero-event observations, specifically reconciling the reported **16.11%** Wilson score upper bound against the **16.84%** Clopper–Pearson exact upper bound for the K=10 bottle adaptation false positive rate ($k = 0 \text{ false positives out of } n = 20 \text{ normal test units}$).

**Key Resolution:**
- Both bounds evaluate the **identical observed data** ($k = 0, n = 20$) at the **identical confidence level** ($95\%$, two-sided $\alpha = 0.05$).
- The numerical difference ($16.11\%$ vs. $16.84\%$) arises strictly from the chosen estimator:
  - **Wilson Score Interval:** An asymptotic inverted score test without continuity correction $\implies \mathbf{16.11\%}$.
  - **Clopper–Pearson Exact Interval:** The exact inversion of the cumulative binomial distribution (Beta distribution quantile) $\implies \mathbf{16.84\%}$.
  - **Rule of Three Approximation:** The asymptotic Poisson/exponential approximation for zero events ($p_{\text{upper}} \approx 3/n$) $\implies \mathbf{15.00\%}$.
- **Resolution:** To maintain mathematical conservatism, DefectVision AI adopts the **Exact Clopper–Pearson interval ($16.84\%$)** as the primary formal bound, while reporting the Wilson interval ($16.11\%$) for continuity with standard classification literature.

---

## 2. Mathematical Derivations for Zero False Alarms ($k = 0, n = 20$)

Let $X \sim \text{Binomial}(n, p)$ where $n = 20$ independent normal test bottles, and $k = 0$ observed false positives ($\hat{p} = 0.00\%$).

### 2.1 Clopper–Pearson Exact Binomial Interval
The Clopper–Pearson interval is conservative, guaranteeing coverage probability of at least $1 - \alpha$:
- For $k = 0$, the lower bound is strictly $0.0$.
- The two-sided $95\%$ upper bound ($\alpha = 0.05$, $\alpha/2 = 0.025$) is the root of $(1 - p)^n = \alpha/2$:
  $$p_{\text{upper, CP}} = 1 - (\alpha/2)^{1/n} = 1 - (0.025)^{1/20} = 1 - 0.831567 = \mathbf{0.168433 \quad (16.84\%)}$$
- The one-sided $95\%$ upper bound ($\alpha = 0.05$) is the root of $(1 - p)^n = \alpha$:
  $$p_{\text{upper, CP, 1-sided}} = 1 - (0.05)^{1/20} = 1 - 0.860892 = \mathbf{0.139108 \quad (13.91\%)}$$

### 2.2 Wilson Score Interval
The Wilson score interval inverts the score test based on the normal approximation to the binomial:
$$\text{CI} = \frac{\hat{p} + \frac{z^2}{2n} \pm z \sqrt{\frac{\hat{p}(1-\hat{p})}{n} + \frac{z^2}{4n^2}}}{1 + \frac{z^2}{n}}$$
- For two-sided $95\%$ confidence, $z = 1.95996 \approx 1.96$:
  $$p_{\text{upper, Wilson}} = \frac{0 + \frac{1.96^2}{40} + 1.96 \sqrt{0 + \frac{1.96^2}{1600}}}{1 + \frac{1.96^2}{20}} = \frac{0.19208}{1.19208} = \mathbf{0.161130 \quad (16.11\%)}$$
- For one-sided $95\%$ confidence, $z = 1.64485 \approx 1.645$:
  $$p_{\text{upper, Wilson, 1-sided}} = \frac{0.1353}{1.1353} = \mathbf{0.119177 \quad (11.92\%)}$$

### 2.3 The Rule of Three (Hanley & Lippman-Hand, 1983)
A standard heuristic in clinical and engineering safety when zero events occur:
$$p_{\text{upper}} \approx \frac{-\ln(0.05)}{n} = \frac{2.99573}{20} \approx \frac{3}{20} = \mathbf{0.1500 \quad (15.00\%)}$$

---

## 3. Reconciliation and Comparison Table

| Statistical Method | Sidedness | Confidence Level | Mathematical Formulation | Evaluated Upper Bound | Recommended Use in Project |
|---|---|:---:|---|---:|---|
| **Exact Clopper–Pearson** | Two-Sided | 95% ($\alpha/2 = 0.025$) | $1 - (0.025)^{1/20}$ | **16.84%** | **Primary Benchmark Standard** (Most conservative) |
| **Exact Clopper–Pearson** | One-Sided | 95% ($\alpha = 0.050$) | $1 - (0.050)^{1/20}$ | **13.91%** | Directional Risk Bound |
| **Wilson Score Test** | Two-Sided | 95% ($z = 1.96$) | $\frac{z^2 / n}{1 + z^2 / n}$ | **16.11%** | Parametric Classification Reference |
| **Wilson Score Test** | One-Sided | 95% ($z = 1.645$) | $\frac{z^2 / n}{1 + z^2 / n}$ | **11.92%** | One-Sided Parametric Bound |
| **Rule of Three (Exact)** | One-Sided | 95% | $-\ln(0.05) / n$ | **14.98%** | Quality Assurance Guideline |
| **Rule of Three (Approx)**| One-Sided | 95% | $3 / n$ | **15.00%** | Quality Assurance Heuristic |

---

## 4. Impact on Factory Qualification Sample Sizing

Regardless of whether one cites $16.11\%$ (Wilson), $16.84\%$ (Clopper–Pearson), or $15.00\%$ (Rule of Three), the scientific conclusion remains identical:

> **Core Statistical Conclusion:**  
> Observing zero false positives on a small sample of $n = 20$ normal units cannot validate an industrial false alarm rate $< 1.0\%$, because the true underlying rate could be as high as $16.8\%$.  
> To statistically certify a false positive rate $< 1.0\%$ at $95\%$ confidence:
> $$n \ge \frac{-\ln(0.05)}{0.01} \approx \mathbf{300 \text{ normal units without a single false alarm}}.$$

---

## 5. Audit Verdict & Documentation Directive

In `README.md`, `release/FINAL_RESEARCH_REPORT.md`, and all public documentation:
- Report the **Exact Clopper–Pearson 95% confidence interval** as $[0.00\%, 16.84\%]$.
- Acknowledge that the asymptotic Wilson score interval yields $[0.00\%, 16.11\%]$.
- Prohibit any claims of "0% false alarm rate in production" based on $N=20$.
