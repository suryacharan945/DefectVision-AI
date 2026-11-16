"""
DefectVision AI — Regression Test Suite: Case B (Unknown Category / OOD Rejection)
Validates that out-of-distribution, non-MVTec AD items (e.g., ceiling fan, furniture, noise, solid surfaces):
1. Are rejected by CategoryRecognitionService multi-criterion OOD gating:
   - Softmax Confidence, Normalized Entropy, Free Energy Score, Prototype Cosine Similarity.
2. Are returned with is_supported=False and status='UNSUPPORTED_OR_UNCERTAIN'.
3. PatchCore is NEVER invoked for unsupported categories (model_selected="None").
4. Verdict is strictly "UNSUPPORTED" and conclusion is "UNSUPPORTED OR UNKNOWN CATEGORY".
5. Telemetry safely reports anomaly_score=0.0, defect_area_pct=0.0, severity_score=0.0.
"""

import os
import sys
import unittest
import cv2
import numpy as np
from io import BytesIO
from fastapi.testclient import TestClient

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "DefectVisionAI"))

from app import app, get_optical_engine
from src.category_classifier import CategoryRecognitionService

client = TestClient(app)


def encode_image(img_bgr, ext=".png"):
    _, buf = cv2.imencode(ext, img_bgr)
    return BytesIO(buf.tobytes())


def generate_ceiling_fan():
    """Generates synthetic 3-blade ceiling fan mounted on ceiling."""
    img = np.full((400, 400, 3), 220, dtype=np.uint8)
    cv2.circle(img, (200, 200), 40, (50, 50, 50), -1)
    cv2.circle(img, (200, 200), 15, (30, 30, 30), -1)
    for angle in [0, 120, 240]:
        cv2.ellipse(img, (200, 200), (140, 25), angle, 0, 360, (70, 70, 70), -1)
    return img


def generate_office_desk():
    """Generates synthetic office desk scene with monitor and keyboard."""
    img = np.full((400, 400, 3), 180, dtype=np.uint8)
    # Desk surface
    cv2.rectangle(img, (20, 250), (380, 390), (120, 90, 60), -1)
    # Monitor
    cv2.rectangle(img, (100, 60), (300, 210), (30, 30, 30), -1)
    cv2.rectangle(img, (110, 70), (290, 200), (200, 220, 240), -1)
    cv2.rectangle(img, (190, 210), (210, 250), (80, 80, 80), -1)
    # Keyboard
    cv2.rectangle(img, (120, 270), (280, 320), (50, 50, 50), -1)
    return img


def generate_coffee_mug():
    """Generates synthetic ceramic coffee mug with handle."""
    img = np.full((350, 350, 3), 235, dtype=np.uint8)
    # Mug body
    cv2.rectangle(img, (100, 100), (220, 260), (20, 80, 220), -1)
    cv2.ellipse(img, (160, 260), (60, 20), 0, 0, 180, (15, 60, 180), -1)
    cv2.ellipse(img, (160, 100), (60, 20), 0, 0, 360, (30, 100, 240), -1)
    cv2.ellipse(img, (160, 100), (50, 15), 0, 0, 360, (50, 30, 10), -1)
    # Handle
    cv2.ellipse(img, (220, 180), (30, 45), 0, 270, 90, (20, 80, 220), 12)
    return img


class TestUnknownCategoryRejection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = get_optical_engine()
        cls.cat_service = cls.engine.category_service

    def test_classifier_multi_criterion_ood_rejection(self):
        """Validates that CategoryRecognitionService rejects diverse non-MVTec inputs."""
        test_cases = [
            ("ceiling_fan", generate_ceiling_fan()),
            ("office_desk", generate_office_desk()),
            ("coffee_mug", generate_coffee_mug()),
            ("random_noise", np.random.randint(0, 256, (300, 300, 3), dtype=np.uint8)),
            ("solid_black", np.zeros((300, 300, 3), dtype=np.uint8)),
            ("solid_white", np.full((300, 300, 3), 255, dtype=np.uint8)),
            ("solid_gray", np.full((300, 300, 3), 128, dtype=np.uint8)),
        ]

        for name, img in test_cases:
            pred = self.cat_service.predict(img)
            self.assertFalse(
                pred["is_supported"],
                f"OOD test case '{name}' was falsely accepted! Telemetry: {pred}"
            )
            self.assertEqual(pred["category"], "unknown")
            self.assertEqual(pred["status"], "UNSUPPORTED_OR_UNCERTAIN")

    def test_ceiling_fan_end_to_end_inspection_rejection(self):
        """Case B reproduction: Ceiling fan must yield UNSUPPORTED without invoking PatchCore."""
        fan_img = generate_ceiling_fan()
        res = self.engine.inspect_frame(fan_img, operator_category_override=None, mode="live")

        # Must reject category
        self.assertEqual(res["category"], "unsupported")
        self.assertEqual(res["verdict"], "UNSUPPORTED")
        self.assertEqual(res["conclusion"], "UNSUPPORTED OR UNKNOWN CATEGORY")

        # PatchCore must NEVER be invoked
        self.assertEqual(res["model_selected"], "None")
        self.assertEqual(res["anomaly_score"], 0.0)
        self.assertEqual(res["defect_area_pct"], 0.0)
        self.assertEqual(res["severity_score"], 0.0)
        self.assertEqual(res["severity_level"], "unsupported")
        self.assertEqual(res["defect_type"], "unsupported")

    def test_upload_endpoint_ood_rejection(self):
        """FastAPI /predict upload with ceiling fan rejects as UNSUPPORTED."""
        fan_img = generate_ceiling_fan()
        buf = encode_image(fan_img)

        res = client.post("/predict", files={"file": ("fan.png", buf, "image/png")})
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertEqual(data["verdict"], "UNSUPPORTED")
        self.assertEqual(data["conclusion"], "UNSUPPORTED OR UNKNOWN CATEGORY")
        self.assertEqual(data["category"], "unsupported")
        self.assertEqual(data["model_selected"], "None")
        self.assertEqual(data["anomaly_score"], 0.0)
        self.assertEqual(data["defect_area_pct"], 0.0)
        self.assertEqual(data["severity_score"], 0.0)

    def test_live_camera_endpoint_ood_rejection(self):
        """FastAPI /api/optical-inspection/inspect-frame with office scene rejects as UNSUPPORTED."""
        desk_img = generate_office_desk()
        buf = encode_image(desk_img)

        res = client.post(
            "/api/optical-inspection/inspect-frame",
            files={"frame": ("desk.png", buf, "image/png")},
            data={"operator_override": "auto"}
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertEqual(data["verdict"], "UNSUPPORTED")
        self.assertEqual(data["conclusion"], "UNSUPPORTED OR UNKNOWN CATEGORY")
        self.assertEqual(data["model_selected"], "None")


if __name__ == "__main__":
    unittest.main()
