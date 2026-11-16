"""
DefectVision AI — Category Recognition Architecture
Lightweight EfficientNet-B0 15-class industrial category recognizer with
calibrated confidence estimation and open-set unknown-category rejection.
"""

import os
import json
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models
import numpy as np
import cv2

KNOWN_CATEGORIES = [
    "bottle", "cable", "capsule", "carpet", "grid",
    "hazelnut", "leather", "metal_nut", "pill", "screw",
    "tile", "toothbrush", "transistor", "wood", "zipper"
]

CATEGORY_TYPE = {
    "bottle": "object", "cable": "object", "capsule": "object", "carpet": "texture",
    "grid": "texture", "hazelnut": "object", "leather": "texture", "metal_nut": "object",
    "pill": "object", "screw": "object", "tile": "texture", "toothbrush": "object",
    "transistor": "object", "wood": "texture", "zipper": "object"
}

IMG_SIZE = 224
IMG_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
IMG_STD  = np.array([0.229, 0.224, 0.225], dtype=np.float32)

class CategoryClassifier(nn.Module):
    def __init__(self, num_classes=15, pretrained=True, dropout=0.2):
        super().__init__()
        weights = models.EfficientNet_B0_Weights.IMAGENET1K_V1 if pretrained else None
        base = models.efficientnet_b0(weights=weights)
        self.features = base.features
        self.avgpool = base.avgpool
        in_features = base.classifier[1].in_features  # 1280
        
        self.head = nn.Sequential(
            nn.Dropout(p=dropout),
            nn.Linear(in_features, 256),
            nn.SiLU(),
            nn.Dropout(p=dropout),
            nn.Linear(256, num_classes)
        )
        self.temperature = nn.Parameter(torch.ones(1) * 1.0)
        self.num_classes = num_classes

    def forward(self, x):
        feat = self.features(x)
        pooled = self.avgpool(feat)
        flat = torch.flatten(pooled, 1)
        logits = self.head(flat)
        return logits

    def forward_calibrated(self, x):
        logits = self.forward(x)
        # Scaled by learned temperature
        T = torch.clamp(self.temperature, min=0.1, max=10.0)
        return logits / T

    def extract_features(self, x):
        feat = self.features(x)
        pooled = self.avgpool(feat)
        return torch.flatten(pooled, 1)


class CategoryRecognitionService:
    """
    High-level inference and unknown-rejection service for live optical inspection.
    """
    def __init__(self, model_path=None, meta_path=None, device="cpu", confidence_threshold=0.70):
        self.device = torch.device(device)
        self.confidence_threshold = confidence_threshold
        self.categories = KNOWN_CATEGORIES
        self.cat_to_id = {cat: i for i, cat in enumerate(self.categories)}
        self.id_to_cat = {i: cat for i, cat in enumerate(self.categories)}
        self.category_types = CATEGORY_TYPE

        self.model_path = model_path
        self.meta_path = meta_path
        self.model = CategoryClassifier(num_classes=len(self.categories), pretrained=False)
        self.is_loaded = False

        if model_path and os.path.exists(model_path):
            self.load(model_path, meta_path)

    def load(self, model_path, meta_path=None):
        checkpoint = torch.load(model_path, map_location=self.device)
        if isinstance(checkpoint, dict) and "state_dict" in checkpoint:
            self.model.load_state_dict(checkpoint["state_dict"])
            if "temperature" in checkpoint:
                self.model.temperature.data.fill_(float(checkpoint["temperature"]))
            if "confidence_threshold" in checkpoint:
                self.confidence_threshold = float(checkpoint["confidence_threshold"])
        else:
            self.model.load_state_dict(checkpoint)

        self.model.to(self.device)
        self.model.eval()
        self.is_loaded = True

        if meta_path and os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
                if "confidence_threshold" in meta:
                    self.confidence_threshold = float(meta["confidence_threshold"])
                if "categories" in meta:
                    self.categories = meta["categories"]
                    self.cat_to_id = {cat: i for i, cat in enumerate(self.categories)}
                    self.id_to_cat = {i: cat for i, cat in enumerate(self.categories)}

    def preprocess_image(self, img_bgr):
        """Preprocesses BGR image matrix to normalized PyTorch tensor (1, 3, 224, 224)."""
        if img_bgr is None:
            return None
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        img_res = cv2.resize(img_rgb, (IMG_SIZE, IMG_SIZE)).astype(np.float32) / 255.0
        img_norm = (img_res - IMG_MEAN) / IMG_STD
        tensor = torch.from_numpy(img_norm).permute(2, 0, 1).unsqueeze(0).float()
        return tensor.to(self.device)

    @torch.no_grad()
    def predict(self, img_bgr):
        """
        Runs category identification with confidence calibration and unknown rejection.
        Returns structured dict with detection telemetry.
        """
        if not self.is_loaded:
            if self.model_path and os.path.exists(self.model_path):
                try:
                    self.load(self.model_path, self.meta_path)
                except Exception as e:
                    print(f"Warning: Failed to load category classifier from {self.model_path}: {e}")
            if not self.is_loaded:
                return {
                    "category": "unknown",
                    "candidate_category": "unknown",
                    "category_type": "unknown",
                    "confidence": 0.0,
                    "confidence_threshold": self.confidence_threshold,
                    "is_supported": False,
                    "normalized_entropy": 1.0,
                    "status": "CLASSIFIER_NOT_LOADED",
                    "probabilities": {}
                }

        tensor = self.preprocess_image(img_bgr)
        if tensor is None:
            return {
                "category": "unknown",
                "category_type": "unknown",
                "confidence": 0.0,
                "is_supported": False,
                "entropy": 0.0,
                "status": "IMAGE_DECODE_FAILED",
                "probabilities": {}
            }

        logits = self.model.forward_calibrated(tensor)
        probs = F.softmax(logits, dim=1)[0].cpu().numpy()
        
        top_idx = int(np.argmax(probs))
        top_prob = float(probs[top_idx])
        top_cat = self.id_to_cat[top_idx]
        cat_type = self.category_types.get(top_cat, "unknown")

        # Shannon Entropy as uncertainty metric: H(P) = -sum(p * log(p))
        eps = 1e-9
        entropy = float(-np.sum(probs * np.log(probs + eps)))
        max_entropy = np.log(len(self.categories))
        norm_entropy = float(entropy / max_entropy)

        # Rejection decision
        is_supported = bool(top_prob >= self.confidence_threshold and norm_entropy < 0.65)
        status = "RECOGNIZED" if is_supported else "UNSUPPORTED_OR_UNCERTAIN"

        all_probs = {self.id_to_cat[i]: float(round(float(probs[i]), 4)) for i in range(len(probs))}

        return {
            "category": top_cat if is_supported else "unknown",
            "candidate_category": top_cat,
            "category_type": cat_type if is_supported else "unknown",
            "confidence": float(round(top_prob, 4)),
            "confidence_threshold": float(round(self.confidence_threshold, 4)),
            "is_supported": is_supported,
            "normalized_entropy": float(round(norm_entropy, 4)),
            "status": status,
            "probabilities": all_probs
        }
