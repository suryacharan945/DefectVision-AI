"""
DefectVision AI — Auditable Decision Fusion Service
Combines optical quality validation, category recognition confidence,
category-specific PatchCore anomaly scoring, and conditional supervised classification.
Evaluates explicit decision states: NORMAL, DEFECTIVE, REVIEW_REQUIRED, UNSUPPORTED.
"""

class DecisionFusionService:
    def __init__(self, borderline_margin=0.08):
        """
        borderline_margin: fractional score band around calibrated threshold
        [T * (1 - margin), T * (1 + margin)] flagged for REVIEW_REQUIRED.
        """
        self.borderline_margin = borderline_margin

    def evaluate_inspection(
        self,
        quality_is_valid,
        quality_status,
        category_result,
        anomaly_score,
        calibrated_threshold,
        effnet_prob_defective=None,
        supported_effnet_category=False
    ):
        """
        Computes final operational inspection verdict.
        Returns: (verdict: str, severity_level: str, review_reason: str, telemetry: dict)
        """
        # 1. Image Quality Gate
        if not quality_is_valid:
            return (
                "REVIEW REQUIRED",
                "review",
                f"Image Quality Gate Failed: {quality_status}",
                {"quality_status": quality_status, "rejection_stage": "IMAGE_QUALITY"}
            )

        # 2. Category Recognition Gate
        is_supported = category_result.get("is_supported", False)
        category = category_result.get("category", "unknown")
        category_conf = category_result.get("confidence", 0.0)

        if not is_supported or category == "unknown":
            return (
                "UNSUPPORTED",
                "unsupported",
                f"Unsupported or uncertain object category (Confidence: {category_conf:.2%}, Status: {category_result.get('status', 'UNCERTAIN')})",
                {"category_result": category_result, "rejection_stage": "CATEGORY_RECOGNITION"}
            )

        # 3. PatchCore Anomaly Decision
        patchcore_defective = bool(anomaly_score > calibrated_threshold)

        # Borderline threshold band
        lower_borderline = calibrated_threshold * (1.0 - self.borderline_margin)
        upper_borderline = calibrated_threshold * (1.0 + self.borderline_margin)
        is_borderline = (lower_borderline <= anomaly_score <= upper_borderline)

        # 4. Supervised EfficientNet decision (only if category is supported by classifier)
        effnet_defective = None
        has_effnet_conflict = False
        if supported_effnet_category and effnet_prob_defective is not None:
            effnet_defective = bool(effnet_prob_defective >= 0.50)
            if effnet_defective != patchcore_defective:
                has_effnet_conflict = True

        # 5. Determine State
        if is_borderline:
            return (
                "REVIEW REQUIRED",
                "moderate",
                f"Borderline anomaly score {anomaly_score:.4f} within ±{self.borderline_margin*100:.0f}% of threshold {calibrated_threshold:.4f}",
                {
                    "anomaly_score": anomaly_score,
                    "calibrated_threshold": calibrated_threshold,
                    "is_borderline": True,
                    "rejection_stage": "BORDERLINE_SCORE"
                }
            )

        if has_effnet_conflict:
            return (
                "REVIEW REQUIRED",
                "moderate",
                f"Conflicting model outputs: PatchCore={'DEFECTIVE' if patchcore_defective else 'NORMAL'} vs EfficientNet={'DEFECTIVE' if effnet_defective else 'NORMAL'}",
                {
                    "anomaly_score": anomaly_score,
                    "calibrated_threshold": calibrated_threshold,
                    "effnet_prob": effnet_prob_defective,
                    "rejection_stage": "MODEL_CONFLICT"
                }
            )

        if patchcore_defective:
            # Determine severity level
            rel_ratio = anomaly_score / calibrated_threshold if calibrated_threshold > 0 else 1.0
            if rel_ratio >= 1.50:
                sev_level = "critical"
            else:
                sev_level = "moderate"

            return (
                "DEFECTIVE",
                sev_level,
                "",
                {
                    "anomaly_score": anomaly_score,
                    "calibrated_threshold": calibrated_threshold,
                    "rel_ratio": round(rel_ratio, 2),
                    "rejection_stage": "NONE"
                }
            )

        # Nominal pass
        return (
            "NORMAL",
            "normal",
            "",
            {
                "anomaly_score": anomaly_score,
                "calibrated_threshold": calibrated_threshold,
                "rejection_stage": "NONE"
            }
        )
