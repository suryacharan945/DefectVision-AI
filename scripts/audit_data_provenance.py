import os
import pandas as pd

def check_overlaps():
    print("=== TASK 2: EVALUATION INDEPENDENCE & LEAKAGE AUDIT ===")
    
    test_path = "G:/My Drive/DefectVisionAI/dataset/splits/benchmark_test_v2.csv"
    test_df = pd.read_csv(test_path)
    test_fps = set(test_df["filepath"])
    print(f"Benchmark test specimens: {len(test_fps)}")

    splits_dir = "G:/My Drive/DefectVisionAI/dataset/splits"
    split_files = [
        "train_split.csv",
        "val_split.csv",
        "test_split.csv",
        "supervised_train_split.csv",
        "supervised_val_split.csv",
        "supervised_test_split.csv",
        "supervised_train_split_v2.csv",
        "supervised_val_split_v2.csv",
        "supervised_train_split_v3.csv",
        "supervised_val_split_v3.csv"
    ]

    for sf in split_files:
        p = os.path.join(splits_dir, sf)
        if os.path.exists(p):
            df = pd.read_csv(p)
            overlap = test_fps.intersection(set(df["filepath"]))
            print(f"Overlap with {sf:30s}: {len(overlap)} / {len(df)} rows")

    # Check baseline nominal sample counts
    baseline_csv = "DefectVisionAI/reports/step9_severity_baselines.csv"
    if os.path.exists(baseline_csv):
        bdf = pd.read_csv(baseline_csv)
        print(f"\nStep 9 Severity Baselines:\n{bdf[['category', 'baseline_mean', 'baseline_p99', 'n_normal_samples']]}")

if __name__ == "__main__":
    check_overlaps()
