import pandas as pd
import numpy as np

# Load test predictions
df = pd.read_csv('DefectVisionAI/logs/step8_efficientnet_on_common_testset.csv')
p = df['anomaly_score'].values
y = (df['true_label'] == 'defective').values.astype(int)
y_hat = (p >= 0.5).astype(int)

# Total metrics
N = len(y) # 1725
is_fn = (y == 1) & (y_hat == 0)
is_fp = (y == 0) & (y_hat == 1)
is_err = (y != y_hat)

FN0 = is_fn.sum() # 124
FP0 = is_fp.sum() # 3
E0 = is_err.sum() # 127

# Uncertainty: supervised margin
u = 1.0 - np.abs(2.0 * p - 1.0)

print(f"Total Images N={N}, Positives={y.sum()}, Negatives={(~y.astype(bool)).sum()}")
print(f"Baseline Errors: Total={E0}, FN (Escapes)={FN0}, FP (False Alarms)={FP0}")
print()

# 1. FIXED BUDGET EVALUATION
print("--- FIXED BUDGET EVALUATION (Rank by u descending) ---")
budgets = [0.01, 0.05, 0.10, 0.20]
order = np.argsort(-u)

for b in budgets:
    k = int(np.round(b * N))
    idx = order[:k]
    fn_cap = is_fn[idx].sum()
    fp_cap = is_fp[idx].sum()
    err_cap = is_err[idx].sum()
    ecr = err_cap / E0 * 100
    derr = fn_cap / FN0 * 100
    fparr = fp_cap / FP0 * 100
    yield_rate = fn_cap / k * 100
    print(f"Budget {b*100:4.1f}% (K={k:4d}) | Errors Cap: {err_cap:3d}/{E0} ({ecr:5.2f}%) | Escapes Cap: {fn_cap:3d}/{FN0} ({derr:5.2f}%) | FP Cap: {fp_cap:2d}/{FP0} ({fparr:5.2f}%) | Review Yield: {yield_rate:5.2f}%")

print()
# 2. THRESHOLD-BASED EVALUATION (u >= thresh)
print("--- SCORE-THRESHOLD EVALUATION (Filter by u >= threshold) ---")
thresholds = [0.05, 0.10, 0.15, 0.20, 0.30]
for th in thresholds:
    mask = u >= th
    k = mask.sum()
    pct_b = k / N * 100
    fn_cap = is_fn[mask].sum()
    fp_cap = is_fp[mask].sum()
    err_cap = is_err[mask].sum()
    ecr = err_cap / E0 * 100
    derr = fn_cap / FN0 * 100
    fparr = fp_cap / FP0 * 100
    yield_rate = fn_cap / k * 100 if k > 0 else 0
    print(f"Thresh u>={th:.2f} (K={k:4d}, {pct_b:5.2f}%) | Errors Cap: {err_cap:3d}/{E0} ({ecr:5.2f}%) | Escapes Cap: {fn_cap:3d}/{FN0} ({derr:5.2f}%) | FP Cap: {fp_cap:2d}/{FP0} ({fparr:5.2f}%) | Review Yield: {yield_rate:5.2f}%")
