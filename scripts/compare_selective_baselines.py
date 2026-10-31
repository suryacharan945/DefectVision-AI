import os
import pandas as pd
import numpy as np

LOGS_DIR = "DefectVisionAI/logs"
df = pd.read_csv(os.path.join(LOGS_DIR, "step11_uncertainty_log.csv"))

# Let's verify what data is here
N = len(df)
is_error = (df['true_label'] != df['predicted_label'])
total_errors = is_error.sum()
is_defect = (df['true_label'] == 'defective')
is_false_negative = is_defect & (df['predicted_label'] == 'normal') # defect escapes!
total_escapes = is_false_negative.sum()

print(f"Total dataset size: {N}")
print(f"Total classification errors: {total_errors} ({total_errors/N*100:.2f}%)")
print(f"Total escaping defects (False Negatives): {total_escapes}")

# Selection strategies:
# 1. Random Selection (seeded)
# 2. Highest Anomaly Score Review (raw_patchcore_score)
# 3. Smallest Distance-to-Threshold Review (abs(prob_defective - 0.5) or distance to threshold)
# 4. Uncertainty Score Review (df['uncertainty'])

budgets = [0.01, 0.05, 0.10, 0.20]

print("\n" + "="*80)
print(f"{'Budget':<8} | {'Strategy':<32} | {'Flagged':<8} | {'Errors Captured':<18} | {'Defect Escapes Captured':<24}")
print("="*80)

for b in budgets:
    k = int(np.round(b * N))
    
    # 1. Random (average over 100 seeds)
    rand_errors = []
    rand_escapes = []
    for s in range(100):
        np.random.seed(s)
        idx = np.random.choice(N, k, replace=False)
        rand_errors.append(is_error.iloc[idx].sum())
        rand_escapes.append(is_false_negative.iloc[idx].sum())
    mean_rand_err = np.mean(rand_errors)
    mean_rand_esc = np.mean(rand_escapes)
    print(f"{b*100:>5.1f}%  | {'1. Random Selection':<32} | {k:<8} | {mean_rand_err:4.1f} ({mean_rand_err/total_errors*100:5.1f}%)    | {mean_rand_esc:4.1f} ({mean_rand_esc/total_escapes*100:5.1f}%)")
    
    # 2. Highest Anomaly Score
    top_score_idx = df['raw_patchcore_score'].nlargest(k).index
    top_score_err = is_error.iloc[top_score_idx].sum()
    top_score_esc = is_false_negative.iloc[top_score_idx].sum()
    print(f"{b*100:>5.1f}%  | {'2. Highest Anomaly Score':<32} | {k:<8} | {top_score_err:4d} ({top_score_err/total_errors*100:5.1f}%)    | {top_score_esc:4d} ({top_score_esc/total_escapes*100:5.1f}%)")
    
    # 3. Smallest Distance to Decision Boundary (0.5)
    dist_to_05 = np.abs(df['prob_defective'] - 0.5)
    margin_idx = dist_to_05.nsmallest(k).index
    margin_err = is_error.iloc[margin_idx].sum()
    margin_esc = is_false_negative.iloc[margin_idx].sum()
    print(f"{b*100:>5.1f}%  | {'3. Margin (Smallest Dist to 0.5)':<32} | {k:<8} | {margin_err:4d} ({margin_err/total_errors*100:5.1f}%)    | {margin_esc:4d} ({margin_esc/total_escapes*100:5.1f}%)")
    
    # 4. Uncertainty Score from log (which is 1 - 2*|p-0.5|)
    unc_idx = df['uncertainty'].nlargest(k).index
    unc_err = is_error.iloc[unc_idx].sum()
    unc_esc = is_false_negative.iloc[unc_idx].sum()
    print(f"{b*100:>5.1f}%  | {'4. Supervised Prediction Margin':<32} | {k:<8} | {unc_err:4d} ({unc_err/total_errors*100:5.1f}%)    | {unc_esc:4d} ({unc_esc/total_escapes*100:5.1f}%)")
    print("-" * 80)
