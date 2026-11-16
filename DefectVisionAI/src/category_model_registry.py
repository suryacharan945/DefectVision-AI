"""
DefectVision AI — Category Model Registry
Centralized registry managing model configurations, memory banks, calibrated thresholds,
and feature extractors across all 15 official MVTec AD categories.
"""

import os
import json
import numpy as np

KNOWN_CATEGORIES = [
    "bottle", "cable", "capsule", "carpet", "grid",
    "hazelnut", "leather", "metal_nut", "pill", "screw",
    "tile", "toothbrush", "transistor", "wood", "zipper"
]

CATEGORY_TYPE = {
    "bottle": "object", "cable": "object", "capsule": "object", "carpet": "texture",
    "grid": "texture", "hazelnut": "object", "leather": "texture", "metal_nut": "object",
    "pill": "object", "screw": "object", "tile": "texture", "toothbrush": "object",
    "transistor": "object", "wood": "texture", "zipper": "object"
}

class CategoryModelRegistry:
    def __init__(self, models_dir=None, threshold_json=None):
        if models_dir is None:
            models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
        self.models_dir = models_dir
        self.patchcore_dir = os.path.join(models_dir, "patchcore")
        self.category_classifier_dir = os.path.join(models_dir, "category_classifier")
        
        self.thresholds = {}
        if threshold_json and os.path.exists(threshold_json):
            with open(threshold_json, "r", encoding="utf-8") as f:
                self.thresholds = json.load(f)
        else:
            default_thresh = os.path.join(self.patchcore_dir, "category_thresholds.json")
            if os.path.exists(default_thresh):
                with open(default_thresh, "r", encoding="utf-8") as f:
                    self.thresholds = json.load(f)

        self.registry = self._build_registry()

    def _build_registry(self):
        reg = {}
        for cat in KNOWN_CATEGORIES:
            mb_path = os.path.join(self.patchcore_dir, cat, "memory_bank.npy")
            has_mb = os.path.exists(mb_path)
            tokens = 0
            feat_dim = 0
            if has_mb:
                try:
                    mb = np.load(mb_path, mmap_mode="r")
                    tokens, feat_dim = mb.shape
                except Exception:
                    pass

            thresh_meta = self.thresholds.get(cat, {})
            cal_thresh = thresh_meta.get("calibrated_threshold", 1.7452)
            base_mean = thresh_meta.get("baseline_mean", 1.25)
            base_std = thresh_meta.get("baseline_std", 0.18)
            base_p99 = thresh_meta.get("baseline_p99", 1.65)

            reg[cat] = {
                "category_id": cat,
                "category_type": CATEGORY_TYPE.get(cat, "unknown"),
                "model_version": "v1.0.0-audited",
                "backbone": "ResNet-18 (IMAGENET1K_V1)",
                "feature_layers": ["layer2", "layer3"],
                "grid_size": 28,
                "input_resolution": [224, 224],
                "memory_bank_path": mb_path,
                "memory_bank_available": has_mb,
                "memory_bank_tokens": tokens,
                "feature_dimension": feat_dim,
                "calibrated_threshold": cal_thresh,
                "baseline_mean": base_mean,
                "baseline_std": base_std,
                "baseline_p99": base_p99,
                "status": "READY" if has_mb else "UNAVAILABLE",
                "training_split": "train_registration (80% nominal)",
                "calibration_split": "calibration_validation (20% nominal)"
            }
        return reg

    def get_category_config(self, category):
        return self.registry.get(category, None)

    def get_all_categories(self):
        return KNOWN_CATEGORIES

    def get_model_status_summary(self):
        summary = {}
        for cat, meta in self.registry.items():
            summary[cat] = {
                "status": meta["status"],
                "type": meta["category_type"],
                "threshold": meta["calibrated_threshold"],
                "tokens": meta["memory_bank_tokens"]
            }
        return summary

    def get_models_status(self):
        status = {}
        for cat, meta in self.registry.items():
            status[cat] = {
                "is_ready": meta["memory_bank_available"],
                "status": meta["status"],
                "category_type": meta["category_type"],
                "calibrated_threshold": meta["calibrated_threshold"],
                "baseline_mean": meta["baseline_mean"],
                "baseline_p99": meta["baseline_p99"],
                "tokens": meta["memory_bank_tokens"]
            }
        return status
