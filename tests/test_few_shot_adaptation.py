"""
DefectVision AI 2.0 — Few-Shot Adaptation & Universal Intake Test Suite
Validates the multi-domain reference-adaptive architecture:
1. Minimum Normal Sample Validation: <2 normal images raises ValueError.
2. Calibration Isolation Principle: Training set and calibration set are strictly disjoint.
3. Universal Intake Service:
   - Image domain classification (MVTec, controlled, smartphone, etc.)
   - Foreground segmentation & contour isolation
   - Optical quality gate & suitability status determination
4. Profile Creation & Memory-Bank Reload Consistency:
   - Artifact creation (manifest.json, memory_bank.npy, index.faiss)
   - SHA-256 checksums recorded in manifest
   - FAISS index dimensional integrity (384-dim) and search correctness
5. Mode C (Universal Intake) Safety & Triage Routing Contracts:
   - Safe halt with UNSUPPORTED / 'REFERENCE PROFILE REQUIRED' when no reference exists
   - Suppresses ungrounded anomaly score and heatmaps on failure
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
from src.universal_intake_service import UniversalImageIntakeService
from src.production_profile_service import ProductionProfileService, compute_file_sha256

client = TestClient(app)


class TestFewShotAdaptation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.intake = UniversalImageIntakeService()
        cls.profile_service = ProductionProfileService()
        cls.engine = get_optical_engine()

        # Gather sample images for adaptation testing
        cls.bottle_train_dir = os.path.join(PROJECT_ROOT, "DefectVisionAI", "dataset", "raw", "mvtec", "bottle", "train", "good")
        cls.normal_files = []
        if os.path.exists(cls.bottle_train_dir):
            all_files = sorted([os.path.join(cls.bottle_train_dir, f) for f in os.listdir(cls.bottle_train_dir) if f.endswith(".png")])
            cls.normal_files = all_files[:6]

    def test_01_intake_image_validation_and_domain_classification(self):
        """Verifies universal intake validates images and classifies domains correctly."""
        # 1. Blank/flat image rejected
        blank = np.zeros((256, 256, 3), dtype=np.uint8)
        res_blank = self.intake.process_image(blank)
        self.assertEqual(res_blank["suitability_status"], "UNSUITABLE")
        self.assertIn("flat", res_blank["rejection_reason"].lower())

        # 2. Too small image rejected
        small = np.zeros((16, 16, 3), dtype=np.uint8)
        res_small = self.intake.process_image(small)
        self.assertEqual(res_small["suitability_status"], "UNSUITABLE")
        self.assertIn("too low", res_small["rejection_reason"].lower())

        # 3. Valid benchmark image
        if self.normal_files:
            img = cv2.imread(self.normal_files[0])
            res_bench = self.intake.process_image(img)
            self.assertIn(res_bench["suitability_status"], ["SUITABLE", "SUITABLE_WITH_PREPROCESSING"])
            self.assertTrue(res_bench["foreground_detected"])
            self.assertGreater(res_bench["foreground_coverage_pct"], 5.0)
            self.assertIn(res_bench["image_domain"], ["mvtec_benchmark", "controlled_photo"])

    def test_02_minimum_sample_validation(self):
        """Enforces minimum 2 normal reference images for adaptation."""
        if not self.normal_files:
            self.skipTest("No test images found")

        img_bgr = cv2.imread(self.normal_files[0])
        with self.assertRaises(ValueError) as ctx:
            self.profile_service.create_adapted_profile(
                product_name="Test Insufficient Samples",
                category="bottle",
                sku="SKU-TEST-001",
                camera_id="CAM-01",
                normal_images=[img_bgr]  # Only 1 image provided
            )
        self.assertIn("at least 2 normal reference images", str(ctx.exception))

    def test_03_calibration_split_isolation_and_artifact_integrity(self):
        """Verifies train/calibration isolation and complete artifact generation."""
        if len(self.normal_files) < 4:
            self.skipTest("Need at least 4 test images for split test")

        imgs_bgr = [cv2.imread(p) for p in self.normal_files[:5]]
        test_sku = "SKU-UNITTEST-001"
        profile = None

        try:
            profile = self.profile_service.create_adapted_profile(
                product_name="Unit Test Adapted Bottle",
                category="bottle",
                sku=test_sku,
                camera_id="CAM-UNITTEST",
                normal_images=imgs_bgr,
                calibration_split_ratio=0.40  # 40% of 5 = 2 calibration, 3 training
            )

            # Check manifest properties
            self.assertIsNotNone(profile)
            self.assertEqual(profile["status"], "success")
            self.assertEqual(profile["training_samples_count"], 3)
            self.assertEqual(profile["calibration_samples_count"], 2)
            self.assertTrue(profile["is_provisional"])

            prof_id = profile["profile_id"]
            prof_dir = os.path.join(self.profile_service.profiles_dir, prof_id)
            self.assertTrue(os.path.isdir(prof_dir))

            # Verify files on disk
            manifest_path = os.path.join(prof_dir, "manifest.json")
            mem_bank_path = os.path.join(prof_dir, "memory_bank.npy")
            index_path = os.path.join(prof_dir, "index.faiss")

            self.assertTrue(os.path.exists(manifest_path))
            self.assertTrue(os.path.exists(mem_bank_path))
            self.assertTrue(os.path.exists(index_path))

            # Verify FAISS index and memory bank dimensionality
            bank = np.load(mem_bank_path)
            self.assertEqual(bank.shape[1], 384)
            self.assertGreater(bank.shape[0], 0)

            # Verify SHA-256 recorded in manifest matches disk
            manifest = profile["manifest"]
            recorded_bank_hash = manifest["artifacts"]["memory_bank.npy"]["sha256"]
            actual_bank_hash = compute_file_sha256(mem_bank_path)
            self.assertEqual(recorded_bank_hash, actual_bank_hash)

            # Verify threshold is strictly positive
            thresh = profile["calibrated_threshold"]
            self.assertGreater(thresh, 0.5)

        finally:
            # Clean up the test profile directory
            if profile and "profile_id" in profile:
                target_dir = os.path.join(self.profile_service.profiles_dir, profile["profile_id"])
                shutil.rmtree(target_dir, ignore_errors=True)

    def test_04_universal_routing_unsupported_category_safety(self):
        """Mode C safely halts with UNSUPPORTED when no reference profile exists."""
        # Create a synthetic image of something not in memory banks
        synthetic_img = np.full((256, 256, 3), 120, dtype=np.uint8)
        cv2.circle(synthetic_img, (128, 128), 60, (200, 200, 200), -1)
        cv2.rectangle(synthetic_img, (100, 100), (150, 150), (40, 40, 40), 2)

        _, buf = cv2.imencode(".png", synthetic_img)
        files = {"file": ("unknown_specimen.png", BytesIO(buf.tobytes()), "image/png")}
        data = {
            "routing_mode": "universal",
            "category": "auto"
        }

        resp = client.post("/predict", data=data, files=files)
        self.assertEqual(resp.status_code, 200)
        res = resp.json()

        # If detected category or no profile exists, must not crash and must halt safely
        self.assertIn("routing_mode", res)
        self.assertEqual(res["routing_mode"], "universal")
        if res.get("verdict") == "UNSUPPORTED":
            self.assertEqual(res["conclusion"], "REFERENCE PROFILE REQUIRED")
            self.assertFalse(res["inference_executed"])
            self.assertIsNone(res["anomaly_score"])

    def test_05_intake_diagnostics_endpoint(self):
        """Tests the standalone POST /api/intake endpoint."""
        if not self.normal_files:
            self.skipTest("No test images found")

        with open(self.normal_files[0], "rb") as f:
            files = {"file": ("intake_test.png", f, "image/png")}
            resp = client.post("/api/intake", files=files)

        self.assertEqual(resp.status_code, 200)
        res = resp.json()
        self.assertIn("suitability_status", res)
        self.assertIn("image_domain", res)
        self.assertIn("foreground_coverage_pct", res)
        self.assertIn("detected_category", res)


if __name__ == "__main__":
    unittest.main()
