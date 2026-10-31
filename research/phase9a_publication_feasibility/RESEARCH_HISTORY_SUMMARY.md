# Phase 9A Deliverable: Research History and Provenance Summary

**Project:** DefectVision AI — Advanced Quality Inspection Platform  
**Phase:** 9A (Research Reset and Publication Feasibility)  
**Status:** COMPLETE & INDEPENDENTLY AUDITED  
**Artifact:** `research/phase9a_publication_feasibility/RESEARCH_HISTORY_SUMMARY.md`  

---

## 1. Executive Summary

This document establishes the comprehensive, unvarnished scientific record of the DefectVision AI research program from inception through the completion of Phase 8C.

The dual mission established at the start of this engagement was:
- **Goal A (Immediate Product Deadline):** Deliver a fully verified, hardened, and demonstrable visual anomaly detection application.
- **Goal B (Long-Term Research):** Establish a scientifically defensible, reproducible foundation for a future submission to a reputable Q1 journal.

**Current Program Status:**
1. **Goal A is FULLY ACHIEVED:** The DefectVision AI platform is fully operational, verified end-to-end, and frozen under versioned release tag `v1.0.0-research-prototype` (Git commit `78ecd20`).
2. **Goal B Algorithmic Hypotheses are CONCLUSIVELY RESOLVED as NEGATIVE / EQUIVALENT:**
   - **Hypothesis 1 (Conformal Patch-Neighborhood Dispersion - CPND):** Disproven in Phase 7B and 7C (`STOP CPND`). Local feature dispersion does not outperform simple decision-boundary distance.
   - **Hypothesis 2 (Multi-Category Adaptive Budget Allocation - MACBA):** Disproven as a novel algorithm in Phase 8C (`STANDARD METHOD EQUIVALENCE`). Greedy knapsack optimization on marginal utility under unit inspection costs is mathematically and empirically identical to Chow's (1970) classic cost-weighted Bayes error-risk ranking.
   - **Statistical Discrepancy Resolved:** The reported Phase 8B advantage of MACBA at symmetric costs ($\lambda = 1$) was proven to be an artifact of an inconsistent probability estimator (`error_clf` on unsigned distance) which inadvertently crippled the BL6 baseline.
3. **Quarantine Preserved:** All reserved evaluation benchmarks (11 unexposed VisA categories, BTAD, and Chukyo) remain completely untouched and unaccessed.

---

## 2. Chronological Trajectory of Research Phases

### 2.1 Phase 0–6: Application Recovery, Hardening, and Release Freeze
- **Initial State:** An Antigravity full-stack repository (FastAPI backend + React frontend) coupled with exploratory Google Colab notebooks.
- **Application Audit & Verification (Phases 1–3):** Resolved dependency mismatches (PyTorch 2.5, TorchVision, FAISS-CPU, Vite proxy). Fixed mock data fallbacks to ensure genuine neural network inference.
- **Hybrid Decision Hardening (Priority 1):** Verified that the hybrid EfficientNet + PatchCore decision rule operated effectively for severe gross defects, but established that PatchCore was the primary driver of fine structural anomaly detection.
- **Release Freeze (Phase 4):** Created release tag `v1.0.0-research-prototype` at Git commit `78ecd20`. Preserved complete model artifact hashes (EfficientNet-B0 SHA-256 `c1fa0b5...`, PatchCore FAISS index, and calibration parameters).

### 2.2 Phase 7A: Exposure Inventory and Independence Audit
- **Protocol Correction:** Audited the actual exposure history across historical Google Drive and Colab runs.
- **Identified Prior Exposure:** Established that 4 VisA categories (`candle`, `capsule`, `macaroni`, `pcb1`) and 3 MVTec categories (`bottle`, `capsule`, `metal_nut`) were exposed during prior model development and threshold fitting.
- **Quarantine Established:** Strictly partitioned the remaining datasets into an untouched quarantine pool:
  - 11 VisA categories (`bones`, `cashew`, `chewinggum`, `fryum`, `pipefryum`, `pushpins`, `screw`, `socket`, `tag`, `wallnut`, `waterbottle`).
  - Entire BTAD dataset (3 industrial categories).
  - Entire Chukyo dataset.
- **Protocol V2:** Adopted `research/protocols/Q1_EXPERIMENT_PROTOCOL_V2.json` (SHA-256 `effd056...`).

### 2.3 Phase 7B & 7C: The CPND Hypothesis and Failure
- **Proposed Method:** Conformal Patch-Neighborhood Dispersion (CPND) attempted to quantify epistemic localization uncertainty by measuring spatial feature dispersion in PatchCore's $k\text{NN}$ memory bank retrieval.
- **Phase 7B Results:** Evaluated on the 330 development images. CPND achieved an error review yield of $30.6\%$, exactly matching raw distance-to-threshold ranking, while incurring non-trivial compute overhead. Decision: `REVISE METHOD`.
- **Phase 7C Revision (Density-Normalized CPND):** Normalized dispersion by local core-set feature density.
- **Phase 7C Empirical Failure:** Review yield dropped sharply from $30.6\%$ down to $22.2\%$. Boundary distance consistently outperformed dispersion metrics across all thresholds.
- **Phase 7C Gate Verdict:** `STOP CPND` (Git commit `8abbc7a`).

### 2.4 Phase 8A & 8B: Risk-Aware Allocation (MACBA Hypothesis)
- **Phase 8A Literature Pivot:** Transitioned from feature-level uncertainty to decision-theoretic review allocation (Direction B: MACBA). Formulated human inspection as a marginal utility knapsack problem under asymmetric misclassification costs ($\lambda = c_{\text{FN}} / c_{\text{FP}} \gg 1$).
- **Phase 8B Feasibility Experiment:** Evaluated on a leakage-free 50/50 calibration ($N=156$) vs. internal evaluation ($N=174$) split.
  - At industrial cost ratio $\lambda = 20$, MACBA achieved $46.27\%$ cost reduction, outperforming uniform allocation (BL0, $12.49\%$) and pooled distance (BL2, $15.75\%$).
  - At symmetric cost ratio $\lambda = 1$, MACBA reported $23.71\%$ cost reduction versus $18.00\%$ for Baseline BL6 (Simple Cost-Weighted Risk).
  - Decision: Conditionally approved as a research hypothesis (commit `87d9775`).

### 2.5 Phase 8C: Mathematical Equivalence and Novelty Gate
- **Mission:** Investigate whether MACBA is mathematically distinct from conventional cost-sensitive Bayes risk ranking (BL6) and explain the $\lambda = 1$ discrepancy.
- **Mathematical Proof:** Proved that under additive loss and unit review capacity ($w_i = c_{\text{rev}} = 1$), greedy knapsack on marginal utility $\Delta L(X)$ is **isomorphic** to sorting by cost-weighted error risk $\text{Score}_{\text{BL6}}(X) = P(\text{Error} \mid X, \hat{Y}) \cdot W(\hat{Y})$.
- **Root Cause of Symmetric Cost Gap:** In Phase 8B, BL6 was evaluated using `error_clf` fitted on unsigned scalar distance $|S(X) - \tau|$, which collapsed BL6 into raw distance ranking (BL2) at $\lambda = 1$. In contrast, MACBA used signed `defect_clf`.
- **Empirical Re-evaluation:** When BL6 uses the correct signed error probability:
  - Spearman rank correlation is **$\rho_s = 1.000000$**.
  - Selection overlap is **$100.0\%$** across all 11 budgets and all 5 cost ratios.
  - Paired cost difference is **$\$0.0000$**.
- **Constraint Assessment:** Proved that extending MACBA with manufacturing constraints (heterogeneous inspection times, coverage floors, inspector assignments, batch setups) reduces to standard Operations Research problems with zero AI/ML algorithmic novelty.
- **Phase 8C Gate Verdict:** **`STANDARD METHOD EQUIVALENCE`** (Git commit `cae06dd`).

---

## 3. Methodological and Experimental Status Summary

| Research Hypothesis | Proposed Mechanism | Empirical / Theoretical Verdict | Final Status |
|:---|:---|:---|:---:|
| **CPND (Phase 7B/7C)** | Spatial feature dispersion in memory bank $k\text{NN}$ | Review yield dropped to $22.2\%$; inferior to raw boundary distance. | **DISPROVEN & TERMINATED** |
| **MACBA (Phase 8A/8B/8C)** | Greedy knapsack allocation over marginal loss reduction | Analytically & empirically identical to Chow (1970) Bayes risk ranking ($\rho_s = 1.0$). | **STANDARD EQUIVALENCE — TERMINATED** |
| **Symmetric Cost Gap ($\lambda=1$)** | Purported algorithmic advantage of knapsack allocation | Artifact of unsigned `error_clf` implementation defect in baseline. | **RESOLVED & DISMISSED** |
| **Industrial Constraints (Phase 8C)** | Knapsack extensions for factory operations | Reduces to classic 1950s–1990s OR problems (0-1 KP, MKP, GAP, FCKP). | **ZERO ALGORITHMIC NOVELTY** |

---

## 4. Integrity and Preservation Guarantees

1. **No Retrospective Narrative Sanitization:** All negative results, implementation artifacts, failed ablations, and audit documents remain permanently committed to the repository history.
2. **Strict Dataset Independence:** The 330 development images represent an exposed exploratory set. They cannot and will not be used to claim independent statistical generalization.
3. **Quarantined Evaluation Pool Intact:** The 11 VisA categories, BTAD test images, and Chukyo dataset remain completely untouched, ensuring that DefectVision AI retains a pristine benchmark for any future evaluation.
4. **Stable Operational Asset:** The DefectVision AI software application is a fully working, robust product asset ready for real-world demonstration.
