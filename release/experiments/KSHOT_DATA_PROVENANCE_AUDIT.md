# DEFECTVISION AI 2.3 — K-SHOT DATA PROVENANCE AUDIT

**Document Identifier:** `release/experiments/KSHOT_DATA_PROVENANCE_AUDIT.md`  
**Audit Execution Date:** 2026-11-19 01:57:51  
**Status:** FULLY VERIFIED (113 Total Distinct Physical Specimens Audited)  

---

## 1. Executive Provenance Summary

The 83-specimen K-shot sample efficiency experiment executed in Sprint 2.2 and audited in Sprint 2.3 uses **strictly genuine MVTec AD industrial benchmark specimens**.
None of these specimens are synthetic, augmented, or derived from arbitrary web downloads.

### Specimen Breakdown
- **Training Pool:** 20 genuine normal bottle specimens (`train/good/000.png` through `019.png`)
- **Calibration Pool:** 10 genuine normal bottle specimens (`train/good/020.png` through `029.png`)
- **Held-Out Test Set (83 specimens):**
  - Normal Test: 20 specimens (`test/good/000.png` through `019.png`)
  - Large Broken Defects: 20 specimens (`test/broken_large/000.png` through `019.png`)
  - Small Broken Defects: 22 specimens (`test/broken_small/000.png` through `021.png`)
  - Contamination Defects: 21 specimens (`test/contamination/000.png` through `020.png`)

All file hashes have been computed and verified in `release/experiments/kshot_partition_manifest.csv`.

---

## 2. Partition Independence & Leakage Verification

1. **Zero Overlap:** The intersection between `train_pool` (20), `calib_pool` (10), and `test` (83) is exactly $\emptyset$.
2. **No Data Leakage:** The 10 calibration specimens were never exposed to the nearest-neighbor coreset memory banks; they were strictly used to evaluate normal distance distributions and set the operational cutoff.
3. **Scientific Scope Clarification:** This experiment strictly evaluates **in-domain few-shot sample efficiency on the MVTec AD benchmark** (Track A). It does **NOT** represent external-domain adaptation across camera hardware or studio lighting (Track B).
