# DefectVision AI — Limitations & Future Research Roadmap
**Release:** v1.0.0-rc1 (Research Prototype)  
**Date:** 2026-11-19  

---

## 1. Documented System Limitations

DefectVision AI v1.0.0-rc1 is a research prototype evaluated on the MVTec AD benchmark. The following limitations are documented to prevent unwarranted operational assumptions:

### 1.1 Photometric and Color-Only Anomaly Blindness
- **Finding:** PatchCore utilizing ResNet-18 features pre-trained on ImageNet possesses strong inductive biases toward high-frequency spatial gradients, edges, and textures, while exhibiting invariance to pure photometric and color changes.
- **Experimental Evidence:** On the MVTec AD pill color defect set, standard PatchCore missed $92.0\%$ of color defects (recall: $8.0\%$).
- **Failed Concatenation Mitigation:** Attempting single-bank concatenation of spatial embeddings (384 channels) with color vectors (3 channels) failed completely (color recall $\le 24.0\%$). Channel dimension imbalance caused Euclidean distances to be $>98\%$ dominated by spatial variance.

### 1.2 Calibration Sample Variance in Few-Shot Adaptation
- **Finding:** In few-shot adaptation ($K=10, 20$), estimating an empirical decision threshold $\tau = \max(S_{\text{cal}})$ from a small calibration sample ($N_{\text{cal}} = 10$) introduces severe sampling variance.
- **Consequence:** In the K=20 bottle experiment, the calibration set happened to underestimate the normal test set variance, yielding a $20.0\%$ false positive rate under the un-tuned policy.
- **Rule of Three Constraint:** Observing 0 false alarms on 20 test bottles yields an upper 95% confidence bound of $15.0\%$, which cannot prove factory-grade sub-1% false alarm rates.

### 1.3 External Domain Shift & Track B Status
- **Finding:** Domain shifts caused by uncontrolled smartphone optics, ambient illumination changes, non-rigid object pose variations, and cluttered backgrounds severely degrade performance relative to MVTec AD conditions.
- **Current Status:** **`BLOCKED — DATA REQUIRED`**. The current external dataset contains only 1 physical defect specimen, precluding statistically meaningful claims of external factory adaptation.

### 1.4 Inference Speed on High-Throughput Lines
- **Finding:** Single-image CPU latency averages $110 - 165 \text{ ms}$ (approx. $6 - 9$ frames per second). High-speed industrial lines operating at $30 - 120$ parts per second require GPU acceleration, quantization, or specialized hardware.

---

## 2. Future Research Roadmap

```
                                  [ DefectVision AI Roadmap ]
                                               │
               ┌───────────────────────────────┼───────────────────────────────┐
               ▼                               ▼                               ▼
    [ Decoupled Dual-Stream ]         [ Foundation Backbones ]          [ Edge Optimization ]
    - Decoupled Spatial & Color        - DINOv2 ViT Backbones           - INT8 / FP16 Quantization
      Memory Banks                     - Self-Supervised Reps           - TensorRT Engine Export
    - Max-Ratio Decision Fusion        - Enhanced Color Sensitivity     - Sub-15ms Latency on Jetson
    - Preserves Subspace Balance       - Zero-Shot Category Intake      - Industrial GigE Camera SDK
```

### 2.1 Decoupled Dual-Stream Spatial-Photometric Architecture (Experiment 2)
To resolve photometric blindness without subspace corruption, a decoupled dual-stream architecture is designed:
- **Spatial Stream:** ResNet-18 (Layers 2 & 3), embedding dim 384, independent memory bank $\mathcal{M}_s$, threshold $\tau_s$.
- **Photometric Stream:** Dense patch Lab/HSV statistics, embedding dim 3, independent memory bank $\mathcal{M}_c$, threshold $\tau_c$.
- **Max-Ratio Decision Fusion:**
  $$s_{\text{fused}} = \max\left(\frac{s_s}{\tau_s}, \frac{s_c}{\tau_c}\right)$$
  Anomalies in either structural morphology or color independently trigger a defect decision when $s_{\text{fused}} > 1.0$.

### 2.2 Foundation Vision Transformer Backbones (DINOv2)
Replacing supervised ImageNet CNNs with self-supervised vision transformers (DINOv2-S/B) provides richer patch semantics that naturally balance semantic structure and color appearance without requiring separate handcrafted color extractors.

### 2.3 Extreme Value Theory (EVT) Calibration
Replacing empirical sample maximums with statistical Extreme Value Theory (fitting Generalized Extreme Value / Gumbel distributions to calibration tail scores) to establish mathematically guaranteed false alarm rates at defined confidence levels.

### 2.4 Edge Acceleration and Hardware Interfacing
Compiling the ResNet-18 extractor and FAISS indexes into NVIDIA TensorRT engines and ONNX Runtime to achieve sub-15ms inference latency for embedded deployment on NVIDIA Jetson Orin platforms.
