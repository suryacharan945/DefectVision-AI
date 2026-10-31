# Phase 9A Deliverable: Empirical Research Question Assessment

**Project:** DefectVision AI — Advanced Quality Inspection Platform  
**Phase:** 9A (Research Reset and Publication Feasibility)  
**Status:** COMPLETE & INDEPENDENTLY AUDITED  
**Artifact:** `research/phase9a_publication_feasibility/EMPIRICAL_RESEARCH_QUESTION.md`  

---

## 1. Candidate Research Question Formulation

The proposed candidate empirical research question for DefectVision AI is:

> **"How reliable are industrial visual anomaly detectors and selective inspection policies under fixed human-review budgets, heterogeneous product categories, and imperfect calibration?"**

This question shifts the focus away from attempting to claim a novel algorithm (which Phase 8C proved to be equivalent to established methods) toward conducting a rigorous, large-scale **empirical benchmark study** of how state-of-the-art anomaly detectors interface with operational human inspection constraints.

---

## 2. Deconstruction into Formal Scientific Hypotheses

To be defensible in an empirical computer vision or industrial informatics venue, this overarching question must be decomposed into four falsifiable hypotheses:

### Hypothesis H1: Calibration Brittleness Under Cross-Category Heterogeneity
- **Formal Question:** Can post-hoc calibration methods (Platt scaling, Isotonic regression, Conformal Prediction) reliably calibrate continuous anomaly scores across diverse product categories when fitted on small industrial validation sets ($N \le 30$ samples per category)?
- **Independent Variables:** Calibration estimator type (Parametric Sigmoid / Platt, Non-parametric Isotonic, Temperature Scaling, Split Conformal), validation sample size ($N \in \{10, 20, 50, 100\}$), category complexity (simple textures vs. multi-component assemblies).
- **Dependent Metrics:** Expected Calibration Error (ECE), Maximum Calibration Error (MCE), Brier Score, Negative Log-Likelihood (NLL).
- **Scientific Value:** Unsupervised anomaly detectors produce arbitrary, category-specific score distributions. Establishing the sample complexity required for reliable probability calibration across industrial categories addresses a documented practitioner challenge.

### Hypothesis H2: The Miscalibration Inversion Boundary
- **Formal Question:** Does estimation error in posterior defect probabilities cause cost-sensitive selective review to perform *worse* than simple, uncalibrated distance-to-threshold heuristics?
- **Theoretical Basis:** Cost-sensitive review multiplies estimated probability $\hat{p}$ by a large cost factor ($c_{\text{FN}} = 20 \times c_{\text{FP}}$). A large overestimation error on a predicted normal sample could erroneously displace true near-threshold anomalies.
- **Empirical Test:** Sweep calibration noise ($\sigma_{\text{cal}}$) and measure the critical inversion point $\sigma^*$ where distance-to-threshold ranking (BL2) outperforms cost-weighted risk ranking (BL6).
- **Scientific Value:** High. This would provide the field with a non-trivial, counter-intuitive insight: proving that under high calibration noise, practitioners should avoid cost-weighted probabilistic policies in favor of robust non-parametric distance ranking.

### Hypothesis H3: Cross-Category Capacity Starvation Under Global Budgets
- **Formal Question:** Under a pooled factory-level inspection budget ($K$), does global cost-sensitive allocation disproportionately starve low-contrast or low-error categories of human oversight, leading to localized defect escapes?
- **Independent Variables:** Inter-category error rate variance, category score margin distribution, global review quota ($K \in [2\%, 20\%]$ of total factory throughput).
- **Dependent Metrics:** Category-level Escape Rate (CER), Category Gini Coefficient of Inspection Workload, Total Factory Realized Loss.
- **Scientific Value:** Moderate. Addresses an important operational safety trade-off in multi-line manufacturing facilities.

### Hypothesis H4: Inspection Ergonomics and Human Imperfection Attenuation
- **Formal Question:** At what human inspector error rate ($p_{\text{sens}}, p_{\text{spec}} < 1.0$) does the economic advantage of selective inspection over fully automated inspection vanish?
- **Independent Variables:** Inspector sensitivity $p_{\text{sens}} \in [0.75, 1.00]$, inspector specificity $p_{\text{spec}} \in [0.85, 1.00]$, asymmetric cost ratio $\lambda \in [1, 100]$.
- **Dependent Metrics:** Break-even human accuracy $(p^*_{\text{sens}}, p^*_{\text{spec}})$, Net Cost Savings over Unassisted Automation.
- **Scientific Value:** Moderate-High. Establishes practical boundary conditions for when deploying human-in-the-loop inspection is economically irrational.

---

## 3. Scientific Defensibility and Novelty Evaluation

### 3.1 Does This Constitute an Original Contribution?
- **Novelty Type:** Empirical / Benchmark Study (not an algorithmic contribution).
- **Literature Overlap:** As established in `CLOSEST_RELATED_WORK.md`, selective classification (Chow 1970; Geifman 2017) and PatchCore benchmarking (Roth 2022; Anomalib 2022) are well known. However, existing benchmarks almost universally evaluate image-level AUROC on isolated categories with zero human review constraints.
- **Novelty Defense:** The novelty lies in the **systematic interaction analysis**: rigorously quantifying how the interplay of *small-sample calibration drift*, *multi-category capacity contention*, and *imperfect human verification* degrades real-world economic inspection outcomes.

### 3.2 Key Risks of Rejection or Triviality
1. **The "Predictable Outcome" Risk:** If the study simply demonstrates that "calibrated policies are better when calibration is good, but worse when calibration is bad," reviewers will criticize the conclusions as theoretically obvious and mathematically predictable.
2. **The "Lack of Deep Insight" Risk:** Without a unifying theoretical framework (such as distribution-free finite-sample conformal bounds or a formal error bound theorem), pure empirical sweeps are often viewed by top journals (e.g., IEEE TPAMI, IJCV) as technical reports rather than foundational science.
3. **Execution Scale Requirement:** An empirical benchmark paper cannot rely on the 3 development categories (`bottle`, `capsule`, `metal_nut`). It strictly requires evaluating 20+ diverse categories across multiple datasets (MVTec AD, VisA, BTAD), multiple detector architectures (PatchCore, SimpleNet, PaDiM), and extensive statistical replication (multiple cross-validation folds and seeds).

---

## 4. Assessment Summary

| Criterion | Evaluation | Assessment |
|:---|:---:|:---|
| **Practical Relevance** | High | Directly addresses the real-world deployment gap in automated factory quality control. |
| **Scientific Depth** | Moderate | Hypotheses H1–H4 are clearly defined, but rely primarily on empirical measurement rather than new theory. |
| **Risk of Triviality** | Moderate-High | High risk if results simply replicate standard cost-sensitive learning curves without discovering failure boundaries. |
| **Target Journal Viability** | Plausible for Applied / Systems Venues | Unsuitable for top theoretical AI journals (TPAMI/IJCV/NeurIPS). Feasible for applied journals (e.g., *IEEE Transactions on Industrial Informatics*, *Computers in Industry*, *Machine Vision and Applications*) if executed at sufficient empirical scale. |

---

## 5. Prerequisite Conditions for a "GO" Decision

Before DefectVision AI could proceed with this empirical research path, three non-negotiable operational conditions must be met:
1. **Unlocking Reserved Datasets:** Must unquarantine and evaluate the 11 reserved VisA categories and BTAD.
2. **Multi-Model Implementation:** Must implement and run at least one additional established detector (e.g., PaDiM or SimpleNet) alongside PatchCore to prevent model-specific bias.
3. **Substantial Compute Allocation:** Must secure dedicated GPU resources capable of running multi-seed feature extraction, memory bank indexing, and calibration sweeps across $>5,000$ images.
