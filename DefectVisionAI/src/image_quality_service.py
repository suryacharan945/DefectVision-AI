"""
DefectVision AI — Optical Image Quality Validation Service
Inspects live camera frames for blur, low light, overexposure, low contrast,
and framing stability before anomaly inference. Prevents false alarms on corrupted frames.
"""

import cv2
import numpy as np

class ImageQualityService:
    def __init__(self, blur_threshold=4.0, min_brightness=20.0, max_brightness=245.0, min_contrast=8.0, **kwargs):
        self.blur_threshold = kwargs.get("min_sharpness", blur_threshold)
        self.min_brightness = kwargs.get("min_luminance", min_brightness)
        self.max_brightness = kwargs.get("max_luminance", max_brightness)
        self.min_contrast = kwargs.get("min_contrast", min_contrast)

    def validate_frame(self, frame_bgr):
        """
        Validates frame quality metrics with background-aware optical isolation.
        Distinguishes white/bright lightbox background from genuine product specular glare.
        Returns: (is_valid: bool, status: str, metrics: dict)
        """
        if frame_bgr is None or frame_bgr.size == 0:
            return False, "EMPTY_FRAME", {"error": "Empty or unreadable image frame"}

        # 1. Convert to grayscale for optical telemetry
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        total_pixels = h * w

        # Overall frame metrics
        mean_brightness = float(gray.mean())
        full_frame_overexposed_ratio = float((gray >= 250).sum() / total_pixels)

        # Immediate illumination rejections if entire frame is dark or blown out
        if mean_brightness < self.min_brightness:
            metrics = {
                "resolution": f"{w}x{h}",
                "sharpness": 0.0,
                "sharpness_threshold": self.blur_threshold,
                "brightness": round(mean_brightness, 2),
                "brightness_range": [self.min_brightness, self.max_brightness],
                "contrast": round(float(gray.std()), 2),
                "contrast_threshold": self.min_contrast,
                "overexposed_ratio": round(full_frame_overexposed_ratio, 4),
                "full_frame_overexposed_ratio": round(full_frame_overexposed_ratio, 4)
            }
            return False, "REJECT_INSUFFICIENT_ILLUMINATION", metrics

        if mean_brightness > self.max_brightness or full_frame_overexposed_ratio >= 0.95:
            metrics = {
                "resolution": f"{w}x{h}",
                "sharpness": 0.0,
                "sharpness_threshold": self.blur_threshold,
                "brightness": round(mean_brightness, 2),
                "brightness_range": [self.min_brightness, self.max_brightness],
                "contrast": round(float(gray.std()), 2),
                "contrast_threshold": self.min_contrast,
                "overexposed_ratio": round(full_frame_overexposed_ratio, 4),
                "full_frame_overexposed_ratio": round(full_frame_overexposed_ratio, 4)
            }
            return False, "REJECT_OVEREXPOSED_OR_GLARE", metrics

        # 2. Border sampling for background detection
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

        fg_mask = None
        segmentation_status = "FULL_FRAME"

        if is_uniform_bg:
            edges = cv2.Canny(gray, 20, 80)
            pts = np.argwhere(edges > 0)
            if len(pts) >= 40:
                pts_xy = np.column_stack((pts[:, 1], pts[:, 0]))
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

        if is_uniform_bg and fg_coverage_pct < 5.0:
            metrics = {
                "resolution": f"{w}x{h}",
                "segmentation_status": segmentation_status,
                "foreground_coverage_pct": round(fg_coverage_pct, 2),
                "border_mean": round(border_mean, 2),
                "border_std": round(border_std, 2)
            }
            return False, "REJECT_INSUFFICIENT_FOREGROUND", metrics

        # 3. Compute optical metrics on segmented foreground
        fg_gray = gray[fg_mask]
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        fg_laplacian = laplacian[fg_mask]

        sharpness_score = float(np.var(fg_laplacian))
        mean_brightness = float(fg_gray.mean())
        contrast_score = float(fg_gray.std())

        fg_clipped_count = int((fg_gray >= 250).sum())
        overexposed_ratio = float(fg_clipped_count / fg_pixel_count)

        full_frame_overexposed_ratio = float((gray >= 250).sum() / total_pixels)

        is_blurred = sharpness_score < self.blur_threshold
        is_too_dark = mean_brightness < self.min_brightness
        is_too_bright = mean_brightness > self.max_brightness

        metrics = {
            "resolution": f"{w}x{h}",
            "segmentation_status": segmentation_status,
            "foreground_coverage_pct": round(fg_coverage_pct, 2),
            "sharpness": round(sharpness_score, 2),
            "sharpness_threshold": self.blur_threshold,
            "brightness": round(mean_brightness, 2),
            "brightness_range": [self.min_brightness, self.max_brightness],
            "contrast": round(contrast_score, 2),
            "contrast_threshold": self.min_contrast,
            "overexposed_ratio": round(overexposed_ratio, 4),
            "full_frame_overexposed_ratio": round(full_frame_overexposed_ratio, 4)
        }

        # Priority checks
        if is_too_dark:
            return False, "REJECT_INSUFFICIENT_ILLUMINATION", metrics
        if is_too_bright or overexposed_ratio > 0.40:
            return False, "REJECT_OVEREXPOSED_OR_GLARE", metrics
        if is_blurred:
            return False, "REJECT_MOTION_OR_OPTICAL_BLUR", metrics
        if contrast_score < self.min_contrast:
            return False, "REJECT_LOW_CONTRAST", metrics

        return True, "OPTICAL_QUALITY_VERIFIED", metrics
