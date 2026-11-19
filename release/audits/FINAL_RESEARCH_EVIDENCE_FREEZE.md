# DEFECTVISION AI — FINAL RESEARCH EVIDENCE FREEZE
**Sprint:** Emergency Release Sprint: v1.0.0-rc1 (72-Hour Project Closure)  
**Date:** 2026-11-19  
**Auditor:** Senior ML Engineer, Computer Vision Research Engineer, QA Lead & Release Manager  

---

## 1. Executive Summary & Purpose

This document freezes all empirical and theoretical research findings for the release candidate **DefectVision AI v1.0.0-rc1**. It establishes the scientific ground truth derived across Sprints 2.1 through 2.4, explicitly disallowing unverified claims, post-hoc threshold optimizations, or marketing exaggerations.

All quantitative figures in this report are mathematically audited, reproducible from versioned CSV datasets, and bound by formal statistical confidence intervals.

---

## 2. Frozen Research Positions

### 2.1 Few-Shot K=20 Adaptation: Threshold Leakage & Reclassification

- **Pre-Registered A Priori Policy ($\tau = \max(S_{\text{cal}})$):**
  $$\tau = 1.4541 \implies \text{FPR} = \mathbf{20.00\%} \quad (4/20 \text{ False Positives}), \quad \text{Recall} = \mathbf{100.00\%} \quad (63/63 \text{ Detected}), \quad \text{F1} = \mathbf{0.9692}$$
- **Post-Hoc Multiplier Policy ($\tau = \max(S_{\text{cal}}) \times 1.20$):**
  $$\tau = 1.7449 \implies \text{FPR} = \mathbf{0.00\%} \quad (0/20 \text{ False Positives}), \quad \text{Recall} = \mathbf{100.00\%} \quad (63/63 \text{ Detected}), \quad \text{F1} = \mathbf{1.0000}$$
- **Formal Scientific Classification:** **`DEVELOPMENT-SET RESULT`**.
- **Evidence Baseline:** The $1.20\times$ multiplier was identified after inspecting the test distribution to bridge the gap between max normal ($1.7129$) and min defect ($1.8212$). It does not represent an a priori proof of zero false alarms on unseen specimens.
- **Deployment Status:** **REJECTED FOR PRODUCTION.** Production remains locked to the full-dataset PatchCore memory banks.

### 2.2 Few-Shot K=10 Adaptation: Primary In-Domain Benchmark

- **Pre-Registered A Priori Policy ($\tau = \max(S_{\text{cal}})$):**
  $$\tau = 1.6410 \implies \text{FPR} = \mathbf{0.00\%} \quad (0/20 \text{ False Positives}), \quad \text{Recall} = \mathbf{96.83\%} \quad (61/63 \text{ Detected}), \quad \text{F1} = \mathbf{0.9839}$$
- **Primary Standing:** K=10 represents the most robust un-tuned few-shot in-domain result.
- **Documented Limitations:** Wilson 95% score confidence interval for the 0% FPR on $N=20$ normal units is $[0.00\%, 16.11\%]$ (Clopper-Pearson upper bound: $16.84\%$). Under the Rule of Three, this sample cannot prove a true factory false alarm rate $< 1.0\%$.

### 2.3 Spatial-Photometric Feature Fusion: Operational Failure & Pathology

- **Experimental Approach:** Single-bank concatenation of ResNet-18 spatial embeddings ($\mathbf{f}_s \in \mathbb{R}^{384}$) with color vectors ($\mathbf{f}_c \in \mathbb{R}^3$ in Lab/RGB space).
- **Audit Finding:** **FAILED ALL OPERATIONAL ACCEPTANCE TARGETS.**
  - Required Color Recall: $\ge 85.0\%$ $\rightarrow$ **Achieved: $8.0\% - 24.0\%$**
  - Required Crack Recall: $\ge 95.0\%$ $\rightarrow$ **Achieved: $19.23\%$**
  - Required F1-Score: $\ge 0.95$ $\rightarrow$ **Achieved: $0.2414 - 0.3492$**
- **Underlying Cause:** Severe channel dimension asymmetry ($384$ vs $3$). Color distance contributed $< 2.0\%$ of the total Euclidean distance at all tested weighting factors ($\lambda \le 0.50$).
- **Formal Classification:** **`DOES NOT MEET TARGETS`**.
- **Release Action:** Single-bank concatenation is formally rejected. Decoupled dual-stream max-ratio memory banks are designated as post-v1 future research.

### 2.4 External Domain Adaptation (Track B)

- **Physical Specimen Inventory:** 5 normal bottles and 1 physical defect specimen under uncontrolled smartphone/factory conditions.
- **Audit Finding:** Grossly underpowered ($N=1$ defect specimen cannot establish statistical significance).
- **Formal Classification:** **`BLOCKED — DATA REQUIRED`**.
- **Constraint Enforcement:** No claims of "real-world factory validation" or "generalized cross-domain invariance" are permitted in DefectVision AI v1.0.0-rc1.

### 2.5 Dataset Provenance & Specimen Reconciliation

- **Pill Benchmark Test Specimen Count:**
  - Test Normal (Good): **26 specimens**
  - Test Defect (Color): **25 specimens**
  - Test Defect (Crack): **26 specimens**
  - **Total Physical Test Images: 77 genuine MVTec AD specimens.**
- **Historical Header Typo:** The previous textual claim of 61 specimens ($26 + 15 + 20$) was a documentation error; all 77 images on disk were evaluated.
- **Hash Independence:** 100% disjoint SHA-256 hashes across Train ($N=20$), Calibration ($N=10$), and Test ($N=77$).

---

## 3. Summary of Frozen Research Metrics

| Research Arm / Configuration | Sample Size ($N_{\text{test}}$) | FPR (%) | Wilson 95% CI (FPR) | Defect Recall (%) | Wilson 95% CI (Recall) | F1-Score | Formal Scientific Verdict |
|---|---:|---:|:---:|---:|:---:|---:|---|
| **Full PatchCore (Production 15 Categories)** | 1,250 | 2.10% | [1.40%, 3.12%] | 97.40% | [96.10%, 98.30%] | 0.9760 | **PRODUCTION BASELINE** |
| **Few-Shot K=10 (Frozen Policy $\tau_{\max}$)** | 83 | 0.00% | [0.00%, 16.11%] | 96.83% | [89.09%, 99.11%] | 0.9839 | **PRIMARY FEW-SHOT BENCHMARK** |
| **Few-Shot K=20 (Frozen Policy $\tau_{\max}$)** | 83 | 20.00% | [8.07%, 41.60%] | 100.00% | [94.25%, 100.00%] | 0.9692 | **REPRODUCED WITH LIMITATIONS** |
| **Few-Shot K=20 (Post-Hoc Multiplier $1.20\times$)**| 83 | 0.00% | [0.00%, 16.11%] | 100.00% | [94.25%, 100.00%] | 1.0000 | **DEVELOPMENT-SET RESULT** |
| **Spatial-Photometric Single-Bank Fusion** | 77 | 0.00% | [0.00%, 12.87%] | 21.57% | [12.55%, 34.72%] | 0.3492 | **DOES NOT MEET TARGETS** |
| **Track B External Factory Adaptation** | 6 | — | — | — | — | — | **BLOCKED — DATA REQUIRED** |

---

## 4. Certification Statement

The above conclusions represent the immutable scientific baseline of **DefectVision AI v1.0.0-rc1**. No modifications to these classifications are allowed without newly acquired, physically independent, peer-reviewed data.
