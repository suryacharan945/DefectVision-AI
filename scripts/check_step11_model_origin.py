import os
import pandas as pd

LOGS_DIR = "DefectVisionAI/logs"
df = pd.read_csv(os.path.join(LOGS_DIR, "step11_uncertainty_log.csv"))

print("Correlation between prob_defective and raw_patchcore_score:")
print(df[['prob_defective', 'raw_patchcore_score', 'anomaly_norm_0_100', 'confidence_pct', 'uncertainty']].corr())

print("\nSample rows where prob_defective is close to 0.5:")
print(df[df['uncertainty'] > 0.5][['category', 'true_label', 'predicted_label', 'raw_patchcore_score', 'prob_defective', 'uncertainty']].head(10))
