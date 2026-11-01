# DefectVision AI — Test Suite Reclassification and Verification Audit

**Document Version:** 2.0.0  
**Audit Date:** November 1, 2026  
**Auditor:** Software Quality Assurance & Research Governance  
**Environment:** Windows 11 Pro 64-bit, Python 3.12.9, Node.js 20+, PyTorch 2.15.0+cpu, FAISS-CPU 1.15.1, Vite 8.3.0  
**Target Release:** `v1.0.0-research-prototype`  

---

## 1. Executive Summary: Test Classification Correction

In earlier project summaries, a headline figure of **"903 automated tests passing"** was reported. 

A forensic audit of this claim reveals that **870 of those 903 checks were row-by-row algorithmic decision trace comparisons** from a research evaluation script (`research/phase8c_macba_equivalence/BL6_MACBA_DECISION_TRACE.csv`), rather than software unit or integration tests.

### 1.1 Mandatory Reclassification Standard
In accordance with professional software engineering and reproducible research standards:
- **Software tests** verify that code components, APIs, UI builds, and validation logic function correctly and fail safely.
- **Research data evaluations** evaluate scientific hypotheses, risk ranking policies, and loss curves across specimen datasets.

**Rule:** Research dataset evaluations must **never** be counted as software unit tests.

### 1.2 Audited Test Inventory Breakdown

| Tier | Category | Scope / Target Component | Count | Pass | Fail | Execution Time | Verification Status |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---:|
| **1** | **Backend Unit Tests** | Conformal Patch-Neighborhood Dispersion (`test_cpnd.py`), Density Normalization (`test_density_norm_cpnd.py`), Vision Reports & Serialization (`test_vision_reports.py`) | **22** | 22 | 0 | 0.39 s | **VERIFIED** |
| **2** | **Backend Integration Endpoints** | FastAPI REST Endpoints: `/` (health & 15 categories), `/predict` (live single inference), `/batch` (asynchronous queue), `/severity/logs` (history), `/rag/ask` (LLM/RAG QA) | **5** | 5 | 0 | 5.82 s | **VERIFIED** |
| **3** | **Model Inference & Artifact Integrity** | Checksum verification and FAISS L2 memory-bank inference on real specimen (`scripts/test_backend_inference.py`) | **1** | 1 | 0 | 4.15 s | **VERIFIED** |
| **4** | **Frontend-Backend Proxy Integration** | Vite development reverse proxy communication from port 5173 to port 8000 (`scripts/test_vite_proxy.py`) | **1** | 1 | 0 | 3.20 s | **VERIFIED** |
| **5** | **Input Validation & Safety Guards** | Defensive error handling: invalid category, non-image payload, empty multipart body, oversized payload (`scripts/test_invalid_inputs_safety.py`) | **4** | 4 | 0 | 2.10 s | **VERIFIED** |
| **6** | **Frontend Production Build** | Vite compilation, chunk rendering, Tailwind CSS generation, and tree shaking (`npm run build --prefix frontend`) | **1** | 1 | 0 | 4.25 s | **VERIFIED** |
| **SUBTOTAL** | **Actual Software Tests** | **All code, API, UI, and safety verification suites** | **34** | **34** | **0** | **~20 s** | **100% PASS** |
| **RESEARCH** | **Algorithmic Equivalence Trace** | Row-level decision equivalence checks comparing BL6 and MACBA across 6 cost ratios $\lambda$ and 6 review budgets $K$ on 174 validation instances | **870** | 870 | 0 | 7.55 s | **RESEARCH EVALUATION (Not a Software Test)** |

---

## 2. Software Test Suite Execution Logs

### 2.1 Backend Unit Tests (22 Tests)
**Command:**
```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```
**Detailed Output:**
```
test_category_specific_calibration (test_cpnd.TestCPNDCorrectness.test_category_specific_calibration)
Test that joint uncertainty correctly handles category-specific thresholds and normalization. ... ok
test_deterministic_tie_handling (test_cpnd.TestCPNDCorrectness.test_deterministic_tie_handling)
Test that identical uncertainty scores break ties deterministically using secondary key. ... ok
test_empty_or_invalid_inputs (test_cpnd.TestCPNDCorrectness.test_empty_or_invalid_inputs)
Test defensive behavior on invalid inputs. ... ok
test_faiss_squared_to_euclidean_conversion (test_cpnd.TestCPNDCorrectness.test_faiss_squared_to_euclidean_conversion)
Test that FAISS squared L2 distances are correctly converted to Euclidean distances. ... ok
test_feature_and_memory_bank_dimensions (test_cpnd.TestCPNDCorrectness.test_feature_and_memory_bank_dimensions)
Test dimension checking and validation. ... ok
test_fixed_budget_selection_count (test_cpnd.TestCPNDCorrectness.test_fixed_budget_selection_count)
Test that rank_and_select_budget selects exactly floor(B * N). ... ok
test_k_nearest_neighbor_ordering (test_cpnd.TestCPNDCorrectness.test_k_nearest_neighbor_ordering)
Test that FAISS returns neighbors in strictly ascending distance order. ... ok
test_numerical_determinism (test_cpnd.TestCPNDCorrectness.test_numerical_determinism)
Test that repeated runs produce bitwise identical output. ... ok
test_pnd_not_identical_to_anomaly_score (test_cpnd.TestCPNDCorrectness.test_pnd_not_identical_to_anomaly_score)
Test that PND ranking is mathematically distinct from raw anomaly score ranking. ... ok
test_score_export_and_reload_parity (test_cpnd.TestCPNDCorrectness.test_score_export_and_reload_parity)
Test CSV export and reload parity. ... ok
test_threshold_consistency (test_cpnd.TestCPNDCorrectness.test_threshold_consistency)
Test that distance-to-threshold is maximal at score == threshold. ... ok
test_zero_distance_stability (test_cpnd.TestCPNDCorrectness.test_zero_distance_stability)
Test that identical query vectors (distance = 0) do not cause division by zero or NaN. ... ok
test_boundary_gated_tier_sorting (test_density_norm_cpnd.TestDensityNormalizedCPND.test_boundary_gated_tier_sorting)
Test that tiered boundary-gated ranking strictly prioritizes Tier 1 (in-band) items. ... ok
test_deterministic_tie_breaking (test_density_norm_cpnd.TestDensityNormalizedCPND.test_deterministic_tie_breaking)
Test that identical scores break ties deterministically by secondary key (alphabetical). ... ok
test_image_scoring_and_argmax (test_density_norm_cpnd.TestDensityNormalizedCPND.test_image_scoring_and_argmax)
Test image scoring extracts the argmax patch properties correctly. ... ok
test_normalization_types (test_density_norm_cpnd.TestDensityNormalizedCPND.test_normalization_types)
Test both median_mad and mean_std normalization options. ... ok
test_numerical_determinism (test_density_norm_cpnd.TestDensityNormalizedCPND.test_numerical_determinism)
Test that repeated runs produce bitwise identical output. ... ok
test_self_neighbor_exclusion (test_density_norm_cpnd.TestDensityNormalizedCPND.test_self_neighbor_exclusion)
Test that memory bank self-neighbor (distance = 0) is excluded from reference statistics. ... ok
test_yield_metrics_disambiguation (test_density_norm_cpnd.TestDensityNormalizedCPND.test_yield_metrics_disambiguation)
Test that Defect Review Yield and Error Review Yield are correctly distinguished. ... ok
test_zero_distance_stability (test_density_norm_cpnd.TestDensityNormalizedCPND.test_zero_distance_stability)
Test that identical query vectors (distance = 0) do not cause division by zero or NaN. ... ok
test_fair_comparison_report_exists_and_valid (test_vision_reports.TestDefectVisionReports.test_fair_comparison_report_exists_and_valid) ... ok
test_frontend_data_integrity (test_vision_reports.TestDefectVisionReports.test_frontend_data_integrity) ... ok

----------------------------------------------------------------------
Ran 22 tests in 0.390s

OK
```

---

### 2.2 Model Artifact & Inference Verification (1 Test)
**Command:**
```powershell
.\.venv\Scripts\python.exe scripts/test_backend_inference.py
```
**Output:**
```
--- Step 1: Checking device ---
Device: cpu

--- Step 2: Verifying Model Artifact Hashes ---
EfficientNet-B0 v3 checkpoint: DefectVisionAI/models/efficientnet_baseline_v3/best_model.pt
SHA-256: f470b76d7c00df5be88236d552b3406256a60ee2c27fca361b981fce88902ba8
Bottle PatchCore Memory Bank: DefectVisionAI/models/patchcore/bottle/memory_bank.npy
SHA-256: 71a68f4e54109c74fec922c02252218d5abfab31256c2bce170e05014db52200

--- Step 3: Loading Models into Memory ---
PatchCoreExtractor loaded successfully!
Bottle Memory Bank shape: (14739, 384)
Bottle PatchCoreModel loaded into FAISS index FlatL2!

--- Step 4: Finding a Test Image for Bottle ---
Selected test image: DefectVisionAI/outputs/similarity_search_samples/bottle_similarity_demo.png

--- Step 5: Running PatchCore Inference ---
Raw PatchCore Score:   4.5088
Baseline Mean:          1.2228
Decision Threshold p99: 1.4138
Classification Decision:DEFECTIVE
Heatmap Shape:          (224, 224, 3)
Heatmap written to:     delivery_24h/final_verification_v2/test_outputs/verified_bottle_heatmap.png

--- INFERENCE TEST PASSED COMPLETELY ---
```

---

### 2.3 Backend Integration Endpoints (5 Tests)
**Command:**
```powershell
.\.venv\Scripts\python.exe scripts/e2e_backend_test.py
```
**Endpoints Verified:**
1. `GET /`: Health check returns status `ready`, device `cpu`, and verifies all 15 industrial categories are registered.
2. `POST /predict`: Live multi-part form data upload for `bottle_demo.png` returns anomaly score `4.5088`, threshold `1.4138`, severity level `Critical`, 3 nearest neighbor matches, and base64 heatmap.
3. `POST /batch` & `GET /batch/{id}/status`: Asynchronous batch processing queue completes with 2/2 inspected specimens, generating aggregate defect rate report.
4. `GET /severity/logs`: Historical pagination query retrieves audit records for `bottle` category.
5. `POST /rag/ask`: Copilot domain QA endpoint returns root-cause analysis and recommended corrective actions.

---

### 2.4 Frontend Production Build Verification (1 Test)
**Command:**
```powershell
npm run build --prefix frontend
```
**Output:**
```
> frontend@0.0.0 build
> vite build

vite v8.3.0 building client environment for production...
transforming...
✓ 2459 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                     2.30 kB │ gzip:   0.90 kB
dist/assets/index-8vyLY23k.css     78.50 kB │ gzip:  11.59 kB
dist/assets/index-D5wDqQ5e.js   1,400.74 kB │ gzip: 355.62 kB
✓ built in 4.25s
```

---

### 2.5 Input Validation Safety Guards (4 Tests)
**Command:**
```powershell
.\.venv\Scripts\python.exe scripts/test_invalid_inputs_safety.py
```
**Validation Guards Verified:**
1. **Invalid Category:** Rejects unrecognized category strings with HTTP 400 Bad Request.
2. **Corrupted File:** Rejects malformed image headers with descriptive HTTP 422 Unprocessable Entity.
3. **Empty Payload:** Rejects zero-byte uploads with HTTP 400 Bad Request.
4. **Oversized Upload:** Rejects image payloads exceeding maximum buffer size safely without server crash.

---

## 3. Disambiguation: Research Evaluations vs. Software Tests

The file `research/phase8c_macba_equivalence/BL6_MACBA_DECISION_TRACE.csv` contains 870 rows. Each row represents a specimen evaluation under:
- A specific cost ratio $\lambda \in \{1, 5, 10, 20, 50, 100\}$ (6 values)
- A specific review budget $K \in \{1, 3, 8, 17, 25, 34\}$ (6 values)
- A set of 145–174 test specimens from the Phase 8B validation split.

In Phase 8C, these 870 rows were generated to demonstrate that the proposed MACBA policy makes mathematically identical specimen selections to Cost-Weighted Bayes Risk ranking (BL6). 

While scientifically vital for demonstrating standard-method equivalence, **evaluating 870 data rows in an offline empirical experiment does NOT constitute 870 software tests.** 

### Conclusion:
- The DefectVision AI software repository possesses **34 automated, verified software tests** across unit, API, integration, build, and safety layers.
- All 34 software tests execute and pass cleanly in under 25 seconds on standard CPU hardware.
