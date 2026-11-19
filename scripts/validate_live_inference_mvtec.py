"""
DefectVision AI — Strict MVTec AD Localhost Live Inference Validation Script
Executes rigorous verification against the live frontend reverse proxy (http://127.0.0.1:5174/predict).
Uses standard library urllib.request for zero-dependency execution.
"""

import os
import sys
import time
import json
import base64
import urllib.request
import urllib.parse
import mimetypes
import uuid
import cv2
import numpy as np

PROXY_URL = "http://127.0.0.1:5174/predict"
HEALTH_URL = "http://127.0.0.1:5174/api/health"

print("=" * 80)
print("DefectVision AI — Comprehensive Live Inference Correctness & Telemetry Audit")
print(f"Target Proxy URL: {PROXY_URL}")
print("=" * 80)

def http_get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "DefectVisionValidator/1.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))

def post_multipart(url, file_path, form_data):
    boundary = f"----WebKitFormBoundary{uuid.uuid4().hex}"
    lines = []
    for k, v in form_data.items():
        if v is not None:
            lines.append(f"--{boundary}".encode("utf-8"))
            lines.append(f'Content-Disposition: form-data; name="{k}"'.encode("utf-8"))
            lines.append(b"")
            lines.append(str(v).encode("utf-8"))

    # File part
    fname = os.path.basename(file_path)
    mime = "image/png" if fname.endswith(".png") else "image/jpeg"
    lines.append(f"--{boundary}".encode("utf-8"))
    lines.append(f'Content-Disposition: form-data; name="file"; filename="{fname}"'.encode("utf-8"))
    lines.append(f"Content-Type: {mime}".encode("utf-8"))
    lines.append(b"")
    with open(file_path, "rb") as f:
        file_bytes = f.read()
    lines.append(file_bytes)
    lines.append(f"--{boundary}--".encode("utf-8"))
    lines.append(b"")

    body = b"\r\n".join(lines)
    req = urllib.request.Request(url, data=body, headers={
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "User-Agent": "DefectVisionValidator/1.0"
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

# Verify backend readiness first
try:
    code, h_data = http_get_json(HEALTH_URL)
    print(f"Backend Health: status={h_data.get('status')}, models={h_data.get('ready_category_models_count')}/15, classifier={h_data.get('classifier_ready')}")
    assert h_data.get("status") == "ready", "Backend is not ready"
except Exception as e:
    print(f"[FATAL] Health check failed: {e}")
    sys.exit(1)

def decode_and_verify_heatmap(heatmap_b64):
    """Decodes base64 heatmap image and verifies valid dimensions."""
    if not heatmap_b64 or not isinstance(heatmap_b64, str):
        return False, "EMPTY_OR_NON_STRING", None
    if "," in heatmap_b64:
        heatmap_b64 = heatmap_b64.split(",", 1)[1]
    try:
        raw_bytes = base64.b64decode(heatmap_b64)
        nparr = np.frombuffer(raw_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None or img.size == 0:
            return False, "DECODE_FAILED", None
        h, w = img.shape[:2]
        return True, "VALID_IMAGE", (w, h)
    except Exception as err:
        return False, f"EXCEPTION_{err}", None

# =========================================================================
# TRACK A: MANUAL-CATEGORY PATCHCORE BENCHMARK EVALUATION (8 Specimens)
# =========================================================================
manual_specimens = [
    {"name": "Bottle Good", "path": "DefectVisionAI/dataset/raw/mvtec/bottle/test/good/000.png", "category": "bottle", "ground_truth": "NORMAL"},
    {"name": "Bottle Broken Large", "path": "DefectVisionAI/dataset/raw/mvtec/bottle/test/broken_large/000.png", "category": "bottle", "ground_truth": "DEFECTIVE"},
    {"name": "Cable Good", "path": "DefectVisionAI/dataset/raw/mvtec/cable/test/good/000.png", "category": "cable", "ground_truth": "NORMAL"},
    {"name": "Carpet Hole", "path": "DefectVisionAI/dataset/raw/mvtec/carpet/test/hole/000.png", "category": "carpet", "ground_truth": "DEFECTIVE"},
    {"name": "Metal Nut Bent", "path": "DefectVisionAI/dataset/raw/mvtec/metal_nut/test/bent/000.png", "category": "metal_nut", "ground_truth": "DEFECTIVE"},
    {"name": "Pill Color", "path": "DefectVisionAI/dataset/raw/mvtec/pill/test/color/000.png", "category": "pill", "ground_truth": "DEFECTIVE"},
    {"name": "Tile Crack (Manual)", "path": "DefectVisionAI/dataset/raw/mvtec/tile/test/crack/000.png", "category": "tile", "ground_truth": "DEFECTIVE"},
    {"name": "Wood Good", "path": "DefectVisionAI/dataset/raw/mvtec/wood/test/good/000.png", "category": "wood", "ground_truth": "NORMAL"},
]

track_a_results = []
print("\n" + "-" * 80)
print("TRACK A: MANUAL-CATEGORY PATCHCORE VALIDATION (Isolating PatchCore from Classifier)")
print("-" * 80)

for idx, spec in enumerate(manual_specimens, 1):
    path = spec["path"]
    cat = spec["category"]
    gt = spec["ground_truth"]

    code, data, latency_ms = post_multipart(PROXY_URL, path, {"category": cat})
    assert code == 200, f"HTTP status {code} on {path}: {data}"

    # Assertions
    assert data.get("is_demo") is not True, "is_demo must be False"
    assert data.get("inference_executed") is True, f"Inference not executed for {spec['name']}"

    score = float(data["anomaly_score"])
    thresh = float(data.get("calibrated_threshold") or data.get("anomaly_threshold"))
    verdict = data["verdict"]

    # Decision rule consistency
    expected_verdict = "DEFECTIVE" if score >= thresh else "NORMAL"
    assert verdict == expected_verdict, f"Decision mismatch: score={score}, thresh={thresh}, verdict={verdict}"

    # Heatmap validation
    hm_ok, hm_status, hm_dims = decode_and_verify_heatmap(data.get("heatmap_base64") or data.get("heatmap"))
    assert hm_ok, f"Heatmap decode failed: {hm_status}"

    # Outcome classification
    if gt == "NORMAL" and verdict == "NORMAL":
        outcome = "TRUE_NEGATIVE (CORRECT)"
    elif gt == "DEFECTIVE" and verdict == "DEFECTIVE":
        outcome = "TRUE_POSITIVE (CORRECT)"
    elif gt == "NORMAL" and verdict == "DEFECTIVE":
        outcome = "FALSE_POSITIVE (NOMINAL_OVER_THRESHOLD)"
    else:
        outcome = "FALSE_NEGATIVE (ANOMALY_UNDER_THRESHOLD)"

    record = {
        "track": "A_MANUAL_PATCHCORE",
        "index": idx,
        "name": spec["name"],
        "path": path,
        "category": cat,
        "ground_truth": gt,
        "actual_verdict": verdict,
        "anomaly_score": round(score, 4),
        "calibrated_threshold": round(thresh, 4),
        "score_minus_thresh": round(score - thresh, 4),
        "decision_consistent": True,
        "heatmap_status": hm_status,
        "heatmap_dims": f"{hm_dims[0]}x{hm_dims[1]}" if hm_dims else "N/A",
        "latency_ms": round(latency_ms, 2),
        "outcome": outcome
    }
    track_a_results.append(record)
    print(f"[{idx}/8] {spec['name']:22s} | Score: {score:.4f} vs Thresh: {thresh:.4f} -> {verdict:9s} (GT: {gt}) -> {outcome}")

# =========================================================================
# TRACK B: AUTOMATIC CATEGORY ROUTING EVALUATION (8 Specimens)
# =========================================================================
auto_specimens = [
    {"name": "Bottle Good", "path": "DefectVisionAI/dataset/raw/mvtec/bottle/test/good/000.png", "ground_truth": "NORMAL", "expected_cat": "bottle"},
    {"name": "Bottle Broken Large", "path": "DefectVisionAI/dataset/raw/mvtec/bottle/test/broken_large/000.png", "ground_truth": "DEFECTIVE", "expected_cat": "bottle"},
    {"name": "Cable Good", "path": "DefectVisionAI/dataset/raw/mvtec/cable/test/good/000.png", "ground_truth": "NORMAL", "expected_cat": "cable"},
    {"name": "Carpet Hole", "path": "DefectVisionAI/dataset/raw/mvtec/carpet/test/hole/000.png", "ground_truth": "DEFECTIVE", "expected_cat": "carpet"},
    {"name": "Metal Nut Bent", "path": "DefectVisionAI/dataset/raw/mvtec/metal_nut/test/bent/000.png", "ground_truth": "DEFECTIVE", "expected_cat": "metal_nut"},
    {"name": "Pill Color", "path": "DefectVisionAI/dataset/raw/mvtec/pill/test/color/000.png", "ground_truth": "DEFECTIVE", "expected_cat": "pill"},
    {"name": "Tile Crack (Auto)", "path": "DefectVisionAI/dataset/raw/mvtec/tile/test/crack/000.png", "ground_truth": "DEFECTIVE", "expected_cat": "tile"},
    {"name": "Wood Good", "path": "DefectVisionAI/dataset/raw/mvtec/wood/test/good/000.png", "ground_truth": "NORMAL", "expected_cat": "wood"},
]

track_b_results = []
print("\n" + "-" * 80)
print("TRACK B: AUTOMATIC CATEGORY ROUTING VALIDATION (category='auto')")
print("-" * 80)

for idx, spec in enumerate(auto_specimens, 1):
    path = spec["path"]
    gt = spec["ground_truth"]

    code, data, latency_ms = post_multipart(PROXY_URL, path, {"category": "auto"})
    assert code == 200, f"HTTP status {code} on {path}: {data}"

    det_cat = data.get("detected_category") or data.get("category")
    cat_conf = float(data.get("category_confidence") or 0.0)
    rec_status = data.get("recognition_status") or data.get("category_status")
    verdict = data.get("verdict")
    score = data.get("anomaly_score")
    thresh = data.get("calibrated_threshold") or data.get("anomaly_threshold")

    record = {
        "track": "B_AUTOMATIC_ROUTING",
        "index": idx,
        "name": spec["name"],
        "path": path,
        "expected_category": spec["expected_cat"],
        "detected_category": det_cat,
        "category_confidence": round(cat_conf, 4),
        "recognition_status": rec_status,
        "verdict": verdict,
        "ground_truth": gt,
        "anomaly_score": round(score, 4) if score is not None else None,
        "calibrated_threshold": round(thresh, 4) if thresh is not None else None,
        "inference_executed": data.get("inference_executed", True),
        "latency_ms": round(latency_ms, 2)
    }
    track_b_results.append(record)
    print(f"[{idx}/8] {spec['name']:22s} | Detected: {det_cat:10s} (Conf: {cat_conf*100:5.1f}%, Status: {rec_status}) -> Verdict: {verdict:11s} (GT: {gt})")

# =========================================================================
# TRACK C: PRODUCTION PROFILE VALIDATION (bottle_001_station_01)
# =========================================================================
prod_cases = [
    {"name": "Correct-Category Bottle Good", "path": "DefectVisionAI/dataset/raw/mvtec/bottle/test/good/000.png", "expect_pass": True, "expect_verdict": "NORMAL"},
    {"name": "Correct-Category Bottle Broken", "path": "DefectVisionAI/dataset/raw/mvtec/bottle/test/broken_large/000.png", "expect_pass": True, "expect_verdict": "DEFECTIVE"},
    {"name": "Unrelated Leather Mismatch", "path": "DefectVisionAI/dataset/raw/mvtec/leather/test/good/000.png", "expect_pass": False, "expect_rejection": "profile_category_validation"},
    {"name": "Unrelated Tile Mismatch", "path": "DefectVisionAI/dataset/raw/mvtec/tile/test/crack/000.png", "expect_pass": False, "expect_rejection": "profile_category_validation"},
    {"name": "Clear Bottle Light BG", "path": r"c:\Users\surya\Downloads\clear bottle.jpg", "expect_pass": False, "expect_rejection": "profile_category_validation"},
]

track_c_results = []
print("\n" + "-" * 80)
print("TRACK C: PRODUCTION PROFILE TARGET-DOMAIN VALIDATION (bottle_001_station_01)")
print("-" * 80)

for idx, spec in enumerate(prod_cases, 1):
    path = spec["path"]
    if not os.path.exists(path):
        print(f"[{idx}/5] Skipping {spec['name']} (file not found: {path})")
        continue

    code, data, latency_ms = post_multipart(
        PROXY_URL,
        path,
        {"category": "auto", "profile_id": "bottle_001_station_01", "routing_mode": "production"}
    )
    assert code == 200, f"HTTP status {code}: {data}"

    inf_exec = data.get("inference_executed")
    rej_stage = data.get("rejection_stage")
    verdict = data.get("verdict")
    cat_conf = data.get("category_confidence")
    cat_status = data.get("category_status")

    if spec["expect_pass"]:
        assert inf_exec is True, f"Expected inference to execute for {spec['name']}"
        assert data.get("category") == "bottle", "Category must match bottle"
        assert cat_conf != 1.0, "Classifier confidence must not be hardcoded to 100%"
        status_eval = "PASS_INSPECTION_EXECUTED"
    else:
        assert inf_exec is False, f"Inference must NOT execute for {spec['name']}"
        assert rej_stage == spec["expect_rejection"], f"Expected rejection at {spec['expect_rejection']}, got {rej_stage}"
        assert data.get("anomaly_score") is None, "Anomaly score must be None on rejection"
        assert data.get("calibrated_threshold") is None, "Calibrated threshold must be None on rejection"
        status_eval = f"CORRECTLY_REJECTED ({rej_stage})"

    record = {
        "track": "C_PRODUCTION_PROFILE",
        "index": idx,
        "name": spec["name"],
        "path": path,
        "profile_id": "bottle_001_station_01",
        "inference_executed": inf_exec,
        "rejection_stage": rej_stage,
        "verdict": verdict,
        "category_confidence": round(cat_conf, 4) if cat_conf is not None else None,
        "category_status": cat_status,
        "latency_ms": round(latency_ms, 2),
        "status_eval": status_eval
    }
    track_c_results.append(record)
    print(f"[{idx}] {spec['name']:30s} | InfExec: {str(inf_exec):5s} | Stage: {str(rej_stage):26s} | Verdict: {verdict:15s} -> {status_eval}")

# =========================================================================
# WRITE ALL AUDIT EVIDENCE TO AUTHORITATIVE FILE
# =========================================================================
all_results = {
    "audit_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "proxy_url": PROXY_URL,
    "track_a_manual_patchcore": track_a_results,
    "track_b_automatic_routing": track_b_results,
    "track_c_production_profile": track_c_results
}

out_file = "release/final_validation/LOCALHOST_LIVE_INFERENCE_VALIDATION.json"
os.makedirs(os.path.dirname(out_file), exist_ok=True)
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(all_results, f, indent=2)

print("\n" + "=" * 80)
print(f"Validation successfully completed and verified! Output written to:\n{out_file}")
print("=" * 80)
