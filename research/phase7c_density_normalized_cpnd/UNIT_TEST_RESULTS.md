# Phase 7C: Unit & Integration Test Results

**Document ID:** `DV-PHASE7C-TESTS-V1`  
**Date:** October 31, 2026  
**Status:** **100% PASSED (8/8 Tests Passed)**  
**Test Suite File:** `tests/test_density_norm_cpnd.py`  
**Execution Runtime:** 0.144 seconds  
**Test Runner:** `python -m unittest tests/test_density_norm_cpnd.py -v`

---

## 1. Test Execution Summary

```
test_boundary_gated_tier_sorting ....................................... ok
test_deterministic_tie_breaking ........................................ ok
test_image_scoring_and_argmax .......................................... ok
test_normalization_types ............................................... ok
test_numerical_determinism ............................................. ok
test_self_neighbor_exclusion ........................................... ok
test_yield_metrics_disambiguation ...................................... ok
test_zero_distance_stability ........................................... ok

----------------------------------------------------------------------
Ran 8 tests in 0.144s

OK
```

---

## 2. Detailed Test Specifications

| Test Case Name | Objective & Verification Standard | Result |
| :--- | :--- | :---: |
| `test_self_neighbor_exclusion` | Verifies that querying the nominal training coreset for reference statistics queries $k_{\text{ref}} + 1$ neighbors and excludes column 0 (self-distance 0.0), guaranteeing that reference dispersions reflect inter-patch manifold density without self-contamination. | **PASS** |
| `test_normalization_types` | Validates both robust median/MAD (`median_mad`) and parametric mean/std (`mean_std`) normalizations, confirming valid numerical output and zero NaN/inf values. | **PASS** |
| `test_zero_distance_stability` | Queries identical duplicate vectors (query = memory bank vector). Asserts that $\mu_K \to 0$ does not produce division by zero or NaN under the $\epsilon = 10^{-7}$ stabilizer. | **PASS** |
| `test_numerical_determinism` | Instantiates two independent scorers and processes synthetic patches across multiple runs. Asserts bitwise identical float arrays (`np.testing.assert_array_equal`). | **PASS** |
| `test_image_scoring_and_argmax` | Introduces an extreme synthetic outlier patch into a 20-patch set. Verifies that `score_image` correctly identifies patch 7 as the argmax and extracts its exact 1-NN score, raw dispersion, and normalized dispersion. | **PASS** |
| `test_boundary_gated_tier_sorting` | Constructs a four-specimen synthetic batch with varying boundary band membership (`in_band \in {0, 1}`) and dispersion values. Asserts that `rank_and_select_budget` strictly prioritizes Tier 1 items before Tier 0 items, and sorts within Tier 1 by normalized dispersion descending. | **PASS** |
| `test_deterministic_tie_breaking` | Tests that identical uncertainty scores break ties deterministically in alphabetical order of secondary key `image_id` (`img_A` before `img_M` before `img_Z`). | **PASS** |
| `test_yield_metrics_disambiguation` | Verifies the separation of `defect_review_yield` (defects found / reviewed) and `error_review_yield` (errors found / reviewed) on a controlled 4-image confusion scenario (TP, FN, TN, FP). | **PASS** |

---

## 3. Regression Test Verification

Phase 7B core tests were simultaneously re-verified to ensure zero regressions across legacy modules:
- **Command:** `python -m unittest tests/test_cpnd.py -v`
- **Result:** **12 passed, 0 failed** in 0.146s.
- **Total Combined Test Suite:** **20 passed, 0 failed**.
