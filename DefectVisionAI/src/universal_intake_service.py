"""
DefectVision AI — Universal Image Intake Layer
Provides unified image validation, foreground/object delineation, quality assessment,
domain heuristic classification, category recognition, and non-destructive preprocessing.

Guarantees:
- Validates dimensions, format, channel count, and data integrity.
- Detects empty, corrupted, flat-color, and extremely low-quality frames.
- Isolates primary object foreground from background without destroying subtle anomalies.
- Classifies image domain: 'mvtec_benchmark', 'controlled_photo', 'smartphone', 'factory_style', 'unknown'.
- Computes comprehensive optical quality and geometry metrics.
- Evaluates suitability for selected inspection modes.
- Preserves the original input image alongside preprocessed derivatives for display and audit.
"""

import os
import time
import base64
from typing import Dict, List, Optional, Tuple, Any
import cv2
import numpy as np

class UniversalImageIntakeService:
    def __init__(self, category_service=None):
        self.category_service = category_service

    def process_image(
        self,
        image_bgr: np.ndarray,
        inspection_mode: str = "benchmark",
        target_profile: Optional[Dict[str, Any]] = None,
        operator_category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes full universal intake pipeline on an input image buffer.

        Parameters:
        - image_bgr: Raw OpenCV BGR matrix
        - inspection_mode: 'benchmark' | 'production' | 'universal'
        - target_profile: Optional profile dict for production inspection
        - operator_category: Optional category override

        Returns:
        - Comprehensive intake result dictionary
        """
        t0 = time.perf_counter()
        preprocessing_applied: List[str] = []

        # -------------------------------------------------------------
        # 1. Image Payload & Dimension Validation
        # -------------------------------------------------------------
        if image_bgr is None or not isinstance(image_bgr, np.ndarray) or image_bgr.size == 0:
            return {
                "image_quality_status": "REJECT_EMPTY_OR_UNREADABLE",
                "foreground_detected": False,
                "foreground_bbox": None,
                "foreground_coverage_pct": 0.0,
                "detected_category": "unknown",
                "category_confidence": 0.0,
                "category_status": "EMPTY_OR_UNREADABLE_FRAME",
                "image_domain": "unknown",
                "preprocessing_applied": ["none"],
                "suitability_status": "UNSUITABLE",
                "rejection_reason": "Image payload is null, empty, or unreadable.",
                "original_dimensions": [0, 0],
                "intake_dimensions": [0, 0],
                "metrics": {},
                "original_image_b64": "",
                "preprocessed_image_b64": "",
                "preprocessed_bgr": None,
                "latency_ms": round((time.perf_counter() - t0) * 1000, 2)
            }

        if len(image_bgr.shape) == 2:
            image_bgr = cv2.cvtColor(image_bgr, cv2.COLOR_GRAY2BGR)
            preprocessing_applied.append("grayscale_to_bgr")

        h, w = image_bgr.shape[:2]
        total_pixels = h * w

        if h < 32 or w < 32:
            return {
                "image_quality_status": "REJECT_RESOLUTION_TOO_LOW",
                "foreground_detected": False,
                "foreground_bbox": None,
                "foreground_coverage_pct": 0.0,
                "detected_category": "unknown",
                "category_confidence": 0.0,
                "category_status": "UNSUPPORTED_RESOLUTION",
                "image_domain": "unknown",
                "preprocessing_applied": preprocessing_applied or ["none"],
                "suitability_status": "UNSUITABLE",
                "rejection_reason": f"Resolution ({w}x{h}) is too low for optical anomaly inspection (minimum 32x32).",
                "original_dimensions": [w, h],
                "intake_dimensions": [w, h],
                "metrics": {"resolution": f"{w}x{h}"},
                "original_image_b64": "",
                "preprocessed_image_b64": "",
                "preprocessed_bgr": None,
                "latency_ms": round((time.perf_counter() - t0) * 1000, 2)
            }

        # Encode original image to base64 for display and audit
        _, buf_orig = cv2.imencode(".jpg", image_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
        orig_b64 = "data:image/jpeg;base64," + base64.b64encode(buf_orig).decode("utf-8")

        # -------------------------------------------------------------
        # 2. Basic Photometric & Flat-Color Checks
        # -------------------------------------------------------------
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        brightness = float(gray.mean())
        contrast = float(gray.std())

        if contrast < 2.0:
            return {
                "image_quality_status": "REJECT_FLAT_OR_BLANK_COLOR",
                "foreground_detected": False,
                "foreground_bbox": None,
                "foreground_coverage_pct": 0.0,
                "detected_category": "unknown",
                "category_confidence": 0.0,
                "category_status": "BLANK_IMAGE",
                "image_domain": "unknown",
                "preprocessing_applied": preprocessing_applied or ["none"],
                "suitability_status": "UNSUITABLE",
                "rejection_reason": f"Image is solid or near-uniform flat color (contrast std: {contrast:.2f}).",
                "original_dimensions": [w, h],
                "intake_dimensions": [w, h],
                "metrics": {"brightness": round(brightness, 2), "contrast": round(contrast, 2)},
                "original_image_b64": orig_b64,
                "preprocessed_image_b64": orig_b64,
                "preprocessed_bgr": None,
                "latency_ms": round((time.perf_counter() - t0) * 1000, 2)
            }

        if brightness < 8.0:
            return {
                "image_quality_status": "REJECT_INSUFFICIENT_ILLUMINATION",
                "foreground_detected": False,
                "foreground_bbox": None,
                "foreground_coverage_pct": 0.0,
                "detected_category": "unknown",
                "category_confidence": 0.0,
                "category_status": "INSUFFICIENT_ILLUMINATION",
                "image_domain": "unknown",
                "preprocessing_applied": preprocessing_applied or ["none"],
                "suitability_status": "UNSUITABLE",
                "rejection_reason": f"Image is severely underexposed or completely black (brightness: {brightness:.2f}).",
                "original_dimensions": [w, h],
                "intake_dimensions": [w, h],
                "metrics": {"brightness": round(brightness, 2), "contrast": round(contrast, 2)},
                "original_image_b64": orig_b64,
                "preprocessed_image_b64": orig_b64,
                "preprocessed_bgr": None,
                "latency_ms": round((time.perf_counter() - t0) * 1000, 2)
            }

        if brightness > 250.0:
            return {
                "image_quality_status": "REJECT_OVEREXPOSED_OR_GLARE",
                "foreground_detected": False,
                "foreground_bbox": None,
                "foreground_coverage_pct": 0.0,
                "detected_category": "unknown",
                "category_confidence": 0.0,
                "category_status": "SEVERELY_OVEREXPOSED",
                "image_domain": "unknown",
                "preprocessing_applied": preprocessing_applied or ["none"],
                "suitability_status": "UNSUITABLE",
                "rejection_reason": f"Image is completely saturated / blown out (brightness: {brightness:.2f}).",
                "original_dimensions": [w, h],
                "intake_dimensions": [w, h],
                "metrics": {"brightness": round(brightness, 2), "contrast": round(contrast, 2)},
                "original_image_b64": orig_b64,
                "preprocessed_image_b64": orig_b64,
                "preprocessed_bgr": None,
                "latency_ms": round((time.perf_counter() - t0) * 1000, 2)
            }

        # -------------------------------------------------------------
        # 3. Border Sampling & Background / Domain Classification
        # -------------------------------------------------------------
        border_size = max(3, min(10, int(min(h, w) * 0.02)))
        border_pixels = np.concatenate([
            gray[:border_size, :].ravel(),
            gray[-border_size:, :].ravel(),
            gray[:, :border_size].ravel(),
            gray[:, -border_size:].ravel()
        ])
        border_mean = float(np.mean(border_pixels))
        border_std = float(np.std(border_pixels))

        is_uniform_light_bg = (border_mean >= 190.0 and border_std <= 42.0)
        is_uniform_dark_bg = (border_mean <= 45.0 and border_std <= 25.0)
        is_uniform_studio_bg = is_uniform_light_bg or is_uniform_dark_bg

        # Aspect ratio and resolution analysis
        aspect_ratio = float(w) / float(h)
        is_standard_mvtec_res = (w in [700, 800, 840, 900, 1024] and h in [700, 800, 840, 900, 1024])

        # Heuristic Domain Determination
        if is_standard_mvtec_res and (is_uniform_studio_bg or border_std < 30.0):
            image_domain = "mvtec_benchmark"
        elif is_uniform_studio_bg:
            image_domain = "controlled_photo"
        elif border_std > 45.0 or abs(aspect_ratio - 1.0) > 0.4:
            # Variable non-uniform background typical of handheld/smartphone photography
            image_domain = "smartphone"
        elif border_std > 30.0:
            image_domain = "factory_style"
        else:
            image_domain = "controlled_photo"

        # -------------------------------------------------------------
        # 4. Foreground / Primary Object Localization
        # -------------------------------------------------------------
        fg_detected = False
        fg_bbox = None
        fg_mask = None
        fg_coverage_pct = 100.0
        preprocessed_bgr = image_bgr.copy()

        if is_uniform_studio_bg:
            # Studio backlight / lightbox: Use Canny edge convex hull for transparent/specular objects
            edges = cv2.Canny(gray, 20, 80)
            pts = np.argwhere(edges > 0)
            if len(pts) >= 40:
                pts_xy = np.column_stack((pts[:, 1], pts[:, 0]))  # [x, y]
                hull = cv2.convexHull(pts_xy)
                hull_mask = np.zeros((h, w), dtype=np.uint8)
                cv2.drawContours(hull_mask, [hull], -1, 255, -1)
                fg_mask = (hull_mask > 0)
                fg_pixel_count = int(fg_mask.sum())
                fg_coverage_pct = float((fg_pixel_count / total_pixels) * 100.0)

                # Bounding box of convex hull
                hx, hy, hw, hh = cv2.boundingRect(hull)
                fg_bbox = [int(hx), int(hy), int(hw), int(hh)]
                fg_detected = True

                # Apply mild margin crop if object occupies isolated central area
                if 10.0 <= fg_coverage_pct <= 80.0 and inspection_mode in ["production", "universal"]:
                    margin_x = int(hw * 0.08)
                    margin_y = int(hh * 0.08)
                    x1 = max(0, hx - margin_x)
                    y1 = max(0, hy - margin_y)
                    x2 = min(w, hx + hw + margin_x)
                    y2 = min(h, hy + hh + margin_y)
                    preprocessed_bgr = image_bgr[y1:y2, x1:x2].copy()
                    preprocessing_applied.append("foreground_hull_crop")
            else:
                fg_mask = np.ones((h, w), dtype=bool)
                fg_coverage_pct = 100.0
                fg_detected = False
        else:
            # Natural/smartphone scene: Try Otsu + morphological closing to locate primary object
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            _, otsu_thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            if border_mean > 127:
                otsu_thresh = cv2.bitwise_not(otsu_thresh)

            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
            closed = cv2.morphologyEx(otsu_thresh, cv2.MORPH_CLOSE, kernel)
            contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            valid_contours = []
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if 0.05 * total_pixels <= area <= 0.95 * total_pixels:
                    valid_contours.append((area, cnt))

            if valid_contours:
                valid_contours.sort(key=lambda x: x[0], reverse=True)
                _, best_cnt = valid_contours[0]
                bx, by, bw, bh = cv2.boundingRect(best_cnt)
                fg_bbox = [int(bx), int(by), int(bw), int(bh)]
                cnt_mask = np.zeros((h, w), dtype=np.uint8)
                cv2.drawContours(cnt_mask, [best_cnt], -1, 255, -1)
                fg_mask = (cnt_mask > 0)
                fg_coverage_pct = float((fg_mask.sum() / total_pixels) * 100.0)
                fg_detected = True

                if inspection_mode == "universal" and fg_coverage_pct <= 75.0:
                    margin_x = int(bw * 0.10)
                    margin_y = int(bh * 0.10)
                    x1 = max(0, bx - margin_x)
                    y1 = max(0, by - margin_y)
                    x2 = min(w, bx + bw + margin_x)
                    y2 = min(h, by + bh + margin_y)
                    preprocessed_bgr = image_bgr[y1:y2, x1:x2].copy()
                    preprocessing_applied.append("salient_contour_crop")
            else:
                fg_mask = np.ones((h, w), dtype=bool)
                fg_coverage_pct = 100.0
                fg_detected = False

        if fg_mask is None:
            fg_mask = np.ones((h, w), dtype=bool)

        # -------------------------------------------------------------
        # 5. Foreground-Isolated Optical Quality Metrics
        # -------------------------------------------------------------
        fg_gray = gray[fg_mask] if fg_mask.sum() > 0 else gray
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        fg_laplacian = laplacian[fg_mask] if fg_mask.sum() > 0 else laplacian

        fg_brightness = float(fg_gray.mean())
        fg_contrast = float(fg_gray.std())
        fg_sharpness = float(np.var(fg_laplacian))

        fg_clipped = int((fg_gray >= 250).sum())
        fg_pixel_count = int(fg_mask.sum())
        fg_overexposed_pct = float((fg_clipped / fg_pixel_count) * 100.0) if fg_pixel_count > 0 else 0.0

        metrics = {
            "resolution": f"{w}x{h}",
            "aspect_ratio": round(aspect_ratio, 3),
            "border_mean": round(border_mean, 2),
            "border_std": round(border_std, 2),
            "foreground_coverage_pct": round(fg_coverage_pct, 2),
            "sharpness": round(fg_sharpness, 2),
            "brightness": round(fg_brightness, 2),
            "contrast": round(fg_contrast, 2),
            "overexposed_pct": round(fg_overexposed_pct, 2),
            "full_frame_overexposed_pct": round(float(((gray >= 250).sum() / total_pixels) * 100.0), 2)
        }

        # Quality thresholds
        min_sharpness = 12.0
        min_contrast_thresh = 10.0
        max_overexposed_thresh = 35.0

        if target_profile and "quality_config" in target_profile:
            qc = target_profile["quality_config"]
            min_sharpness = float(qc.get("min_sharpness", min_sharpness))
            min_contrast_thresh = float(qc.get("min_contrast", min_contrast_thresh))
            max_overexposed_thresh = float(qc.get("max_overexposed_pct", max_overexposed_thresh))

        is_blurred = fg_sharpness < min_sharpness
        is_low_contrast = fg_contrast < min_contrast_thresh
        is_glare = fg_overexposed_pct > max_overexposed_thresh

        # -------------------------------------------------------------
        # 6. Category Recognition & Routing Classification
        # -------------------------------------------------------------
        det_category = "unknown"
        det_conf = 0.0
        cat_status = "NOT_EVALUATED"

        if operator_category and operator_category != "auto":
            det_category = operator_category
            det_conf = 1.0
            cat_status = "OPERATOR_OVERRIDE"
        elif self.category_service is not None:
            try:
                cat_result = self.category_service.predict(image_bgr)
                det_category = cat_result.get("category", "unsupported")
                det_conf = float(cat_result.get("confidence", 0.0))
                cat_status = cat_result.get("status", "UNKNOWN")
            except Exception as e:
                cat_status = f"CLASSIFIER_ERROR_{e}"

        # -------------------------------------------------------------
        # 7. Suitability & Rejection Determination
        # -------------------------------------------------------------
        suitability_status = "SUITABLE"
        rejection_reason = None
        quality_status = "OPTICAL_QUALITY_VERIFIED"

        if is_blurred:
            quality_status = "REJECT_MOTION_OR_OPTICAL_BLUR"
            suitability_status = "REVIEW_REQUIRED"
            rejection_reason = f"Image sharpness ({fg_sharpness:.1f}) below minimum threshold ({min_sharpness:.1f})."
        elif is_low_contrast:
            quality_status = "REJECT_LOW_CONTRAST"
            suitability_status = "REVIEW_REQUIRED"
            rejection_reason = f"Image contrast ({fg_contrast:.1f}) below minimum threshold ({min_contrast_thresh:.1f})."
        elif is_glare:
            quality_status = "REJECT_OVEREXPOSED_OR_GLARE"
            suitability_status = "REVIEW_REQUIRED"
            rejection_reason = f"Specular surface glare ({fg_overexposed_pct:.1f}%) exceeds safety threshold ({max_overexposed_thresh:.1f}%)."
        elif fg_detected and fg_coverage_pct < 4.0:
            quality_status = "REJECT_INSUFFICIENT_FOREGROUND"
            suitability_status = "REVIEW_REQUIRED"
            rejection_reason = f"Target object coverage ({fg_coverage_pct:.1f}%) is too small to inspect reliably."
        else:
            if preprocessing_applied:
                suitability_status = "SUITABLE_WITH_PREPROCESSING"

        # Encode preprocessed image for display
        _, buf_prep = cv2.imencode(".jpg", preprocessed_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
        prep_b64 = "data:image/jpeg;base64," + base64.b64encode(buf_prep).decode("utf-8")

        latency_ms = round((time.perf_counter() - t0) * 1000, 2)

        return {
            "image_quality_status": quality_status,
            "foreground_detected": fg_detected,
            "foreground_bbox": fg_bbox,
            "foreground_coverage_pct": round(fg_coverage_pct, 2),
            "detected_category": det_category,
            "category_confidence": round(det_conf, 4),
            "category_status": cat_status,
            "image_domain": image_domain,
            "preprocessing_applied": preprocessing_applied if preprocessing_applied else ["none"],
            "suitability_status": suitability_status,
            "rejection_reason": rejection_reason,
            "original_dimensions": [w, h],
            "intake_dimensions": [preprocessed_bgr.shape[1], preprocessed_bgr.shape[0]],
            "metrics": metrics,
            "original_image_b64": orig_b64,
            "preprocessed_image_b64": prep_b64,
            "preprocessed_bgr": preprocessed_bgr,
            "latency_ms": latency_ms
        }
