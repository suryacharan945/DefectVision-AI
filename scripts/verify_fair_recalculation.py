import os
import pandas as pd
import numpy as np
from sklearn.metrics import roc_auc_score, accuracy_score, precision_score, recall_score, f1_score

LOGS_DIR = "DefectVisionAI/logs"

# Load the 856 benchmark predictions
effnet_bm = pd.read_csv(os.path.join(LOGS_DIR, "step8_efficientnet_v3_on_benchmark.csv"))
print(f"Benchmark images: {len(effnet_bm)}")

# Normalize filepaths (e.g. get relative filename or category + defect_type + filename)
def get_key(fp):
    parts = fp.replace("\\", "/").split("/")
    # e.g. .../bottle/test/broken_large/000.png -> bottle/broken_large/000.png
    return "/".join(parts[-4:])

effnet_bm['key'] = effnet_bm['filepath'].apply(get_key)
benchmark_keys = set(effnet_bm['key'])
print(f"Unique benchmark keys: {len(benchmark_keys)}")

# Let's verify EfficientNet v3 directly
y_true = (effnet_bm['true_label'] == 'defective').astype(int)
y_pred_bin = (effnet_bm['predicted_label'] == 'defective').astype(int)
scores = effnet_bm['anomaly_score']

# Pooled image AUROC vs Macro category AUROC
pooled_auc = roc_auc_score(y_true, scores)
cat_aucs = []
for cat, grp in effnet_bm.groupby('category'):
    yt = (grp['true_label'] == 'defective').astype(int)
    if len(yt.unique()) > 1:
        cat_aucs.append(roc_auc_score(yt, grp['anomaly_score']))
macro_auc = np.mean(cat_aucs)

acc = accuracy_score(y_true, y_pred_bin)
prec = precision_score(y_true, y_pred_bin)
rec = recall_score(y_true, y_pred_bin)
f1 = f1_score(y_true, y_pred_bin)

print("\n--- EfficientNet-B0 v3 Recalculation ---")
print(f"Macro-category AUROC: {macro_auc:.4f} (Reported: 0.9732)")
print(f"Pooled-image AUROC:   {pooled_auc:.4f}")
print(f"Accuracy:             {acc:.4f} (Reported: 0.8692)")
print(f"Precision:            {prec:.4f} (Reported: 0.9981)")
print(f"Recall:               {rec:.4f} (Reported: 0.8224)")
print(f"F1-Score:             {f1:.4f} (Reported: 0.9018)")
