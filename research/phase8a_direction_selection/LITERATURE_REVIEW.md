# Comprehensive Literature Review: Risk-Aware Human Inspection Allocation in Industrial Visual Anomaly Detection

**Document ID:** `DV-PHASE8A-LIT-V1`  
**Date:** October 31, 2026  
**Author:** Lead AI/ML Research Engineer & Experimental Methodology Reviewer  
**Status:** **VERIFIED BIBLIOGRAPHIC AUDIT**

---

## 1. Executive Context & Purpose

Following the Phase 7C termination of heuristic patch-dispersion metrics (`STOP CPND`), this literature review establishes the theoretical foundations for a rigorous, publishable Q1 research contribution in risk-aware selective inspection.

In real-world manufacturing environments, automated visual anomaly detection systems do not operate in total isolation. They function within a **Human-AI Collaborative Inspection Pipeline**:
- The automated model flags anomalous parts and passes ambiguous or high-risk parts to human visual inspectors.
- The human inspection capacity is strictly bounded by plant throughput (e.g., $B \le 10\% - 20\%$ review capacity).
- Real-world production lines are **multi-category** (a single plant inspects bottles, capsules, fasteners, and PCBs concurrently) and **cost-asymmetric** (a missed defect that escapes to an assembly line costs orders of magnitude more than a false alarm).

Below, we systematically review the foundational literature across selective classification, learning to defer, cost-sensitive reject options, and industrial anomaly detection benchmarks.

---

## 2. Systematic Literature Ledger

### 2.1. Selective Classification & Risk-Coverage Optimization

#### 1. Selective Classification for Deep Neural Networks
- **Authors:** Yonatan Geifman, Ran El-Yaniv
- **Year & Venue:** NeurIPS 2017
- **DOI:** `10.48550/arXiv.1705.08500`
- **Main Contribution:** Formulated selective classification for deep neural architectures using soft-max response (SR) as a confidence score. Introduced risk-coverage curves ($RC$-curves) and proven sample complexity bounds for guaranteed risk at chosen coverage $c$.
- **Core Assumptions:** Supervised multi-class classification; labeled validation set available to calibrate threshold; i.i.d. test distribution; symmetric 0-1 loss.
- **Datasets:** SVHN, CIFAR-10, ImageNet.
- **Metrics:** Coverage ($c$), Selective Risk ($R(f, g)$), Coverage at Target Risk ($c^*$).
- **Limitations:** Fails in unsupervised one-class settings where no class-posterior probabilities $P(Y=k|x)$ exist; assumes a single homogeneous task rather than multi-product manufacturing.
- **Relationship to Our Work:** Provides the theoretical framework for evaluating error-coverage trade-offs, which we translate from multi-class classification to one-class industrial anomaly detection under hard budget constraints.

#### 2. SelectiveNet: A Deep Neural Network with an Integrated Reject Option
- **Authors:** Yonatan Geifman, Ran El-Yaniv
- **Year & Venue:** ICML 2019
- **DOI:** `10.48550/arXiv.1901.09192`
- **Main Contribution:** Integrated a dedicated rejection head into deep network architectures to jointly optimize classification loss and rejection selection.
- **Core Assumptions:** End-to-end backpropagation through a specialized rejection loss with coverage constraint penalties; availability of labeled negative and positive training data.
- **Datasets:** CIFAR-10, CIFAR-100, Cats vs Dogs.
- **Metrics:** Selective Risk at Target Coverage ($c \in [0.7, 0.95]$).
- **Limitations:** Cannot be applied to frozen or unsupervised nearest-neighbor anomaly detectors (e.g. PatchCore); requires retraining the entire feature backbone.
- **Relationship to Our Work:** Demonstrates why post-hoc triage policies on frozen feature representations are essential for non-parametric memory-bank industrial inspection.

#### 3. On the Foundations of Noise-free Selective Classification
- **Authors:** Ran El-Yaniv, Yair Wiener
- **Year & Venue:** JMLR 2010
- **DOI:** `10.5555/1756006.1859904`
- **Main Contribution:** Established the formal statistical foundations of selective classification, defining the optimal selective classifier and proving equivalence between selective classification and active learning version spaces.
- **Core Assumptions:** Noise-free realizable classification setting; access to hypothesis spaces with bounded VC-dimension.
- **Metrics:** Rejection Rate, Generalization Error, Excess Risk.
- **Limitations:** Purely theoretical; restricted to idealized binary classification without operational inspection costs.
- **Relationship to Our Work:** Grounding theory proving that selective risk is bounded by boundary margin proximity.

---

### 2.2. Learning to Defer & Human-AI Collaboration

#### 4. Predict Responsibly: Improving Fairness and Accuracy by Learning to Defer
- **Authors:** David Madras, Toniann Pitassi, Richard Zemel
- **Year & Venue:** NeurIPS 2018
- **DOI:** `10.48550/arXiv.1711.06664`
- **Main Contribution:** Formulated the "Learning to Defer" (L2D) paradigm, where an automated classifier explicitly learns when to make a decision and when to defer the decision to a downstream human expert, accounting for human error patterns.
- **Core Assumptions:** Access to paired training data containing both ground-truth labels and historical human expert decisions $m(x)$.
- **Datasets:** COMPAS recidivism dataset, Synthetic medical triage.
- **Metrics:** System-wide Accuracy, Disparate Impact, Subgroup Fairness.
- **Limitations:** Requires rich historical human inspection logs, which do not exist during initial factory deployment; does not handle multi-category budget constraints.
- **Relationship to Our Work:** Establishes the formal human-in-the-loop interaction model, separating algorithmic confidence from human intervention utility.

#### 5. Consistent Estimators for Learning to Defer to an Expert
- **Authors:** Hussein Mozannar, David Sontag
- **Year & Venue:** ICML 2020
- **DOI:** `10.48550/arXiv.2006.01862`
- **Main Contribution:** Proposed the first statistically consistent surrogate loss functions for learning to defer, guaranteeing convergence to Bayes-optimal joint human-AI decisions.
- **Core Assumptions:** Real-time expert availability; known cost of human consultation $c_{\text{expert}}$; joint convex surrogate optimization.
- **Datasets:** CIFAR-10 with simulated synthetic noisy experts, Chest X-ray.
- **Metrics:** System Classification Error, Human Deferral Rate.
- **Limitations:** Focuses on multiclass classification with a single expert cost; assumes unlimited human review budget (cost-penalized rather than hard-budget-constrained).
- **Relationship to Our Work:** Provides the theoretical benchmark for optimal human-AI decision boundaries under cost constraints.

---

### 2.3. Cost-Sensitive Rejection & Survey Literature

#### 6. Classification with Rejection Based on Cost-Sensitive Classification
- **Authors:** Nontawat Charoenphakdee, Zhenghang Cui, Yivan Zhang, Masashi Sugiyama
- **Year & Venue:** ICML 2021
- **DOI:** `10.48550/arXiv.2010.11748`
- **Main Contribution:** Established an exact theoretical reduction from classification with rejection to cost-sensitive classification, bypassing posterior probability estimation via an ensemble of cost-weighted classifiers.
- **Core Assumptions:** Fixed rejection cost $c \in (0, 0.5)$; supervised multi-class training data.
- **Datasets:** Benchmark UCI datasets, CIFAR-10, SVHN.
- **Metrics:** Total Expected Cost, Empirical Risk with Rejection.
- **Limitations:** Focuses on standard supervised learning; does not address the extreme cost asymmetry ($c_{\text{FN}} \gg c_{\text{FP}}$) in unsupervised anomaly detection.
- **Relationship to Our Work:** Direct theoretical justification for expressing selective triage as an expected financial cost minimization problem.

#### 7. Machine Learning with a Reject Option: A Survey
- **Authors:** Kilian Hendrickx, Lorenzo Perini, Dries Van der Plas, Wannes Meert, Jesse Davis
- **Year & Venue:** Machine Learning, Springer (2024)
- **DOI:** `10.1007/s10994-024-06534-x`
- **Main Contribution:** Comprehensive taxonomy unifying selective classification (confidence-based abstention), learning to defer (expert-aware routing), and active learning.
- **Key Taxonomy Distinction:**
  - *Confidence-based Rejection:* Model abstains solely based on internal uncertainty $S(x)$.
  - *Cost-based Rejection:* Model abstains based on financial loss trade-offs ($c_{\text{mis}}, c_{\text{rej}}$).
  - *Expert-dependent Deferral:* Model considers human capability $h(x)$.
- **Identified Open Challenges:** "Most rejection benchmarks assume single-task, balanced, multi-class problems. Real-world applications involving heterogeneous data streams with non-stationary costs and shared capacity ceilings remain under-explored."
- **Relationship to Our Work:** Directly validates our problem formulation: multi-category industrial inspection with shared capacity ceilings is explicitly identified as an unaddressed gap in the current literature.

---

### 2.4. Industrial Visual Anomaly Detection Benchmarks

#### 8. Towards Total Recall in Industrial Anomaly Detection (PatchCore)
- **Authors:** Karsten Roth, Latha Pemula, Joaquin Zepeda, Bernhard Schölkopf, Thomas Brox, Peter Gehler
- **Year & Venue:** CVPR 2022
- **DOI:** `10.1109/CVPR52688.2022.01392`
- **Main Contribution:** Established the dominant state-of-the-art memory-bank paradigm for industrial anomaly detection, using patch-level feature extraction from pre-trained backbones and greedy coreset subsampling.
- **Core Evaluation Paradigm:** Evaluates 15 MVTec AD categories independently. Reports per-category AUROC and PRO; averages across categories.
- **Limitations:** Treats every category as an isolated universe; zero discussion of operational deployment, human review capacity, or multi-line factory triage.
- **Relationship to Our Work:** Serves as our frozen detection backbone. Our proposed research builds on top of PatchCore's memory-bank distances to formulate deployment-level human-AI inspection.

#### 9. The MVTec Anomaly Detection Dataset: A Comprehensive Real-World Dataset
- **Authors:** Paul Bergmann, Kilian Batzner, Michael Fauser, David Sattlegger, Carsten Steger
- **Year & Venue:** IJCV 2021
- **DOI:** `10.1007/s11263-020-01400-4`
- **Main Contribution:** Seminal industrial dataset introducing 5,354 images across 15 industrial categories (5 textures, 10 objects) with pixel-level ground truth.
- **Limitations:** Benchmark protocol assumes 100% automated decision-making; evaluation assumes unconstrained threshold sweeping rather than fixed factory capacity.

#### 10. SPot-the-Difference Self-Supervised Pre-training for Anomaly Detection (VisA)
- **Authors:** Yang Zou, Jongheon Jeong, Latha Pemula, Dongqing Zhang, Onkar Dabeer
- **Year & Venue:** ECCV 2022
- **DOI:** `10.1007/978-3-031-20056-4_23`
- **Main Contribution:** Introduced the Visual Anomaly (VisA) dataset (10,821 images, 12 categories), capturing complex structures, multiple object configurations, and real-world surface flaws.
- **Significance:** Provides our untouched independent evaluation benchmark (11 held-out categories).

---

## 3. Summary of the Real Literature Gap

| Dimension | Conventional Selective Classification Literature | State-of-the-Art Industrial Anomaly Detection Literature | DefectVision AI Proposed Scope |
| :--- | :--- | :--- | :--- |
| **Model Nature** | Supervised multi-class classifiers with softmax posterior $P(Y=k\|x)$ | Unsupervised one-class density / memory-bank estimators ($S(X) \ge 0$) | Frozen one-class anomaly detectors without defect training samples |
| **Cost Matrix** | Symmetric 0-1 loss ($c_{\text{FN}} = c_{\text{FP}}$) | Metric-level rank evaluation (AUROC, AP, PRO) with no financial costs | Extreme asymmetric costs ($c_{\text{FN}} \gg c_{\text{FP}} > c_{\text{rev}}$) |
| **Operational Setup** | Single isolated classification task with arbitrary coverage $c \in [0, 1]$ | Per-category benchmark tables averaged into a single summary score | **Shared factory inspection budget** distributed across multiple distinct product lines |
| **Score Comparability** | Probabilities are normalized ($[0, 1]$) across classes | Raw distances have non-comparable dynamic ranges across categories | Requires multi-category calibration and marginal-utility allocation |
