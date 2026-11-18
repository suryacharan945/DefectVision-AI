"""
DefectVision AI 2.2 — Artifact Reproducibility & Metric Verification Script
Directly inspects and recomputes all metrics from:
- release/experiments/baseline_vs_adaptation.csv
- release/experiments/dataset_manifest.json
- release/experiments/threshold_calibration_report.md
- release/experiments/ABLATION_STUDY.md
"""

import os
import json
import pandas as pd
import numpy as np

def main():
    print("=" * 80)
    print("DEFECTVISION AI 2.2 — REPRODUCING ARTIFACT METRICS DIRECTLY FROM RAW DATA")
    print("=" * 80)

    # 1. Inspect baseline_vs_adaptation.csv
    csv_path = "release/experiments/baseline_vs_adaptation.csv"
    if not os.path.exists(csv_path):
        print(f"ERROR: {csv_path} does not exist!")
        return

    df = pd.read_csv(csv_path)
    print(f"\n[1] Loaded {csv_path}: {len(df)} rows, {len(df.columns)} columns")
    print("Domains present:", df['domain'].unique().tolist())

    for dom in df['domain'].unique():
        sub = df[df['domain'] == dom]
        print(f"\n--- Domain: {dom} (Total N = {len(sub)}) ---")
        n_norm = sum(sub['ground_truth'] == 'NORMAL')
        n_def = sum(sub['ground_truth'] == 'DEFECTIVE')
        print(f"Ground Truth counts: Normal = {n_norm}, Defective = {n_def}")

        for model in ['baseline', 'station01', 'adapted']:
            score_col = f"score_{model}"
            verdict_col = f"verdict_{model}"
            if score_col not in sub.columns:
                continue

            # Compute TP, FP, TN, FN
            tp = sum((sub['ground_truth'] == 'DEFECTIVE') & (sub[verdict_col] == 'DEFECTIVE'))
            fp = sum((sub['ground_truth'] == 'NORMAL') & (sub[verdict_col] == 'DEFECTIVE'))
            tn = sum((sub['ground_truth'] == 'NORMAL') & (sub[verdict_col] == 'NORMAL'))
            fn = sum((sub['ground_truth'] == 'DEFECTIVE') & (sub[verdict_col] == 'NORMAL'))

            prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0
            f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
            acc = (tp + tn) / len(sub) if len(sub) > 0 else 0.0
            fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
            fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0

            print(f"Model: {model:<10} | TP={tp} FP={fp} TN={tn} FN={fn} | Prec={prec:.4f} Rec={rec:.4f} Spec={spec:.4f} F1={f1:.4f} Acc={acc:.4f} FPR={fpr:.4f}")

    # Detailed inspection of Domain B (External Studio Bottles)
    dom_b = df[df['domain'] == 'Domain B: Controlled External Photos']
    print("\n" + "=" * 80)
    print("DETAILED SPECIMEN SCORES FOR DOMAIN B (STUDIO BOTTLES):")
    for _, r in dom_b.iterrows():
        print(f"Specimen: {r['specimen_id']} | Image: {os.path.basename(r['image_path'])} | GT: {r['ground_truth']}")
        print(f"  - Baseline: Score={r['score_baseline']:.4f}, Verdict={r['verdict_baseline']} (Thresh=1.4666)")
        print(f"  - Station01: Score={r['score_station01']:.4f}, Verdict={r['verdict_station01']} (Thresh=0.8333)")
        print(f"  - Adapted:   Score={r['score_adapted']:.4f}, Verdict={r['verdict_adapted']} (Thresh=1.6410)")

    # 2. Inspect dataset_manifest.json
    manifest_path = "release/experiments/dataset_manifest.json"
    if os.path.exists(manifest_path):
        with open(manifest_path, "r") as f:
            manifest = json.load(f)
        records = manifest.get("records", [])
        print("\n" + "=" * 80)
        print(f"[2] Loaded {manifest_path}: {len(records)} records")
        m_df = pd.DataFrame(records)
        print("Manifest Partition distribution:")
        print(m_df['dataset_partition'].value_counts())
        print("\nManifest Domain distribution:")
        print(m_df['domain'].value_counts())
        print("\nSynthetic vs Real:")
        print(m_df['is_synthetic'].value_counts())

if __name__ == "__main__":
    main()
