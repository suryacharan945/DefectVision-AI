import pandas as pd
import numpy as np

# Load step11 uncertainty log
df11 = pd.read_csv('DefectVisionAI/logs/step11_uncertainty_log.csv')
y_true = (df11['true_label'] == 'defective').values.astype(int)
y_pred = (df11['predicted_label'] == 'defective').values.astype(int)
u = df11['uncertainty'].values

N = len(df11) # 1725
is_fn = (y_true == 1) & (y_pred == 0)
is_fp = (y_true == 0) & (y_pred == 1)
is_err = (y_true != y_pred)

FN0 = int(is_fn.sum())
FP0 = int(is_fp.sum())
E0 = int(is_err.sum())

print(f"Total Dataset N = {N}")
print(f"True Defectives = {y_true.sum()}, True Normals = {(~y_true.astype(bool)).sum()}")
print(f"Baseline Errors: Total={E0}, FN (Escapes)={FN0}, FP (False Alarms)={FP0}")
print("=" * 110)

# 1. FIXED BUDGET EVALUATION (Rank by uncertainty descending)
print("1. FIXED BUDGET EVALUATION (Strict Capacity Constraint B in {1%, 5%, 10%, 20%}):")
print(f"{'Budget':<10} | {'Reviewed (K)':<14} | {'Errors Cap':<14} | {'ECR (%)':<10} | {'Escapes Cap':<14} | {'DERR (%)':<10} | {'FP Cap':<8} | {'Yield (%)':<10}")
print("-" * 110)

order = np.argsort(-u)
budgets = [0.01, 0.05, 0.10, 0.20]
fixed_rows = []

for b in budgets:
    k = int(np.round(b * N))
    idx = order[:k]
    fn_cap = int(is_fn[idx].sum())
    fp_cap = int(is_fp[idx].sum())
    err_cap = int(is_err[idx].sum())
    ecr = err_cap / E0 * 100
    derr = fn_cap / FN0 * 100
    yield_rate = fn_cap / k * 100
    print(f"{b*100:>5.1f}%     | {k:>5d} ({k/N*100:4.1f}%)   | {err_cap:>3d}/{E0}        | {ecr:>6.2f}%    | {fn_cap:>3d}/{FN0}        | {derr:>6.2f}%    | {fp_cap:>2d}/{FP0}   | {yield_rate:>6.2f}%")
    fixed_rows.append({
        'Budget_Pct': b * 100, 'K': k, 'Reviewed_Pct': k / N * 100,
        'Errors_Cap': err_cap, 'E0': E0, 'ECR_Pct': ecr,
        'Escapes_Cap': fn_cap, 'FN0': FN0, 'DERR_Pct': derr,
        'FP_Cap': fp_cap, 'FP0': FP0, 'Yield_Pct': yield_rate
    })

print()
print("=" * 110)

# 2. SCORE-THRESHOLD SELECTION (Filter by uncertainty >= threshold)
print("2. SCORE-THRESHOLD SELECTION (Operational Filter u >= tau):")
print(f"{'Threshold':<10} | {'Reviewed (K)':<14} | {'Errors Cap':<14} | {'ECR (%)':<10} | {'Escapes Cap':<14} | {'DERR (%)':<10} | {'FP Cap':<8} | {'Yield (%)':<10}")
print("-" * 110)

thresholds = [0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80]
thresh_rows = []

for th in thresholds:
    mask = u >= th
    k = int(mask.sum())
    fn_cap = int(is_fn[mask].sum())
    fp_cap = int(is_fp[mask].sum())
    err_cap = int(is_err[mask].sum())
    ecr = err_cap / E0 * 100
    derr = fn_cap / FN0 * 100
    yield_rate = fn_cap / k * 100 if k > 0 else 0.0
    print(f"u >= {th:.2f}   | {k:>5d} ({k/N*100:4.1f}%)   | {err_cap:>3d}/{E0}        | {ecr:>6.2f}%    | {fn_cap:>3d}/{FN0}        | {derr:>6.2f}%    | {fp_cap:>2d}/{FP0}   | {yield_rate:>6.2f}%")
    thresh_rows.append({
        'Threshold': th, 'K': k, 'Reviewed_Pct': k / N * 100,
        'Errors_Cap': err_cap, 'E0': E0, 'ECR_Pct': ecr,
        'Escapes_Cap': fn_cap, 'FN0': FN0, 'DERR_Pct': derr,
        'FP_Cap': fp_cap, 'FP0': FP0, 'Yield_Pct': yield_rate
    })
