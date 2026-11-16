# DefectVision AI — Verified Scientific Claims & Evidence Boundaries

**Phase:** Phase 51 — Evidence Reconciliation and Journal Manuscript  
**Role:** Senior Computer Vision Researcher, Scientific Editor, and Research Integrity Auditor  
**Workspace:** `C:\Users\surya\Downloads\Mini Project`  
**Date:** November 2, 2026  
**Status:** **PERMANENTLY FROZEN FOR MANUSCRIPT DRAFTING**

---

## 1. Absolute Boundary Rules (Strict Prohibitions)

The following claims are **STRICTLY PROHIBITED** from appearing in the manuscript draft, abstracts, or presentations:

1.  **NO Claim of Algorithmic or Architectural Novelty:**  
    Do not claim novel neural network layers, novel loss formulations, or new mathematical operators. The system combines established components: PatchCore (Roth et al., CVPR 2022) with a ResNet-18 backbone and EfficientNet-B0 v3 (Tan & Le, ICML 2019). Architectural experiments (CPND, MACBA) yielded negative/unstable results and serve as negative findings.
2.  **NO Claim of Zero-Shot or Universal Generalization:**  
    Do not claim zero-shot transfer across industrial categories. Target-domain adaptation requires $350$ nominal (defect-free) calibration specimens from the target manufacturing line to populate the nearest-neighbor coreset.
3.  **NO Conflation of Independent and Development-Exposed Cohorts:**  
    **NEVER** state or imply that the "hybrid architecture" was independently validated.  
    - The **Hybrid Architecture** (EfficientNet-B0 + PatchCore) was evaluated strictly on the **Development-Exposed MVTec AD benchmark** ($856$ specimens).  
    - The **Independent Evaluation** on VisA Cashew evaluated **PatchCore Nominal-Only Registration alone** ($200$ test specimens). EfficientNet-B0 was trained on MVTec defect classes and cannot transfer to VisA without supervised labels.
4.  **NO Claim of Unassisted Production Deployment Readiness:**  
    Autonomous inline sorting is **DISQUALIFIED** due to a $43.0\%$ defect escape rate on subtle hairline scratches under factory-grade false-alarm thresholds ($\tau_{\text{p99}}$). The system is viable strictly for **supervised human-in-the-loop assistance** and **asynchronous shadow-pilot evaluation**.
5.  **NO Speculative or Fabricated Explanations as Proven Facts:**  
    Hypotheses regarding feature pooling dilution on hairline scratches must be stated as *mechanistic hypotheses consistent with observations*, not as experimentally isolated causal proofs.

---

## 2. Segregated Evidence-to-Claim Matrix

---

### Domain A: Development-Exposed MVTec Hybrid Results
*Evaluated on 856 MVTec AD specimens across 15 categories. Supervised and unsupervised models were iteratively refined on development splits.*

| Claim # | Claim Statement | Verified Quantitative Evidence | Boundary Condition / Qualification |
| :--- | :--- | :--- | :--- |
| **A-1** | Supervised EfficientNet-B0 provides high precision on recurring defects. | Standalone EfficientNet-B0: $764/856$ accuracy ($86.92\%$), $514/625$ recall ($82.24\%$), precision $99.81\%$, only **$1$ false alarm** ($\text{FP}=1$, FPR $0.43\%$). | Vulnerable to novel defect geometries, escaping **$111$ defect instances** ($\text{FN}=111$, FNR $17.76\%$). |
| **A-2** | Unsupervised PatchCore captures out-of-distribution defects without defect supervision. | Standalone PatchCore: $669/856$ accuracy ($78.15\%$), $449/625$ recall ($71.84\%$), catching diverse topological flaws, but producing **$11$ false alarms** ($\text{FP}=11$, FPR $4.76\%$). | Lower precision ($97.61\%$) and higher nuisance false alarm rate due to natural surface variations. |
| **A-3** | Dual-branch hybrid fusion (logical OR) slashes defect escapes relative to the supervised model. | Hybrid System: $787/856$ accuracy ($91.94\%$), $568/625$ defect recall ($90.88\%$). Captured **$54$ defects missed by EfficientNet-B0** (reducing escapes from $111$ to $57$). | Must be explicitly labeled Category C Development-Exposed. Does not represent zero-leakage generalization. |
| **A-4** | Defect escape reduction incurs an explicit false-alarm scrap penalty. | Hybrid false alarms increased from **$1$ to $12$** ($\text{FP}=12$, FPR $5.19\%$, an increase of **$+11$ false alarms** or $+4.76$ percentage points). | The hybrid represents an asymmetric operating trade-off, not a strict Pareto improvement across all metrics. |

---

### Domain B: Independently Evaluated VisA Cashew Adaptation
*Evaluated on 200 untouched specimens (100 nominal, 100 defective) from the official Amazon Science VisA Cashew distribution after registering 350 domain-specific nominal images. Evaluates PatchCore memory alone.*

| Claim # | Claim Statement | Verified Quantitative Evidence | Boundary Condition / Qualification |
| :--- | :--- | :--- | :--- |
| **B-1** | Nominal-only PatchCore registration separates normal and defective specimens on an unseen category. | Image-level AUROC: **$0.9237$** ($95\%$ CI: $[0.8852, 0.9565]$), Image-level AUPRC: **$0.9270$**. | Requires $350$ nominal calibration images and a $27,440$-token coreset. Not zero-shot. |
| **B-2** | Calibrating $\tau$ at the 99.5th nominal percentile achieves industrial-grade false-alarm suppression. | Specificity: **$98.00\%$** ($98/100$ nominals cleared; $95\%$ CI: $[92.96\%, 99.45\%]$); False Positive Rate: **$2.00\%$** ($2/100$ false alarms). Precision: **$96.61\%$** ($57/59$). | Operating point locked at $\tau_{\text{p99}} = 1.745232$ derived strictly from 50 nominal calibration samples. |
| **B-3** | Conservative false-alarm control causes substantial defect escape on fine surface flaws. | Defect Recall: **$57.00\%$** ($57/100$ defects caught; $95\%$ CI: $[47.24\%, 66.24\%]$); Defect Escape Rate: **$43.00\%$** ($43/100$ defects missed). Overall Accuracy: $77.50\%$. | Demonstrates the fundamental trade-off of distance-based detection on organic substrates. |
| **B-4** | Detection sensitivity is strictly partitioned by physical defect morphology. | Gross breaks & deformation: `middle breakage` $6/6$ ($100\%$), `stuck together` $6/6$ ($100\%$), `holes` $17/20$ ($85\%$). Fine surface flaws: `small scratches` $1/15$ ($6.7\%$), `same colour spot` $0/10$ ($0.0\%$). | Nearest-neighbor distance in downsampled feature space cannot reliably resolve sub-pixel hairline scratches on textured surfaces. |
| **B-5** | Spatial anomaly heatmaps provide high pixel-level localization accuracy. | Full-Census Pixel AUROC across $10,035,200$ test pixels: **$0.9930$**; Defect-Only Specimen Pixel AUROC ($5,017,600$ pixels): **$0.9877$**. | Uses bilinear interpolation to $224 \times 224$ and Gaussian smoothing ($\sigma=4.0$). |

---

### Domain C: CPU Runtime and Deployment Constraints
*Benchmarked on Intel Core i7-10750H @ 2.60GHz, 16 GB DDR4 RAM, PyTorch CPU, FAISS-CPU.*

| Claim # | Claim Statement | Verified Quantitative Evidence | Boundary Condition / Qualification |
| :--- | :--- | :--- | :--- |
| **C-1** | Memory registration is viable on standard workstation hardware without GPUs. | 350 registration images ($274,400$ raw patch vectors $\to$ $27,440$ coreset tokens) processed in **$392.25$ seconds** ($\sim 6.5$ minutes). | Coreset memory bank size: $40.2\text{ MB}$; FAISS index size: $40.2\text{ MB}$. RAM working set $< 650\text{ MB}$. |
| **C-2** | PatchCore standalone inference provides deterministic sub-half-second execution on CPU. | Median CPU latency: **$392.5\text{ ms}$**, Mean: $396.7\text{ ms}$, p95: **$438.1\text{ ms}$**. | Validated for $224 \times 224$ resolution with $27,440$ coreset tokens in memory. |
| **C-3** | End-to-end hybrid API inference satisfies discrete inspection cycle times $\ge 1.5$ seconds. | Hybrid API round-trip: Median **$881.7\text{ ms}$**, p95 **$1455.7\text{ ms}$**. | Unsuitable for ultra-high-speed canning/bottling lines ($< 100\text{ ms}$ takt time) without GPU/TensorRT acceleration. |

---

### Domain D: Limitations and Negative Findings
*Rigorous accounting of technical boundaries and experimental dead-ends.*

| Finding # | Description of Finding | Empirical Evidence | Scientific Significance |
| :--- | :--- | :--- | :--- |
| **D-1** | Context-Preserving Normalization Dropout (CPND) failed to improve generalizability. | Extensive ablation showed statistically indistinguishable performance from standard dropout ($p > 0.05$). | Documented as an engineering negative finding; prevents redundant research exploration. |
| **D-2** | Multi-Axis Cross-Branch Attention (MACBA) suffered severe optimization instability. | Joint training of attention cross-connections between supervised and unsupervised branches led to gradient collapse and loss divergence. | Demonstrates that late-stage OR-logic decision fusion is superior to early-stage deep feature coupling. |
| **D-3** | Single-Threshold Dilemma in Distance-Based Anomaly Detection. | Enforcing $FPR \le 2\%$ on VisA cashew causes $93.3\%$ of scratches and $100\%$ of same-color indentations to escape. | Proves that distance to nominal feature manifold cannot simultaneously eliminate false alarms and guarantee hairline surface sensitivity. |
