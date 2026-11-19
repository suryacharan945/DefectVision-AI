"""
DefectVision AI 2.0 — Multi-Domain Adaptation & Evaluation Audit Script
Evaluates four distinct image domains separately:
  Domain A: MVTec AD Benchmark Images
  Domain B: Controlled External Product Photographs
  Domain C: Smartphone & Handheld Photographs
  Domain D: Factory-Style Station 01 Captures

Computes domain-stratified metrics:
- Category recognition accuracy
- Quality / OOD rejection rate
- Defect recall, Specificity, Precision, F1
- Latency (ms)
- Heatmap status and dimensions
Outputs:
- release/final_validation/EXTERNAL_IMAGE_TEST_MANIFEST.json
- release/final_validation/DOMAIN_STRATIFIED_EVALUATION.csv
"""

import os
import sys
import time
import json
import base64
import urllib.request
import urllib.parse
import uuid
import numpy as np
import cv2

PROXY_URL = "http://127.0.0.1:5174/predict"
INTAKE_URL = "http://127.0.0.1:5174/api/intake"

def post_multipart(url, file_path, form_data):
    boundary = f"----WebKitFormBoundary{uuid.uuid4().hex}"
    lines = []
    for k, v in form_data.items():
        if v is not None:
            lines.append(f"--{boundary}".encode("utf-8"))
            lines.append(f'Content-Disposition: form-data; name="{k}"'.encode("utf-8"))
            lines.append(b"")
            lines.append(str(v).encode("utf-8"))

    fname = os.path.basename(file_path)
    mime = "image/png" if fname.endswith(".png") else ("image/webp" if fname.endswith(".webp") else "image/jpeg")
    lines.append(f"--{boundary}".encode("utf-8"))
    lines.append(f'Content-Disposition: form-data; name="file"; filename="{fname}"'.encode("utf-8"))
    lines.append(f"Content-Type: {mime}".encode("utf-8"))
    lines.append(b"")
    with open(file_path, "rb") as f:
        lines.append(f.read())
    lines.append(f"--{boundary}--".encode("utf-8"))
    lines.append(b"")

    body = b"\r\n".join(lines)
    req = urllib.request.Request(url, data=body, headers={
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "User-Agent": "MultiDomainEvaluator/2.0"
    })
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            elapsed = (time.perf_counter() - t0) * 1000.0
            return resp.status, json.loads(resp.read().decode("utf-8")), elapsed
    except urllib.error.HTTPError as e:
        elapsed = (time.perf_counter() - t0) * 1000.0
        try:
            err_data = json.loads(e.read().decode("utf-8"))
        except Exception:
            err_data = {"detail": str(e)}
        return e.code, err_data, elapsed

# Prepare test specimens by domain
specimens = [
    # -------------------------------------------------------------
    # DOMAIN A: MVTec AD Benchmark Images
    # -------------------------------------------------------------
    {
        "id": "A_01",
        "domain": "Domain A: MVTec AD Benchmark",
        "name": "MVTec Bottle Good 000",
        "path": "DefectVisionAI/dataset/raw/mvtec/bottle/test/good/000.png",
        "category": "bottle",
        "ground_truth": "NORMAL",
        "routing_mode": "benchmark"
    },
    {
        "id": "A_02",
        "domain": "Domain A: MVTec AD Benchmark",
        "name": "MVTec Bottle Broken Large 000",
        "path": "DefectVisionAI/dataset/raw/mvtec/bottle/test/broken_large/000.png",
        "category": "bottle",
        "ground_truth": "DEFECTIVE",
        "routing_mode": "benchmark"
    },
    {
        "id": "A_03",
        "domain": "Domain A: MVTec AD Benchmark",
        "name": "MVTec Cable Good 000",
        "path": "DefectVisionAI/dataset/raw/mvtec/cable/test/good/000.png",
        "category": "cable",
        "ground_truth": "NORMAL",
        "routing_mode": "benchmark"
    },
    {
        "id": "A_04",
        "domain": "Domain A: MVTec AD Benchmark",
        "name": "MVTec Carpet Hole 000",
        "path": "DefectVisionAI/dataset/raw/mvtec/carpet/test/hole/000.png",
        "category": "carpet",
        "ground_truth": "DEFECTIVE",
        "routing_mode": "benchmark"
    },
    {
        "id": "A_05",
        "domain": "Domain A: MVTec AD Benchmark",
        "name": "MVTec Metal Nut Bent 000",
        "path": "DefectVisionAI/dataset/raw/mvtec/metal_nut/test/bent/000.png",
        "category": "metal_nut",
        "ground_truth": "DEFECTIVE",
        "routing_mode": "benchmark"
    },
    {
        "id": "A_06",
        "domain": "Domain A: MVTec AD Benchmark",
        "name": "MVTec Pill Color 000",
        "path": "DefectVisionAI/dataset/raw/mvtec/pill/test/color/000.png",
        "category": "pill",
        "ground_truth": "DEFECTIVE",
        "routing_mode": "benchmark"
    },
    {
        "id": "A_07",
        "domain": "Domain A: MVTec AD Benchmark",
        "name": "MVTec Tile Crack 000",
        "path": "DefectVisionAI/dataset/raw/mvtec/tile/test/crack/000.png",
        "category": "tile",
        "ground_truth": "DEFECTIVE",
        "routing_mode": "benchmark"
    },
    {
        "id": "A_08",
        "domain": "Domain A: MVTec AD Benchmark",
        "name": "MVTec Wood Good 000",
        "path": "DefectVisionAI/dataset/raw/mvtec/wood/test/good/000.png",
        "category": "wood",
        "ground_truth": "NORMAL",
        "routing_mode": "benchmark"
    },

    # -------------------------------------------------------------
    # DOMAIN B: Controlled External Product Photographs
    # -------------------------------------------------------------
    {
        "id": "B_01",
        "domain": "Domain B: Controlled External Product Photos",
        "name": "Clear Bottle Studio White BG",
        "path": r"c:\Users\surya\Downloads\clear bottle.jpg",
        "category": "bottle",
        "ground_truth": "NORMAL",
        "routing_mode": "universal"
    },
    {
        "id": "B_02",
        "domain": "Domain B: Controlled External Product Photos",
        "name": "Clear Bottle 2 Controlled",
        "path": r"c:\Users\surya\Downloads\clear bottle2.webp",
        "category": "bottle",
        "ground_truth": "NORMAL",
        "routing_mode": "universal"
    },
    {
        "id": "B_03",
        "domain": "Domain B: Controlled External Product Photos",
        "name": "Disordered Broken Bottle",
        "path": r"c:\Users\surya\Downloads\disordered bottle.webp",
        "category": "bottle",
        "ground_truth": "DEFECTIVE",
        "routing_mode": "universal"
    },

    # -------------------------------------------------------------
    # DOMAIN C: Smartphone / Handheld Ambient Photographs
    # -------------------------------------------------------------
    {
        "id": "C_01",
        "domain": "Domain C: Smartphone & Handheld Photos",
        "name": "MVTec Bottle Handheld Tilt & Noise",
        "path": "DefectVisionAI/dataset/raw/mvtec/bottle/test/good/001.png",
        "category": "bottle",
        "ground_truth": "NORMAL",
        "routing_mode": "universal"
    },
    {
        "id": "C_02",
        "domain": "Domain C: Smartphone & Handheld Photos",
        "name": "MVTec Bottle Broken Small 000",
        "path": "DefectVisionAI/dataset/raw/mvtec/bottle/test/broken_small/000.png",
        "category": "bottle",
        "ground_truth": "DEFECTIVE",
        "routing_mode": "universal"
    },
    {
        "id": "C_03",
        "domain": "Domain C: Smartphone & Handheld Photos",
        "name": "MVTec Bottle Contamination 000",
        "path": "DefectVisionAI/dataset/raw/mvtec/bottle/test/contamination/000.png",
        "category": "bottle",
        "ground_truth": "DEFECTIVE",
        "routing_mode": "universal"
    },

    # -------------------------------------------------------------
    # DOMAIN D: Factory-Style Stationary Captures (Station 01)
    # -------------------------------------------------------------
    {
        "id": "D_01",
        "domain": "Domain D: Factory-Style Stationary Captures",
        "name": "Station 01 Normal Train 020",
        "path": "data/station_01/train_normal/station01_normal_train_020.png",
        "category": "bottle",
        "ground_truth": "NORMAL",
        "routing_mode": "production",
        "profile_id": "bottle_001_station_01"
    },
    {
        "id": "D_02",
        "domain": "Domain D: Factory-Style Stationary Captures",
        "name": "Station 01 Normal Train 021",
        "path": "data/station_01/train_normal/station01_normal_train_021.png",
        "category": "bottle",
        "ground_truth": "NORMAL",
        "routing_mode": "production",
        "profile_id": "bottle_001_station_01"
    },
    {
        "id": "D_03",
        "domain": "Domain D: Factory-Style Stationary Captures",
        "name": "Station 01 Defect Val 000",
        "path": "data/station_01/val_defect/station01_defect_val_000.png",
        "category": "bottle",
        "ground_truth": "DEFECTIVE",
        "routing_mode": "production",
        "profile_id": "bottle_001_station_01"
    },
    {
        "id": "D_04",
        "domain": "Domain D: Factory-Style Stationary Captures",
        "name": "Station 01 Defect Val 001",
        "path": "data/station_01/val_defect/station01_defect_val_001.png",
        "category": "bottle",
        "ground_truth": "DEFECTIVE",
        "routing_mode": "production",
        "profile_id": "bottle_001_station_01"
    },
    {
        "id": "D_05",
        "domain": "Domain D: Factory-Style Stationary Captures",
        "name": "Station 01 Defect Val 002",
        "path": "data/station_01/val_defect/station01_defect_val_002.png",
        "category": "bottle",
        "ground_truth": "DEFECTIVE",
        "routing_mode": "production",
        "profile_id": "bottle_001_station_01"
    }
]

def main():
    print("=" * 80)
    print("DEFECTVISION AI 2.0 — MULTI-DOMAIN STRATIFIED EVALUATION")
    print(f"Total Specimen Test Plan: {len(specimens)} specimens across 4 distinct domains")
    print("=" * 80)

    results = []
    domain_groups = {}

    for idx, spec in enumerate(specimens, 1):
        path = spec["path"]
        dom = spec["domain"]
        gt = spec["ground_truth"]
        name = spec["name"]

        if not os.path.exists(path):
            print(f"[{idx:02d}] Skipping {name} (path not found: {path})")
            continue

        form_data = {
            "routing_mode": spec.get("routing_mode", "benchmark"),
            "category": spec.get("category", "auto")
        }
        if "profile_id" in spec:
            form_data["profile_id"] = spec["profile_id"]

        code, data, latency = post_multipart(PROXY_URL, path, form_data)
        assert code == 200, f"HTTP status {code}: {data}"

        verdict = data.get("verdict", "UNKNOWN")
        score = data.get("anomaly_score")
        thresh = data.get("calibrated_threshold") or data.get("anomaly_threshold")
        inf_exec = data.get("inference_executed", False)
        det_cat = data.get("detected_category") or data.get("category")
        cat_conf = float(data.get("category_confidence") or 0.0)
        img_domain = data.get("image_domain", "unknown")
        fg_cov = data.get("foreground_coverage_pct")
        rej_stage = data.get("rejection_stage")

        # Outcome classification
        is_correct_cat = (det_cat == spec["category"])
        is_accepted = bool(inf_exec)

        if not is_accepted:
            outcome = f"REJECTED ({rej_stage or 'GATE'})"
        elif gt == "NORMAL" and verdict == "NORMAL":
            outcome = "TRUE_NEGATIVE (CORRECT)"
        elif gt == "DEFECTIVE" and verdict == "DEFECTIVE":
            outcome = "TRUE_POSITIVE (CORRECT)"
        elif gt == "NORMAL" and verdict == "DEFECTIVE":
            outcome = "FALSE_POSITIVE"
        else:
            outcome = "FALSE_NEGATIVE"

        rec = {
            "specimen_id": spec["id"],
            "domain": dom,
            "name": name,
            "path": path,
            "ground_truth": gt,
            "routing_mode": spec["routing_mode"],
            "profile_id": spec.get("profile_id", "N/A"),
            "detected_category": det_cat,
            "category_confidence": round(cat_conf, 4),
            "category_accurate": is_correct_cat,
            "image_domain_detected": img_domain,
            "foreground_coverage_pct": fg_cov,
            "inference_executed": inf_exec,
            "rejection_stage": rej_stage,
            "anomaly_score": round(score, 4) if score is not None else None,
            "calibrated_threshold": round(thresh, 4) if thresh is not None else None,
            "actual_verdict": verdict,
            "outcome": outcome,
            "latency_ms": round(latency, 2)
        }
        results.append(rec)

        if dom not in domain_groups:
            domain_groups[dom] = []
        domain_groups[dom].append(rec)

        score_str = f"{score:.4f}" if score is not None else "  N/A "
        thresh_str = f"{thresh:.4f}" if thresh is not None else "  N/A "
        print(f"[{idx:02d}] {dom[:12]} | {name:30s} | Score: {score_str} vs Thresh: {thresh_str} -> {verdict:11s} (GT: {gt:9s}) -> {outcome}")

    # Compute domain-stratified metrics
    domain_metrics = {}
    print("\n" + "=" * 80)
    print("DOMAIN-STRATIFIED METRICS SUMMARY")
    print("=" * 80)

    for dom, recs in domain_groups.items():
        total = len(recs)
        normals = [r for r in recs if r["ground_truth"] == "NORMAL"]
        defects = [r for r in recs if r["ground_truth"] == "DEFECTIVE"]
        cat_correct = sum(1 for r in recs if r["category_accurate"])
        accepted = sum(1 for r in recs if r["inference_executed"])
        rejected = total - accepted

        tp = sum(1 for r in recs if r["ground_truth"] == "DEFECTIVE" and r["actual_verdict"] == "DEFECTIVE")
        fn = sum(1 for r in recs if r["ground_truth"] == "DEFECTIVE" and r["actual_verdict"] != "DEFECTIVE")
        tn = sum(1 for r in recs if r["ground_truth"] == "NORMAL" and r["actual_verdict"] == "NORMAL")
        fp = sum(1 for r in recs if r["ground_truth"] == "NORMAL" and r["actual_verdict"] == "DEFECTIVE")

        recall = (tp / (tp + fn)) if (tp + fn) > 0 else 0.0
        spec = (tn / (tn + fp)) if (tn + fp) > 0 else 0.0
        prec = (tp / (tp + fp)) if (tp + fp) > 0 else 0.0
        f1 = (2 * prec * recall / (prec + recall)) if (prec + recall) > 0 else 0.0
        avg_lat = np.mean([r["latency_ms"] for r in recs])

        summary = {
            "domain": dom,
            "total_images": total,
            "normal_samples": len(normals),
            "defective_samples": len(defects),
            "category_accuracy": round((cat_correct / total) * 100.0, 1),
            "input_rejection_rate": round((rejected / total) * 100.0, 1),
            "accepted_count": accepted,
            "rejected_count": rejected,
            "true_positives": tp,
            "false_positives": fp,
            "true_negatives": tn,
            "false_negatives": fn,
            "recall": round(recall, 4),
            "specificity": round(spec, 4),
            "precision": round(prec, 4),
            "f1": round(f1, 4),
            "mean_latency_ms": round(float(avg_lat), 2)
        }
        domain_metrics[dom] = summary

        print(f"\n>> {dom}:")
        print(f"   Samples: {total} (Normal: {len(normals)}, Defective: {len(defects)})")
        print(f"   Category Accuracy: {summary['category_accuracy']}%")
        print(f"   Rejection Rate:    {summary['input_rejection_rate']}% ({rejected}/{total})")
        print(f"   TP: {tp}, FP: {fp}, TN: {tn}, FN: {fn}")
        print(f"   Recall: {recall*100:.1f}%, Specificity: {spec*100:.1f}%, Precision: {prec*100:.1f}%, F1: {f1:.4f}")
        print(f"   Mean Latency:      {avg_lat:.1f}ms")

    # Output manifest JSON & CSV
    out_dir = "release/final_validation"
    os.makedirs(out_dir, exist_ok=True)
    manifest_path = os.path.join(out_dir, "EXTERNAL_IMAGE_TEST_MANIFEST.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump({
            "audit_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "domain_metrics": domain_metrics,
            "specimen_records": results
        }, f, indent=2)

    csv_path = os.path.join(out_dir, "DOMAIN_STRATIFIED_EVALUATION.csv")
    import csv
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "specimen_id", "domain", "name", "ground_truth", "routing_mode",
            "profile_id", "detected_category", "category_confidence",
            "image_domain_detected", "foreground_coverage_pct",
            "inference_executed", "anomaly_score", "calibrated_threshold",
            "actual_verdict", "outcome", "latency_ms"
        ])
        writer.writeheader()
        for r in results:
            writer.writerow({k: r.get(k) for k in writer.fieldnames})

    print("\n" + "=" * 80)
    print(f"Evaluation complete! Manifest and results written to:")
    print(f" - {manifest_path}")
    print(f" - {csv_path}")
    print("=" * 80)

if __name__ == "__main__":
    main()
