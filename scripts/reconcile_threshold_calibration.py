"""
DefectVision AI 2.2 — Threshold Calibration Reconciliation Script
Resolves the provenance and statistical contradictions for bottle_sku_btl_adapt_002.
Outputs:
- release/experiments/threshold_provenance.csv
- release/experiments/threshold_comparison.csv
- release/experiments/calibration_score_distribution.png
- release/experiments/false_positive_vs_threshold.png
"""

import os
import sys
import hashlib
import json
import numpy as np
import pandas as pd
import cv2
import torch
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "DefectVisionAI"))

from src.patchcore import PatchCoreExtractor
from src.production_profile_service import ProductionProfileService

def sha256_file(path):
    if not os.path.exists(path):
        return "FILE_NOT_FOUND"
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def wilson_score_interval(k, n, confidence=0.95):
    """Computes Wilson score binomial confidence interval for k successes in n trials."""
    if n == 0:
        return 0.0, 1.0
    z = 1.95996  # 95% confidence
    p_hat = k / n
    denominator = 1 + z**2 / n
    center = (p_hat + z**2 / (2 * n)) / denominator
    spread = z * np.sqrt(p_hat * (1 - p_hat) / n + z**2 / (4 * n**2)) / denominator
    lower = max(0.0, center - spread)
    upper = min(1.0, center + spread)
    return lower, upper

def main():
    print("=" * 80)
    print("DEFECTVISION AI 2.2 — THRESHOLD CALIBRATION RECONCILIATION")
    print("=" * 80)

    profile_service = ProductionProfileService()
    extractor = PatchCoreExtractor(grid_size=28)
    extractor.eval()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    extractor.to(device)

    PC_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    PC_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)

    model_adapt = profile_service.get_profile_model("bottle_sku_btl_adapt_002")
    prof_adapt = profile_service.get_profile("bottle_sku_btl_adapt_002")

    if not model_adapt:
        print("ERROR: Could not load model for bottle_sku_btl_adapt_002!")
        return

    # 1. Compile complete threshold provenance:
    # A. The 2 calibration images used to set threshold 1.6410
    # B. The 5 training images used to build the memory bank
    # C. The 30 nominal images evaluated in scripts/audit_threshold_calibration.py
    
    provenance_rows = []

    # Category A: Calibration set (used to set 1.6410)
    cal_files = [
        ("CAL-STA01-TRN-003", os.path.join(PROJECT_ROOT, "data", "station_01", "train_normal", "station01_normal_train_003.png"), "NORMAL_CALIBRATION", "PHYS_SOURCE_MVTEC_BOTTLE_NOMINAL_JITTER", True),
        ("CAL-STA01-TRN-004", os.path.join(PROJECT_ROOT, "data", "station_01", "train_normal", "station01_normal_train_004.png"), "NORMAL_CALIBRATION", "PHYS_SOURCE_MVTEC_BOTTLE_NOMINAL_JITTER", True)
    ]

    # Category B: Training set (used to build memory bank)
    train_files = [
        ("TRN-EXT-BTL-001", r"c:\Users\surya\Downloads\clear bottle.jpg", "MEMORY_BANK_TRAIN", "PHYS_SPECIMEN_EXT_BTL_A", False),
        ("TRN-EXT-BTL-002", r"c:\Users\surya\Downloads\clear bottle2.webp", "MEMORY_BANK_TRAIN", "PHYS_SPECIMEN_EXT_BTL_B", False),
        ("TRN-STA01-TRN-000", os.path.join(PROJECT_ROOT, "data", "station_01", "train_normal", "station01_normal_train_000.png"), "MEMORY_BANK_TRAIN", "PHYS_SOURCE_MVTEC_BOTTLE_NOMINAL_JITTER", False),
        ("TRN-STA01-TRN-001", os.path.join(PROJECT_ROOT, "data", "station_01", "train_normal", "station01_normal_train_001.png"), "MEMORY_BANK_TRAIN", "PHYS_SOURCE_MVTEC_BOTTLE_NOMINAL_JITTER", False),
        ("TRN-STA01-TRN-002", os.path.join(PROJECT_ROOT, "data", "station_01", "train_normal", "station01_normal_train_002.png"), "MEMORY_BANK_TRAIN", "PHYS_SOURCE_MVTEC_BOTTLE_NOMINAL_JITTER", False)
    ]

    # Category C: The 30 nominal images from audit_threshold_calibration.py
    # 20 MVTec good test images
    mvtec_good_dir = os.path.join(PROJECT_ROOT, "DefectVisionAI", "dataset", "raw", "mvtec", "bottle", "test", "good")
    mvtec_files = []
    if os.path.exists(mvtec_good_dir):
        for f in sorted(os.listdir(mvtec_good_dir)):
            if f.endswith(".png"):
                mvtec_files.append((f"AUDIT-MVTEC-GOOD-{f[:3]}", os.path.join(mvtec_good_dir, f), "FINAL_TEST", f"PHYS_MVTEC_BOTTLE_{f[:3]}", False))

    # 10 Station 01 val_normal images
    station_val_dir = os.path.join(PROJECT_ROOT, "data", "station_01", "val_normal")
    station_files = []
    if os.path.exists(station_val_dir):
        for f in sorted(os.listdir(station_val_dir))[:10]:
            if f.endswith(".png"):
                idx = f.replace("station01_normal_val_", "").replace(".png", "")
                part = "NORMAL_CALIBRATION" if int(idx) < 5 else "VALIDATION"
                station_files.append((f"AUDIT-STA01-VAL-{idx}", os.path.join(station_val_dir, f), part, "PHYS_SOURCE_MVTEC_BOTTLE_NOMINAL_JITTER", False))

    all_provenance_entries = cal_files + train_files + mvtec_files + station_files

    print(f"\nScoring {len(all_provenance_entries)} provenance entries with bottle_sku_btl_adapt_002...")

    for img_id, path, partition, phys_id, used_for_thresh in all_provenance_entries:
        h_val = sha256_file(path)
        img_bgr = cv2.imread(path)
        if img_bgr is None:
            score = np.nan
        else:
            rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            resized = cv2.resize(rgb, (224, 224)).astype(np.float32) / 255.0
            norm = (resized - PC_MEAN) / PC_STD
            t = torch.from_numpy(norm).permute(2, 0, 1).unsqueeze(0).float().to(device)
            with torch.no_grad():
                fused = extractor(t)[0].cpu().numpy()
            _, sc = model_adapt.score(fused)
            score = float(sc)

        provenance_rows.append({
            "image_id": img_id,
            "filename": os.path.basename(path),
            "sha256": h_val,
            "physical_specimen_id": phys_id,
            "domain": "Domain B: Studio" if "EXT" in img_id else ("Domain A: MVTec" if "MVTEC" in img_id else "Domain D: Station01 Jitter"),
            "dataset_partition": partition,
            "patchcore_score": round(score, 4),
            "used_for_threshold_selection": used_for_thresh,
            "exceeds_provisional_1_6410": bool(score >= 1.6410)
        })

    df_prov = pd.DataFrame(provenance_rows)
    prov_csv_path = "release/experiments/threshold_provenance.csv"
    df_prov.to_csv(prov_csv_path, index=False)
    print(f"Saved threshold provenance table to: {prov_csv_path} ({len(df_prov)} rows)")

    # 2. Reconcile the 30-image audit distribution vs N=2 calibration
    df_audit30 = df_prov[df_prov['image_id'].str.startswith("AUDIT-")]
    audit_scores = df_audit30['patchcore_score'].dropna().values

    print("\n--- Summary of 30 Audit Images (Cross-Domain Nominal) ---")
    print(f"Count: {len(audit_scores)}")
    print(f"Mean:   {np.mean(audit_scores):.4f}")
    print(f"Std:    {np.std(audit_scores):.4f}")
    print(f"Min:    {np.min(audit_scores):.4f}")
    print(f"Max:    {np.max(audit_scores):.4f}")
    print(f"P50:    {np.percentile(audit_scores, 50):.4f}")
    print(f"P90:    {np.percentile(audit_scores, 90):.4f}")
    print(f"P95:    {np.percentile(audit_scores, 95):.4f}")
    print(f"P99:    {np.percentile(audit_scores, 99):.4f}")

    # Candidate Threshold Comparison Matrix
    policies = [
        ("Current Provisional (N=2 Calib)", 1.6410, "Derived from max of 2 calibration frames (1.5610) * 1.15 fallback"),
        ("Empirical P90 (30 cross-domain)", float(np.percentile(audit_scores, 90)), "90th percentile of 30 cross-domain nominals"),
        ("Empirical P95 (30 cross-domain)", float(np.percentile(audit_scores, 95)), "95th percentile of 30 cross-domain nominals"),
        ("Empirical P99 (30 cross-domain)", float(np.percentile(audit_scores, 99)), "99th percentile of 30 cross-domain nominals"),
        ("Parametric Mean + 3*Std", float(np.mean(audit_scores) + 3.0 * np.std(audit_scores)), "Normal approximation at 99.73% containment"),
        ("Max Observed + Margin", float(np.max(audit_scores) + 0.10), "Max observed cross-domain score + 0.10 buffer")
    ]

    comp_rows = []
    total_n = len(audit_scores)
    for name, thresh, desc in policies:
        fp = int(np.sum(audit_scores >= thresh))
        tn = total_n - fp
        fpr = fp / total_n
        ci_low, ci_high = wilson_score_interval(fp, total_n, confidence=0.95)
        comp_rows.append({
            "threshold_policy": name,
            "threshold_value": round(thresh, 4),
            "total_normal_evaluated": total_n,
            "true_negatives": tn,
            "false_positives": fp,
            "empirical_fpr": round(fpr, 4),
            "empirical_fpr_pct": round(fpr * 100, 2),
            "wilson_95ci_low_pct": round(ci_low * 100, 2),
            "wilson_95ci_high_pct": round(ci_high * 100, 2),
            "statistical_status": "PROVISIONAL HEURISTIC" if "Provisional" in name else "EMPIRICAL ESTIMATE (UNGUARANTEED)",
            "description": desc
        })

    df_comp = pd.DataFrame(comp_rows)
    comp_csv_path = "release/experiments/threshold_comparison.csv"
    df_comp.to_csv(comp_csv_path, index=False)
    print(f"\nSaved threshold comparison matrix to: {comp_csv_path}")
    print(df_comp[['threshold_policy', 'threshold_value', 'false_positives', 'empirical_fpr_pct', 'wilson_95ci_low_pct', 'wilson_95ci_high_pct']])

    # 3. Generate Visual Plots
    # Plot A: Calibration Score Distribution
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(audit_scores, bins=15, color='#3B82F6', edgecolor='#1D4ED8', alpha=0.75, label='30 Audit Normals (MVTec + Station01)')
    
    # Mark the 2 calibration samples
    cal_scores = df_prov[df_prov['used_for_threshold_selection'] == True]['patchcore_score'].values
    ax.scatter(cal_scores, [1, 1], color='#EF4444', s=120, zorder=5, label=f'N=2 Calibration Samples (Scores: {cal_scores.tolist()})')

    # Mark thresholds
    ax.axvline(1.6410, color='#DC2626', linestyle='--', linewidth=2, label='Current Provisional Threshold (1.6410)')
    ax.axvline(np.percentile(audit_scores, 95), color='#F59E0B', linestyle='-.', linewidth=2, label=f'Audit P95 ({np.percentile(audit_scores, 95):.4f})')
    ax.axvline(np.percentile(audit_scores, 99), color='#10B981', linestyle=':', linewidth=2, label=f'Audit P99 ({np.percentile(audit_scores, 99):.4f})')

    ax.set_title("PatchCore Distance Distribution for bottle_sku_btl_adapt_002\nCalibration Samples vs. 30 Cross-Domain Held-Out Normals", fontsize=12, fontweight='bold')
    ax.set_xlabel("PatchCore Anomaly Distance", fontsize=11)
    ax.set_ylabel("Specimen Count", fontsize=11)
    ax.legend(loc='upper right', frameon=True)
    ax.grid(True, linestyle='--', alpha=0.5)

    plot_dist_path = "release/experiments/calibration_score_distribution.png"
    plt.tight_layout()
    plt.savefig(plot_dist_path, dpi=200)
    plt.close()
    print(f"Saved distribution plot to: {plot_dist_path}")

    # Plot B: False Positive Rate vs Threshold
    thresh_range = np.linspace(1.2, 3.2, 200)
    fpr_curve = [(np.sum(audit_scores >= t) / total_n) * 100.0 for t in thresh_range]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(thresh_range, fpr_curve, color='#4F46E5', linewidth=2.5, label='Empirical False Positive Rate (%) on 30 Audit Normals')
    ax.axvline(1.6410, color='#DC2626', linestyle='--', linewidth=2, label='Current Provisional Thresh (1.6410, FPR=63.3%)')
    ax.axhline(63.33, color='#DC2626', linestyle=':', alpha=0.7)
    ax.axvline(np.percentile(audit_scores, 95), color='#F59E0B', linestyle='-.', linewidth=2, label=f'Audit P95 Thresh ({np.percentile(audit_scores, 95):.4f}, FPR=6.7%)')
    ax.axvline(np.percentile(audit_scores, 99), color='#10B981', linestyle=':', linewidth=2, label=f'Audit P99 Thresh ({np.percentile(audit_scores, 99):.4f}, FPR=3.3%)')

    ax.set_title("False Positive Rate vs. Anomaly Threshold (Operating Characteristic)\nEvaluated on Cross-Domain Nominal Specimens", fontsize=12, fontweight='bold')
    ax.set_xlabel("Threshold Value", fontsize=11)
    ax.set_ylabel("Empirical False Positive Rate (%)", fontsize=11)
    ax.set_ylim(-2, 105)
    ax.legend(loc='upper right', frameon=True)
    ax.grid(True, linestyle='--', alpha=0.5)

    plot_fpr_path = "release/experiments/false_positive_vs_threshold.png"
    plt.tight_layout()
    plt.savefig(plot_fpr_path, dpi=200)
    plt.close()
    print(f"Saved FPR vs Threshold plot to: {plot_fpr_path}")

if __name__ == "__main__":
    main()
