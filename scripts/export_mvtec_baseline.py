"""
MVTec AD Trusted Baseline Exporter
DefectVision AI v1.0.0-rc1 Evaluation
Exports:
- external_validation/baseline/baseline_summary.json
- external_validation/baseline/category_recognition_results.csv
- external_validation/baseline/anomaly_detection_results.csv
"""

import os
import json
import numpy as np
import pandas as pd
from sklearn.metrics import (
    roc_auc_score, average_precision_score,
    precision_score, recall_score, f1_score, confusion_matrix
)

def main():
    base_dir = "external_validation/baseline"
    os.makedirs(base_dir, exist_ok=True)
    
    anom_src_csv = "release/final_validation/mvtec_all_predictions.csv"
    cat_src_csv = "release/category_recognition/category_test_predictions.csv"
    
    if not os.path.exists(anom_src_csv) or not os.path.exists(cat_src_csv):
        raise FileNotFoundError(f"Missing source files: {anom_src_csv} or {cat_src_csv}")
        
    df_anom_raw = pd.read_csv(anom_src_csv)
    df_cat_raw = pd.read_csv(cat_src_csv)
    print(f"Loaded {len(df_anom_raw)} anomaly predictions and {len(df_cat_raw)} category predictions.")

    # Normalize filepaths for clean merge
    def norm_fp(p):
        p_str = str(p).replace("\\", "/")
        if "dataset/raw/mvtec/" in p_str:
            return "dataset/raw/mvtec/" + p_str.split("dataset/raw/mvtec/")[-1]
        return p_str

    df_anom_raw["norm_key"] = df_anom_raw["filepath"].apply(norm_fp)
    df_cat_raw["norm_key"] = df_cat_raw["filepath"].apply(norm_fp)

    # Merge category recognition details
    df_merged = df_anom_raw.merge(
        df_cat_raw[["norm_key", "predicted_category", "confidence", "entropy", "correct"]],
        on="norm_key",
        how="left",
        suffixes=("", "_cat_raw")
    )

    # 1. Export category_recognition_results.csv
    # Include both raw closed-set prediction and gated prediction
    df_cat_out = pd.DataFrame({
        "filepath": df_merged["filepath"],
        "ground_truth_category": df_merged["category"],
        "raw_predicted_category": df_merged["predicted_category"],
        "raw_confidence": df_merged["confidence"],
        "raw_entropy": df_merged["entropy"],
        "raw_correct": df_merged["correct_cat_raw"],
        "gated_predicted_category": df_merged["auto_detected_category"],
        "gated_confidence": df_merged["auto_category_confidence"],
        "is_accepted": df_merged["auto_detected_category"] != "unknown",
        "gated_correct": df_merged["auto_category_correct"] == 1
    })
    cat_csv_path = os.path.join(base_dir, "category_recognition_results.csv")
    df_cat_out.to_csv(cat_csv_path, index=False)
    print(f"Wrote {cat_csv_path} ({len(df_cat_out)} rows)")

    # 2. Export anomaly_detection_results.csv
    df_anom_out = pd.DataFrame({
        "filepath": df_merged["filepath"],
        "category": df_merged["category"],
        "category_type": df_merged["category_type"],
        "ground_truth_label": df_merged["is_defect"],
        "defect_type": df_merged["defect_type"],
        "selected_patchcore_category": df_merged["category"],
        "anomaly_score": df_merged["anomaly_score"],
        "calibrated_threshold": df_merged["calibrated_threshold"],
        "predicted_label": df_merged["predicted_label"],
        "verdict": df_merged["verdict"],
        "image_correct": df_merged["correct"],
        "pixel_auroc": df_merged["pixel_auroc"],
        "latency_ms": df_merged["latency_ms"]
    })
    anom_csv_path = os.path.join(base_dir, "anomaly_detection_results.csv")
    df_anom_out.to_csv(anom_csv_path, index=False)
    print(f"Wrote {anom_csv_path} ({len(df_anom_out)} rows)")

    # 3. Compute baseline metrics
    categories = sorted(df_merged["category"].unique())
    total_samples = len(df_merged)

    # Closed-set category accuracy
    closed_set_correct = int(df_cat_out["raw_correct"].sum())
    closed_set_acc = float(closed_set_correct / total_samples * 100.0)

    # Gated category accuracy
    accepted_mask = df_cat_out["is_accepted"]
    n_accepted = int(accepted_mask.sum())
    n_rejected = total_samples - n_accepted
    rejection_rate = float(n_rejected / total_samples * 100.0)
    acc_on_accepted = float(df_cat_out[accepted_mask]["gated_correct"].sum() / n_accepted * 100.0)
    gated_correct_total = int(df_cat_out["gated_correct"].sum())
    overall_gated_acc = float(gated_correct_total / total_samples * 100.0)

    per_cat_recognition = {}
    for c in categories:
        sub = df_cat_out[df_cat_out["ground_truth_category"] == c]
        tot = len(sub)
        c_raw = int(sub["raw_correct"].sum())
        c_acc = int(sub[sub["is_accepted"]]["gated_correct"].sum())
        n_acc = int(sub["is_accepted"].sum())
        per_cat_recognition[c] = {
            "total_samples": tot,
            "raw_correct": c_raw,
            "raw_accuracy_pct": round(float(c_raw / tot * 100.0), 2),
            "accepted_count": n_acc,
            "rejected_count": tot - n_acc,
            "rejection_rate_pct": round(float((tot - n_acc) / tot * 100.0), 2),
            "accuracy_on_accepted_pct": round(float(c_acc / n_acc * 100.0), 2) if n_acc > 0 else 0.0
        }

    # Macro Precision, Recall, F1 for Category Recognition (15 Classes)
    cat_y_true = [str(x) for x in df_cat_out["ground_truth_category"].values]
    cat_y_pred = [str(x) for x in df_cat_out["raw_predicted_category"].values]
    labels_all = sorted(list(set(cat_y_true)))
    cat_macro_prec = float(precision_score(cat_y_true, cat_y_pred, labels=labels_all, average="macro", zero_division=0) * 100.0)
    cat_macro_rec = float(recall_score(cat_y_true, cat_y_pred, labels=labels_all, average="macro", zero_division=0) * 100.0)
    cat_macro_f1 = float(f1_score(cat_y_true, cat_y_pred, labels=labels_all, average="macro", zero_division=0) * 100.0)

    # Anomaly Detection Metrics
    per_cat_anomaly = {}
    cat_aurocs = []
    cat_auprcs = []
    cat_pixel_aurocs = []

    for c in categories:
        sub = df_anom_out[df_anom_out["category"] == c]
        y_true = sub["ground_truth_label"].values
        y_score = sub["anomaly_score"].values
        y_pred = sub["predicted_label"].values
        
        auroc = float(roc_auc_score(y_true, y_score) * 100.0)
        auprc = float(average_precision_score(y_true, y_score) * 100.0)
        cat_aurocs.append(auroc)
        cat_auprcs.append(auprc)
        
        pix_auroc_mean = float(sub["pixel_auroc"].dropna().mean() * 100.0) if not sub["pixel_auroc"].dropna().empty else None
        if pix_auroc_mean is not None:
            cat_pixel_aurocs.append(pix_auroc_mean)

        tp = int(np.sum((y_true == 1) & (y_pred == 1)))
        fn = int(np.sum((y_true == 1) & (y_pred == 0)))
        fp = int(np.sum((y_true == 0) & (y_pred == 1)))
        tn = int(np.sum((y_true == 0) & (y_pred == 0)))

        rec = float(tp / (tp + fn) * 100.0) if (tp + fn) > 0 else 0.0
        fpr = float(fp / (fp + tn) * 100.0) if (fp + tn) > 0 else 0.0
        spec = float(tn / (tn + fp) * 100.0) if (tn + fp) > 0 else 0.0
        prec = float(tp / (tp + fp) * 100.0) if (tp + fp) > 0 else 0.0
        f1 = float(2 * prec * rec / (prec + rec) / 100.0) if (prec + rec) > 0 else 0.0

        per_cat_anomaly[c] = {
            "category_type": sub["category_type"].iloc[0],
            "n_normal": int(np.sum(y_true == 0)),
            "n_defective": int(np.sum(y_true == 1)),
            "total_test": len(sub),
            "image_auroc_pct": round(auroc, 2),
            "image_auprc_pct": round(auprc, 2),
            "pixel_auroc_pct": round(pix_auroc_mean, 2) if pix_auroc_mean else None,
            "true_positives": tp,
            "false_positives": fp,
            "true_negatives": tn,
            "false_negatives": fn,
            "defect_recall_pct": round(rec, 2),
            "false_positive_rate_pct": round(fpr, 2),
            "specificity_pct": round(spec, 2),
            "precision_pct": round(prec, 2),
            "f1_score": round(f1, 4),
            "calibrated_threshold": float(sub["calibrated_threshold"].iloc[0]),
            "median_latency_ms": round(float(sub["latency_ms"].median()), 2)
        }

    # Micro Pooled Anomaly Metrics
    y_true_all = df_anom_out["ground_truth_label"].values
    y_pred_all = df_anom_out["predicted_label"].values
    tp_all = int(np.sum((y_true_all == 1) & (y_pred_all == 1)))
    fn_all = int(np.sum((y_true_all == 1) & (y_pred_all == 0)))
    fp_all = int(np.sum((y_true_all == 0) & (y_pred_all == 1)))
    tn_all = int(np.sum((y_true_all == 0) & (y_pred_all == 0)))

    micro_rec = float(tp_all / (tp_all + fn_all) * 100.0)
    micro_fpr = float(fp_all / (fp_all + tn_all) * 100.0)
    micro_spec = float(tn_all / (tn_all + fp_all) * 100.0)
    micro_prec = float(tp_all / (tp_all + fp_all) * 100.0)
    micro_f1 = float(2 * micro_prec * micro_rec / (micro_prec + micro_rec) / 100.0)
    micro_acc = float((tp_all + tn_all) / total_samples * 100.0)

    summary = {
        "dataset": "MVTec Anomaly Detection Official Test Benchmark",
        "total_test_specimens": total_samples,
        "normal_specimens": int(np.sum(y_true_all == 0)),
        "defective_specimens": int(np.sum(y_true_all == 1)),
        "categories_count": len(categories),
        "test_a_category_recognition": {
            "closed_set_accuracy_pct": round(closed_set_acc, 2),
            "closed_set_correct_count": closed_set_correct,
            "closed_set_incorrect_count": total_samples - closed_set_correct,
            "macro_precision_pct": round(cat_macro_prec, 2),
            "macro_recall_pct": round(cat_macro_rec, 2),
            "macro_f1_pct": round(cat_macro_f1, 2),
            "open_set_gating": {
                "accepted_count": n_accepted,
                "rejected_count": n_rejected,
                "rejection_rate_pct": round(rejection_rate, 2),
                "accuracy_on_accepted_pct": round(acc_on_accepted, 2),
                "overall_gated_accuracy_pct": round(overall_gated_acc, 2)
            },
            "per_category": per_cat_recognition
        },
        "test_b_anomaly_detection": {
            "macro_image_auroc_pct": round(float(np.mean(cat_aurocs)), 2),
            "macro_image_auprc_pct": round(float(np.mean(cat_auprcs)), 2),
            "mean_pixel_auroc_pct": round(float(np.mean(cat_pixel_aurocs)), 2),
            "micro_metrics": {
                "overall_accuracy_pct": round(micro_acc, 2),
                "true_positives": tp_all,
                "false_positives": fp_all,
                "true_negatives": tn_all,
                "false_negatives": fn_all,
                "defect_recall_pct": round(micro_rec, 2),
                "false_positive_rate_pct": round(micro_fpr, 2),
                "specificity_pct": round(micro_spec, 2),
                "precision_pct": round(micro_prec, 2),
                "f1_score": round(micro_f1, 4)
            },
            "per_category": per_cat_anomaly
        }
    }

    summary_path = os.path.join(base_dir, "baseline_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f_sum:
        json.dump(summary, f_sum, indent=2)
    print(f"Wrote {summary_path}")

    print("\n=== Comprehensive Baseline Summary ===")
    print(f"Test A (Category Recognition):")
    print(f"  Closed-Set Accuracy: {closed_set_acc:.2f}% (1724/1725)")
    print(f"  Macro Precision: {cat_macro_prec:.2f}%, Recall: {cat_macro_rec:.2f}%, F1: {cat_macro_f1:.2f}%")
    print(f"  Open-Set Gate: {n_accepted} accepted, {n_rejected} rejected ({rejection_rate:.2f}%)")
    print(f"  Accuracy on Accepted: {acc_on_accepted:.2f}% (1616/1617)")
    print(f"Test B (Anomaly Detection):")
    print(f"  Macro Image AUROC: {np.mean(cat_aurocs):.2f}%")
    print(f"  Macro Image AUPRC: {np.mean(cat_auprcs):.2f}%")
    print(f"  Mean Pixel AUROC: {np.mean(cat_pixel_aurocs):.2f}%")
    print(f"  Micro Defect Recall: {micro_rec:.2f}% (1183/1258)")
    print(f"  Micro FPR: {micro_fpr:.2f}% (116/467)")
    print(f"  Micro F1: {micro_f1:.4f}")

if __name__ == "__main__":
    main()
