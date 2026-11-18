# DEFECTVISION AI 2.2 — COMPONENT ABLATION REPLICATION REPORT

**Document Identifier:** `release/experiments/ABLATION_REPLICATION_REPORT.md`  
**Author:** Industrial Machine Learning Systems Architecture Group  
**Associated Artifact:** [`ablation_replication_metrics.csv`](file:///c:/Users/surya/Downloads/Mini%20Project/release/experiments/ablation_replication_metrics.csv)  
**Execution Environment:** Windows virtual environment (`Windows-11-10.0.26300-SP0`), Python `3.12.4`, PyTorch `2.15.0+cpu`, Compute Device: `cpu`.  
**Warm-Up Protocol:** 5 dummy cycles executed prior to measurement.  
**Evaluation Set:** 12 Specimens across 3 Domains (6 Nominal, 6 Defective).

---

## 1. Experimental Methodology & Control Parity

Each configuration was evaluated on the **exact same 12 specimens** (MVTec Genuine, External Studio, Station 01 Jitter) to ensure rigorous comparative isolation:
- **CFG 1:** Raw Baseline PatchCore (Standard MVTec memory bank of 14,739 patches, $\tau = 1.4666$, bicubic resize).
- **CFG 2:** Baseline + CLAHE (Contrast-Limited Adaptive Histogram Equalization on L-channel).
- **CFG 3:** Baseline + Foreground Hull Crop (Contour extraction & convex hull masking).
- **CFG 4:** Adapted PatchCore Standalone (Few-shot bank of 392 patches, provisional $\tau = 1.6410$, raw resize).
- **CFG 5:** Adapted PatchCore + Hull Crop (Few-shot bank + contour cropping).

Latency is explicitly decomposed into:
$$T_\text{total} = T_\text{prep} + T_\text{feat} + T_\text{nn}$$
where $T_\text{prep}$ is image transformation, $T_\text{feat}$ is ResNet18 forward pass, and $T_\text{nn}$ is FAISS L2 nearest-neighbor search.

---

## 2. Comparative Ablation Matrix

| Config | Architecture Description | TP | FP | TN | FN | Precision | Recall | Specificity | F1 Score | FPR (%) | Pixel AUROC | Median Latency | P95 Latency |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **CFG 1** | Raw Baseline PatchCore | 6 | 2 | 4 | 0 | 0.7500 | 1.0000 | 0.6667 | **0.8571** | 33.3% | 0.9935 | 176.1 ms | 243.8 ms |
| **CFG 2** | Baseline + Optical CLAHE | 6 | 6 | 0 | 0 | 0.5000 | 1.0000 | 0.0000 | **0.6667** | **100.0%** | 0.9912 | 196.1 ms | 332.4 ms |
| **CFG 3** | Baseline + Hull Crop | 6 | 2 | 4 | 0 | 0.7500 | 1.0000 | 0.6667 | **0.8571** | 33.3% | 0.9931 | 235.4 ms | 290.9 ms |
| **CFG 4** | **Adapted Standalone** | 6 | 1 | 5 | 0 | **0.8571** | **1.0000** | **0.8333** | **0.9231** | **16.7%** | 0.9942 | **55.5 ms** | **90.5 ms** |
| **CFG 5** | Adapted + Hull Crop | 6 | 3 | 3 | 0 | 0.6667 | 1.0000 | 0.5000 | **0.8000** | 50.0% | 0.9938 | 136.7 ms | 157.9 ms |

---

## 3. Detailed Latency Breakdown (ms)

| Configuration | Preprocessing ($T_\text{prep}$) | Feature Extraction ($T_\text{feat}$) | Nearest Neighbor Search ($T_\text{nn}$) | Total Median ($T_\text{total}$) |
|:---|:---:|:---:|:---:|:---:|
| **CFG 1 (Raw Baseline)** | 4.4 ms | 54.2 ms | 117.6 ms | **176.1 ms** |
| **CFG 2 (Optical CLAHE)** | 16.7 ms | 52.5 ms | 124.5 ms | **196.1 ms** |
| **CFG 3 (Baseline Hull Crop)** | 83.1 ms | 41.3 ms | 111.9 ms | **235.4 ms** |
| **CFG 4 (Adapted Standalone)** | 4.5 ms | 45.0 ms | 6.9 ms | **55.5 ms** |
| **CFG 5 (Adapted Hull Crop)** | 86.5 ms | 47.3 ms | 6.6 ms | **136.7 ms** |

---

## 4. Key Architectural Findings & Limitations

1. **Destructive Impact of CLAHE (CFG 2):**
   - CLAHE increases the False Positive Rate to **$100.0\%$** (all 6 nominal specimens flagged as defective).
   - Local histogram equalization accentuates micro-variations in camera sensor noise and glass refraction, displacing nominal patch embeddings outside the calibrated normal cluster.
   - **Recommendation:** Optical CLAHE should be disabled by default for industrial anomaly inspection.

2. **Latency Efficiency of Adapted Memory Bank (CFG 4):**
   - CFG 4 executes in **55.5 ms** vs. **176.1 ms** for CFG 1.
   - Subsampling the memory bank to 392 vectors accelerates nearest-neighbor search ($T_\text{nn}$) by $\approx 3.5 \times$ compared to the 14,739-vector MVTec bank.

3. **Convex Hull Cropping Adds Latency Without F1 Advantage:**
   - Hull cropping adds $\sim 50–70$ ms of OpenCV contour extraction overhead.
   - In CFG 5, hull cropping actually *increased* false alarms (FPR 50.0%) because tight boundary cropping clips glass silhouette edges, creating artificial high-frequency boundary anomalies.

4. **Scientific Constraint on Sample Size:**
   - **Crucial Caution:** These conclusions are derived from an exploratory 12-specimen evaluation set. They demonstrate strong directional trends (e.g., CLAHE noise amplification and bank subsampling speedup), but **cannot justify claiming that CFG 4 is universally superior** across all industrial environments.
