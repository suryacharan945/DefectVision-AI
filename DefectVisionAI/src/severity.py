
import numpy as np

def normalize_anomaly_score(raw_score, baseline_mean, baseline_p99):
    """Maps a raw per-category anomaly score onto a comparable 0-100 scale
    using that category's OWN normal-image score distribution as the reference frame."""
    span = max(baseline_p99 - baseline_mean, 1e-6)
    normed = (raw_score - baseline_mean) / span
    normed = np.clip(normed, 0, 1.5)  # allow some headroom above p99 for genuinely severe cases
    return float(np.clip(normed * 100, 0, 100))


def compute_severity_score(anomaly_norm, defect_area_pct, confidence_pct=0.0,
                            w_anomaly=0.6, w_area=0.4, w_confidence=0.0,
                            verdict=None):
    """
    Computes calibrated defect anomaly priority score on a 0-100 scale.
    If verdict is 'NORMAL' or no defect area is detected with baseline scores,
    returns 0.0 (nominal). Classification confidence is decoupled from defect severity.
    """
    if verdict == "NORMAL":
        return 0.0

    area_capped = min(float(defect_area_pct), 100.0)
    if area_capped <= 0.0 and anomaly_norm <= 25.0:
        return 0.0

    score = (w_anomaly * float(anomaly_norm)) + (w_area * area_capped)
    return float(np.clip(score, 0.0, 100.0))


def bucket_severity(score, verdict=None):
    if verdict == "NORMAL" or score <= 0.0:
        return "Normal"
    elif score < 40:
        return "Minor"
    elif score < 75:
        return "Moderate"
    else:
        return "Critical"
