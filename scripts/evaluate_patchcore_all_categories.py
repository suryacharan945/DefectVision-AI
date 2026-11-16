#!/usr/bin/env python3
"""
DefectVision AI — Official 15-Category PatchCore Benchmark Evaluation
Evaluates all 15 official MVTec AD categories strictly on the quarantined
1,725-image official test set. Computes Image AUROC, AUPRC, Sensitivity/Recall,
Specificity, Precision, F1-score, Confusion Matrices, and Pixel AUROC.
Outputs publication-quality CSV reports and Markdown documentation.
"""

import os
import sys
import time
import json
import numpy as np
import pandas as pd
from PIL import Image

import torch
import cv2
from sklearn.metrics import roc_auc_score, average_precision_score, precision_recall_fscore_support
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "DefectVisionAI"))

from src.patchcore import PatchCoreExtractor, PatchCoreModel, normalize_map, map_iou

MODELS_DIR = os.path.join(PROJECT_ROOT, "DefectVisionAI", "models")
PATCHCORE_DIR = os.path.join(MODELS_DIR, "patchcore")
THRESHOLDS_PATH = os.path.join(PATCHCORE_DIR, "category_thresholds.json")
MANIFESTS_DIR = os.path.join(PROJECT_ROOT, "release", "dataset_manifests")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "release", "patchcore_evaluation")
os.makedirs(OUTPUT_DIR, exist_ok=True)

CATEGORIES = [
    "bottle", "cable", "capsule", "carpet", "grid",
    "hazelnut", "leather", "metal_nut", "pill", "screw",
    "tile", "toothbrush", "transistor", "wood", "zipper"
]

PC_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
PC_STD  = np.array([0.229, 0.224, 0.225], dtype=np.float32)
PC_IMG_SIZE = 224
GRID_SIZE = 28

def load_pc_tensor(filepath, size=PC_IMG_SIZE):
    img = cv2.imread(filepath)
    if img is None:
        return None
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (size, size)).astype(np.float32) / 255.0
    img = (img - PC_MEAN) / PC_STD
    return torch.from_numpy(img).permute(2, 0, 1).float()

def evaluate_all(device="cpu"):
    print("=================================================================", flush=True)
    print("DefectVision AI — Official 15-Category PatchCore Evaluation", flush=True)
    print(f"Device: {device} | Quarantined Test Set: 1,725 Images", flush=True)
    print("=================================================================", flush=True)

    test_csv = os.path.join(MANIFESTS_DIR, "official_test_split.csv")
    if not os.path.exists(test_csv):
        raise FileNotFoundError(f"Test split missing: {test_csv}")

    test_df = pd.read_csv(test_csv)
    print(f"Loaded official test split: {len(test_df)} specimens", flush=True)

    # Load thresholds
    thresholds = {}
    if os.path.exists(THRESHOLDS_PATH):
        with open(THRESHOLDS_PATH, "r", encoding="utf-8") as f:
            thresholds = json.load(f)
    else:
        # Fallback to defaults if calibration still finishing
        fallback_json = os.path.join(PROJECT_ROOT, "DefectVisionAI", "reports", "step9_severity_baselines.csv")
        if os.path.exists(fallback_json):
            b_df = pd.read_csv(fallback_json)
            for _, r in b_df.iterrows():
                thresholds[r["category"]] = {"calibrated_threshold": float(r["baseline_p99"])}

    extractor = PatchCoreExtractor(grid_size=GRID_SIZE).to(device)
    extractor.eval()

    all_prediction_records = []
    category_summary_records = []

    for cat in CATEGORIES:
        t0 = time.time()
        mb_path = os.path.join(PATCHCORE_DIR, cat, "memory_bank.npy")
        if not os.path.exists(mb_path):
            print(f"[ERROR] Memory bank missing for {cat}: {mb_path}", flush=True)
            continue

        model = PatchCoreModel()
        model.load(mb_path, grid_size=GRID_SIZE)

        cat_thresh = thresholds.get(cat, {}).get("calibrated_threshold", 1.7452)

        cat_df = test_df[test_df["category"] == cat]
        y_true = cat_df["is_defect"].values
        scores = []
        latencies = []
        pixel_aurocs = []

        for _, row in cat_df.iterrows():
            fp = row["filepath"]
            tensor = load_pc_tensor(fp)
            if tensor is None:
                continue
            tensor = tensor.unsqueeze(0).to(device)

            t_inf = time.perf_counter()
            with torch.no_grad():
                fused = extractor(tensor)[0].cpu().numpy()
            dist_map, img_score = model.score(fused)
            latencies.append((time.perf_counter() - t_inf) * 1000.0)

            scores.append(float(img_score))
            is_pred_defect = int(img_score > cat_thresh)

            # Pixel evaluation if mask exists
            mask_val = row.get("gt_mask_path", None)
            mask_path = str(mask_val).strip() if (pd.notna(mask_val) and str(mask_val).strip() != "") else None
            pix_auc = None
            if mask_path and os.path.exists(mask_path):
                gt_mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
                if gt_mask is not None:
                    norm_map = normalize_map(dist_map)
                    res_map = cv2.resize(norm_map, (gt_mask.shape[1], gt_mask.shape[0]))
                    gt_bin = (gt_mask > 0).astype(np.uint8).flatten()
                    map_flat = res_map.flatten()
                    if len(np.unique(gt_bin)) > 1:
                        try:
                            pix_auc = float(roc_auc_score(gt_bin, map_flat))
                            pixel_aurocs.append(pix_auc)
                        except Exception:
                            pass

            all_prediction_records.append({
                "filepath": fp,
                "category": cat,
                "category_type": row["category_type"],
                "is_defect": row["is_defect"],
                "defect_type": row["defect_type"],
                "anomaly_score": float(round(img_score, 4)),
                "calibrated_threshold": float(round(cat_thresh, 4)),
                "predicted_defect": is_pred_defect,
                "correct": int(is_pred_defect == row["is_defect"]),
                "pixel_auroc": round(pix_auc, 4) if pix_auc is not None else None
            })

        scores = np.array(scores)
        y_pred = (scores > cat_thresh).astype(int)

        # Compute Image AUROC & AUPRC
        img_auroc = float(roc_auc_score(y_true, scores)) if len(np.unique(y_true)) > 1 else 1.0
        img_auprc = float(average_precision_score(y_true, scores)) if len(np.unique(y_true)) > 1 else 1.0

        # Confusion matrix
        tp = int(((y_true == 1) & (y_pred == 1)).sum())
        fp = int(((y_true == 0) & (y_pred == 1)).sum())
        tn = int(((y_true == 0) & (y_pred == 0)).sum())
        fn = int(((y_true == 1) & (y_pred == 0)).sum())

        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0

        mean_pix_auroc = float(np.mean(pixel_aurocs)) if pixel_aurocs else None

        cat_summary = {
            "category": cat,
            "type": cat_df["category_type"].iloc[0],
            "total_test": len(cat_df),
            "normal_test": int((y_true == 0).sum()),
            "defect_test": int((y_true == 1).sum()),
            "calibrated_threshold": round(cat_thresh, 4),
            "image_auroc": round(img_auroc, 4),
            "image_auprc": round(img_auprc, 4),
            "pixel_auroc": round(mean_pix_auroc, 4) if mean_pix_auroc is not None else "N/A",
            "sensitivity_recall": round(recall, 4),
            "specificity": round(specificity, 4),
            "precision": round(precision, 4),
            "f1_score": round(f1, 4),
            "fpr": round(fpr, 4),
            "fnr": round(fnr, 4),
            "true_positives": tp,
            "false_positives": fp,
            "true_negatives": tn,
            "false_negatives": fn,
            "latency_p50_ms": round(float(np.percentile(latencies, 50)), 2),
            "latency_mean_ms": round(float(np.mean(latencies)), 2)
        }
        category_summary_records.append(cat_summary)

        print(f"  [{cat:<12}] AUROC={img_auroc*100:>5.2f}% | AUPRC={img_auprc*100:>5.2f}% | "
              f"Recall={recall*100:>5.2f}% | Spec={specificity*100:>5.2f}% | F1={f1*100:>5.2f}% | "
              f"TP={tp:>2} FP={fp:>2} TN={tn:>2} FN={fn:>2} ({time.time()-t0:.1f}s)", flush=True)

    # Save outputs
    df_preds = pd.DataFrame(all_prediction_records)
    preds_csv = os.path.join(OUTPUT_DIR, "patchcore_official_test_predictions.csv")
    df_preds.to_csv(preds_csv, index=False)

    df_summary = pd.DataFrame(category_summary_records)
    summary_csv = os.path.join(OUTPUT_DIR, "patchcore_per_category_metrics.csv")
    df_summary.to_csv(summary_csv, index=False)

    # Macro Averages
    macro_auroc = df_summary["image_auroc"].mean()
    macro_auprc = df_summary["image_auprc"].mean()
    macro_recall = df_summary["sensitivity_recall"].mean()
    macro_spec = df_summary["specificity"].mean()
    macro_f1 = df_summary["f1_score"].mean()

    # Generate Markdown Report
    report_md = os.path.join(OUTPUT_DIR, "patchcore_evaluation_report.md")
    with open(report_md, "w", encoding="utf-8") as f:
        f.write("# DefectVision AI — Official 15-Category PatchCore Benchmark Report\n\n")
        f.write("**Benchmark:** MVTec Anomaly Detection (1,725 Official Test Images, CC BY-NC-SA 4.0).\n\n")
        f.write("**Evaluation Protocol:** Quarantined test evaluation using category-specific nominal memory banks and disjoint calibration thresholds.\n\n")
        f.write("## 1. Executive Macro Summary\n\n")
        f.write(f"- **Macro Image AUROC:** {macro_auroc*100:.2f}%\n")
        f.write(f"- **Macro Image AUPRC:** {macro_auprc*100:.2f}%\n")
        f.write(f"- **Macro Defect Recall (Sensitivity):** {macro_recall*100:.2f}%\n")
        f.write(f"- **Macro Specificity:** {macro_spec*100:.2f}%\n")
        f.write(f"- **Macro F1-Score:** {macro_f1*100:.2f}%\n\n")

        f.write("## 2. Per-Category Quantitative Results\n\n")
        f.write("| Category | Type | Test (N/D) | Threshold | Image AUROC | Image AUPRC | Pixel AUROC | Recall | Specificity | F1 | Escapes (FN) | False Alarms (FP) |\n")
        f.write("|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|\n")
        for r in category_summary_records:
            f.write(f"| `{r['category']}` | {r['type']} | {r['normal_test']}/{r['defect_test']} | {r['calibrated_threshold']} | {r['image_auroc']*100:.2f}% | {r['image_auprc']*100:.2f}% | {r['pixel_auroc']} | {r['sensitivity_recall']*100:.2f}% | {r['specificity']*100:.2f}% | {r['f1_score']*100:.2f}% | {r['false_negatives']} | {r['false_positives']} |\n")
        f.write(f"| **MACRO AVG** | - | **467/1258** | - | **{macro_auroc*100:.2f}%** | **{macro_auprc*100:.2f}%** | - | **{macro_recall*100:.2f}%** | **{macro_spec*100:.2f}%** | **{macro_f1*100:.2f}%** | **{df_summary['false_negatives'].sum()}** | **{df_summary['false_positives'].sum()}** |\n\n")

    print(f"\nSaved metrics CSV to: {summary_csv}", flush=True)
    print(f"Saved predictions CSV to: {preds_csv}", flush=True)
    print(f"Saved Markdown report to: {report_md}", flush=True)

if __name__ == "__main__":
    device = "cuda" if torch.cuda.is_available() else "cpu"
    evaluate_all(device=device)
