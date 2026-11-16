import os
import pandas as pd
import numpy as np
from sklearn.metrics import roc_auc_score, accuracy_score, precision_score, recall_score, f1_score

LOGS_DIR = "DefectVisionAI/logs"
REPORTS_DIR = "DefectVisionAI/reports"

print("--- Checking step8_model_comparison_FAIR.csv ---")
fair_df = pd.read_csv(os.path.join(REPORTS_DIR, "step8_model_comparison_FAIR.csv"))
print(fair_df)

print("\n--- Checking stored predictions in logs ---")
# step8_efficientnet_v3_on_benchmark.csv
b_effnet = pd.read_csv(os.path.join(LOGS_DIR, "step8_efficientnet_v3_on_benchmark.csv"))
print("EfficientNet v3 benchmark rows:", len(b_effnet))
print(b_effnet.head(2))

# Check columns
print("Columns:", b_effnet.columns.tolist())

# Check patchcore, padim, ae logs
pc_log = pd.read_csv(os.path.join(LOGS_DIR, "step7_patchcore_inference_log.csv"))
print("PatchCore log rows:", len(pc_log))

padim_log = pd.read_csv(os.path.join(LOGS_DIR, "step6_padim_inference_log.csv"))
print("PaDiM log rows:", len(padim_log))

ae_log = pd.read_csv(os.path.join(LOGS_DIR, "step5_ae_inference_log.csv"))
print("Autoencoder log rows:", len(ae_log))
