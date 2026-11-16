"""
DefectVision AI — Optical Inspection Pipeline Comprehensive Test Suite
Validates:
1. Optical Image Quality Gate (Blur, Exposure, Contrast)
2. Region-of-Interest Extraction (Object vs Texture)
3. Category Model Registry (15 MVTec AD models & thresholds)
4. Decision Fusion Service (NORMAL, DEFECTIVE, REVIEW REQUIRED, UNSUPPORTED)
5. Inspection History Ring Buffer & Persistence
6. FastAPI Optical Inspection Endpoints
"""

import os
import sys
import unittest
import numpy as np
import cv2
from fastapi.testclient import TestClient

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "DefectVisionAI"))

from src.image_quality_service import ImageQualityService
from src.object_region_service import ObjectRegionService
from src.category_model_registry import CategoryModelRegistry
from src.decision_fusion_service import DecisionFusionService
from src.inspection_history_service import InspectionHistoryService
from app import app


# -------------------------------------------------------------------
# Test 1: Image Quality Service
# -------------------------------------------------------------------
class TestImageQualityService(unittest.TestCase):
    def setUp(self):
        self.service = ImageQualityService(
            min_sharpness=80.0,
            min_luminance=35.0,
            max_luminance=235.0,
            min_contrast=18.0
        )

    def test_sharp_image_passes(self):
        # Create a sharp image with high contrast shapes and good lighting
        img = np.full((300, 300, 3), 128, dtype=np.uint8)
        cv2.rectangle(img, (50, 50), (250, 250), (220, 220, 220), -1)
        cv2.circle(img, (150, 150), 40, (30, 30, 30), -1)

        is_valid, status, metrics = self.service.validate_frame(img)
        self.assertTrue(is_valid)
        self.assertEqual(status, "OPTICAL_QUALITY_VERIFIED")
        self.assertGreaterEqual(metrics["sharpness"], 60.0)
        self.assertTrue(35.0 <= metrics["brightness"] <= 235.0)

    def test_blurred_image_fails_quality_gate(self):
        img = np.full((300, 300, 3), 128, dtype=np.uint8)
        cv2.circle(img, (150, 150), 40, (140, 140, 140), -1)
        blurred = cv2.GaussianBlur(img, (51, 51), 30.0)

        is_valid, status, metrics = self.service.validate_frame(blurred)
        self.assertFalse(is_valid)
        self.assertIn(status, ("REJECT_MOTION_OR_OPTICAL_BLUR", "REJECT_LOW_CONTRAST"))

    def test_underexposed_image_fails_quality_gate(self):
        dark_img = np.full((200, 200, 3), 10, dtype=np.uint8)
        is_valid, status, metrics = self.service.validate_frame(dark_img)
        self.assertFalse(is_valid)
        self.assertEqual(status, "REJECT_INSUFFICIENT_ILLUMINATION")

    def test_overexposed_image_fails_quality_gate(self):
        bright_img = np.full((200, 200, 3), 250, dtype=np.uint8)
        is_valid, status, metrics = self.service.validate_frame(bright_img)
        self.assertFalse(is_valid)
        self.assertIn(status, ("REJECT_OVEREXPOSED_OR_GLARE", "REJECT_LOW_CONTRAST"))


# -------------------------------------------------------------------
# Test 2: Object Region Service
# -------------------------------------------------------------------
class TestObjectRegionService(unittest.TestCase):
    def setUp(self):
        self.service = ObjectRegionService(margin_ratio=0.10)

    def test_object_contour_extraction(self):
        img = np.zeros((400, 400, 3), dtype=np.uint8)
        cv2.circle(img, (200, 200), 60, (220, 220, 220), -1)

        roi_img, bbox = self.service.extract_roi(img, category_type="object")
        self.assertIsNotNone(bbox)
        bx, by, bw, bh = bbox
        self.assertGreater(bw, 100)
        self.assertGreater(bh, 100)
        self.assertEqual(roi_img.shape[0], bh)
        self.assertEqual(roi_img.shape[1], bw)

    def test_texture_center_window_extraction(self):
        img = np.random.randint(50, 200, (400, 400, 3), dtype=np.uint8)
        roi_img, bbox = self.service.extract_roi(img, category_type="texture")
        self.assertIsNotNone(bbox)
        bx, by, bw, bh = bbox
        self.assertEqual(bw, 400)
        self.assertEqual(bh, 400)


# -------------------------------------------------------------------
# Test 3: Category Model Registry
# -------------------------------------------------------------------
class TestCategoryModelRegistry(unittest.TestCase):
    def setUp(self):
        models_dir = os.path.join(PROJECT_ROOT, "DefectVisionAI", "models")
        self.registry = CategoryModelRegistry(models_dir=models_dir)

    def test_all_15_categories_registered(self):
        cats = self.registry.get_all_categories()
        self.assertEqual(len(cats), 15)
        expected = [
            "bottle", "cable", "capsule", "carpet", "grid",
            "hazelnut", "leather", "metal_nut", "pill", "screw",
            "tile", "toothbrush", "transistor", "wood", "zipper"
        ]
        for exp in expected:
            self.assertIn(exp, cats)

    def test_category_configuration_validity(self):
        for cat in self.registry.get_all_categories():
            cfg = self.registry.get_category_config(cat)
            self.assertIsNotNone(cfg)
            self.assertIn("category_type", cfg)
            self.assertIn(cfg["category_type"], ("object", "texture"))
            self.assertIn("calibrated_threshold", cfg)
            self.assertGreater(cfg["calibrated_threshold"], 0.5)
            self.assertIn("baseline_mean", cfg)
            self.assertIn("baseline_p99", cfg)

    def test_models_status_reports_ready(self):
        status = self.registry.get_models_status()
        self.assertEqual(len(status), 15)
        for cat, s in status.items():
            self.assertIn("is_ready", s)
            self.assertIn("calibrated_threshold", s)
            self.assertIn("category_type", s)


# -------------------------------------------------------------------
# Test 4: Decision Fusion Service
# -------------------------------------------------------------------
class TestDecisionFusionService(unittest.TestCase):
    def setUp(self):
        self.fusion = DecisionFusionService(borderline_margin=0.08)

    def test_quality_failure_yields_review_required(self):
        cat_result = {"is_supported": True, "category": "bottle", "confidence": 0.95}
        verdict, sev, reason, telem = self.fusion.evaluate_inspection(
            quality_is_valid=False,
            quality_status="BLUR_DETECTED",
            category_result=cat_result,
            anomaly_score=1.0,
            calibrated_threshold=1.5
        )
        self.assertEqual(verdict, "REVIEW REQUIRED")
        self.assertEqual(sev, "review")
        self.assertIn("BLUR_DETECTED", reason)

    def test_unsupported_category_yields_unsupported_verdict(self):
        cat_result = {
            "is_supported": False,
            "category": "unknown",
            "candidate_category": "banana",
            "confidence": 0.35,
            "status": "OUT_OF_DISTRIBUTION"
        }
        verdict, sev, reason, telem = self.fusion.evaluate_inspection(
            quality_is_valid=True,
            quality_status="OPTICAL_QUALITY_VERIFIED",
            category_result=cat_result,
            anomaly_score=1.0,
            calibrated_threshold=1.5
        )
        self.assertEqual(verdict, "UNSUPPORTED")
        self.assertEqual(sev, "unsupported")
        self.assertIn("Unsupported", reason)

    def test_normal_score_yields_normal(self):
        cat_result = {"is_supported": True, "category": "bottle", "confidence": 0.96}
        verdict, sev, reason, telem = self.fusion.evaluate_inspection(
            quality_is_valid=True,
            quality_status="PASSED",
            category_result=cat_result,
            anomaly_score=1.10,
            calibrated_threshold=1.50
        )
        self.assertEqual(verdict, "NORMAL")
        self.assertEqual(sev, "normal")
        self.assertIn(reason, (None, ""))

    def test_defect_score_yields_defective(self):
        cat_result = {"is_supported": True, "category": "bottle", "confidence": 0.96}
        verdict, sev, reason, telem = self.fusion.evaluate_inspection(
            quality_is_valid=True,
            quality_status="PASSED",
            category_result=cat_result,
            anomaly_score=2.85,
            calibrated_threshold=1.50
        )
        self.assertEqual(verdict, "DEFECTIVE")
        self.assertIn(sev, ("moderate", "critical"))

    def test_borderline_score_yields_review_required(self):
        cat_result = {"is_supported": True, "category": "bottle", "confidence": 0.96}
        borderline_score = 1.48
        verdict, sev, reason, telem = self.fusion.evaluate_inspection(
            quality_is_valid=True,
            quality_status="PASSED",
            category_result=cat_result,
            anomaly_score=borderline_score,
            calibrated_threshold=1.50
        )
        self.assertEqual(verdict, "REVIEW REQUIRED")
        self.assertIn("Borderline anomaly score", reason)


# -------------------------------------------------------------------
# Test 5: Inspection History Service
# -------------------------------------------------------------------
class TestInspectionHistoryService(unittest.TestCase):
    def setUp(self):
        self.history = InspectionHistoryService(max_records=10)
        self.history.clear_history()

    def test_add_and_retrieve_history(self):
        rec = {
            "verdict": "NORMAL",
            "detected_category": "bottle",
            "anomaly_score": 0.95
        }
        self.history.add_inspection(rec)
        self.assertEqual(len(self.history.get_history()), 1)

        res = self.history.get_history(category="bottle")
        self.assertEqual(len(res), 1)
        res_empty = self.history.get_history(category="cable")
        self.assertEqual(len(res_empty), 0)

    def test_statistics_summary(self):
        self.history.add_inspection({"verdict": "NORMAL", "detected_category": "bottle", "processing_time_ms": 50})
        self.history.add_inspection({"verdict": "DEFECTIVE", "detected_category": "cable", "processing_time_ms": 60})
        stats = self.history.get_statistics()
        self.assertEqual(stats["total_inspections"], 2)
        self.assertEqual(stats["verdicts"]["NORMAL"], 1)
        self.assertEqual(stats["verdicts"]["DEFECTIVE"], 1)
        self.assertEqual(stats["avg_latency_ms"], 55.0)


# -------------------------------------------------------------------
# Test 6: FastAPI Optical Inspection Endpoints
# -------------------------------------------------------------------
class TestFastAPIOpticalEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_get_optical_model_status_endpoint(self):
        response = self.client.get("/api/optical-inspection/model-status")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("categories", data)
        self.assertEqual(data["total_categories"], 15)
        self.assertIn("bottle", data["categories"])
        self.assertIn("screw", data["categories"])

    def test_get_optical_categories_endpoint(self):
        response = self.client.get("/api/optical-inspection/categories")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total"], 15)
        self.assertEqual(len(data["categories"]), 15)

    def test_inspect_frame_optical_endpoint_with_image(self):
        img = np.full((224, 224, 3), 120, dtype=np.uint8)
        cv2.circle(img, (112, 112), 40, (200, 200, 200), -1)
        _, img_encoded = cv2.imencode(".jpg", img)

        response = self.client.post(
            "/api/optical-inspection/inspect-frame",
            files={"frame": ("test.jpg", img_encoded.tobytes(), "image/jpeg")},
            data={"operator_override": "bottle"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("verdict", data)
        self.assertIn("detected_category", data)
        self.assertIn("heatmap_base64", data)
        self.assertIn("processing_time_ms", data)
        self.assertEqual(data["detected_category"], "bottle")


if __name__ == "__main__":
    unittest.main()
