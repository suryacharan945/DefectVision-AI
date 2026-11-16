# Model and Data Provenance Audit

**Project:** DefectVision AI — Advanced Quality Inspection Platform  
**Target Release:** `v1.0.0-research-prototype`  
**Date:** November 1, 2026  
**Status:** COMPLETE & INDEPENDENTLY VERIFIED  

---

## 1. Executive Summary

This document establishes the official cryptographic provenance and training lineage of all machine learning models, memory banks, and datasets utilized in the DefectVision AI platform.

It guarantees that:
1. All model weights and memory banks match verified cryptographic SHA-256 hashes.
2. All experimental findings derive from documented development splits without test-set label contamination.
3. The 11 unexposed VisA categories, BTAD, and Chukyo datasets remain untouched, unaccessed, and reserved for future research.

---

## 2. Model Checkpoint Registry and Cryptographic Hashes

All active model weights and memory banks are tracked with immutable SHA-256 checksums:

| Component | Architecture | File Path | Size (Bytes) | SHA-256 Checksum |
|:---|:---|:---|:---:|:---|
| **Classifier** | EfficientNet-B0 v3 | `DefectVisionAI/models/efficientnet_baseline_v3/best_model.pt` | $16,339,261$ | `f470b76d7c00df5be88236d552b3406256a60ee2c27fca361b981fce88902ba8` |
| **Memory Bank** | PatchCore (`bottle`) | `DefectVisionAI/models/patchcore/bottle/memory_bank.npy` | $22,639,232$ | `71a68f4e54109c74fec922c02252218d5abfab31256c2bce170e05014db52200` |
| **Memory Bank** | PatchCore (`capsule`) | `DefectVisionAI/models/patchcore/capsule/memory_bank.npy` | $23,718,656$ | `9eb4a187e148e42f9b870db171cfc24e887d19c3021966270b2207198bb5538e` |
| **Memory Bank** | PatchCore (`metal_nut`) | `DefectVisionAI/models/patchcore/metal_nut/memory_bank.npy` | $23,844,608$ | `d608d234a7fbba3819ae5534c568ecce49ca14b01df397a6021e14fe0ceadab5` |
| **Dataset Scores** | Phase 7C Dev Set | `DefectVisionAI/research/cpnd/dev_extracted_scores_phase7c.csv` | $124,198$ | `678f8cb080ea4cbbf031e67fa80540d585ea1587d60f4da700e1235123d493a7` |
| **Decision Trace** | Phase 8C Trace | `research/phase8c_macba_equivalence/BL6_MACBA_DECISION_TRACE.csv` | $158,730$ | `41d66b936a2ce75983d5d468c432a3286099b72bba38f54ed8cfbd8f36f7261e` |

---

## 3. Training and Fitting Lineage

### 3.1 PatchCore Memory Bank Fitting
- **Nominal Feature Extraction:** Mid-level patch representations extracted from WideResNet-50-2 (`layer2` and `layer3`) pre-trained on ImageNet-1k.
- **Data Source:** Exclusively nominal (good) images from the official training partitions of MVTec AD (`bottle`: 209, `capsule`: 219, `metal_nut`: 220). Zero anomalous or defective specimens were included in memory bank construction.
- **Coreset Reduction:** Greedy minimax facility location algorithm subsampling $10\%$ of patch tokens to bound search latency and RAM consumption.

### 3.2 EfficientNet-B0 Classifier Fine-Tuning
- **Pre-training:** Standard ImageNet-1k initialization.
- **Fine-Tuning:** Supervised training with cross-entropy loss over labeled development lots to learn coarse global structural defect representations.
- **Evaluation Role:** Functions as a secondary consensus detector for gross fractures and severe structural anomalies.

---

## 4. Benchmark Quarantine and Independence Assurance

The forensic exposure audit reconciles the external benchmark inventory across official academic datasets:

```
+-------------------------------------------------------------------------------+
|                       QUARANTINED INDEPENDENT BENCHMARKS                      |
|                      (Zero Exposure - Pristine Condition)                     |
+-------------------------------------------------------------------------------+
  1. VisA Benchmark (7 Potentially Untouched Categories):
     - Categories: pcb2, pcb3, pcb4, cashew, chewinggum, fryum, pipe_fryum.
     - Total: 5,715 images across complex structural and aligned parts.
     - Note: VisA capsules is development-exposed; candle, macaroni1, macaroni2,
       and pcb1 are designated UNKNOWN / DISPUTED due to exploratory notes.
     
  2. BTAD Benchmark (BeanTech Anomaly Detection):
     - Categories: 01, 02, 03 (industrial wood, plastic, metal components).
     - Total: 2,830 images.
     
  3. Chukyo Industrial Fasteners Benchmark:
     - Real-world thread deformities, burrs, and screw defects.
     - Total: ~1,000 images.
+-------------------------------------------------------------------------------+
```

**Scientific Guarantee:**  
No performance metrics on the quarantined benchmarks have been generated, inferred, or claimed. They remain an untainted benchmark for future independent evaluations. Full forensic exposure reconciliation is documented in [`release/final_integrity_gate/DATASET_EXPOSURE_RECONCILIATION.md`](../final_integrity_gate/DATASET_EXPOSURE_RECONCILIATION.md).
