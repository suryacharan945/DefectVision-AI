#!/usr/bin/env python3
"""
DefectVision AI — Official MVTec AD Deterministic Split Manifest Generator
Partitions normal training images into Registration (80%) and Calibration/Validation (20%)
using stratified random sampling with SEED=42.
The official MVTec test set (1,725 images) is quarantined strictly for evaluation.
"""

import os
import sys
import json
import pandas as pd
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_ROOT = os.path.join(PROJECT_ROOT, "DefectVisionAI", "dataset", "raw", "mvtec")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "release", "dataset_manifests")
os.makedirs(OUTPUT_DIR, exist_ok=True)

CATEGORIES = [
    "bottle", "cable", "capsule", "carpet", "grid",
    "hazelnut", "leather", "metal_nut", "pill", "screw",
    "tile", "toothbrush", "transistor", "wood", "zipper"
]

CATEGORY_TYPE = {
    "bottle": "object", "cable": "object", "capsule": "object", "carpet": "texture",
    "grid": "texture", "hazelnut": "object", "leather": "texture", "metal_nut": "object",
    "pill": "object", "screw": "object", "tile": "texture", "toothbrush": "object",
    "transistor": "object", "wood": "texture", "zipper": "object"
}

SEED = 42
TRAIN_RATIO = 0.80

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".PNG", ".JPG", ".JPEG"}

def get_image_files(folder):
    if not os.path.isdir(folder):
        return []
    return sorted([
        os.path.join(folder, f) for f in os.listdir(folder)
        if os.path.splitext(f)[1] in IMAGE_EXTENSIONS and not f.startswith(".")
    ])

def generate_splits():
    print(f"Generating deterministic splits (SEED={SEED}, TRAIN_RATIO={TRAIN_RATIO})", flush=True)
    rng = np.random.RandomState(SEED)

    reg_records = []
    cal_records = []
    test_records = []

    cat_to_id = {cat: idx for idx, cat in enumerate(CATEGORIES)}
    
    # Save category mapping
    mapping_path = os.path.join(OUTPUT_DIR, "category_mapping.json")
    with open(mapping_path, "w", encoding="utf-8") as f:
        json.dump({
            "categories": CATEGORIES,
            "category_to_id": cat_to_id,
            "id_to_category": {v: k for k, v in cat_to_id.items()},
            "category_types": CATEGORY_TYPE
        }, f, indent=2)

    summary_rows = []

    for cat in CATEGORIES:
        cat_dir = os.path.join(DATA_ROOT, cat)
        cat_id = cat_to_id[cat]
        cat_type = CATEGORY_TYPE[cat]

        # 1. Normal Train Images
        train_good_files = get_image_files(os.path.join(cat_dir, "train", "good"))
        n_total_train = len(train_good_files)
        
        # Shuffle deterministically
        indices = rng.permutation(n_total_train)
        n_reg = int(round(n_total_train * TRAIN_RATIO))
        reg_indices = indices[:n_reg]
        cal_indices = indices[n_reg:]

        for idx in reg_indices:
            reg_records.append({
                "filepath": train_good_files[idx],
                "rel_path": os.path.relpath(train_good_files[idx], PROJECT_ROOT),
                "category": cat,
                "category_id": cat_id,
                "category_type": cat_type,
                "split": "train_registration",
                "is_defect": 0,
                "defect_type": "good"
            })

        for idx in cal_indices:
            cal_records.append({
                "filepath": train_good_files[idx],
                "rel_path": os.path.relpath(train_good_files[idx], PROJECT_ROOT),
                "category": cat,
                "category_id": cat_id,
                "category_type": cat_type,
                "split": "calibration_validation",
                "is_defect": 0,
                "defect_type": "good"
            })

        # 2. Official Test Images (Quarantined)
        # Test Good
        test_good_files = get_image_files(os.path.join(cat_dir, "test", "good"))
        for f in test_good_files:
            test_records.append({
                "filepath": f,
                "rel_path": os.path.relpath(f, PROJECT_ROOT),
                "category": cat,
                "category_id": cat_id,
                "category_type": cat_type,
                "split": "official_test",
                "is_defect": 0,
                "defect_type": "good",
                "has_gt_mask": False,
                "gt_mask_path": ""
            })

        # Test Defective
        test_dir = os.path.join(cat_dir, "test")
        defect_subdirs = sorted([
            d for d in os.listdir(test_dir)
            if os.path.isdir(os.path.join(test_dir, d)) and d != "good"
        ])

        n_defects_cat = 0
        for d in defect_subdirs:
            defect_files = get_image_files(os.path.join(test_dir, d))
            n_defects_cat += len(defect_files)
            for f in defect_files:
                stem = os.path.splitext(os.path.basename(f))[0]
                mask_path = os.path.join(cat_dir, "ground_truth", d, f"{stem}_mask.png")
                has_mask = os.path.exists(mask_path)
                test_records.append({
                    "filepath": f,
                    "rel_path": os.path.relpath(f, PROJECT_ROOT),
                    "category": cat,
                    "category_id": cat_id,
                    "category_type": cat_type,
                    "split": "official_test",
                    "is_defect": 1,
                    "defect_type": d,
                    "has_gt_mask": has_mask,
                    "gt_mask_path": mask_path if has_mask else ""
                })

        summary_rows.append({
            "category": cat,
            "type": cat_type,
            "train_total": n_total_train,
            "registration_80%": len(reg_indices),
            "calibration_20%": len(cal_indices),
            "test_good": len(test_good_files),
            "test_defect": n_defects_cat,
            "test_total": len(test_good_files) + n_defects_cat
        })

    # Save dataframes
    df_reg = pd.DataFrame(reg_records)
    df_cal = pd.DataFrame(cal_records)
    df_test = pd.DataFrame(test_records)
    df_summary = pd.DataFrame(summary_rows)

    reg_csv = os.path.join(OUTPUT_DIR, "patchcore_registration_split.csv")
    cal_csv = os.path.join(OUTPUT_DIR, "patchcore_calibration_split.csv")
    test_csv = os.path.join(OUTPUT_DIR, "official_test_split.csv")
    summary_csv = os.path.join(OUTPUT_DIR, "dataset_splits_summary.csv")

    df_reg.to_csv(reg_csv, index=False)
    df_cal.to_csv(cal_csv, index=False)
    df_test.to_csv(test_csv, index=False)
    df_summary.to_csv(summary_csv, index=False)

    # Combined classification sets
    cls_train_csv = os.path.join(OUTPUT_DIR, "category_classifier_train_split.csv")
    cls_val_csv = os.path.join(OUTPUT_DIR, "category_classifier_val_split.csv")
    df_reg.to_csv(cls_train_csv, index=False)
    df_cal.to_csv(cls_val_csv, index=False)

    metadata = {
        "random_seed": SEED,
        "train_registration_ratio": TRAIN_RATIO,
        "calibration_validation_ratio": round(1.0 - TRAIN_RATIO, 2),
        "total_normal_train_images": len(df_reg) + len(df_cal),
        "registration_images": len(df_reg),
        "calibration_images": len(df_cal),
        "quarantined_test_images": len(df_test),
        "test_normal_images": int((df_test["is_defect"] == 0).sum()),
        "test_defect_images": int((df_test["is_defect"] == 1).sum()),
        "generated_timestamp": pd.Timestamp.now().isoformat()
    }
    meta_path = os.path.join(OUTPUT_DIR, "dataset_splits_metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print("\n=== Split Generation Summary ===")
    print(f"Registration (Train): {len(df_reg)} images")
    print(f"Calibration (Val):   {len(df_cal)} images")
    print(f"Official Test:       {len(df_test)} images ({metadata['test_normal_images']} normal, {metadata['test_defect_images']} defect)")
    print(f"All files saved to: {OUTPUT_DIR}")

if __name__ == "__main__":
    generate_splits()
