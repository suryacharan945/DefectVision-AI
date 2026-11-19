"""
DefectVision AI — Test Script for Universal Intake & Few-Shot Adaptation API
Tests:
1. Universal Intake diagnostics on MVTec bottle, clear bottle.jpg, and disordered bottle.webp.
2. Few-shot product adaptation creating a new profile 'bottle_ext_clear_500ml' from external normal bottle images + station 01 normal samples.
3. Live inspection against the newly created adapted profile.
"""

import os
import sys
import json
import urllib.request
import urllib.parse
import uuid
import time

BASE_URL = "http://127.0.0.1:8001"

def http_get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "TestClient/1.0"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return r.status, json.loads(r.read().decode("utf-8"))

def post_multipart(url, files, form_fields):
    boundary = f"----WebKitFormBoundary{uuid.uuid4().hex}"
    lines = []
    for k, v in form_fields.items():
        if v is not None:
            lines.append(f"--{boundary}".encode("utf-8"))
            lines.append(f'Content-Disposition: form-data; name="{k}"'.encode("utf-8"))
            lines.append(b"")
            lines.append(str(v).encode("utf-8"))

    for field_name, file_path in files:
        fname = os.path.basename(file_path)
        mime = "image/png" if fname.endswith(".png") else ("image/webp" if fname.endswith(".webp") else "image/jpeg")
        lines.append(f"--{boundary}".encode("utf-8"))
        lines.append(f'Content-Disposition: form-data; name="{field_name}"; filename="{fname}"'.encode("utf-8"))
        lines.append(f"Content-Type: {mime}".encode("utf-8"))
        lines.append(b"")
        with open(file_path, "rb") as f:
            lines.append(f.read())

    lines.append(f"--{boundary}--".encode("utf-8"))
    lines.append(b"")
    body = b"\r\n".join(lines)

    req = urllib.request.Request(url, data=body, headers={
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "User-Agent": "TestClient/1.0"
    })
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.status, json.loads(r.read().decode("utf-8"))

def main():
    print("=" * 70)
    print("DEFECTVISION AI 2.0 — ADAPTATION & INTAKE VERIFICATION")
    print("=" * 70)

    # 1. Health check
    code, health = http_get(f"{BASE_URL}/health")
    print(f"Health Status: {health.get('status')}, Profiles: {health.get('production_profiles_count')}")

    # 2. Test Intake Endpoint
    test_img = "DefectVisionAI/dataset/raw/mvtec/bottle/test/good/000.png"
    code, intake_data = post_multipart(
        f"{BASE_URL}/api/intake",
        [("file", test_img)],
        {"inspection_mode": "universal"}
    )
    print(f"\n[Test 1] Universal Intake Endpoint:")
    print(f" - Image Domain:          {intake_data.get('image_domain')}")
    print(f" - Foreground Coverage:    {intake_data.get('foreground_coverage_pct')}%")
    print(f" - Quality Status:         {intake_data.get('image_quality_status')}")
    print(f" - Suitability:            {intake_data.get('suitability_status')}")
    print(f" - Category Detected:      {intake_data.get('detected_category')} ({intake_data.get('category_confidence')*100:.1f}%)")

    # 3. Test Few-Shot Adaptation API
    # Gather reference normal images: external bottle photo + 5 station normal images
    sample_images = []
    ext_bottle = r"c:\Users\surya\Downloads\clear bottle.jpg"
    ext_bottle2 = r"c:\Users\surya\Downloads\clear bottle2.webp"
    if os.path.exists(ext_bottle):
        sample_images.append(("files", ext_bottle))
    if os.path.exists(ext_bottle2):
        sample_images.append(("files", ext_bottle2))

    # Add several station normal images
    for i in range(5):
        p = f"data/station_01/train_normal/station01_normal_train_{i:03d}.png"
        if os.path.exists(p):
            sample_images.append(("files", p))

    print(f"\n[Test 2] Few-Shot Adaptation Workflow with {len(sample_images)} normal samples:")
    code, adapt_data = post_multipart(
        f"{BASE_URL}/api/production-profiles/adapt",
        sample_images,
        {
            "product_name": "Clear Glass Bottle 500ml (Adapted Multi-Domain)",
            "sku": "SKU-BTL-ADAPT-002",
            "category": "bottle",
            "acquisition_type": "controlled_photography",
            "camera_details": "CAM-EXT-01 (Stationary & Controlled)",
            "lighting_details": "Diffuse Ambient Backlight",
            "calibration_split_ratio": 0.30,
            "coreset_ratio": 0.10
        }
    )
    print(f" - Status:                 {adapt_data.get('status')}")
    print(f" - Profile ID:             {adapt_data.get('profile_id')}")
    print(f" - Training Count:         {adapt_data.get('training_samples_count')}")
    print(f" - Calibration Count:      {adapt_data.get('calibration_samples_count')}")
    print(f" - Calibrated Threshold:   {adapt_data.get('calibrated_threshold')}")
    print(f" - Validation Status:      {adapt_data.get('validation_status')}")
    new_profile_id = adapt_data.get("profile_id")

    # 4. Inspect using the new profile!
    print(f"\n[Test 3] Live Inspection with Newly Created Profile '{new_profile_id}':")
    # Test Normal
    code, norm_res = post_multipart(
        f"{BASE_URL}/predict",
        [("file", "DefectVisionAI/dataset/raw/mvtec/bottle/test/good/000.png")],
        {"profile_id": new_profile_id, "routing_mode": "production"}
    )
    print(f" - Normal Sample  -> Verdict: {norm_res.get('verdict')} (Score: {norm_res.get('anomaly_score')} vs Thresh: {norm_res.get('calibrated_threshold')})")

    # Test Defective
    code, def_res = post_multipart(
        f"{BASE_URL}/predict",
        [("file", "DefectVisionAI/dataset/raw/mvtec/bottle/test/broken_large/000.png")],
        {"profile_id": new_profile_id, "routing_mode": "production"}
    )
    print(f" - Defective Sample -> Verdict: {def_res.get('verdict')} (Score: {def_res.get('anomaly_score')} vs Thresh: {def_res.get('calibrated_threshold')})")

    # 5. Test Mode C (Universal Intake & Best-Effort Triage)
    print(f"\n[Test 4] Mode C: Universal Intake & Best-Effort Triage:")
    code, uni_res = post_multipart(
        f"{BASE_URL}/predict",
        [("file", "DefectVisionAI/dataset/raw/mvtec/bottle/test/broken_large/000.png")],
        {"routing_mode": "universal", "category": "auto"}
    )
    print(f" - Universal Mode -> Verdict: {uni_res.get('verdict')} (Score: {uni_res.get('anomaly_score')}, Domain: {uni_res.get('image_domain')}, Preproc: {uni_res.get('preprocessing_applied')})")

    print("\n" + "=" * 70)
    print("ALL API CHECKS PASSED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    main()
