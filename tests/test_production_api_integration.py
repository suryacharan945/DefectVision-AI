"""
DefectVision AI — Production API Integration Test Suite
Verifies:
1. Production health check endpoints (/health, /api/health, /api, /api/)
2. Dynamic CORS response headers for production Vercel domain and preview regex
3. 15-category model registry endpoint (/api/optical-inspection/model-status)
4. Unified /predict endpoint contract
"""

import os
import sys
import unittest
import numpy as np
import cv2
import io
from fastapi.testclient import TestClient

# Ensure DefectVisionAI is on path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(REPO_ROOT, "DefectVisionAI")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app import app, known_categories


class TestProductionApiIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health_endpoints_respond_with_json(self):
        """Verify that all health endpoints return 200 JSON with required telemetry."""
        endpoints = ["/health", "/api/health", "/api", "/api/"]
        for ep in endpoints:
            with self.subTest(endpoint=ep):
                resp = self.client.get(ep)
                self.assertEqual(resp.status_code, 200)
                self.assertTrue("application/json" in resp.headers.get("content-type", ""))
                data = resp.json()
                self.assertEqual(data.get("status"), "ready")
                self.assertIn("device", data)
                self.assertEqual(data.get("total_categories"), 15)
                self.assertIn("bottle", data.get("categories", []))

    def test_cors_production_origin(self):
        """Verify CORS headers for authoritative Vercel production frontend."""
        headers = {
            "Origin": "https://defectvision-ai.vercel.app"
        }
        resp = self.client.get("/health", headers=headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.headers.get("access-control-allow-origin"),
            "https://defectvision-ai.vercel.app"
        )
        self.assertEqual(resp.headers.get("access-control-allow-credentials"), "true")

    def test_cors_vercel_preview_origin(self):
        """Verify CORS regex allows arbitrary Vercel branch preview deployments."""
        headers = {
            "Origin": "https://defectvision-ai-git-fix-backend-test-suryacharan945.vercel.app"
        }
        resp = self.client.get("/health", headers=headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.headers.get("access-control-allow-origin"),
            "https://defectvision-ai-git-fix-backend-test-suryacharan945.vercel.app"
        )

    def test_optical_model_status_endpoint(self):
        """Verify model-status endpoint returns calibrated thresholds for 15 categories."""
        resp = self.client.get("/api/optical-inspection/model-status")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("categories", data)
        self.assertEqual(data.get("total_categories"), 15)
        categories = data["categories"]
        for cat in known_categories:
            self.assertIn(cat, categories)
            cat_info = categories[cat]
            self.assertIn("calibrated_threshold", cat_info)
            self.assertGreater(cat_info["calibrated_threshold"], 0.0)

    def test_predict_endpoint_contract(self):
        """Verify /predict endpoint handles uploaded image bytes and returns structured schema."""
        # Create synthetic 224x224 RGB image
        img = np.full((224, 224, 3), 180, dtype=np.uint8)
        cv2.circle(img, (112, 112), 40, (50, 50, 50), -1)
        _, buf = cv2.imencode(".png", img)
        file_bytes = io.BytesIO(buf.tobytes())

        resp = self.client.post(
            "/predict",
            files={"file": ("test_specimen.png", file_bytes, "image/png")},
            data={"category": "bottle"}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("verdict", data)
        self.assertIn("predicted_label", data)
        self.assertIn("anomaly_score", data)
        self.assertIn("calibrated_threshold", data)
        self.assertIn("processing_time_ms", data)
        self.assertIn("defect_area_pct", data)


if __name__ == "__main__":
    unittest.main()
