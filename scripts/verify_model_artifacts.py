import os
import sys
import hashlib
import json
import numpy as np
import pandas as pd
import torch
import torchvision.models as models
import cv2
import faiss
import timm

def get_file_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def verify_artifacts(models_dir, reports_dir):
    print("=== STEP 1: VERIFYING MODEL ARTIFACTS ===")
    artifacts_report = []

    # 1. PatchCore memory banks
    pc_dir = os.path.join(models_dir, "patchcore")
    categories = sorted(os.listdir(pc_dir)) if os.path.exists(pc_dir) else []
    print(f"Found {len(categories)} PatchCore categories in {pc_dir}")
    
    for cat in categories:
        mb_path = os.path.join(pc_dir, cat, "memory_bank.npy")
        if os.path.exists(mb_path):
            size = os.path.getsize(mb_path)
            sha = get_file_sha256(mb_path)
            data = np.load(mb_path)
            shape = data.shape
            artifacts_report.append({
                "category": cat,
                "artifact": "patchcore_memory_bank",
                "path": mb_path,
                "size_bytes": size,
                "sha256": sha,
                "shape": f"{shape[0]}x{shape[1]}",
                "dtype": str(data.dtype)
            })
            print(f"  [PatchCore] {cat:12s}: shape={shape}, size={size:,} bytes, sha256={sha[:12]}...")
        else:
            print(f"  [PatchCore] {cat:12s}: MISSING memory_bank.npy")

    # 2. EfficientNet-B0 v3
    eff_ckpt_path = os.path.join(models_dir, "efficientnet_baseline_v3", "best_model.pt")
    if os.path.exists(eff_ckpt_path):
        size = os.path.getsize(eff_ckpt_path)
        sha = get_file_sha256(eff_ckpt_path)
        ckpt = torch.load(eff_ckpt_path, map_location="cpu")
        state_keys = len(ckpt.get("model_state", {}))
        artifacts_report.append({
            "category": "all (classifier)",
            "artifact": "efficientnet_b0_v3",
            "path": eff_ckpt_path,
            "size_bytes": size,
            "sha256": sha,
            "shape": f"{state_keys} tensor keys",
            "dtype": "torch.state_dict"
        })
        print(f"  [EfficientNet-B0 v3]: keys={state_keys}, size={size:,} bytes, sha256={sha[:12]}...")

    # 3. Baselines
    baseline_csv = os.path.join(reports_dir, "step9_severity_baselines.csv")
    if os.path.exists(baseline_csv):
        df = pd.read_csv(baseline_csv)
        size = os.path.getsize(baseline_csv)
        sha = get_file_sha256(baseline_csv)
        artifacts_report.append({
            "category": "all",
            "artifact": "severity_baselines",
            "path": baseline_csv,
            "size_bytes": size,
            "sha256": sha,
            "shape": f"{len(df)} rows",
            "dtype": "csv"
        })
        print(f"  [Baselines CSV]: {len(df)} categories, size={size:,} bytes, sha256={sha[:12]}...")

    df_art = pd.DataFrame(artifacts_report)
    df_art.to_csv("release/final_18h_validation/verified_model_artifacts.csv", index=False)
    print("Saved verified_model_artifacts.csv\n")
    return df_art

if __name__ == "__main__":
    models_dir = os.path.abspath("DefectVisionAI/models")
    reports_dir = os.path.abspath("DefectVisionAI/reports")
    verify_artifacts(models_dir, reports_dir)
