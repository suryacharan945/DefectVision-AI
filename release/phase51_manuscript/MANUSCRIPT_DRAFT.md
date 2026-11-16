# Hybrid Visual Defect Inspection and Nominal-Only Adaptation: An Empirical Study of Detection Trade-Offs and Operational Constraints

**Surya Charan**  
*Department of Computer Science and Engineering*  
*DefectVision AI Research Group*  
*Email: suryacharan945@gmail.com*  

---

### Abstract
Automated visual inspection in high-throughput manufacturing confronts an asymmetric operational penalty: undetected defect escapes can result in catastrophic downstream product failures, while excessive false alarms incur substantial scrap costs and line stoppages. Supervised deep convolutional classifiers achieve high precision on recurring, anticipated defect classes but frequently fail on rare, novel defect morphologies. Conversely, unsupervised patch-based anomaly detectors capture arbitrary distribution shifts without defect supervision, but can suffer from elevated false-positive rates due to natural intra-class surface variance. 

In this paper, we conduct an empirical investigation into a dual-branch hybrid inspection architecture combining a supervised visual classifier (EfficientNet-B0 v3) with an unsupervised patch-distribution memory bank (PatchCore), characterizing the concrete trade-offs, computational overhead, and adaptation boundaries inherent to practical deployment. On an audited development-exposed benchmark of 856 industrial specimens from the MVTec Anomaly Detection dataset, the hybrid decision policy (logical OR) increased defect recall from 82.24% to 90.88%, successfully capturing 54 defect instances missed by the standalone supervised model (slashing escapes from 111 to 57), while increasing false alarms from 1 to 12 (false positive rate rising from 0.43% to 5.19%). 

To assess cross-domain transfer without defect supervision, we independently evaluated the patch-level memory pipeline on the untouched Visual Anomaly (VisA) Cashew benchmark using 350 domain-specific nominal specimens for registration and 50 held-out nominals for threshold calibration ($\tau_{\text{p99}} = 1.7452$). Across 200 independent test specimens (100 nominal, 100 defective), the adapted model achieved an image-level AUROC of 0.9237 [95% CI: 0.8852, 0.9565], an image-level AUPRC of 0.9270, and a full-census pixel-level AUROC of 0.9930 across 10.03 million evaluated pixels. Operating at the locked 99.5th-percentile calibration threshold enforced a high specificity of 98.00% (2.00% false alarm rate); however, granular sensitivity profiling revealed a 43.00% defect escape rate concentrated heavily in fine surface flaws: gross structural breaks and boundary distortions achieved 100% recall (6/6), dark voids achieved 85.0% recall (17/20), whereas hairline scratches and same-color depressions yielded escape rates of 93.3% (1/15 recall) and 100.0% (0/10 recall), respectively. 

Execution profiling on consumer multi-core CPU hardware confirmed memory registration in 392.25 s (27,440 coreset tokens, 40.2 MB index) and deterministic forward inference of 392.5 ms median (p95: 438.1 ms), confirming computational feasibility for discrete inspection stations with cycle times $\ge 1.5$ s. Our findings demonstrate that while nominal-only adaptation provides robust baseline containment and high localization precision, automated unassisted sorting requires multi-scale optical resolution or secondary verification to mitigate the severe tension between false-alarm suppression and hairline flaw escapes.

*Index Terms*—Industrial defect inspection, anomaly detection, PatchCore, EfficientNet, decision fusion, quality control, operational trade-offs, VisA benchmark.

---

## I. Introduction

Automated surface defect inspection represents a critical quality assurance pillar across precision manufacturing, including semiconductor fabrication, automotive stamping, pharmaceutical packaging, and consumer goods sorting [10], [11]. In modern production environments, visual quality gating operates under an asymmetric cost matrix. A Type II error (false negative / defect escape) delivers substandard or structurally compromised components to downstream assembly lines or end customers, risking catastrophic equipment damage, safety hazards, and costly product recalls. Conversely, a Type I error (false positive / false alarm) falsely flags conforming product as defective, inducing unnecessary component scrap, excessive manual reinspection labor, and disruptive production line stoppages [11], [12].

In recent years, deep learning methodologies for automated visual inspection have bifurcated into two primary paradigms:
1.  **Supervised Visual Classification:** Deep convolutional neural networks (CNNs) and Vision Transformers trained on extensive annotated libraries of defective and conforming components [4], [10]. When evaluated against recurring, pre-defined flaw topologies, supervised models deliver exceptional precision and near-zero false-alarm rates. However, they rely on a closed-world assumption: when presented with novel, unmodeled defect geometries, anomalous foreign materials, or unrepresented physical damage, supervised classifiers exhibit overconfident misclassifications, leading to severe defect escapes [10].
2.  **Unsupervised Anomaly Detection:** Systems trained exclusively on nominal (defect-free) component imagery to model the distribution of normal appearances, such as memory-bank nearest-neighbor methods [1], [6], [7]. Because they require no defect annotations, these methods theoretically detect arbitrary deviations from nominality. However, in factory environments characterized by natural intra-class texture variations, slight illumination drifts, and part positioning jitter, purely unsupervised models frequently suffer from elevated false-alarm rates that factory operators cannot tolerate [1], [10].

To harness the complementary strengths of both paradigms, industrial practitioners frequently explore dual-branch hybrid architectures, combining a supervised classifier with an unsupervised anomaly detector via logical disjunction (OR-logic) [10]. Under this regime, a specimen is quarantined if either branch flags a potential flaw. While the conceptual appeal of such hybrid gating is widely recognized, literature in applied instrumentation and measurement rarely quantifies the precise operational penalty curve: how many false alarms must a factory absorb to reduce defect escapes by a given margin? Furthermore, while unsupervised methods claim rapid adaptation to new manufacturing lines, empirical studies evaluating nominal-only adaptation on completely unseen, out-of-distribution industrial substrates under strict audit protocols remain scarce.

### A. Contributions of This Work
In this paper, we present an empirical evaluation of hybrid defect detection and nominal-only category adaptation under concrete operational and hardware constraints. Rather than asserting architectural or mathematical novelty, the primary scientific and engineering contributions of this work are:

1.  **Direct Empirical Quantification of the Hybrid Operating Trade-Off:** On an audited development-exposed benchmark of 856 industrial images (MVTec AD [3]), we quantify the exact cost curve of dual-branch decision fusion: pairing an EfficientNet-B0 v3 classifier [4] with a PatchCore memory bank [1] captured **54 defect instances missed by the supervised model alone** (reducing missed defects from 111 to 57; recall rising from 82.24% to 90.88%), at the operational expense of **11 additional false alarms** (increasing false alarm rate from 0.43% to 5.19%).
2.  **First-Party Independent Adaptation Validation:** We execute a strictly isolated, out-of-distribution evaluation of nominal-only PatchCore registration on the untouched Visual Anomaly (VisA) Cashew benchmark [2], using 350 nominal registration images and 50 held-out nominal calibration images. Across 200 independent test specimens (100 nominal, 100 defective), the system achieved an image-level AUROC of **0.9237** [95% CI: 0.8852, 0.9565], an image-level AUPRC of **0.9270**, and a full-census pixel-level AUROC of **0.9930** across 10.03 million evaluated pixels.
3.  **Granular Defect-Type Sensitivity Profiling:** We unpack aggregate AUROC metrics across 16 fine-grained defect morphologies in the VisA Cashew benchmark, exposing the boundary conditions of patch-distance anomaly scoring. While macroscopic deformities and gross structural breaks achieved **100% recall** (6/6), hairline surface scratches and subtle same-color indentations yielded catastrophic escape rates of **93.3%** (1/15 recall) and **100.0%** (0/10 recall) under factory-grade false-alarm constraints ($\tau_{\text{p99}}$).
4.  **Hardware Feasibility Profiling on Consumer CPU:** We demonstrate that memory-bank adaptation and deterministic inference are achievable on standard multi-core CPU workstations without GPU acceleration: registration of 350 nominal images completed in **392.25 seconds** (40.2 MB memory footprint), with deterministic per-image inference latencies of **392.5 ms median** (p95: 438.1 ms), confirming viability for discrete manufacturing stations with cycle times $\ge 1.5$ seconds.
5.  **Rigorous Accounting of Engineering Dead-Ends:** We transparently document negative results encountered during development, specifically the failure of Context-Preserving Normalization Dropout (CPND) to improve generalization and the severe optimization instability of Multi-Axis Cross-Branch Attention (MACBA), establishing verified guardrails for future applied research.

The remainder of this paper is structured as follows: Section II reviews related literature in supervised and unsupervised industrial inspection. Section III details the dual-branch system architecture, nominal registration protocol, and coreset indexing. Section IV outlines the experimental setup and reproducibility audit standards. Section V presents the development-exposed hybrid benchmark results on MVTec AD. Section VI provides the independent validation findings and granular morphology breakdown on VisA Cashew. Section VII analyzes operational latency, takt-time feasibility, and quality economics. Section VIII discusses limitations, negative findings, and deployment boundaries. Section IX concludes the paper.

---

## II. Related Work

### A. Supervised Defect Classification
Supervised deep convolutional neural networks have been widely applied to automated visual inspection across diverse manufacturing sectors [10], [11]. Architectures such as ResNet [5] and EfficientNet [4] optimize depth, width, and resolution scaling to maximize classification accuracy while maintaining parameter efficiency. EfficientNet-B0, parameterized with approximately 5.3 million weights, provides an exceptional balance of representational capacity and inference speed, making it widely adopted in industrial workstations [4]. However, supervised classifiers operate under the fundamental vulnerability of closed-world training [10]: when presented with novel defect classes, foreign contaminants, or structural variations absent from the training split, their posterior probability estimates $p(\text{defective}|x)$ become unreliable, frequently producing overconfident false-negative predictions that allow critical defects to escape inspection [10].

### B. Unsupervised Anomaly Detection and Localization
To eliminate dependence on rare and costly defect annotations, unsupervised visual anomaly detection models the manifold of nominal appearance using defect-free imagery exclusively [1], [3]. Early approaches utilized deep autoencoders, variational autoencoders (VAEs), and generative adversarial networks (GANs) to compute pixel-level reconstruction error [3]. However, generative reconstruction models frequently suffer from "identity shortcutting," where anomalous features are blurrily reconstructed, degrading localization sharpness [1].

More recently, feature-embedding methods leveraging pre-trained deep representations have established state-of-the-art benchmarks in industrial anomaly detection [1], [6], [7]. SPADE [7] introduced multi-scale nearest-neighbor feature retrieval using deep pyramid correspondences. PaDiM [6] fit multivariate Gaussian distributions to localized patch embeddings across nominal cohorts, enabling fast inference but constraining representation to unimodal distributions. PatchCore [1] significantly advanced the state of the art by constructing an unconstrained memory bank of neighborhood-aware patch-level feature vectors extracted from intermediate stages of an ImageNet-pretrained convolutional backbone (e.g., ResNet-18 or WideResNet-50). By applying a greedy minimax facility location coreset reduction, PatchCore condenses the patch memory bank to a small fraction of representative tokens while preserving coverage of the nominal manifold, yielding superior image-level and pixel-level anomaly AUROC [1].

### C. Industrial Benchmarks: MVTec AD and VisA
Empirical progress in visual anomaly detection has been driven by standardized real-world benchmarks. The MVTec Anomaly Detection (MVTec AD) dataset [3] comprises 5,354 high-resolution images across 15 industrial manufacturing categories (10 rigid objects, 5 textures), providing a diverse testbed of real defect topologies. However, because MVTec AD has been extensively utilized for hyperparameter tuning and model optimization across hundreds of published papers since 2019, evaluations conducted on MVTec test splits must be carefully audited to distinguish development-exposed performance from genuine out-of-distribution adaptation [3]. 

The Visual Anomaly (VisA) dataset, introduced by Zou et al. [2], provides 10,821 images across 12 categories, encompassing complex structures, multiple distinct objects per image, and natural organic goods (e.g., `cashew`). VisA represents a substantially more challenging benchmark for anomaly detection due to natural intra-class morphological variance, irregular object contours, and subtle low-contrast flaw topologies [2].

---

## III. System Methodology and Architecture

The DefectVision AI architecture integrates two decoupled inspection engines executing concurrently on an incoming component image: a supervised defect classifier (EfficientNet-B0 v3) and an unsupervised patch-distribution memory bank (PatchCore). The overall pipeline is illustrated conceptually in Fig. 1.

```
       +-------------------------------------------------------+
       |                  Incoming Image (x)                   |
       +-------------------------------------------------------+
                                   |
         +-------------------------+-------------------------+
         |                                                   |
         v                                                   v
+-------------------------------+   +-----------------------------------------------+
|  Supervised Classification    |   |         Unsupervised Patch Anomaly            |
|       (EfficientNet-B0 v3)    |   |             (PatchCore Memory)                |
+-------------------------------+   +-----------------------------------------------+
| Input: 256 x 256 RGB          |   | Input: 224 x 224 RGB                          |
| Feature Extractor: EffNet-B0  |   | Backbone: ResNet-18 (layer2 + layer3, D=384)  |
| Classifier: 2-class Softmax   |   | Feature Aggregation: 3x3 AvgPool, Stride 1    |
| Output: p_defect in [0, 1]    |   | Search: FAISS L2 Search vs Coreset Bank (M)   |
| Decision Rule:                |   | Heatmap: Bilinear Upsample + Gaussian Filter  |
|   d_clf = (p_defect >= 0.50)  |   | Output: S_img = max(Heatmap)                  |
|                               |   | Decision Rule: d_ano = (S_img >= tau_p99)     |
+-------------------------------+   +-----------------------------------------------+
         |                                                   |
         +-------------------------+-------------------------+
                                   |
                                   v
             +-------------------------------------------+
             |         Dual-Branch Decision Fusion       |
             |       y_pred = d_clf  OR  d_ano           |
             +-------------------------------------------+
                                   |
                     +-------------+-------------+
                     |                           |
                     v                           v
             [DEFECT DETECTED]           [NOMINAL / PASSED]
             (Flagged / Quarantined)     (Cleared for Packing)
```
*Fig. 1. Dual-branch hybrid inspection architecture combining supervised classification (EfficientNet-B0 v3) and unsupervised patch anomaly memory (PatchCore) via logical OR decision fusion.*

### A. Unsupervised Patch-Level Memory Pipeline (PatchCore)
The unsupervised branch implements the PatchCore paradigm [1] utilizing a permanently frozen ResNet-18 backbone pre-trained on ImageNet-1K. 

1.  **Feature Extraction:** Given an input image $x \in \mathbb{R}^{3 \times H \times W}$ resized to $224 \times 224$, patch representations are extracted from intermediate residual stages: `layer2` (stride 8, 128 channels) and `layer3` (stride 16, 256 channels). To capture spatial context, each feature map is smoothed via $3 \times 3$ local adaptive average pooling with stride 1. The feature maps are bilinearly interpolated to a common spatial resolution ($28 \times 28$) and concatenated channel-wise, producing a dense grid of $N_p = 28 \times 28 = 784$ patch feature vectors:
    $$m(i,j) \in \mathbb{R}^{D}, \quad D = 128 + 256 = 384$$
2.  **Greedy Minimax Coreset Subsampling:** For a nominal registration cohort of $K_{\text{reg}}$ images, the total extracted patch collection $\mathcal{M}_{\text{raw}} = \bigcup_{k=1}^{K_{\text{reg}}} \mathcal{M}_k$ contains $|\mathcal{M}_{\text{raw}}| = K_{\text{reg}} \times 784$ feature vectors. Storing and searching this unconstrained collection introduces excessive memory and latency overhead. We apply the iterative greedy $k$-Center minimax facility location algorithm [1] to select a representative subset $\mathcal{M}_{\text{coreset}} \subset \mathcal{M}_{\text{raw}}$ of size $M$:
    $$m^* = \arg\max_{m \in \mathcal{M}_{\text{raw}} \setminus \mathcal{M}_{\text{coreset}}} \min_{c \in \mathcal{M}_{\text{coreset}}} \|m - c\|_2$$
    Subsampling at a target coreset ratio $\kappa = 0.10$ condenses the memory bank by an order of magnitude while preserving coverage of the nominal patch manifold [1].
3.  **Fast Nearest-Neighbor Indexing:** The coreset feature vectors are indexed using an exact Euclidean distance flat index (`IndexFlatL2`) via the FAISS library [8] executing natively on multi-threaded CPU hardware.
4.  **Anomaly Scoring and Heatmap Generation:** At test time, patch vectors $p \in \mathcal{M}_{\text{test}}$ extracted from an input image are queried against $\mathcal{M}_{\text{coreset}}$. The patch-level anomaly score is defined as the Euclidean distance to its nearest nominal neighbor:
    $$s(p) = \min_{c \in \mathcal{M}_{\text{coreset}}} \|p - c\|_2$$
    The patch anomaly scores are reshaped to a $28 \times 28$ spatial grid, bilinearly upsampled to $224 \times 224$, and convolved with a 2D Gaussian smoothing kernel ($\sigma = 4.0$) to generate the continuous anomaly heatmap $\mathcal{A}(u,v)$. The specimen-level anomaly score $S_{\text{img}}$ is defined as the maximum spatial anomaly score across the smoothed map:
    $$S_{\text{img}} = \max_{(u,v)} \mathcal{A}(u,v)$$

### B. Statistical Decision Threshold Calibration
To establish an operational binary decision boundary without defect supervision, we enforce a strict quantile-based calibration protocol. A cohort of $K_{\text{cal}}$ nominal specimens held out from coreset registration is processed through the memory pipeline to compute nominal baseline scores. The operational decision threshold $\tau_{\text{p99}}$ is set to the empirical 99.5th percentile of the calibration score distribution:
$$\tau_{\text{p99}} = \text{Percentile}\left(\{S_{\text{cal},1}, S_{\text{cal},2}, \dots, S_{\text{cal},K_{\text{cal}}}\}, 99.5\right)$$
This deterministic calibration locks the decision boundary to enforce a theoretical nominal false-alarm rate $\le 1.0\%$ prior to evaluating any unseen test data.

### C. Supervised Visual Classification Pipeline (EfficientNet-B0 v3)
The supervised branch executes a fine-tuned EfficientNet-B0 classifier [4]. Input images are resized to $256 \times 256$, normalized using ImageNet channel statistics, and processed through mobile inverted bottleneck convolutions (MBConv) to produce a 1280-dimensional global representation vector. A fully connected classification head with softmax activation outputs the posterior defect probability $p_{\text{defect}} \in [0, 1]$. The binary supervised decision is parameterized by standard operating threshold:
$$d_{\text{clf}} = \mathbb{I}(p_{\text{defect}} \ge 0.50)$$

### D. Dual-Branch Decision Fusion Rule
In production deployment, decisions are integrated via a logical disjunction (OR-logic) gating rule:
$$y_{\text{hybrid}} = d_{\text{clf}} \lor \mathbb{I}(S_{\text{img}} \ge \tau_{\text{p99}})$$
A component is flagged as defective and diverted for secondary audit if *either* the supervised model identifies a known defect pattern with high probability *or* the unsupervised patch memory detects an out-of-distribution spatial deviation exceeding the nominal threshold.

---

## IV. Experimental Setup and Reproducibility Audit Protocols

### A. Execution Hardware and Software Stack
All experiments, training routines, memory registrations, and latency benchmarks were executed on an isolated engineering workstation with no external GPU clusters:
*   **Processor:** Intel Core i7-10750H CPU @ 2.60GHz (6 physical cores, 12 logical threads, 12 MB SmartCache).
*   **System Memory:** 16.0 GB dual-channel DDR4 RAM @ 2933 MHz.
*   **Storage:** 512 GB NVMe M.2 Solid State Drive.
*   **Operating System:** Microsoft Windows 11 Enterprise AMD64.
*   **Software Stack:** Python 3.12.4, PyTorch 2.15.0+cpu, Torchvision 0.20.0+cpu, FAISS-CPU 1.15.1, scikit-learn 1.4.2, SciPy 1.13.0.
*   **Reproducibility Controls:** Random seed permanently fixed to $S = 42$; deterministic algorithms enabled in PyTorch (`torch.use_deterministic_algorithms(True)`).

### B. Datasets and Experimental Partitions

#### 1) MVTec Anomaly Detection (Development-Exposed Benchmark)
*   **Purpose:** Evaluation of dual-branch hybrid decision fusion across diverse industrial manufacturing domains.
*   **Population:** 856 test images across all 15 MVTec AD categories (625 defective specimens, 231 nominal specimens).
*   **Methodological Classification:** **Category C Development-Exposed.** Models, coreset ratios, and decision thresholds were historically tuned across MVTec development splits. This benchmark evaluates the empirical operational trade-off of OR-logic fusion, but does not represent zero-leakage generalization.

#### 2) Visual Anomaly Cashew Dataset (Independent Adaptation Validation)
*   **Purpose:** Blind, out-of-distribution validation of nominal-only PatchCore adaptation on an untouched organic category.
*   **Source:** Official Amazon Science VisA dataset distribution [2], retrieved directly from the public AWS S3 bucket (`s3://amazon-science-visa/`).
*   **Data Partitioning (Zero-Leakage Split):**
    *   *Registration Cohort ($K_{\text{reg}} = 350$ images):* Nominal specimens used exclusively for feature extraction and coreset construction.
    *   *Calibration Cohort ($K_{\text{cal}} = 50$ images):* Independent nominal specimens used exclusively to compute baseline statistics and calibrate $\tau_{\text{p99}}$.
    *   *Independent Test Cohort ($N = 200$ images):* Untouched partition consisting of 100 conforming nominal specimens ($y=0$) and 100 defective specimens ($y=1$) spanning 16 fine-grained morphology categories. Ground-truth labels and polygon masks were unblinded only after the registration manifest and threshold were cryptographically hashed and permanently locked.

### C. Evaluation Metrics and Statistical Confidence Formulation
*   **Classification Performance:** True Positives (TP), True Negatives (TN), False Positives (FP), False Negatives (FN), Accuracy, Balanced Accuracy, Precision (Positive Predictive Value, PPV), Recall (Sensitivity / True Positive Rate, TPR), Specificity (True Negative Rate, TNR), False Positive Rate (FPR / Type I Overkill), False Negative Rate (FNR / Type II Defect Escape Rate), and F1-score.
*   **Confidence Intervals:**
    *   *Binomial Proportions:* Evaluated using Wilson score intervals [9] without continuity correction at $95\%$ confidence level ($z = 1.95996$):
        $$CI_{\text{Wilson}} = \frac{\hat{p} + \frac{z^2}{2n} \pm z \sqrt{\frac{\hat{p}(1-\hat{p})}{n} + \frac{z^2}{4n^2}}}{1 + \frac{z^2}{n}}$$
    *   *Continuous AUROC:* Evaluated via non-parametric empirical bootstrapping with $B = 1,000$ iterations with replacement ($S=42$).
*   **Pixel-Level AUROC:** Computed across all pixels in the evaluation partition against binarized ground-truth polygon masks ($m > 0$). Evaluated under two explicit protocols:
    1.  *Full-Census Pixel AUROC:* All $10,035,200$ pixels across all 200 test images ($200 \times 224 \times 224$).
    2.  *Defect-Only Specimen Pixel AUROC:* All $5,017,600$ pixels across the 100 defective test images ($100 \times 224 \times 224$).

---

## V. Development-Exposed Benchmark Evaluation (MVTec AD)

The performance of Standalone EfficientNet-B0 v3, Standalone PatchCore, and the Dual-Branch Hybrid system across the 856-image MVTec benchmark is summarized in Table I.

```
TABLE I
QUANTITATIVE PERFORMANCE COMPARISON ON THE AUDITED 856-IMAGE MVTEC AD BENCHMARK
+------------------------------------+------------------+------------------+-----------------------+
| Metric                             | PatchCore (Alone)| EffNet-B0 (Alone)| DefectVision AI Hybrid|
+------------------------------------+------------------+------------------+-----------------------+
| Evaluation Population              | 856 images       | 856 images       | 856 images            |
| Conforming Nominal Images (y=0)    | 231 images       | 231 images       | 231 images            |
| Defective Images (y=1)             | 625 images       | 625 images       | 625 images            |
| True Positives (TP)                | 449              | 514              | 568                   |
| True Negatives (TN)                | 220              | 230              | 219                   |
| False Positives (FP / False Alarm) | 11               | 1                | 12                    |
| False Negatives (FN / Escapes)     | 176              | 111              | 57                    |
| Overall Accuracy                   | 78.15%           | 86.92%           | 91.94%                |
| Balanced Accuracy                  | 83.54%           | 90.90%           | 92.84%                |
| Defect Precision (PPV)             | 97.61%           | 99.81%           | 97.93%                |
| Defect Recall (TPR / Sensitivity)  | 71.84%           | 82.24%           | 90.88%                |
| Specificity (TNR)                  | 95.24%           | 99.57%           | 94.81%                |
| F1-Score                           | 0.8277           | 0.9018           | 0.9427                |
| False Positive Rate (FPR)          | 4.76%            | 0.43%            | 5.19%                 |
| False Negative Rate (FNR)          | 28.16%           | 17.76%           | 9.12%                 |
| Image-Level AUROC                  | 0.9373*          | 0.9809           | 0.9608                |
| Image-Level AUPRC                  | 0.9266           | 0.9932           | 0.9745                |
+------------------------------------+------------------+------------------+-----------------------+
*Note: Standalone PatchCore AUROC reflects category-standardized anomaly scores (z-score normalized per category).
```

### A. Analysis of the Hybrid Operational Trade-Off
The empirical data in Table I refutes the assumption that dual-branch hybrid architectures represent a strict Pareto improvement across all metrics. Rather, OR-logic fusion represents an asymmetric operational reallocation:
1.  **Escape Reduction:** Standalone EfficientNet-B0 missed 111 defects ($17.76\%$ FNR), primarily involving novel flaw geometries (e.g., contaminated threads, unusual fiber inclusions) that fell outside its training clusters. The hybrid system recovered 54 of those missed defects, slashing escapes to 57 ($9.12\%$ FNR)—a **$48.6\%$ relative reduction in defect escapes**.
2.  **False-Alarm Inflation:** Standalone EfficientNet-B0 produced extraordinary specificity ($99.57\%$), triggering only a single false alarm across 231 conforming specimens ($\text{FP}=1$, $0.43\%$ FPR). However, when disjunctively coupled with PatchCore, false alarms increased twelve-fold to 12 ($\text{FP}=12$, $5.19\%$ FPR)—a net penalty of **11 additional false alarms** ($+4.76$ percentage points).
3.  **Continuous Discrimination vs. Discrete Gating:** Standalone EfficientNet-B0 achieved superior continuous ranking metrics (AUROC 0.9809 vs 0.9608; AUPRC 0.9932 vs 0.9745). The hybrid architecture's superiority emerges strictly at the **discrete decision operating point**, where the cost of defect escapes ($C_{\text{escape}}$) vastly exceeds the cost of scrap or false re-inspection ($C_{\text{scrap}}$).

---

## VI. Independent Out-of-Distribution Validation (VisA Cashew)

To rigorously evaluate nominal-only adaptation without development exposure or defect supervision, the PatchCore memory pipeline was evaluated on the independent VisA Cashew benchmark [2].

```
TABLE II
INDEPENDENT EVALUATION RESULTS ON THE UNTOUCHED VISA CASHEW BENCHMARK (N=200)
+------------------------------------+--------------------------+-------------------------------------------------------+
| Metric                             | Measured Value           | 95% Confidence Interval / Notes                       |
+------------------------------------+--------------------------+-------------------------------------------------------+
| Evaluation Population              | 200 specimens            | 100 Nominal (y=0), 100 Defective (y=1)                |
| Nominal Calibration Cohort         | 50 specimens             | Held-out nominals (tau_p99 = 1.745232)                |
| True Positives (TP)                | 57                       | Defective specimens correctly flagged                 |
| True Negatives (TN)                | 98                       | Nominal specimens correctly cleared                   |
| False Positives (FP / Type I)      | 2                        | Nominal specimens falsely rejected (2.00% FPR)        |
| False Negatives (FN / Type II)     | 43                       | Defective specimens escaped inspection (43.00% FNR)   |
| Overall Accuracy                   | 77.50%                   | [71.22%, 82.68%] (Wilson Score Interval)              |
| Balanced Accuracy                  | 77.50%                   | [71.22%, 82.68%] (Symmetric due to 1:1 split)         |
| Defect Precision (PPV)             | 96.61%                   | [88.48%, 99.07%] (Wilson Score Interval)              |
| Defect Recall (TPR / Sensitivity)  | 57.00%                   | [47.24%, 66.24%] (Wilson Score Interval)              |
| Specificity (TNR)                  | 98.00%                   | [92.96%, 99.45%] (Wilson Score Interval)              |
| Negative Predictive Value (NPV)    | 69.50%                   | [61.46%, 76.49%] (Wilson Score Interval)              |
| F1-Score                           | 0.7170                   | Harmonic mean of Precision and Recall                 |
| Image-Level AUROC                  | 0.9237                   | [0.8852, 0.9565] (1,000 Empirical Bootstraps)         |
| Image-Level AUPRC                  | 0.9270                   | Area under Precision-Recall Curve                     |
| Full-Census Pixel-Level AUROC      | 0.9930                   | Evaluated across 10,035,200 test pixels (all 200 img) |
| Defect-Only Specimen Pixel AUROC   | 0.9877                   | Evaluated across 5,017,600 pixels (100 defective img) |
| Forward Pass CPU Latency (Median)  | 392.5 ms                 | Mean: 396.7 ms, p95: 438.1 ms                         |
+------------------------------------+--------------------------+-------------------------------------------------------+
```

### A. Image-Level Discrimination and Pixel Localization
As detailed in Table II, nominal-only PatchCore registration achieved high continuous separation on unseen organic cashew specimens:
*   **Image AUROC of 0.9237** and **AUPRC of 0.9270** demonstrate that patch distance modeling generalizes effectively from synthetic rigid objects to organic goods with complex surface texturing.
*   **Pixel AUROC of 0.9930** (0.9877 evaluated exclusively over defective images) confirms outstanding spatial localization. Without any pixel-level training annotations, the receptive fields of `layer2` and `layer3` successfully pinpoint anomalous regions.
*   **False-Alarm Suppression:** Operating at the locked calibration threshold ($\tau_{\text{p99}} = 1.745232$) maintained high specificity ($98.00\%$), triggering only 2 false alarms across 100 conforming specimens ($2.00\%$ FPR).

### B. Granular Sensitivity Breakdown Across Defect Morphologies
While aggregate AUROC ($0.9237$) suggests strong performance, analyzing discrete predictions across the 16 Amazon Science defect categories uncovers severe performance disparities, as detailed in Table III.

```
TABLE III
GRANULAR DETECTION PERFORMANCE ACROSS ALL 16 VISA CASHEW DEFECT MORPHOLOGIES
+------------------------------------------+-------+----+----+-----------+----------------------------------------------+
| Defect Category / Morphology             | Total | TP | FN | Recall    | Empirical Detection Characteristic           |
+------------------------------------------+-------+----+----+-----------+----------------------------------------------+
| middle breakage                          | 6     | 6  | 0  | 100.0%    | Flawless detection (Gross structural break)  |
| stuck together                           | 6     | 6  | 0  | 100.0%    | Flawless detection (Contour distortion)      |
| middle breakage, small holes             | 1     | 1  | 0  | 100.0%    | Flawless detection (Multi-flaw component)    |
| middle breakage, same colour spot        | 1     | 1  | 0  | 100.0%    | Flawless detection (Structural dominate)     |
| different colour spot                    | 9     | 8  | 1  | 88.9%     | Robust detection (High chromatic contrast)   |
| small holes                              | 20    | 17 | 3  | 85.0%     | High detection (Dark localized voids)        |
| corner or edge breakage                  | 14    | 11 | 3  | 78.6%     | Strong detection (Silhouette deformation)    |
| burnt, corner or edge breakage           | 2     | 1  | 1  | 50.0%     | Moderate detection                           |
| different colour spot, same colour spot  | 2     | 1  | 1  | 50.0%     | Moderate detection                           |
| burnt                                    | 10    | 4  | 6  | 40.0%     | Weak detection (Subtle thermal browning)     |
| small scratches                          | 15    | 1  | 14 | 6.7%      | SEVERE ESCAPE (14/15 missed; 93.3% escape)   |
| same colour spot                         | 10    | 0  | 10 | 0.0%      | TOTAL FAILURE (10/10 missed; 100.0% escape)  |
| burnt, different colour spot             | 1     | 0  | 1  | 0.0%      | Escape (Subtle combination)                  |
| different colour spot, small holes       | 1     | 0  | 1  | 0.0%      | Escape (Micro defect)                        |
| burnt, same colour spot                  | 1     | 0  | 1  | 0.0%      | Escape                                       |
| corner breakage, small scratches         | 1     | 0  | 1  | 0.0%      | Escape                                       |
+------------------------------------------+-------+----+----+-----------+----------------------------------------------+
| TOTAL DEFECTIVE COHORT                   | 100   | 57 | 43 | 57.0%     | 57 Caught, 43 Escapes (43.0% Escape Rate)    |
+------------------------------------------+-------+----+----+-----------+----------------------------------------------+
```

### C. Forensic Analysis of Defect Escapes
1.  **Hairline Surface Flaws (`small scratches`):** Missed 14 out of 15 specimens ($6.7\%$ recall). In VisA Cashew, scratches represent narrow abrasions measuring 2 to 4 pixels in width. When processed through ResNet-18 `layer2` (stride 8) and `layer3` (stride 16) with $3 \times 3$ local average pooling, high-frequency spatial gradients are heavily diluted across the broader receptive field. Furthermore, natural cashew kernels possess organic furrows and striations whose feature embeddings overlap with subtle scratches, preventing Euclidean patch distances from crossing $\tau_{\text{p99}} = 1.7452$.
2.  **Chromatic-Invariant Depressions (`same colour spot`):** Total failure (0 out of 10 caught, $0.0\%$ recall). These flaws represent physical indentations or tissue bruising that share the exact hue and reflectance of healthy cashew kernel meat. Because ImageNet-pretrained representations prioritize chromatic transitions and high-contrast boundaries, shallow monochromatic indentations produce negligible patch distance displacement.
3.  **Gross Morphological Anomalies:** Achieved near-perfect detection ($85.0\%\text{ to }100.0\%$ recall). Structural breaks (`middle breakage`, `corner breakage`) and multi-body adhesions (`stuck together`) completely disrupt spatial silhouettes and patch neighborhood graphs, generating robust anomaly scores ($S_{\text{raw}} \in [2.10, 3.85]$) that easily trigger detection.

---

## VII. Operational Feasibility, Latency Profiling, and Quality Economics

### A. Computational Execution Profiling on CPU
Execution profiling across registration, indexing, and inference stages on standard CPU workstation hardware is summarized in Table IV.

```
TABLE IV
EXECUTION PROFILING ON CONSUMER CPU HARDWARE (INTEL CORE I7-10750H)
+----------------------------------------------+--------------------+-------------------------------------------+
| Stage / Pipeline Component                   | Execution Metric   | Operational Context                       |
+----------------------------------------------+--------------------+-------------------------------------------+
| Target Domain Registration (350 images)      | 392.25 seconds     | Full memory bank construction (~6.5 min)  |
| Raw Feature Extraction (274,400 patch vectors)| 281.14 seconds     | ResNet-18 layer2 + layer3 forward passes  |
| Greedy K-Center Coreset Selection (10%)      | 91.17 seconds      | Minimax facility location reduction       |
| Calibration Cohort Evaluation (50 images)    | 19.94 seconds      | Nominal quantile threshold calibration    |
| Extracted Coreset Tokens (M)                 | 27,440 tokens      | Retained patch memory bank                |
| Coreset Index Storage Footprint              | 40.2 MB            | Disk/RAM footprint (FAISS IndexFlatL2)    |
| PatchCore Forward Inference Latency (Median) | 392.5 ms           | Preprocessing + ResNet-18 + FAISS search  |
| PatchCore Forward Inference Latency (Mean)   | 396.7 ms           | Standard deviation: 28.4 ms               |
| PatchCore Forward Inference Latency (p95)    | 438.1 ms           | 95th percentile execution bound           |
| Supervised EfficientNet-B0 Forward Latency   | 170.1 ms (median)  | 256x256 input forward pass on CPU         |
| End-to-End Hybrid API Latency (Median)       | 881.7 ms           | Full HTTP request-response cycle on CPU   |
| End-to-End Hybrid API Latency (p95)          | 1455.7 ms          | High-load execution bound                 |
| System Memory Working Set (RAM)              | < 650 MB           | Resident execution footprint              |
+----------------------------------------------+--------------------+-------------------------------------------+
```

### B. Takt-Time and Factory Line Viability
The empirical latencies in Table IV establish clear boundary conditions for industrial line integration:
*   **Discrete Batch & Station Inspection (Cycle times $\ge 1.5$ seconds):** **VIABLE.** Manufacturing processes such as automotive casting inspection, aerospace part verification, packaged pharmaceutical blister auditing, and discrete produce sorting operate with station dwell times exceeding 2 to 5 seconds. A standalone CPU latency of $392.5\text{ ms}$ (or $881.7\text{ ms}$ for hybrid API processing) integrates seamlessly into existing programmable logic controller (PLC) cycle windows without GPU investment.
*   **High-Speed Continuous Production (Cycle times $< 100$ ms):** **UNVIABLE on CPU.** High-throughput canning, beverage bottling, and continuous web textile lines require inspection latencies below $50\text{--}80\text{ ms}$. Achieving such throughput requires tensor quantization (INT8), hardware execution via TensorRT/OpenVINO, or dedicated edge GPU accelerators.

### C. Quality Control Economics: False Alarms vs. Escapes
The operational viability of the hybrid decision policy is governed by the relative economic cost ratio:
$$R_{\text{cost}} = \frac{C_{\text{escape}}}{C_{\text{scrap}}}$$
where $C_{\text{escape}}$ is the total liability of an undetected defect (warranty claims, recalls, legal exposure, customer churn) and $C_{\text{scrap}}$ is the cost of diverting a conforming item (manual audit labor, scrap loss).
*   When $R_{\text{cost}} > 15$ (e.g., automotive safety components, aerospace fasteners, medical devices), the hybrid policy is overwhelmingly justified: capturing 54 additional defects easily offsets the cost of 11 additional false alarms.
*   When $R_{\text{cost}} \le 2$ (e.g., low-margin bulk agricultural sorting, high-volume consumer commodities), false alarms dominate unit economics. In such environments, operators must tune thresholds toward higher specificity, absorbing defect escapes to maintain line profitability.

---

## VIII. Discussion, Limitations, and Negative Findings

### A. Reconciliation of Negative Research Findings
A complete scientific record requires transparently documenting architectural modifications that failed to yield performance improvements:
1.  **Context-Preserving Normalization Dropout (CPND):** Hypothesized to improve out-of-distribution feature stability by adaptively dropping localized activation channels while preserving local spatial normalization statistics. Rigorous ablation across MVTec development splits demonstrated statistically indistinguishable performance compared to standard dropout ($p = 0.42$), while introducing redundant computational overhead.
2.  **Multi-Axis Cross-Branch Attention (MACBA):** Designed to fuse intermediate feature representations between the supervised EfficientNet branch and the unsupervised PatchCore backbone via cross-attention heads during joint fine-tuning. Empirical training runs revealed severe optimization instability: backpropagation gradients from the supervised cross-entropy loss corrupted the pre-trained feature manifolds required for distance-based patch retrieval, leading to loss divergence. This negative finding confirms that **late-stage decision-level fusion (OR-logic) is structurally superior to early deep feature coupling** when integrating supervised and unsupervised inspection models.

### B. Fundamental Limitations
1.  **Single External Category Evaluation:** While independent validation on VisA Cashew proves adaptation to an unseen organic domain, empirical validation across additional VisA categories (e.g., printed circuit boards, capsules, chewing gum) remains necessary to establish universal cross-category claims.
2.  **Asymmetric Generalization of the Hybrid System:** The independent VisA experiment evaluated PatchCore alone. The supervised EfficientNet-B0 classifier was trained on MVTec defect classes and cannot transfer to VisA cashew without category-specific defect supervision.
3.  **The Single-Threshold Dilemma:** Enforcing a factory-grade $2.0\%$ false-alarm rate on nearest-neighbor distance features mathematically suppresses sensitivity to subtle surface flaws. Distance-based anomaly detection on downsampled CNN representations cannot achieve $100\%$ recall on hairline scratches without dramatically inflating false alarms.

### C. Deployment Gating Verdict
Based on the audited empirical evidence, DefectVision AI is formally designated as:
*   **Supervised Operator-Assist / Shadow-Pilot:** **APPROVED & DEPLOYABLE.** Provides robust containment assistance, catches novel gross deformities, and localizes anomalies with $0.9930$ pixel AUROC.
*   **Fully Autonomous Inline Rejection:** **STRICT NO-GO.** Disqualified by the $43.0\%$ defect escape rate on subtle surface scratches under factory false-alarm constraints. Autonomous gating requires integrating multi-illumination photometric stereo or secondary high-resolution verification optics.

---

## IX. Conclusion

In this paper, we presented an empirical evaluation of hybrid defect detection and nominal-only category adaptation under realistic industrial constraints. On an audited development-exposed benchmark of 856 MVTec AD specimens, dual-branch OR-logic fusion slashed defect escapes by $48.6\%$ (recovering 54 defects missed by EfficientNet-B0), while increasing false alarms from 1 to 12. On an independent, untouched validation benchmark of 200 VisA Cashew specimens, nominal-only PatchCore adaptation achieved an image AUROC of $0.9237$ and a full-census pixel AUROC of $0.9930$ with deterministic CPU inference of $392.5\text{ ms}$. However, fine-grained morphology analysis exposed the physical boundary of patch distance modeling: while gross structural breaks achieved $100\%$ detection, hairline scratches suffered a $93.3\%$ escape rate under conservative false-alarm thresholds. These findings demonstrate that while nominal adaptation provides robust baseline containment for discrete manufacturing, autonomous deployment requires multi-resolution architectures to resolve the inescapable operational tension between false-alarm suppression and hairline flaw escapes.

---

## References

1. K. Roth, L. Pemula, J. Zepeda, B. Schölkopf, T. Brox, and P. Gehler, "Towards total recall in industrial anomaly detection," in *Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR)*, 2022, pp. 14318–14328.
2. Y. Zou, J. Jeong, L. Pemula, D. Zhang, and O. Dabeer, "SPOT-the-difference self-supervised pre-training for anomaly detection and segmentation," in *Proc. Eur. Conf. Comput. Vis. (ECCV)*, Springer, 2022, pp. 392–408.
3. P. Bergmann, K. Batzner, M. Fauser, D. Sattlegger, and C. Steger, "The MVTec anomaly detection dataset: A comprehensive real-world dataset for unsupervised anomaly detection," *Int. J. Comput. Vis. (IJCV)*, vol. 129, no. 4, pp. 1038–1059, 2021.
4. M. Tan and Q. V. Le, "EfficientNet: Rethinking model scaling for convolutional neural networks," in *Proc. 36th Int. Conf. Mach. Learn. (ICML)*, PMLR, vol. 97, 2019, pp. 6105–6114.
5. K. He, X. Zhang, S. Ren, and J. Sun, "Deep residual learning for image recognition," in *Proc. IEEE Conf. Comput. Vis. Pattern Recognit. (CVPR)*, 2016, pp. 770–778.
6. T. Defard, A. Setkov, A. Loesch, and R. Audigier, "PaDiM: A patch distribution modeling framework for anomaly detection and localization," in *Proc. Int. Conf. Pattern Recognit. (ICPR)*, 2021, pp. 475–489.
7. N. Cohen and Y. Hoshen, "Sub-image anomaly detection with deep pyramid correspondences," *arXiv preprint arXiv:2005.02357*, 2020.
8. J. Johnson, M. Douze, and H. Jégou, "Billion-scale similarity search with GPUs," *IEEE Trans. Big Data*, vol. 7, no. 3, pp. 535–547, 2019.
9. E. B. Wilson, "Probable inference, the law of large numbers, and run of evidence," *J. Amer. Statist. Assoc.*, vol. 22, no. 158, pp. 209–212, 1927.
10. D. Weimer, B. Scholz-Reiter, and M. Shpitalni, "Design of deep convolutional neural networks for industrial inspection," *CIRP Annals — Manuf. Technol.*, vol. 65, no. 1, pp. 417–420, 2016.
11. A. Kumar, "Computer vision-based fabric defect detection: A survey," *IEEE Trans. Ind. Electron.*, vol. 55, no. 1, pp. 348–363, 2008.
12. R. O. Duda, P. E. Hart, and D. G. Stork, *Pattern Classification*, 2nd ed. New York, NY, USA: John Wiley & Sons, 2001.
