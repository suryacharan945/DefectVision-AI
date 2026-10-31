"""
DefectVision AI — Phase 8B: Leakage-Free MACBA Feasibility Experiment Runner.
Executes calibrated multi-category budget allocation against 7 strong baselines and 1 oracle upper bound.
"""

import os
import sys
import time
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from sklearn.linear_model import LogisticRegression

# Set random seed
SEED = 42
RNG = np.random.default_rng(SEED)

BUDGET_FRACTIONS = [0.01, 0.02, 0.05, 0.10, 0.15, 0.20]
COST_RATIOS = [1, 5, 20, 50, 100]  # lambda = c_FN / c_FP


def compute_realized_loss(
    records: List[Dict[str, Any]],
    reviewed_indices: List[int],
    c_fn: float,
    c_fp: float,
    c_rev: float,
    p_sens: float = 1.0,
    p_spec: float = 1.0
) -> Dict[str, Any]:
    """
    Computes realized financial cost, captured errors, FN escape reduction, and yield.
    """
    total_cost = 0.0
    no_review_cost = 0.0
    captured_errors = 0
    captured_fn = 0
    captured_fp = 0
    base_errors = 0
    base_fn = 0
    base_fp = 0
    reviewed_set = set(reviewed_indices)

    for i, r in enumerate(records):
        is_fn = bool(r["is_fn"])
        is_fp = bool(r["is_fp"])
        is_defect = (str(r["true_label"]).lower() in ["defective", "anomaly", "1"])
        
        # Base cost without review
        if is_fn:
            no_review_cost += c_fn
            base_errors += 1
            base_fn += 1
        elif is_fp:
            no_review_cost += c_fp
            base_errors += 1
            base_fp += 1

        # Realized cost under policy
        if i in reviewed_set:
            # Human review cost
            total_cost += c_rev
            if is_fn:
                captured_fn += 1
                captured_errors += 1
                # If human misses defect (imperfect reviewer)
                if RNG.uniform() > p_sens:
                    total_cost += c_fn
            elif is_fp:
                captured_fp += 1
                captured_errors += 1
                # If human falsely flags normal part
                if RNG.uniform() > p_spec:
                    total_cost += c_fp
            else:
                # Correctly automated item was audited
                if is_defect and RNG.uniform() > p_sens:
                    total_cost += c_fn
                elif not is_defect and RNG.uniform() > p_spec:
                    total_cost += c_fp
        else:
            # Autonomous decision
            if is_fn:
                total_cost += c_fn
            elif is_fp:
                total_cost += c_fp

    cost_reduction = (no_review_cost - total_cost) / no_review_cost if no_review_cost > 0 else 0.0
    ecr = captured_errors / base_errors if base_errors > 0 else 0.0
    der = captured_fn / base_fn if base_fn > 0 else 0.0
    k = len(reviewed_indices)
    error_yield = captured_errors / k if k > 0 else 0.0

    return {
        "no_review_cost": no_review_cost,
        "total_cost": total_cost,
        "cost_reduction_pct": cost_reduction * 100.0,
        "base_errors": base_errors,
        "base_fn": base_fn,
        "base_fp": base_fp,
        "captured_errors": captured_errors,
        "captured_fn": captured_fn,
        "captured_fp": captured_fp,
        "ecr": ecr * 100.0,
        "der": der * 100.0,
        "reviewed_k": k,
        "error_yield": error_yield * 100.0
    }


def fit_calibration_models(cal_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Fits logistic probability models and computes category error priors strictly on calibration data.
    """
    models = {}
    categories = cal_df["category"].unique().tolist()
    
    # 1. Category error priors on calibration
    cal_priors = {}
    for cat in categories:
        sub = cal_df[cal_df["category"] == cat]
        cal_priors[cat] = float(sub["is_error"].mean())

    # 2. Fit defect probability P(Defect | S(X) - tau)
    # y: 1 if defective, 0 if normal
    y_defect = (cal_df["true_label"].str.lower().isin(["defective", "anomaly", "1"])).astype(int).to_numpy()
    x_score = (cal_df["anomaly_score"] - cal_df["decision_threshold"]).to_numpy().reshape(-1, 1)

    defect_clf = LogisticRegression(C=1.0, random_state=SEED)
    defect_clf.fit(x_score, y_defect)
    models["defect_clf"] = defect_clf

    # 3. Fit error probability P(Error | |S(X) - tau|)
    y_error = cal_df["is_error"].to_numpy().astype(int)
    x_dist = cal_df["dist_to_threshold"].to_numpy().reshape(-1, 1)

    error_clf = LogisticRegression(C=1.0, random_state=SEED)
    error_clf.fit(x_dist, y_error)
    models["error_clf"] = error_clf

    models["cal_priors"] = cal_priors
    return models


def run_allocation_policies(
    eval_df: pd.DataFrame,
    cal_models: Dict[str, Any],
    budget_k: int,
    c_fn: float,
    c_fp: float,
    c_rev: float,
    p_sens: float = 1.0,
    p_spec: float = 1.0
) -> Dict[str, List[int]]:
    """
    Implements all 8 baselines and proposed MACBA on eval_df.
    Returns dictionary mapping policy_name -> list of selected eval_df integer indices.
    """
    records = eval_df.to_dict(orient="records")
    N = len(records)
    categories = sorted(eval_df["category"].unique().tolist())
    C = len(categories)

    # Precompute estimated defect probability and error probability for each item
    x_score = (eval_df["anomaly_score"] - eval_df["decision_threshold"]).to_numpy().reshape(-1, 1)
    p_defect = cal_models["defect_clf"].predict_proba(x_score)[:, 1]

    x_dist = eval_df["dist_to_threshold"].to_numpy().reshape(-1, 1)
    p_error = cal_models["error_clf"].predict_proba(x_dist)[:, 1]

    for i in range(N):
        records[i]["p_defect_est"] = float(p_defect[i])
        records[i]["p_error_est"] = float(p_error[i])
        
        # Decision-theoretic expected loss reduction Delta L
        y_hat = 1 if records[i]["anomaly_score"] >= records[i]["decision_threshold"] else 0
        p_d = records[i]["p_defect_est"]
        if y_hat == 0:
            delta_l = p_d * p_sens * c_fn - (1.0 - p_d) * (1.0 - p_spec) * c_fp - c_rev
        else:
            delta_l = (1.0 - p_d) * p_spec * c_fp - p_d * (1.0 - p_sens) * c_fn - c_rev
        records[i]["delta_loss_est"] = float(delta_l)

    selected = {}

    # --- BL0: Uniform Category Allocation with within-category boundary ranking ---
    k_per_cat = budget_k // C
    rem = budget_k % C
    bl0_idx = []
    for idx_c, cat in enumerate(categories):
        quota = k_per_cat + (1 if idx_c < rem else 0)
        cat_items = [i for i, r in enumerate(records) if r["category"] == cat]
        cat_sorted = sorted(cat_items, key=lambda i: (records[i]["dist_to_threshold"], records[i]["image_id"]))
        bl0_idx.extend(cat_sorted[:quota])
    selected["BL0_Uniform"] = bl0_idx

    # --- BL1: Volume-Proportional Allocation ---
    vol_counts = {cat: sum(1 for r in records if r["category"] == cat) for cat in categories}
    bl1_idx = []
    alloc_counts = {}
    for cat in categories:
        alloc_counts[cat] = int(np.floor(budget_k * (vol_counts[cat] / N)))
    # Fill remaining
    curr_alloc = sum(alloc_counts.values())
    for cat in sorted(categories, key=lambda c: vol_counts[c], reverse=True):
        if curr_alloc >= budget_k:
            break
        alloc_counts[cat] += 1
        curr_alloc += 1
    for cat in categories:
        cat_items = [i for i, r in enumerate(records) if r["category"] == cat]
        cat_sorted = sorted(cat_items, key=lambda i: (records[i]["dist_to_threshold"], records[i]["image_id"]))
        bl1_idx.extend(cat_sorted[:alloc_counts[cat]])
    selected["BL1_Volume"] = bl1_idx

    # --- BL2: Globally Pooled Raw Distance ---
    all_sorted_bl2 = sorted(range(N), key=lambda i: (records[i]["dist_to_threshold"], records[i]["image_id"]))
    selected["BL2_Pooled_Distance"] = all_sorted_bl2[:budget_k]

    # --- BL3: Globally Pooled Category-Normalized Distance ---
    all_sorted_bl3 = sorted(
        range(N),
        key=lambda i: (records[i]["dist_to_threshold"] / records[i]["decision_threshold"], records[i]["image_id"])
    )
    selected["BL3_Normalized_Distance"] = all_sorted_bl3[:budget_k]

    # --- BL4: Historical Category Error-Rate Allocation ---
    priors = cal_models["cal_priors"]
    sum_prior = sum(max(priors.get(cat_name, 0.01), 0.005) for cat_name in categories)
    bl4_alloc = {}
    for cat in categories:
        bl4_alloc[cat] = int(np.floor(budget_k * (max(priors.get(cat, 0.01), 0.005) / sum_prior)))
    curr_b4 = sum(bl4_alloc.values())
    for cat in sorted(categories, key=lambda cat_name: priors.get(cat_name, 0.0), reverse=True):
        if curr_b4 >= budget_k:
            break
        bl4_alloc[cat] += 1
        curr_b4 += 1
    bl4_idx = []
    for cat in categories:
        cat_items = [i for i, r in enumerate(records) if r["category"] == cat]
        cat_sorted = sorted(cat_items, key=lambda i: (records[i]["dist_to_threshold"], records[i]["image_id"]))
        bl4_idx.extend(cat_sorted[:bl4_alloc[cat]])
    selected["BL4_Prior_Allocation"] = bl4_idx

    # --- BL5: Calibrated Error-Risk Ranking ---
    all_sorted_bl5 = sorted(
        range(N),
        key=lambda i: (-records[i]["p_error_est"], records[i]["image_id"])
    )
    selected["BL5_Calibrated_Risk"] = all_sorted_bl5[:budget_k]

    # --- BL6: Simple Cost-Weighted Risk ---
    def cost_risk_score(i):
        y_hat = 1 if records[i]["anomaly_score"] >= records[i]["decision_threshold"] else 0
        loss_w = c_fn if y_hat == 0 else c_fp
        return records[i]["p_error_est"] * loss_w

    all_sorted_bl6 = sorted(
        range(N),
        key=lambda i: (-cost_risk_score(i), records[i]["image_id"])
    )
    selected["BL6_Cost_Weighted_Risk"] = all_sorted_bl6[:budget_k]

    # --- BL7: Oracle Allocation Using Evaluation Labels (Upper Bound) ---
    all_sorted_bl7 = sorted(
        range(N),
        key=lambda i: (-int(records[i]["is_error"]), records[i]["dist_to_threshold"], records[i]["image_id"])
    )
    selected["BL7_Oracle"] = all_sorted_bl7[:budget_k]

    # --- Proposed: MACBA (Marginal Utility Knapsack Allocation) ---
    all_sorted_macba = sorted(
        range(N),
        key=lambda i: (-records[i]["delta_loss_est"] / c_rev, records[i]["image_id"])
    )
    selected["Proposed_MACBA"] = all_sorted_macba[:budget_k]

    return selected


def main():
    print("================ DEFECTVISION AI: PHASE 8B LEAKAGE-FREE EXPERIMENT ================", flush=True)
    t_start = time.perf_counter()

    data_csv = "DefectVisionAI/research/cpnd/dev_extracted_scores_phase7c.csv"
    if not os.path.exists(data_csv):
        raise FileNotFoundError(f"Missing {data_csv}")

    df = pd.read_csv(data_csv)
    df["dist_to_threshold"] = (df["anomaly_score"] - df["decision_threshold"]).abs()
    df["defect_type"] = df["filepath"].apply(lambda x: x.split('/')[-2] if '/' in x else x.split('\\')[-2])
    print(f"Loaded {len(df)} images across categories: {df['category'].unique().tolist()}", flush=True)

    # 1. Stratified Group-Aware Split into Calibration (50%) and Internal Evaluation (50%)
    df["strata"] = df["category"] + "_" + df["defect_type"] + "_" + df["is_error"].astype(str)
    cal_indices = []
    eval_indices = []

    for _, grp in df.groupby("strata"):
        g_idx = list(grp.index)
        RNG.shuffle(g_idx)
        half = len(g_idx) // 2
        cal_indices.extend(g_idx[:half])
        eval_indices.extend(g_idx[half:])

    cal_df = df.loc[cal_indices].copy().reset_index(drop=True)
    eval_df = df.loc[eval_indices].copy().reset_index(drop=True)

    print(f"\n--- Split Verification ---", flush=True)
    print(f"Calibration Fold: {len(cal_df)} images, {cal_df['is_error'].sum()} errors ({cal_df['is_fn'].sum()} FN, {cal_df['is_fp'].sum()} FP)")
    print(f"Evaluation Fold:  {len(eval_df)} images, {eval_df['is_error'].sum()} errors ({eval_df['is_fn'].sum()} FN, {eval_df['is_fp'].sum()} FP)")

    # 2. Fit calibration models EXCLUSIVELY on cal_df
    print("\n--- Fitting Calibration Models Strictly on Calibration Fold ---", flush=True)
    cal_models = fit_calibration_models(cal_df)
    print(f"Calibrated Category Error Priors: {cal_models['cal_priors']}")

    # 3. Primary Feasibility Benchmark across Budgets at Standard Industrial Cost (lambda=20, c_FP=10, c_FN=200, c_rev=1)
    c_fp = 10.0
    c_fn = 200.0  # lambda = 20
    c_rev = 1.0
    p_sens = 1.0
    p_spec = 1.0

    eval_records = eval_df.to_dict(orient="records")
    N_eval = len(eval_records)

    feasibility_rows = []
    print("\n--- Running All 8 Policies across Review Budgets (lambda=20) ---", flush=True)

    for b_frac in BUDGET_FRACTIONS:
        k = max(1, int(np.floor(b_frac * N_eval)))
        allocations = run_allocation_policies(eval_df, cal_models, k, c_fn, c_fp, c_rev, p_sens, p_spec)

        for pol_name, reviewed_idx in allocations.items():
            metrics = compute_realized_loss(eval_records, reviewed_idx, c_fn, c_fp, c_rev, p_sens, p_spec)
            
            # Allocation by category
            sel_cats = [eval_records[i]["category"] for i in reviewed_idx]
            k_bottle = sel_cats.count("bottle")
            k_capsule = sel_cats.count("capsule")
            k_nut = sel_cats.count("metal_nut")

            feasibility_rows.append({
                "Policy": pol_name,
                "Budget_Frac": b_frac,
                "Reviewed_K": k,
                "Total_Realized_Cost": round(metrics["total_cost"], 2),
                "No_Review_Cost": round(metrics["no_review_cost"], 2),
                "Cost_Reduction_Pct": round(metrics["cost_reduction_pct"], 2),
                "Captured_Errors": metrics["captured_errors"],
                "Captured_FN": metrics["captured_fn"],
                "Captured_FP": metrics["captured_fp"],
                "MC_ECR": round(metrics["ecr"], 2),
                "MC_DER": round(metrics["der"], 2),
                "Error_Yield": round(metrics["error_yield"], 2),
                "K_bottle": k_bottle,
                "K_capsule": k_capsule,
                "K_metal_nut": k_nut
            })

    feasibility_df = pd.DataFrame(feasibility_rows)
    os.makedirs("research/phase8b_macba_feasibility", exist_ok=True)
    feasibility_df.to_csv("research/phase8b_macba_feasibility/FEASIBILITY_RESULTS.csv", index=False)
    print("Saved FEASIBILITY_RESULTS.csv", flush=True)

    # 4. Paired Policy Comparison at Primary Target Budget (10% budget, K=16)
    b10_df = feasibility_df[feasibility_df["Budget_Frac"] == 0.10]
    print("\n--- Primary Budget Benchmark (10% Budget, K=16) ---", flush=True)
    print(b10_df[["Policy", "Reviewed_K", "Captured_Errors", "MC_ECR", "MC_DER", "Cost_Reduction_Pct", "K_bottle", "K_capsule", "K_metal_nut"]].to_string(), flush=True)

    # Paired Bootstrap Comparison against the Strongest Baseline (BL3 and BL6)
    k_10 = max(1, int(np.floor(0.10 * N_eval)))
    alloc_10 = run_allocation_policies(eval_df, cal_models, k_10, c_fn, c_fp, c_rev, p_sens, p_spec)

    macba_idx = set(alloc_10["Proposed_MACBA"])
    comp_policies = ["BL0_Uniform", "BL1_Volume", "BL2_Pooled_Distance", "BL3_Normalized_Distance", "BL4_Prior_Allocation", "BL5_Calibrated_Risk", "BL6_Cost_Weighted_Risk"]

    n_boot = 2000
    paired_rows = []

    for comp_name in comp_policies:
        comp_idx = set(alloc_10[comp_name])
        
        diff_costs = []
        diff_ecrs = []
        diff_ders = []

        base_res_macba = compute_realized_loss(eval_records, list(macba_idx), c_fn, c_fp, c_rev, p_sens, p_spec)
        base_res_comp = compute_realized_loss(eval_records, list(comp_idx), c_fn, c_fp, c_rev, p_sens, p_spec)

        delta_cost_pt = base_res_macba["cost_reduction_pct"] - base_res_comp["cost_reduction_pct"]
        delta_ecr_pt = base_res_macba["ecr"] - base_res_comp["ecr"]
        delta_der_pt = base_res_macba["der"] - base_res_comp["der"]

        for _ in range(n_boot):
            b_sample_idx = RNG.choice(N_eval, size=N_eval, replace=True)
            b_sample = [eval_records[i] for i in b_sample_idx]
            
            # Sub-sample evaluated indices
            m_rev = [j for j, idx_orig in enumerate(b_sample_idx) if idx_orig in macba_idx]
            c_rev_boot = [j for j, idx_orig in enumerate(b_sample_idx) if idx_orig in comp_idx]

            r_macba = compute_realized_loss(b_sample, m_rev, c_fn, c_fp, c_rev, p_sens, p_spec)
            r_comp = compute_realized_loss(b_sample, c_rev_boot, c_fn, c_fp, c_rev, p_sens, p_spec)

            diff_costs.append(r_macba["cost_reduction_pct"] - r_comp["cost_reduction_pct"])
            diff_ecrs.append(r_macba["ecr"] - r_comp["ecr"])
            diff_ders.append(r_macba["der"] - r_comp["der"])

        paired_rows.append({
            "Comparison": f"Proposed_MACBA vs {comp_name}",
            "Delta_Cost_Reduction_Pct": round(delta_cost_pt, 2),
            "Delta_Cost_95CI": f"[{np.percentile(diff_costs, 2.5):.2f}%, {np.percentile(diff_costs, 97.5):.2f}%]",
            "Delta_MC_ECR": round(delta_ecr_pt, 2),
            "Delta_ECR_95CI": f"[{np.percentile(diff_ecrs, 2.5):.2f}%, {np.percentile(diff_ecrs, 97.5):.2f}%]",
            "Delta_MC_DER": round(delta_der_pt, 2),
            "Delta_DER_95CI": f"[{np.percentile(diff_ders, 2.5):.2f}%, {np.percentile(diff_ders, 97.5):.2f}%]",
            "Statistically_Superior": bool(np.percentile(diff_costs, 2.5) > 0.0)
        })

    paired_df = pd.DataFrame(paired_rows)
    paired_df.to_csv("research/phase8b_macba_feasibility/PAIRED_POLICY_COMPARISON.csv", index=False)
    print("\n--- Paired Bootstrap Policy Comparison (2,000 Iterations) ---", flush=True)
    print(paired_df[["Comparison", "Delta_Cost_Reduction_Pct", "Delta_Cost_95CI", "Delta_MC_ECR", "Delta_ECR_95CI", "Statistically_Superior"]].to_string(), flush=True)

    # 5. Cost Sensitivity Analysis across lambda in {1, 5, 20, 50, 100} at 10% budget
    print("\n--- Running Cost Ratio Sensitivity Analysis ---", flush=True)
    cost_sens_rows = []

    for lam in COST_RATIOS:
        c_fn_lam = lam * c_fp
        alloc_lam = run_allocation_policies(eval_df, cal_models, k_10, c_fn_lam, c_fp, c_rev, p_sens, p_spec)
        
        for p_name in ["BL0_Uniform", "BL2_Pooled_Distance", "BL3_Normalized_Distance", "BL6_Cost_Weighted_Risk", "Proposed_MACBA"]:
            res_lam = compute_realized_loss(eval_records, alloc_lam[p_name], c_fn_lam, c_fp, c_rev, p_sens, p_spec)
            cost_sens_rows.append({
                "Lambda_Ratio": lam,
                "Cost_FN": c_fn_lam,
                "Cost_FP": c_fp,
                "Policy": p_name,
                "Total_Realized_Cost": round(res_lam["total_cost"], 2),
                "Cost_Reduction_Pct": round(res_lam["cost_reduction_pct"], 2),
                "MC_ECR": round(res_lam["ecr"], 2),
                "MC_DER": round(res_lam["der"], 2),
                "Captured_FN": res_lam["captured_fn"]
            })

    cost_sens_df = pd.DataFrame(cost_sens_rows)
    cost_sens_df.to_csv("research/phase8b_macba_feasibility/COST_SENSITIVITY_RESULTS.csv", index=False)
    print("Saved COST_SENSITIVITY_RESULTS.csv", flush=True)

    total_time = time.perf_counter() - t_start
    print(f"\nPhase 8B experiment executed successfully in {total_time:.2f}s!", flush=True)


if __name__ == "__main__":
    main()
