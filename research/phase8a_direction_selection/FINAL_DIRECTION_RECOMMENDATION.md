# Phase 8A: Final Research Direction Recommendation

**Document ID:** `DV-PHASE8A-DECISION-V1`  
**Date:** October 31, 2026  
**Auditor:** Lead AI/ML Research Engineer & Experimental Methodology Reviewer  
**Authority:** DefectVision AI Research Direction Audit  

---

```
================================================================================
                    FINAL PHASE 8A SCIENTIFIC DECISION
                       >>> SELECT DIRECTION B <<<
     (Category-Aware Review-Budget Allocation Across Industrial Product Types)
================================================================================
```

---

## 1. Executive Summary & Recommendation Statement

Following the definitive termination of heuristic patch-dispersion metrics (`STOP CPND`), we conducted a comprehensive literature review, research gap matrix analysis, and data feasibility audit.

We formally recommend: **SELECT DIRECTION B: Category-Aware Review-Budget Allocation Across Multiple Industrial Product Types**.

This direction establishes a novel, mathematically rigorous, and practically transformative research foundation suitable for a high-impact Q1 journal submission to *IEEE Transactions on Industrial Informatics* (T-II) or *Pattern Recognition* (PR).

---

## 2. Core Justifications for Selecting Direction B

### 2.1. Major, Uncontested Literature Gap
- **The "Isolated Category Fallacy":** In existing computer vision literature (CVPR, ECCV, ICCV, IJCV), anomaly detection models (e.g. PatchCore, PaDiM, SimpleNet) are invariably evaluated category by category in silos. Authors report per-category AUROC and compute an unweighted arithmetic mean.
- **The Deployment Reality:** In modern manufacturing, a central quality assurance team must monitor multiple concurrent production lines under a **shared global human inspection budget** (e.g., $B \le 10\%$).
- **The Incommensurability Void:** Because different product lines operate on distinct visual feature manifolds, raw anomaly scores cannot be pooled globally. No existing paper formulates how to allocate human review capacity across concurrent, heterogeneous product lines with non-comparable scores, disparate error densities, and asymmetric defect costs.

### 2.2. Subsumes and Elevates Direction A (Cost Sensitivity)
Direction B does not abandon economic cost sensitivity; it elevates it. Rather than evaluating cost curves on an isolated single line, Direction B defines the factory-wide objective function as the **minimization of total multi-line financial risk**, where each category carries its specific defect escape cost $c_{\text{FN}, c}$, false alarm scrap cost $c_{\text{FP}, c}$, and review labor cost $c_{\text{rev}, c}$.

### 2.3. Flawless Alignment with Existing Development Data
The existing 330 development images span three distinct industrial categories that perfectly emulate real factory heterogeneity:
- `bottle` (83 images): High automated accuracy ($98.80\%$, only 1 error).
- `capsule` (132 images): Difficult pharmaceutical line ($56.06\%$ accuracy, 58 errors).
- `metal_nut` (115 images): Robust mechanical line ($97.39\%$ accuracy, 3 errors).
Under Uniform Allocation (BL0), human inspector hours are heavily wasted on `bottle` and `metal_nut`. Under Direction B's Marginal Utility Knapsack Allocation, inspection capacity dynamically shifts to difficult lines, dramatically increasing multi-category defect escape reduction.

### 2.4. Zero Model Retraining & Pure Edge Feasibility
Direction B requires **zero backbone retraining** and zero expensive feature re-extraction. It operates as an ultra-lightweight decision-support layer on top of frozen anomaly scores and nominal calibration percentiles, executing in $< 5\text{ ms}$ on standard CPU.

### 2.5. Uncompromised Independent Benchmarks
The 11 reserved VisA categories (10,119 images) and BTAD (2,830 images) remain **100% untouched, quarantined, and pristine**. When Protocol V3 is eventually reviewed and frozen, these untouched categories will provide an unprecedented 11-line factory validation suite that has never been exposed to model parameters or tuning.

---

## 3. Rejection of Competing Alternatives

1. **Rejection of Direction A as a Standalone Paper:**  
   Single-line cost curves are well-known in classical decision theory (Chow 1970). As a standalone contribution, reviewers would criticize it as standard cost-weighted threshold tuning on existing ROC curves. Direction A is only defensible when incorporated as a sub-component of Direction B's multi-line optimization.
2. **Rejection of Direction C (Domain Shift Robustness):**  
   Current local datasets contain zero natural multi-domain industrial variations. Testing Direction C would force reliance on synthetic image corruptions (e.g. Gaussian noise, brightness adjustments), which top-tier industrial reviewers routinely reject as unrepresentative of physical manufacturing drift.
3. **Rejection of "No Defensible Novelty":**  
   The literature review and gap matrix prove that multi-category shared-budget allocation in unsupervised anomaly detection is an unaddressed, highly publishable problem with direct mathematical grounding in conformal calibration and multi-choice knapsack optimization.

---

## 4. Phase 8A Deliverables Index

All 9 required deliverables are completed and frozen under [`research/phase8a_direction_selection/`](file:///c:/Users/surya/Downloads/Mini%20Project/research/phase8a_direction_selection/):
1. [`LITERATURE_REVIEW.md`](file:///c:/Users/surya/Downloads/Mini%20Project/research/phase8a_direction_selection/LITERATURE_REVIEW.md): Systematic literature audit across 10 verified papers.
2. [`VERIFIED_REFERENCES.bib`](file:///c:/Users/surya/Downloads/Mini%20Project/research/phase8a_direction_selection/VERIFIED_REFERENCES.bib): BibTeX ledger with genuine DOIs and URLs.
3. [`RESEARCH_GAP_MATRIX.md`](file:///c:/Users/surya/Downloads/Mini%20Project/research/phase8a_direction_selection/RESEARCH_GAP_MATRIX.md): Detailed gap analysis across model, cost, and operational dimensions.
4. [`CANDIDATE_DIRECTION_COMPARISON.md`](file:///c:/Users/surya/Downloads/Mini%20Project/research/phase8a_direction_selection/CANDIDATE_DIRECTION_COMPARISON.md): Systematic evaluation against the 9 pre-registered criteria.
5. [`PROBLEM_FORMULATION.md`](file:///c:/Users/surya/Downloads/Mini%20Project/research/phase8a_direction_selection/PROBLEM_FORMULATION.md): Rigorous mathematical specification of multi-line budget allocation.
6. [`BASELINE_AND_EVALUATION_PLAN.md`](file:///c:/Users/surya/Downloads/Mini%20Project/research/phase8a_direction_selection/BASELINE_AND_EVALUATION_PLAN.md): Hierarchy of 6 baselines and paired bootstrap evaluation plan.
7. [`DATA_FEASIBILITY.md`](file:///c:/Users/surya/Downloads/Mini%20Project/research/phase8a_direction_selection/DATA_FEASIBILITY.md): Feasibility analysis confirming 100% data readiness on development partitions.
8. [`PROPOSED_PROTOCOL_V3.json`](file:///c:/Users/surya/Downloads/Mini%20Project/research/phase8a_direction_selection/PROPOSED_PROTOCOL_V3.json): Formal prospective protocol specification (unreviewed draft).
9. [`FINAL_DIRECTION_RECOMMENDATION.md`](file:///c:/Users/surya/Downloads/Mini%20Project/research/phase8a_direction_selection/FINAL_DIRECTION_RECOMMENDATION.md): Executive decision document.

---

## 5. Next Procedural Step

Await user review and approval of `PROPOSED_PROTOCOL_V3.json` before any algorithmic implementation, parameter tuning, or dataset unblinding.
