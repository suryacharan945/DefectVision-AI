# DefectVision AI — Research Archive & Provenance Manifest

**Document Type:** Formal Research & Engineering Archive Catalog  
**Effective Archival Date:** 2026-11-02  
**Baseline Private Commit:** `2a6fda2` (Branch `main`)  
**Frozen Research Tag:** `v1.0.0-research-prototype` (Commit `a6c4145`)  
**Clean Public Release Baseline:** `e3c3a78` (Tag `v1.0.0-clean`)  
**Authoritative Evidence Audit:** `release/final_18h_validation/FINAL_EVIDENCE_AUDIT.md`  
**Authoritative Closure Record:** `release/project_closure/PROJECT_CLOSURE_DECISION.md`

---

## 1. Repository Archival Topology

```
+-----------------------------------------------------------------------------------------+
|                               DEFECTVISION AI ARCHIVE TOPOLOGY                          |
+-----------------------------------------------------------------------------------------+
|                                                                                         |
|  [ 1. PRIVATE RESEARCH REPOSITORY ]                 [ 2. PUBLIC CLEAN-ROOM EXPORT ]     |
|  Path: C:\Users\surya\Downloads\Mini Project        Path: ...\DefectVisionAI-CleanExport|
|  Git Head: 2a6fda2                                  Git Head: e3c3a78                   |
|  Tag: v1.0.0-research-prototype                     Tag: v1.0.0-clean                   |
|  Status: PERMANENTLY FROZEN                         Remote: .../DefectVisionAI-OpenSource|
|  Contains: Complete research history, raw splits,   Contains: Clean source code, tests, |
|            negative findings, full audit reports              safe demo assets, MIT lic.|
|                                                                                         |
|                                                                                         |
|  [ 3. EXTERNAL MODEL & DATASET STORAGE ]            [ 4. QUARANTINED BENCHMARKS ]       |
|  Path: G:\My Drive\DefectVisionAI\                  Status: STRICTLY QUARANTINED        |
|  Contains: 15 PatchCore memory banks (2.4 GB)       - 11 Reserved VisA Categories       |
|            EfficientNet v3 checkpoint (19 MB)       - BTAD (BeanTech Anomaly Detection) |
|            Category calibration baselines           - Chukyo Anomaly Dataset            |
|                                                                                         |
+-----------------------------------------------------------------------------------------+
```

---

## 2. Benchmark Manifests & Split Provenance

All evaluation records and data splits are preserved in the research repository and external storage:

| Split Identifier | Image Count | Distribution | File Path / Storage Location | Overlap with Benchmark |
| :--- | :---: | :--- | :--- | :---: |
| **`benchmark_test_v2.csv`** | **856** | 625 Defective / 231 Nominal | `release/final_18h_validation/evaluation_predictions.csv` | **100% (Audited Primary Benchmark)** |
| **`train_split.csv`** | 3,262 | 100% Nominal | `G:/My Drive/DefectVisionAI/dataset/splits/` | **0.0% Overlap** |
| **`val_split.csv`** | 367 | 100% Nominal | `G:/My Drive/DefectVisionAI/dataset/splits/` | **0.0% Overlap** |
| **`supervised_train_v3.csv`** | 3,499 | Nominal + Defect Mix | `G:/My Drive/DefectVisionAI/dataset/splits/` | **0.0% Overlap** |
| **`supervised_val_v3.csv`** | 632 | Nominal + Defect Mix | `G:/My Drive/DefectVisionAI/dataset/splits/` | **0.0% Overlap** |
| **`supervised_train_v1.csv`** | 3,737 | Historical Prototype | `G:/My Drive/DefectVisionAI/dataset/splits/` | **788 Overlapping Images (Disclosed)** |

---

## 3. Quarantined External Datasets (Zero Exposure Guarantee)

To guarantee that future independent generalization benchmarks remain uncorrupted and scientifically valid, the following datasets are quarantined:

1. **VisA (Visual Anomaly Dataset) — 11 Reserved Categories:**
   - Categories: `capsules`, `cashew`, `chewinggum`, `fryum`, `macaroni1`, `macaroni2`, `pcb2`, `pcb3`, `pcb4`, `pipefryum`.
   - Access Status: **NEVER ACCESSED FOR TRAINING, TUNING, OR EVALUATION.**
2. **BTAD (BeanTech Anomaly Detection):**
   - 3 industrial product categories (`01`, `02`, `03`).
   - Access Status: **STRICTLY QUARANTINED.**
3. **Chukyo Surface Defect Dataset:**
   - Real-world metal stamping surface defects.
   - Access Status: **STRICTLY QUARANTINED.**

---

## 4. Model Artifacts & Calibration Parameter Archive

| Model Component | Architecture | Checkpoint / File Path | Storage Size | Origin & Licensing |
| :--- | :--- | :--- | :---: | :--- |
| **PatchCore Feature Extractor** | ResNet-18 (Layers 2+3) | PyTorch Torchvision Weights | ~45 MB | Apache 2.0 / BSD |
| **15 PatchCore Memory Banks** | 10% Greedy Coreset Embeddings | `DefectVisionAI/models/patchcore/<cat>/` | 2.41 GB | Derived from MVTec AD Nominal Splits |
| **EfficientNet-B0 Classifier** | Transfer Learning (15 Classes) | `DefectVisionAI/models/efficientnet_v3/best_model.pt` | 19.3 MB | Apache 2.0 / Fine-Tuned Local Weights |
| **FAISS L2 Similarity Galleries** | FAISS IndexFlatL2 | `DefectVisionAI/models/faiss_indices/` | 14.2 MB | Internal Embedding Index |
| **Category Calibration Baselines** | Category Thresholds ($\mu_0, \tau_c$) | `DefectVisionAI/reports/step9_severity_baselines.csv` | 4.8 KB | Computed from Nominal Validation Splits |

---

## 5. Negative Research Findings & Ablation Experiment Catalog

All negative research records are permanently preserved to document empirical failure modes:

1. **CPND (Confidence-Penalized Neighborhood Density) Post-Mortem:**
   - Hypothesis: Neighbor dispersion penalty suppresses edge noise in patch distance maps.
   - Finding: 0% statistically significant gain in AUROC/F1 over boundary distance; exacerbated false negatives on subtle scratches.
   - Archive Log: `DefectVisionAI/reports/cpnd_ablation_results.csv` (Phase 7C).
2. **MACBA (Margin-Calibrated Active Budget Allocation) Equivalence Post-Mortem:**
   - Hypothesis: Active learning decision agent dynamically optimizes human review queues.
   - Finding: Mathematically and empirically equivalent to standard cost-weighted ranking (BL6) under aligned probability calibration.
   - Archive Log: `DefectVisionAI/reports/macba_equivalence_matrix.csv` (Phase 8C).

---

## 6. Project Closure Deliverables Catalog

All final closeout documentation is archived in `release/project_closure/`:
- `FINAL_TECHNICAL_REPORT.md` (Engineering architecture, audited metrics, stress testing)
- `VERIFIED_RESULTS_SUMMARY.md` (Concise confusion matrices and category breakdown)
- `RESEARCH_LIMITATIONS.md` (Threats to validity, micro-defect dilution, photometric noise)
- `INDUSTRIAL_SHADOW_PILOT_PROTOCOL.md` (SOP-DVAI-PILOT-001: supervised shadow testing rules)
- `PUBLICATION_READINESS.md` (Strategy for applied journal submission to IEEE TIM)
- `RESUME_AND_INTERVIEW_SUMMARY.md` (Portfolio and technical interview questions)
- `PROJECT_CLOSURE_DECISION.md` (Official executive sign-off and 5 verdicts)

---

## 7. Archival Verification Commands

To verify the integrity of the research archive, run:
```powershell
# 1. Verify Git commit in private research repository
git rev-parse HEAD  # Expected: 2a6fda2...

# 2. Verify all 856 prediction records in primary benchmark
python scripts/audit_evaluation_predictions.py

# 3. Verify numerical determinism across 5 consecutive runs
python scripts/verify_real_inference_deterministic.py

# 4. Verify clean export repository integrity
cd "C:\Users\surya\Downloads\DefectVisionAI-CleanExport"
git log -n 1 --oneline  # Expected: e3c3a78...
git status              # Clean working tree
```
