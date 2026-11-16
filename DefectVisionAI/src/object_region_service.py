"""
DefectVision AI — Optical Region of Interest (ROI) Service
Detects foreground object boundaries, applies center-weighted framing,
and segments continuous texture surfaces vs discrete manufactured objects.
"""

import cv2
import numpy as np

class ObjectRegionService:
    def __init__(self, min_area_ratio=0.05, max_area_ratio=0.95, margin_ratio=0.10, **kwargs):
        self.min_area_ratio = min_area_ratio
        self.max_area_ratio = max_area_ratio
        self.margin_ratio = margin_ratio

    def extract_roi(self, frame_bgr, category_type="object", target_size=224):
        """
        Extracts salient inspection region.
        - Textures: returns centered full-field surface patch.
        - Objects: detects object contours, crops bounding box with margin, or uses central optical ROI.
        """
        if frame_bgr is None:
            return None, None

        h, w = frame_bgr.shape[:2]

        if category_type == "texture":
            # Continuous texture surface: use high-resolution central optical window
            crop_size = min(h, w)
            y1 = (h - crop_size) // 2
            x1 = (w - crop_size) // 2
            roi = frame_bgr[y1:y1 + crop_size, x1:x1 + crop_size]
            bbox = (x1, y1, crop_size, crop_size)
            return roi, bbox

        # Discrete object: foreground contour detection
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (7, 7), 0)

        # Otsu thresholding for foreground separation
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Invert if object is darker than background
        border_mean = (thresh[0, :].mean() + thresh[-1, :].mean() + thresh[:, 0].mean() + thresh[:, -1].mean()) / 4.0
        if border_mean > 127:
            thresh = cv2.bitwise_not(thresh)

        # Morphological closing
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
        closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        frame_area = float(h * w)
        valid_boxes = []

        for cnt in contours:
            area = cv2.contourArea(cnt)
            ratio = area / frame_area
            if self.min_area_ratio <= ratio <= self.max_area_ratio:
                x, y, bw, bh = cv2.boundingRect(cnt)
                valid_boxes.append((area, (x, y, bw, bh)))

        if valid_boxes:
            # Pick largest salient contour
            valid_boxes.sort(key=lambda item: item[0], reverse=True)
            _, (x, y, bw, bh) = valid_boxes[0]

            # Add 12% margin around object
            margin_x = int(bw * 0.12)
            margin_y = int(bh * 0.12)
            x1 = max(0, x - margin_x)
            y1 = max(0, y - margin_y)
            x2 = min(w, x + bw + margin_x)
            y2 = min(h, y + bh + margin_y)

            roi = frame_bgr[y1:y2, x1:x2]
            bbox = (x1, y1, x2 - x1, y2 - y1)
            return roi, bbox

        # Fallback: standard 65% optical center ROI
        roi_w = int(w * 0.65)
        roi_h = int(h * 0.65)
        x1 = (w - roi_w) // 2
        y1 = (h - roi_h) // 2
        roi = frame_bgr[y1:y1 + roi_h, x1:x1 + roi_w]
        bbox = (x1, y1, roi_w, roi_h)
        return roi, bbox
