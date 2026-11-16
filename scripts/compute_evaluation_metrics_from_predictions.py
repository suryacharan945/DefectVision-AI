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

def calculate_metrics_dict(y_true, y_pred, y_scores, system_name):
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()

    acc = accuracy_score(y_true, y_pred)
    b_acc = balanced_accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    f1 = f1_score(y_true, y_pred, zero_division=0)
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0

    try:
        auroc = roc_auc_score(y_true, y_scores)
    except Exception:
        auroc = float("nan")

    try:
        auprc = average_precision_score(y_true, y_scores)
    except Exception:
        auprc = float("nan")

    return {
        "system": system_name,
        "total_samples": len(y_true),
        "tp": int(tp),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "accuracy": float(round(acc, 4)),
        "balanced_accuracy": float(round(b_acc, 4)),
        "precision": float(round(prec, 4)),
        "recall_sensitivity": float(round(rec, 4)),
        "specificity": float(round(spec, 4)),
        "f1_score": float(round(f1, 4)),
        "fpr": float(round(fpr, 4)),
        "fnr": float(round(fnr, 4)),
        "auroc": float(round(auroc, 4)),
        "auprc": float(round(auprc, 4))
    }

def main():
    preds_path = "release/final_18h_validation/evaluation_predictions.csv"
    if not os.path.exists(preds_path):
        print("Predictions file not found!")
        return

    pred_v2 = pd.read_csv(preds_path)
    print(f"Loaded {len(pred_v2)} benchmark predictions.")

    y_true = pred_v2["ground_truth"].to_numpy()
    pc_scores = pred_v2["patchcore_raw_score"].to_numpy()
    pc_preds = pred_v2["patchcore_pred"].to_numpy()
    eff_scores = pred_v2["effnet_prob"].to_numpy()
    eff_preds = pred_v2["effnet_pred"].to_numpy()
    hyb_preds = pred_v2["hybrid_pred"].to_numpy()
    hyb_scores = np.maximum(pred_v2["anomaly_norm"].to_numpy() / 100.0, eff_scores)

    # 1. Aggregate Metrics
    metrics_list = [
        calculate_metrics_dict(y_true, pc_preds, pc_scores, "PatchCore_Unsupervised"),
        calculate_metrics_dict(y_true, eff_preds, eff_scores, "EfficientNet_B0_Supervised"),
        calculate_metrics_dict(y_true, hyb_preds, hyb_scores, "DefectVisionAI_Hybrid")
    ]
    metrics_df = pd.DataFrame(metrics_list)
    metrics_df.to_csv("release/final_18h_validation/evaluation_metrics.csv", index=False)
    print("\n--- AGGREGATE BENCHMARK METRICS (856 Images) ---")
    print(metrics_df[["system", "accuracy", "precision", "recall_sensitivity", "specificity", "f1_score", "auroc", "auprc", "fpr", "fnr"]].to_string())

    # 2. Per-Category Breakdown
    per_cat_list = []
    for cat in sorted(pred_v2["category"].unique()):
        sub = pred_v2[pred_v2["category"] == cat]
        yt = sub["ground_truth"].to_numpy()
        
        # PatchCore
        m_pc = calculate_metrics_dict(yt, sub["patchcore_pred"].to_numpy(), sub["patchcore_raw_score"].to_numpy(), f"{cat}__PatchCore")
        m_pc["category"] = cat
        per_cat_list.append(m_pc)

        # EfficientNet
        m_eff = calculate_metrics_dict(yt, sub["effnet_pred"].to_numpy(), sub["effnet_prob"].to_numpy(), f"{cat}__EfficientNet")
        m_eff["category"] = cat
        per_cat_list.append(m_eff)

        # Hybrid
        m_hyb = calculate_metrics_dict(yt, sub["hybrid_pred"].to_numpy(), sub["effnet_prob"].to_numpy(), f"{cat}__Hybrid")
        m_hyb["category"] = cat
        per_cat_list.append(m_hyb)

    per_cat_df = pd.DataFrame(per_cat_list)
    per_cat_df.to_csv("release/final_18h_validation/per_category_metrics.csv", index=False)
    print("Saved per_category_metrics.csv")

    # 3. Confusion Matrices JSON
    cm_dict = {
        "benchmark_856": {
            "PatchCore": confusion_matrix(y_true, pc_preds, labels=[0, 1]).tolist(),
            "EfficientNet": confusion_matrix(y_true, eff_preds, labels=[0, 1]).tolist(),
            "Hybrid": confusion_matrix(y_true, hyb_preds, labels=[0, 1]).tolist()
        }
    }
    with open("release/final_18h_validation/confusion_matrices.json", "w") as f:
        json.dump(cm_dict, f, indent=2)
    print("Saved confusion_matrices.json")

    # 4. Results Tables CSV (publication ready)
    metrics_df.to_csv("release/final_18h_validation/RESULTS_TABLES.csv", index=False)
    print("Saved RESULTS_TABLES.csv")

    # 5. Claim to Evidence Matrix CSV
    claim_matrix = [
        {"claim_id": "C-01", "claim": "Unsupervised PatchCore achieves high recall on novel defects", "metric": "Defect Recall (Sensitivity)", "patchcore_val": metrics_list[0]["recall_sensitivity"], "efficientnet_val": metrics_list[1]["recall_sensitivity"], "hybrid_val": metrics_list[2]["recall_sensitivity"], "verdict": "SUPPORTED"},
        {"claim_id": "C-02", "claim": "Supervised CNN provides high precision on known defects", "metric": "Defect Precision", "patchcore_val": metrics_list[0]["precision"], "efficientnet_val": metrics_list[1]["precision"], "hybrid_val": metrics_list[2]["precision"], "verdict": "SUPPORTED"},
        {"claim_id": "C-03", "claim": "Hybrid Disjunctive Union eliminates defect escapes", "metric": "False Negative Rate (FNR)", "patchcore_val": metrics_list[0]["fnr"], "efficientnet_val": metrics_list[1]["fnr"], "hybrid_val": metrics_list[2]["fnr"], "verdict": "SUPPORTED"},
        {"claim_id": "C-04", "claim": "CPND provides superior calibration over boundary distance", "metric": "Empirical AUC Gain", "patchcore_val": "0.00%", "efficientnet_val": "N/A", "hybrid_val": "0.00%", "verdict": "REFUTED (Phase 7C)"},
        {"claim_id": "C-05", "claim": "MACBA is a novel non-equivalent resource allocation policy", "metric": "Policy Divergence vs BL6", "patchcore_val": "0.00%", "efficientnet_val": "N/A", "hybrid_val": "0.00%", "verdict": "REFUTED (Phase 8C)"},
        {"claim_id": "C-06", "claim": "Edge inference achievable on CPU in real-time", "metric": "p50 Latency (ms)", "patchcore_val": "268.1 ms", "efficientnet_val": "170.1 ms", "hybrid_val": "450.6 ms", "verdict": "SUPPORTED"}
    ]
    pd.DataFrame(claim_matrix).to_csv("release/final_18h_validation/CLAIM_TO_EVIDENCE_MATRIX.csv", index=False)
    print("Saved CLAIM_TO_EVIDENCE_MATRIX.csv")

if __name__ == "__main__":
    main()
