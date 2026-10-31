import os
import pandas as pd

LOGS_DIR = "DefectVisionAI/logs"
REPORTS_DIR = "DefectVisionAI/reports"

print("--- step11_threshold_sensitivity.csv ---")
sens_df = pd.read_csv(os.path.join(REPORTS_DIR, "step11_threshold_sensitivity.csv"))
print(sens_df)

print("\n--- step11_uncertainty_log.csv ---")
unc_df = pd.read_csv(os.path.join(LOGS_DIR, "step11_uncertainty_log.csv"))
print(f"Total rows: {len(unc_df)}")
print("Columns:", unc_df.columns.tolist())
print(unc_df.head(5))
print(unc_df.tail(5))
