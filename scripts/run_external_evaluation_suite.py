"""
External Evaluation Suite & Failure Diagnostic Engine
Runs live inference on external images via FastAPI endpoint (http://127.0.0.1:8001/api/inspect-frame),
records full telemetry, saves heatmaps, diagnoses failure modes (Stages A-J),
and generates comprehensive results CSV and JSON files.
"""

import os
import io
import json
import base64
import time
import urllib.request
import urllib.error
import numpy as np
import pandas as pd
import cv2

API_URL = "http://127.0.0.1:8001/api/inspect-frame"

def post_image_to_api(file_path, category_param):
    # Load and optionally cap extreme dimensions to prevent event loop starvation
    cv_img = cv2.imread(file_path)
    if cv_img is None:
        return {"error": "Failed to read image from disk"}
        
    h, w = cv_img.shape[:2]
    max_dim = 1400
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        new_w, new_h = int(w * scale), int(h * scale)
        cv_img = cv2.resize(cv_img, (new_w, new_h), interpolation=cv2.INTER_AREA)
        
    _, buf = cv2.imencode(".jpg", cv_img, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
    img_bytes = buf.tobytes()
    
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    body = io.BytesIO()
    body.write(f"--{boundary}\r\nContent-Disposition: form-data; name=\"category\"\r\n\r\n{category_param}\r\n".encode("utf-8"))
    filename = os.path.basename(file_path)
    body.write(f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{filename}\"\r\nContent-Type: image/jpeg\r\n\r\n".encode("utf-8"))
    body.write(img_bytes)
    body.write(f"\r\n--{boundary}--\r\n".encode("utf-8"))
    
    req = urllib.request.Request(
        API_URL, 
        data=body.getvalue(), 
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode())

def classify_failure_stage(row, auto_res, target_res):
    """
    Classifies prediction failures into Stages A through J:
    A. Wrong category recognition
    B. Correct category but wrong PatchCore model selected
    C. Correct model but incorrect preprocessing
    D. Incorrect anomaly score
    E. Incorrect threshold decision
    F. Defect not localized by the heatmap
    G. Image-quality gate incorrectly rejects an acceptable image
    H. Category-consistency gate incorrectly rejects a valid image
    I. Image is too different from the training distribution (Domain Shift)
    J. Backend or frontend integration failure
    """
    expected_cond = row["expected_condition"]
    gt_cat = row["category"]
    sim_group = row["similarity_group"]
    
    # Check for API integration error
    if "error" in target_res or target_res.get("rejection_stage") == "api_error":
        return "J_integration_failure", "API connection or response decoding error"
        
    # Check for Quality Gate Rejection
    if target_res.get("rejection_stage") == "quality_gate":
        if row["laplacian_sharpness_variance"] >= 50.0 and 20.0 <= row["mean_luminance"] <= 235.0:
            return "G_quality_gate_incorrect_rejection", f"Acceptable image falsely rejected by quality gate: {target_res.get('rejection_reason')}"
        else:
            return "G_quality_gate_legitimate_rejection", f"Image correctly filtered by quality gate: {target_res.get('rejection_reason')}"

    # Check Category Recognition
    detected_cat = auto_res.get("detected_category", "unknown")
    if detected_cat != gt_cat:
        if sim_group == "different_visual_domain":
            return "A_wrong_category_domain_shift", f"Category misclassified as '{detected_cat}' due to environmental domain shift"
        else:
            return "A_wrong_category_recognition", f"Category misclassified as '{detected_cat}' (expected '{gt_cat}')"
            
    # Check Anomaly Prediction
    score = float(target_res.get("anomaly_score", 0.0))
    thresh = float(target_res.get("calibrated_threshold", target_res.get("anomaly_threshold", 1.50)))
    raw_verdict = target_res.get("verdict", "UNKNOWN")
    
    predicted_cond = "DEFECTIVE" if (raw_verdict in ["DEFECTIVE", "FAIL", "ANOMALOUS"] or score >= thresh) else "NORMAL"
    
    if expected_cond == "NORMAL" and predicted_cond == "DEFECTIVE":
        if sim_group == "different_visual_domain":
            return "I_domain_shift_false_alarm", f"Normal object scored {score:.2f} > thresh {thresh:.2f} due to background/lighting domain shift"
        elif score < thresh * 1.15:
            return "E_threshold_decision_boundary", f"Normal object slightly crossed threshold ({score:.2f} vs {thresh:.2f}); calibration margin needed"
        else:
            return "D_anomaly_score_elevation", f"Normal object patch distance elevated ({score:.2f} vs {thresh:.2f})"
            
    if expected_cond == "DEFECTIVE" and predicted_cond == "NORMAL":
        if row.get("defect_type") == "colour_variation":
            return "C_preprocessing_or_backbone_blindspot", "Pure photometric/color defect invisible to spatial ResNet-18 features"
        else:
            return "D_missed_defect_low_score", f"Defect failed to elevate anomaly score ({score:.2f} <= thresh {thresh:.2f})"
            
    return "NONE_CORRECT", "Prediction matches expected ground truth"

def main():
    base_dir = "external_validation"
    sim_path = os.path.join(base_dir, "metadata", "external_similarity_results.csv")
    meta_path = os.path.join(base_dir, "metadata", "external_image_metadata.csv")
    results_dir = os.path.join(base_dir, "results")
    heatmaps_dir = os.path.join(base_dir, "heatmaps")
    os.makedirs(results_dir, exist_ok=True)
    os.makedirs(heatmaps_dir, exist_ok=True)
    
    if not os.path.exists(sim_path):
        raise FileNotFoundError(f"Missing {sim_path}")
        
    df_sim = pd.read_csv(sim_path)
    df_meta = pd.read_csv(meta_path)
    print(f"Loaded {len(df_sim)} stratified images for live external evaluation.")
    
    predictions = []
    failed_cases = []
    inference_errors = []
    latencies = []
    
    t_start_suite = time.perf_counter()
    
    for idx, row in df_sim.iterrows():
        img_id = row["image_id"]
        cat = row["category"]
        expected_cond = row["expected_condition"]
        sim_group = row["similarity_group"]
        val_status = row["manual_validation_status"]
        
        # Locate image file
        rel_path = df_meta[df_meta["image_id"] == img_id]["relative_path"].iloc[0]
        abs_path = os.path.join(base_dir, rel_path)
        
        print(f"[{idx+1}/{len(df_sim)}] Evaluating {img_id} ({cat} | {expected_cond} | {sim_group})...")
        
        # 1. Unconstrained Category Recognition Call (category="auto")
        auto_res = {}
        try:
            auto_res = post_image_to_api(abs_path, category_param="auto")
        except Exception as e:
            auto_res = {"error": str(e), "detected_category": "api_error"}
            
        detected_cat_auto = auto_res.get("detected_category", "unknown")
        cat_conf_auto = float(auto_res.get("category_confidence", 0.0))
        cat_status_auto = auto_res.get("category_status", auto_res.get("recognition_status", "UNKNOWN"))
        is_cat_correct = bool(detected_cat_auto == cat)
        
        # 2. Target Category PatchCore Anomaly Inspection Call (category=cat)
        target_res = {}
        t0 = time.perf_counter()
        try:
            target_res = post_image_to_api(abs_path, category_param=cat)
            t_call_ms = (time.perf_counter() - t0) * 1000.0
        except Exception as e:
            target_res = {"error": str(e), "verdict": "ERROR", "rejection_stage": "api_error"}
            t_call_ms = (time.perf_counter() - t0) * 1000.0
            inference_errors.append({
                "image_id": img_id, "category": cat, "error_stage": "target_inference",
                "error_message": str(e), "latency_ms": round(t_call_ms, 2)
            })

        raw_verdict = target_res.get("verdict", "UNKNOWN")
        score = target_res.get("anomaly_score")
        score = float(score) if score is not None else 0.0
        
        threshold = target_res.get("calibrated_threshold")
        if threshold is None:
            threshold = target_res.get("anomaly_threshold", 1.50)
        threshold = float(threshold)
        
        rejection_stage = target_res.get("rejection_stage")
        rejection_reason = target_res.get("rejection_reason")
        quality_status = target_res.get("image_quality_status", "UNKNOWN")
        latency_ms = float(target_res.get("processing_time_ms", target_res.get("inference_latency_ms", t_call_ms)))
        
        # Predicted Label Resolution
        if raw_verdict in ["NORMAL", "PASS", "ACCEPT"]:
            predicted_cond = "NORMAL"
        elif raw_verdict in ["DEFECTIVE", "FAIL", "ANOMALOUS"]:
            predicted_cond = "DEFECTIVE"
        elif rejection_stage == "quality_gate":
            predicted_cond = "QUALITY_REJECTED"
        else:
            predicted_cond = "DEFECTIVE" if score >= threshold and threshold > 0 else "NORMAL"
            
        is_pred_correct = bool(predicted_cond == expected_cond)
        
        # Save Heatmap
        hm_rel_path = ""
        heatmap_b64 = target_res.get("heatmap_base64", "")
        if heatmap_b64:
            cat_hm_dir = os.path.join(heatmaps_dir, cat)
            os.makedirs(cat_hm_dir, exist_ok=True)
            hm_filename = f"{img_id}_heatmap.png"
            hm_path = os.path.join(cat_hm_dir, hm_filename)
            try:
                with open(hm_path, "wb") as f_hm:
                    f_hm.write(base64.b64decode(heatmap_b64))
                hm_rel_path = os.path.relpath(hm_path, base_dir).replace("\\", "/")
            except Exception as e_hm:
                print(f"Error saving heatmap {img_id}: {e_hm}")
                
        # Failure classification
        fail_code, fail_diag = classify_failure_stage(row, auto_res, target_res)
        
        rec = {
            "image_id": img_id,
            "category": cat,
            "category_type": row["category_type"],
            "expected_condition": expected_cond,
            "defect_type": row["defect_type"],
            "similarity_group": sim_group,
            "manual_validation_status": val_status,
            "detected_category_auto": detected_cat_auto,
            "category_confidence_auto": round(cat_conf_auto, 4),
            "is_category_correct": is_cat_correct,
            "target_patchcore_model": f"PatchCore-{cat}",
            "anomaly_score": round(score, 4),
            "calibrated_threshold": round(threshold, 4),
            "margin_to_threshold": round(score - threshold, 4),
            "raw_verdict": raw_verdict,
            "predicted_condition": predicted_cond,
            "is_prediction_correct": is_pred_correct,
            "heatmap_generated": bool(len(hm_rel_path) > 0),
            "relative_heatmap_path": hm_rel_path,
            "latency_ms": round(latency_ms, 2),
            "quality_gate_status": quality_status,
            "rejection_stage": str(rejection_stage) if rejection_stage else "none",
            "rejection_reason": str(rejection_reason) if rejection_reason else "none",
            "failure_category": fail_code,
            "failure_diagnosis": fail_diag
        }
        predictions.append(rec)
        latencies.append({"category": cat, "latency_ms": latency_ms})
        
        if not is_pred_correct or not is_cat_correct or fail_code != "NONE_CORRECT":
            failed_cases.append(rec)

    total_time = time.perf_counter() - t_start_suite
    print(f"\nEvaluated 150 images in {total_time:.2f}s ({total_time/150*1000:.1f}ms/img).")
    
    # 1. Export predictions.csv & predictions.json
    df_preds = pd.DataFrame(predictions)
    preds_csv = os.path.join(results_dir, "predictions.csv")
    df_preds.to_csv(preds_csv, index=False)
    print(f"Wrote {preds_csv}")
    
    preds_json = os.path.join(results_dir, "predictions.json")
    with open(preds_json, "w", encoding="utf-8") as f_pj:
        json.dump(predictions, f_pj, indent=2)
    print(f"Wrote {preds_json}")
    
    # 2. Export failure_analysis.csv
    df_fails = pd.DataFrame(failed_cases)
    fails_csv = os.path.join(results_dir, "failure_analysis.csv")
    df_fails.to_csv(fails_csv, index=False)
    print(f"Wrote {fails_csv} ({len(df_fails)} failure records)")
    
    # 3. Export inference_errors.csv
    df_errs = pd.DataFrame(inference_errors)
    errs_csv = os.path.join(results_dir, "inference_errors.csv")
    df_errs.to_csv(errs_csv, index=False)
    print(f"Wrote {errs_csv} ({len(df_errs)} API errors)")

    # 4. Export threshold_audit.csv
    thresh_records = []
    for cat in df_preds["category"].unique():
        sub = df_preds[df_preds["category"] == cat]
        t = sub["calibrated_threshold"].iloc[0]
        norm_scores = sub[sub["expected_condition"] == "NORMAL"]["anomaly_score"].values
        def_scores = sub[sub["expected_condition"] == "DEFECTIVE"]["anomaly_score"].values
        
        thresh_records.append({
            "category": cat,
            "calibrated_threshold": t,
            "min_normal_score": round(float(np.min(norm_scores)), 4) if len(norm_scores) else None,
            "mean_normal_score": round(float(np.mean(norm_scores)), 4) if len(norm_scores) else None,
            "max_normal_score": round(float(np.max(norm_scores)), 4) if len(norm_scores) else None,
            "min_defective_score": round(float(np.min(def_scores)), 4) if len(def_scores) else None,
            "mean_defective_score": round(float(np.mean(def_scores)), 4) if len(def_scores) else None,
            "max_defective_score": round(float(np.max(def_scores)), 4) if len(def_scores) else None,
            "separation_margin": round(float(np.mean(def_scores) - np.mean(norm_scores)), 4) if len(def_scores) and len(norm_scores) else None
        })
    df_thresh = pd.DataFrame(thresh_records)
    thresh_csv = os.path.join(results_dir, "threshold_audit.csv")
    df_thresh.to_csv(thresh_csv, index=False)
    print(f"Wrote {thresh_csv}")

    # 5. Export category_metrics.csv
    # Calculate for Approved images and All images separately
    cat_metrics = []
    for cat in sorted(df_preds["category"].unique()):
        sub_all = df_preds[df_preds["category"] == cat]
        sub_appr = df_preds[(df_preds["category"] == cat) & (df_preds["manual_validation_status"].str.startswith("APPROVED"))]
        
        for name, sub in [("ALL_IMAGES", sub_all), ("APPROVED_ONLY", sub_appr)]:
            if len(sub) == 0:
                continue
            tot = len(sub)
            n_norm = len(sub[sub["expected_condition"] == "NORMAL"])
            n_def = len(sub[sub["expected_condition"] == "DEFECTIVE"])
            
            cat_acc = float(sub["is_category_correct"].sum() / tot * 100.0)
            tp = int(((sub["expected_condition"] == "DEFECTIVE") & (sub["predicted_condition"] == "DEFECTIVE")).sum())
            fn = int(((sub["expected_condition"] == "DEFECTIVE") & (sub["predicted_condition"] != "DEFECTIVE")).sum())
            fp = int(((sub["expected_condition"] == "NORMAL") & (sub["predicted_condition"] == "DEFECTIVE")).sum())
            tn = int(((sub["expected_condition"] == "NORMAL") & (sub["predicted_condition"] == "NORMAL")).sum())
            rej = int(sub["predicted_condition"].str.contains("REJECT").sum())
            
            rec = float(tp / (tp + fn) * 100.0) if (tp + fn) > 0 else 0.0
            fpr = float(fp / (fp + tn) * 100.0) if (fp + tn) > 0 else 0.0
            prec = float(tp / (tp + fp) * 100.0) if (tp + fp) > 0 else 0.0
            f1 = float(2 * prec * rec / (prec + rec) / 100.0) if (prec + rec) > 0 else 0.0
            
            cat_metrics.append({
                "category": cat,
                "subset": name,
                "total_images": tot,
                "normal_images": n_norm,
                "defective_images": n_def,
                "category_recognition_accuracy_pct": round(cat_acc, 2),
                "true_positives": tp,
                "false_positives": fp,
                "true_negatives": tn,
                "false_negatives": fn,
                "quality_rejections": rej,
                "defect_recall_pct": round(rec, 2),
                "false_positive_rate_pct": round(fpr, 2),
                "precision_pct": round(prec, 2),
                "f1_score": round(f1, 4),
                "median_latency_ms": round(float(sub["latency_ms"].median()), 2)
            })

    df_cat_metrics = pd.DataFrame(cat_metrics)
    cat_met_csv = os.path.join(results_dir, "category_metrics.csv")
    df_cat_metrics.to_csv(cat_met_csv, index=False)
    print(f"Wrote {cat_met_csv}")

    # 6. Export confusion_matrix.csv
    conf_rows = []
    for sub_name in ["ALL_IMAGES", "APPROVED_ONLY"]:
        sub = df_preds if sub_name == "ALL_IMAGES" else df_preds[df_preds["manual_validation_status"].str.startswith("APPROVED")]
        tp = int(((sub["expected_condition"] == "DEFECTIVE") & (sub["predicted_condition"] == "DEFECTIVE")).sum())
        fn = int(((sub["expected_condition"] == "DEFECTIVE") & (sub["predicted_condition"] != "DEFECTIVE")).sum())
        fp = int(((sub["expected_condition"] == "NORMAL") & (sub["predicted_condition"] == "DEFECTIVE")).sum())
        tn = int(((sub["expected_condition"] == "NORMAL") & (sub["predicted_condition"] == "NORMAL")).sum())
        rej = int(sub["predicted_condition"].str.contains("REJECT").sum())
        conf_rows.append({
            "subset": sub_name, "TP": tp, "FP": fp, "TN": tn, "FN": fn, "REJECTED": rej,
            "Recall": round(tp/(tp+fn)*100, 2) if (tp+fn) else 0,
            "FPR": round(fp/(fp+tn)*100, 2) if (fp+tn) else 0,
            "Precision": round(tp/(tp+fp)*100, 2) if (tp+fp) else 0,
            "F1": round(2*tp/(2*tp+fp+fn), 4) if (2*tp+fp+fn) else 0
        })
    df_conf = pd.DataFrame(conf_rows)
    conf_csv = os.path.join(results_dir, "confusion_matrix.csv")
    df_conf.to_csv(conf_csv, index=False)
    print(f"Wrote {conf_csv}")

    # 7. Export latency_results.csv
    df_lat = pd.DataFrame(latencies)
    lat_summary = df_lat.groupby("category")["latency_ms"].agg(["count", "min", "median", "mean", "max"]).reset_index()
    lat_csv = os.path.join(results_dir, "latency_results.csv")
    lat_summary.to_csv(lat_csv, index=False)
    print(f"Wrote {lat_csv}")

    print("\n=== External Evaluation Complete ===")

if __name__ == "__main__":
    main()
