# CPND Unit & Integration Test Results

**Document ID:** `DV-TEST-CPND-V1`  
**Date:** October 31, 2026  
**Test Suite:** [`tests/test_cpnd.py`](file:///c:/Users/surya/Downloads/Mini%20Project/tests/test_cpnd.py)  
**Status:** **12 OF 12 TESTS PASSED (100% SUCCESS)**  
**Runtime:** 0.136 seconds  

---

## 1. Test Execution Summary

```
----------------------------------------------------------------------
Ran 12 tests in 0.136s

OK
----------------------------------------------------------------------
```

---

## 2. Itemized Test Verification Ledger

| Test Case Name | Objective / Invariant Checked | Verification Criteria | Status |
| :--- | :--- | :--- | :---: |
| `test_faiss_squared_to_euclidean_conversion` | Validates that FAISS squared L2 distance $D_{(j)}$ is converted via $\sqrt{\max(D, 0)}$ to analytical Euclidean distance. | Query at $[1, 0, 0, 0]$ with memory at $[0, 2, 4, 6]$ produces exact $1\text{-NN} = 1.0$, $\mu = 1.6667$, $\sigma = 0.9428$, $\text{PND} = 0.5657$. | **PASS** |
| `test_k_nearest_neighbor_ordering` | Ensures neighbor distances are strictly monotonic non-decreasing ($d_{(1)} \le d_{(2)} \le \dots \le d_{(K)}$). | Checked $\Delta d \ge -10^{-6}$ across 50 random vectors. | **PASS** |
| `test_zero_distance_stability` | Validates that identical vectors ($d=0$, $\mu=0$, $\sigma=0$) do not cause `ZeroDivisionError`, `NaN`, or `Inf`. | Returns finite $\text{PND} = 0.00000$ and $d=0.0$. | **PASS** |
| `test_numerical_determinism` | Verifies bitwise determinism across repeated executions. | Repeated executions yield identical NumPy arrays (`assert_array_equal`). | **PASS** |
| `test_feature_and_memory_bank_dimensions` | Asserts defensive validation against mismatched dimensions ($D \ne 384$) or memory bank size $< K$. | Throws `ValueError` with clear descriptive message. | **PASS** |
| `test_fixed_budget_selection_count` | Confirms that `rank_and_select_budget` selects exactly $K = \lfloor B \cdot N \rfloor$ items across all test budgets $B \in \{1\%, 2\%, 5\%, 10\%, 15\%, 20\%\}$. | $K$ matches expected count across all budgets. | **PASS** |
| `test_deterministic_tie_handling` | Ensures identical uncertainty values break ties deterministically using the secondary key (`image_id`). | Returns lexicographically sorted records. | **PASS** |
| `test_threshold_consistency` | Confirms that boundary distance uncertainty $u_{\text{dist}}$ is strictly maximal at $|S(X) - \tau_c| = 0$ and decreases monotonically. | $u(1.50) > u(1.51) > u(2.50)$ for threshold $\tau = 1.50$. | **PASS** |
| `test_category_specific_calibration` | Validates that joint uncertainty correctly handles category-specific thresholds and rank normalizations. | Normalization bounds $u \in [0, 1]$ across diverse category threshold scales. | **PASS** |
| `test_pnd_not_identical_to_anomaly_score` | Confirms that PND is mathematically distinct from anomaly score ranking and not trivially collinear ($|r| < 0.95$). | Empirical correlation $|r| < 0.95$ confirmed. | **PASS** |
| `test_score_export_and_reload_parity` | Validates that exported CSV records reload without floating-point drift or schema corruption. | 100% roundtrip numerical parity. | **PASS** |
| `test_empty_or_invalid_inputs` | Tests defensive error handling for uninitialized models, $K < 2$, invalid aggregation methods, and budget fractions $> 1.0$. | Raises appropriate exceptions gracefully. | **PASS** |

---

## 3. Engineering Integrity Certification

All 12 unit tests execute deterministically using the Python standard library `unittest` framework without requiring third-party testing harnesses, ensuring zero dependency churn in the project runtime.
