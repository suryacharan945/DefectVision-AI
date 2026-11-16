import os
import sys
import json
import numpy as np
import pandas as pd
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    accuracy_score,
    balanced_accuracy_score,
    precision_score,
    recall_score,
    f1_score
)

def audit_predictions():
    csv_path = "release/final_18h_validation/evaluation_predictions.csv"
    if not os.path.exists(csv_path):
        print(f"ERROR: {csv_path} does not exist!")
        return

    df = pd.read_csv(csv_path)
    print("=== TASK 1: RECOMPUTE METRICS & RECORD VERIFICATION ===")
    print(f"Total rows read: {len(df)}")
    
    # 1. Distinct records & duplicate check
    distinct_filepaths = df["filepath"].nunique()
    print(f"Distinct filepaths: {distinct_filepaths} / {len(df)}")
    duplicates = df[df.duplicated(subset=["filepath"], keep=False)]
    print(f"Duplicate rows count: {len(duplicates)}")
    if len(duplicates) > 0:
        print("Duplicate examples:\n", duplicates.head(4))

    # 2. Ground-truth distribution
    normal_count = (df["is_normal"] == True).sum()
    defect_count = (df["is_normal"] == False).sum()
    gt_0_count = (df["ground_truth"] == 0).sum()
    gt_1_count = (df["ground_truth"] == 1).sum()
    print(f"\nGround Truth Counts:")
    print(f"  is_normal == True:  {normal_count} (Expected: 231)")
    print(f"  is_normal == False: {defect_count} (Expected: 625)")
    print(f"  ground_truth == 0:  {gt_0_count} (Expected: 231)")
    print(f"  ground_truth == 1:  {gt_1_count} (Expected: 625)")
    
    # Consistency check between is_normal and ground_truth
    inconsistent_gt = df[((df["is_normal"] == True) & (df["ground_truth"] != 0)) |
                         ((df["is_normal"] == False) & (df["ground_truth"] != 1))]
    print(f"Inconsistent GT rows: {len(inconsistent_gt)}")

    # Defect type check
    defect_types = df["defect_type"].value_counts()
    print(f"\nUnique defect types: {len(defect_types)}")
    print(f"Good/normal defect type count: {defect_types.get('good', 0)}")

    # 3. Category distribution
    cat_counts = df["category"].value_counts()
    print(f"\nPer-Category specimen counts:\n{cat_counts.to_dict()}")

    # 4. Recomputing confusion matrices and metrics
    y_true = df["ground_truth"].to_numpy()
    
    # A. PatchCore
    pc_preds = df["patchcore_pred"].to_numpy()
    pc_scores = df["patchcore_raw_score"].to_numpy()
    cm_pc = confusion_matrix(y_true, pc_preds, labels=[0, 1])
    tn_pc, fp_pc, fn_pc, tp_pc = cm_pc.ravel()

    # B. EfficientNet
    eff_preds = df["effnet_pred"].to_numpy()
    eff_scores = df["effnet_prob"].to_numpy()
    cm_eff = confusion_matrix(y_true, eff_preds, labels=[0, 1])
    tn_eff, fp_eff, fn_eff, tp_eff = cm_eff.ravel()

    # C. Hybrid
    hyb_preds = df["hybrid_pred"].to_numpy()
    # Note on continuous hybrid score:
    # In earlier script: np.maximum(anomaly_norm / 100.0, eff_scores)
    hyb_scores = np.maximum(df["anomaly_norm"].to_numpy() / 100.0, eff_scores)
    cm_hyb = confusion_matrix(y_true, hyb_preds, labels=[0, 1])
    tn_hyb, fp_hyb, fn_hyb, tp_hyb = cm_hyb.ravel()

    def calc_metrics(y_t, y_p, y_s):
        tn, fp, fn, tp = confusion_matrix(y_t, y_p, labels=[0, 1]).ravel()
        acc = accuracy_score(y_t, y_p)
        b_acc = balanced_accuracy_score(y_t, y_p)
        prec = precision_score(y_t, y_p, zero_division=0)
        rec = recall_score(y_t, y_p, zero_division=0)
        spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0
        f1 = f1_score(y_t, y_p, zero_division=0)
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0
        auroc = roc_auc_score(y_t, y_s)
        auprc = average_precision_score(y_t, y_s)
        return {
            "TN": int(tn), "FP": int(fp), "FN": int(fn), "TP": int(tp),
            "Accuracy": acc, "Balanced_Accuracy": b_acc,
            "Precision": prec, "Recall": rec, "Specificity": spec,
            "F1": f1, "FPR": fpr, "FNR": fnr,
            "AUROC": auroc, "AUPRC": auprc
        }

    m_pc = calc_metrics(y_true, pc_preds, pc_scores)
    m_eff = calc_metrics(y_true, eff_preds, eff_scores)
    m_hyb = calc_metrics(y_true, hyb_preds, hyb_scores)

    recomputed = pd.DataFrame([
        {"System": "PatchCore", **m_pc},
        {"System": "EfficientNet", **m_eff},
        {"System": "Hybrid", **m_hyb}
    ])
    print("\n--- RECOMPUTED METRICS ---")
    print(recomputed.to_string())

    # 5. Compare with reported evaluation_metrics.csv
    rep_csv = "release/final_18h_validation/evaluation_metrics.csv"
    if os.path.exists(rep_csv):
        rep_df = pd.read_csv(rep_csv)
        print("\n--- REPORTED METRICS IN evaluation_metrics.csv ---")
        print(rep_df.to_string())
    
    # 6. Check continuous scores validity
    print("\nScore distributions:")
    print(f"  PatchCore scores: min={pc_scores.min():.4f}, max={pc_scores.max():.4f}, NaN={np.isnan(pc_scores).sum()}")
    print(f"  EfficientNet prob: min={eff_scores.min():.4f}, max={eff_scores.max():.4f}, NaN={np.isnan(eff_scores).sum()}")
    print(f"  Hybrid score: min={hyb_scores.min():.4f}, max={hyb_scores.max():.4f}, NaN={np.isnan(hyb_scores).sum()}")

    # AUROC of PatchCore with normalized score instead of raw score:
    auroc_pc_norm = roc_auc_score(y_true, df["anomaly_norm"])
    print(f"  AUROC PatchCore (raw vs norm): {m_pc['AUROC']:.4f} vs {auroc_pc_norm:.4f}")

if __name__ == "__main__":
    audit_predictions()
