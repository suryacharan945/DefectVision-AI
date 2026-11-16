"""
DefectVision AI — Regression Test Suite: Case A (Normal Bottle Inspection)
Validates that clear, nominal transparent bottle specimens from the official MVTec AD dataset:
1. Are automatically recognized as 'bottle' with high confidence.
2. Are evaluated by the Bottle PatchCore memory bank without false defect alarms.
3. Yield strictly verdict="NORMAL" and conclusion="NO DEFECT DETECTED".
4. Report anomaly score below the calibrated decision threshold (1.4666).
5. Report defect_area_pct == 0.0% (no spurious defect area).
6. Report severity_score == 0.0 and severity_level == "normal" (no spurious Critical 94.0 claims).
7. Do not invent semantic physical defect labels like "Sidewall Structural Fracture".
"""

import os
import sys
import glob
import unittest
import cv2
import numpy as np
from io import BytesIO
from fastapi.testclient import TestClient

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "DefectVisionAI"))

from app import app, get_optical_engine

client = TestClient(app)


def encode_image(img_bgr, ext=".png"):
    _, buf = cv2.imencode(ext, img_bgr)
    return BytesIO(buf.tobytes())


class TestNormalBottleRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = get_optical_engine()
        cls.dataset_dir = os.path.join(
            PROJECT_ROOT, "DefectVisionAI", "dataset", "raw", "mvtec", "bottle", "test", "good"
        )
        cls.bottle_files = sorted(glob.glob(os.path.join(cls.dataset_dir, "*.png")))
        if not cls.bottle_files:
            raise unittest.SkipTest(f"MVTec AD bottle test dataset not present in {cls.dataset_dir}")

    def test_nominal_bottles_batch_evaluation(self):
        """Tests multiple nominal bottle images from official MVTec AD test/good split."""
        # Test first 10 nominal specimens
        eval_samples = self.bottle_files[:10]
        self.assertGreaterEqual(len(eval_samples), 5, "Should have at least 5 nominal bottle images to test.")

        for fp in eval_samples:
            img = cv2.imread(fp)
            self.assertIsNotNone(img, f"Failed to load image from {fp}")

            res = self.engine.inspect_frame(img, operator_category_override=None, mode="upload")

            # 1. Automatic category recognition must recognize 'bottle'
            self.assertEqual(res["category"], "bottle", f"Image {fp} was misclassified as {res['category']}")
            self.assertGreaterEqual(res["category_confidence"], 0.70, f"Confidence too low on {fp}")

            # 2. PatchCore routing
            self.assertEqual(res["model_selected"], "PatchCore-Bottle-MemoryBank")
            self.assertAlmostEqual(res["calibrated_threshold"], 1.4666, places=3)

            # 3. Score must be below calibrated threshold
            self.assertLess(
                res["anomaly_score"],
                res["calibrated_threshold"],
                f"Anomaly score {res['anomaly_score']} falsely exceeded threshold {res['calibrated_threshold']} on {fp}"
            )

            # 4. Strict Normal Verdict & Standardized Conclusion
            self.assertEqual(res["verdict"], "NORMAL", f"Expected NORMAL on {fp}, got {res['verdict']}")
            self.assertEqual(res["conclusion"], "NO DEFECT DETECTED")

            # 5. Defect Area must be 0.0%
            self.assertEqual(
                res["defect_area_pct"], 0.0,
                f"Spurious defect area {res['defect_area_pct']}% reported on pristine bottle {fp}"
            )

            # 6. Severity must be 0.0 and normal (never Critical 94.0)
            self.assertEqual(
                res["severity_score"], 0.0,
                f"Spurious severity score {res['severity_score']} reported on pristine bottle {fp}"
            )
            self.assertEqual(res["severity_level"], "normal")

            # 7. Defect type must be 'normal' (never 'Sidewall Structural Fracture')
            self.assertEqual(res["defect_type"], "normal")
            self.assertNotIn("fracture", res.get("defect_type", "").lower())
            self.assertNotIn("crack", res.get("defect_type", "").lower())

    def test_upload_api_endpoint_normal_bottle(self):
        """Tests FastAPI /predict endpoint with official normal bottle specimen."""
        fp = self.bottle_files[0]
        img = cv2.imread(fp)
        buf = encode_image(img)

        # Default category='auto'
        res = client.post("/predict", files={"file": ("bottle.png", buf, "image/png")})
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertEqual(data["category"], "bottle")
        self.assertEqual(data["verdict"], "NORMAL")
        self.assertEqual(data["conclusion"], "NO DEFECT DETECTED")
        self.assertEqual(data["defect_area_pct"], 0.0)
        self.assertEqual(data["severity_score"], 0.0)
        self.assertEqual(data["severity_level"], "normal")
        self.assertEqual(data["defect_type"], "normal")

    def test_live_camera_api_endpoint_normal_bottle(self):
        """Tests FastAPI /api/optical-inspection/inspect-frame with official normal bottle."""
        fp = self.bottle_files[0]
        img = cv2.imread(fp)
        buf = encode_image(img)

        res = client.post(
            "/api/optical-inspection/inspect-frame",
            files={"frame": ("frame.png", buf, "image/png")},
            data={"operator_override": "auto"}
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertEqual(data["category"], "bottle")
        self.assertEqual(data["verdict"], "NORMAL")
        self.assertEqual(data["conclusion"], "NO DEFECT DETECTED")
        self.assertEqual(data["defect_area_pct"], 0.0)
        self.assertEqual(data["severity_score"], 0.0)
        self.assertEqual(data["severity_level"], "normal")


if __name__ == "__main__":
    unittest.main()
