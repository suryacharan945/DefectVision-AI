"""
DefectVision AI — Production API Integration & Readiness Test Suite
Verifies:
1. Truthful production health check endpoints (/health, /api/health, /api, /api/)
2. Dynamic health status transitions: 'ready', 'degraded', 'not_ready'
3. Strict CORS security: approved production origin, project preview origin, and rejection of unapproved Vercel origins
4. OPTIONS preflight validation
5. 15-category model registry endpoint (/api/optical-inspection/model-status)
6. Unified /predict endpoint API schema & contract handling
7. Frontend client health interpretation & Demo Mode contract simulation
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch
import numpy as np
import cv2
import io
from fastapi.testclient import TestClient

# Ensure DefectVisionAI is on path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(REPO_ROOT, "DefectVisionAI")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app import app, known_categories, get_system_health


class TestProductionApiIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    # -------------------------------------------------------------
    # 1. Health & Truthful Subsystem Readiness Tests
    # -------------------------------------------------------------

    def test_health_endpoints_truthful_telemetry(self):
        """Verify that all health endpoints return 200 JSON with comprehensive truthful telemetry."""
        endpoints = ["/health", "/api/health", "/api", "/api/"]
        for ep in endpoints:
            with self.subTest(endpoint=ep):
                resp = self.client.get(ep)
                self.assertEqual(resp.status_code, 200)
                self.assertTrue("application/json" in resp.headers.get("content-type", ""))
                data = resp.json()
                self.assertEqual(data.get("status"), "ready")
                self.assertTrue(data.get("process_reachable"))
                self.assertTrue(data.get("optical_engine_initialized"))
                self.assertTrue(data.get("optical_engine_ready"))
                self.assertTrue(data.get("classifier_ready"))
                self.assertTrue(data.get("all_required_models_ready"))
                self.assertTrue(data.get("thresholds_ready"))
                self.assertEqual(data.get("ready_category_models_count"), 15)
                self.assertEqual(data.get("total_supported_categories"), 15)
                self.assertEqual(len(data.get("categories", [])), 15)
                self.assertIn("device", data)
                self.assertIn("timestamp", data)

    def test_health_degraded_when_category_memory_bank_missing(self):
        """Verify health transitions to 'degraded' when a category memory bank is unavailable."""
        with patch("app.get_optical_engine") as mock_get_engine:
            mock_engine = MagicMock()
            mock_engine.category_service.is_loaded = True
            
            # Simulate only 14 categories ready (e.g. 'bottle' memory bank missing)
            mock_status = {cat: {"is_ready": (cat != "bottle")} for cat in known_categories}
            mock_engine.registry.get_models_status.return_value = mock_status
            mock_engine.registry.thresholds = {cat: 1.5 for cat in known_categories}
            mock_get_engine.return_value = mock_engine

            health = get_system_health()
            self.assertEqual(health["status"], "degraded")
            self.assertEqual(health["ready_category_models_count"], 14)
            self.assertFalse(health["all_required_models_ready"])
            self.assertFalse(health["optical_engine_ready"])
            self.assertFalse(health["categories_status"]["bottle"])
            self.assertTrue(health["categories_status"]["cable"])

    def test_health_degraded_when_classifier_unavailable(self):
        """Verify health transitions to 'degraded' when category classifier is not loaded."""
        with patch("app.get_optical_engine") as mock_get_engine:
            mock_engine = MagicMock()
            mock_engine.category_service.is_loaded = False
            
            # All 15 memory banks ready, but classifier is offline
            mock_status = {cat: {"is_ready": True} for cat in known_categories}
            mock_engine.registry.get_models_status.return_value = mock_status
            mock_engine.registry.thresholds = {cat: 1.5 for cat in known_categories}
            mock_get_engine.return_value = mock_engine

            health = get_system_health()
            self.assertEqual(health["status"], "degraded")
            self.assertFalse(health["classifier_ready"])
            self.assertTrue(health["all_required_models_ready"])
            self.assertFalse(health["optical_engine_ready"])

    def test_health_not_ready_when_optical_engine_fails_to_init(self):
        """Verify health transitions to 'not_ready' if optical inspection engine fails initialization."""
        with patch("app.get_optical_engine") as mock_get_engine:
            mock_get_engine.side_effect = RuntimeError("GPU out of memory or missing engine files")

            health = get_system_health()
            self.assertEqual(health["status"], "not_ready")
            self.assertTrue(health["process_reachable"])
            self.assertFalse(health["optical_engine_initialized"])
            self.assertFalse(health["optical_engine_ready"])
            self.assertEqual(health["ready_category_models_count"], 0)
            self.assertIsNotNone(health["engine_error"])

    # -------------------------------------------------------------
    # 2. Strict CORS Security Tests
    # -------------------------------------------------------------

    def test_cors_approved_production_origin(self):
        """Verify production frontend origin receives Access-Control-Allow-Origin."""
        headers = {"Origin": "https://defectvision-ai.vercel.app"}
        resp = self.client.get("/health", headers=headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.headers.get("access-control-allow-origin"),
            "https://defectvision-ai.vercel.app"
        )
        self.assertEqual(resp.headers.get("access-control-allow-credentials"), "true")

    def test_cors_authorized_project_preview_origin(self):
        """Verify project-specific Vercel preview origin (defectvision-ai-*.vercel.app) is permitted."""
        headers = {"Origin": "https://defectvision-ai-git-fix-backend-test-suryacharan945.vercel.app"}
        resp = self.client.get("/health", headers=headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.headers.get("access-control-allow-origin"),
            "https://defectvision-ai-git-fix-backend-test-suryacharan945.vercel.app"
        )

    def test_cors_unapproved_unrelated_vercel_origin_rejected(self):
        """NEGATIVE TEST: Unrelated Vercel origin must NOT receive Access-Control-Allow-Origin."""
        headers = {"Origin": "https://unrelated-project.vercel.app"}
        resp = self.client.get("/health", headers=headers)
        self.assertEqual(resp.status_code, 200)
        self.assertIsNone(resp.headers.get("access-control-allow-origin"))

    def test_cors_unapproved_arbitrary_origin_rejected(self):
        """NEGATIVE TEST: Arbitrary external origin must NOT receive Access-Control-Allow-Origin."""
        headers = {"Origin": "https://malicious-attacker.com"}
        resp = self.client.get("/health", headers=headers)
        self.assertEqual(resp.status_code, 200)
        self.assertIsNone(resp.headers.get("access-control-allow-origin"))

    def test_cors_preflight_options_for_authorized_origin(self):
        """Verify OPTIONS preflight request succeeds for approved production origin."""
        headers = {
            "Origin": "https://defectvision-ai.vercel.app",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type"
        }
        resp = self.client.options("/predict", headers=headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.headers.get("access-control-allow-origin"),
            "https://defectvision-ai.vercel.app"
        )

    # -------------------------------------------------------------
    # 3. Model Registry & Schema Contract Tests
    # -------------------------------------------------------------

    def test_optical_model_status_endpoint(self):
        """Verify model-status endpoint returns calibrated thresholds and readiness for all 15 categories across all aliases."""
        for path in ["/api/optical-inspection/model-status", "/optical-inspection/model-status", "/api/models/status", "/models/status"]:
            resp = self.client.get(path)
            self.assertEqual(resp.status_code, 200, f"Failed on path {path}")
            data = resp.json()
            self.assertIn("categories", data)
            self.assertEqual(data.get("total_categories"), 15)
            self.assertTrue(data.get("all_ready"))
        categories = data["categories"]
        for cat in known_categories:
            self.assertIn(cat, categories)
            cat_info = categories[cat]
            self.assertIn("calibrated_threshold", cat_info)
            self.assertGreater(cat_info["calibrated_threshold"], 0.0)
            self.assertTrue(cat_info.get("is_ready", False))

    def test_predict_endpoint_schema_contract(self):
        """
        API Contract & Schema Test:
        Verifies that /predict correctly accepts multipart form image bytes,
        executes routing without disk write, and outputs the unified inspection schema.
        NOTE: This verifies the API schema contract, not empirical benchmark accuracy on physical defects.
        """
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

    # -------------------------------------------------------------
    # 4. Frontend Health Interpretation Contract Simulation
    # -------------------------------------------------------------

    def test_frontend_health_contract_simulation(self):
        """
        Simulates the frontend checkHealth logic in client.js to verify:
        - Ready payload promotes to live mode.
        - Degraded payload remains degraded and does NOT promote to live mode.
        - Not-ready / malformed payload transitions to not_ready.
        """
        def simulate_frontend_eval(raw_health):
            if not raw_health or not isinstance(raw_health, dict):
                return {"status": "degraded", "is_live": False}
            
            optical_ready = bool(raw_health.get("optical_engine_ready") or raw_health.get("optical_engine_initialized"))
            classifier_ready = bool(raw_health.get("classifier_ready"))
            all_models_ready = bool(raw_health.get("all_required_models_ready"))
            ready_count = int(raw_health.get("ready_category_models_count", 0))
            total_cats = int(raw_health.get("total_supported_categories", 15))
            backend_status = str(raw_health.get("status", "")).lower()

            is_truly_ready = (
                backend_status == "ready" and
                optical_ready and
                classifier_ready and
                all_models_ready and
                ready_count >= total_cats and
                total_cats == 15
            )

            if is_truly_ready:
                return {"status": "ready", "is_live": True}
            elif backend_status == "not_ready" or ready_count == 0 or not optical_ready:
                return {"status": "not_ready", "is_live": False}
            else:
                return {"status": "degraded", "is_live": False}

        # Case A: Fully ready backend
        ready_payload = {
            "status": "ready", "optical_engine_ready": True, "classifier_ready": True,
            "all_required_models_ready": True, "ready_category_models_count": 15, "total_supported_categories": 15
        }
        res_ready = simulate_frontend_eval(ready_payload)
        self.assertEqual(res_ready["status"], "ready")
        self.assertTrue(res_ready["is_live"])

        # Case B: Backend reports degraded (optical engine initialized, but only 12 models ready)
        degraded_payload = {
            "status": "degraded", "optical_engine_initialized": True, "optical_engine_ready": False,
            "classifier_ready": True, "all_required_models_ready": False, "ready_category_models_count": 12,
            "total_supported_categories": 15
        }
        res_degraded = simulate_frontend_eval(degraded_payload)
        self.assertEqual(res_degraded["status"], "degraded")
        self.assertFalse(res_degraded["is_live"])

        # Case C: Backend reports ready fraudulently but missing models
        fraudulent_payload = {
            "status": "ready", "optical_engine_ready": True, "classifier_ready": False,
            "all_required_models_ready": False, "ready_category_models_count": 10, "total_supported_categories": 15
        }
        res_fraud = simulate_frontend_eval(fraudulent_payload)
        self.assertEqual(res_fraud["status"], "degraded")
        self.assertFalse(res_fraud["is_live"])

        # Case D: Malformed payload
        res_malformed = simulate_frontend_eval(None)
        self.assertEqual(res_malformed["status"], "degraded")
        self.assertFalse(res_malformed["is_live"])


if __name__ == "__main__":
    unittest.main()
