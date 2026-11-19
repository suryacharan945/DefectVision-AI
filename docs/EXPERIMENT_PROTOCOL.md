# DefectVision AI — Experimental Protocol & Evaluation Guidelines

## 1. Principles of Leakage-Free Evaluation

To prevent optimistic metric inflation and preserve scientific integrity, all experiments conducted with DefectVision AI must adhere to the following rules:

1. **Strict Partitioning:** No specimen used for memory bank construction or threshold calibration may ever appear in the test set.
2. **Deterministic Seeds:** Greedy coreset subsampling, initialization vectors, and data splits must record seed `42`.
3. **Macro vs. Micro Separation:** Both Macro metrics (unweighted mean of 15 category scores) and Micro metrics (aggregate specimen counts) must be explicitly reported and mathematically labeled.
4. **Independent Gating Evaluation:** Classification accuracy must distinguish between:
   - Closed-Set Accuracy (forcing 1 of 15 categories).
   - Auto-Gated Accuracy (allowing `LOW_CONFIDENCE`, `UNSUPPORTED_CATEGORY`, or `POOR_IMAGE_QUALITY` rejections).

---

## 2. Standard Benchmark Reproduction Protocol

To reproduce the canonical $N=1,725$ MVTec AD evaluation:

```bash
# Activate virtual environment
source .venv/bin/activate

# Execute frozen benchmark evaluation suite
python scripts/run_external_evaluation_suite.py --dataset mvtec --output release/final_validation/
```

Expected Metrics Verification:
- Closed-Set Classifier Accuracy: $\ge 99.9\%$
- Image AUROC: $97.15\% \pm 0.05\%$
- Image AUPRC: $98.98\% \pm 0.05\%$
- Micro Defect Recall: $94.04\%$
- Micro Precision: $91.07\%$
