import os
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def clean_path_val(val):
    if pd.isna(val):
        return val
    s = str(val).strip().replace("\\", "/")
    # Extract relative path starting with DefectVisionAI/ or release/
    for prefix in ["DefectVisionAI/", "release/", "frontend/", "scripts/"]:
        if prefix in s:
            idx = s.find(prefix)
            return s[idx:]
    return s

def sanitize_csv(filepath):
    if not os.path.exists(filepath):
        print(f"Skipping missing file: {filepath}")
        return
    df = pd.read_csv(filepath)
    changed = False
    for col in df.columns:
        if "path" in col.lower() or "file" in col.lower():
            original = df[col].astype(str)
            df[col] = df[col].apply(clean_path_val)
            if not original.equals(df[col].astype(str)):
                changed = True
                print(f"Sanitized paths in '{filepath}', column '{col}'")

    if changed:
        df.to_csv(filepath, index=False)
        print(f"Saved sanitized: {filepath}")
    else:
        print(f"Already clean: {filepath}")

if __name__ == "__main__":
    targets = [
        os.path.join(PROJECT_ROOT, "release", "final_validation", "mvtec_all_predictions.csv"),
        os.path.join(PROJECT_ROOT, "release", "final_validation", "FEATURE_ACCEPTANCE_MATRIX.csv"),
        os.path.join(PROJECT_ROOT, "release", "dataset_manifests", "official_test_split.csv"),
        os.path.join(PROJECT_ROOT, "release", "dataset_manifests", "patchcore_calibration_split.csv")
    ]
    for t in targets:
        sanitize_csv(t)
