#!/usr/bin/env python3
"""
DefectVision AI — Category-Specific PatchCore Decision Threshold Calibration
Computes empirical anomaly score distributions on nominal calibration images
(strictly disjoint from training memory banks and official test sets) for all 15 MVTec AD categories.
Generates production threshold manifest and calibration audit report.
"""

import os
import sys
import time
import json
import numpy as np
import pandas as pd
import cv2
import torch

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "DefectVisionAI"))

from src.patchcore import PatchCoreExtractor, PatchCoreModel, normalize_map

MODELS_DIR = os.path.join(PROJECT_ROOT, "DefectVisionAI", "models")
PATCHCORE_DIR = os.path.join(MODELS_DIR, "patchcore")
MANIFESTS_DIR = os.path.join(PROJECT_ROOT, "release", "dataset_manifests")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "release", "patchcore_calibration")
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

def calibrate_all_categories(device="cpu"):
    print("=================================================================", flush=True)
    print("DefectVision AI — Category-Specific PatchCore Threshold Calibration", flush=True)
    print(f"Device: {device} | Grid Size: {GRID_SIZE} | Resolution: {PC_IMG_SIZE}x{PC_IMG_SIZE}", flush=True)
    print("=================================================================", flush=True)

    cal_csv = os.path.join(MANIFESTS_DIR, "patchcore_calibration_split.csv")
    if not os.path.exists(cal_csv):
        raise FileNotFoundError(f"Calibration split missing: {cal_csv}")

    cal_df = pd.read_csv(cal_csv)
    print(f"Total calibration images across 15 categories: {len(cal_df)}", flush=True)

    extractor = PatchCoreExtractor(grid_size=GRID_SIZE).to(device)
    extractor.eval()

    calibration_results = []
    threshold_dict = {}

    for cat in CATEGORIES:
        t0 = time.time()
        mb_path = os.path.join(PATCHCORE_DIR, cat, "memory_bank.npy")
        if not os.path.exists(mb_path):
            print(f"[ERROR] Memory bank missing for {cat}: {mb_path}", flush=True)
            continue

        model = PatchCoreModel()
        model.load(mb_path, grid_size=GRID_SIZE)

        cat_images = cal_df[cal_df["category"] == cat]["filepath"].tolist()
        if not cat_images:
            print(f"[WARN] No calibration images found for {cat}", flush=True)
            continue

        scores = []
        for p in cat_images:
            tensor = load_pc_tensor(p)
            if tensor is None:
                continue
            tensor = tensor.unsqueeze(0).to(device)
            with torch.no_grad():
                fused = extractor(tensor)[0].cpu().numpy()
            _, img_score = model.score(fused)
            scores.append(float(img_score))

        scores = np.array(scores)
        mean_s = float(np.mean(scores))
        std_s = float(np.std(scores))
        p90_s = float(np.percentile(scores, 90.0))
        p95_s = float(np.percentile(scores, 95.0))
        p99_s = float(np.percentile(scores, 99.0))
        p995_s = float(np.percentile(scores, 99.5))
        max_s = float(np.max(scores))
        dt = time.time() - t0

        # Calibrated threshold: 99.5th percentile or max(p99, mean + 3*std)
        calibrated_threshold = float(round(p995_s, 4))

        record = {
            "category": cat,
            "memory_bank_path": f"models/patchcore/{cat}/memory_bank.npy",
            "memory_bank_tokens": int(model.memory_bank.shape[0]),
            "feature_dim": int(model.memory_bank.shape[1]),
            "n_calibration_samples": len(scores),
            "baseline_mean": round(mean_s, 4),
            "baseline_std": round(std_s, 4),
            "p90_threshold": round(p90_s, 4),
            "p95_threshold": round(p95_s, 4),
            "p99_threshold": round(p99_s, 4),
            "p995_threshold": round(p995_s, 4),
            "calibrated_threshold": calibrated_threshold,
            "max_calibration_score": round(max_s, 4),
            "calibration_latency_s": round(dt, 2)
        }
        calibration_results.append(record)

        threshold_dict[cat] = {
            "calibrated_threshold": calibrated_threshold,
            "baseline_mean": round(mean_s, 4),
            "baseline_std": round(std_s, 4),
            "baseline_p99": round(p99_s, 4),
            "baseline_p995": round(p995_s, 4),
            "n_calibration_samples": len(scores),
            "memory_bank_tokens": int(model.memory_bank.shape[0])
        }

        print(f"  [{cat:<12}] N={len(scores):>2} | Mean={mean_s:.4f} | Std={std_s:.4f} | "
              f"P95={p95_s:.4f} | P99={p99_s:.4f} | Threshold(P99.5)={calibrated_threshold:.4f} ({dt:.1f}s)", flush=True)

    # Save CSV
    df_res = pd.DataFrame(calibration_results)
    csv_path = os.path.join(OUTPUT_DIR, "calibrated_thresholds.csv")
    df_res.to_csv(csv_path, index=False)
    print(f"\nSaved CSV to: {csv_path}", flush=True)

    # Save JSON for backend and model registry
    json_path = os.path.join(PATCHCORE_DIR, "category_thresholds.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(threshold_dict, f, indent=2)
    print(f"Saved threshold manifest to: {json_path}", flush=True)

    # Save to release directory as well
    rel_json = os.path.join(OUTPUT_DIR, "category_thresholds.json")
    with open(rel_json, "w", encoding="utf-8") as f:
        json.dump(threshold_dict, f, indent=2)

    # Generate Markdown Report
    md_path = os.path.join(OUTPUT_DIR, "calibration_report.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# DefectVision AI — Category-Specific PatchCore Threshold Calibration\n\n")
        f.write("**Protocol:** 80/20 nominal training split (Zero test leakage). Fitted strictly on disjoint nominal calibration images.\n\n")
        f.write("| Category | Calibration Samples | MB Tokens | Baseline Mean | Baseline Std | P95 | P99 | Calibrated Threshold (P99.5) |\n")
        f.write("|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|\n")
        for r in calibration_results:
            f.write(f"| `{r['category']}` | {r['n_calibration_samples']} | {r['memory_bank_tokens']:,} | {r['baseline_mean']} | {r['baseline_std']} | {r['p95_threshold']} | {r['p99_threshold']} | **{r['calibrated_threshold']}** |\n")
        f.write("\n")

    print(f"Report generated: {md_path}", flush=True)
    return threshold_dict

if __name__ == "__main__":
    device = "cuda" if torch.cuda.is_available() else "cpu"
    calibrate_all_categories(device=device)
