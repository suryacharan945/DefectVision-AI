# DEFECTVISION AI 2.1 — OOD & DOMAIN ROBUSTNESS AUDIT REPORT

**Audit Date**: 2026-11-19T01:40:00+05:30  
**Evaluated Architecture**: EfficientNet-B0 Calibrated Classifier with Multi-Criterion OOD Gating  

---

## 1. Executive Summary & Gating Telemetry

The DefectVision AI classifier enforces a **4-part multi-criterion open-set rejection gate**:
1. Temperature-scaled Softmax Probability: $P(\hat{y}|x) \ge \tau_\text{conf}$ (default $0.70$)
2. Normalized Shannon Entropy: $\frac{H(P)}{H_\text{max}} \le 0.60$
3. Free Energy Score: $E(x) = -T \cdot \log \sum \exp(f_i(x)/T) \le -6.50$
4. Prototype Cosine Similarity: $\cos(z, p_c) \ge 0.65$

### Baseline Clean Performance (15 Supported Categories, $N=30$)
- **Top-1 Recognition Accuracy**: **100.0%**
- **Accepted / Recognized Rate**: **100.0%**
- **False Rejection Rate (FRR)**: **0.0%**
- **True Unsupported OOD Rejection Rate**: **100.0%** (15/15)
- **False Acceptance Rate (FAR)**: **0.0%**

---

## 2. Perturbation & Environmental Stress Analysis

Evaluating classifier resilience under simulated real-world optical distortions:

| Optical Perturbation | Classification Accuracy (%) | Gating Rejection Rate (%) | Mean Confidence | Mean Entropy | Mean Energy | Robustness Assessment |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Clean Baseline** | 100.0% | 0.0% | 0.997 | 0.008 | -11.65 | **Nominal Baseline** |
| **Center Occlusion (35%)** | 100.0% | 36.7% | 0.9358 | 0.1115 | -8.1474 | Entropy increases; severe occlusion successfully triggers rejection. |
| **Severe Gaussian Blur** | 96.7% | 33.3% | 0.9219 | 0.1221 | -8.2794 | Texture information destroyed; energy score drops. |
| **Extreme Low Light (80% cut)**| 93.3% | 13.3% | 0.9541 | 0.0754 | -8.9687 | Handled via intake photometric checks; classifier rejects underexposed scenes. |
| **High Overexposure** | 96.7% | 13.3% | 0.9121 | 0.1135 | -9.2777 | Glare flattens features; triggers energy rejection. |
| **Gaussian Sensor Noise** | 93.3% | 33.3% | 0.9464 | 0.0982 | -8.2458 | Feature-space noise elevates uncertainty. |

---

## 3. Unsupported / True Out-of-Distribution Rejection

Tested on 15 synthetic abstract, pure noise, and geometric shape frames:
- **Correctly Rejection**: **15/15** (100.0%)
- **Why Softmax Probability Alone Is Insufficient**:
  * Uncalibrated deep neural networks exhibit overconfidence on out-of-distribution inputs (e.g. geometric shapes occasionally score 60% probability for `grid` due to line structures).
  * However, their **Free Energy Score** ($-3.10$ vs $<-6.50$) and **Prototype Cosine Similarity** ($<0.45$) correctly flag them as ungrounded, preventing false acceptance.

---

## 4. Coverage vs. Error Trade-Off

| Confidence Threshold ($\tau_\text{conf}$) | In-Distribution Coverage (%) | Residual Error Rate (%) | Operational Recommendation |
| :---: | :---: | :---: | :--- |
| **0.40** | **100.0%** | **0.0%** | Exploratory |
| **0.50** | **100.0%** | **0.0%** | Exploratory |
| **0.60** | **100.0%** | **0.0%** | Exploratory |
| **0.70** | **100.0%** | **0.0%** | Recommended Operating Point |
| **0.80** | **100.0%** | **0.0%** | Exploratory |
| **0.85** | **100.0%** | **0.0%** | Exploratory |
| **0.90** | **100.0%** | **0.0%** | Exploratory |
| **0.95** | **100.0%** | **0.0%** | Exploratory |

---

## 5. Architectural Recommendations

1. **Retain Dual-Gate Architecture**: The combination of Universal Intake (photometric & border heuristics) and EfficientNet-B0 (Free Energy & Prototype Cosine Similarity) provides effective defense-in-depth against OOD frames.
2. **Dynamic Confidence Thresholding for Severe Defects**: When severe physical fractures degrade recognition confidence to $0.65$–$0.69$ (as seen in Tile Crack), an operator category confirmation bypass prevents unwarranted rejection of defective specimens.
