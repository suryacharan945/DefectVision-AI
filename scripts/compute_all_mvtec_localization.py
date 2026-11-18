import os
import sys
import time
import json
import cv2
import numpy as np
import pandas as pd
import torch
import scipy.ndimage
from sklearn.metrics import roc_auc_score

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "DefectVisionAI"))

from src.patchcore import PatchCoreExtractor, PatchCoreModel

DATA_ROOT = os.path.join(PROJECT_ROOT, "DefectVisionAI", "dataset", "raw", "mvtec")
MANIFEST_PATH = os.path.join(PROJECT_ROOT, "release", "dataset_manifests", "official_test_split.csv")
THRESHOLDS_PATH = os.path.join(PROJECT_ROOT, "DefectVisionAI", "models", "patchcore", "category_thresholds.json")
OUT_DIR = os.path.join(PROJECT_ROOT, "release", "final_validation")
os.makedirs(OUT_DIR, exist_ok=True)

CATEGORIES = [
    "bottle", "cable", "capsule", "carpet", "grid",
    "hazelnut", "leather", "metal_nut", "pill", "screw",
    "tile", "toothbrush", "transistor", "wood", "zipper"
]

PC_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
PC_STD  = np.array([0.229, 0.224, 0.225], dtype=np.float32)

def run_localization_audit():
    print("=" * 70, flush=True)
    print("DefectVision AI — Comprehensive 15-Category MVTec Localization Audit", flush=True)
    print("Computing Raw-Map Pooled Category Pixel AUROC, Per-Defect AUROC, IoU, and Dice", flush=True)
    print("=" * 70, flush=True)

    df = pd.read_csv(MANIFEST_PATH)
    with open(THRESHOLDS_PATH, "r", encoding="utf-8") as f:
        thresh_data = json.load(f)

    # Use single extractor
    extractor = PatchCoreExtractor(grid_size=28)
    extractor.eval()

    results = []

    for cat_idx, cat in enumerate(CATEGORIES):
        t0 = time.time()
        cat_df = df[df["category"] == cat].copy()
        cat_type = cat_df["category_type"].iloc[0]
        cat_thresh = thresh_data.get(cat, {}).get("calibrated_threshold", 1.5)

        mb_path = os.path.join(PROJECT_ROOT, "DefectVisionAI", "models", "patchcore", cat, "memory_bank.npy")
        if not os.path.exists(mb_path):
            print(f"[ERROR] Memory bank missing for {cat}: {mb_path}", flush=True)
            continue

        model = PatchCoreModel()
        model.load(mb_path, grid_size=28)

        all_gt_pixels = []
        all_pred_pixels = []
        per_defect_auroc = []
        defect_ious = []
        defect_dices = []
        n_defects = 0

        # Process specimens
        for _, row in cat_df.iterrows():
            fp = row["filepath"]
            if not os.path.exists(fp):
                # Try relative resolution
                fp = os.path.join(PROJECT_ROOT, row["rel_path"])
            img = cv2.imread(fp)
            if img is None:
                continue

            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_resized = cv2.resize(img_rgb, (224, 224)).astype(np.float32) / 255.0
            img_norm = (img_resized - PC_MEAN) / PC_STD
            tensor = torch.from_numpy(img_norm).permute(2, 0, 1).unsqueeze(0).float()

            with torch.no_grad():
                fused = extractor(tensor)[0].numpy()
            dist_map, _ = model.score(fused)

            # Raw un-normalized continuous map smoothed with sigma=4.0
            smooth_map = cv2.resize(dist_map, (224, 224), interpolation=cv2.INTER_CUBIC)
            smooth_map = scipy.ndimage.gaussian_filter(smooth_map, sigma=4.0)

            mask_path = row.get("gt_mask_path")
            is_def = int(row["is_defect"])

            if is_def == 1:
                n_defects += 1
                if pd.notna(mask_path) and os.path.exists(str(mask_path)):
                    gt_mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
                    gt_bin = (cv2.resize(gt_mask, (224, 224), interpolation=cv2.INTER_NEAREST) > 0).astype(np.uint8)
                else:
                    gt_bin = np.ones((224, 224), dtype=np.uint8)

                if len(np.unique(gt_bin)) > 1:
                    try:
                        auc = roc_auc_score(gt_bin.flatten(), smooth_map.flatten())
                        per_defect_auroc.append(auc)
                    except Exception:
                        pass

                # IoU and Dice using calibrated threshold
                pred_bin = (smooth_map >= cat_thresh).astype(np.uint8)
                inter = np.logical_and(pred_bin, gt_bin).sum()
                union = np.logical_or(pred_bin, gt_bin).sum()
                iou = inter / union if union > 0 else 0.0
                dice = 2 * inter / (pred_bin.sum() + gt_bin.sum()) if (pred_bin.sum() + gt_bin.sum()) > 0 else 0.0
                defect_ious.append(iou)
                defect_dices.append(dice)
            else:
                gt_bin = np.zeros((224, 224), dtype=np.uint8)

            all_gt_pixels.append(gt_bin.flatten())
            all_pred_pixels.append(smooth_map.flatten())

        all_gt = np.concatenate(all_gt_pixels)
        all_pred = np.concatenate(all_pred_pixels)
        total_pixels = len(all_gt)

        try:
            pooled_auc = float(roc_auc_score(all_gt, all_pred))
        except Exception:
            pooled_auc = 0.0

        mean_per_defect_auc = float(np.mean(per_defect_auroc)) if per_defect_auroc else 0.0
        mean_iou = float(np.mean(defect_ious)) if defect_ious else 0.0
        mean_dice = float(np.mean(defect_dices)) if defect_dices else 0.0

        grade = "EXCELLENT" if pooled_auc >= 0.95 else ("GOOD" if pooled_auc >= 0.90 else "ACCEPTABLE")

        elapsed = time.time() - t0
        print(f"[{cat_idx+1}/15] {cat.upper():<12} ({cat_type}): Pooled Pixel AUROC={pooled_auc*100:.2f}%, Per-Defect AUROC={mean_per_defect_auc*100:.2f}%, Mean IoU={mean_iou*100:.2f}%, Dice={mean_dice*100:.2f}% ({elapsed:.1f}s)", flush=True)

        results.append({
            "category": cat,
            "category_type": cat_type,
            "total_test_specimens": len(cat_df),
            "defect_specimens": n_defects,
            "total_pixels_evaluated": total_pixels,
            "calibrated_threshold": round(cat_thresh, 4),
            "per_defect_mean_pixel_auroc": round(mean_per_defect_auc, 4),
            "pooled_category_pixel_auroc": round(pooled_auc, 4),
            "mean_defect_iou": round(mean_iou, 4),
            "mean_defect_dice": round(mean_dice, 4),
            "localization_quality_grade": grade
        })

    out_df = pd.DataFrame(results)
    out_csv = os.path.join(OUT_DIR, "MVTEC_LOCALIZATION_AUDIT.csv")
    out_df.to_csv(out_csv, index=False)
    print("\n" + "=" * 70, flush=True)
    print(f"Localization Audit Table written to: {out_csv}", flush=True)
    print(f"Macro Pooled Category Pixel AUROC: {out_df['pooled_category_pixel_auroc'].mean()*100:.2f}%", flush=True)
    print(f"Macro Per-Defect Mean Pixel AUROC: {out_df['per_defect_mean_pixel_auroc'].mean()*100:.2f}%", flush=True)
    print(f"Macro Mean Defect IoU:            {out_df['mean_defect_iou'].mean()*100:.2f}%", flush=True)
    print(f"Macro Mean Defect Dice:           {out_df['mean_defect_dice'].mean()*100:.2f}%", flush=True)
    print("=" * 70, flush=True)

if __name__ == "__main__":
    run_localization_audit()
