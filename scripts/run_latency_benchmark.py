import os
import sys
import time
import io
import numpy as np
import pandas as pd
import torch
import cv2

dv_path = os.path.abspath("DefectVisionAI")
if dv_path not in sys.path:
    sys.path.insert(0, dv_path)

import app
from starlette.testclient import TestClient

def run_latency_bench():
    print("=== STEP 5: LATENCY & RESOURCE PROFILE BENCHMARK ===")
    client = TestClient(app.app)

    # Test specimen
    img_path = "G:/My Drive/DefectVisionAI/dataset/raw/mvtec/bottle/test/broken_large/000.png"
    if not os.path.exists(img_path):
        img_bgr = np.zeros((224, 224, 3), dtype=np.uint8)
    else:
        img_bgr = cv2.imread(img_path)

    _, img_bytes = cv2.imencode(".png", img_bgr)
    raw_payload = img_bytes.tobytes()

    # 1. Warm-up
    print("Warming up inference pipeline (10 runs)...")
    for _ in range(10):
        app.inspect_single_image(img_path, "bottle")

    # 2. Benchmark Component Breakdown (Direct)
    print("Measuring component latencies (50 iterations)...")
    t_pc_list = []
    t_eff_list = []
    t_total_list = []

    device = torch.device("cpu")
    pc_m = app.get_patchcore_model("bottle")
    extractor = app.extractor
    effnet = app.effnet_model
    eff_transform = app.eff_transform
    PC_MEAN = app.PC_MEAN
    PC_STD = app.PC_STD

    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    img_pc = cv2.resize(img_rgb, (224, 224)).astype(np.float32) / 255.0
    img_pc = (img_pc - PC_MEAN) / PC_STD
    pc_tensor = torch.from_numpy(img_pc).permute(2, 0, 1).float().unsqueeze(0).to(device)
    eff_tensor = eff_transform(image=img_rgb)["image"].unsqueeze(0).to(device)

    for _ in range(50):
        t0 = time.perf_counter()
        with torch.no_grad():
            emb = extractor(pc_tensor)[0].cpu().numpy()
        dist_map, raw_score = pc_m.score(emb)
        t1 = time.perf_counter()

        with torch.no_grad():
            out = effnet(eff_tensor)
            prob = float(torch.softmax(out, dim=1)[0, 1].item())
        t2 = time.perf_counter()

        t_pc_list.append((t1 - t0) * 1000)
        t_eff_list.append((t2 - t1) * 1000)
        t_total_list.append((t2 - t0) * 1000)

    # 3. Benchmark API Endpoints
    print("Measuring FastAPI API latencies (50 iterations)...")
    t_api_frame_list = []
    t_api_predict_list = []

    for _ in range(50):
        t0 = time.perf_counter()
        resp = client.post("/inspect-frame", data={"category": "bottle"}, files={"frame": ("frame.png", io.BytesIO(raw_payload), "image/png")})
        t1 = time.perf_counter()
        t_api_frame_list.append((t1 - t0) * 1000)

        t2 = time.perf_counter()
        resp2 = client.post("/predict", data={"category": "bottle"}, files={"file": ("file.png", io.BytesIO(raw_payload), "image/png")})
        t3 = time.perf_counter()
        t_api_predict_list.append((t3 - t2) * 1000)

    # Compile Benchmark Results
    bench_data = [
        {"metric": "PatchCore Extractor + FAISS (ms)", "mean": np.mean(t_pc_list), "p50": np.percentile(t_pc_list, 50), "p90": np.percentile(t_pc_list, 90), "p95": np.percentile(t_pc_list, 95), "p99": np.percentile(t_pc_list, 99)},
        {"metric": "EfficientNet-B0 Forward (ms)", "mean": np.mean(t_eff_list), "p50": np.percentile(t_eff_list, 50), "p90": np.percentile(t_eff_list, 90), "p95": np.percentile(t_eff_list, 95), "p99": np.percentile(t_eff_list, 99)},
        {"metric": "Direct Dual-Model Total (ms)", "mean": np.mean(t_total_list), "p50": np.percentile(t_total_list, 50), "p90": np.percentile(t_total_list, 90), "p95": np.percentile(t_total_list, 95), "p99": np.percentile(t_total_list, 99)},
        {"metric": "API /inspect-frame (ms)", "mean": np.mean(t_api_frame_list), "p50": np.percentile(t_api_frame_list, 50), "p90": np.percentile(t_api_frame_list, 90), "p95": np.percentile(t_api_frame_list, 95), "p99": np.percentile(t_api_frame_list, 99)},
        {"metric": "API /predict multipart (ms)", "mean": np.mean(t_api_predict_list), "p50": np.percentile(t_api_predict_list, 50), "p90": np.percentile(t_api_predict_list, 90), "p95": np.percentile(t_api_predict_list, 95), "p99": np.percentile(t_api_predict_list, 99)}
    ]
    df_bench = pd.DataFrame(bench_data)
    out_csv = "release/final_18h_validation/latency_benchmark.csv"
    df_bench.to_csv(out_csv, index=False)
    print(f"\nLatency benchmark saved to {out_csv}")
    print(df_bench.to_string())

if __name__ == "__main__":
    run_latency_bench()
