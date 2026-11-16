import os
import sys
import io
import time
import numpy as np
import cv2
import pandas as pd
# pytest not required

dv_path = os.path.abspath("DefectVisionAI")
if dv_path not in sys.path:
    sys.path.insert(0, dv_path)

import app
from starlette.testclient import TestClient

def run_reliability_tests():
    print("=== RELIABILITY & STRESS TEST HARNESS ===")
    client = TestClient(app.app)
    results = []

    # Test 1: Corrupted / Non-Image File
    print("\nTest 1: Corrupted / 0-byte upload payload...")
    corrupt_bytes = b"NOT_AN_IMAGE_HEADER_CORRUPTED_BYTES"
    resp = client.post("/inspect-frame", data={"category": "bottle"}, files={"file": ("corrupt.png", io.BytesIO(corrupt_bytes), "image/png")})
    # Expect 400 Bad Request
    passed_1 = (resp.status_code == 400)
    print(f"  Status code: {resp.status_code} | Passed: {passed_1}")
    results.append({
        "test_name": "corrupt_image_payload",
        "description": "Upload corrupted non-image byte sequence to /inspect-frame",
        "expected_code": 400,
        "actual_code": resp.status_code,
        "passed": passed_1,
        "details": resp.text[:120]
    })

    # Test 2: Unknown / Unsupported Category
    print("\nTest 2: Unknown category string ('flux_capacitor_v9')...")
    test_img = np.zeros((224, 224, 3), dtype=np.uint8)
    _, buf = cv2.imencode(".png", test_img)
    resp = client.post("/predict", data={"category": "flux_capacitor_v9"}, files={"file": ("test.png", io.BytesIO(buf.tobytes()), "image/png")})
    # Expect 400 Bad Request
    passed_2 = (resp.status_code == 400)
    print(f"  Status code: {resp.status_code} | Passed: {passed_2}")
    results.append({
        "test_name": "unknown_category_rejection",
        "description": "Submit inference request with non-existent category name",
        "expected_code": 400,
        "actual_code": resp.status_code,
        "passed": passed_2,
        "details": resp.text[:120]
    })

    # Test 3: SQL Injection / Malicious Category String
    print("\nTest 3: Malicious category parameter (\"' OR 1=1; DROP TABLE users;--\")...")
    resp = client.post("/predict", data={"category": "' OR 1=1; DROP TABLE users;--"}, files={"file": ("test.png", io.BytesIO(buf.tobytes()), "image/png")})
    passed_3 = (resp.status_code == 400)
    print(f"  Status code: {resp.status_code} | Passed: {passed_3}")
    results.append({
        "test_name": "malicious_string_injection",
        "description": "Attempt SQL injection in category parameter",
        "expected_code": 400,
        "actual_code": resp.status_code,
        "passed": passed_3,
        "details": resp.text[:120]
    })

    # Test 4: Extreme Aspect Ratio (Ultra-wide 1200x50 strip)
    print("\nTest 4: Extreme aspect ratio image (1200x50)...")
    strip_img = np.random.randint(0, 255, (50, 1200, 3), dtype=np.uint8)
    _, strip_buf = cv2.imencode(".png", strip_img)
    resp = client.post("/predict", data={"category": "bottle"}, files={"file": ("strip.png", io.BytesIO(strip_buf.tobytes()), "image/png")})
    passed_4 = (resp.status_code == 200)
    print(f"  Status code: {resp.status_code} | Passed: {passed_4}")
    results.append({
        "test_name": "extreme_aspect_ratio_1200x50",
        "description": "Submit ultra-wide aspect ratio image to verify resize stability",
        "expected_code": 200,
        "actual_code": resp.status_code,
        "passed": passed_4,
        "details": f"Pred: {resp.json().get('predicted_label') if passed_4 else 'ERROR'}"
    })

    # Test 5: High Resolution (2048x2048)
    print("\nTest 5: High resolution 2048x2048 image...")
    hi_res = np.random.randint(0, 255, (2048, 2048, 3), dtype=np.uint8)
    _, hi_buf = cv2.imencode(".png", hi_res)
    resp = client.post("/inspect-frame", data={"category": "bottle"}, files={"frame": ("hi.png", io.BytesIO(hi_buf.tobytes()), "image/png")})
    passed_5 = (resp.status_code == 200)
    print(f"  Status code: {resp.status_code} | Passed: {passed_5}")
    results.append({
        "test_name": "high_resolution_2048x2048",
        "description": "Submit 2048x2048 image to /inspect-frame to test memory footprint",
        "expected_code": 200,
        "actual_code": resp.status_code,
        "passed": passed_5,
        "details": f"Latency: {resp.json().get('processing_time_ms') if passed_5 else 'ERROR'}ms"
    })

    # Test 6: Rapid Sequential Burst (10 requests)
    print("\nTest 6: Rapid sequential burst of 10 requests...")
    burst_passed = True
    latencies = []
    for i in range(10):
        t0 = time.perf_counter()
        resp = client.post("/inspect-frame", data={"category": "bottle"}, files={"frame": ("test.png", io.BytesIO(buf.tobytes()), "image/png")})
        dt = (time.perf_counter() - t0) * 1000
        latencies.append(dt)
        if resp.status_code != 200:
            burst_passed = False
    print(f"  10 requests completed: {burst_passed} | Avg Latency: {np.mean(latencies):.1f}ms | p95: {np.percentile(latencies, 95):.1f}ms")
    results.append({
        "test_name": "rapid_burst_10_requests",
        "description": "Fire 10 back-to-back requests on /inspect-frame",
        "expected_code": 200,
        "actual_code": 200 if burst_passed else 500,
        "passed": burst_passed,
        "details": f"Avg: {np.mean(latencies):.1f}ms, p95: {np.percentile(latencies, 95):.1f}ms"
    })

    # Save summary
    df_res = pd.DataFrame(results)
    out_csv = "release/final_18h_validation/reliability_test_results.csv"
    df_res.to_csv(out_csv, index=False)
    print(f"\nAll reliability tests completed. Written to {out_csv}")
    print(f"Total Passed: {df_res['passed'].sum()} / {len(df_res)}")

if __name__ == "__main__":
    run_reliability_tests()
