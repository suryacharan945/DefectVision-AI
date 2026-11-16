import os
import sys
import time
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
import cv2
import faiss
import timm

dv_path = os.path.abspath("DefectVisionAI")
if dv_path not in sys.path:
    sys.path.insert(0, dv_path)

from src.patchcore import PatchCoreExtractor, PatchCoreModel, normalize_map
from src.severity import normalize_anomaly_score, compute_severity_score, bucket_severity

def apply_perturbation(img_rgb, p_type, param):
    img = img_rgb.copy().astype(np.float32) / 255.0
    if p_type == "gaussian_noise":
        noise = np.random.normal(0, param, img.shape).astype(np.float32)
        res = np.clip(img + noise, 0.0, 1.0)
    elif p_type == "brightness":
        res = np.clip(img * param, 0.0, 1.0)
    elif p_type == "contrast":
        mean = np.mean(img, axis=(0, 1), keepdims=True)
        res = np.clip((img - mean) * param + mean, 0.0, 1.0)
    elif p_type == "blur":
        ksize = int(param * 4) | 1
        res = cv2.GaussianBlur(img, (ksize, ksize), param)
    elif p_type == "rotation":
        h, w = img.shape[:2]
        M = cv2.getRotationMatrix2D((w / 2, h / 2), param, 1.0)
        res = cv2.warpAffine(img, M, (w, h), borderMode=cv2.BORDER_REFLECT)
    else:
        res = img
    return (res * 255.0).astype(np.uint8)

def run_robustness():
    print("=== STEP 4: ROBUSTNESS & PERTURBATION STRESS TEST ===")
    device = torch.device("cpu")

    # Baselines
    baseline_df = pd.read_csv("DefectVisionAI/reports/step9_severity_baselines.csv")
    baseline_lookup = baseline_df.set_index("category").to_dict("index")

    # Models
    extractor = PatchCoreExtractor(grid_size=28).to(device)
    extractor.eval()

    best_ckpt = torch.load("DefectVisionAI/models/efficientnet_baseline_v3/best_model.pt", map_location=device)
    effnet = timm.create_model("efficientnet_b0", pretrained=False, num_classes=2)
    effnet.load_state_dict(best_ckpt["model_state"])
    effnet.to(device)
    effnet.eval()

    import albumentations as A
    from albumentations.pytorch import ToTensorV2
    eff_transform = A.Compose([
        A.Resize(256, 256),
        A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ToTensorV2()
    ])

    PC_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    PC_STD  = np.array([0.229, 0.224, 0.225], dtype=np.float32)

    # Test on representative specimens from multiple categories
    test_specs = [
        {"cat": "bottle", "path": "G:/My Drive/DefectVisionAI/dataset/raw/mvtec/bottle/test/broken_large/000.png", "gt": 1},
        {"cat": "bottle", "path": "G:/My Drive/DefectVisionAI/dataset/raw/mvtec/bottle/test/good/000.png", "gt": 0},
        {"cat": "cable", "path": "G:/My Drive/DefectVisionAI/dataset/raw/mvtec/cable/test/bent_wire/000.png", "gt": 1},
        {"cat": "cable", "path": "G:/My Drive/DefectVisionAI/dataset/raw/mvtec/cable/test/good/000.png", "gt": 0},
        {"cat": "carpet", "path": "G:/My Drive/DefectVisionAI/dataset/raw/mvtec/carpet/test/hole/000.png", "gt": 1},
        {"cat": "carpet", "path": "G:/My Drive/DefectVisionAI/dataset/raw/mvtec/carpet/test/good/000.png", "gt": 0}
    ]

    perturbations = [
        {"name": "clean", "type": "none", "param": 0},
        {"name": "noise_sigma_0.05", "type": "gaussian_noise", "param": 0.05},
        {"name": "noise_sigma_0.10", "type": "gaussian_noise", "param": 0.10},
        {"name": "brightness_+20%", "type": "brightness", "param": 1.20},
        {"name": "brightness_-20%", "type": "brightness", "param": 0.80},
        {"name": "contrast_+20%", "type": "contrast", "param": 1.20},
        {"name": "contrast_-20%", "type": "contrast", "param": 0.80},
        {"name": "blur_sigma_1.0", "type": "blur", "param": 1.0},
        {"name": "rotation_+5deg", "type": "rotation", "param": 5.0},
        {"name": "rotation_-5deg", "type": "rotation", "param": -5.0}
    ]

    # Preload memory banks
    pc_models = {}
    for spec in test_specs:
        cat = spec["cat"]
        if cat not in pc_models:
            m = PatchCoreModel()
            m.load(f"DefectVisionAI/models/patchcore/{cat}/memory_bank.npy", grid_size=28)
            pc_models[cat] = m

    records = []
    for spec in test_specs:
        cat = spec["cat"]
        p = spec["path"]
        gt = spec["gt"]
        baseline = baseline_lookup[cat]
        thresh = float(round(baseline["baseline_p99"], 4))
        pc_m = pc_models[cat]

        img_bgr = cv2.imread(p)
        if img_bgr is None:
            continue
        img_rgb_clean = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

        for pert in perturbations:
            img_pert_rgb = apply_perturbation(img_rgb_clean, pert["type"], pert["param"])

            # PatchCore
            img_pc = cv2.resize(img_pert_rgb, (224, 224)).astype(np.float32) / 255.0
            img_pc = (img_pc - PC_MEAN) / PC_STD
            pc_tensor = torch.from_numpy(img_pc).permute(2, 0, 1).float().unsqueeze(0).to(device)

            with torch.no_grad():
                emb = extractor(pc_tensor)[0].cpu().numpy()
            dist_map, raw_score = pc_m.score(emb)
            dist_map_norm = normalize_map(dist_map)
            defect_area_pct = float(100.0 * (dist_map_norm >= 0.5).sum() / dist_map_norm.size)
            anomaly_norm = float(normalize_anomaly_score(raw_score, baseline["baseline_mean"], baseline["baseline_p99"]))
            pc_pred = 1 if (raw_score > thresh) else 0

            # EfficientNet
            eff_tensor = eff_transform(image=img_pert_rgb)["image"].unsqueeze(0).to(device)
            with torch.no_grad():
                out = effnet(eff_tensor)
                prob = float(F.softmax(out, dim=1)[0, 1].item())
            eff_pred = 1 if (prob >= 0.50) else 0

            hybrid_pred = 1 if (pc_pred == 1 or eff_pred == 1) else 0
            conf = float(round(prob * 100, 2))
            sev = float(round(compute_severity_score(anomaly_norm, defect_area_pct, conf), 2))

            records.append({
                "category": cat,
                "specimen": os.path.basename(p),
                "ground_truth": gt,
                "perturbation": pert["name"],
                "raw_patchcore_score": float(round(raw_score, 4)),
                "patchcore_pred": pc_pred,
                "effnet_prob": float(round(prob, 4)),
                "effnet_pred": eff_pred,
                "hybrid_pred": hybrid_pred,
                "severity_score": sev,
                "correct_hybrid": (hybrid_pred == gt)
            })

    df = pd.DataFrame(records)
    out_csv = "release/final_18h_validation/robustness_results.csv"
    df.to_csv(out_csv, index=False)
    print(f"Robustness results saved to {out_csv}")

    # Summary table
    agg = df.groupby("perturbation").agg(
        mean_pc_score=("raw_patchcore_score", "mean"),
        mean_eff_prob=("effnet_prob", "mean"),
        hybrid_accuracy=("correct_hybrid", "mean")
    ).reset_index()
    print("\n--- ROBUSTNESS SUMMARY ---")
    print(agg.to_string())

if __name__ == "__main__":
    run_robustness()
