import pandas as pd
import numpy as np
import glob

print("Testing all logs for 68 FN and 59 FP...")

# Let's inspect step11_uncertainty_log.csv
df11 = pd.read_csv("DefectVisionAI/logs/step11_uncertainty_log.csv")
print("df11 columns:", df11.columns)

# Let's check if different threshold on prob_defective produces 68 FN and 59 FP
y_true = (df11['true_label'].str.lower() == 'defective').astype(int)

probs = df11['prob_defective']
for th in np.linspace(0.01, 0.99, 100):
    y_pred = (probs >= th).astype(int)
    fn = ((y_true == 1) & (y_pred == 0)).sum()
    fp = ((y_true == 0) & (y_pred == 1)).sum()
    if fn == 68 or fp == 59 or (fn + fp == 127):
        print(f"Threshold {th:.4f} on prob_defective: FN={fn}, FP={fp}, Total={fn+fp}")

# Let's check PatchCore, PaDiM, Autoencoder logs
for path in glob.glob("DefectVisionAI/logs/*.csv"):
    try:
        df = pd.read_csv(path)
        if 'anomaly_score' in df.columns and 'true_label' in df.columns:
            scores = df['anomaly_score']
            y_t = (df['true_label'].str.lower() == 'defective').astype(int)
            for th in np.percentile(scores, np.linspace(1, 99, 100)):
                y_p = (scores >= th).astype(int)
                fn = ((y_t == 1) & (y_p == 0)).sum()
                fp = ((y_t == 0) & (y_p == 1)).sum()
                if (fn == 68 and fp == 59) or (fn == 126 and fp == 1):
                    print(f"{path} at th={th:.4f}: FN={fn}, FP={fp}")
    except Exception:
        pass
