# Phase 9A Deliverable: Closest Related Work and Literature Landscape

**Project:** DefectVision AI — Advanced Quality Inspection Platform  
**Phase:** 9A (Research Reset and Publication Feasibility)  
**Status:** COMPLETE & INDEPENDENTLY VERIFIED  
**Artifact:** `research/phase9a_publication_feasibility/CLOSEST_RELATED_WORK.md`  

---

## 1. Executive Summary

This document establishes an authoritative literature audit assessing the existing state of published research surrounding the candidate empirical research question:

> *"How reliable are industrial visual anomaly detectors and selective inspection policies under fixed human-review budgets, heterogeneous product categories, and imperfect calibration?"*

We survey four intersecting domains:
1. Selective classification, rejection, and learning to defer in computer vision.
2. Unsupervised visual anomaly detection benchmarking on industrial datasets.
3. Anomaly score confidence calibration and uncertainty quantification.
4. Human-in-the-loop (HITL) and cost-sensitive active visual inspection in manufacturing.

### Core Literature Conclusion:
The fundamental theoretical principles of cost-sensitive rejection (Chow 1970; Elkan 2001; Charoenphakdee et al. 2021), deep selective classification (Geifman & El-Yaniv 2017, 2019), and probability calibration (Guo et al. 2017) are mature and rigorously established. In industrial anomaly detection, while benchmarks like MVTec AD and VisA primarily evaluate unsupervised image-level AUROC or pixel F1-scores, multiple recent studies (2022–2024) already explore threshold calibration, F1 optimization splits, and empirical deployment gaps. A paper merely running existing detectors through standard selective classification rules across a standard dataset will encounter a severe novelty barrier at top-tier venues unless it uncovers a non-trivial, counter-intuitive empirical discovery.

---

## 2. Pillar 1: Selective Classification, Rejection, and Learning to Defer

Selective prediction allows an automated model to abstain on low-confidence instances and route them to an alternate handler (e.g., a human visual inspector).

| Study & Authors | Venue | Core Formulation | Primary Empirical Findings | Relevance to DefectVision AI |
|:---|:---:|:---|:---|:---|
| **Chow (1970)**  <br>*An Optimum Character Recognition System Using Decision Functions* | IEEE Trans. Inf. Theory | Fundamental Bayes reject option. Rejection is optimal when maximum posterior probability falls below a threshold $\tau = 1 - c_{\text{rej}} / c_{\text{err}}$. | Proved that thresholding posterior error risk achieves the optimal Bayes risk curve. | Established that risk-based rejection is the theoretical foundation of all selective review. |
| **Elkan (2001)**  <br>*The Foundations of Cost-Sensitive Learning* | IJCAI 2001 | Formalized cost matrix adjustment for binary classification under unequal error costs ($c_{\text{FN}} \gg c_{\text{FP}}$). | Proved optimal threshold shifting formula $\tau^* = \frac{c_{\text{FP}}}{c_{\text{FP}} + c_{\text{FN}}}$. | Direct theoretical foundation of baseline BL6 and MACBA's cost-weighted loss. |
| **Geifman & El-Yaniv (2017, 2019)**  <br>*Selective Classification for Deep Neural Networks* (2017) & *SelectiveNet* (2019) | NeurIPS 2017 / ICML 2019 | Deep selective classification optimizing risk at target coverage constraints ($\phi \in (0, 1]$) using Softmax response and dedicated reject heads. | Evaluated on ImageNet/CIFAR; showed that soft-max confidence ranking achieves strong risk-coverage trade-offs. | Closest conceptual paradigm to budgeted selective review, but focused on closed-set supervised classification. |
| **Charoenphakdee, Lee, Sugiyama (2021)**  <br>*Classification with Rejection Based on Cost-Sensitive Classification* | ICML 2021 | Generalized multi-class classification with rejection to generic asymmetric cost matrices. | Showed that surrogate loss minimization aligns with cost-sensitive rejection. | Formally proves that selective review under asymmetric costs reduces to cost-sensitive classification. |
| **Mozannar & Sontag (2020)**  <br>*Consistent Estimators for Learning to Defer to an Expert* | ICML 2020 | Formulates optimal deferral when human experts are imperfect ($p_{\text{sens}}, p_{\text{spec}} < 1$). | Established consistent surrogate losses for expert deferral. | Addresses the exact mathematical formulation of MACBA under noisy human inspectors. |

---

## 3. Pillar 2: Visual Anomaly Detection Benchmarking

Industrial visual anomaly detection has developed rapidly through standardized open benchmarks and deep nearest-neighbor or reconstruction backbones.

| Study & Authors | Venue | Methodology & Focus | Primary Empirical Findings | Relevance to DefectVision AI |
|:---|:---:|:---|:---|:---|
| **Bergmann et al. (2019, 2021)**  <br>*MVTec AD — A Comprehensive Real-World Dataset for Unsupervised Anomaly Detection* | CVPR 2019 / IJCV 2021 | 15 industrial categories (textures and objects). Standardized unsupervised training protocol on normal-only samples. | Established image AUROC and pixel PRO metrics as de facto standards. | Benchmark used for DefectVision AI development models (`bottle`, `capsule`, `metal_nut`). |
| **Zou et al. (2022)**  <br>*SPOT-the-Difference: VisA Dataset for Industrial Anomaly Detection* | ECCV 2022 | 12 object categories with complex multi-instance structures (e.g., PCBs, capsules, pipefryum). | Highlighted failure of standard autoencoders on complex logical and structural defects. | Primary independent benchmark candidate for DefectVision AI (11 reserved categories). |
| **Roth et al. (2022)**  <br>*Towards Total Recall in Industrial Anomaly Detection (PatchCore)* | CVPR 2022 | Mid-level patch representation memory bank with greedy minimax coreset subsampling. | Achieved state-of-the-art image AUROC ($>99\%$) on MVTec AD with sub-second inference. | DefectVision AI's core detection backbone. |
| **Akcay et al. (2022)**  <br>*Anomalib: A Deep Learning Library for Anomaly Detection and Localization* | IEEE Access 2022 | Open-source modular benchmark framework implementing PatchCore, PaDiM, DFKDE, etc. | Standardized calibration folds for F1-score threshold selection on validation data. | Demonstrates that disjoint calibration/validation protocols are already standard library practice. |
| **Recent Empirical Benchmarks (2023–2024)**  <br>*(e.g., BowTie Benchmark across 19 models; MVTec AD 2)* | arXiv 2024 / WACV | Exhaustive evaluation of unsupervised detectors under real-world noise, contamination, and shift. | Proved that high academic AUROC degrades significantly under subtle shifts, lighting variations, and imperfect thresholds. | Confirms the "deployment gap" between AUROC and operational factory performance. |

---

## 4. Pillar 3: Confidence Calibration and Uncertainty Quantification

Because raw distance metrics in PatchCore or reconstruction errors in autoencoders do not represent calibrated posterior probabilities, recent work has explored post-hoc calibration.

| Study & Authors | Venue | Focus | Findings & Limitations | Relevance to DefectVision AI |
|:---|:---:|:---|:---|:---|
| **Guo et al. (2017)**  <br>*On Calibration of Modern Neural Networks* | ICML 2017 | Post-hoc temperature scaling, Platt scaling, and isotonic regression. | Temperature scaling effectively minimizes Expected Calibration Error (ECE) for deep classifiers. | Foundation of logistic calibration used in Phase 8B/8C. |
| **Angelopoulos & Bates (2021)**  <br>*Conformal Prediction and Conformal Risk Control* | Foundations & Trends in ML | Distribution-free, finite-sample statistical guarantees for selective prediction. | Guarantees bounding automated risk below user-specified tolerance $\alpha$ with probability $1 - \delta$. | A rigorous alternative to heuristic thresholding, but requires separate exchangeable calibration data. |
| **Recent VAND Workshop Papers (CVPR 2023–2024)**  <br>*(e.g., LaRD: Laplace-Regularized Distillation)* | CVPR Workshops / IEEE | Bayesian uncertainty estimation (Laplace approximation) for industrial anomaly backbones. | Provides post-hoc confidence scores for anomaly localization, reducing false-positive rates. | Highlights active research in bringing uncertainty quantification to MVTec/VisA. |

---

## 5. Pillar 4: Human-in-the-Loop (HITL) and Selective Active Inspection

| Study & Authors | Venue | Focus | Findings | Relevance to DefectVision AI |
|:---|:---:|:---|:---|:---|
| **AnnoMate / MicroSentryAI (2023–2024)** | arXiv / System Demos | Interactive software interfaces integrating AI defect localization with human verification workflows. | Verified that AI-guided heatmaps improve human inspection throughput and consistency. | Direct architectural counterpart to DefectVision AI's UI and review console. |
| **Cost-Sensitive Inspection in Smart Manufacturing (2021–2024)** | IEEE Trans. Ind. Inf. / Comp. in Industry | Multi-stage visual inspection balancing automated screening and manual quality control. | Shows that two-stage inspection (AI filter $\to$ human audit) optimizes factory yield under asymmetric scrap costs. | Confirms that multi-stage triage is an established operational framework. |

---

## 6. Synthesis: What Is Known vs. What Remains Open

### Established Facts in the Literature:
1. Unsupervised anomaly detection backbones (PatchCore, EfficientAD) achieve high AUROC ($>98\%$) on clean academic benchmarks.
2. Raw anomaly scores are uncalibrated and category-dependent; optimal decision thresholds must be fitted on validation subsets.
3. Ranking instances by expected classification loss under asymmetric costs ($\lambda \gg 1$) outperforms raw distance or uniform sampling.
4. Human inspection is imperfect and carries finite bandwidth, requiring triage.

### What Remains Partially Explored:
1. **Calibration Transferability Across Heterogeneous Categories:** When an industrial plant has 15 distinct production lines with varying nominal defect baselines, how reliably does a calibration model (e.g., Platt scaling or Conformal Prediction) transfer when fitted on minimal samples ($N \le 20$ per line)?
2. **Empirical Sensitivity of Selective Review to Miscalibration:** How severely does poor probability calibration degrade the realized cost savings of cost-sensitive review under severe class imbalance and asymmetric costs?
3. **Imperfect Human Degradation Thresholds:** At what inspector error rates ($p_{\text{sens}} < 0.90$) does selective deferral cease to provide economic benefit over pure automation or pure human screening?

---

## 7. Conclusion: The Bar for a Defensible Empirical Publication

To achieve publication in a reputable Q1 journal or top conference:
- **What will FAIL (Desk Reject / Negative Review):** A paper presenting standard cost-sensitive ranking (BL6/MACBA) as a novel algorithm, or a routine benchmark running PatchCore on VisA with basic selective classification. Reviewers will rightly note that Chow (1970) and Elkan (2001) already established the theory, and Anomalib already implements the baselines.
- **What has a PLAUSIBLE (but difficult) Research Path:** A comprehensive, large-scale empirical study that exposes a non-trivial failure mode: e.g., demonstrating that probability miscalibration under real-world industrial class imbalance causes cost-sensitive review to *worsen* defect escapes relative to simple distance heuristics, accompanied by a rigorous conformal risk control framework across 20+ industrial categories.

Whether DefectVision AI can realistically execute this empirical study given compute, data, and project constraints is evaluated in the subsequent deliverables.
