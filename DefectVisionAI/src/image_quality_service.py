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
        Validates frame quality metrics.
        Returns: (is_valid: bool, status: str, metrics: dict)
        """
        if frame_bgr is None or frame_bgr.size == 0:
            return False, "EMPTY_FRAME", {"error": "Empty or unreadable image frame"}

        # 1. Convert to grayscale for optical telemetry
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape

        # 2. Blur / Sharpness via Laplacian Variance: Var(Laplacian(I))
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sharpness_score = float(laplacian.var())
        is_blurred = sharpness_score < self.blur_threshold

        # 3. Brightness: Mean pixel luminance
        mean_brightness = float(gray.mean())
        is_too_dark = mean_brightness < self.min_brightness
        is_too_bright = mean_brightness > self.max_brightness

        # 4. Contrast: Standard deviation of pixel luminance
        contrast_score = float(gray.std())
        is_low_contrast = contrast_score < self.min_contrast

        # 5. Overexposed pixel ratio (specular highlights)
        overexposed_ratio = float((gray >= 250).sum() / gray.size)

        metrics = {
            "resolution": f"{w}x{h}",
            "sharpness": round(sharpness_score, 2),
            "sharpness_threshold": self.blur_threshold,
            "brightness": round(mean_brightness, 2),
            "brightness_range": [self.min_brightness, self.max_brightness],
            "contrast": round(contrast_score, 2),
            "contrast_threshold": self.min_contrast,
            "overexposed_ratio": round(overexposed_ratio, 4)
        }

        # Priority checks
        if is_too_dark:
            return False, "REJECT_INSUFFICIENT_ILLUMINATION", metrics
        if is_too_bright or overexposed_ratio > 0.40:
            return False, "REJECT_OVEREXPOSED_OR_GLARE", metrics
        if is_blurred:
            return False, "REJECT_MOTION_OR_OPTICAL_BLUR", metrics
        if is_low_contrast:
            return False, "REJECT_LOW_CONTRAST", metrics

        return True, "OPTICAL_QUALITY_VERIFIED", metrics
