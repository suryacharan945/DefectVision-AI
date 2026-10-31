# Phase 7C: Computational Profile & Scalability Assessment

**Document ID:** `DV-PHASE7C-PERF-V1`  
**Date:** October 31, 2026  
**Hardware Platform:** Intel Core i5-1135G7 @ 2.40GHz (4 cores / 8 threads), 16GB DDR4 RAM, Windows 11  
**Execution Environment:** Python 3.12 64-bit, PyTorch 2.1 CPU, FAISS-CPU 1.8.0

---

## 1. Latency Profile

| Stage | Baseline PatchCore | Raw CPND (Phase 7B) | Density-Normalized CPND (Phase 7C) | Incremental Overhead |
| :--- | :---: | :---: | :---: | :---: |
| **Image Preprocessing (OpenCV 224x224)** | 2.1 ms | 2.1 ms | 2.1 ms | 0.0 ms |
| **ResNet-18 Backbone Embedding** | 22.4 ms | 22.4 ms | 22.4 ms | 0.0 ms |
| **Average Pooling & Feature Projection** | 4.8 ms | 4.8 ms | 4.8 ms | 0.0 ms |
| **FAISS Nearest Neighbor Search** | 9.1 ms (1-NN) | 13.9 ms ($k=5$) | 13.9 ms ($k=5$) | +4.8 ms |
| **Local Reference Statistics Lookup** | — | — | 1.1 ms | +1.1 ms |
| **Robust Median / MAD Calculation** | — | — | 0.2 ms | +0.2 ms |
| **Boundary Gating Evaluation** | — | — | < 0.1 ms | < 0.1 ms |
| **Total Inference Latency per Image** | **38.4 ms** | **43.2 ms** | **44.5 ms** | **+6.1 ms (+15.9%)** |
| **Throughput (Images / Second)** | **26.0 img/s** | **23.1 img/s** | **22.5 img/s** | **-3.5 img/s** |

---

## 2. Memory Footprint Profile

| Resource Component | Memory Usage per Category | Multi-Category (15 Categories) | Notes |
| :--- | :---: | :---: | :--- |
| **PatchCore Memory Bank (Array)** | 22.8 MB (15k x 384 x 4B) | 342.0 MB | Nominal coreset features |
| **FAISS FlatL2 Index** | 23.8 MB | 357.0 MB | In-memory exact search index |
| **Nominal Training Dispersions ($U_{\text{train}}$)** | **59.2 KB** (15k x 4B) | **0.89 MB** | Negligible offline reference array |
| **Peak Resident Set Size (RSS)** | 342 MB | ~720 MB | Full backend daemon process |

---

## 3. Offline Precomputation Cost

Nominal training reference dispersions are precomputed once during model initialization with self-neighbor exclusion:
- `bottle` (14,739 vectors): $1.68\text{ seconds}$
- `capsule` (15,444 vectors): $2.24\text{ seconds}$
- `metal_nut` (15,523 vectors): $2.15\text{ seconds}$
- **Average Offline Initialization Time:** $2.02\text{ seconds}$ per category.

---

## 4. Engineering & Deployment Assessment

From a pure computational perspective, Density-Normalized CPND satisfies all edge latency and memory requirements:
- Latency overhead of $+6.1\text{ ms}$ is well below the pre-registered limit of $15\text{ ms}$.
- Memory overhead of $59\text{ KB}$ is negligible.
- **However, because the method provides negative incremental error capture over Distance-to-Threshold ($\Delta \text{ECR} = -4.84\%$), deploying this additional computational overhead is scientifically unjustified.**
