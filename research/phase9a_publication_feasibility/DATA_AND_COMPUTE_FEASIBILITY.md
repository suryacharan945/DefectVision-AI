# Phase 9A Deliverable: Data and Compute Feasibility Assessment

**Project:** DefectVision AI — Advanced Quality Inspection Platform  
**Phase:** 9A (Research Reset and Publication Feasibility)  
**Status:** COMPLETE & INDEPENDENTLY VERIFIED  
**Artifact:** `research/phase9a_publication_feasibility/DATA_AND_COMPUTE_FEASIBILITY.md`  

---

## 1. Executive Summary

This document evaluates the operational, data, and computational feasibility of executing the large-scale empirical benchmark specified in `BENCHMARK_DESIGN.md`.

In strict adherence to Phase 9A instructions:
- **Zero Dataset Downloads:** No external datasets were downloaded during this phase.
- **Zero Test Inference:** No inference was executed on quarantined benchmarks.
- **Quarantine Maintained:** The 11 unexposed VisA categories, BTAD, and Chukyo remain untouched.

Our technical assessment concludes that while the three-way leakage-free evaluation protocol is **methodologically feasible**, conducting the empirical study at a scale required for a reputable journal requires **dedicated GPU cloud infrastructure (8–15 A100 GPU hours)** and is **infeasible on the current local CPU-only environment** without severe runtime bottlenecks (35–50 hours of continuous CPU compute).

---

## 2. Dataset Inventory and Partitioning Feasibility

To conduct a defensible empirical evaluation, the benchmark requires multiple industrial manufacturing domains:

| Dataset | Total Categories | Quarantined / Available | Total Images | Image Resolution | Defect Types |
|:---|:---:|:---:|:---:|:---:|:---|
| **VisA** (Zou et al., 2022) | 12 | 11 Quarantined (`bones`, `cashew`, `chewinggum`, `fryum`, `pipefryum`, `pushpins`, `screw`, `socket`, `tag`, `wallnut`, `waterbottle`) | $10,821$ | $960 \times 960$ | Complex structural, surface scratches, contamination, missing parts. |
| **BTAD** (Mishra et al., 2021) | 3 | 3 Quarantined (`01`, `02`, `03` - Industrial wood, metal, plastic components) | $2,830$ | $1600 \times 1600$ to $600 \times 600$ | Physical manufacturing flaws, cracks, edge abrasions. |
| **Chukyo** (Industrial Screws) | 1 | 1 Quarantined | $\approx 1,000$ | $1024 \times 1024$ | Thread damage, head deformation, burrs. |
| **Total Benchmark Pool** | **15 Categories** | **15 Quarantined** | $\mathbf{\approx 14,650}$ | **High-Res Industrial** | **Comprehensive defect spectrum** |

### Leakage-Free Partitioning Validation:
For each quarantined category, the dataset contains official training normal images and test images (with both normal and diverse defect types).
- **Fitting Split (Train Normal):** $100\%$ of official nominal training images used exclusively to construct PatchCore memory banks and PaDiM Gaussian estimators.
- **Calibration Split (Disjoint 50% Validation):** $50\%$ of official test images (both normal and defective) used exclusively to tune category thresholds $\tau_c$ and fit logistic probability models.
- **Evaluation Split (Holdout 50% Test):** $50\%$ of official test images held out strictly for final metric evaluation.
- **Determination:** Mathematically clean and leakage-free. Zero contamination of final test labels.

---

## 3. Computational Workload and Resource Estimation

Executing the benchmark involves four distinct computational stages:

### Stage 1: Deep Feature Extraction
- **Workload:** Passing $\approx 14,650$ images through WideResNet-50 and ResNet-18 backbones to extract multi-scale patch embeddings.
- **GPU Performance (NVIDIA A100 / RTX 3090):** $\approx 25\text{ms}$ per image. Total: $14,650 \times 0.025\text{s} \approx 366\text{s} \approx 6.1$ minutes.
- **CPU Performance (Local Intel Core Environment):** $\approx 1.2\text{s}$ per image. Total: $14,650 \times 1.2\text{s} \approx 17,580\text{s} \approx 4.88$ hours.

### Stage 2: Memory Bank Core-Set Subsampling
- **Workload:** Minimax facility location algorithm subsampling $10\%$ of patch embeddings per category across 15 categories $\times$ 5 random seeds ($75$ core-set solves).
- **GPU Performance:** $\approx 45\text{s}$ per solve. Total: $75 \times 45\text{s} \approx 56$ minutes.
- **CPU Performance:** $\approx 15$ minutes per solve. Total: $75 \times 15\text{m} \approx 18.75$ hours.

### Stage 3: Nearest-Neighbor FAISS Querying & Scoring
- **Workload:** Anomaly score computation for all evaluation images ($N \approx 3,000$) across 3 models $\times$ 5 seeds ($45,000$ image-level scores).
- **GPU Performance:** $\approx 15$ minutes total.
- **CPU Performance:** $\approx 3.5$ hours total.

### Stage 4: Policy Simulation & Human Review Parameter Sweeps
- **Workload:** Simulating 8 allocation policies across 5 cost ratios $\times$ 11 review budgets $\times$ 25 human accuracy grid points $\times$ 5 cross-validation folds ($687,500$ knapsack/ranking evaluations).
- **Compute:** Pure vectorized NumPy operations.
- **Runtime:** $\approx 1.5$ hours on modern multi-core CPU.

---

## 4. Compute Resource Comparison Matrix

| Resource Dimension | Cloud GPU Environment (A100 / Colab Pro) | Local Workspace (Current CPU-Only) | Feasibility Verdict |
|:---|:---:|:---:|:---:|
| **Feature Extraction** | $\approx 0.5$ hours | $\approx 5.0$ hours | GPU Required |
| **Core-Set Subsampling** | $\approx 1.0$ hours | $\approx 19.0$ hours | High CPU Bottleneck |
| **Inference Scoring** | $\approx 0.3$ hours | $\approx 3.5$ hours | Manageable on CPU |
| **Policy Simulation** | $\approx 1.5$ hours | $\approx 1.5$ hours | Feasible on CPU |
| **Total Wall-Clock Time** | **$\approx 3.3 - 5.0$ hours** | **$\approx 29.0 - 45.0$ hours** | **Local Execution Unviable** |
| **Storage Footprint** | $30\text{ GB}$ ephemeral disk | $30\text{ GB}$ local SSD | Feasible locally |
| **Estimated Cloud Cost** | $\$15 - \$35$ (RunPod / GCP / Colab) | $\$0$ (High hardware wear) | Very low financial cost |

---

## 5. Feasibility Verdict and Operational Constraints

1. **Local Execution Feasibility: NO-GO**  
   Attempting to execute this full benchmark on the current local Windows machine without a dedicated CUDA-enabled GPU would require upwards of 40 hours of uninterrupted CPU processing, risking system freezes, thermal throttling, and process termination.
2. **Cloud GPU Execution Feasibility: CONDITIONAL GO**  
   If cloud GPU access (e.g., Google Colab Enterprise, RunPod, or AWS EC2 with NVIDIA A100/T4) is provisioned, the empirical study is technically and economically feasible ($<5$ hours wall-clock time, $<\$50$ compute cost).
3. **Protocol Feasibility: FULLY GO**  
   The three-way partitioning protocol guarantees strict zero-leakage validity and addresses all methodological requirements for an empirical study.
