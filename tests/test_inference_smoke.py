"""
DefectVision AI — End-to-End Real Inference Smoke Test Suite
Validates the full ML inference pipeline on actual genuine specimens and synthetic edge cases:
1. Normal genuine specimen: Automatic recognition, score < threshold, verdict NORMAL, defect_area 0.0%
2. Defective genuine specimen: Automatic recognition, score > threshold, verdict DEFECTIVE, valid heatmap
3. Texture category specimen: Router dispatches to texture memory bank, valid finite score and threshold
4. Object category specimen: Router dispatches to object memory bank, valid finite score and threshold
5. Out-of-distribution (OOD) image: Shannon entropy & Free Energy rejection, verdict UNSUPPORTED, model None
6. Corrupted/Empty image: Quality gate safely returns verdict REVIEW REQUIRED
7. API HTTP endpoints: End-to-end multipart form verification on /predict and /api/inspect-frame
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

import app
from app import app as fastapi_app, get_optical_engine

client = TestClient(fastapi_app)

NOMINAL_BOTTLE_PATH = os.path.join(
    PROJECT_ROOT, "release", "portfolio_handover", "assets", "04_genuine_specimen_raw_bottle_nominal.png"
)
DEFECTIVE_BOTTLE_PATH = os.path.join(
    PROJECT_ROOT, "release", "portfolio_handover", "assets", "01_genuine_specimen_raw_bottle_defective.png"
)
TILE_SAMPLE_PATH = os.path.join(
    PROJECT_ROOT, "DefectVisionAI", "outputs", "similarity_search_samples", "tile_similarity_demo.png"
)
NUT_SAMPLE_PATH = os.path.join(
    PROJECT_ROOT, "DefectVisionAI", "outputs", "similarity_search_samples", "metal_nut_similarity_demo.png"
)


def encode_image_bytes(img_bgr, ext=".png"):
    _, buf = cv2.imencode(ext, img_bgr)
    return BytesIO(buf.tobytes())


class TestInferenceSmoke(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = get_optical_engine()

    def test_01_nominal_bottle_inference(self):
        """Scenario 1: Nominal specimen -> Category recognized, score < threshold, verdict NORMAL."""
        self.assertTrue(os.path.exists(NOMINAL_BOTTLE_PATH), f"Missing asset: {NOMINAL_BOTTLE_PATH}")
        img = cv2.imread(NOMINAL_BOTTLE_PATH)
        self.assertIsNotNone(img, "Failed to load nominal bottle image.")

        result = self.engine.inspect_frame(img, operator_category_override=None, mode="upload")

        # Telemetry assertions
        self.assertEqual(result["category"], "bottle")
        self.assertEqual(result["category_type"], "object")
        self.assertGreaterEqual(result["category_confidence"], 0.70)
        self.assertEqual(result["model_selected"], "PatchCore-Bottle-MemoryBank")
        self.assertAlmostEqual(result["calibrated_threshold"], 1.4666, places=3)
        self.assertLess(result["anomaly_score"], result["calibrated_threshold"])
        self.assertEqual(result["verdict"], "NORMAL")
        self.assertEqual(result["conclusion"], "NO DEFECT DETECTED")
        self.assertEqual(result["defect_area_pct"], 0.0)
        self.assertEqual(result["severity_score"], 0.0)
        self.assertEqual(result["severity_level"], "normal")
        self.assertGreater(result["inference_latency_ms"], 0.0)
        self.assertIn("does not guarantee", result["diagnosis"])

    def test_02_defective_bottle_inference(self):
        """Scenario 2: Defective specimen -> Category recognized, score > threshold, verdict DEFECTIVE."""
        self.assertTrue(os.path.exists(DEFECTIVE_BOTTLE_PATH), f"Missing asset: {DEFECTIVE_BOTTLE_PATH}")
        img = cv2.imread(DEFECTIVE_BOTTLE_PATH)
        self.assertIsNotNone(img, "Failed to load defective bottle image.")

        result = self.engine.inspect_frame(img, operator_category_override=None, mode="upload")

        # Telemetry assertions
        self.assertEqual(result["category"], "bottle")
        self.assertEqual(result["category_type"], "object")
        self.assertGreaterEqual(result["category_confidence"], 0.70)
        self.assertEqual(result["model_selected"], "PatchCore-Bottle-MemoryBank")
        self.assertAlmostEqual(result["calibrated_threshold"], 1.4666, places=3)
        self.assertGreater(result["anomaly_score"], result["calibrated_threshold"])
        self.assertEqual(result["verdict"], "DEFECTIVE")
        self.assertEqual(result["conclusion"], "POSSIBLE DEFECT DETECTED")
        self.assertGreater(result["defect_area_pct"], 0.0)
        self.assertGreater(result["severity_score"], 0.0)
        self.assertIn(result["severity_level"], ["moderate", "critical"])
        self.assertTrue(result["heatmap_base64"].startswith("data:image/jpeg;base64,"))
        self.assertGreater(result["inference_latency_ms"], 0.0)
        self.assertIn("does not guarantee", result["diagnosis"])

    def test_03_texture_category_inference(self):
        """Scenario 3: Texture category specimen (tile) with operator override."""
        self.assertTrue(os.path.exists(TILE_SAMPLE_PATH), f"Missing sample: {TILE_SAMPLE_PATH}")
        img = cv2.imread(TILE_SAMPLE_PATH)
        self.assertIsNotNone(img, "Failed to load tile sample.")

        result = self.engine.inspect_frame(img, operator_category_override="tile", mode="upload")

        self.assertEqual(result["category"], "tile")
        self.assertEqual(result["category_type"], "texture")
        self.assertEqual(result["model_selected"], "PatchCore-Tile-MemoryBank")
        self.assertAlmostEqual(result["calibrated_threshold"], 1.4735, places=3)
        self.assertGreater(result["anomaly_score"], 0.0)
        self.assertIn(result["verdict"], ["NORMAL", "DEFECTIVE", "REVIEW REQUIRED"])
        self.assertIn(result["conclusion"], ["NO DEFECT DETECTED", "POSSIBLE DEFECT DETECTED", "MANUAL INSPECTION REQUIRED"])
        self.assertGreater(result["inference_latency_ms"], 0.0)

    def test_04_object_category_inference(self):
        """Scenario 4: Object category specimen (metal_nut) with operator override."""
        self.assertTrue(os.path.exists(NUT_SAMPLE_PATH), f"Missing sample: {NUT_SAMPLE_PATH}")
        img = cv2.imread(NUT_SAMPLE_PATH)
        self.assertIsNotNone(img, "Failed to load metal nut sample.")

        result = self.engine.inspect_frame(img, operator_category_override="metal_nut", mode="upload")

        self.assertEqual(result["category"], "metal_nut")
        self.assertEqual(result["category_type"], "object")
        self.assertEqual(result["model_selected"], "PatchCore-Metal_nut-MemoryBank")
        self.assertAlmostEqual(result["calibrated_threshold"], 1.8271, places=3)
        self.assertGreater(result["anomaly_score"], 0.0)
        self.assertIn(result["verdict"], ["NORMAL", "DEFECTIVE", "REVIEW REQUIRED"])
        self.assertIn(result["conclusion"], ["NO DEFECT DETECTED", "POSSIBLE DEFECT DETECTED", "MANUAL INSPECTION REQUIRED"])
        self.assertGreater(result["inference_latency_ms"], 0.0)

    def test_05_out_of_distribution_noise_rejection(self):
        """Scenario 5: Out-of-distribution input -> UNSUPPORTED verdict, model None."""
        noise_img = np.random.randint(0, 256, (300, 300, 3), dtype=np.uint8)

        result = self.engine.inspect_frame(noise_img, operator_category_override=None, mode="upload")

        self.assertEqual(result["category"], "unsupported")
        self.assertEqual(result["verdict"], "UNSUPPORTED")
        self.assertEqual(result["conclusion"], "UNSUPPORTED OR UNKNOWN CATEGORY")
        self.assertEqual(result["model_selected"], "None")
        self.assertEqual(result["anomaly_score"], 0.0)
        self.assertEqual(result["defect_area_pct"], 0.0)
        self.assertEqual(result["severity_score"], 0.0)

    def test_06_corrupted_empty_image_handling(self):
        """Scenario 6: Corrupted/Empty image -> REVIEW REQUIRED verdict."""
        result = self.engine.inspect_frame(None, operator_category_override=None, mode="upload")

        self.assertEqual(result["verdict"], "REVIEW REQUIRED")
        self.assertEqual(result["conclusion"], "MANUAL INSPECTION REQUIRED")
        self.assertIn("Failed to decode input frame", result["review_reason"])

    def test_07_api_http_endpoints_end_to_end(self):
        """Scenario 7: Full FastAPI HTTP endpoints end-to-end verification."""
        # A. POST /predict with nominal bottle image
        with open(NOMINAL_BOTTLE_PATH, "rb") as f:
            resp_upload = client.post(
                "/predict",
                files={"file": ("bottle.png", f, "image/png")},
                data={"category": "auto"}
            )
        self.assertEqual(resp_upload.status_code, 200, f"Upload API failed: {resp_upload.text}")
        data_upload = resp_upload.json()
        self.assertEqual(data_upload["category"], "bottle")
        self.assertEqual(data_upload["verdict"], "NORMAL")
        self.assertEqual(data_upload["conclusion"], "NO DEFECT DETECTED")

        # B. POST /api/optical-inspection/inspect-frame with defective bottle image
        with open(DEFECTIVE_BOTTLE_PATH, "rb") as f:
            resp_stream = client.post(
                "/api/optical-inspection/inspect-frame",
                files={"frame": ("frame.png", f, "image/png")},
                data={"operator_override": "auto"}
            )
        self.assertEqual(resp_stream.status_code, 200, f"Stream API failed: {resp_stream.text}")
        data_stream = resp_stream.json()
        self.assertEqual(data_stream["category"], "bottle")
        self.assertEqual(data_stream["verdict"], "DEFECTIVE")
        self.assertEqual(data_stream["conclusion"], "POSSIBLE DEFECT DETECTED")


if __name__ == "__main__":
    unittest.main()
