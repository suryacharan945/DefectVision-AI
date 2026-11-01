import os
import sys
import time
import json
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
import cv2
import faiss
import timm
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

dv_path = os.path.abspath("DefectVisionAI")
if dv_path not in sys.path:
    sys.path.insert(0, dv_path)

from src.patchcore import PatchCoreExtractor, PatchCoreModel, normalize_map
from src.severity import normalize_anomaly_score, compute_severity_score, bucket_severity

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

def run_evaluation():
    print("=== STEP 3: QUANTITATIVE EVALUATION BENCHMARK ===")
    device = torch.device("cpu")

    # Load baseline thresholds
    baseline_csv = "DefectVisionAI/reports/step9_severity_baselines.csv"
    baseline_df = pd.read_csv(baseline_csv)
    baseline_lookup = baseline_df.set_index("category").to_dict("index")

    # Load PatchCore Extractor
    print("Initializing ResNet-18 PatchCore Extractor...")
    extractor = PatchCoreExtractor(grid_size=28).to(device)
    extractor.eval()

    # Load EfficientNet-B0 v3
    print("Initializing EfficientNet-B0 v3 Classifier...")
    effnet_ckpt_path = "DefectVisionAI/models/efficientnet_baseline_v3/best_model.pt"
    best_ckpt = torch.load(effnet_ckpt_path, map_location=device)
    effnet_model = timm.create_model("efficientnet_b0", pretrained=False, num_classes=2)
    effnet_model.load_state_dict(best_ckpt["model_state"])
    effnet_model.to(device)
    effnet_model.eval()

    # Transforms
    import albumentations as A
    from albumentations.pytorch import ToTensorV2
    eff_transform = A.Compose([
        A.Resize(256, 256),
        A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ToTensorV2()
    ])

    PC_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    PC_STD  = np.array([0.229, 0.224, 0.225], dtype=np.float32)

    def evaluate_split(split_csv_path, output_preds_name):
        df_split = pd.read_csv(split_csv_path)
        print(f"\nEvaluating dataset: {split_csv_path} ({len(df_split)} samples)")

        predictions = []
        categories = sorted(df_split["category"].unique())

        t_bench_start = time.perf_counter()

        for cat in categories:
            cat_df = df_split[df_split["category"] == cat]
            baseline = baseline_lookup.get(cat)
            if not baseline:
                print(f"Warning: No baseline for category {cat}")
                continue

            # Load PatchCore memory bank for category
            mb_path = f"DefectVisionAI/models/patchcore/{cat}/memory_bank.npy"
            pc_model = PatchCoreModel()
            pc_model.load(mb_path, grid_size=28)

            optimal_thresh = float(round(baseline["baseline_p99"], 4))
            base_mean = baseline["baseline_mean"]
            base_p99 = baseline["baseline_p99"]

            for _, row in cat_df.iterrows():
                # Map filepath
                fp = row["filepath"].replace("/content/drive/MyDrive", "G:/My Drive")
                gt_is_normal = bool(row["is_normal"])
                gt_label = 0 if gt_is_normal else 1
                defect_type = row["defect_type"]

                img_bgr = cv2.imread(fp)
                if img_bgr is None:
                    continue

                # 1. PatchCore Inference
                img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
                img_pc = cv2.resize(img_rgb, (224, 224)).astype(np.float32) / 255.0
                img_pc = (img_pc - PC_MEAN) / PC_STD
                pc_tensor = torch.from_numpy(img_pc).permute(2, 0, 1).float().unsqueeze(0).to(device)

                with torch.no_grad():
                    emb = extractor(pc_tensor)[0].cpu().numpy()
                dist_map, raw_score = pc_model.score(emb)
                dist_map_norm = normalize_map(dist_map)
                defect_area_pct = float(100.0 * (dist_map_norm >= 0.5).sum() / dist_map_norm.size)
                anomaly_norm = float(normalize_anomaly_score(raw_score, base_mean, base_p99))
                pc_pred = 1 if (raw_score > optimal_thresh) else 0

                # 2. EfficientNet Inference
                eff_tensor = eff_transform(image=img_rgb)["image"].unsqueeze(0).to(device)
                with torch.no_grad():
                    logits = effnet_model(eff_tensor)
                    prob_defective = float(F.softmax(logits, dim=1)[0, 1].item())
                eff_pred = 1 if (prob_defective >= 0.50) else 0

                # 3. Hybrid Decision
                hybrid_pred = 1 if (pc_pred == 1 or eff_pred == 1) else 0

                # Severity
                confidence_pct = float(round(prob_defective * 100, 2))
                sev_score = float(round(compute_severity_score(anomaly_norm, defect_area_pct, confidence_pct), 2))
                sev_level = bucket_severity(sev_score)

                predictions.append({
                    "filepath": row["filepath"],
                    "category": cat,
                    "defect_type": defect_type,
                    "is_normal": gt_is_normal,
                    "ground_truth": gt_label,
                    "patchcore_raw_score": float(round(raw_score, 6)),
                    "patchcore_threshold": optimal_thresh,
                    "patchcore_pred": pc_pred,
                    "effnet_prob": float(round(prob_defective, 6)),
                    "effnet_pred": eff_pred,
                    "hybrid_pred": hybrid_pred,
                    "anomaly_norm": anomaly_norm,
                    "defect_area_pct": defect_area_pct,
                    "confidence_pct": confidence_pct,
                    "severity_score": sev_score,
                    "severity_level": sev_level
                })

        elapsed = time.perf_counter() - t_bench_start
        print(f"Evaluated {len(predictions)} images in {elapsed:.2f}s ({elapsed/len(predictions)*1000:.1f}ms/img)")

        pred_df = pd.DataFrame(predictions)
        pred_df.to_csv(f"release/final_18h_validation/{output_preds_name}", index=False)
        return pred_df

    # Evaluate Primary Benchmark Set (856 samples)
    pred_v2 = evaluate_split("G:/My Drive/DefectVisionAI/dataset/splits/benchmark_test_v2.csv", "evaluation_predictions.csv")

    # Evaluate Full MVTec AD Test Set (1725 samples)
    pred_full = evaluate_split("G:/My Drive/DefectVisionAI/dataset/splits/test_split.csv", "evaluation_predictions_full_mvtec.csv")

    # Compute Aggregate Metrics for Primary Benchmark Set
    y_true = pred_v2["ground_truth"].to_numpy()
    pc_scores = pred_v2["patchcore_raw_score"].to_numpy()
    pc_preds = pred_v2["patchcore_pred"].to_numpy()
    eff_scores = pred_v2["effnet_prob"].to_numpy()
    eff_preds = pred_v2["effnet_pred"].to_numpy()
    hyb_preds = pred_v2["hybrid_pred"].to_numpy()
    # For hybrid continuous score, take maximum of normalized patchcore probability and effnet prob
    hyb_scores = np.maximum(pred_v2["anomaly_norm"].to_numpy() / 100.0, eff_scores)

    metrics_list = [
        calculate_metrics_dict(y_true, pc_preds, pc_scores, "PatchCore_Unsupervised"),
        calculate_metrics_dict(y_true, eff_preds, eff_scores, "EfficientNet_B0_Supervised"),
        calculate_metrics_dict(y_true, hyb_preds, hyb_scores, "DefectVisionAI_Hybrid")
    ]
    metrics_df = pd.DataFrame(metrics_list)
    metrics_df.to_csv("release/final_18h_validation/evaluation_metrics.csv", index=False)
    print("\n--- AGGREGATE BENCHMARK METRICS (856 Images) ---")
    print(metrics_df[["system", "accuracy", "precision", "recall_sensitivity", "specificity", "f1_score", "auroc", "auprc", "fpr", "fnr"]].to_string())

    # Compute Per-Category Metrics for Primary Benchmark Set
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

    # Save Confusion Matrices JSON
    cm_dict = {
        "benchmark_856": {
            "PatchCore": confusion_matrix(y_true, pc_preds, labels=[0, 1]).tolist(),
            "EfficientNet": confusion_matrix(y_true, eff_preds, eff_scores >= 0.50).tolist(),
            "Hybrid": confusion_matrix(y_true, hyb_preds, labels=[0, 1]).tolist()
        }
    }
    with open("release/final_18h_validation/confusion_matrices.json", "w") as f:
        json.dump(cm_dict, f, indent=2)

    print("\nQuantitative Evaluation Complete! Outputs written to release/final_18h_validation/")

if __name__ == "__main__":
    run_evaluation()
