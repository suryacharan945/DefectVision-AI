"""
DefectVision AI — Real-Time Optical Camera Inspection Engine
Coordinates live optical inspection pipeline:
Quality Gate -> ROI Extraction -> Category Recognition -> Model Routing ->
PatchCore Anomaly Localization -> Decision Fusion -> Structured Telemetry.
"""

import os
import sys
import time
import uuid
import base64
import cv2
import numpy as np
import torch

from src.image_quality_service import ImageQualityService
from src.object_region_service import ObjectRegionService
from src.category_classifier import CategoryRecognitionService
from src.category_model_registry import CategoryModelRegistry
from src.decision_fusion_service import DecisionFusionService
from src.inspection_history_service import InspectionHistoryService
from src.patchcore import PatchCoreExtractor, PatchCoreModel, normalize_map, overlay_heatmap, calibrate_score_map
from src.severity import normalize_anomaly_score, compute_severity_score, bucket_severity

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
PATCHCORE_DIR = os.path.join(MODELS_DIR, "patchcore")
CAT_CLASSIFIER_PATH = os.path.join(MODELS_DIR, "category_classifier", "category_classifier.pth")
CAT_META_PATH = os.path.join(MODELS_DIR, "category_classifier", "category_metadata.json")

PC_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
PC_STD  = np.array([0.229, 0.224, 0.225], dtype=np.float32)
PC_IMG_SIZE = 224
GRID_SIZE = 28

CONCLUSION_MAP = {
    "NORMAL": "NO DEFECT DETECTED",
    "DEFECTIVE": "POSSIBLE DEFECT DETECTED",
    "REVIEW REQUIRED": "MANUAL INSPECTION REQUIRED",
    "UNSUPPORTED": "UNSUPPORTED OR UNKNOWN CATEGORY",
}

DISCLAIMER = "The result reflects the model's learned visual patterns and does not guarantee the absence of all possible defects."

def generate_diagnosis_text(verdict, category, raw_score, threshold, defect_area_pct, severity_level, review_reason):
    if verdict == "NORMAL":
        return (
            f"Automated optical inspection of the {category} component identified no significant "
            f"visual anomalies. The peak anomaly score ({raw_score:.4f}) is strictly below the calibrated "
            f"decision threshold ({threshold:.4f}). {DISCLAIMER}"
        )
    elif verdict == "DEFECTIVE":
        return (
            f"Possible defect detected on the {category} component. Anomalous surface region spans "
            f"{defect_area_pct:.2f}% with peak anomaly score ({raw_score:.4f}) exceeding calibrated "
            f"threshold ({threshold:.4f}) at {severity_level} severity. {DISCLAIMER}"
        )
    elif verdict == "REVIEW REQUIRED":
        return (
            f"Manual inspection required for {category} component. Reason: {review_reason}. {DISCLAIMER}"
        )
    elif verdict == "UNSUPPORTED":
        return (
            f"Unsupported or unknown object category detected. Object does not match any of the 15 "
            f"supported MVTec AD profiles. Safe inspection cannot be performed without model support. {DISCLAIMER}"
        )
    return f"Inspection completed with verdict: {verdict}. {DISCLAIMER}"

class OpticalInspectionEngine:
    def __init__(self, device=None, confidence_threshold=0.70):
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = torch.device(device)

        # Initialize sub-services
        self.quality_service = ImageQualityService()
        self.roi_service = ObjectRegionService()
        self.registry = CategoryModelRegistry(models_dir=MODELS_DIR)
        self.fusion_service = DecisionFusionService(borderline_margin=0.02)
        self.history_service = InspectionHistoryService()

        # Category Recognition Service
        self.category_service = CategoryRecognitionService(
            model_path=CAT_CLASSIFIER_PATH if os.path.exists(CAT_CLASSIFIER_PATH) else None,
            meta_path=CAT_META_PATH if os.path.exists(CAT_META_PATH) else None,
            device=device,
            confidence_threshold=confidence_threshold
        )

        # Feature Extractor for PatchCore
        print("Initializing Resident PatchCore Extractor...", flush=True)
        self.extractor = PatchCoreExtractor(grid_size=GRID_SIZE).to(self.device)
        self.extractor.eval()

        # Resident PatchCore Model Cache
        self.loaded_patchcore_models = {}

    def get_patchcore_model(self, category):
        if category not in self.loaded_patchcore_models:
            mb_path = os.path.join(PATCHCORE_DIR, category, "memory_bank.npy")
            if not os.path.exists(mb_path):
                return None
            m = PatchCoreModel()
            m.load(mb_path, grid_size=GRID_SIZE)
            self.loaded_patchcore_models[category] = m
        return self.loaded_patchcore_models[category]

    def inspect_frame(self, image_bgr, operator_category_override=None, multi_frame_candidates=None, mode="live"):
        """
        Executes end-to-end category-aware optical inspection pipeline on single frame.
        mode: "live" (camera stream) or "upload" (image upload).
        """
        t_start = time.perf_counter()
        insp_id = f"insp_{int(time.time()*1000)}_{uuid.uuid4().hex[:6]}"

        if image_bgr is None or image_bgr.size == 0:
            verdict = "REVIEW REQUIRED"
            conclusion = CONCLUSION_MAP[verdict]
            review_reason = "Failed to decode input frame."
            diagnosis = f"Manual inspection required. The provided image payload was empty or corrupted. {DISCLAIMER}"
            record = {
                "inspection_id": insp_id,
                "mode": mode,
                "category": "unknown",
                "detected_category": "unknown",
                "category_type": "unknown",
                "category_confidence": 0.0,
                "category_status": "EMPTY_OR_UNREADABLE_FRAME",
                "recognition_status": "EMPTY_OR_UNREADABLE_FRAME",
                "image_quality": {"status": "INVALID_IMAGE", "metrics": {}},
                "image_quality_status": "INVALID_IMAGE",
                "image_quality_metrics": {},
                "model_id": "None",
                "model_selected": "None",
                "model_version": "v1.0.0",
                "anomaly_score": 0.0,
                "anomaly_threshold": 0.0,
                "calibrated_threshold": 0.0,
                "optimal_threshold": 0.0,
                "verdict": verdict,
                "conclusion": conclusion,
                "heatmap_url": "",
                "heatmap_base64": "",
                "heatmap": "",
                "annotated_image_url": "",
                "original_image": "",
                "raw_heatmap": "",
                "inference_latency_ms": 0.0,
                "processing_time_ms": 0.0,
                "review_reason": review_reason,
                "diagnosis": diagnosis,
                "defect_type": "error",
                "severity_level": "review",
                "severity_score": 0.0,
                "defect_area_pct": 0.0,
                "confidence_pct": 0.0,
                "predicted_label": "review",
            }
            return record

        h, w = image_bgr.shape[:2]

        # ----------------------------------------------------
        # Stage 1: Optical Image Quality Validation
        # ----------------------------------------------------
        is_quality_valid, quality_status, quality_metrics = self.quality_service.validate_frame(image_bgr)
        if not is_quality_valid:
            # Produce early return without running expensive deep networks
            _, buf_orig = cv2.imencode(".jpg", image_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
            orig_b64 = "data:image/jpeg;base64," + base64.b64encode(buf_orig).decode("utf-8")
            elapsed = float(round((time.perf_counter() - t_start) * 1000, 2))

            verdict = "REVIEW REQUIRED"
            conclusion = CONCLUSION_MAP[verdict]
            review_reason = f"Optical quality failure: {quality_status}"
            diagnosis = (
                f"Manual inspection required. The specimen image failed the optical quality gate "
                f"due to {quality_status.lower().replace('_', ' ')}. Please ensure adequate illumination "
                f"and verify camera focus before re-evaluating. {DISCLAIMER}"
            )

            record = {
                "inspection_id": insp_id,
                "mode": mode,
                "category": "unknown",
                "detected_category": "unknown",
                "category_type": "unknown",
                "category_confidence": 0.0,
                "category_status": "SKIPPED_QUALITY_FAILURE",
                "recognition_status": "SKIPPED_QUALITY_FAILURE",
                "image_quality": {"status": quality_status, "metrics": quality_metrics},
                "image_quality_status": quality_status,
                "image_quality_metrics": quality_metrics,
                "model_id": "None",
                "model_selected": "None",
                "model_version": "v1.0.0",
                "anomaly_score": 0.0,
                "anomaly_threshold": 0.0,
                "calibrated_threshold": 0.0,
                "optimal_threshold": 0.0,
                "verdict": verdict,
                "conclusion": conclusion,
                "original_image": orig_b64,
                "heatmap_url": orig_b64,
                "heatmap_base64": orig_b64,
                "heatmap": orig_b64,
                "annotated_image_url": orig_b64,
                "raw_heatmap": orig_b64,
                "inference_latency_ms": elapsed,
                "processing_time_ms": elapsed,
                "review_reason": review_reason,
                "diagnosis": diagnosis,
                "defect_type": "quality_failure",
                "severity_level": "review",
                "severity_score": 0.0,
                "defect_area_pct": 0.0,
                "confidence_pct": 0.0,
                "predicted_label": "review",
            }
            return self.history_service.add_inspection(record)

        # ----------------------------------------------------
        # Stage 2: Automatic Category Recognition
        # ----------------------------------------------------
        if operator_category_override and operator_category_override != "auto" and operator_category_override in self.registry.get_all_categories():
            category_result = {
                "category": operator_category_override,
                "candidate_category": operator_category_override,
                "category_type": self.registry.get_category_config(operator_category_override)["category_type"],
                "confidence": 1.0,
                "is_supported": True,
                "status": "OPERATOR_OVERRIDE",
                "normalized_entropy": 0.0
            }
        else:
            category_result = self.category_service.predict(image_bgr)

        detected_category = category_result["category"]
        candidate_category = category_result.get("candidate_category", "unknown")
        category_conf = float(category_result.get("confidence", 0.0))
        is_supported = category_result.get("is_supported", False)

        # If unsupported or unrecognized category
        if not is_supported or detected_category == "unknown":
            _, buf_orig = cv2.imencode(".jpg", image_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
            orig_b64 = "data:image/jpeg;base64," + base64.b64encode(buf_orig).decode("utf-8")
            elapsed = float(round((time.perf_counter() - t_start) * 1000, 2))

            verdict = "UNSUPPORTED"
            conclusion = CONCLUSION_MAP[verdict]
            review_reason = f"Input object does not belong to the 15 supported categories (Top candidate: '{candidate_category}' at {category_conf:.1%})"
            diagnosis = (
                f"Unsupported or unknown object category detected. The presented item does not match "
                f"any of the 15 supported MVTec AD industrial profiles (confidence: {category_conf:.1%}). "
                f"Automatic inspection cannot be safely completed without category support. {DISCLAIMER}"
            )

            record = {
                "inspection_id": insp_id,
                "mode": mode,
                "category": "unsupported",
                "detected_category": "unsupported",
                "candidate_category": candidate_category,
                "category_type": category_result.get("category_type", "unknown"),
                "category_confidence": round(category_conf, 4),
                "category_status": category_result.get("status", "UNSUPPORTED"),
                "recognition_status": category_result.get("status", "UNSUPPORTED"),
                "image_quality": {"status": quality_status, "metrics": quality_metrics},
                "image_quality_status": quality_status,
                "image_quality_metrics": quality_metrics,
                "model_id": "None",
                "model_selected": "None",
                "model_version": "v1.0.0",
                "anomaly_score": 0.0,
                "anomaly_threshold": 0.0,
                "calibrated_threshold": 0.0,
                "optimal_threshold": 0.0,
                "verdict": verdict,
                "conclusion": conclusion,
                "original_image": orig_b64,
                "heatmap_url": orig_b64,
                "heatmap_base64": orig_b64,
                "heatmap": orig_b64,
                "annotated_image_url": orig_b64,
                "raw_heatmap": orig_b64,
                "inference_latency_ms": elapsed,
                "processing_time_ms": elapsed,
                "review_reason": review_reason,
                "diagnosis": diagnosis,
                "defect_type": "unsupported",
                "severity_level": "unsupported",
                "severity_score": 0.0,
                "defect_area_pct": 0.0,
                "confidence_pct": round(category_conf * 100, 1),
                "predicted_label": "unsupported",
            }
            return self.history_service.add_inspection(record)

        # ----------------------------------------------------
        # Stage 3: Region of Interest (ROI) Extraction
        # ----------------------------------------------------
        cat_type = category_result.get("category_type", "object")
        roi_img, bbox = self.roi_service.extract_roi(image_bgr, category_type=cat_type)
        if roi_img is None:
            roi_img = image_bgr

        # ----------------------------------------------------
        # Stage 4: Category-Specific PatchCore Anomaly Inference
        # ----------------------------------------------------
        cat_cfg = self.registry.get_category_config(detected_category)
        calibrated_thresh = cat_cfg["calibrated_threshold"] if cat_cfg else 1.7452

        patchcore_model = self.get_patchcore_model(detected_category)
        if patchcore_model is None:
            elapsed = float(round((time.perf_counter() - t_start) * 1000, 2))
            verdict = "REVIEW REQUIRED"
            conclusion = CONCLUSION_MAP[verdict]
            review_reason = f"PatchCore memory bank not loaded for category '{detected_category}'"
            diagnosis = f"Manual inspection required. {review_reason}. {DISCLAIMER}"
            record = {
                "inspection_id": insp_id,
                "mode": mode,
                "category": detected_category,
                "detected_category": detected_category,
                "category_type": cat_type,
                "category_confidence": round(category_conf, 4),
                "category_status": category_result.get("status", "RECOGNIZED"),
                "recognition_status": category_result.get("status", "RECOGNIZED"),
                "image_quality": {"status": quality_status, "metrics": quality_metrics},
                "image_quality_status": quality_status,
                "image_quality_metrics": quality_metrics,
                "model_id": f"PatchCore-{detected_category.capitalize()}-MemoryBank",
                "model_selected": f"PatchCore-{detected_category.capitalize()}-MemoryBank",
                "model_version": cat_cfg.get("model_version", "v1.0.0") if cat_cfg else "v1.0.0",
                "anomaly_score": 0.0,
                "anomaly_threshold": float(round(calibrated_thresh, 4)),
                "calibrated_threshold": float(round(calibrated_thresh, 4)),
                "optimal_threshold": float(round(calibrated_thresh, 4)),
                "verdict": verdict,
                "conclusion": conclusion,
                "review_reason": review_reason,
                "diagnosis": diagnosis,
                "inference_latency_ms": elapsed,
                "processing_time_ms": elapsed,
                "predicted_label": "review",
            }
            return self.history_service.add_inspection(record)

        # Preprocess ROI for PatchCore
        img_rgb = cv2.cvtColor(roi_img, cv2.COLOR_BGR2RGB)
        img_pc = cv2.resize(img_rgb, (PC_IMG_SIZE, PC_IMG_SIZE)).astype(np.float32) / 255.0
        img_pc = (img_pc - PC_MEAN) / PC_STD
        pc_tensor = torch.from_numpy(img_pc).permute(2, 0, 1).unsqueeze(0).float().to(self.device)

        with torch.no_grad():
            fused_emb = self.extractor(pc_tensor)[0].cpu().numpy()

        dist_map, raw_score = patchcore_model.score(fused_emb)

        import scipy.ndimage
        smooth_dist_map = cv2.resize(dist_map, (PC_IMG_SIZE, PC_IMG_SIZE), interpolation=cv2.INTER_CUBIC)
        smooth_dist_map = scipy.ndimage.gaussian_filter(smooth_dist_map, sigma=4.0)

        # Defect area is percentage of surface where distance meets or exceeds calibrated threshold
        anomalous_pixels = float((smooth_dist_map >= calibrated_thresh).sum())
        defect_area_pct = float(100.0 * anomalous_pixels / smooth_dist_map.size)

        baseline_mean = cat_cfg.get("baseline_mean", 1.25)
        baseline_p99 = cat_cfg.get("baseline_p99", 1.65)
        anomaly_norm = float(normalize_anomaly_score(raw_score, baseline_mean, baseline_p99))

        # ----------------------------------------------------
        # Stage 5: Decision Fusion Logic
        # ----------------------------------------------------
        verdict, severity_level, review_reason, fusion_telemetry = self.fusion_service.evaluate_inspection(
            quality_is_valid=is_quality_valid,
            quality_status=quality_status,
            category_result=category_result,
            anomaly_score=raw_score,
            calibrated_threshold=calibrated_thresh
        )

        is_defective = bool(verdict == "DEFECTIVE")
        if verdict == "NORMAL":
            defect_area_pct = 0.0
            sev_score = 0.0
            severity_level = "normal"
            defect_type = "normal"
        elif verdict == "DEFECTIVE":
            sev_score = float(round(compute_severity_score(anomaly_norm, defect_area_pct, verdict=verdict), 2))
            defect_type = "surface_anomaly"
        elif verdict == "REVIEW REQUIRED":
            sev_score = float(round(compute_severity_score(anomaly_norm, defect_area_pct, verdict=verdict), 2))
            defect_type = "review_required"
        else:
            sev_score = 0.0
            defect_type = "unsupported"

        # ----------------------------------------------------
        # Stage 6: Defect Heatmap Overlays
        # ----------------------------------------------------
        dist_map_norm = calibrate_score_map(dist_map, threshold=calibrated_thresh, baseline_mean=baseline_mean)
        roi_overlay = overlay_heatmap(img_rgb, dist_map_norm, alpha=0.45, is_defective=is_defective)
        roi_overlay_bgr = cv2.cvtColor(roi_overlay, cv2.COLOR_RGB2BGR)

        # Composite onto original frame
        full_overlay = image_bgr.copy()
        if bbox is not None:
            bx, by, bw, bh = bbox
            resized_roi_hm = cv2.resize(roi_overlay_bgr, (bw, bh))
            full_overlay[by:by+bh, bx:bx+bw] = resized_roi_hm
            # Status bounding box: Green for NORMAL, Red for DEFECTIVE, Amber for REVIEW
            box_color = (0, 200, 0) if verdict == "NORMAL" else ((0, 0, 220) if verdict == "DEFECTIVE" else (0, 180, 240))
            cv2.rectangle(full_overlay, (bx, by), (bx+bw, by+bh), box_color, 2)
        else:
            full_overlay = cv2.resize(roi_overlay_bgr, (w, h))

        # Raw color map
        if is_defective:
            hm_raw = cv2.resize(dist_map_norm, (w, h))
            hm_raw = cv2.applyColorMap(np.uint8(255 * hm_raw), cv2.COLORMAP_JET)
        else:
            hm_raw = image_bgr.copy()

        # Base64 encodings
        _, buf_overlay = cv2.imencode(".jpg", full_overlay, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
        heatmap_b64 = "data:image/jpeg;base64," + base64.b64encode(buf_overlay).decode("utf-8")

        _, buf_orig = cv2.imencode(".jpg", image_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
        orig_b64 = "data:image/jpeg;base64," + base64.b64encode(buf_orig).decode("utf-8")

        _, buf_raw_hm = cv2.imencode(".jpg", hm_raw, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
        raw_hm_b64 = "data:image/jpeg;base64," + base64.b64encode(buf_raw_hm).decode("utf-8")

        elapsed_ms = float(round((time.perf_counter() - t_start) * 1000, 2))
        conclusion = CONCLUSION_MAP.get(verdict, "INSPECTION COMPLETE")

        diagnosis = generate_diagnosis_text(
            verdict=verdict,
            category=detected_category,
            raw_score=raw_score,
            threshold=calibrated_thresh,
            defect_area_pct=defect_area_pct,
            severity_level=severity_level,
            review_reason=review_reason
        )

        # Build comprehensive inspection record
        record = {
            "inspection_id": insp_id,
            "mode": mode,
            "category": detected_category,
            "detected_category": detected_category,
            "category_type": cat_type,
            "category_confidence": round(category_conf, 4),
            "category_status": category_result.get("status", "RECOGNIZED"),
            "recognition_status": category_result.get("status", "RECOGNIZED"),
            "model_id": f"PatchCore-{detected_category.capitalize()}-MemoryBank",
            "model_selected": f"PatchCore-{detected_category.capitalize()}-MemoryBank",
            "model_version": cat_cfg.get("model_version", "v1.0.0"),
            "image_quality": {"status": quality_status, "metrics": quality_metrics},
            "image_quality_status": quality_status,
            "image_quality_metrics": quality_metrics,
            "severity_level": severity_level,
            "severity_score": sev_score,
            "anomaly_score": float(round(raw_score, 4)),
            "anomaly_threshold": float(round(calibrated_thresh, 4)),
            "calibrated_threshold": float(round(calibrated_thresh, 4)),
            "optimal_threshold": float(round(calibrated_thresh, 4)),
            "anomaly_norm": float(round(anomaly_norm, 2)),
            "defect_area_pct": float(round(defect_area_pct, 2)),
            "confidence_pct": float(round(category_conf * 100, 1)),
            "verdict": verdict,
            "conclusion": conclusion,
            "predicted_label": verdict.lower().replace(" ", "_"),
            "defect_type": defect_type,
            "review_reason": review_reason if review_reason else None,
            "diagnosis": diagnosis,
            "roi_bbox": list(bbox) if bbox else None,
            "original_image": orig_b64,
            "heatmap_url": heatmap_b64,
            "heatmap_base64": heatmap_b64,
            "heatmap": heatmap_b64,
            "annotated_image_url": heatmap_b64,
            "raw_heatmap": raw_hm_b64,
            "inference_latency_ms": elapsed_ms,
            "processing_time_ms": elapsed_ms
        }

        return self.history_service.add_inspection(record)
