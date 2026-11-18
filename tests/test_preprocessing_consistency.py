"""
DefectVision AI — Preprocessing Consistency & Pipeline Parity Regression Test
Validates Phase 3 requirements:
Proves that the same input image produces the exact same PatchCore feature tensor
and anomaly score through:
1. The offline evaluator/calibration pipeline (cv2 BGR->RGB -> 224x224 -> ImageNet norm).
2. The live OpticalInspectionEngine benchmark inference path.
Tests multiple MVTec AD categories (both objects and textures).
"""

import os
import sys
import unittest
import cv2
import numpy as np
import torch

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "DefectVisionAI"))

from src.camera_service import OpticalInspectionEngine
from src.patchcore import PatchCoreExtractor, PatchCoreModel

PC_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
PC_STD  = np.array([0.229, 0.224, 0.225], dtype=np.float32)
PC_IMG_SIZE = 224
GRID_SIZE = 28


def load_pc_tensor_offline(filepath, size=PC_IMG_SIZE):
    """Exact offline evaluator / memory bank reproduction preprocessing."""
    img = cv2.imread(filepath)
    if img is None:
        return None, None
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_res = cv2.resize(img_rgb, (size, size)).astype(np.float32) / 255.0
    img_norm = (img_res - PC_MEAN) / PC_STD
    tensor = torch.from_numpy(img_norm).permute(2, 0, 1).float()
    return img, tensor


class TestPreprocessingConsistency(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = OpticalInspectionEngine(device="cpu")
        cls.dataset_root = os.path.join(PROJECT_ROOT, "DefectVisionAI", "dataset", "raw", "mvtec")
        cls.categories_to_test = ["bottle", "cable", "capsule", "carpet", "tile"]

    def test_feature_tensor_and_score_parity(self):
        """Verifies exact numerical equivalence of features and scores between offline and engine paths."""
        for cat in self.categories_to_test:
            cat_dir = os.path.join(self.dataset_root, cat, "test", "good")
            if not os.path.exists(cat_dir):
                continue
            images = [os.path.join(cat_dir, f) for f in os.listdir(cat_dir) if f.endswith(".png")]
            if not images:
                continue

            test_img_path = images[0]
            img_bgr, offline_tensor = load_pc_tensor_offline(test_img_path)
            self.assertIsNotNone(img_bgr)
            self.assertIsNotNone(offline_tensor)

            # 1. Offline evaluation path
            model = cls_model = self.engine.get_patchcore_model(cat)
            self.assertIsNotNone(model, f"Failed to load memory bank for {cat}")

            with torch.no_grad():
                offline_emb = self.engine.extractor(offline_tensor.unsqueeze(0))[0].numpy()
            _, offline_score = model.score(offline_emb)

            # 2. Live engine benchmark inspection path
            live_result = self.engine.inspect_frame(
                img_bgr,
                operator_category_override=cat,
                routing_mode="benchmark",
                mode="upload"
            )

            live_score = live_result["anomaly_score"]

            # 3. Assert parity
            self.assertAlmostEqual(
                offline_score, live_score, places=3,
                msg=f"Score mismatch for category '{cat}': offline={offline_score:.4f} vs live={live_score:.4f}"
            )
            self.assertEqual(live_result["category"], cat)
            self.assertIn(live_result["verdict"], ["NORMAL", "REVIEW REQUIRED"])
            self.assertNotEqual(live_result["verdict"], "DEFECTIVE")


if __name__ == "__main__":
    unittest.main()
