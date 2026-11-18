"""
DefectVision AI â€” Production Inspection Profile Service
Manages domain-adapted, product-specific optical inspection profiles.
Each profile encapsulates:
- Station & camera hardware configuration
- Region of Interest (ROI) geometry (fixed coordinates or contour fallback)
- Image quality thresholds tailored to the product & illumination
- Domain-adapted PatchCore memory bank & FAISS index
- Calibrated decision threshold with targeted False Alarm Rate (FAR)
"""

import os
import json
import logging
import hashlib
from typing import Dict, List, Optional, Tuple, Any
import cv2
import numpy as np

logger = logging.getLogger("defectvision.production_profile")


class ProductionProfileService:
    def __init__(self, profiles_dir: Optional[str] = None):
        if profiles_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            profiles_dir = os.path.join(base_dir, "models", "production_profiles")
        self.profiles_dir = profiles_dir
        self.profiles: Dict[str, Dict[str, Any]] = {}
        self.loaded_models: Dict[str, Any] = {}
        self.reload_profiles()

    def reload_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Scans the profiles directory and loads all valid profile definitions."""
        self.profiles.clear()
        self.loaded_models.clear()

        if not os.path.exists(self.profiles_dir):
            os.makedirs(self.profiles_dir, exist_ok=True)
            return self.profiles

        for entry in os.listdir(self.profiles_dir):
            profile_path = os.path.join(self.profiles_dir, entry)
            if not os.path.isdir(profile_path):
                continue

            config_file = os.path.join(profile_path, "profile.json")
            if not os.path.exists(config_file):
                continue

            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                profile_id = data.get("profile_id", entry)
                is_valid, err = self.validate_profile_schema(data, profile_path)
                if is_valid:
                    data["_profile_dir"] = profile_path
                    self.profiles[profile_id] = data
                    logger.info(f"Loaded production profile: {profile_id}")
                else:
                    logger.warning(f"Skipping invalid profile '{entry}': {err}")
            except Exception as e:
                logger.error(f"Error loading profile '{entry}': {e}")

        return self.profiles

    def validate_profile_schema(self, data: Dict[str, Any], profile_path: str) -> Tuple[bool, Optional[str]]:
        """Validates that a profile contains all required fields and artifacts."""
        required_fields = [
            "profile_id",
            "product_id",
            "product_name",
            "inspection_station",
            "category",
            "roi_config",
            "quality_config",
            "threshold_config"
        ]
        for field in required_fields:
            if field not in data:
                return False, f"Missing required configuration field: '{field}'"

        mb_file = os.path.join(profile_path, "memory_bank.npy")
        if not os.path.exists(mb_file):
            return False, f"Missing PatchCore memory bank at: {mb_file}"

        return True, None

    def list_profiles(self) -> List[Dict[str, Any]]:
        """Returns summarized metadata for all loaded production profiles."""
        summaries = []
        for pid, p in self.profiles.items():
            thresh_cfg = p.get("threshold_config", {})
            model_cfg = p.get("model_config", {})
            summaries.append({
                "profile_id": p.get("profile_id", pid),
                "product_id": p.get("product_id", ""),
                "product_name": p.get("product_name", ""),
                "sku": p.get("sku", ""),
                "inspection_station": p.get("inspection_station", ""),
                "category": p.get("category", "unknown"),
                "category_type": p.get("category_type", "object"),
                "camera_id": p.get("camera_id", ""),
                "lighting_profile": p.get("lighting_profile", ""),
                "acquisition_type": p.get("acquisition_type", "stationary"),
                "calibrated_threshold": thresh_cfg.get("calibrated_threshold", 1.50),
                "target_far": thresh_cfg.get("target_far", 0.01),
                "model_version": model_cfg.get("model_version", "v1.0.0-prod"),
                "validation_status": p.get("validation_status", "SIMULATED REFERENCE PROFILE â€” NOT PRODUCTION VALIDATED"),
                "is_ready": True
            })
        return summaries

    def get_profile(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves full configuration dictionary for a given profile ID."""
        return self.profiles.get(profile_id)

    def get_profile_model(self, profile_id: str):
        """
        Loads and caches the PatchCoreModel for a given profile.
        Uses pre-built index.faiss if available, otherwise generates it from memory_bank.npy.
        """
        if profile_id in self.loaded_models:
            return self.loaded_models[profile_id]

        profile = self.get_profile(profile_id)
        if profile is None:
            return None

        profile_dir = profile.get("_profile_dir")
        if not profile_dir or not os.path.exists(profile_dir):
            return None

        mb_path = os.path.join(profile_dir, "memory_bank.npy")
        if not os.path.exists(mb_path):
            return None

        from src.patchcore import PatchCoreModel
        import faiss

        grid_size = profile.get("model_config", {}).get("grid_size", 28)
        model = PatchCoreModel()

        faiss_path = os.path.join(profile_dir, "index.faiss")
        if os.path.exists(faiss_path):
            try:
                model.memory_bank = np.load(mb_path)
                model.grid_size = grid_size
                model.index = faiss.read_index(faiss_path)
                self.loaded_models[profile_id] = model
                return model
            except Exception as e:
                logger.warning(f"Failed to load FAISS index from {faiss_path}, rebuilding: {e}")

        # Fallback to standard memory bank load
        model.load(mb_path, grid_size=grid_size)
        self.loaded_models[profile_id] = model
        return model

    def extract_roi(self, frame_bgr: np.ndarray, profile: Dict[str, Any]) -> Tuple[np.ndarray, Optional[Tuple[int, int, int, int]]]:
        """
        Extracts Region of Interest from frame based on profile configuration.
        Returns: (roi_bgr, bbox) where bbox is (x, y, w, h).
        """
        if frame_bgr is None or frame_bgr.size == 0:
            return frame_bgr, None

        h, w = frame_bgr.shape[:2]
        roi_cfg = profile.get("roi_config", {})
        roi_type = roi_cfg.get("type", "fixed_box")

        if roi_type == "fixed_box":
            # 1. Try relative bbox [rx, ry, rw, rh] (proportions of frame 0.0-1.0)
            if "relative_bbox" in roi_cfg:
                rx, ry, rw, rh = roi_cfg["relative_bbox"]
                bx = max(0, min(w - 1, int(rx * w)))
                by = max(0, min(h - 1, int(ry * h)))
                bw = max(1, min(w - bx, int(rw * w)))
                bh = max(1, min(h - by, int(rh * h)))
                roi = frame_bgr[by:by + bh, bx:bx + bw]
                return roi, (bx, by, bw, bh)

            # 2. Try absolute bbox [x, y, w, h]
            if "bbox" in roi_cfg:
                bx, by, bw, bh = roi_cfg["bbox"]
                bx = max(0, min(w - 1, int(bx)))
                by = max(0, min(h - 1, int(by)))
                bw = max(1, min(w - bx, int(bw)))
                bh = max(1, min(h - by, int(bh)))
                roi = frame_bgr[by:by + bh, bx:bx + bw]
                return roi, (bx, by, bw, bh)

        # Fallback to contour detection if configured or unknown type
        if roi_cfg.get("fallback_to_contour", True):
            from src.object_region_service import ObjectRegionService
            roi_service = ObjectRegionService()
            category_type = profile.get("category_type", "object")
            return roi_service.extract_roi(frame_bgr, category_type=category_type)

        # Full frame fallback
        return frame_bgr, (0, 0, w, h)

    def validate_quality(self, roi_bgr: np.ndarray, profile: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validates optical quality on the extracted ROI using background-aware foreground criteria.
        Distinguishes benign studio lightbox/backlight illumination from genuine product surface glare.
        Returns: (is_valid: bool, status: str, metrics: dict)
        """
        if roi_bgr is None or roi_bgr.size == 0:
            return False, "EMPTY_ROI", {"error": "ROI is empty or unreadable"}

        gray = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        total_pixels = h * w

        q_cfg = profile.get("quality_config", {})
        min_sharpness = float(q_cfg.get("min_sharpness", 15.0))
        min_brightness = float(q_cfg.get("min_brightness", 10.0))
        max_brightness = float(q_cfg.get("max_brightness", 245.0))
        min_contrast = float(q_cfg.get("min_contrast", 12.0))
        max_overexposed_pct = float(q_cfg.get("max_overexposed_pct", 35.0))
        min_fg_coverage_pct = float(q_cfg.get("min_fg_coverage_pct", 5.0))

        full_brightness = float(gray.mean())
        full_overexposed_pct = float(((gray >= 250).sum() / total_pixels) * 100.0)

        # Immediate illumination checks on full ROI
        if full_brightness < min_brightness:
            metrics = {
                "roi_resolution": f"{w}x{h}",
                "sharpness": 0.0,
                "sharpness_threshold": min_sharpness,
                "brightness": round(full_brightness, 2),
                "brightness_range": [min_brightness, max_brightness],
                "contrast": round(float(gray.std()), 2),
                "contrast_threshold": min_contrast,
                "overexposed_pct": round(full_overexposed_pct, 2),
                "max_overexposed_pct": max_overexposed_pct,
                "segmentation_status": "FULL_FRAME"
            }
            return False, "REJECT_INSUFFICIENT_ILLUMINATION", metrics

        if full_brightness > max_brightness or full_overexposed_pct >= 95.0:
            metrics = {
                "roi_resolution": f"{w}x{h}",
                "sharpness": 0.0,
                "sharpness_threshold": min_sharpness,
                "brightness": round(full_brightness, 2),
                "brightness_range": [min_brightness, max_brightness],
                "contrast": round(float(gray.std()), 2),
                "contrast_threshold": min_contrast,
                "overexposed_pct": round(full_overexposed_pct, 2),
                "max_overexposed_pct": max_overexposed_pct,
                "segmentation_status": "FULL_FRAME"
            }
            return False, "REJECT_OVEREXPOSED_OR_GLARE", metrics

        # 1. Border sampling to detect uniform studio illumination background
        border_pixels = np.concatenate([
            gray[:5, :].ravel(),
            gray[-5:, :].ravel(),
            gray[:, :5].ravel(),
            gray[:, -5:].ravel()
        ])
        border_mean = float(np.mean(border_pixels))
        border_std = float(np.std(border_pixels))

        is_uniform_light_bg = (border_mean >= 195.0 and border_std <= 40.0)
        is_uniform_dark_bg = (border_mean <= 50.0 and border_std <= 25.0)
        is_uniform_bg = is_uniform_light_bg or is_uniform_dark_bg

        # 2. Determine foreground region
        fg_mask = None
        segmentation_status = "FULL_FRAME"

        if is_uniform_bg:
            edges = cv2.Canny(gray, 20, 80)
            pts = np.argwhere(edges > 0)
            if len(pts) >= 40:
                pts_xy = np.column_stack((pts[:, 1], pts[:, 0]))  # [x, y]
                hull = cv2.convexHull(pts_xy)
                hull_mask = np.zeros((h, w), dtype=np.uint8)
                cv2.drawContours(hull_mask, [hull], -1, 255, -1)
                fg_mask = (hull_mask > 0)
                segmentation_status = "CONVEX_HULL_SEGMENTED"
            else:
                segmentation_status = "INSUFFICIENT_EDGES"
                fg_mask = np.zeros((h, w), dtype=bool)
        else:
            fg_mask = np.ones((h, w), dtype=bool)
            segmentation_status = "TEXTURE_OR_NONUNIFORM_BG"

        fg_pixel_count = int(fg_mask.sum())
        fg_coverage_pct = float((fg_pixel_count / total_pixels) * 100.0)

        # 3. Check for insufficient foreground visibility
        if is_uniform_bg and fg_coverage_pct < min_fg_coverage_pct:
            metrics = {
                "roi_resolution": f"{w}x{h}",
                "segmentation_status": segmentation_status,
                "foreground_coverage_pct": round(fg_coverage_pct, 2),
                "min_fg_coverage_pct": min_fg_coverage_pct,
                "border_mean": round(border_mean, 2),
                "border_std": round(border_std, 2)
            }
            return False, "REJECT_INSUFFICIENT_FOREGROUND", metrics

        # 4. Compute optical quality metrics on the segmented foreground
        fg_gray = gray[fg_mask]
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        fg_laplacian = laplacian[fg_mask]

        fg_brightness = float(fg_gray.mean())
        fg_contrast = float(fg_gray.std())
        fg_sharpness = float(np.var(fg_laplacian))

        fg_clipped_count = int((fg_gray >= 250).sum())
        fg_overexposed_pct = float((fg_clipped_count / fg_pixel_count) * 100.0)

        full_frame_overexposed_pct = float(((gray >= 250).sum() / total_pixels) * 100.0)
        full_frame_brightness = float(gray.mean())

        metrics = {
            "roi_resolution": f"{w}x{h}",
            "segmentation_status": segmentation_status,
            "foreground_coverage_pct": round(fg_coverage_pct, 2),
            "foreground_brightness": round(fg_brightness, 2),
            "foreground_contrast": round(fg_contrast, 2),
            "foreground_sharpness": round(fg_sharpness, 2),
            "foreground_overexposed_pct": round(fg_overexposed_pct, 2),
            "full_frame_overexposed_pct": round(full_frame_overexposed_pct, 2),
            "full_frame_brightness": round(full_frame_brightness, 2),
            "sharpness": round(fg_sharpness, 2),
            "sharpness_threshold": min_sharpness,
            "brightness": round(fg_brightness, 2),
            "brightness_range": [min_brightness, max_brightness],
            "contrast": round(fg_contrast, 2),
            "contrast_threshold": min_contrast,
            "overexposed_pct": round(fg_overexposed_pct, 2),
            "max_overexposed_pct": max_overexposed_pct
        }

        # 5. Evaluate Rejection Criteria
        is_too_dark = fg_brightness < min_brightness
        is_too_bright = fg_brightness > max_brightness
        is_excessive_glare = fg_overexposed_pct > max_overexposed_pct
        is_low_contrast = fg_contrast < min_contrast
        is_blurred = fg_sharpness < min_sharpness

        if is_too_dark:
            return False, "REJECT_INSUFFICIENT_ILLUMINATION", metrics
        if is_too_bright or is_excessive_glare:
            return False, "REJECT_OVEREXPOSED_OR_GLARE", metrics
        if is_low_contrast:
            return False, "REJECT_LOW_CONTRAST", metrics
        if is_blurred:
            return False, "REJECT_MOTION_OR_OPTICAL_BLUR", metrics

        return True, "OPTICAL_QUALITY_VERIFIED", metrics


def compute_file_sha256(filepath: str) -> str:
    """Computes SHA-256 checksum for a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()
