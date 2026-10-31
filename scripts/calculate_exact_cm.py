import pandas as pd
import numpy as np

print("=== STEP 11 SENSITIVITY TABLE ===")
df_sens = pd.read_csv("DefectVisionAI/reports/step11_threshold_sensitivity.csv")
print(df_sens.to_string())

print("\n=== STEP 8 MODEL COMPARISON (1725 images) ===")
df_m1725 = pd.read_csv("DefectVisionAI/reports/step8_model_comparison.csv")
print(df_m1725.to_string())

print("\n=== STEP 8 FAIR MODEL COMPARISON (856 images) ===")
df_mfair = pd.read_csv("DefectVisionAI/reports/step8_model_comparison_FAIR.csv")
print(df_mfair.to_string())

print("\n=== CONFUSION MATRIX: step11_uncertainty_log.csv (1725 images) ===")
df_u = pd.read_csv("DefectVisionAI/logs/step11_uncertainty_log.csv")
print("true_label counts:")
print(df_u['true_label'].value_counts())
print("predicted_label counts:")
print(df_u['predicted_label'].value_counts())
ct_u = pd.crosstab(df_u['true_label'], df_u['predicted_label'])
print("Crosstab (true_label vs predicted_label):")
print(ct_u)

# calculate TP, TN, FP, FN assuming defective is positive, normal is negative
# Let's check label names
labels = df_u['true_label'].unique()
print(f"Labels: {labels}")
def calc_cm(df, true_col, pred_col, pos_label='defective', neg_label='good'):
    # normalize labels
    y_true = df[true_col].astype(str).str.lower().map(lambda x: 'defective' if x in ['defective', 'defect', 'anomaly', '1'] else 'normal')
    y_pred = df[pred_col].astype(str).str.lower().map(lambda x: 'defective' if x in ['defective', 'defect', 'anomaly', '1'] else 'normal')
    
    tp = ((y_true == 'defective') & (y_pred == 'defective')).sum()
    tn = ((y_true == 'normal') & (y_pred == 'normal')).sum()
    fp = ((y_true == 'normal') & (y_pred == 'defective')).sum()
    fn = ((y_true == 'defective') & (y_pred == 'normal')).sum()
    err = fp + fn
    acc = (tp + tn) / len(df)
    prec = tp / (tp + fp) if (tp + fp) > 0 else 0
    rec = tp / (tp + fn) if (tp + fn) > 0 else 0
    return {"TP": tp, "TN": tn, "FP": fp, "FN": fn, "Errors": err, "Accuracy": acc, "Precision": prec, "Recall": rec}

print("Metrics for step11_uncertainty_log:")
print(calc_cm(df_u, 'true_label', 'predicted_label'))

print("\n=== CONFUSION MATRIX: step8_efficientnet_on_common_testset.csv (1725 images) ===")
df_c = pd.read_csv("DefectVisionAI/logs/step8_efficientnet_on_common_testset.csv")
print("Metrics for step8_common_testset (predicted_label):")
print(calc_cm(df_c, 'true_label', 'predicted_label'))

print("\n=== CONFUSION MATRIX: step8_efficientnet_v3_on_benchmark.csv (856 images) ===")
df_b = pd.read_csv("DefectVisionAI/logs/step8_efficientnet_v3_on_benchmark.csv")
print("Metrics for step8_benchmark (predicted_label):")
print(calc_cm(df_b, 'true_label', 'predicted_label'))

