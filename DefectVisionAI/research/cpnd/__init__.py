"""
CPND Package: Calibrated Patch-Neighborhood Dispersion
DefectVision AI — Phase 7B
"""

from .cpnd_core import (
    CPNDScorer,
    rank_and_select_budget,
    evaluate_selective_review
)

__all__ = [
    "CPNDScorer",
    "rank_and_select_budget",
    "evaluate_selective_review"
]
