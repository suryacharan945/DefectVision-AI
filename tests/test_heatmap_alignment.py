"""
DefectVision AI — Heatmap Alignment & Validation Test Suite
Validates:
1. Spatial dimension alignment: heatmap overlay matches input image (H, W).
2. Aspect ratio preservation and ROI composition alignment.
3. Absence of discrete circular patch-center artifacts (verified via continuous Gaussian smoothing).
4. Threshold-grounded calibration:
   - Nominal bottle: zero pixels exceed anomaly threshold, overlay is clean and uncorrupted.
   - Defective bottle: anomalous region is properly highlighted with peak exceeding threshold.
"""

import os
import sys
import unittest
import cv2
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "DefectVisionAI"))

from app import get_optical_engine
from src.patchcore import calibrate_score_map, overlay_heatmap, normalize_map


class TestHeatmapAlignmentAndValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = get_optical_engine()
        dataset_base = os.path.join(PROJECT_ROOT, "DefectVisionAI", "dataset", "raw", "mvtec", "bottle", "test")
        cls.normal_bottle = os.path.join(dataset_base, "good", "000.png")
        cls.broken_bottle = os.path.join(dataset_base, "broken_large", "000.png")
        if not os.path.exists(cls.normal_bottle) or not os.path.exists(cls.broken_bottle):
            raise unittest.SkipTest("MVTec AD bottle test dataset not present.")

    def test_heatmap_dimension_and_aspect_ratio_alignment(self):
        """Verifies that full overlay matches non-square input dimensions."""
        # Non-square image (480 x 640)
        img = cv2.imread(self.normal_bottle)
        h, w = img.shape[:2]

        res = self.engine.inspect_frame(img, mode="upload")

        self.assertIn("heatmap_url", res)
        self.assertIn("original_image", res)
        self.assertEqual(res["verdict"], "NORMAL")

        # Decode base64 overlay
        import base64
        overlay_b64 = res["heatmap_base64"].split(",")[-1]
        overlay_bytes = base64.b64decode(overlay_b64)
        nparr = np.frombuffer(overlay_bytes, np.uint8)
        decoded_overlay = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        self.assertEqual(
            decoded_overlay.shape[:2], (h, w),
            f"Heatmap overlay shape {decoded_overlay.shape[:2]} does not match input {(h, w)}"
        )

    def test_absence_of_circular_patch_grid_artifacts(self):
        """
        Verifies that distance maps smoothed with Gaussian filter (sigma=4 on 224x224)
        do not exhibit high-frequency discrete patch-grid spikes.
        """
        # Create a synthetic 28x28 distance map with an isolated patch spike
        raw_grid = np.full((28, 28), 0.8, dtype=np.float32)
        raw_grid[14, 14] = 2.5  # single patch spike

        cal_map = calibrate_score_map(raw_grid, threshold=1.5, baseline_mean=1.0)

        # In a smoothed map, adjacent pixel step differences must be smooth (< 0.15)
        diff_y = np.max(np.abs(np.diff(cal_map, axis=0)))
        diff_x = np.max(np.abs(np.diff(cal_map, axis=1)))
        max_step = float(max(diff_y, diff_x))

        self.assertLess(max_step, 0.15, f"Discontinuous patch cliff detected: max step {max_step:.4f}")

    def test_nominal_specimen_has_clean_overlay(self):
        """Verifies that nominal bottle has 0% defect area and clean overlay without red spots."""
        img = cv2.imread(self.normal_bottle)
        res = self.engine.inspect_frame(img, mode="upload")

        self.assertEqual(res["verdict"], "NORMAL")
        self.assertEqual(res["defect_area_pct"], 0.0)
        self.assertEqual(res["severity_score"], 0.0)

        # Decode raw heatmap and verify no red hot-spots
        import base64
        raw_hm_b64 = res["raw_heatmap"].split(",")[-1]
        raw_hm_bytes = base64.b64decode(raw_hm_b64)
        raw_hm = cv2.imdecode(np.frombuffer(raw_hm_bytes, np.uint8), cv2.IMREAD_COLOR)

        # In nominal mode, raw_hm is clean image (no red jet artifacts)
        # Check that red channel is not artificially boosted over green/blue
        diff = cv2.absdiff(raw_hm, img)
        self.assertLess(float(diff.mean()), 5.0, "Nominal specimen image was altered with false defect overlays!")

    def test_defective_specimen_heatmap_localization(self):
        """Verifies that defective bottle localizes defect with significant defect area."""
        img = cv2.imread(self.broken_bottle)
        res = self.engine.inspect_frame(img, mode="upload")

        self.assertEqual(res["verdict"], "DEFECTIVE")
        self.assertGreater(res["anomaly_score"], res["calibrated_threshold"])
        self.assertGreater(res["defect_area_pct"], 10.0)
        self.assertIn(res["severity_level"], ["moderate", "critical"])


if __name__ == "__main__":
    unittest.main()
