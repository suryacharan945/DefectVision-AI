import numpy as np
import pandas as pd

def compute_margin_uncertainty(probabilities):
    """
    Computes binary prediction margin uncertainty from classifier probabilities:
    u(p) = 1.0 - |2p - 1.0| = 2 * (0.5 - |p - 0.5|)
    Maximum uncertainty (1.0) occurs when p = 0.5.
    """
    p = np.asarray(probabilities, dtype=np.float64)
    return 1.0 - np.abs(2.0 * p - 1.0)

def compute_distance_to_threshold(anomaly_scores, thresholds, eps=1e-5):
    """
    Computes boundary proximity uncertainty for anomaly detection models.
    Higher score indicates higher priority for review (closer to decision boundary).
    proximity = 1.0 / (|score - tau_c| + eps)
    """
    s = np.asarray(anomaly_scores, dtype=np.float64)
    t = np.asarray(thresholds, dtype=np.float64)
    dist = np.abs(s - t)
    return 1.0 / (dist + eps)

def simulate_selective_review(y_true, y_pred, selection_scores, budgets=[0.01, 0.05, 0.10, 0.20]):
    """
    Simulates a human review policy under fixed budget constraints.
    Under budget B in (0, 1], flags top floor(B * N) images ranked by selection_scores descending.
    Human reviewer overrides model predictions on flagged images (assumed ground truth oracle).
    
    Returns structured DataFrame with:
    - Reviewed count (K)
    - Review budget (%)
    - Errors captured
    - Error Capture Rate (ECR %)
    - Defect Escapes (FN) captured
    - Defect Escape Reduction Rate (DERR %)
    - False Alarms (FP) captured
    - Review Defect Yield (%)
    """
    y_true = np.asarray(y_true, dtype=int)
    y_pred = np.asarray(y_pred, dtype=int)
    scores = np.asarray(selection_scores, dtype=np.float64)
    
    N = len(y_true)
    is_err = (y_true != y_pred)
    is_fn = (y_true == 1) & (y_pred == 0)
    is_fp = (y_true == 0) & (y_pred == 1)
    
    E0 = int(is_err.sum())
    FN0 = int(is_fn.sum())
    FP0 = int(is_fp.sum())
    
    # Sort indices descending by selection priority
    order = np.argsort(-scores)
    
    records = []
    for b in budgets:
        k = int(np.round(b * N))
        idx = order[:k]
        
        err_cap = int(is_err[idx].sum())
        fn_cap = int(is_fn[idx].sum())
        fp_cap = int(is_fp[idx].sum())
        
        ecr = (err_cap / E0 * 100.0) if E0 > 0 else 0.0
        derr = (fn_cap / FN0 * 100.0) if FN0 > 0 else 0.0
        fparr = (fp_cap / FP0 * 100.0) if FP0 > 0 else 0.0
        yield_rate = (fn_cap / k * 100.0) if k > 0 else 0.0
        
        records.append({
            "budget": b,
            "budget_pct": b * 100.0,
            "k_reviewed": k,
            "reviewed_pct": k / N * 100.0,
            "errors_captured": err_cap,
            "total_errors": E0,
            "ecr_pct": ecr,
            "escapes_captured": fn_cap,
            "total_escapes": FN0,
            "derr_pct": derr,
            "fp_captured": fp_cap,
            "total_fp": FP0,
            "yield_pct": yield_rate
        })
    return pd.DataFrame(records)

def compute_risk_coverage_curve(y_true, y_pred, selection_scores, n_points=50):
    """
    Computes selective classification Risk-Coverage curve (Geifman & El-Yaniv, NeurIPS 2017).
    Coverage phi in [0, 1] is fraction of population retained by automated model.
    Selective Risk R(phi) is error rate on retained population:
    R(phi) = (1 / |Retained|) * sum_{i in Retained} 1(y_i != y_hat_i)
    """
    y_true = np.asarray(y_true, dtype=int)
    y_pred = np.asarray(y_pred, dtype=int)
    scores = np.asarray(selection_scores, dtype=np.float64)
    N = len(y_true)
    
    # Uncertainty is priority for human review -> automated model retains lowest uncertainty
    # Rank by priority ascending (lowest uncertainty retained first)
    order = np.argsort(scores)
    
    coverages = np.linspace(0.1, 1.0, n_points)
    risks = []
    
    for cov in coverages:
        k_retain = int(np.round(cov * N))
        retained_idx = order[:k_retain]
        errs = (y_true[retained_idx] != y_pred[retained_idx]).sum()
        risk = errs / k_retain
        risks.append(risk)
        
    return pd.DataFrame({
        "coverage": coverages,
        "selective_risk": risks
    })

def compute_bootstrap_ci(metric_fn, df, n_resamples=1000, ci=0.95, random_seed=42):
    """
    Computes non-parametric bootstrap confidence intervals at image-level sampling unit.
    """
    rng = np.random.default_rng(random_seed)
    n = len(df)
    estimates = []
    
    for _ in range(n_resamples):
        sample_idx = rng.choice(n, size=n, replace=True)
        sample_df = df.iloc[sample_idx]
        val = metric_fn(sample_df)
        estimates.append(val)
        
    alpha = (1.0 - ci) / 2.0
    lower = np.percentile(estimates, alpha * 100.0)
    upper = np.percentile(estimates, (1.0 - alpha) * 100.0)
    mean_val = np.mean(estimates)
    return {"mean": mean_val, "ci_lower": lower, "ci_upper": upper, "ci_level": ci}
