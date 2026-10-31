"""
DefectVision AI — Research Experimentation Foundation
Modular framework for selective human review, risk-coverage analysis, and baseline benchmarking.
"""

from .selective_review import (
    compute_margin_uncertainty,
    compute_distance_to_threshold,
    simulate_selective_review,
    compute_risk_coverage_curve,
    compute_bootstrap_ci
)

__all__ = [
    "compute_margin_uncertainty",
    "compute_distance_to_threshold",
    "simulate_selective_review",
    "compute_risk_coverage_curve",
    "compute_bootstrap_ci"
]
