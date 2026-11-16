#!/usr/bin/env python3
"""
DefectVision AI — Official MVTec AD Dataset Integrity Auditor
Scans all 15 MVTec AD categories, validates directory structures, image dimensions,
file formats, ground-truth mask alignment, and compares against official benchmark standards.
"""

import os
import sys
import glob
import json
from PIL import Image
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_ROOT = os.path.join(PROJECT_ROOT, "DefectVisionAI", "dataset", "raw", "mvtec")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "release", "dataset_integrity")
os.makedirs(OUTPUT_DIR, exist_ok=True)

OFFICIAL_CATEGORIES = {
    # Objects
    "bottle": {"type": "object", "train_good": 209, "test_good": 20, "test_defect": 63, "defects": 3},
    "cable": {"type": "object", "train_good": 224, "test_good": 58, "test_defect": 92, "defects": 8},
    "capsule": {"type": "object", "train_good": 219, "test_good": 23, "test_defect": 109, "defects": 5},
    "hazelnut": {"type": "object", "train_good": 391, "test_good": 40, "test_defect": 70, "defects": 4},
    "metal_nut": {"type": "object", "train_good": 220, "test_good": 22, "test_defect": 93, "defects": 4},
    "pill": {"type": "object", "train_good": 267, "test_good": 26, "test_defect": 141, "defects": 9},
    "screw": {"type": "object", "train_good": 320, "test_good": 41, "test_defect": 119, "defects": 5},
    "toothbrush": {"type": "object", "train_good": 60, "test_good": 12, "test_defect": 30, "defects": 1},
    "transistor": {"type": "object", "train_good": 213, "test_good": 60, "test_defect": 40, "defects": 4},
    "zipper": {"type": "object", "train_good": 240, "test_good": 32, "test_defect": 119, "defects": 7},
    # Textures
    "carpet": {"type": "texture", "train_good": 280, "test_good": 28, "test_defect": 89, "defects": 5},
    "grid": {"type": "texture", "train_good": 264, "test_good": 21, "test_defect": 57, "defects": 5},
    "leather": {"type": "texture", "train_good": 245, "test_good": 32, "test_defect": 92, "defects": 5},
    "tile": {"type": "texture", "train_good": 230, "test_good": 33, "test_defect": 84, "defects": 5},
    "wood": {"type": "texture", "train_good": 247, "test_good": 19, "test_defect": 60, "defects": 5},
}

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".PNG", ".JPG", ".JPEG"}

def get_images(folder):
    if not os.path.isdir(folder):
        return []
    return [
        os.path.join(folder, f) for f in os.listdir(folder)
        if os.path.splitext(f)[1] in IMAGE_EXTENSIONS and not f.startswith(".")
    ]

def audit_dataset():
    print(f"Auditing MVTec AD dataset at: {DATA_ROOT}", flush=True)
    audit_records = []
    defect_details = {}
    missing_files = []
    unreadable_files = []

    for cat, meta in OFFICIAL_CATEGORIES.items():
        cat_dir = os.path.join(DATA_ROOT, cat)
        if not os.path.exists(cat_dir):
            print(f"[ERROR] Category directory missing: {cat_dir}", flush=True)
            missing_files.append(cat)
            continue

        train_good = sorted(get_images(os.path.join(cat_dir, "train", "good")))
        test_good = sorted(get_images(os.path.join(cat_dir, "test", "good")))
        
        test_dir = os.path.join(cat_dir, "test")
        test_defect_dirs = sorted([
            os.path.join(test_dir, d) for d in os.listdir(test_dir)
            if os.path.isdir(os.path.join(test_dir, d)) and d != "good"
        ])
        defect_types = [os.path.basename(d) for d in test_defect_dirs]
        
        test_defect_images = []
        for d in test_defect_dirs:
            imgs = sorted(get_images(d))
            test_defect_images.extend(imgs)
            defect_name = os.path.basename(d)
            defect_details[f"{cat}/{defect_name}"] = len(imgs)

        gt_dir = os.path.join(cat_dir, "ground_truth")
        gt_masks = []
        if os.path.isdir(gt_dir):
            for d in os.listdir(gt_dir):
                d_path = os.path.join(gt_dir, d)
                if os.path.isdir(d_path):
                    gt_masks.extend(get_images(d_path))

        # Inspect image dimensions and validity on sample images
        dims = set()
        formats = set()
        modes = set()
        
        sample_images = train_good[:3] + test_good[:3] + test_defect_images[:5]
        for img_path in sample_images:
            try:
                with Image.open(img_path) as im:
                    dims.add(f"{im.size[0]}x{im.size[1]}")
                    formats.add(im.format)
                    modes.add(im.mode)
            except Exception as e:
                unreadable_files.append((img_path, str(e)))

        # Verify ground truth alignment for defect images
        unmatched_gt = 0
        for img_path in test_defect_images:
            defect_type = os.path.basename(os.path.dirname(img_path))
            stem = os.path.splitext(os.path.basename(img_path))[0]
            expected_gt = os.path.join(cat_dir, "ground_truth", defect_type, f"{stem}_mask.png")
            if not os.path.exists(expected_gt):
                unmatched_gt += 1

        record = {
            "category": cat,
            "type": meta["type"],
            "train_good": len(train_good),
            "expected_train_good": meta["train_good"],
            "train_match": len(train_good) == meta["train_good"],
            "test_good": len(test_good),
            "expected_test_good": meta["test_good"],
            "test_good_match": len(test_good) == meta["test_good"],
            "test_defect": len(test_defect_images),
            "expected_test_defect": meta["test_defect"],
            "test_defect_match": len(test_defect_images) == meta["test_defect"],
            "defect_types": len(defect_types),
            "expected_defect_types": meta["defects"],
            "defect_types_list": defect_types,
            "gt_masks": len(gt_masks),
            "unmatched_gt": unmatched_gt,
            "resolutions": sorted(list(dims)),
            "formats": sorted(list(formats)),
            "color_modes": sorted(list(modes))
        }
        audit_records.append(record)
        is_pass = record["train_match"] and record["test_good_match"] and record["test_defect_match"] and record["unmatched_gt"] == 0
        print(f"  [{'PASS' if is_pass else 'FAIL'}] {cat:<12} | "
              f"train={len(train_good):>3}/{meta['train_good']:>3} | "
              f"test_good={len(test_good):>2}/{meta['test_good']:>2} | "
              f"test_defect={len(test_defect_images):>3}/{meta['test_defect']:>3} | "
              f"defects={len(defect_types)}/{meta['defects']} | "
              f"gt={len(gt_masks):>3} | dims={list(dims)}", flush=True)

    df = pd.DataFrame(audit_records)
    csv_path = os.path.join(OUTPUT_DIR, "mvtec_dataset_audit.csv")
    df.to_csv(csv_path, index=False)
    print(f"\nAudit saved to: {csv_path}", flush=True)

    # Generate Markdown Report
    md_path = os.path.join(OUTPUT_DIR, "mvtec_dataset_integrity_report.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# DefectVision AI — Official MVTec AD Dataset Integrity Audit Report\n\n")
        f.write("**Reference:** Paul Bergmann et al., 'MVTec AD — A Comprehensive Real-World Dataset for Unsupervised Anomaly Detection', CVPR 2019 / IJCV 2021.\n\n")
        f.write("**License:** Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0).\n\n")
        f.write(f"**Dataset Location:** `{DATA_ROOT}`\n\n")
        f.write("## 1. Summary of All 15 Categories\n\n")
        f.write("| Category | Type | Train (Good) | Test (Good) | Test (Defect) | Total Test | Defect Types | GT Masks | Resolution | Formats | Status |\n")
        f.write("|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|\n")
        
        tot_train = tot_tg = tot_td = tot_masks = 0
        all_passed = True
        for r in audit_records:
            tot_train += r["train_good"]
            tot_tg += r["test_good"]
            tot_td += r["test_defect"]
            tot_masks += r["gt_masks"]
            status = "VERIFIED" if (r["train_match"] and r["test_good_match"] and r["test_defect_match"] and r["unmatched_gt"] == 0) else "MISMATCH"
            if status != "VERIFIED":
                all_passed = False
            f.write(f"| `{r['category']}` | {r['type']} | {r['train_good']} | {r['test_good']} | {r['test_defect']} | {r['test_good'] + r['test_defect']} | {r['defect_types']} | {r['gt_masks']} | {', '.join(r['resolutions'])} | {', '.join(r['formats'])} | **{status}** |\n")

        f.write(f"| **TOTAL** | **15 Categories** | **{tot_train}** | **{tot_tg}** | **{tot_td}** | **{tot_tg + tot_td}** | **-** | **{tot_masks}** | - | - | **{'100% VERIFIED' if all_passed else 'ACTION REQUIRED'}** |\n\n")

        f.write("## 2. Benchmark Concordance Verification\n\n")
        f.write(f"- **Expected Total Train Images:** 3,629 nominal images across 15 categories.\n")
        f.write(f"- **Audited Total Train Images:** {tot_train} nominal images.\n")
        f.write(f"- **Expected Total Test Images:** 1,725 images (467 nominal, 1,258 defective).\n")
        f.write(f"- **Audited Total Test Images:** {tot_tg + tot_td} images ({tot_tg} nominal, {tot_td} defective).\n")
        f.write(f"- **Expected Total Ground-Truth Masks:** Exactly equal to defective test images ({tot_td}).\n")
        f.write(f"- **Audited Total Ground-Truth Masks:** {tot_masks}.\n")
        f.write(f"- **Unreadable/Corrupted Images:** {len(unreadable_files)}.\n")
        f.write(f"- **Missing Category Folders:** {len(missing_files)}.\n\n")

        f.write("## 3. Defect-Type Breakdown per Category\n\n")
        for r in audit_records:
            f.write(f"### `{r['category']}` ({r['type'].upper()})\n")
            f.write(f"- **Train Good:** {r['train_good']}\n")
            f.write(f"- **Test Good:** {r['test_good']}\n")
            f.write(f"- **Defect Classes ({len(r['defect_types_list'])}):** {', '.join(r['defect_types_list'])}\n")
            for dt in r["defect_types_list"]:
                count = defect_details.get(f"{r['category']}/{dt}", 0)
                f.write(f"  - `{dt}`: {count} test images\n")
            f.write("\n")

    print(f"Markdown report generated: {md_path}", flush=True)
    return all_passed

if __name__ == "__main__":
    success = audit_dataset()
    sys.exit(0 if success else 1)
