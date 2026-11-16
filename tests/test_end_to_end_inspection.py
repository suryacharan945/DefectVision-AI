"""
DefectVision AI — End-to-End Unified Inspection Pipeline Test Suite
Validates:
1. Image Upload (/predict) with category="auto" (default) and operator override.
2. Live Camera (/api/optical-inspection/inspect-frame).
3. 4-State Verdicts and Standardized Conclusions:
   - NORMAL -> "NO DEFECT DETECTED"
   - DEFECTIVE -> "POSSIBLE DEFECT DETECTED"
   - REVIEW REQUIRED -> "MANUAL INSPECTION REQUIRED"
   - UNSUPPORTED -> "UNSUPPORTED OR UNKNOWN CATEGORY"
4. Standardized Limitation Disclaimer in diagnosis text:
   "The result reflects the model's learned visual patterns and does not guarantee the absence of all possible defects."
5. Image Quality Gates (Blur, Underexposure, Contrast).
6. Non-MVTec out-of-distribution unknown object rejection.
"""

import os
import sys
import unittest
import numpy as np
import cv2
from io import BytesIO
from fastapi.testclient import TestClient

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "DefectVisionAI"))

from app import app, get_optical_engine
from src.camera_service import DISCLAIMER, CONCLUSION_MAP

client = TestClient(app)


def encode_image_bytes(img_bgr, ext=".jpg"):
    _, buffer = cv2.imencode(ext, img_bgr)
    return BytesIO(buffer.tobytes())


class TestUnifiedInspectionPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = get_optical_engine()
        # Find real sample images from MVTec dataset
        dataset_base = os.path.join(PROJECT_ROOT, "DefectVisionAI", "dataset", "raw", "mvtec")
        cls.sample_bottle_normal = os.path.join(dataset_base, "bottle", "test", "good", "000.png")
        cls.sample_bottle_broken = os.path.join(dataset_base, "bottle", "test", "broken_large", "000.png")
        cls.sample_screw_scratch = os.path.join(dataset_base, "screw", "test", "scratch_neck", "000.png")

    def test_upload_inspection_schema_and_defaults(self):
        """Tests /predict upload with default category='auto'."""
        if os.path.exists(self.sample_bottle_normal):
            img = cv2.imread(self.sample_bottle_normal)
        else:
            img = np.full((300, 300, 3), 120, dtype=np.uint8)
            cv2.circle(img, (150, 150), 60, (200, 200, 200), -1)

        buf = encode_image_bytes(img)
        # category not passed -> defaults to 'auto'
        res = client.post("/predict", files={"file": ("test.jpg", buf, "image/jpeg")})
        self.assertEqual(res.status_code, 200)
        data = res.json()

        # Validate mandatory schema fields
        self.assertIn("inspection_id", data)
        self.assertEqual(data["mode"], "upload")
        self.assertIn("category", data)
        self.assertIn("category_type", data)
        self.assertIn("category_confidence", data)
        self.assertIn("image_quality", data)
        self.assertIn("model_id", data)
        self.assertIn("model_version", data)
        self.assertIn("anomaly_score", data)
        self.assertIn("anomaly_threshold", data)
        self.assertIn("verdict", data)
        self.assertIn("conclusion", data)
        self.assertIn("heatmap_url", data)
        self.assertIn("annotated_image_url", data)
        self.assertIn("original_image", data)
        self.assertIn("raw_heatmap", data)
        self.assertIn("inference_latency_ms", data)
        self.assertIn("diagnosis", data)

        # Validate disclaimer in diagnosis
        self.assertIn(DISCLAIMER, data["diagnosis"])
        # Validate verdict is one of the 4 valid states
        self.assertIn(data["verdict"], ["NORMAL", "DEFECTIVE", "REVIEW REQUIRED", "UNSUPPORTED"])
        self.assertEqual(data["conclusion"], CONCLUSION_MAP[data["verdict"]])

    def test_upload_inspection_manual_override(self):
        """Tests /predict upload with explicit operator category override."""
        if os.path.exists(self.sample_bottle_normal):
            img = cv2.imread(self.sample_bottle_normal)
        else:
            img = np.full((300, 300, 3), 120, dtype=np.uint8)
            cv2.circle(img, (150, 150), 60, (200, 200, 200), -1)

        buf = encode_image_bytes(img)
        res = client.post(
            "/predict",
            files={"file": ("test.jpg", buf, "image/jpeg")},
            data={"category": "bottle"}
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["category"], "bottle")
        self.assertEqual(data["category_status"], "OPERATOR_OVERRIDE")
        self.assertIn("PatchCore-Bottle", data["model_id"])

    def test_live_camera_frame_inspection(self):
        """Tests live frame optical inspection endpoint."""
        if os.path.exists(self.sample_bottle_broken):
            img = cv2.imread(self.sample_bottle_broken)
        else:
            img = np.full((300, 300, 3), 120, dtype=np.uint8)
            cv2.circle(img, (150, 150), 60, (200, 200, 200), -1)

        buf = encode_image_bytes(img)
        res = client.post(
            "/api/optical-inspection/inspect-frame",
            files={"frame": ("frame.jpg", buf, "image/jpeg")},
            data={"operator_override": "bottle"}
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["mode"], "live")
        self.assertIn(data["verdict"], ["NORMAL", "DEFECTIVE", "REVIEW REQUIRED", "UNSUPPORTED"])
        self.assertEqual(data["conclusion"], CONCLUSION_MAP[data["verdict"]])
        self.assertIn(DISCLAIMER, data["diagnosis"])

    def test_quality_gate_blurred_frame_rejection(self):
        """Heavily blurred frame should trigger REVIEW REQUIRED."""
        blurred = np.full((300, 300, 3), 120, dtype=np.uint8)
        # Uniform solid color has ~0 Laplacian variance
        buf = encode_image_bytes(blurred)
        res = client.post(
            "/predict",
            files={"file": ("blur.jpg", buf, "image/jpeg")},
            data={"category": "bottle"}
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["verdict"], "REVIEW REQUIRED")
        self.assertEqual(data["conclusion"], "MANUAL INSPECTION REQUIRED")
        self.assertIn("quality failure", data["review_reason"].lower())
        self.assertIn(DISCLAIMER, data["diagnosis"])

    def test_quality_gate_underexposed_frame_rejection(self):
        """Pitch-dark frame should trigger REVIEW REQUIRED with UNDEREXPOSED."""
        dark = np.zeros((300, 300, 3), dtype=np.uint8)
        buf = encode_image_bytes(dark)
        res = client.post(
            "/api/optical-inspection/inspect-frame",
            files={"frame": ("dark.jpg", buf, "image/jpeg")},
            data={"operator_override": "auto"}
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["verdict"], "REVIEW REQUIRED")
        self.assertEqual(data["conclusion"], "MANUAL INSPECTION REQUIRED")
        self.assertIn("quality failure", data["review_reason"].lower())

    def test_unknown_out_of_distribution_object(self):
        """Random noise / unrepresented texture without override should trigger UNSUPPORTED."""
        rng = np.random.RandomState(42)
        noise = rng.randint(0, 256, (300, 300, 3), dtype=np.uint8)
        buf = encode_image_bytes(noise)

        # Automatic category recognition on noise should reject as unsupported/uncertain
        res = client.post(
            "/predict",
            files={"file": ("noise.jpg", buf, "image/jpeg")},
            data={"category": "auto"}
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        # Should be UNSUPPORTED (or REVIEW REQUIRED if noise tripped quality contrast gate)
        self.assertIn(data["verdict"], ["UNSUPPORTED", "REVIEW REQUIRED"])
        self.assertEqual(data["conclusion"], CONCLUSION_MAP[data["verdict"]])
        self.assertIn(DISCLAIMER, data["diagnosis"])

    def test_invalid_category_override_returns_400(self):
        """Non-existent category name should be rejected by input validation."""
        img = np.full((100, 100, 3), 120, dtype=np.uint8)
        buf = encode_image_bytes(img)
        res = client.post(
            "/predict",
            files={"file": ("test.jpg", buf, "image/jpeg")},
            data={"category": "aeroplane_not_mvtec"}
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("Unknown category", res.json()["detail"])


if __name__ == "__main__":
    unittest.main()
