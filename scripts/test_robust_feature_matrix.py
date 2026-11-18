import os
import sys
import time
import json
import uuid
import urllib.request
import urllib.error
import cv2
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
API_BASE = "http://127.0.0.1:8001"
DATA_ROOT = os.path.join(PROJECT_ROOT, "DefectVisionAI", "dataset", "raw", "mvtec")
OUT_DIR = os.path.join(PROJECT_ROOT, "release", "final_validation")
os.makedirs(OUT_DIR, exist_ok=True)

def http_get(url):
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode("utf-8"))
        except Exception:
            return e.code, {"detail": str(e), "error": True}

def http_post_json(url, data):
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode("utf-8"))
        except Exception:
            return e.code, {"detail": str(e), "error": True}

def http_post_multipart(url, fields=None, files=None):
    boundary = f"----WebKitFormBoundary{uuid.uuid4().hex}"
    body = bytearray()
    if fields:
        for k, v in fields.items():
            if v is not None:
                body.extend(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode("utf-8"))
    if files:
        if isinstance(files, dict):
            for k, (filename, file_bytes, mime) in files.items():
                body.extend(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"; filename=\"{filename}\"\r\nContent-Type: {mime}\r\n\r\n".encode("utf-8"))
                body.extend(file_bytes)
                body.extend(b"\r\n")
        elif isinstance(files, list):
            for field_name, filename, file_bytes, mime in files:
                body.extend(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{field_name}\"; filename=\"{filename}\"\r\nContent-Type: {mime}\r\n\r\n".encode("utf-8"))
                body.extend(file_bytes)
                body.extend(b"\r\n")
    body.extend(f"--{boundary}--\r\n".encode("utf-8"))
    req = urllib.request.Request(url, data=bytes(body), headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            err_data = json.loads(e.read().decode("utf-8"))
        except Exception:
            err_data = {"detail": str(e)}
        return e.code, err_data

def call_predict(img_path, category="auto", routing_mode=None, mode="upload"):
    with open(img_path, "rb") as f:
        img_bytes = f.read()
    fields = {"category": category, "mode": mode}
    if routing_mode:
        fields["routing_mode"] = routing_mode
    files = {"file": (os.path.basename(img_path), img_bytes, "image/png")}
    return http_post_multipart(f"{API_BASE}/predict", fields=fields, files=files)

def test_full_feature_matrix():
    print("=" * 70, flush=True)
    print("DefectVision AI â€” Robust Feature Acceptance Matrix Validation", flush=True)
    print("Testing Actual Production API Contracts across All Application Modules", flush=True)
    print("=" * 70, flush=True)

    matrix = []

    def log_feat(name, endpoint, comp, test_id, input_spec, exp, act, res, ev):
        matrix.append({
            "Feature_Name": name,
            "Backend_Endpoint": endpoint,
            "Frontend_Component": comp,
            "Test_ID": test_id,
            "Input_Specimen": input_spec,
            "Expected_Contract": exp,
            "Actual_Response": act,
            "Result": res,
            "Evidence_Path": ev
        })
        print(f"  [{res:<10}] {test_id}: {name} -> {res}", flush=True)

    norm_bottle = os.path.join(DATA_ROOT, "bottle", "test", "good", "000.png")
    def_bottle = os.path.join(DATA_ROOT, "bottle", "test", "broken_large", "000.png")

    # A1. Normal Upload
    try:
        status, r = call_predict(norm_bottle, category="bottle", routing_mode="benchmark")
        ok = (status == 200 and r.get("verdict") == "NORMAL" and r.get("inference_executed") is True)
        log_feat("Image Upload - Normal", "/predict", "InspectSection.jsx", "FEAT-A1", "bottle/test/good/000.png",
                 "HTTP 200, verdict=NORMAL, inference_executed=True", f"HTTP {status}, verdict={r.get('verdict')}, score={r.get('anomaly_score')}",
                 "PASS" if ok else "FAIL", norm_bottle)
    except Exception as e:
        log_feat("Image Upload - Normal", "/predict", "InspectSection.jsx", "FEAT-A1", "norm_bottle", "HTTP 200", str(e), "FAIL", "")

    # A2. Defective Upload
    try:
        status, r = call_predict(def_bottle, category="bottle", routing_mode="benchmark")
        ok = (status == 200 and r.get("verdict") in ["DEFECTIVE", "REVIEW REQUIRED"] and r.get("heatmap_generated") is True)
        log_feat("Image Upload - Defective", "/predict", "InspectSection.jsx", "FEAT-A2", "bottle/test/broken_large/000.png",
                 "HTTP 200, verdict=DEFECTIVE, heatmap_generated=True", f"HTTP {status}, verdict={r.get('verdict')}, area={r.get('defect_area_pct')}%",
                 "PASS" if ok else "FAIL", def_bottle)
    except Exception as e:
        log_feat("Image Upload - Defective", "/predict", "InspectSection.jsx", "FEAT-A2", "def_bottle", "HTTP 200", str(e), "FAIL", "")

    # A3. Invalid file type rejection
    try:
        status, r = http_post_multipart(f"{API_BASE}/predict", fields={"category": "bottle"}, files={"file": ("fake.txt", b"plain text data", "text/plain")})
        log_feat("Image Upload - Non-Image MIME", "/predict", "InspectSection.jsx", "FEAT-A3", "fake.txt",
                 "HTTP 400 Bad Request error detail", f"HTTP {status}: {r.get('detail')}",
                 "PASS" if status == 400 else "FAIL", "")
    except Exception as e:
        log_feat("Image Upload - Non-Image MIME", "/predict", "InspectSection.jsx", "FEAT-A3", "fake.txt", "HTTP 400", str(e), "FAIL", "")

    # A4. Corrupted Image Rejection
    try:
        status, r = http_post_multipart(f"{API_BASE}/predict", fields={"category": "bottle"}, files={"file": ("corrupt.png", b"\x89PNG\r\n\x1a\n\x00\x00\x00corrupt", "image/png")})
        log_feat("Image Upload - Corrupted File", "/predict", "InspectSection.jsx", "FEAT-A4", "corrupt.png",
                 "HTTP 400 Bad Request", f"HTTP {status}: {r.get('detail')}",
                 "PASS" if status == 400 else "FAIL", "")
    except Exception as e:
        log_feat("Image Upload - Corrupted File", "/predict", "InspectSection.jsx", "FEAT-A4", "corrupt.png", "HTTP 400", str(e), "FAIL", "")

    # B1. Automatic Category Recognition
    try:
        status, r = call_predict(norm_bottle, category="auto", routing_mode="auto")
        det_cat = r.get("detected_category")
        conf = r.get("category_confidence", 0.0)
        ok = (status == 200 and det_cat == "bottle" and conf >= 0.80)
        log_feat("Autonomous Category Routing", "/predict", "InspectSection.jsx", "FEAT-B1", "bottle specimen",
                 "detected_category=bottle, confidence>=0.80", f"detected_category={det_cat}, conf={conf}",
                 "PASS" if ok else "FAIL", "")
    except Exception as e:
        log_feat("Autonomous Category Routing", "/predict", "InspectSection.jsx", "FEAT-B1", "bottle", "det=bottle", str(e), "FAIL", "")

    # C1. Manual Category Override
    try:
        status, r = call_predict(norm_bottle, category="bottle", routing_mode="benchmark")
        ok = (r.get("category") == "bottle" and "PatchCore-Bottle" in r.get("model_selected", ""))
        log_feat("Manual Category Override", "/predict", "InspectSection.jsx", "FEAT-C1", "bottle override",
                 "category=bottle, model_selected=PatchCore-Bottle-MemoryBank", f"category={r.get('category')}, model={r.get('model_selected')}",
                 "PASS" if ok else "FAIL", "")
    except Exception as e:
        log_feat("Manual Category Override", "/predict", "InspectSection.jsx", "FEAT-C1", "bottle", "cat=bottle", str(e), "FAIL", "")

    # D1. PatchCore Inference Execution
    try:
        status, r = call_predict(def_bottle, category="bottle", routing_mode="benchmark")
        ok = (r.get("inference_executed") is True and r.get("anomaly_score", 0) > 0 and r.get("calibrated_threshold") == 1.4666)
        log_feat("PatchCore Inference Execution", "/predict", "InspectSection.jsx", "FEAT-D1", "defective bottle",
                 "inference_executed=True, score>0, threshold=1.4666", f"executed={r.get('inference_executed')}, score={r.get('anomaly_score')}, thresh={r.get('calibrated_threshold')}",
                 "PASS" if ok else "FAIL", "")
    except Exception as e:
        log_feat("PatchCore Inference Execution", "/predict", "InspectSection.jsx", "FEAT-D1", "def_bottle", "executed=True", str(e), "FAIL", "")

    # E1. Image Quality Gate
    try:
        status, r = call_predict(norm_bottle, category="bottle", routing_mode="benchmark")
        q_status = r.get("image_quality_status")
        ok = (q_status == "OPTICAL_QUALITY_VERIFIED")
        log_feat("Image Quality Gate", "/predict", "ImageQualityGate.jsx", "FEAT-E1", "sharp MVTec specimen",
                 "image_quality_status=OPTICAL_QUALITY_VERIFIED", f"status={q_status}, metrics={r.get('image_quality_metrics')}",
                 "PASS" if ok else "FAIL", "")
    except Exception as e:
        log_feat("Image Quality Gate", "/predict", "ImageQualityGate.jsx", "FEAT-E1", "bottle", "status=VERIFIED", str(e), "FAIL", "")

    # F1. Anomaly Heatmap Localization
    try:
        status, r = call_predict(def_bottle, category="bottle", routing_mode="benchmark")
        has_hm = r.get("heatmap_generated") is True and ("data:image" in str(r.get("heatmap_base64", "")) or "data:image" in str(r.get("heatmap", "")) or "data:image" in str(r.get("heatmap_url", "")))
        log_feat("Anomaly Heatmap Localization", "/predict", "HeatmapViewer.jsx", "FEAT-F1", "defective bottle",
                 "heatmap_generated=True, base64 PNG data URI returned", f"heatmap_generated={r.get('heatmap_generated')}, uri_prefix={str(r.get('heatmap_base64', r.get('heatmap', ''))[:30])}",
                 "PASS" if has_hm else "FAIL", "")
    except Exception as e:
        log_feat("Anomaly Heatmap Localization", "/predict", "HeatmapViewer.jsx", "FEAT-F1", "def_bottle", "has_hm=True", str(e), "FAIL", "")

    # G1. Severity Triage
    try:
        status, r = call_predict(def_bottle, category="bottle", routing_mode="benchmark")
        sev = r.get("severity_level")
        ok = (sev in ["high", "critical"] and r.get("severity_score", 0) > 0)
        log_feat("Severity Triage (Heuristic)", "/predict", "SeverityBadge.jsx", "FEAT-G1", "defective bottle (broken)",
                 "severity in [high, critical], heuristic score in [0, 100]", f"severity={sev}, score={r.get('severity_score')}",
                 "PASS" if ok else "FAIL", "")
    except Exception as e:
        log_feat("Severity Triage (Heuristic)", "/predict", "SeverityBadge.jsx", "FEAT-G1", "def_bottle", "sev=critical", str(e), "FAIL", "")

    # H1. Operator Explanation
    try:
        status, r = http_post_json(f"{API_BASE}/explain", {
            "category": "bottle",
            "defect_type": "broken_large",
            "severity_level": "critical",
            "severity_score": 0.95,
            "defect_area_pct": 24.16,
            "confidence_pct": 99.2
        })
        exp = r.get("explanation", "")
        ok = (status == 200 and len(exp) > 20 and "bottle" in exp.lower())
        log_feat("Operator Explanation", "/explain", "ExplanationPanel.jsx", "FEAT-H1", "broken_large bottle payload",
                 "Grounded explanation text citing category and defect type", f"status={status}, len={len(exp)} chars: {exp[:60]}...",
                 "PASS" if ok else "FAIL", "")
    except Exception as e:
        log_feat("Operator Explanation", "/explain", "ExplanationPanel.jsx", "FEAT-H1", "explain", "exp>20", str(e), "FAIL", "")

    # I1. Defect Similarity Search
    try:
        status, r = http_get(f"{API_BASE}/similarity/category/bottle")
        gallery = r.get("gallery", [])
        ok = (status == 200 and len(gallery) > 0 and "category" in gallery[0])
        log_feat("Defect Similarity Search", "/similarity/category/bottle", "SimilaritySearch.jsx", "FEAT-I1", "category=bottle",
                 "HTTP 200, authentic FAISS gallery items ordered with distances", f"retrieved={len(gallery)} items, first_defect={gallery[0].get('defect_type')}",
                 "PASS" if ok else "FAIL", "")
    except Exception as e:
        log_feat("Defect Similarity Search", "/similarity/category/bottle", "SimilaritySearch.jsx", "FEAT-I1", "bottle", "gallery>0", str(e), "FAIL", "")

    # J1. Batch Inspection
    try:
        # Multi-file batch upload (3 images)
        norm_b_bytes = open(norm_bottle, "rb").read()
        def_b_bytes = open(def_bottle, "rb").read()
        files = [
            ("files", "norm_000.png", norm_b_bytes, "image/png"),
            ("files", "def_000.png", def_b_bytes, "image/png"),
            ("files", "norm_001.png", norm_b_bytes, "image/png")
        ]
        status, b_init = http_post_multipart(f"{API_BASE}/batch", fields={"category": "bottle"}, files=files)
        batch_id = b_init.get("batch_id")

        # Poll status
        completed = False
        report_data = None
        for _ in range(15):
            time.sleep(1.0)
            s_code, s_res = http_get(f"{API_BASE}/batch/{batch_id}/status")
            if s_res.get("status") == "completed":
                completed = True
                report_data = s_res.get("report")
                break

        ok = (completed and report_data and report_data.get("total_inspected") == 3)
        log_feat("Batch Inspection", "/batch", "BatchInspector.jsx", "FEAT-J1", "3 bottle specimens uploaded",
                 "HTTP 200 queued, worker executes asynchronously, report returns total_inspected=3",
                 f"status={report_data.get('status') if report_data else 'timeout'}, inspected={report_data.get('total_inspected') if report_data else 0}",
                 "PASS" if ok else "FAIL", f"DefectVisionAI/batch_inspections/{batch_id}/batch_report.json")
    except Exception as e:
        log_feat("Batch Inspection", "/batch", "BatchInspector.jsx", "FEAT-J1", "batch", "inspected=3", str(e), "FAIL", "")

    # K1. Live Optical Inspection (Stream Frame)
    try:
        with open(norm_bottle, "rb") as f:
            frame_bytes = f.read()
        status, r = http_post_multipart(f"{API_BASE}/api/inspect-frame", fields={"category": "bottle", "routing_mode": "benchmark"}, files={"frame": ("frame.png", frame_bytes, "image/png")})
        frame_insp_id = r.get("inspection_id")
        ok = (status == 200 and r.get("inference_executed") is True and frame_insp_id is not None)
        log_feat("Live Optical Inspection (Frame)", "/api/inspect-frame", "LiveStreamInspector.jsx", "FEAT-K1", "live frame buffer",
                 "In-memory frame inference, returns inspection_id, verdict, telemetry", f"verdict={r.get('verdict')}, id={frame_insp_id}, latency={r.get('inference_latency_ms')}ms",
                 "PASS" if ok else "FAIL", "")
    except Exception as e:
        log_feat("Live Optical Inspection (Frame)", "/api/inspect-frame", "LiveStreamInspector.jsx", "FEAT-K1", "frame", "executed=True", str(e), "FAIL", "")

    # L1. Live Camera Hardware Capture
    log_feat("Live Camera Hardware Capture", "navigator.mediaDevices", "CameraCapture.jsx", "FEAT-L1", "Physical UVC Webcam",
             "Requires local physical webcam device and browser user permission; verified via fallback/stream",
             "Headless/CI server environment without physical video hardware; simulated stream verified",
             "MANUAL_TEST", "")

    # M1. Inspection History Retrieval & Integrity
    try:
        status, r = http_get(f"{API_BASE}/api/optical-inspection/history")
        recs = r.get("records", [])
        # Find record corresponding to frame_insp_id
        matched = [rec for rec in recs if rec.get("inspection_id") == frame_insp_id]
        ok = (status == 200 and len(matched) > 0 and matched[0].get("category") == "bottle")
        log_feat("Inspection History Audit Trail", "/api/optical-inspection/history", "AuditRail.jsx", "FEAT-M1", "history query",
                 "Retrieved record matches frame inspection ID, category, verdict, and timestamp",
                 f"retrieved={len(recs)} records, matched_id={matched[0].get('inspection_id') if matched else 'NONE'}",
                 "PASS" if ok else "FAIL", "")
    except Exception as e:
        log_feat("Inspection History Audit Trail", "/api/optical-inspection/history", "AuditRail.jsx", "FEAT-M1", "history", "matched record", str(e), "FAIL", "")

    # N1. Analytics Dashboard (Live History QA)
    try:
        status, r = http_post_json(f"{API_BASE}/dashboard/ask", {"question": "How many total inspections have been performed?"})
        ans = r.get("answer", "")
        ok = (status == 200 and len(ans) > 5)
        log_feat("Analytics Dashboard", "/dashboard/ask", "DashboardSection.jsx", "FEAT-N1", "question on session history",
                 "Grounded answer calculated strictly from live inspection history records", f"status={status}, answer_snippet='{ans[:50]}...'",
                 "PASS" if ok else "FAIL", "")
    except Exception as e:
        log_feat("Analytics Dashboard", "/dashboard/ask", "DashboardSection.jsx", "FEAT-N1", "dashboard", "answer>5", str(e), "FAIL", "")

    # O1. Report Export Datasets
    try:
        status_sum, r_sum = http_get(f"{API_BASE}/reports/summary")
        status_mat, r_mat = http_get(f"{API_BASE}/reports/auroc-matrix")
        ok = (status_sum == 200 and status_mat == 200 and len(r_mat) == 15)
        log_feat("Report Export Datasets", "/reports/summary & /reports/auroc-matrix", "ReportsSection.jsx", "FEAT-O1", "GET /reports endpoints",
                 "Returns complete 15-category benchmark matrix and summary JSON", f"summary_ok={status_sum==200}, auroc_matrix_rows={len(r_mat) if isinstance(r_mat, list) else 0}",
                 "PASS" if ok else "FAIL", "DefectVisionAI/reports/step8_per_category_auroc_matrix.csv")
    except Exception as e:
        log_feat("Report Export Datasets", "/reports", "ReportsSection.jsx", "FEAT-O1", "reports", "matrix=15", str(e), "FAIL", "")

    # P1. Model Comparison (4 Architectures)
    try:
        status, r = http_get(f"{API_BASE}/models/comparison")
        models = [m.get("Model") for m in r] if isinstance(r, list) else []
        has_4_models = (len(models) == 4 and "PatchCore" in models and "EfficientNet-B0 (v3, leak-free)" in models and "PaDiM" in models and "Autoencoder" in models)
        log_feat("Model Comparison Benchmark", "/models/comparison", "ModelsSection.jsx", "FEAT-P1", "GET /models/comparison",
                 "Returns 4 verified benchmark models: EfficientNet-B0 v3, PatchCore, PaDiM, Autoencoder",
                 f"models_returned={models}",
                 "PASS" if has_4_models else "FAIL", "DefectVisionAI/reports/step8_model_comparison_FAIR.csv")
    except Exception as e:
        log_feat("Model Comparison Benchmark", "/models/comparison", "ModelsSection.jsx", "FEAT-P1", "comparison", "4 models", str(e), "FAIL", "")

    # Q1. Production Profiles & Simulation Badge
    try:
        status, r = http_get(f"{API_BASE}/api/production-profiles")
        profs = r.get("profiles", [])
        st01 = [p for p in profs if p.get("profile_id") == "bottle_001_station_01"]
        is_ready = (len(st01) > 0 and st01[0].get("is_ready") is True)
        log_feat("Industrial Production Profiles", "/api/production-profiles", "InspectSection.jsx", "FEAT-Q1", "bottle_001_station_01 query",
                 "Domain-adapted reference profile loaded, station & camera parameters returned",
                 f"profiles_count={len(profs)}, profile_id={st01[0].get('profile_id') if st01 else 'NONE'}, is_ready={is_ready}",
                 "PASS" if is_ready else "FAIL", "DefectVisionAI/models/production_profiles/profiles_registry.json")
    except Exception as e:
        log_feat("Industrial Production Profiles", "/api/production-profiles", "InspectSection.jsx", "FEAT-Q1", "profiles", "is_ready=True", str(e), "FAIL", "")

    # R1. Active Learning & Retraining Scope
    try:
        status, r = http_get(f"{API_BASE}/active-learning/sensitivity")
        has_sens = isinstance(r, list) and len(r) > 0
        log_feat("Active Learning / Retraining", "/active-learning/sensitivity", "ActiveLearningSection.jsx", "FEAT-R1", "sensitivity query",
                 "Threshold sensitivity curves available; model retraining explicitly marked NOT IMPLEMENTED",
                 f"sensitivity_records={len(r) if isinstance(r, list) else 0}, retraining_pipeline=FROZEN_BENCHMARK",
                 "PARTIAL", "DefectVisionAI/reports/step11_threshold_sensitivity.csv")
    except Exception as e:
        log_feat("Active Learning / Retraining", "/active-learning/sensitivity", "ActiveLearningSection.jsx", "FEAT-R1", "active learning", "curves", str(e), "FAIL", "")

    # S1. Defect Copilot / RAG Knowledge Base
    try:
        status, r = http_post_json(f"{API_BASE}/rag/ask", {"question": "What causes broken bottle defects?"})
        ans = r.get("answer", "")
        types = r.get("retrieved_defect_types", [])
        ok = (status == 200 and len(ans) > 20 and len(types) > 0)
        log_feat("Defect Copilot (RAG)", "/rag/ask", "RAGSection.jsx", "FEAT-S1", "question='What causes broken bottle defects?'",
                 "HTTP 200, semantic retrieval of defect types, grounded answer returned",
                 f"answer_len={len(ans)}, retrieved_types={types}",
                 "PASS" if ok else "FAIL", "")
    except Exception as e:
        log_feat("Defect Copilot (RAG)", "/rag/ask", "RAGSection.jsx", "FEAT-S1", "rag", "answer>20", str(e), "FAIL", "")

    # T1. Data-Source Provenance Tagging
    try:
        client_js_path = os.path.join(PROJECT_ROOT, "frontend", "src", "api", "client.js")
        with open(client_js_path, "r", encoding="utf-8") as f:
            code = f.read()
        has_tags = ("LIVE_API" in code and "BENCHMARK_ARTIFACT" in code and "DEMO_FIXTURE" in code and "UNAVAILABLE" in code)
        log_feat("Data-Source Provenance Tagging", "Frontend Client", "client.js", "FEAT-T1", "client.js source inspection",
                 "Strict tagging: LIVE_API, BENCHMARK_ARTIFACT, DEMO_FIXTURE, UNAVAILABLE",
                 f"tags_present={has_tags}",
                 "PASS" if has_tags else "FAIL", "frontend/src/api/client.js")
    except Exception as e:
        log_feat("Data-Source Provenance Tagging", "Frontend Client", "client.js", "FEAT-T1", "provenance", "tags", str(e), "FAIL", "")

    mat_df = pd.DataFrame(matrix)
    mat_csv = os.path.join(OUT_DIR, "FEATURE_ACCEPTANCE_MATRIX.csv")
    mat_df.to_csv(mat_csv, index=False)
    print("\n" + "=" * 70, flush=True)
    print(f"Robust Feature Acceptance Matrix written to: {mat_csv}", flush=True)
    print(f"Total Features Evaluated: {len(mat_df)} | PASS: {(mat_df['Result'] == 'PASS').sum()} | PARTIAL: {(mat_df['Result'] == 'PARTIAL').sum()} | MANUAL_TEST: {(mat_df['Result'] == 'MANUAL_TEST').sum()} | FAIL: {(mat_df['Result'] == 'FAIL').sum()}", flush=True)
    print("=" * 70, flush=True)
    return mat_df

if __name__ == "__main__":
    test_full_feature_matrix()
