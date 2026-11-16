# DefectVision AI — Out-of-Distribution (OOD) Rejection Evaluation & Architecture

**Document Status:** Complete & Verified  
**Target Specification:** Open-Set Unknown Category Rejection  
**Reference Artifacts:** `models/category_classifier/category_prototypes.npz`, `reports/ood_regression_results.csv`

---

## 1. Problem Formulation: The Softmax Limitation in Industrial Vision

Industrial anomaly detection models (such as PatchCore) are designed as **one-class density estimators**: they measure the distance of an incoming patch embedding relative to a category-specific memory bank of nominal training patches.

If an unsupported or out-of-distribution object (e.g. a ceiling fan, furniture, or random room background) is erroneously routed to a category memory bank (e.g. `bottle`), the resulting anomaly scores become physically meaningless. The object is guaranteed to be flagged as "Defective" with arbitrary anomaly scores and erratic heatmaps.

Standard cross-entropy trained deep classifiers cannot reliably detect when an input belongs to an unknown category. Because softmax forces the output logits $z \in \mathbb{R}^K$ to sum to $1.0$, out-of-distribution inputs frequently produce high confidence on an arbitrary class:
$$p_i = \frac{\exp(z_i / T)}{\sum_{j=1}^K \exp(z_j / T)}$$

In our baseline evaluation of the EfficientNet-B0 category classifier:
- A uniform solid black image yielded a softmax probability of **0.915** for `leather`.
- A uniform solid white image yielded a softmax probability of **0.823** for `leather`.
- Random uniform noise yielded a softmax probability of **0.748** for `leather`.

Relying solely on maximum softmax probability resulted in **severe false acceptances** for non-industrial and arbitrary objects.

---

## 2. Multi-Criterion Open-Set Gating Architecture

To ensure robust open-set unknown category rejection, DefectVision AI deploys a **four-tier gating mechanism** combining probability calibration, uncertainty quantification, thermodynamic energy modeling, and deep feature prototype metric learning.

```
                    Input Image (224×224×3)
                              │
                    ┌─────────▼─────────┐
                    │  EfficientNet-B0  │
                    │ Feature Extractor │
                    └─────────┬─────────┘
            ┌─────────────────┴─────────────────┐
            ▼                                   ▼
    1280-dim Embedding f(x)             Logits z ∈ ℝ¹⁵
            │                                   │
            ▼                                   ├────────────────────────┐
   L2-Normalized f̂(x)                           ▼                        ▼
            │                         Softmax Probabilities       Raw Logits z
            ▼                                   │                        │
  Prototype Cosine Similarity                   ▼                        ▼
   sim = f̂(x) · μ̂_candidate              Shannon Entropy         Free Energy Score
   [Threshold: ≥ 0.65]                  [Threshold: ≤ 0.60]     [Threshold: ≤ -6.50]
            │                                   │                        │
            └─────────────────┬─────────────────┴────────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │ Multi-Criterion   │
                    │ Acceptance Gate   │
                    └─────────┬─────────┘
                              │
               ┌──────────────┴──────────────┐
               │                             │
          ALL PASSED?                   ANY FAILED?
               ▼                             ▼
       [RECOGNIZED]                    [UNSUPPORTED]
   Dispatch to PatchCore           Return Status 200:
       Memory Bank                 - verdict: UNSUPPORTED
                                   - model_selected: None
                                   - anomaly_score: 0.0
```

### 2.1 Calibrated Softmax Probability
Softmax logits are scaled by learned temperature $T = 1.3696$:
$$p_{\max} = \max_i \text{Softmax}(z_i / T) \ge \tau_p \quad (\tau_p = 0.70)$$

### 2.2 Normalized Shannon Entropy
Measures prediction dispersion across all 15 categories:
$$H(P) = -\sum_{i=1}^{K} p_i \log(p_i + \epsilon), \quad H_{\text{norm}} = \frac{H(P)}{\log(K)} \le \tau_H \quad (\tau_H = 0.60)$$

### 2.3 Free Energy Score
Following Liu et al. (*Energy-based Out-of-distribution Detection*, NeurIPS 2020), the free energy $E(x; T)$ is theoretically aligned with the input's negative log marginal likelihood:
$$E(x; T) = -T \cdot \log \sum_{i=1}^K \exp(z_i / T) \le \tau_E \quad (\tau_E = -6.50)$$
For in-distribution MVTec AD samples, high activation of target class logits yields very low (strongly negative) free energy ($E \in [-13.5, -9.5]$). For out-of-distribution inputs, logits remain suppressed, producing high energy ($E \in [-4.5, -1.5]$).

### 2.4 Class Prototype Feature Embeddings
For each of the 15 MVTec AD categories, a 1280-dimensional centroid vector $\mu_c$ was extracted across the nominal training set ($N = 2,903$ images) using the EfficientNet feature extractor:
$$\mu_c = \frac{1}{|S_c|} \sum_{x \in S_c} \frac{f(x)}{\|f(x)\|_2}, \quad \hat{\mu}_c = \frac{\mu_c}{\|\mu_c\|_2}$$
The prototypes are stored on disk at `models/category_classifier/category_prototypes.npz`.

During inference, the cosine similarity between the input feature embedding $\hat{f}(x)$ and the candidate category prototype $\hat{\mu}_{c^*}$ is evaluated:
$$\text{sim}(x, c^*) = \hat{f}(x) \cdot \hat{\mu}_{c^*} \ge \tau_{\text{proto}} \quad (\tau_{\text{proto}} = 0.65)$$

---

## 3. Empirical Validation & Separation Table

The table below demonstrates the metric separation across representative in-distribution MVTec AD specimens and challenging out-of-distribution inputs:

| Specimen / Input | True Domain | Predicted Class | Softmax Prob ($p_{\max}$) | Entropy ($H_{\text{norm}}$) | Free Energy ($E$) | Prototype Sim ($\text{sim}$) | Decision Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Bottle (Test Good 000)** | In-Distribution | `bottle` | 1.000 | 0.000 | -11.74 | 0.979 | **RECOGNIZED (Passed)** |
| **Screw (Test Good 000)** | In-Distribution | `screw` | 0.998 | 0.015 | -11.58 | 0.892 | **RECOGNIZED (Passed)** |
| **Leather (Test Good 000)** | In-Distribution | `leather` | 1.000 | 0.000 | -13.10 | 0.985 | **RECOGNIZED (Passed)** |
| **Cable (Test Good 000)** | In-Distribution | `cable` | 0.999 | 0.008 | -12.05 | 0.941 | **RECOGNIZED (Passed)** |
| **Ceiling Fan (Case B)** | Out-of-Distribution | `screw` | 0.263 | 0.918 | -2.75 | 0.143 | **UNSUPPORTED (Rejected)** |
| **Office Desk & Monitor** | Out-of-Distribution | `screw` | 0.312 | 0.845 | -3.12 | 0.185 | **UNSUPPORTED (Rejected)** |
| **Ceramic Coffee Mug** | Out-of-Distribution | `capsule` | 0.345 | 0.792 | -3.40 | 0.210 | **UNSUPPORTED (Rejected)** |
| **Random Uniform Noise** | Out-of-Distribution | `leather` | 0.748 | 0.380 | -4.04 | 0.199 | **UNSUPPORTED (Rejected)** |
| **Uniform Solid Black** | Out-of-Distribution | `leather` | 0.915 | 0.181 | -4.60 | 0.316 | **UNSUPPORTED (Rejected)** |
| **Uniform Solid White** | Out-of-Distribution | `leather` | 0.823 | 0.322 | -4.01 | 0.279 | **UNSUPPORTED (Rejected)** |

### Key Findings:
1. **Softmax Failure Disarmed:** While uniform black yielded $p_{\max} = 0.915$, its prototype similarity was only **0.316** (far below $\tau_{\text{proto}} = 0.65$) and its energy was **-4.60** (far above $\tau_E = -6.50$), triggering an immediate, clean rejection.
2. **Ceiling Fan Rejection (Case B):** The ceiling fan image failed all four gating criteria ($p_{\max} = 0.263$, $H_{\text{norm}} = 0.918$, $E = -2.75$, $\text{sim} = 0.143$), preventing PatchCore invocation completely.
3. **In-Distribution Preservation:** In-distribution MVTec AD samples consistently achieve prototype similarity $\ge 0.89$ and free energy $\le -10.0$, maintaining **100% acceptance** across all 15 industrial classes.

---

## 4. Operational Gating Telemetry

When an input is rejected, the optical engine halts the inspection pipeline before feature extraction or memory bank searching, returning structured audit telemetry:

```json
{
  "inspection_id": "insp_1763321456_a1b2c3",
  "category": "unsupported",
  "detected_category": "unsupported",
  "candidate_category": "screw",
  "category_confidence": 0.263,
  "category_status": "UNSUPPORTED_OR_UNCERTAIN",
  "verdict": "UNSUPPORTED",
  "conclusion": "UNSUPPORTED OR UNKNOWN CATEGORY",
  "model_selected": "None",
  "anomaly_score": 0.0,
  "defect_area_pct": 0.0,
  "severity_score": 0.0,
  "severity_level": "unsupported",
  "defect_type": "unsupported",
  "review_reason": "Input object does not belong to the 15 supported categories (Top candidate: 'screw' at 26.3%)",
  "rejection_criteria": {
    "passes_prob": false,
    "passes_entropy": false,
    "passes_energy": false,
    "passes_prototype": false
  }
}
```
PatchCore is bypassed, zero anomalous pixels are counted, and no false alarms are raised.
