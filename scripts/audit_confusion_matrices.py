import pandas as pd
import numpy as np

def inspect_df(name, path):
    print(f"\n==========================================")
    print(f"FILE: {name} ({path})")
    try:
        df = pd.read_csv(path)
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print(df.head(2))
        return df
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return None

files = {
    "step11_uncertainty": "DefectVisionAI/logs/step11_uncertainty_log.csv",
    "step8_common_testset": "DefectVisionAI/logs/step8_efficientnet_on_common_testset.csv",
    "step8_benchmark": "DefectVisionAI/logs/step8_efficientnet_v3_on_benchmark.csv",
    "step7_patchcore": "DefectVisionAI/logs/step7_patchcore_inference_log.csv",
    "step6_padim": "DefectVisionAI/logs/step6_padim_inference_log.csv",
    "step5_ae": "DefectVisionAI/logs/step5_ae_inference_log.csv",
    "step11_threshold_sensitivity": "DefectVisionAI/reports/step11_threshold_sensitivity.csv",
    "step8_model_comparison_FAIR": "DefectVisionAI/reports/step8_model_comparison_FAIR.csv",
    "step8_model_comparison": "DefectVisionAI/reports/step8_model_comparison.csv"
}

dfs = {}
for k, v in files.items():
    dfs[k] = inspect_df(k, v)
