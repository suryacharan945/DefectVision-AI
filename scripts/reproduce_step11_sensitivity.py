import os
import pandas as pd
import numpy as np

LOGS_DIR = "DefectVisionAI/logs"
REPORTS_DIR = "DefectVisionAI/reports"

df = pd.read_csv(os.path.join(LOGS_DIR, "step11_uncertainty_log.csv"))
sens_df = pd.read_csv(os.path.join(REPORTS_DIR, "step11_threshold_sensitivity.csv"))

print("Original sensitivity table:")
print(sens_df)

# Check total errors
# What defines an error? true_label != predicted_label
is_error = (df['true_label'] != df['predicted_label'])
total_errors = is_error.sum()
print(f"\nTotal errors in dataset: {total_errors} out of {len(df)} images")

print("\nVerifying each threshold:")
for thresh in sens_df['uncertainty_threshold']:
    flagged = df['uncertainty'] >= thresh
    n_flagged = flagged.sum()
    pct_flagged = (n_flagged / len(df)) * 100
    captured_errors = (flagged & is_error).sum()
    pct_captured = (captured_errors / total_errors) * 100
    print(f"Thresh >= {thresh:.1f} | Flagged: {n_flagged:3d} ({pct_flagged:4.1f}%) | Errors Captured: {captured_errors:2d} ({pct_captured:4.1f}%)")
