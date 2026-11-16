import os
import sys
import time
import json
import numpy as np
import pandas as pd
import torch

# Ensure DefectVisionAI is on sys.path
dv_path = os.path.abspath("DefectVisionAI")
if dv_path not in sys.path:
    sys.path.insert(0, dv_path)

import app
from starlette.testclient import TestClient

def test_inference_pipeline():
    print("=== STEP 2: VERIFYING REAL INFERENCE & NUMERICAL DETERMINISM ===")
    
    # Check torch seed
    torch.manual_seed(42)
    np.random.seed(42)

    # Initialize FastAPI TestClient
    client = TestClient(app.app)
    
    # Test cases: select diverse specimens from MVTec AD
    # Bottle and Cable test sets on Google Drive
    test_cases = [
        {
            "category": "bottle",
            "rel_path": "G:/My Drive/DefectVisionAI/dataset/raw/mvtec/bottle/test/broken_large/000.png",
            "expected_ground_truth": "defective"
        },
        {
            "category": "bottle",
            "rel_path": "G:/My Drive/DefectVisionAI/dataset/raw/mvtec/bottle/test/good/000.png",
            "expected_ground_truth": "normal"
        },
        {
            "category": "cable",
            "rel_path": "G:/My Drive/DefectVisionAI/dataset/raw/mvtec/cable/test/bent_wire/000.png",
            "expected_ground_truth": "defective"
        },
        {
            "category": "cable",
            "rel_path": "G:/My Drive/DefectVisionAI/dataset/raw/mvtec/cable/test/good/000.png",
            "expected_ground_truth": "normal"
        }
    ]

    verification_records = []
    all_passed = True

    for tc in test_cases:
        cat = tc["category"]
        img_path = tc["rel_path"]
        gt = tc["expected_ground_truth"]

        if not os.path.exists(img_path):
            print(f"Skipping {cat} test: file not found at {img_path}")
            continue

        print(f"\n--- Testing Specimen: {cat} ({os.path.basename(img_path)}) [GT: {gt}] ---")

        # 1. Direct Python function call
        res_direct = app.inspect_single_image(img_path, cat)
        if res_direct is None:
            raise RuntimeError(f"Direct inspection returned None for {img_path}")

        # 2. FastAPI endpoint: /predict (multipart file upload)
        with open(img_path, "rb") as f:
            resp_predict = client.post("/predict", data={"category": cat}, files={"file": ("test.png", f, "image/png")})
        assert resp_predict.status_code == 200, f"/predict failed: {resp_predict.text}"
        res_api_predict = resp_predict.json()

        # 3. FastAPI endpoint: /inspect-frame (multipart frame upload)
        with open(img_path, "rb") as f:
            resp_frame = client.post("/inspect-frame", data={"category": cat}, files={"frame": ("test.png", f, "image/png")})
        assert resp_frame.status_code == 200, f"/inspect-frame failed: {resp_frame.text}"
        res_api_frame = resp_frame.json()

        # Check numerical equality between Direct and /predict
        score_diff_predict = abs(res_direct["anomaly_score"] - res_api_predict["anomaly_score"])
        conf_diff_predict = abs(res_direct["confidence_pct"] - res_api_predict["confidence_pct"])
        sev_diff_predict = abs(res_direct["severity_score"] - res_api_predict["severity_score"])

        # Check numerical equality between Direct and /inspect-frame
        # /inspect-frame rounds raw_score to 4 decimals, so tolerance is 1e-3
        score_diff_frame = abs(res_direct["anomaly_score"] - res_api_frame["anomaly_score"])
        conf_diff_frame = abs(res_direct["confidence_pct"] - res_api_frame["confidence_pct"])
        sev_diff_frame = abs(res_direct["severity_score"] - res_api_frame["severity_score"])

        print(f"  Direct Score:     {res_direct['anomaly_score']:.4f} | Pred: {res_direct['predicted_label']} | Sev: {res_direct['severity_level']} ({res_direct['severity_score']:.2f})")
        print(f"  /predict Score:   {res_api_predict['anomaly_score']:.4f} | Delta: {score_diff_predict:.2e}")
        print(f"  /inspect Score:   {res_api_frame['anomaly_score']:.4f} | Delta: {score_diff_frame:.2e}")

        # Assertions
        tol = 1e-3
        if score_diff_predict > tol or score_diff_frame > tol:
            print(f"  FAILED tolerance check! Delta predict: {score_diff_predict}, Delta frame: {score_diff_frame}")
            all_passed = False
        else:
            print("  PASSED API vs Direct Numerical Equivalence (< 1e-3)")

        # 4. Determinism Test: 5 consecutive runs
        print("  Testing 5 consecutive runs for determinism...")
        run_scores = []
        for r in range(5):
            r_res = app.inspect_single_image(img_path, cat)
            run_scores.append(r_res["anomaly_score"])
        score_variance = max(run_scores) - min(run_scores)
        print(f"  5-run raw scores: {[round(s, 6) for s in run_scores]}")
        print(f"  Max variance across 5 runs: {score_variance:.2e}")
        assert score_variance == 0.0, f"Non-deterministic inference detected! Variance = {score_variance}"
        print("  PASSED Determinism Check (0.000000 variance)")

        verification_records.append({
            "specimen": f"{cat}/{os.path.basename(img_path)}",
            "category": cat,
            "ground_truth": gt,
            "direct_predicted_label": res_direct["predicted_label"],
            "direct_anomaly_score": res_direct["anomaly_score"],
            "direct_confidence_pct": res_direct["confidence_pct"],
            "direct_severity_score": res_direct["severity_score"],
            "api_predict_score": res_api_predict["anomaly_score"],
            "api_frame_score": res_api_frame["anomaly_score"],
            "delta_predict": score_diff_predict,
            "delta_frame": score_diff_frame,
            "determinism_variance_5_runs": score_variance,
            "deterministic_pass": (score_variance == 0.0),
            "equivalence_pass": (score_diff_predict < tol and score_diff_frame < tol)
        })

    # Save detailed record
    df_ver = pd.DataFrame(verification_records)
    out_csv = "release/final_18h_validation/inference_verification_matrix.csv"
    df_ver.to_csv(out_csv, index=False)
    print(f"\nVerification matrix written to {out_csv}")
    print(f"ALL INFERENCE VERIFICATION TESTS PASSED: {all_passed and len(verification_records) > 0}")

if __name__ == "__main__":
    test_inference_pipeline()
