"""
External Domain Validation & Inference Evaluation Engine
Evaluates DefectVision AI (v1.0.0-rc1) on 150 authentic internet images
across all 15 industrial product and surface categories.
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

API_URL = "http://127.0.0.1:8001/api/inspect-frame"

def multipart_post(url, fields, file_path):
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    body = io.BytesIO()
    for k, v in fields.items():
        body.write(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode("utf-8"))
    
    filename = os.path.basename(file_path)
    ext = os.path.splitext(filename)[1].lower()
    content_type = "image/png" if ext == ".png" else "image/jpeg"
    body.write(f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{filename}\"\r\nContent-Type: {content_type}\r\n\r\n".encode("utf-8"))
    
    with open(file_path, "rb") as f:
        body.write(f.read())
    body.write(f"\r\n--{boundary}--\r\n".encode("utf-8"))
    
    req = urllib.request.Request(url, data=body.getvalue(), headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())

def main():
    base_dir = "external_validation"
    meta_path = os.path.join(base_dir, "collection_metadata.csv")
    results_dir = os.path.join(base_dir, "results")
    heatmaps_dir = os.path.join(base_dir, "heatmaps")
    os.makedirs(results_dir, exist_ok=True)
    os.makedirs(heatmaps_dir, exist_ok=True)
    
    if not os.path.exists(meta_path):
        raise FileNotFoundError(f"Missing {meta_path}. Please run image collection first.")
        
    df_meta = pd.read_csv(meta_path)
    print(f"Loaded {len(df_meta)} images from {meta_path} for external evaluation.")
    
    records = []
    latencies = []
    
    for idx, row in df_meta.iterrows():
        img_id = row["image_id"]
        cat = row["category"]
        expected_cond = row["expected_condition"].upper()
        rel_path = row["relative_path"]
        abs_path = os.path.join(base_dir, os.path.basename(os.path.dirname(os.path.dirname(rel_path))), os.path.basename(os.path.dirname(rel_path)), os.path.basename(rel_path))
        
        # Verify file existence
        if not os.path.exists(abs_path):
            abs_path = os.path.join(base_dir, rel_path)
        if not os.path.exists(abs_path):
            print(f"File not found: {abs_path}")
            continue
            
        print(f"[{idx+1}/{len(df_meta)}] Evaluating {img_id} ({cat} | {expected_cond})...")
        
        # 1. Automatic category recognition query
        auto_res = {}
        try:
            auto_res = multipart_post(API_URL, {"category": "auto"}, abs_path)
            detected_cat_auto = auto_res.get("detected_category", "unknown")
            cat_conf_auto = auto_res.get("category_confidence", 0.0)
            recog_status_auto = auto_res.get("recognition_status", auto_res.get("category_status", "UNKNOWN"))
        except Exception as e:
            detected_cat_auto = "error"
            cat_conf_auto = 0.0
            recog_status_auto = str(e)
            
        # 2. Designated target-category PatchCore anomaly inspection query
        target_res = {}
        try:
            t0 = time.perf_counter()
            target_res = multipart_post(API_URL, {"category": cat}, abs_path)
            t_elapsed = (time.perf_counter() - t0) * 1000.0
            
            raw_verdict = target_res.get("verdict", "UNKNOWN")
            anomaly_score = target_res.get("anomaly_score")
            if anomaly_score is None:
                anomaly_score = 0.0
            else:
                anomaly_score = float(anomaly_score)
                
            threshold = target_res.get("calibrated_threshold")
            if threshold is None:
                threshold = target_res.get("anomaly_threshold", 0.0)
            threshold = float(threshold)
            
            latency_ms = target_res.get("processing_time_ms", target_res.get("inference_latency_ms", t_elapsed))
            rejection_stage = target_res.get("rejection_stage")
            rejection_reason = target_res.get("rejection_reason")
            quality_status = target_res.get("image_quality_status", "UNKNOWN")
            heatmap_b64 = target_res.get("heatmap_base64", "")
            
        except Exception as e:
            raw_verdict = "ERROR"
            anomaly_score = 0.0
            threshold = 0.0
            latency_ms = 0.0
            rejection_stage = "api_error"
            rejection_reason = str(e)
            quality_status = "ERROR"
            heatmap_b64 = ""

        # Normalize predicted condition
        # Verdicts: 'NORMAL'/'PASS' -> NORMAL, 'DEFECTIVE'/'FAIL' -> DEFECTIVE, 'REVIEW REQUIRED'/'UNSUPPORTED' -> REJECTED
        if raw_verdict in ["NORMAL", "PASS", "ACCEPT"]:
            predicted_cond = "NORMAL"
        elif raw_verdict in ["DEFECTIVE", "FAIL", "ANOMALOUS"]:
            predicted_cond = "DEFECTIVE"
        elif rejection_stage == "quality_gate":
            predicted_cond = "QUALITY_REJECTED"
        else:
            # Check by score vs threshold if available
            if threshold > 0 and anomaly_score > 0:
                predicted_cond = "DEFECTIVE" if anomaly_score > threshold else "NORMAL"
            else:
                predicted_cond = "REJECTED_OR_UNKNOWN"

        # Correctness evaluation
        is_category_correct = (detected_cat_auto == cat)
        is_anomaly_correct = (predicted_cond == expected_cond)
        
        # Determine failure category
        failure_mode = "none"
        if predicted_cond in ["QUALITY_REJECTED", "REJECTED_OR_UNKNOWN"]:
            failure_mode = f"rejection_{rejection_stage or 'unknown'}"
        elif expected_cond == "NORMAL" and predicted_cond == "DEFECTIVE":
            failure_mode = "false_positive_domain_shift"
        elif expected_cond == "DEFECTIVE" and predicted_cond == "NORMAL":
            failure_mode = "false_negative_missed_defect"
            
        # Save heatmap if present
        heatmap_rel_path = ""
        if heatmap_b64:
            cat_hm_dir = os.path.join(heatmaps_dir, cat)
            os.makedirs(cat_hm_dir, exist_ok=True)
            hm_filename = f"{img_id}_heatmap.png"
            hm_abs_path = os.path.join(cat_hm_dir, hm_filename)
            try:
                with open(hm_abs_path, "wb") as f_hm:
                    f_hm.write(base64.b64decode(heatmap_b64))
                heatmap_rel_path = os.path.relpath(hm_abs_path, base_dir).replace("\\", "/")
            except Exception as e_hm:
                print(f"Error saving heatmap for {img_id}: {e_hm}")

        rec = {
            "image_id": img_id,
            "category": cat,
            "expected_condition": expected_cond,
            "defect_type": row.get("defect_type", "none"),
            "detected_category_auto": detected_cat_auto,
            "category_confidence_auto": round(cat_conf_auto, 4),
            "is_category_correct": is_category_correct,
            "predicted_condition": predicted_cond,
            "is_anomaly_correct": is_anomaly_correct,
            "raw_verdict": raw_verdict,
            "anomaly_score": round(anomaly_score, 4),
            "calibrated_threshold": round(threshold, 4),
            "margin_to_threshold": round(anomaly_score - threshold, 4),
            "inference_latency_ms": round(latency_ms, 2),
            "quality_status": quality_status,
            "rejection_stage": str(rejection_stage) if rejection_stage else "none",
            "rejection_reason": str(rejection_reason) if rejection_reason else "none",
            "failure_mode": failure_mode,
            "relative_image_path": rel_path,
            "relative_heatmap_path": heatmap_rel_path,
            "source_page_url": row.get("source_page_url", ""),
            "original_image_url": row.get("original_image_url", ""),
            "license": row.get("license", "")
        }
        records.append(rec)
        latencies.append({"category": cat, "latency_ms": latency_ms})

    df_preds = pd.DataFrame(records)
    preds_csv = os.path.join(results_dir, "predictions.csv")
    df_preds.to_csv(preds_csv, index=False)
    print(f"\nWrote predictions CSV: {preds_csv} ({len(df_preds)} rows)")

    preds_json = os.path.join(results_dir, "predictions.json")
    with open(preds_json, "w", encoding="utf-8") as f_pj:
        json.dump(records, f_pj, indent=2)
    print(f"Wrote predictions JSON: {preds_json}")

    # Failed images CSV (false alarms, missed defects, rejections, misrouted)
    df_failed = df_preds[~df_preds["is_anomaly_correct"] | ~df_preds["is_category_correct"]]
    failed_csv = os.path.join(results_dir, "failed_images.csv")
    df_failed.to_csv(failed_csv, index=False)
    print(f"Wrote failed images CSV: {failed_csv} ({len(df_failed)} rows)")

    # Category-wise metrics calculation
    cat_metrics = []
    confusion_records = []
    
    for cat in df_preds["category"].unique():
        sub = df_preds[df_preds["category"] == cat]
        total = len(sub)
        n_norm = len(sub[sub["expected_condition"] == "NORMAL"])
        n_def = len(sub[sub["expected_condition"] == "DEFECTIVE"])
        
        # Category recognition
        cat_correct = len(sub[sub["is_category_correct"]])
        cat_acc = (cat_correct / total * 100.0) if total > 0 else 0.0
        
        # Binary confusion matrix (excluding rejected from pure TP/FP or counting them explicitly)
        tp = len(sub[(sub["expected_condition"] == "DEFECTIVE") & (sub["predicted_condition"] == "DEFECTIVE")])
        fn = len(sub[(sub["expected_condition"] == "DEFECTIVE") & (sub["predicted_condition"] != "DEFECTIVE")])
        fp = len(sub[(sub["expected_condition"] == "NORMAL") & (sub["predicted_condition"] == "DEFECTIVE")])
        tn = len(sub[(sub["expected_condition"] == "NORMAL") & (sub["predicted_condition"] == "NORMAL")])
        rej = len(sub[sub["predicted_condition"].isin(["QUALITY_REJECTED", "REJECTED_OR_UNKNOWN"])])
        
        recall = (tp / (tp + fn) * 100.0) if (tp + fn) > 0 else 0.0
        fpr = (fp / (fp + tn) * 100.0) if (fp + tn) > 0 else 0.0
        precision = (tp / (tp + fp) * 100.0) if (tp + fp) > 0 else 0.0
        f1 = (2 * precision * recall / (precision + recall)) / 100.0 if (precision + recall) > 0 else 0.0
        
        med_lat = sub["inference_latency_ms"].median()
        
        cat_metrics.append({
            "category": cat,
            "total_images": total,
            "normal_images": n_norm,
            "defective_images": n_def,
            "category_recognition_rate_pct": round(cat_acc, 2),
            "normal_predicted_normal_tn": tn,
            "normal_predicted_defective_fp": fp,
            "defective_detected_tp": tp,
            "defective_missed_fn": fn,
            "rejected_or_unsupported": rej,
            "defect_recall_pct": round(recall, 2),
            "false_positive_rate_pct": round(fpr, 2),
            "precision_pct": round(precision, 2),
            "f1_score": round(f1, 4),
            "median_latency_ms": round(med_lat, 2)
        })
        
        confusion_records.append({
            "category": cat,
            "TP": tp, "FP": fp, "TN": tn, "FN": fn, "REJECTED": rej
        })

    df_cat = pd.DataFrame(cat_metrics)
    cat_csv = os.path.join(results_dir, "category_metrics.csv")
    df_cat.to_csv(cat_csv, index=False)
    print(f"Wrote category metrics CSV: {cat_csv}")

    df_conf = pd.DataFrame(confusion_records)
    conf_csv = os.path.join(results_dir, "confusion_matrix.csv")
    df_conf.to_csv(conf_csv, index=False)
    print(f"Wrote confusion matrix CSV: {conf_csv}")

    # Latency summary
    df_lat = pd.DataFrame(latencies)
    lat_summary = df_lat.groupby("category")["latency_ms"].agg(["count", "min", "median", "mean", "max"]).reset_index()
    lat_csv = os.path.join(results_dir, "latency_results.csv")
    lat_summary.to_csv(lat_csv, index=False)
    print(f"Wrote latency results CSV: {lat_csv}")

    print("\n=== External Evaluation Inference Complete ===")

if __name__ == "__main__":
    main()
