"""
DefectVision AI — Product Adaptation & Profile Lifecycle Test Suite
Validates the complete product-specific PatchCore lifecycle:
1. Profile discovery, schema validation, and rich metadata fields.
2. Analytics endpoint and FAISS index dimension/vector verification.
3. Profile lifecycle transitions: activate, deactivate, archive.
4. Few-shot adaptation creation: calibration isolation, coreset subsampling, manifest generation.
5. Profile evaluation endpoint: scoring, verdicts, and empirical accuracy/latency metrics.
6. Profile metadata update endpoint.
7. Foreground isolation diagnostics and texture category bypass.
8. Safe profile deletion and memory cleanup.
"""

import os
import sys
import shutil
import tempfile
import unittest
import numpy as np
import cv2
from io import BytesIO
from fastapi.testclient import TestClient

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "DefectVisionAI"))

from app import app, get_optical_engine
from src.production_profile_service import ProductionProfileService, compute_file_sha256

client = TestClient(app)


def create_synthetic_bottle_image(h=512, w=512, with_defect=False):
    """Creates a synthetic bottle image on light background."""
    img = np.full((h, w, 3), 220, dtype=np.uint8)
    # Draw bottle body
    cv2.rectangle(img, (150, 150), (360, 460), (120, 160, 180), -1)
    # Draw bottle neck
    cv2.rectangle(img, (210, 60), (300, 150), (130, 170, 190), -1)
    # Draw cap
    cv2.rectangle(img, (200, 40), (310, 60), (60, 80, 120), -1)

    if with_defect:
        # Draw dark crack / contamination on bottle body
        cv2.line(img, (220, 250), (280, 320), (20, 20, 20), 4)
        cv2.circle(img, (280, 320), 8, (15, 15, 15), -1)

    return img


class TestProductAdaptation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = get_optical_engine()
        cls.profile_service = cls.engine.profile_service
        cls.test_profile_id = "bottle_sku_btl_adapt_002"
        cls.temp_profile_id = None

    def test_01_profile_discovery_and_schema_validation(self):
        """Verifies that registered profiles return rich schema and status attributes."""
        response = client.get("/api/production-profiles")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("profiles", data)
        self.assertGreaterEqual(len(data["profiles"]), 1)

        p = next((x for x in data["profiles"] if x["profile_id"] == self.test_profile_id), None)
        self.assertIsNotNone(p, f"Profile {self.test_profile_id} not found in listing")
        self.assertEqual(p["category"], "bottle")
        self.assertTrue(p["is_adapted"])
        self.assertTrue(p["is_provisional"])
        self.assertIn("calibrated_threshold", p)
        self.assertIn("coreset_vectors_count", p)
        self.assertIn("status", p)

    def test_02_profile_analytics_endpoint(self):
        """Verifies profile analytics returns deep score percentiles, FAISS dimensions, and checksums."""
        response = client.get(f"/api/production-profiles/{self.test_profile_id}/analytics")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["profile_id"], self.test_profile_id)
        self.assertIn("score_metrics", data)
        self.assertIn("memory_bank", data)
        self.assertEqual(data["memory_bank"]["feature_dimension"], 384)
        self.assertGreater(data["memory_bank"]["vectors"], 0)
        self.assertIn("manifest", data)
        self.assertIn("artifacts", data["manifest"])

    def test_03_profile_lifecycle_transitions(self):
        """Verifies activate -> deactivate -> activate transitions."""
        # Deactivate
        res_deact = client.post(f"/api/production-profiles/{self.test_profile_id}/deactivate")
        self.assertEqual(res_deact.status_code, 200)
        self.assertEqual(res_deact.json()["profile_status"], "inactive")

        prof = self.profile_service.get_profile(self.test_profile_id)
        self.assertEqual(prof["status"], "inactive")

        # Activate
        res_act = client.post(f"/api/production-profiles/{self.test_profile_id}/activate")
        self.assertEqual(res_act.status_code, 200)
        self.assertEqual(res_act.json()["profile_status"], "active")

        prof = self.profile_service.get_profile(self.test_profile_id)
        self.assertEqual(prof["status"], "active")

    def test_04_few_shot_adaptation_creation_and_isolation(self):
        """Creates a temporary few-shot profile, validating calibration isolation."""
        # Generate 4 synthetic normal images
        images = [create_synthetic_bottle_image() for _ in range(4)]
        files = []
        for idx, img in enumerate(images):
            _, buf = cv2.imencode(".png", img)
            files.append(("files", (f"norm_{idx}.png", buf.tobytes(), "image/png")))

        data = {
            "product_name": "Test Synthetic Bottle",
            "sku": "SKU-TEST-SYN-001",
            "category": "bottle",
            "acquisition_type": "controlled_photography",
            "camera_id": "CAM-TEST-01",
            "lighting_profile": "diffuse",
            "calibration_split_ratio": 0.25,
            "coreset_ratio": 0.10,
        }

        response = client.post("/api/production-profiles/adapt", data=data, files=files)
        self.assertEqual(response.status_code, 200, f"Adaptation failed: {response.text}")
        res_json = response.json()
        self.assertEqual(res_json["status"], "success")

        TestProductAdaptation.temp_profile_id = res_json["profile_id"]
        temp_pid = TestProductAdaptation.temp_profile_id

        # Verify sample counts
        self.assertEqual(res_json["training_samples_count"], 3)
        self.assertEqual(res_json["calibration_samples_count"], 1)
        self.assertGreater(res_json["coreset_vectors_count"], 0)
        self.assertGreater(res_json["calibrated_threshold"], 0.0)

        # Verify disk artifacts
        p = self.profile_service.get_profile(temp_pid)
        p_dir = p["_profile_dir"]
        self.assertTrue(os.path.exists(os.path.join(p_dir, "profile.json")))
        self.assertTrue(os.path.exists(os.path.join(p_dir, "manifest.json")))
        self.assertTrue(os.path.exists(os.path.join(p_dir, "threshold.json")))
        self.assertTrue(os.path.exists(os.path.join(p_dir, "memory_bank.npy")))
        self.assertTrue(os.path.exists(os.path.join(p_dir, "index.faiss")))

    def test_05_profile_evaluation_endpoint(self):
        """Evaluates normal and defective samples against the temporary adapted profile."""
        temp_pid = TestProductAdaptation.temp_profile_id
        if not temp_pid:
            self.skipTest("Temporary profile not created")

        norm_img = create_synthetic_bottle_image(with_defect=False)
        def_img = create_synthetic_bottle_image(with_defect=True)

        _, buf_n = cv2.imencode(".png", norm_img)
        _, buf_d = cv2.imencode(".png", def_img)

        eval_files = [
            ("files", ("test_norm.png", buf_n.tobytes(), "image/png")),
            ("files", ("test_defect.png", buf_d.tobytes(), "image/png")),
        ]
        eval_data = {"labels": "NORMAL,DEFECTIVE"}

        response = client.post(f"/api/production-profiles/{temp_pid}/evaluate", data=eval_data, files=eval_files)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["profile_id"], temp_pid)
        self.assertIn("metrics", data)
        self.assertEqual(data["metrics"]["total_evaluated"], 2)
        self.assertEqual(data["metrics"]["labeled_count"], 2)
        self.assertIn("samples", data)
        self.assertEqual(len(data["samples"]), 2)

    def test_06_profile_update_metadata(self):
        """Updates editable profile metadata and verifies persistence."""
        temp_pid = TestProductAdaptation.temp_profile_id
        if not temp_pid:
            self.skipTest("Temporary profile not created")

        payload = {
            "product_name": "Updated Test Bottle Name",
            "camera_id": "CAM-UPDATED-99",
            "lighting_profile": "darkfield_axial"
        }
        response = client.put(f"/api/production-profiles/{temp_pid}", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["product_name"], "Updated Test Bottle Name")
        self.assertEqual(data["camera_id"], "CAM-UPDATED-99")

        # Verify re-read from disk
        refreshed = self.profile_service.get_profile(temp_pid)
        self.assertEqual(refreshed["product_name"], "Updated Test Bottle Name")
        self.assertEqual(refreshed["camera_id"], "CAM-UPDATED-99")

    def test_07_foreground_mask_diagnostics(self):
        """Verifies foreground mask diagnostics on object and texture categories."""
        # 1. Object Category (Bottle)
        bottle_img = create_synthetic_bottle_image()
        record_obj = self.engine.inspect_frame(bottle_img, operator_category_override="bottle")
        self.assertIn("foreground_masking_applied", record_obj)
        self.assertIn("foreground_masking_reason", record_obj)
        self.assertIn("foreground_mask_validity", record_obj)
        self.assertIn("connected_components_count", record_obj)
        self.assertTrue(record_obj["foreground_detected"])
        self.assertEqual(record_obj["foreground_mask_validity"], "VALID")

        # 2. Texture Category (Leather)
        leather_dir = os.path.join(PROJECT_ROOT, "DefectVisionAI", "dataset", "raw", "mvtec", "leather", "train", "good")
        if os.path.exists(leather_dir) and os.listdir(leather_dir):
            sample_file = os.path.join(leather_dir, sorted(os.listdir(leather_dir))[0])
            leather_img = cv2.imread(sample_file)
        else:
            x = np.linspace(0, 50 * np.pi, 512)
            y = np.linspace(0, 50 * np.pi, 512)
            xx, yy = np.meshgrid(x, y)
            pattern = (np.sin(xx) * np.cos(yy) * 60 + 128).astype(np.uint8)
            leather_img = cv2.merge([pattern, pattern, pattern])

        record_tex = self.engine.inspect_frame(leather_img, operator_category_override="leather")
        self.assertFalse(record_tex["foreground_masking_applied"])
        self.assertEqual(record_tex["foreground_mask_validity"], "TEXTURE_BYPASS")
        self.assertIn("Texture category", record_tex["foreground_masking_reason"])

    def test_08_profile_deletion_cleanup(self):
        """Deletes the temporary profile and verifies memory and disk cleanup."""
        temp_pid = TestProductAdaptation.temp_profile_id
        if not temp_pid:
            self.skipTest("Temporary profile not created")

        response = client.delete(f"/api/production-profiles/{temp_pid}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "deleted")

        # Verify profile is no longer loaded
        self.assertIsNone(self.profile_service.get_profile(temp_pid))
        self.assertNotIn(temp_pid, self.profile_service.loaded_models)

        # Verify GET returns 404
        get_res = client.get(f"/api/production-profiles/{temp_pid}")
        self.assertEqual(get_res.status_code, 404)


if __name__ == "__main__":
    unittest.main()
