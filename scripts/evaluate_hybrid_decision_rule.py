import os
import pandas as pd
import numpy as np

# Load logs
df_eff_all = pd.read_csv('DefectVisionAI/logs/step8_efficientnet_on_common_testset.csv')
df_eff_856 = pd.read_csv('DefectVisionAI/logs/step8_efficientnet_v3_on_benchmark.csv')
df_pc_all = pd.read_csv('DefectVisionAI/logs/step7_patchcore_inference_log.csv')
baselines = pd.read_csv('DefectVisionAI/reports/step9_severity_baselines.csv').set_index('category')['baseline_p99'].to_dict()

# Merge on filepath
merged_all = pd.merge(df_eff_all, df_pc_all[['filepath', 'anomaly_score']], on='filepath', suffixes=('_eff', '_pc'))
merged_all['benchmark_856'] = merged_all['filepath'].isin(df_eff_856['filepath'])
merged_all['pc_thresh'] = merged_all['category'].map(baselines)

# Ground truth
merged_all['y_true'] = merged_all['true_label'] == 'defective'

# Model decisions
# For EfficientNet: predicted_label == 'defective' (or anomaly_score_eff >= 0.5)
merged_all['eff_pred'] = (merged_all['predicted_label'] == 'defective') | (merged_all['anomaly_score_eff'] >= 0.5)
# For PatchCore: anomaly_score_pc > pc_thresh
merged_all['pc_pred'] = merged_all['anomaly_score_pc'] > merged_all['pc_thresh']
# Hybrid rules
merged_all['or_pred'] = merged_all['eff_pred'] | merged_all['pc_pred']
merged_all['and_pred'] = merged_all['eff_pred'] & merged_all['pc_pred']

def compute_metrics(y_true, y_pred):
    tp = int((y_true & y_pred).sum())
    fp = int((~y_true & y_pred).sum())
    fn = int((y_true & ~y_pred).sum())
    tn = int((~y_true & ~y_pred).sum())
    total = len(y_true)
    
    rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    spec = tn / (fp + tn) if (fp + tn) > 0 else 0.0
    prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    bal_acc = (rec + spec) / 2.0
    acc = (tp + tn) / total
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
    return {
        'TP': tp, 'FP': fp, 'FN': fn, 'TN': tn,
        'Recall': rec, 'FPR': fpr, 'Precision': prec,
        'Specificity': spec, 'Balanced_Acc': bal_acc, 'Accuracy': acc, 'F1': f1
    }

splits = [
    ('Dev Split (869 imgs)', merged_all[~merged_all['benchmark_856']]),
    ('Benchmark Partition (856 imgs)', merged_all[merged_all['benchmark_856']]),
    ('Full Dataset (1725 imgs)', merged_all)
]

for split_name, df_sub in splits:
    n_pos = int(df_sub['y_true'].sum())
    n_neg = int((~df_sub['y_true']).sum())
    print(f"=== {split_name} ===")
    print(f"Total: {len(df_sub)}, Positives (Defective): {n_pos}, Negatives (Normal): {n_neg}")
    rules = [
        ('1. EfficientNet Alone', 'eff_pred'),
        ('2. PatchCore Alone', 'pc_pred'),
        ('3. Hybrid OR (Safety Mode)', 'or_pred'),
        ('4. Hybrid AND (Diagnostic Baseline)', 'and_pred')
    ]
    for rule_name, col in rules:
        m = compute_metrics(df_sub['y_true'], df_sub[col])
        print(f"{rule_name:36s} | Rec: {m['Recall']:.4f} | FPR: {m['FPR']:.4f} | Prec: {m['Precision']:.4f} | Spec: {m['Specificity']:.4f} | BalAcc: {m['Balanced_Acc']:.4f} | F1: {m['F1']:.4f} | CM: [TN={m['TN']}, FP={m['FP']}, FN={m['FN']}, TP={m['TP']}]")
    print()
