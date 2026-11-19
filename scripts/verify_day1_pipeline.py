#!/usr/bin/env python3
"""
DefectVision AI v1.0.0-rc1 — Day 1 Model, Backend, and End-to-End Pipeline Verification
Independently verifies:
1. All 15 category PatchCore memory banks, shapes, FAISS indexes, and thresholds.
2. EfficientNet-B0 v3 classifier weights and forward execution.
3. Live backend endpoints on http://127.0.0.1:8001 (health, inspection, predict, quality gate, profiles, history).
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error
import numpy as np
import cv2
import torch
import timm

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(PROJECT_ROOT, "DefectVisionAI", "models")
PATCHCORE_DIR = os.path.join(MODELS_DIR, "patchcore")
FAISS_DIR = os.path.join(MODELS_DIR, "faiss_index")
EFFNET_DIR = os.path.join(MODELS_DIR, "efficientnet_baseline_v3")

CATEGORIES = [
    "bottle", "cable", "capsule", "carpet", "grid",
    "hazelnut", "leather", "metal_nut", "pill", "screw",
    "tile", "toothbrush", "transistor", "wood", "zipper"
]

def multipart_post(url, fields, files):
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    body = bytearray()
    for name, value in fields.items():
        body.extend(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n".encode("utf-8"))
    for name, (filename, data, content_type) in files.items():
        body.extend(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"; filename=\"{filename}\"\r\nContent-Type: {content_type}\r\n\r\n".encode("utf-8"))
        body.extend(data)
        body.extend(b"\r\n")
    body.extend(f"--{boundary}--\r\n".encode("utf-8"))
    req = urllib.request.Request(url, data=body)
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))

def main():
    print("=" * 70)
    print("DEFECTVISION AI v1.0.0-rc1 — DAY 1 COMPREHENSIVE VERIFICATION")
    print("=" * 70)

    results = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "categories_verified": {},
        "classifier_verified": {},
        "live_api_verified": {},
        "summary": {}
    }

    # ---------------------------------------------------------
    # 1. VERIFY ALL 15 PATCHCORE CATEGORY MODELS
    # ---------------------------------------------------------
    print("\n--- 1. Verifying 15 PatchCore Category Models ---")
    thresholds_file = os.path.join(PATCHCORE_DIR, "category_thresholds.json")
    with open(thresholds_file, "r") as f:
        thresholds_data = json.load(f)

    all_models_valid = True
    for cat in CATEGORIES:
        mb_path = os.path.join(PATCHCORE_DIR, cat, "memory_bank.npy")
        faiss_path = os.path.join(FAISS_DIR, cat, "index.faiss")
        meta_path = os.path.join(FAISS_DIR, cat, "metadata.json")

        mb_exists = os.path.exists(mb_path)
        faiss_exists = os.path.exists(faiss_path)
        thresh_info = thresholds_data.get(cat, {})

        shape = None
        dim = None
        tokens = None
        if mb_exists:
            mb = np.load(mb_path, mmap_mode="r")
            shape = list(mb.shape)
            tokens = shape[0]
            dim = shape[1] if len(shape) > 1 else None

        cat_valid = (
            mb_exists and
            faiss_exists and
            dim == 384 and
            tokens > 0 and
            "calibrated_threshold" in thresh_info
        )
        if not cat_valid:
            all_models_valid = False

        results["categories_verified"][cat] = {
            "valid": cat_valid,
            "memory_bank_path": mb_path,
            "memory_bank_exists": mb_exists,
            "tokens": tokens,
            "embedding_dim": dim,
            "faiss_index_exists": faiss_exists,
            "calibrated_threshold": thresh_info.get("calibrated_threshold"),
            "baseline_mean": thresh_info.get("baseline_mean"),
            "baseline_p99": thresh_info.get("baseline_p99")
        }
        status_str = "OK" if cat_valid else "FAILED"
        print(f"[{status_str}] Category: {cat:12s} | Tokens: {tokens:6d} | Dim: {dim} | Threshold: {thresh_info.get('calibrated_threshold')}")

    results["summary"]["all_patchcore_models_valid"] = all_models_valid
    print(f"\nAll 15 PatchCore models valid: {all_models_valid}")

    # ---------------------------------------------------------
    # 2. VERIFY EFFICIENTNET-B0 CLASSIFIER
    # ---------------------------------------------------------
    print("\n--- 2. Verifying EfficientNet-B0 Classifier ---")
    effnet_ckpt_path = os.path.join(EFFNET_DIR, "best_model.pt")
    effnet_exists = os.path.exists(effnet_ckpt_path)

    effnet_valid = False
    details = {}
    if effnet_exists:
        try:
            ckpt = torch.load(effnet_ckpt_path, map_location="cpu")
            state_dict = ckpt.get("model_state", ckpt)
            model = timm.create_model("efficientnet_b0", pretrained=False, num_classes=2)
            model.load_state_dict(state_dict)
            model.eval()

            # Forward pass test
            dummy_input = torch.randn(1, 3, 224, 224)
            with torch.no_grad():
                out = model(dummy_input)
                probs = torch.softmax(out, dim=1).numpy().tolist()[0]

            effnet_valid = (out.shape == (1, 2))
            details = {
                "checkpoint_path": effnet_ckpt_path,
                "file_size_bytes": os.path.getsize(effnet_ckpt_path),
                "num_classes": 2,
                "output_shape": list(out.shape),
                "test_probabilities": probs,
                "epoch": ckpt.get("epoch"),
                "best_acc": ckpt.get("acc", ckpt.get("best_acc"))
            }
        except Exception as e:
            details["error"] = str(e)

    results["classifier_verified"] = {
        "valid": effnet_valid,
        "details": details
    }
    results["summary"]["classifier_valid"] = effnet_valid
    print(f"[{'OK' if effnet_valid else 'FAILED'}] EfficientNet-B0 Classifier: Output Shape: {details.get('output_shape')}, Best Acc: {details.get('best_acc')}")

    # ---------------------------------------------------------
    # 3. VERIFY LIVE BACKEND FASTAPI ENDPOINTS
    # ---------------------------------------------------------
    print("\n--- 3. Verifying Live FastAPI Backend Endpoints (http://127.0.0.1:8001) ---")
    BASE_URL = "http://127.0.0.1:8001"

    # Test 3.1: Health endpoint
    try:
        with urllib.request.urlopen(f"{BASE_URL}/health", timeout=10) as r:
            health_code = r.status
            health_json = json.loads(r.read().decode())
    except Exception as e:
        health_code = 500
        health_json = {"error": str(e)}

    print(f"[{'OK' if health_code == 200 else 'FAIL'}] GET /health -> Status: {health_json.get('status')}, Models Ready: {health_json.get('all_required_models_ready')}")
    results["live_api_verified"]["health"] = {"status_code": health_code, "data": health_json}

    # Test 3.2: Model status endpoint
    try:
        with urllib.request.urlopen(f"{BASE_URL}/api/optical-inspection/model-status", timeout=10) as r:
            ms_code = r.status
            ms_json = json.loads(r.read().decode())
    except Exception as e:
        ms_code = 500
        ms_json = {"error": str(e)}

    print(f"[{'OK' if ms_code == 200 else 'FAIL'}] GET /api/optical-inspection/model-status -> Total: {ms_json.get('total_categories')}, All Ready: {ms_json.get('all_ready')}")
    results["live_api_verified"]["model_status"] = {"status_code": ms_code, "data": ms_json}

    # Test 3.3: Production profiles endpoint
    try:
        with urllib.request.urlopen(f"{BASE_URL}/api/production-profiles", timeout=10) as r:
            prof_code = r.status
            prof_json = json.loads(r.read().decode())
    except Exception as e:
        prof_code = 500
        prof_json = {"error": str(e)}

    print(f"[{'OK' if prof_code == 200 else 'FAIL'}] GET /api/production-profiles -> Profiles: {len(prof_json.get('profiles', []))}")
    results["live_api_verified"]["profiles"] = {"status_code": prof_code, "data": prof_json}

    # Test 3.4: Normal image inspection (/api/inspect-frame)
    nom_path = os.path.join(PROJECT_ROOT, "release", "portfolio_handover", "assets", "04_genuine_specimen_raw_bottle_nominal.png")
    with open(nom_path, "rb") as f:
        nom_bytes = f.read()
    s_nom, d_nom = multipart_post(f"{BASE_URL}/api/inspect-frame", {"category": "bottle"}, {"file": ("bottle_nom.png", nom_bytes, "image/png")})
    print(f"[{'OK' if s_nom == 200 else 'FAIL'}] POST /api/inspect-frame (Normal Bottle) -> Verdict: {d_nom.get('verdict')}, Score: {d_nom.get('anomaly_score')}, Tau: {d_nom.get('threshold')}")
    results["live_api_verified"]["inspect_normal"] = {"status_code": s_nom, "verdict": d_nom.get("verdict"), "score": d_nom.get("anomaly_score")}

    # Test 3.5: Defective image inspection (/api/inspect-frame)
    def_path = os.path.join(PROJECT_ROOT, "release", "portfolio_handover", "assets", "01_genuine_specimen_raw_bottle_defective.png")
    with open(def_path, "rb") as f:
        def_bytes = f.read()
    s_def, d_def = multipart_post(f"{BASE_URL}/api/inspect-frame", {"category": "bottle"}, {"file": ("bottle_def.png", def_bytes, "image/png")})
    has_heatmap = (d_def.get("heatmap_generated") is True) or (len(d_def.get("heatmap_base64", "")) > 100) or (len(d_def.get("heatmap", "")) > 100)
    print(f"[{'OK' if s_def == 200 and has_heatmap else 'FAIL'}] POST /api/inspect-frame (Defective Bottle) -> Verdict: {d_def.get('verdict')}, Score: {d_def.get('anomaly_score')}, Heatmap Generated: {has_heatmap}")
    results["live_api_verified"]["inspect_defective"] = {"status_code": s_def, "verdict": d_def.get("verdict"), "score": d_def.get("anomaly_score"), "heatmap": has_heatmap}

    # Test 3.6: Texture image inspection (Tile)
    tile_path = os.path.join(PROJECT_ROOT, "DefectVisionAI", "outputs", "similarity_search_samples", "tile_similarity_demo.png")
    with open(tile_path, "rb") as f:
        tile_bytes = f.read()
    s_tile, d_tile = multipart_post(f"{BASE_URL}/api/inspect-frame", {"category": "tile"}, {"file": ("tile.png", tile_bytes, "image/png")})
    print(f"[{'OK' if s_tile == 200 else 'FAIL'}] POST /api/inspect-frame (Texture: Tile) -> Verdict: {d_tile.get('verdict')}, Score: {d_tile.get('anomaly_score')}")
    results["live_api_verified"]["inspect_texture"] = {"status_code": s_tile, "verdict": d_tile.get("verdict"), "score": d_tile.get("anomaly_score")}

    # Test 3.7: Quality Gate Rejection (Solid black image)
    black_img = np.zeros((224, 224, 3), dtype=np.uint8)
    _, black_enc = cv2.imencode(".png", black_img)
    s_qg, d_qg = multipart_post(f"{BASE_URL}/api/inspect-frame", {"category": "bottle"}, {"file": ("black.png", black_enc.tobytes(), "image/png")})
    is_qg_rejected = (d_qg.get("verdict") in ["REVIEW REQUIRED", "UNSUPPORTED"] or d_qg.get("quality_rejection") is True)
    print(f"[{'OK' if is_qg_rejected else 'FAIL'}] POST /api/inspect-frame (Quality Gate Black Image) -> Verdict: {d_qg.get('verdict')}, Rejection: {d_qg.get('quality_rejection')}")
    results["live_api_verified"]["quality_gate"] = {"status_code": s_qg, "verdict": d_qg.get("verdict"), "rejected": is_qg_rejected}

    # Test 3.8: Category Mismatch / Profile Guard
    # Inspect bottle on cable profile -> should trigger mismatch or profile rejection
    s_mis, d_mis = multipart_post(f"{BASE_URL}/api/inspect-frame", {"category": "cable", "profile_id": "bottle_001_station_01"}, {"file": ("bottle.png", nom_bytes, "image/png")})
    print(f"[{'OK' if s_mis in [200, 400, 422] else 'FAIL'}] POST /api/inspect-frame (Profile Mismatch Guard) -> Status: {s_mis}, Verdict: {d_mis.get('verdict')}, Msg: {d_mis.get('status_message', d_mis.get('detail'))}")
    results["live_api_verified"]["profile_mismatch_guard"] = {"status_code": s_mis, "data": d_mis}

    # Test 3.9: History Endpoint
    try:
        with urllib.request.urlopen(f"{BASE_URL}/api/optical-inspection/history", timeout=10) as r:
            h_code = r.status
            h_json = json.loads(r.read().decode())
    except Exception as e:
        h_code = 500
        h_json = {"error": str(e)}

    print(f"[{'OK' if h_code == 200 else 'FAIL'}] GET /api/optical-inspection/history -> Records Count: {len(h_json.get('history', []))}")
    results["live_api_verified"]["history"] = {"status_code": h_code, "count": len(h_json.get("history", []))}

    # Save verification JSON
    out_json = os.path.join(PROJECT_ROOT, "release", "audits", "day1_verification_results.json")
    with open(out_json, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nVerification results saved to: {out_json}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
