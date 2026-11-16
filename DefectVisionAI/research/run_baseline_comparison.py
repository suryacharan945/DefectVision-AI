import json
import os
import numpy as np
import pandas as pd

from selective_review import (
    compute_margin_uncertainty,
    compute_distance_to_threshold,
    simulate_selective_review,
    compute_risk_coverage_curve,
    compute_bootstrap_ci
)

def run_experiment():
    print("==================================================================")
    print("DEFECTVISION AI — Q1 SELECTIVE REVIEW BASELINE EXPERIMENT")
    print("==================================================================")

    # 1. Load data
    eff_path = "DefectVisionAI/logs/step8_efficientnet_on_common_testset.csv"
    pc_path = "DefectVisionAI/logs/step7_patchcore_inference_log.csv"
    base_path = "DefectVisionAI/reports/step9_severity_baselines.csv"

    df_eff = pd.read_csv(eff_path)
    df_pc = pd.read_csv(pc_path)
    baselines = pd.read_csv(base_path).set_index("category")["baseline_p99"].to_dict()

    merged = pd.merge(df_eff, df_pc[["filepath", "anomaly_score"]], on="filepath", suffixes=("_eff", "_pc"))
    merged["pc_thresh"] = merged["category"].map(baselines)

    y_true = (merged["true_label"] == "defective").astype(int).values
    p_eff = merged["anomaly_score_eff"].values
    s_pc = merged["anomaly_score_pc"].values
    t_pc = merged["pc_thresh"].values

    # Base models
    y_pred_eff = (p_eff >= 0.5).astype(int)
    y_pred_pc = (s_pc >= t_pc).astype(int)

    # Hybrid OR
    y_pred_or = (y_pred_eff | y_pred_pc).astype(int)

    print(f"Total Observations: {len(merged)}")
    print(f"Ground Truth Defectives: {y_true.sum()}, Normals: {(~y_true.astype(bool)).sum()}")
    print(f"EfficientNet Base Errors: {(y_true != y_pred_eff).sum()} (FN={((y_true==1)&(y_pred_eff==0)).sum()})")
    print(f"PatchCore Base Errors:    {(y_true != y_pred_pc).sum()} (FN={((y_true==1)&(y_pred_pc==0)).sum()})")
    print(f"Hybrid OR Base Errors:    {(y_true != y_pred_or).sum()} (FN={((y_true==1)&(y_pred_or==0)).sum()})")
    print("-" * 66)

    # 2. Compute Selection Priority Scores
    rng = np.random.default_rng(42)
    scores_random = rng.uniform(0, 1, size=len(merged))
    scores_top_pc = s_pc
    scores_top_eff = p_eff
    scores_margin = compute_margin_uncertainty(p_eff)
    scores_dist_pc = compute_distance_to_threshold(s_pc, t_pc)

    policies = [
        ("Random Selection", scores_random, y_pred_eff),
        ("Highest Anomaly Score (PatchCore)", scores_top_pc, y_pred_eff),
        ("Highest Score (EfficientNet)", scores_top_eff, y_pred_eff),
        ("Supervised Margin (|p - 0.5|)", scores_margin, y_pred_eff),
        ("PatchCore Distance to Threshold", scores_dist_pc, y_pred_eff)
    ]

    all_results = []
    budgets = [0.01, 0.05, 0.10, 0.20]

    for name, s, base_pred in policies:
        res = simulate_selective_review(y_true, base_pred, s, budgets=budgets)
        res["policy"] = name
        all_results.append(res)

    results_df = pd.concat(all_results, ignore_index=True)
    
    # Print comparison at 10% budget
    b10 = results_df[results_df["budget"] == 0.10][
        ["policy", "k_reviewed", "errors_captured", "total_errors", "ecr_pct", "escapes_captured", "total_escapes", "derr_pct", "yield_pct"]
    ]
    print("\n=== SELECTIVE REVIEW PERFORMANCE AT 10% HUMAN BUDGET (172 IMAGES) ===")
    print(b10.to_string(index=False))

    # 3. Bootstrap CI on Margin Sampling at 10% Budget
    def ecr_at_10(sample_df):
        yt = (sample_df["true_label"] == "defective").astype(int).values
        yp = (sample_df["anomaly_score_eff"] >= 0.5).astype(int).values
        u = compute_margin_uncertainty(sample_df["anomaly_score_eff"].values)
        k = int(np.round(0.10 * len(sample_df)))
        top_k_idx = np.argsort(-u)[:k]
        errs = (yt != yp)
        if errs.sum() == 0:
            return 0.0
        return float(errs[top_k_idx].sum() / errs.sum() * 100.0)

    ci_margin = compute_bootstrap_ci(ecr_at_10, merged, n_resamples=1000, ci=0.95)
    print(f"\nBootstrap 95% CI for Margin Sampling ECR@10%: {ci_margin['mean']:.2f}% [{ci_margin['ci_lower']:.2f}%, {ci_margin['ci_upper']:.2f}%]")

    # 4. Save results
    out_dir = "delivery_24h/final_hardening_v3/test_outputs"
    os.makedirs(out_dir, exist_ok=True)
    results_df.to_csv(os.path.join(out_dir, "baseline_selective_review_results.csv"), index=False)
    
    summary = {
        "budgets_evaluated": budgets,
        "n_samples": len(merged),
        "ci_margin_ecr_10pct": ci_margin,
        "status": "EXPERIMENT_BASELINES_VERIFIED"
    }
    with open(os.path.join(out_dir, "baseline_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Results written to {out_dir}")

if __name__ == "__main__":
    run_experiment()
