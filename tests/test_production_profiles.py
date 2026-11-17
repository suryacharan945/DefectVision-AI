"""
DefectVision AI — Production Inspection Profiles Test Suite
Validates the target-domain PatchCore architecture, station profiles,
quality gates, and rejection contracts:
1. Profile Service: Loading, schema validation, FAISS index caching, SHA-256 integrity.
2. Production Normal Inspection: Score < threshold, verdict NORMAL, defect_area 0.0%.
3. Production Defect Inspection: Score >= threshold, verdict DEFECTIVE, valid heatmap.
4. Optical Quality Gate Rejection: Blur/exposure on ROI triggers REVIEW REQUIRED,
   with inference_executed=False, heatmap_generated=False, anomaly_score=None.
5. Profile Resolution Failure: Nonexistent profile safely triggers REVIEW REQUIRED
   with rejection_stage='profile_resolution', anomaly_score=None.
6. FastAPI Production Endpoints: /api/production-profiles, /predict, and /inspect-frame.
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
from src.production_profile_service import ProductionProfileService, compute_file_sha256

client = TestClient(app)

VAL_NORMAL_SAMPLE = os.path.join(PROJECT_ROOT, "data", "station_01", "val_normal", "station01_normal_val_000.png")
VAL_DEFECT_SAMPLE = os.path.join(PROJECT_ROOT, "data", "station_01", "val_defect", "station01_defect_val_000.png")


def encode_image_bytes(img_bgr, ext=".png"):
    _, buf = cv2.imencode(ext, img_bgr)
    return BytesIO(buf.tobytes())


class TestProductionProfiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Ensure held-out station test samples exist, generating deterministically if needed
        if not os.path.exists(VAL_NORMAL_SAMPLE) or not os.path.exists(VAL_DEFECT_SAMPLE):
            sys.path.insert(0, os.path.join(PROJECT_ROOT, "scripts"))
            from prepare_station_01_data import generate_station_data
            generate_station_data()

        cls.engine = get_optical_engine()
        cls.profile_service = ProductionProfileService()
        cls.profile_id = "bottle_001_station_01"

    def test_01_profile_discovery_and_metadata(self):
        """Verifies that bottle_001_station_01 is loaded with valid metadata."""
        profiles = self.profile_service.list_profiles()
        self.assertGreaterEqual(len(profiles), 1)

        pids = [p["profile_id"] for p in profiles]
        self.assertIn(self.profile_id, pids)

        profile = self.profile_service.get_profile(self.profile_id)
        self.assertIsNotNone(profile)
        self.assertEqual(profile["product_id"], "PROD-BTL-001")
        self.assertEqual(profile["category"], "bottle")
        self.assertEqual(profile["category_type"], "object")
        self.assertIn("roi_config", profile)
        self.assertIn("quality_config", profile)
        self.assertIn("threshold_config", profile)
        self.assertIn("model_config", profile)

    def test_02_profile_manifest_sha256_integrity(self):
        """Verifies SHA-256 hashes of memory_bank.npy and index.faiss against manifest."""
        profile = self.profile_service.get_profile(self.profile_id)
        profile_dir = profile["_profile_dir"]
        manifest_path = os.path.join(profile_dir, "manifest.json")
        self.assertTrue(os.path.exists(manifest_path))

        import json
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        mb_file = os.path.join(profile_dir, "memory_bank.npy")
        faiss_file = os.path.join(profile_dir, "index.faiss")

        self.assertEqual(compute_file_sha256(mb_file), manifest["artifacts"]["memory_bank.npy"]["sha256"])
        self.assertEqual(compute_file_sha256(faiss_file), manifest["artifacts"]["index.faiss"]["sha256"])

    def test_03_profile_model_loading_and_faiss(self):
        """Verifies PatchCoreModel loads and initializes FAISS IndexFlatL2."""
        model = self.profile_service.get_profile_model(self.profile_id)
        self.assertIsNotNone(model)
        self.assertIsNotNone(model.memory_bank)
        self.assertIsNotNone(model.index)
        self.assertEqual(model.memory_bank.shape[1], 384)
        self.assertEqual(model.index.ntotal, model.memory_bank.shape[0])

    def test_04_production_normal_specimen_inspection(self):
        """Verifies held-out station normal specimen yields NORMAL verdict with score < threshold."""
        self.assertTrue(os.path.exists(VAL_NORMAL_SAMPLE), f"Missing validation sample: {VAL_NORMAL_SAMPLE}")
        img = cv2.imread(VAL_NORMAL_SAMPLE)
        self.assertIsNotNone(img)

        result = self.engine.inspect_frame(
            img,
            profile_id=self.profile_id,
            routing_mode="production",
            mode="upload"
        )

        self.assertEqual(result["routing_mode"], "production")
        self.assertEqual(result["profile_id"], self.profile_id)
        self.assertTrue(result["inference_executed"])
        self.assertTrue(result["heatmap_generated"])
        self.assertIsNone(result["rejection_stage"])
        self.assertIsNone(result["rejection_reason"])
        self.assertEqual(result["verdict"], "NORMAL")
        self.assertEqual(result["conclusion"], "NO DEFECT DETECTED")
        self.assertLess(result["anomaly_score"], result["calibrated_threshold"])
        self.assertEqual(result["defect_area_pct"], 0.0)
        self.assertEqual(result["severity_score"], 0.0)
        self.assertEqual(result["severity_level"], "normal")
        self.assertIn("data:image/jpeg;base64,", result["heatmap_base64"])

    def test_05_production_defective_specimen_inspection(self):
        """Verifies held-out station defect specimen yields DEFECTIVE verdict with score >= threshold."""
        self.assertTrue(os.path.exists(VAL_DEFECT_SAMPLE), f"Missing validation sample: {VAL_DEFECT_SAMPLE}")
        img = cv2.imread(VAL_DEFECT_SAMPLE)
        self.assertIsNotNone(img)

        result = self.engine.inspect_frame(
            img,
            profile_id=self.profile_id,
            routing_mode="production",
            mode="upload"
        )

        self.assertEqual(result["routing_mode"], "production")
        self.assertEqual(result["profile_id"], self.profile_id)
        self.assertTrue(result["inference_executed"])
        self.assertTrue(result["heatmap_generated"])
        self.assertIsNone(result["rejection_stage"])
        self.assertIsNone(result["rejection_reason"])
        self.assertEqual(result["verdict"], "DEFECTIVE")
        self.assertEqual(result["conclusion"], "POSSIBLE DEFECT DETECTED")
        self.assertGreaterEqual(result["anomaly_score"], result["calibrated_threshold"])
        self.assertGreater(result["defect_area_pct"], 0.0)
        self.assertIn(result["severity_level"].lower(), ("moderate", "critical"))
        self.assertIn("data:image/jpeg;base64,", result["heatmap_base64"])

    def test_06_quality_gate_roi_rejection_contract(self):
        """
        Verifies that blurred ROI triggers REVIEW REQUIRED with:
        inference_executed=False, heatmap_generated=False, anomaly_score=None,
        calibrated_threshold=None, heatmap_base64=''.
        """
        normal_img = cv2.imread(VAL_NORMAL_SAMPLE)
        # Apply heavy blur to trigger quality rejection on ROI
        blurred_img = cv2.GaussianBlur(normal_img, (55, 55), 25.0)

        result = self.engine.inspect_frame(
            blurred_img,
            profile_id=self.profile_id,
            routing_mode="production",
            mode="live"
        )

        self.assertEqual(result["routing_mode"], "production")
        self.assertEqual(result["profile_id"], self.profile_id)
        self.assertEqual(result["verdict"], "REVIEW REQUIRED")
        self.assertFalse(result["inference_executed"])
        self.assertFalse(result["heatmap_generated"])
        self.assertEqual(result["rejection_stage"], "quality_gate")
        self.assertIn("Optical quality failure", result["rejection_reason"])
        self.assertIsNone(result["anomaly_score"])
        self.assertIsNone(result["calibrated_threshold"])
        self.assertEqual(result["heatmap_base64"], "")

    def test_07_invalid_profile_resolution_rejection(self):
        """Verifies that requesting an unconfigured profile triggers graceful rejection."""
        normal_img = cv2.imread(VAL_NORMAL_SAMPLE)
        invalid_pid = "station_99_nonexistent_sku"

        result = self.engine.inspect_frame(
            normal_img,
            profile_id=invalid_pid,
            routing_mode="production",
            mode="upload"
        )

        self.assertEqual(result["routing_mode"], "production")
        self.assertEqual(result["profile_id"], invalid_pid)
        self.assertEqual(result["verdict"], "REVIEW REQUIRED")
        self.assertFalse(result["inference_executed"])
        self.assertFalse(result["heatmap_generated"])
        self.assertEqual(result["rejection_stage"], "profile_resolution")
        self.assertIn("Unknown or unconfigured", result["rejection_reason"])
        self.assertIsNone(result["anomaly_score"])
        self.assertIsNone(result["calibrated_threshold"])

    def test_08_fastapi_production_profile_endpoints(self):
        """Verifies HTTP endpoints for production profile listing and execution."""
        # 1. GET /api/production-profiles
        res_list = client.get("/api/production-profiles")
        self.assertEqual(res_list.status_code, 200)
        data_list = res_list.json()
        self.assertIn("profiles", data_list)
        pids = [p["profile_id"] for p in data_list["profiles"]]
        self.assertIn(self.profile_id, pids)

        # 2. GET /api/production-profiles/{id}
        res_prof = client.get(f"/api/production-profiles/{self.profile_id}")
        self.assertEqual(res_prof.status_code, 200)
        data_prof = res_prof.json()
        self.assertEqual(data_prof["profile_id"], self.profile_id)

        # 3. GET /api/production-profiles/nonexistent -> 404
        res_404 = client.get("/api/production-profiles/nonexistent_xyz")
        self.assertEqual(res_404.status_code, 404)

        # 4. POST /predict with profile_id
        with open(VAL_NORMAL_SAMPLE, "rb") as f:
            res_predict = client.post(
                "/predict",
                files={"file": ("station_normal.png", f, "image/png")},
                data={"profile_id": self.profile_id, "routing_mode": "production"}
            )
        self.assertEqual(res_predict.status_code, 200)
        pred_data = res_predict.json()
        self.assertEqual(pred_data["routing_mode"], "production")
        self.assertEqual(pred_data["profile_id"], self.profile_id)
        self.assertEqual(pred_data["verdict"], "NORMAL")
        self.assertTrue(pred_data["inference_executed"])

        # 5. POST /api/optical-inspection/inspect-frame with profile_id
        with open(VAL_DEFECT_SAMPLE, "rb") as f:
            res_inspect = client.post(
                "/api/optical-inspection/inspect-frame",
                files={"frame": ("station_defect.png", f, "image/png")},
                data={"profile_id": self.profile_id, "routing_mode": "production"}
            )
        self.assertEqual(res_inspect.status_code, 200)
        inspect_data = res_inspect.json()
        self.assertEqual(inspect_data["routing_mode"], "production")
        self.assertEqual(inspect_data["profile_id"], self.profile_id)
        self.assertEqual(inspect_data["verdict"], "DEFECTIVE")
        self.assertTrue(inspect_data["inference_executed"])

        # 6. GET /health reports production profile count
        res_health = client.get("/health")
        self.assertEqual(res_health.status_code, 200)
        health_data = res_health.json()
        self.assertIn("production_profiles_count", health_data)
        self.assertGreaterEqual(health_data["production_profiles_count"], 1)
        self.assertIn(self.profile_id, health_data["production_profiles"])


if __name__ == "__main__":
    unittest.main()
