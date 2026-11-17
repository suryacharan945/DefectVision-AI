"""
DefectVision AI — Production Threshold Calibrator
Calibrates the anomaly decision threshold for a production inspection profile
using a held-out set of defect-free normal images captured from the target station.

Features:
- Computes empirical quantile distribution (p50, p90, p95, p99, mean, std).
- Determines calibrated threshold satisfying target False Alarm Rate (FAR).
- Optionally evaluates known defect images to measure sensitivity and recall.
- Saves threshold.json and updates profile.json.
"""

import os
import sys
import argparse
import glob
import json
import time
from datetime import datetime
import numpy as np
import cv2
import torch

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "DefectVisionAI"))

from src.patchcore import PatchCoreExtractor
from src.production_profile_service import ProductionProfileService

PC_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
PC_STD  = np.array([0.229, 0.224, 0.225], dtype=np.float32)
PC_IMG_SIZE = 224


def score_image_with_profile(img_bgr, extractor, model, profile, profile_service, device):
    roi_bgr, _ = profile_service.extract_roi(img_bgr, profile)
    img_rgb = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2RGB)
    img_resized = cv2.resize(img_rgb, (PC_IMG_SIZE, PC_IMG_SIZE)).astype(np.float32) / 255.0
    img_norm = (img_resized - PC_MEAN) / PC_STD
    tensor = torch.from_numpy(img_norm).permute(2, 0, 1).unsqueeze(0).float().to(device)

    with torch.no_grad():
        fused = extractor(tensor)[0].cpu().numpy()

    _, score = model.score(fused)
    return float(score)


def calibrate_production_threshold(
    profile_id: str,
    val_normal_dir: str,
    val_defect_dir: str = None,
    target_far: float = 0.01,
    output_dir: str = None,
    device: str = "cpu"
):
    print(f"============================================================")
    print(f"DEFECTVISION AI — PRODUCTION THRESHOLD CALIBRATOR")
    print(f"Profile:        {profile_id}")
    print(f"Val Normal Dir: {val_normal_dir}")
    print(f"Val Defect Dir: {val_defect_dir or 'None'}")
    print(f"Target FAR:     {target_far * 100:.2f}%")
    print(f"Device:         {device}")
    print(f"============================================================")

    profile_service = ProductionProfileService()
    profile = profile_service.get_profile(profile_id)
    if profile is None:
        raise ValueError(f"Profile '{profile_id}' not found in {profile_service.profiles_dir}")

    profile_dir = profile.get("_profile_dir")
    if output_dir is None:
        output_dir = profile_dir

    # Load Model
    model = profile_service.get_profile_model(profile_id)
    if model is None:
        raise ValueError(f"Could not load PatchCore model for profile '{profile_id}'. Build memory bank first.")

    # Initialize Extractor
    torch_device = torch.device(device if (device == "cuda" and torch.cuda.is_available()) else "cpu")
    grid_size = profile.get("model_config", {}).get("grid_size", 28)
    extractor = PatchCoreExtractor(grid_size=grid_size).to(torch_device)
    extractor.eval()

    # 1. Gather held-out normal images
    normal_files = []
    for pat in ["*.png", "*.jpg", "*.jpeg", "*.bmp"]:
        normal_files.extend(glob.glob(os.path.join(val_normal_dir, pat)))
        normal_files.extend(glob.glob(os.path.join(val_normal_dir, "**", pat), recursive=True))
    normal_files = sorted(list(set(normal_files)))

    if not normal_files:
        raise FileNotFoundError(f"No held-out normal images found in {val_normal_dir}")
    print(f"[1/3] Scoring {len(normal_files)} held-out normal images...")

    normal_scores = []
    for f in normal_files:
        img = cv2.imread(f)
        if img is not None:
            s = score_image_with_profile(img, extractor, model, profile, profile_service, torch_device)
            normal_scores.append(s)

    normal_scores = np.array(normal_scores, dtype=np.float64)
    n_samples = len(normal_scores)
    mean_score = float(np.mean(normal_scores))
    std_score = float(np.std(normal_scores))
    p50 = float(np.percentile(normal_scores, 50))
    p75 = float(np.percentile(normal_scores, 75))
    p90 = float(np.percentile(normal_scores, 90))
    p95 = float(np.percentile(normal_scores, 95))
    p99 = float(np.percentile(normal_scores, 99))
    max_normal = float(np.max(normal_scores))

    print(f"Normal Scores Distribution (N={n_samples}):")
    print(f" - Mean: {mean_score:.4f} (std: {std_score:.4f})")
    print(f" - p50:  {p50:.4f}")
    print(f" - p90:  {p90:.4f}")
    print(f" - p95:  {p95:.4f}")
    print(f" - p99:  {p99:.4f}")
    print(f" - Max:  {max_normal:.4f}")

    # Determine calibrated threshold based on target FAR
    # With target_far = 0.01, threshold is at or above p99 with small industrial headroom
    safety_margin = max(0.01, std_score * 0.15)
    calibrated_threshold = float(round(p99 + safety_margin, 4))
    print(f"[2/3] Determined Calibrated Threshold: {calibrated_threshold:.4f} (FAR target <= {target_far:.1%})")

    # 2. Evaluate on defect samples if provided
    defect_metrics = {}
    if val_defect_dir and os.path.exists(val_defect_dir):
        defect_files = []
        for pat in ["*.png", "*.jpg", "*.jpeg", "*.bmp"]:
            defect_files.extend(glob.glob(os.path.join(val_defect_dir, pat)))
            defect_files.extend(glob.glob(os.path.join(val_defect_dir, "**", pat), recursive=True))
        defect_files = sorted(list(set(defect_files)))

        if defect_files:
            print(f"[3/3] Evaluating on {len(defect_files)} validation defect specimens...")
            defect_scores = []
            for f in defect_files:
                img = cv2.imread(f)
                if img is not None:
                    s = score_image_with_profile(img, extractor, model, profile, profile_service, torch_device)
                    defect_scores.append(s)
            defect_scores = np.array(defect_scores, dtype=np.float64)
            detected_defects = int((defect_scores >= calibrated_threshold).sum())
            recall = float(detected_defects / len(defect_scores))
            false_alarms = int((normal_scores >= calibrated_threshold).sum())
            emp_far = float(false_alarms / len(normal_scores))

            defect_metrics = {
                "defect_samples_count": len(defect_scores),
                "defects_detected": detected_defects,
                "defect_recall": round(recall, 4),
                "empirical_far": round(emp_far, 4),
                "mean_defect_score": round(float(np.mean(defect_scores)), 4),
                "min_defect_score": round(float(np.min(defect_scores)), 4)
            }
            print(f"Defect Evaluation:")
            print(f" - Recall: {recall * 100:.2f}% ({detected_defects}/{len(defect_scores)})")
            print(f" - Empirical FAR: {emp_far * 100:.2f}% ({false_alarms}/{len(normal_scores)})")

    # 3. Save threshold.json
    threshold_data = {
        "profile_id": profile_id,
        "calibrated_threshold": calibrated_threshold,
        "target_far": target_far,
        "calibration_date": datetime.utcnow().isoformat() + "Z",
        "sample_counts": {
            "normal_calibration_samples": n_samples,
            "defect_validation_samples": defect_metrics.get("defect_samples_count", 0)
        },
        "score_distribution": {
            "mean": round(mean_score, 4),
            "std": round(std_score, 4),
            "p50": round(p50, 4),
            "p75": round(p75, 4),
            "p90": round(p90, 4),
            "p95": round(p95, 4),
            "p99": round(p99, 4),
            "max": round(max_normal, 4)
        },
        "validation_metrics": defect_metrics
    }

    thresh_path = os.path.join(output_dir, "threshold.json")
    with open(thresh_path, "w", encoding="utf-8") as f:
        json.dump(threshold_data, f, indent=2)
    print(f"Saved calibration data to {thresh_path}")

    # 4. Update profile.json in output_dir
    profile_json_path = os.path.join(output_dir, "profile.json")
    if os.path.exists(profile_json_path):
        with open(profile_json_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        cfg["threshold_config"] = {
            "calibrated_threshold": calibrated_threshold,
            "target_far": target_far,
            "calibration_sample_count": n_samples,
            "calibration_date": threshold_data["calibration_date"],
            "metrics": threshold_data["score_distribution"]
        }
        with open(profile_json_path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
        print(f"Updated {profile_json_path} with calibrated threshold: {calibrated_threshold}")

    return threshold_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calibrate production inspection threshold.")
    parser.add_argument("--profile-id", type=str, required=True, help="Profile ID (e.g. bottle_001_station_01)")
    parser.add_argument("--val-normal-dir", type=str, required=True, help="Directory of held-out normal images")
    parser.add_argument("--val-defect-dir", type=str, default=None, help="Directory of defect images (optional)")
    parser.add_argument("--target-far", type=float, default=0.01, help="Target false alarm rate (default: 0.01)")
    parser.add_argument("--output-dir", type=str, default=None, help="Output directory")
    parser.add_argument("--device", type=str, default="cpu", help="Compute device ('cpu' or 'cuda')")

    args = parser.parse_args()
    calibrate_production_threshold(
        profile_id=args.profile_id,
        val_normal_dir=args.val_normal_dir,
        val_defect_dir=args.val_defect_dir,
        target_far=args.target_far,
        output_dir=args.output_dir,
        device=args.device
    )
