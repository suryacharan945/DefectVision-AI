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
import shutil
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any
import cv2
import numpy as np

logger = logging.getLogger("defectvision.production_profile")


def _clean_profile_for_disk(profile: Dict[str, Any]) -> Dict[str, Any]:
    """Returns a clean copy of the profile dictionary stripped of internal runtime keys."""
    return {k: v for k, v in profile.items() if not k.startswith("_")}


class ProductionProfileService:
    def __init__(self, profiles_dir: Optional[str] = None):
        if profiles_dir is None:
            env_profiles = os.environ.get("DEFECTVISION_PROFILES_DIR")
            env_data = os.environ.get("DEFECTVISION_DATA_DIR")
            if env_profiles:
                profiles_dir = env_profiles
            elif env_data:
                profiles_dir = os.path.join(env_data, "profiles")
            else:
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                profiles_dir = os.path.join(base_dir, "models", "production_profiles")
        self.profiles_dir = profiles_dir
        self.profiles: Dict[str, Dict[str, Any]] = {}
        self.loaded_models: Dict[str, Any] = {}
        self.reload_profiles()

    def is_storage_writable(self) -> bool:
        """Verifies that the profile storage directory exists and is writable for persistence."""
        try:
            os.makedirs(self.profiles_dir, exist_ok=True)
            test_path = os.path.join(self.profiles_dir, ".write_probe")
            with open(test_path, "w", encoding="utf-8") as f:
                f.write("probe")
            if os.path.exists(test_path):
                os.remove(test_path)
            return True
        except Exception as e:
            logger.warning(f"Profile storage directory {self.profiles_dir} is not writable: {e}")
            return False

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
            roi_cfg = p.get("roi_config", {})
            status = p.get("status", "active")

            p_dir = p.get("_profile_dir", "")
            manifest_path = os.path.join(p_dir, "manifest.json") if p_dir else ""
            manifest_data = {}
            if manifest_path and os.path.exists(manifest_path):
                try:
                    with open(manifest_path, "r", encoding="utf-8") as mf:
                        manifest_data = json.load(mf)
                except Exception:
                    pass

            mb_file = os.path.join(p_dir, "memory_bank.npy") if p_dir else ""
            mb_size = os.path.getsize(mb_file) if (mb_file and os.path.exists(mb_file)) else 0

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
                "status": status,
                "is_active": (status == "active"),
                "is_adapted": p.get("is_adapted", False),
                "is_provisional": p.get("is_provisional", False),
                "disclaimer": p.get("disclaimer", ""),
                "calibrated_threshold": thresh_cfg.get("calibrated_threshold", 1.50),
                "target_far": thresh_cfg.get("target_far", 0.01),
                "model_version": model_cfg.get("model_version", "v1.0.0-prod"),
                "validation_status": p.get("validation_status", "PROVISIONAL ADAPTED REFERENCE PROFILE"),
                "training_samples_count": manifest_data.get("training_samples_count", thresh_cfg.get("calibration_sample_count", 0)),
                "calibration_samples_count": manifest_data.get("calibration_samples_count", thresh_cfg.get("calibration_sample_count", 0)),
                "coreset_vectors_count": manifest_data.get("coreset_vectors_count", 0),
                "memory_bank_size_bytes": mb_size,
                "created_at": manifest_data.get("created_at", thresh_cfg.get("calibration_date", "")),
                "updated_at": p.get("updated_at", manifest_data.get("created_at", thresh_cfg.get("calibration_date", ""))),
                "roi_type": roi_cfg.get("type", "fixed_box"),
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

    def create_adapted_profile(
        self,
        product_name: str,
        sku: str,
        category: str = "bottle",
        acquisition_type: str = "controlled_photography",
        camera_id: str = "CAM-EXT-01",
        lighting_profile: str = "ambient_or_diffuse",
        normal_images: Optional[List[np.ndarray]] = None,
        image_filenames: Optional[List[str]] = None,
        calibration_split_ratio: float = 0.30,
        extractor=None,
        device=None,
        coreset_ratio: float = 0.10,
        grid_size: int = 28
    ) -> Dict[str, Any]:
        """
        Creates, builds, calibrates, and registers a new product-specific PatchCore profile
        from user-provided defect-free normal reference images.

        Enforces:
        - Strict separation between memory-bank training samples and threshold calibration samples.
        - Reuse of frozen ResNet18 PatchCore feature extractor.
        - Comprehensive artifact manifest with SHA-256 hashes and provisional threshold disclosure.
        - Immediate persistence and live registration into ProductionProfileService.
        """
        import time
        from datetime import datetime, timezone
        import torch
        import faiss

        t_start = time.time()

        if not normal_images or len(normal_images) < 2:
            raise ValueError(
                f"Few-shot adaptation requires at least 2 normal reference images (received {len(normal_images) if normal_images else 0})."
            )

        # 1. Image intake and quality screening on all uploaded samples
        from src.universal_intake_service import UniversalImageIntakeService
        intake_service = UniversalImageIntakeService()

        valid_samples = []
        rejected_samples = []

        for idx, img_bgr in enumerate(normal_images):
            fname = image_filenames[idx] if (image_filenames and idx < len(image_filenames)) else f"sample_{idx:03d}.png"
            intake_res = intake_service.process_image(img_bgr, inspection_mode="production")
            if intake_res["image_quality_status"] == "OPTICAL_QUALITY_VERIFIED" or intake_res["suitability_status"] in ["SUITABLE", "SUITABLE_WITH_PREPROCESSING"]:
                valid_samples.append({
                    "filename": fname,
                    "img_bgr": img_bgr,
                    "intake": intake_res
                })
            else:
                rejected_samples.append({
                    "filename": fname,
                    "reason": intake_res["rejection_reason"] or intake_res["image_quality_status"]
                })

        if len(valid_samples) < 2:
            reasons = "; ".join([f"{r['filename']}: {r['reason']}" for r in rejected_samples])
            raise ValueError(
                f"Fewer than 2 uploaded images passed optical quality verification ({len(valid_samples)} valid, {len(rejected_samples)} rejected). Rejection details: {reasons}"
            )

        # 2. Strict calibration split: separate training subset from calibration subset
        total_valid = len(valid_samples)
        cal_count = max(1, int(round(total_valid * calibration_split_ratio)))
        if total_valid - cal_count < 1:
            cal_count = 1
        train_count = total_valid - cal_count

        train_samples = valid_samples[:train_count]
        cal_samples = valid_samples[train_count:]

        # 3. Generate sanitized profile ID and destination directory
        clean_sku = "".join(c if c.isalnum() else "_" for c in sku.lower()).strip("_")
        clean_cat = "".join(c if c.isalnum() else "_" for c in category.lower()).strip("_")
        profile_id = f"{clean_cat}_{clean_sku}"
        dest_dir = os.path.join(self.profiles_dir, profile_id)
        os.makedirs(dest_dir, exist_ok=True)

        # 4. Determine representative ROI geometry from valid training samples
        bboxes = [s["intake"]["foreground_bbox"] for s in train_samples if s["intake"]["foreground_bbox"] is not None]
        if bboxes:
            sample_h, sample_w = train_samples[0]["img_bgr"].shape[:2]
            avg_x = int(np.median([b[0] for b in bboxes]))
            avg_y = int(np.median([b[1] for b in bboxes]))
            avg_w = int(np.median([b[2] for b in bboxes]))
            avg_h = int(np.median([b[3] for b in bboxes]))

            # Add conservative margin (8%)
            margin_x = int(avg_w * 0.08)
            margin_y = int(avg_h * 0.08)
            bx = max(0, avg_x - margin_x)
            by = max(0, avg_y - margin_y)
            bw = min(sample_w - bx, avg_w + 2 * margin_x)
            bh = min(sample_h - by, avg_h + 2 * margin_y)

            roi_config = {
                "type": "fixed_box",
                "relative_bbox": [
                    round(float(bx) / sample_w, 4),
                    round(float(by) / sample_h, 4),
                    round(float(bw) / sample_w, 4),
                    round(float(bh) / sample_h, 4)
                ],
                "bbox": [bx, by, bw, bh],
                "fallback_to_contour": True
            }
        else:
            roi_config = {
                "type": "fixed_box",
                "relative_bbox": [0.05, 0.05, 0.90, 0.90],
                "fallback_to_contour": True
            }

        # 5. Extract PatchCore patch embeddings using frozen ResNet18
        if extractor is None:
            from src.patchcore import PatchCoreExtractor
            torch_dev = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
            extractor = PatchCoreExtractor(grid_size=grid_size).to(torch_dev)
            extractor.eval()
        else:
            torch_dev = next(extractor.parameters()).device

        PC_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        PC_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        PC_IMG_SIZE = 224

        all_patches = []
        for s in train_samples:
            img = s["img_bgr"]
            # Apply ROI if defined
            if "relative_bbox" in roi_config:
                rx, ry, rw, rh = roi_config["relative_bbox"]
                h_img, w_img = img.shape[:2]
                cx1 = int(rx * w_img)
                cy1 = int(ry * h_img)
                cx2 = min(w_img, cx1 + int(rw * w_img))
                cy2 = min(h_img, cy1 + int(rh * h_img))
                roi = img[cy1:cy2, cx1:cx2]
            else:
                roi = img

            rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
            resized = cv2.resize(rgb, (PC_IMG_SIZE, PC_IMG_SIZE)).astype(np.float32) / 255.0
            norm = (resized - PC_MEAN) / PC_STD
            tensor = torch.from_numpy(norm).permute(2, 0, 1).unsqueeze(0).float().to(torch_dev)

            with torch.no_grad():
                fused = extractor(tensor)[0].cpu().numpy()  # (384, grid_size, grid_size)
            C, g, _ = fused.shape
            patches = fused.reshape(C, g * g).T.astype(np.float32)
            all_patches.append(patches)

        raw_memory_bank = np.vstack(all_patches)
        total_patches, dim = raw_memory_bank.shape

        # 6. Coreset subsampling
        target_k = max(1, int(round(total_patches * coreset_ratio)))
        if total_patches > target_k:
            rng = np.random.RandomState(42)
            indices = [int(rng.randint(total_patches))]
            min_dists = np.linalg.norm(raw_memory_bank - raw_memory_bank[indices[0]], axis=1)
            for _ in range(1, target_k):
                next_idx = int(np.argmax(min_dists))
                indices.append(next_idx)
                new_dists = np.linalg.norm(raw_memory_bank - raw_memory_bank[next_idx], axis=1)
                min_dists = np.minimum(min_dists, new_dists)
            coreset_bank = raw_memory_bank[indices].astype(np.float32)
        else:
            coreset_bank = raw_memory_bank.astype(np.float32)

        # 7. Build FAISS IndexFlatL2
        index = faiss.IndexFlatL2(dim)
        index.add(coreset_bank)

        mb_file = os.path.join(dest_dir, "memory_bank.npy")
        faiss_file = os.path.join(dest_dir, "index.faiss")
        np.save(mb_file, coreset_bank)
        faiss.write_index(index, faiss_file)

        # 8. Score held-out calibration samples using the newly created model
        from src.patchcore import PatchCoreModel
        temp_model = PatchCoreModel()
        temp_model.memory_bank = coreset_bank
        temp_model.grid_size = grid_size
        temp_model.index = index

        cal_scores = []
        for s in cal_samples:
            img = s["img_bgr"]
            if "relative_bbox" in roi_config:
                rx, ry, rw, rh = roi_config["relative_bbox"]
                h_img, w_img = img.shape[:2]
                cx1 = int(rx * w_img)
                cy1 = int(ry * h_img)
                cx2 = min(w_img, cx1 + int(rw * w_img))
                cy2 = min(h_img, cy1 + int(rh * h_img))
                roi = img[cy1:cy2, cx1:cx2]
            else:
                roi = img

            rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
            resized = cv2.resize(rgb, (PC_IMG_SIZE, PC_IMG_SIZE)).astype(np.float32) / 255.0
            norm = (resized - PC_MEAN) / PC_STD
            tensor = torch.from_numpy(norm).permute(2, 0, 1).unsqueeze(0).float().to(torch_dev)

            with torch.no_grad():
                fused = extractor(tensor)[0].cpu().numpy()
            _, score = temp_model.score(fused)
            cal_scores.append(float(score))

        cal_arr = np.array(cal_scores, dtype=np.float32)
        cal_mean = float(np.mean(cal_arr))
        cal_std = float(np.std(cal_arr)) if len(cal_arr) > 1 else 0.05
        cal_max = float(np.max(cal_arr))

        # Provisional calibrated threshold calculation
        if len(cal_arr) >= 10:
            calibrated_threshold = float(round(float(np.percentile(cal_arr, 99)) + 0.3 * cal_std, 4))
        else:
            calibrated_threshold = float(round(cal_max + max(0.08, 0.5 * cal_std), 4))

        now_iso = datetime.now(timezone.utc).isoformat()

        # 9. Build complete profile.json
        profile_json_data = {
            "profile_id": profile_id,
            "product_id": f"PROD-{clean_sku.upper()}",
            "product_name": product_name,
            "sku": sku,
            "inspection_station": f"Station Adapted — {product_name}",
            "category": category,
            "category_type": "object",
            "camera_id": camera_id,
            "lighting_profile": lighting_profile,
            "acquisition_type": acquisition_type,
            "validation_status": "PROVISIONAL ADAPTED REFERENCE PROFILE — FEW-SHOT ADAPTATION",
            "is_adapted": True,
            "is_provisional": True,
            "disclaimer": f"Provisional threshold ({calibrated_threshold:.4f}) derived from {len(cal_samples)} held-out normal calibration samples. Target false alarm rate not certified without larger sample size.",
            "roi_config": roi_config,
            "quality_config": {
                "min_sharpness": 12.0,
                "min_brightness": 10.0,
                "max_brightness": 245.0,
                "min_contrast": 10.0,
                "max_overexposed_pct": 35.0
            },
            "preprocessing_config": {
                "input_size": [224, 224],
                "mean": [0.485, 0.456, 0.406],
                "std": [0.229, 0.224, 0.225]
            },
            "model_config": {
                "backbone": "resnet18",
                "feature_layers": ["layer2", "layer3"],
                "target_dimension": 384,
                "coreset_ratio": coreset_ratio,
                "grid_size": grid_size,
                "faiss_index_type": "IndexFlatL2",
                "model_version": "v2.0.0-adapted"
            },
            "threshold_config": {
                "calibrated_threshold": calibrated_threshold,
                "target_far": 0.01,
                "calibration_sample_count": len(cal_samples),
                "calibration_date": now_iso,
                "is_provisional": True,
                "metrics": {
                    "mean": round(cal_mean, 4),
                    "std": round(cal_std, 4),
                    "p50": round(float(np.percentile(cal_arr, 50)), 4),
                    "p75": round(float(np.percentile(cal_arr, 75)), 4),
                    "p90": round(float(np.percentile(cal_arr, 90)), 4),
                    "p95": round(float(np.percentile(cal_arr, 95)), 4),
                    "p99": round(float(np.percentile(cal_arr, 99)), 4),
                    "max": round(cal_max, 4)
                }
            }
        }

        profile_file = os.path.join(dest_dir, "profile.json")
        with open(profile_file, "w", encoding="utf-8") as f:
            json.dump(profile_json_data, f, indent=2)

        # 10. Build manifest.json
        manifest_data = {
            "profile_id": profile_id,
            "created_at": now_iso,
            "product_name": product_name,
            "sku": sku,
            "category": category,
            "acquisition_type": acquisition_type,
            "camera_id": camera_id,
            "lighting_profile": lighting_profile,
            "training_samples_count": len(train_samples),
            "calibration_samples_count": len(cal_samples),
            "rejected_samples_count": len(rejected_samples),
            "raw_patches_count": total_patches,
            "coreset_vectors_count": int(coreset_bank.shape[0]),
            "feature_dim": dim,
            "grid_size": grid_size,
            "coreset_ratio": coreset_ratio,
            "calibrated_threshold": calibrated_threshold,
            "is_provisional": True,
            "build_duration_sec": round(time.time() - t_start, 2),
            "artifacts": {
                "memory_bank.npy": {
                    "sha256": compute_file_sha256(mb_file),
                    "size_bytes": os.path.getsize(mb_file)
                },
                "index.faiss": {
                    "sha256": compute_file_sha256(faiss_file),
                    "size_bytes": os.path.getsize(faiss_file)
                },
                "profile.json": {
                    "sha256": compute_file_sha256(profile_file),
                    "size_bytes": os.path.getsize(profile_file)
                }
            }
        }

        manifest_file = os.path.join(dest_dir, "manifest.json")
        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2)

        # 11. Build threshold.json
        threshold_data = {
            "profile_id": profile_id,
            "calibrated_threshold": calibrated_threshold,
            "target_far": 0.01,
            "calibration_date": now_iso,
            "is_provisional": True,
            "disclaimer": profile_json_data["disclaimer"],
            "sample_counts": {
                "normal_training_samples": len(train_samples),
                "normal_calibration_samples": len(cal_samples),
                "rejected_samples": len(rejected_samples)
            },
            "score_distribution": profile_json_data["threshold_config"]["metrics"]
        }

        threshold_file = os.path.join(dest_dir, "threshold.json")
        with open(threshold_file, "w", encoding="utf-8") as f:
            json.dump(threshold_data, f, indent=2)

        # 12. Register immediately in active service
        self.reload_profiles()

        return {
            "status": "success",
            "profile_id": profile_id,
            "product_name": product_name,
            "sku": sku,
            "category": category,
            "training_samples_count": len(train_samples),
            "calibration_samples_count": len(cal_samples),
            "rejected_samples_count": len(rejected_samples),
            "coreset_vectors_count": int(coreset_bank.shape[0]),
            "calibrated_threshold": calibrated_threshold,
            "is_provisional": True,
            "validation_status": profile_json_data["validation_status"],
            "disclaimer": profile_json_data["disclaimer"],
            "build_duration_sec": round(time.time() - t_start, 2),
            "manifest": manifest_data
        }

    def activate_profile(self, profile_id: str) -> Dict[str, Any]:
        """Activates a production profile for live inspection routing."""
        profile = self.get_profile(profile_id)
        if not profile:
            raise ValueError(f"Profile '{profile_id}' not found.")
        profile["status"] = "active"
        profile["updated_at"] = datetime.now(timezone.utc).isoformat()
        cfg_file = os.path.join(profile["_profile_dir"], "profile.json")
        with open(cfg_file, "w", encoding="utf-8") as f:
            json.dump(_clean_profile_for_disk(profile), f, indent=2)
        logger.info(f"Activated production profile: {profile_id}")
        return {"status": "success", "profile_id": profile_id, "profile_status": "active"}

    def deactivate_profile(self, profile_id: str) -> Dict[str, Any]:
        """Deactivates a production profile (temporarily suspended from routing)."""
        profile = self.get_profile(profile_id)
        if not profile:
            raise ValueError(f"Profile '{profile_id}' not found.")
        profile["status"] = "inactive"
        profile["updated_at"] = datetime.now(timezone.utc).isoformat()
        cfg_file = os.path.join(profile["_profile_dir"], "profile.json")
        with open(cfg_file, "w", encoding="utf-8") as f:
            json.dump(_clean_profile_for_disk(profile), f, indent=2)
        logger.info(f"Deactivated production profile: {profile_id}")
        return {"status": "success", "profile_id": profile_id, "profile_status": "inactive"}

    def archive_profile(self, profile_id: str) -> Dict[str, Any]:
        """Archives a production profile and unloads it from resident memory."""
        profile = self.get_profile(profile_id)
        if not profile:
            raise ValueError(f"Profile '{profile_id}' not found.")
        profile["status"] = "archived"
        profile["updated_at"] = datetime.now(timezone.utc).isoformat()
        cfg_file = os.path.join(profile["_profile_dir"], "profile.json")
        with open(cfg_file, "w", encoding="utf-8") as f:
            json.dump(_clean_profile_for_disk(profile), f, indent=2)
        if profile_id in self.loaded_models:
            del self.loaded_models[profile_id]
        logger.info(f"Archived production profile: {profile_id}")
        return {"status": "success", "profile_id": profile_id, "profile_status": "archived"}

    def delete_profile(self, profile_id: str) -> Dict[str, Any]:
        """Permanently deletes a production profile directory and unloads its model."""
        profile = self.get_profile(profile_id)
        if not profile:
            raise ValueError(f"Profile '{profile_id}' not found.")
        p_dir = profile.get("_profile_dir")
        if profile_id in self.loaded_models:
            del self.loaded_models[profile_id]
        if profile_id in self.profiles:
            del self.profiles[profile_id]
        if p_dir and os.path.exists(p_dir):
            shutil.rmtree(p_dir)
        logger.info(f"Deleted production profile: {profile_id}")
        return {"status": "deleted", "profile_id": profile_id}

    def update_profile(self, profile_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Updates editable metadata and configuration fields of an existing profile."""
        profile = self.get_profile(profile_id)
        if not profile:
            raise ValueError(f"Profile '{profile_id}' not found.")
        allowed_scalars = ["product_name", "sku", "inspection_station", "camera_id", "lighting_profile", "acquisition_type"]
        for k in allowed_scalars:
            if k in updates and updates[k] is not None:
                profile[k] = updates[k]
        if "quality_config" in updates and isinstance(updates["quality_config"], dict):
            profile.setdefault("quality_config", {}).update(updates["quality_config"])
        if "threshold_config" in updates and isinstance(updates["threshold_config"], dict):
            profile.setdefault("threshold_config", {}).update(updates["threshold_config"])
        if "roi_config" in updates and isinstance(updates["roi_config"], dict):
            profile.setdefault("roi_config", {}).update(updates["roi_config"])
        profile["updated_at"] = datetime.now(timezone.utc).isoformat()
        cfg_file = os.path.join(profile["_profile_dir"], "profile.json")
        with open(cfg_file, "w", encoding="utf-8") as f:
            json.dump(_clean_profile_for_disk(profile), f, indent=2)
        return profile

    def get_profile_analytics(self, profile_id: str) -> Dict[str, Any]:
        """Returns deep telemetry, score distributions, and artifact metadata for a profile."""
        profile = self.get_profile(profile_id)
        if not profile:
            raise ValueError(f"Profile '{profile_id}' not found.")
        p_dir = profile.get("_profile_dir", "")
        manifest_path = os.path.join(p_dir, "manifest.json")
        threshold_path = os.path.join(p_dir, "threshold.json")
        manifest = {}
        threshold_info = {}
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
            except Exception:
                pass
        if os.path.exists(threshold_path):
            try:
                with open(threshold_path, "r", encoding="utf-8") as f:
                    threshold_info = json.load(f)
            except Exception:
                pass

        model = self.get_profile_model(profile_id)
        mb_shape = list(model.memory_bank.shape) if (model and model.memory_bank is not None) else []
        faiss_total = model.index.ntotal if (model and model.index is not None) else 0

        return {
            "profile_id": profile_id,
            "product_name": profile.get("product_name"),
            "sku": profile.get("sku"),
            "category": profile.get("category"),
            "status": profile.get("status", "active"),
            "calibrated_threshold": profile.get("threshold_config", {}).get("calibrated_threshold"),
            "target_far": profile.get("threshold_config", {}).get("target_far"),
            "score_metrics": profile.get("threshold_config", {}).get("metrics", {}),
            "manifest": manifest,
            "threshold_info": threshold_info,
            "memory_bank": {
                "shape": mb_shape,
                "vectors": faiss_total,
                "feature_dimension": mb_shape[1] if len(mb_shape) > 1 else 384,
                "coreset_ratio": profile.get("model_config", {}).get("coreset_ratio", 0.10)
            },
            "roi_config": profile.get("roi_config", {}),
            "quality_config": profile.get("quality_config", {})
        }

    def evaluate_profile(
        self,
        profile_id: str,
        test_images: List[np.ndarray],
        filenames: Optional[List[str]] = None,
        true_labels: Optional[List[str]] = None,
        extractor=None,
        device=None
    ) -> Dict[str, Any]:
        """
        Evaluates a batch of test images against the profile's PatchCore memory bank and threshold.
        Returns accuracy, precision, recall, specificity, F1, and per-sample predictions.
        """
        import torch

        profile = self.get_profile(profile_id)
        if not profile:
            raise ValueError(f"Profile '{profile_id}' not found.")
        model = self.get_profile_model(profile_id)
        if not model:
            raise ValueError(f"Could not load model for profile '{profile_id}'.")

        thresh = float(profile.get("threshold_config", {}).get("calibrated_threshold", 1.50))
        roi_cfg = profile.get("roi_config", {})

        if extractor is None:
            from src.patchcore import PatchCoreExtractor
            torch_dev = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
            extractor = PatchCoreExtractor(grid_size=profile.get("model_config", {}).get("grid_size", 28)).to(torch_dev)
            extractor.eval()
        else:
            torch_dev = next(extractor.parameters()).device

        PC_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        PC_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        PC_IMG_SIZE = 224

        sample_results = []
        scores = []
        latencies = []

        for idx, img in enumerate(test_images):
            fname = filenames[idx] if (filenames and idx < len(filenames)) else f"test_{idx:03d}.png"
            t0 = time.perf_counter()

            if "relative_bbox" in roi_cfg:
                rx, ry, rw, rh = roi_cfg["relative_bbox"]
                h_img, w_img = img.shape[:2]
                cx1 = int(rx * w_img)
                cy1 = int(ry * h_img)
                cx2 = min(w_img, cx1 + int(rw * w_img))
                cy2 = min(h_img, cy1 + int(rh * h_img))
                roi = img[cy1:cy2, cx1:cx2]
            else:
                roi = img

            rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
            resized = cv2.resize(rgb, (PC_IMG_SIZE, PC_IMG_SIZE)).astype(np.float32) / 255.0
            norm = (resized - PC_MEAN) / PC_STD
            tensor = torch.from_numpy(norm).permute(2, 0, 1).unsqueeze(0).float().to(torch_dev)

            with torch.no_grad():
                fused = extractor(tensor)[0].cpu().numpy()
            _, score = model.score(fused)
            elapsed_ms = (time.perf_counter() - t0) * 1000.0

            raw_score = float(score)
            is_defective = bool(raw_score >= thresh)
            pred_verdict = "DEFECTIVE" if is_defective else "NORMAL"

            ground_truth = true_labels[idx].upper() if (true_labels and idx < len(true_labels) and true_labels[idx]) else None
            is_correct = (pred_verdict == ground_truth) if ground_truth in ["NORMAL", "DEFECTIVE"] else None

            sample_results.append({
                "filename": fname,
                "anomaly_score": round(raw_score, 4),
                "threshold": round(thresh, 4),
                "verdict": pred_verdict,
                "ground_truth": ground_truth,
                "is_correct": is_correct,
                "latency_ms": round(elapsed_ms, 2)
            })
            scores.append(raw_score)
            latencies.append(elapsed_ms)

        metrics = {}
        labeled_count = sum(1 for s in sample_results if s["ground_truth"] in ["NORMAL", "DEFECTIVE"])
        if labeled_count > 0:
            tp = sum(1 for s in sample_results if s["verdict"] == "DEFECTIVE" and s["ground_truth"] == "DEFECTIVE")
            tn = sum(1 for s in sample_results if s["verdict"] == "NORMAL" and s["ground_truth"] == "NORMAL")
            fp = sum(1 for s in sample_results if s["verdict"] == "DEFECTIVE" and s["ground_truth"] == "NORMAL")
            fn = sum(1 for s in sample_results if s["verdict"] == "NORMAL" and s["ground_truth"] == "DEFECTIVE")

            total_labeled = tp + tn + fp + fn
            acc = (tp + tn) / max(1, total_labeled)
            prec = tp / max(1, (tp + fp)) if (tp + fp) > 0 else 0.0
            rec = tp / max(1, (tp + fn)) if (tp + fn) > 0 else 0.0
            spec = tn / max(1, (tn + fp)) if (tn + fp) > 0 else 0.0
            f1 = (2 * prec * rec) / max(1e-6, (prec + rec)) if (prec + rec) > 0 else 0.0

            metrics = {
                "total_evaluated": len(test_images),
                "labeled_count": labeled_count,
                "accuracy": round(acc, 4),
                "precision": round(prec, 4),
                "recall": round(rec, 4),
                "specificity": round(spec, 4),
                "f1_score": round(f1, 4),
                "confusion_matrix": {"TP": tp, "TN": tn, "FP": fp, "FN": fn}
            }
        else:
            metrics = {
                "total_evaluated": len(test_images),
                "defective_count": sum(1 for s in sample_results if s["verdict"] == "DEFECTIVE"),
                "normal_count": sum(1 for s in sample_results if s["verdict"] == "NORMAL")
            }

        metrics["mean_score"] = round(float(np.mean(scores)), 4) if scores else 0.0
        metrics["std_score"] = round(float(np.std(scores)), 4) if len(scores) > 1 else 0.0
        metrics["mean_latency_ms"] = round(float(np.mean(latencies)), 2) if latencies else 0.0

        return {
            "profile_id": profile_id,
            "threshold": thresh,
            "metrics": metrics,
            "samples": sample_results
        }

    def update_profile_references(
        self,
        profile_id: str,
        new_normal_images: List[np.ndarray],
        filenames: Optional[List[str]] = None,
        calibration_split_ratio: float = 0.30,
        coreset_ratio: float = 0.10,
        extractor=None,
        device=None
    ) -> Dict[str, Any]:
        """
        Adds additional normal reference images to an existing profile, rebuilding
        the coreset memory bank and re-calibrating the provisional threshold.
        """
        import torch
        import faiss

        profile = self.get_profile(profile_id)
        if not profile:
            raise ValueError(f"Profile '{profile_id}' not found.")

        dest_dir = profile.get("_profile_dir")
        if not dest_dir or not os.path.exists(dest_dir):
            raise ValueError(f"Directory missing for profile '{profile_id}'.")

        # Extract features for new valid images
        from src.universal_intake_service import UniversalImageIntakeService
        intake_service = UniversalImageIntakeService()

        valid_samples = []
        for idx, img_bgr in enumerate(new_normal_images):
            fname = filenames[idx] if (filenames and idx < len(filenames)) else f"update_sample_{idx:03d}.png"
            intake_res = intake_service.process_image(img_bgr, inspection_mode="production")
            if intake_res["image_quality_status"] == "OPTICAL_QUALITY_VERIFIED" or intake_res["suitability_status"] in ["SUITABLE", "SUITABLE_WITH_PREPROCESSING"]:
                valid_samples.append({"filename": fname, "img_bgr": img_bgr, "intake": intake_res})

        if not valid_samples:
            raise ValueError("None of the uploaded update images passed optical quality verification.")

        # Split update samples into training and calibration
        cal_count = max(1, int(round(len(valid_samples) * calibration_split_ratio)))
        train_count = max(1, len(valid_samples) - cal_count)
        train_samples = valid_samples[:train_count]
        cal_samples = valid_samples[train_count:]

        # Feature extraction
        grid_size = profile.get("model_config", {}).get("grid_size", 28)
        if extractor is None:
            from src.patchcore import PatchCoreExtractor
            torch_dev = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
            extractor = PatchCoreExtractor(grid_size=grid_size).to(torch_dev)
            extractor.eval()
        else:
            torch_dev = next(extractor.parameters()).device

        PC_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        PC_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        PC_IMG_SIZE = 224
        roi_config = profile.get("roi_config", {})

        new_patches_list = []
        for s in train_samples:
            img = s["img_bgr"]
            if "relative_bbox" in roi_config:
                rx, ry, rw, rh = roi_config["relative_bbox"]
                h_img, w_img = img.shape[:2]
                cx1 = int(rx * w_img)
                cy1 = int(ry * h_img)
                cx2 = min(w_img, cx1 + int(rw * w_img))
                cy2 = min(h_img, cy1 + int(rh * h_img))
                roi = img[cy1:cy2, cx1:cx2]
            else:
                roi = img

            rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
            resized = cv2.resize(rgb, (PC_IMG_SIZE, PC_IMG_SIZE)).astype(np.float32) / 255.0
            norm = (resized - PC_MEAN) / PC_STD
            tensor = torch.from_numpy(norm).permute(2, 0, 1).unsqueeze(0).float().to(torch_dev)

            with torch.no_grad():
                fused = extractor(tensor)[0].cpu().numpy()
            C, g, _ = fused.shape
            patches = fused.reshape(C, g * g).T.astype(np.float32)
            new_patches_list.append(patches)

        new_raw_patches = np.vstack(new_patches_list)

        # Merge with existing memory bank
        existing_mb_path = os.path.join(dest_dir, "memory_bank.npy")
        if os.path.exists(existing_mb_path):
            existing_mb = np.load(existing_mb_path)
            combined_bank = np.vstack([existing_mb, new_raw_patches])
        else:
            combined_bank = new_raw_patches

        total_patches, dim = combined_bank.shape
        target_k = max(1, int(round(total_patches * coreset_ratio)))

        if total_patches > target_k:
            rng = np.random.RandomState(42)
            indices = [int(rng.randint(total_patches))]
            min_dists = np.linalg.norm(combined_bank - combined_bank[indices[0]], axis=1)
            for _ in range(1, target_k):
                next_idx = int(np.argmax(min_dists))
                indices.append(next_idx)
                new_dists = np.linalg.norm(combined_bank - combined_bank[next_idx], axis=1)
                min_dists = np.minimum(min_dists, new_dists)
            coreset_bank = combined_bank[indices].astype(np.float32)
        else:
            coreset_bank = combined_bank.astype(np.float32)

        # Build FAISS Index
        index = faiss.IndexFlatL2(dim)
        index.add(coreset_bank)

        mb_file = os.path.join(dest_dir, "memory_bank.npy")
        faiss_file = os.path.join(dest_dir, "index.faiss")
        np.save(mb_file, coreset_bank)
        faiss.write_index(index, faiss_file)

        # Calibrate on held-out samples
        from src.patchcore import PatchCoreModel
        temp_model = PatchCoreModel()
        temp_model.memory_bank = coreset_bank
        temp_model.grid_size = grid_size
        temp_model.index = index

        cal_scores = []
        for s in cal_samples:
            img = s["img_bgr"]
            if "relative_bbox" in roi_config:
                rx, ry, rw, rh = roi_config["relative_bbox"]
                h_img, w_img = img.shape[:2]
                cx1 = int(rx * w_img)
                cy1 = int(ry * h_img)
                cx2 = min(w_img, cx1 + int(rw * w_img))
                cy2 = min(h_img, cy1 + int(rh * h_img))
                roi = img[cy1:cy2, cx1:cx2]
            else:
                roi = img

            rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
            resized = cv2.resize(rgb, (PC_IMG_SIZE, PC_IMG_SIZE)).astype(np.float32) / 255.0
            norm = (resized - PC_MEAN) / PC_STD
            tensor = torch.from_numpy(norm).permute(2, 0, 1).unsqueeze(0).float().to(torch_dev)
            with torch.no_grad():
                fused = extractor(tensor)[0].cpu().numpy()
            _, score = temp_model.score(fused)
            cal_scores.append(float(score))

        cal_arr = np.array(cal_scores, dtype=np.float32)
        cal_mean = float(np.mean(cal_arr))
        cal_std = float(np.std(cal_arr)) if len(cal_arr) > 1 else 0.05
        cal_max = float(np.max(cal_arr))

        if len(cal_arr) >= 10:
            calibrated_threshold = float(round(float(np.percentile(cal_arr, 99)) + 0.3 * cal_std, 4))
        else:
            calibrated_threshold = float(round(cal_max + max(0.08, 0.5 * cal_std), 4))

        now_iso = datetime.now(timezone.utc).isoformat()
        current_ver = profile.get("model_config", {}).get("model_version", "v1.0.0-adapted")
        new_ver = current_ver.replace("v1.0.0", "v1.1.0")

        profile.setdefault("threshold_config", {})
        profile["threshold_config"]["calibrated_threshold"] = calibrated_threshold
        profile["threshold_config"]["calibration_sample_count"] = profile["threshold_config"].get("calibration_sample_count", 0) + len(cal_samples)
        profile["threshold_config"]["calibration_date"] = now_iso
        profile["threshold_config"]["metrics"] = {
            "mean": round(cal_mean, 4),
            "std": round(cal_std, 4),
            "max": round(cal_max, 4)
        }
        profile["model_config"]["model_version"] = new_ver
        profile["updated_at"] = now_iso

        cfg_file = os.path.join(dest_dir, "profile.json")
        with open(cfg_file, "w", encoding="utf-8") as f:
            json.dump(_clean_profile_for_disk(profile), f, indent=2)

        # Update manifest
        manifest_file = os.path.join(dest_dir, "manifest.json")
        manifest_data = {}
        if os.path.exists(manifest_file):
            with open(manifest_file, "r", encoding="utf-8") as mf:
                manifest_data = json.load(mf)
        manifest_data["updated_at"] = now_iso
        manifest_data["model_version"] = new_ver
        manifest_data["calibrated_threshold"] = calibrated_threshold
        manifest_data["training_samples_count"] = manifest_data.get("training_samples_count", 0) + len(train_samples)
        manifest_data["calibration_samples_count"] = manifest_data.get("calibration_samples_count", 0) + len(cal_samples)
        manifest_data["coreset_vectors_count"] = int(coreset_bank.shape[0])
        manifest_data["artifacts"] = {
            "memory_bank.npy": {"sha256": compute_file_sha256(mb_file), "size_bytes": os.path.getsize(mb_file)},
            "index.faiss": {"sha256": compute_file_sha256(faiss_file), "size_bytes": os.path.getsize(faiss_file)},
            "profile.json": {"sha256": compute_file_sha256(cfg_file), "size_bytes": os.path.getsize(cfg_file)}
        }
        with open(manifest_file, "w", encoding="utf-8") as mf:
            json.dump(manifest_data, mf, indent=2)

        # Invalidate cached model so it reloads fresh
        if profile_id in self.loaded_models:
            del self.loaded_models[profile_id]
        self.reload_profiles()

        return {
            "status": "success",
            "profile_id": profile_id,
            "new_samples_added": len(valid_samples),
            "total_coreset_vectors": int(coreset_bank.shape[0]),
            "new_calibrated_threshold": calibrated_threshold,
            "version": new_ver,
            "updated_at": now_iso
        }


def compute_file_sha256(filepath: str) -> str:
    """Computes SHA-256 checksum for a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()
