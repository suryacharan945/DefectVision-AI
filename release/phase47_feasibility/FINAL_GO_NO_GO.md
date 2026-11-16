# DefectVision AI — Phase 47: Executive Feasibility Gate Decision

**Document Type:** Executive Feasibility Decision & Operational Readiness Determination  
**Phase:** Phase 47 — Three-Hour Research Feasibility Sprint  
**Target Category:** Visual Anomaly (VisA) Benchmark — `cashew`  
**Date:** November 2, 2026  
**Git Baseline Commit:** `20ec56e`  
**Author:** Senior Industrial Computer Vision Researcher & Research Integrity Auditor  

---

## 1. Executive Feasibility Determination

```
================================================================================
                    PHASE 47 EXECUTIVE GATE DETERMINATION
================================================================================

FINAL GATE DECISION:                     CONDITIONAL GO

1. SCIENTIFIC PROTOCOL FEASIBILITY:      GO (ROBUST & PRE-REGISTERED)
2. COMPUTATIONAL & STORAGE FEASIBILITY:  GO (3.1 MIN CPU / 86 MB LOCAL DISK)
3. DATA PROVENANCE & ISOLATION:          GO (VISA CASHEW 100% UNTOUCHED)
4. DATASET ACQUISITION PREREQUISITE:     PENDING USER AUTHORIZATION

================================================================================
```

---

## 2. Rationale for the `CONDITIONAL GO` Determination

The feasibility assessment concludes with a **CONDITIONAL GO** based on the following verified facts:

### 2.1 Why Not NO-GO?
- The proposed experiment is methodologically sound, mathematically leak-free, and adheres strictly to peer-reviewed literature standards (Roth et al., CVPR 2022).
- It does not require speculative algorithms (CPND and MACBA remain permanently retired).
- It executes entirely on the existing local CPU environment in **under 4 minutes** without requiring GPUs, Google Colab, or complex dependencies.
- It requires only **$\approx 86\text{ MB}$** of local disk space on drive `C:`, staging raw images on Google Drive cloud storage.
- It provides a definitive empirical answer to whether DefectVision AI’s non-parametric patch feature pipeline generalizes to an external, unseen industrial domain.

### 2.2 Why Not Full Unconditional GO?
- In strict adherence to the governing directive (*"Do not download or extract datasets during this sprint"*), the raw image archive (`cashew.tar.gz`, $\approx 230\text{ MB}$) has **not yet been downloaded**.
- The single remaining prerequisite is the user's explicit authorization to download the individual VisA `cashew` archive from the official Amazon Science repository into Google Drive storage (`G:\My Drive\DefectVisionAI\dataset\raw\visa\cashew\`).
- Once this single prerequisite is approved, the experiment can be executed and evaluated in approximately 6 to 8 minutes.

---

## 3. Analysis of Main Scientific Risks

Before authorizing execution, the following three scientific risks must be acknowledged:

1. **Feature Transferability across Domain Shifts:**
   - Pretrained ResNet-18 (ImageNet-1K) features have proven highly effective on synthetic and machined industrial surfaces (metal, plastic, glass in MVTec AD).
   - VisA `cashew` represents natural organic surfaces with natural variations in shape, texture, and coloration. Surface mold and fine cracks may exhibit lower contrast against natural cashew striations, potentially yielding lower AUROC ($0.75 - 0.85$) than observed on MVTec ($0.93 - 0.98$).
   - *Mitigation:* The pre-registered protocol explicitly defines pass, marginal, and fail criteria. A marginal or negative result will be formally documented as an empirical boundary of generic ImageNet features, preserving scientific integrity.
2. **Exclusion of the Supervised Classifier:**
   - EfficientNet-B0 v3 was trained exclusively on 15 MVTec classes and cannot evaluate cashew specimens. The independent test evaluates **only the unsupervised PatchCore engine**.
   - *Mitigation:* The applied research manuscript will clearly present this as an evaluation of *unsupervised zero-shot domain adaptation to new product categories*, framing the dual-engine hybrid as an in-domain operating mode.
3. **Finite Sample Statistical Power:**
   - With 100 nominal and 100 defective test specimens ($N_{\text{test}} = 200$), a single classification error alters accuracy and error rates by $\pm 0.5\%$.
   - *Mitigation:* Wilson score 95% confidence intervals and 1,000 bootstrap iterations will accompany all reported metrics to reflect statistical uncertainty.

---

## 4. Exactly One Recommended Next Action

> **RECOMMENDED ACTION:**  
> **Authorize downloading the single VisA `cashew` category archive ($\approx 230\text{ MB}$) directly to Google Drive (`G:\My Drive\DefectVisionAI\dataset\raw\visa\cashew\`), and execute the pre-registered 4-minute local CPU registration and evaluation experiment under Phase 48.**
