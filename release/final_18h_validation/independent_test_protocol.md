# DefectVision AI — Independent Generalization Protocol

**Protocol Status:** FROZEN & RESERVED (Non-Exposure Maintained)  
**Verification Date:** 2026-11-01  
**Sprint Phase:** Phase 3 Pre-Flight Protocol  
**Compliance Standard:** Zero-Leakage Independent Generalization Protocol V3

---

## 1. Ethical Mandate & Benchmark Reservation Policy

In high-stakes visual quality assurance, empirical validity requires strict separation between:
1. **Development & Ablation Cohorts:** Datasets used to select architectures, calibrate anomaly baselines, or evaluate feature representations (MVTec AD).
2. **Reserved Independent Benchmarks:** Datasets preserved under quarantine to prevent overfitting, unconscious hyperparameter tuning, or indirect leakage.

### Quarantine Status of Reserved Cohorts:
- **Visual Anomaly (VisA) Benchmark:**
  - `candle` & `pcb1`: Historically exposed during exploratory prototype debugging (documented in release audit commit `b9d087c`).
  - **Remaining 11 VisA Categories:** (`capsules`, `cashew`, `chewinggum`, `fryum`, `macaroni1`, `macaroni2`, `pcb2`, `pcb3`, `pcb4`, `pipe_fryum`, `printed_circuit_board`): **STRICTLY RESERVED / UNTOUCHED**.
- **BeanTech Anomaly Detection (BTAD):** **STRICTLY RESERVED / UNTOUCHED**.
- **Chukyo Industrial Dataset:** **STRICTLY RESERVED / UNTOUCHED**.

In accordance with Sprint Constraint 5 ("Do not access previously reserved independent datasets without explicit user approval"), DefectVision AI maintains an uncompromised testing boundary. **No inference was run on these reserved sets.**

---

## 2. Independent Evaluation Protocol Specification

When authorized for external validation, independent generalization must adhere to the following protocol:

### Step 1: Pre-Execution Model Freezing
- All model weights (`best_model.pt`, SHA-256 `f470b76d7c00...`), memory banks (15 categories), and severity baselines (`step9_severity_baselines.csv`) must be hashed and verified prior to cohort ingestion.
- Zero fine-tuning, adaptation, or threshold recalibration is permitted on the target domain.

### Step 2: Unsupervised Zero-Shot Domain Ingestion
- For unseen categories (e.g. VisA `capsules` or BTAD `product01`):
  1. If evaluating unsupervised PatchCore: Extract coreset memory bank strictly from target nominal training images ($\le 10\%$ coreset ratio).
  2. Baseline calibration: Compute mean $\mu_0$ and 99.5th percentile $\tau_{p99}$ strictly from held-out target nominal validation splits.
  3. Zero-defect exposure: The model must never encounter target defective specimens prior to test inference.

### Step 3: Out-of-Distribution (OOD) Sensor Generalization
- The system must evaluate raw image tensors across varying sensor resolutions, aspect ratios, and illumination conditions without ad-hoc parameter tweaks.
- Report both raw anomaly score distributions and normalized severity scores.

---

## 3. Protocol Independence Statement

```
================================================================================
INDEPENDENT BENCHMARK STATUS:
  - VisA (11 Reserved Categories): NOT ACCESSED / QUARANTINE PRESERVED
  - BTAD (3 Industrial Products):  NOT ACCESSED / QUARANTINE PRESERVED
  - Chukyo Metal Screws:          NOT ACCESSED / QUARANTINE PRESERVED
  
VERDICT:
  INDEPENDENT GENERALIZATION: NOT EVALUATED ON UNSEEN DOMAINS / PRESERVED BENCHMARKS
  REASON: PRESERVATION OF BLIND VALIDATION INTEGRITY PENDING EXPLICIT AUTHORIZATION
================================================================================
```
This protocol ensures that DefectVision AI makes zero ungrounded claims of generalizability beyond its verified MVTec AD development domain.
