import os
import sys
import time
import json
import uuid
import hashlib
import urllib.request
import urllib.error
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
API_BASE = "http://127.0.0.1:8001"
MANIFEST_PATH = os.path.join(PROJECT_ROOT, "release", "dataset_manifests", "official_test_split.csv")
OUT_DIR = os.path.join(PROJECT_ROOT, "release", "final_validation")
os.makedirs(OUT_DIR, exist_ok=True)

CATEGORIES = [
    "bottle", "cable", "capsule", "carpet", "grid",
    "hazelnut", "leather", "metal_nut", "pill", "screw",
    "tile", "toothbrush", "transistor", "wood", "zipper"
]

def sha256_file(filepath):
    if not os.path.exists(filepath):
        return "FILE_NOT_FOUND"
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def http_post_multipart(url, fields=None, files=None):
    boundary = f"----WebKitFormBoundary{uuid.uuid4().hex}"
    body = bytearray()
    if fields:
        for k, v in fields.items():
            if v is not None:
                body.extend(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode("utf-8"))
    if files:
        for k, (filename, file_bytes, mime) in files.items():
            body.extend(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"; filename=\"{filename}\"\r\nContent-Type: {mime}\r\n\r\n".encode("utf-8"))
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

def select_90_stratified_specimens():
    df = pd.read_csv(MANIFEST_PATH)
    selected = []

    for cat in CATEGORIES:
        cat_df = df[df["category"] == cat]
        noms = cat_df[cat_df["is_defect"] == 0].sort_values("filepath")
        defs = cat_df[cat_df["is_defect"] == 1].sort_values("filepath")

        # 1. Select 3 distinct normal specimens
        nom_selected = noms.iloc[:3]
        for _, r in nom_selected.iterrows():
            selected.append(r)

        # 2. Select 3 defect specimens across distinct defect types
        def_types = defs["defect_type"].unique().tolist()
        def_chosen = []
        if len(def_types) >= 3:
            for dt in def_types[:3]:
                match = defs[defs["defect_type"] == dt].iloc[0]
                def_chosen.append(match)
        else:
            # Fewer than 3 defect types (e.g. toothbrush has only 'defective')
            for i in range(min(3, len(defs))):
                def_chosen.append(defs.iloc[i])

        for r in def_chosen:
            selected.append(r)

    print(f"Stratified sample selection complete: {len(selected)} specimens total across {len(CATEGORIES)} categories.", flush=True)
    return pd.DataFrame(selected)

def run_workflow_b_evaluation():
    print("=" * 70, flush=True)
    print("DefectVision AI â€” Workflow B 90-Specimen Stratified Evaluation", flush=True)
    print("Testing Autonomous Category Recognition & Pipeline Defect Decisioning", flush=True)
    print("=" * 70, flush=True)

    samples_df = select_90_stratified_specimens()
    records = []
    y_true_cat = []
    y_pred_cat = []

    for idx, row in samples_df.reset_index(drop=True).iterrows():
        cat = row["category"]
        is_def = int(row["is_defect"])
        def_type = row["defect_type"]

        fp = row["filepath"]
        if not os.path.exists(fp):
            fp = os.path.join(PROJECT_ROOT, row["rel_path"])

        # Relative path for public repository hygiene
        rel_p = row.get("rel_path", os.path.relpath(fp, PROJECT_ROOT)).replace("\\", "/")
        file_hash = sha256_file(fp)

        # Workflow A: Operator Override (Benchmark)
        t0 = time.perf_counter()
        status_a, res_a = call_predict(fp, category=cat, routing_mode="benchmark", mode="upload")
        lat_a = (time.perf_counter() - t0) * 1000.0

        # Workflow B: Autonomous Recognition
        t1 = time.perf_counter()
        status_b, res_b = call_predict(fp, category="auto", routing_mode="auto", mode="upload")
        lat_b = (time.perf_counter() - t1) * 1000.0

        pred_cat = res_b.get("detected_category", res_b.get("category", "unknown"))
        conf = float(res_b.get("category_confidence", 0.0))
        cat_status = res_b.get("category_status", "UNKNOWN")
        routing_correct = int(pred_cat == cat)

        y_true_cat.append(cat)
        y_pred_cat.append(pred_cat)

        verdict_a = res_a.get("verdict", "UNKNOWN")
        score_a = float(res_a.get("anomaly_score", 0.0))
        thresh_a = float(res_a.get("calibrated_threshold", 0.0))
        correct_a = int((verdict_a == "NORMAL" and is_def == 0) or (verdict_a in ["DEFECTIVE", "REVIEW REQUIRED"] and is_def == 1))

        verdict_b = res_b.get("verdict", "UNKNOWN")
        score_b = float(res_b.get("anomaly_score", 0.0))
        thresh_b = float(res_b.get("calibrated_threshold", 0.0))
        correct_b = int((verdict_b == "NORMAL" and is_def == 0) or (verdict_b in ["DEFECTIVE", "REVIEW REQUIRED"] and is_def == 1))

        is_false_alarm = int(is_def == 0 and verdict_b in ["DEFECTIVE", "REVIEW REQUIRED"])
        is_defect_escape = int(is_def == 1 and verdict_b == "NORMAL")
        is_review = int(verdict_b == "REVIEW REQUIRED")

        print(f"[{idx+1:02d}/90] {cat.upper():<10} ({def_type:<15}) -> Pred: {pred_cat:<10} (conf={conf:.2f}, match={routing_correct}) | Verdict: {verdict_b:<15} (Score={score_b:.3f}) | Correct: {correct_b}", flush=True)

        records.append({
            "specimen_index": idx + 1,
            "ground_truth_category": cat,
            "is_defect": is_def,
            "defect_type": def_type,
            "relative_path": rel_p,
            "sha256_hash": file_hash,
            # Workflow A
            "wf_a_verdict": verdict_a,
            "wf_a_score": round(score_a, 4),
            "wf_a_threshold": round(thresh_a, 4),
            "wf_a_correct": correct_a,
            "wf_a_latency_ms": round(lat_a, 2),
            # Workflow B
            "wf_b_pred_category": pred_cat,
            "wf_b_confidence": round(conf, 4),
            "wf_b_status": cat_status,
            "wf_b_routing_correct": routing_correct,
            "wf_b_model_selected": res_b.get("model_selected", "none"),
            "wf_b_verdict": verdict_b,
            "wf_b_score": round(score_b, 4),
            "wf_b_threshold": round(thresh_b, 4),
            "wf_b_correct": correct_b,
            "wf_b_latency_ms": round(lat_b, 2),
            "wf_b_heatmap_generated": res_b.get("heatmap_generated", False),
            "is_false_alarm": is_false_alarm,
            "is_defect_escape": is_defect_escape,
            "is_review_required": is_review
        })

    res_df = pd.DataFrame(records)
    out_csv = os.path.join(OUT_DIR, "WORKFLOW_B_STRATIFIED_RESULTS.csv")
    res_df.to_csv(out_csv, index=False)
    print(f"\nStratified 90-Specimen Results saved to: {out_csv}", flush=True)

    # Compute key statistics
    total_n = len(res_df)
    cat_acc = float(accuracy_score(y_true_cat, y_pred_cat))
    prec, rec, f1, _ = precision_recall_fscore_support(y_true_cat, y_pred_cat, labels=CATEGORIES, zero_division=0)
    macro_f1 = float(np.mean(f1))

    # Coverage & OOD rejection
    accepted = res_df[res_df["wf_b_status"] == "ACCEPTED"]
    coverage = len(accepted) / total_n
    ood_rejections = len(res_df[res_df["wf_b_status"].isin(["REJECTED_OOD", "LOW_CONFIDENCE"])]) / total_n

    accepted_routing_acc = float(accuracy_score(
        [y_true_cat[i] for i in accepted.index],
        [y_pred_cat[i] for i in accepted.index]
    )) if len(accepted) > 0 else 0.0

    wf_a_e2e_acc = float(res_df["wf_a_correct"].mean())
    wf_b_e2e_acc = float(res_df["wf_b_correct"].mean())
    total_false_alarms = int(res_df["is_false_alarm"].sum())
    total_escapes = int(res_df["is_defect_escape"].sum())
    total_reviews = int(res_df["is_review_required"].sum())

    print("\n" + "=" * 70, flush=True)
    print("WORKFLOW B 90-SPECIMEN ACCEPTANCE SUMMARY METRICS", flush=True)
    print("=" * 70, flush=True)
    print(f"Total Specimens Evaluated:        {total_n} (45 nominal, 45 defective)", flush=True)
    print(f"Autonomous Category Accuracy:     {cat_acc*100:.2f}% ({res_df['wf_b_routing_correct'].sum()}/{total_n})", flush=True)
    print(f"Autonomous Classifier Macro F1:   {macro_f1*100:.2f}%", flush=True)
    print(f"System Coverage:                  {coverage*100:.2f}% ({len(accepted)}/{total_n} accepted)", flush=True)
    print(f"OOD / Low-Confidence Rate:        {ood_rejections*100:.2f}% ({int(ood_rejections*total_n)}/{total_n})", flush=True)
    print(f"Accepted-Routing Accuracy:        {accepted_routing_acc*100:.2f}%", flush=True)
    print(f"Workflow A E2E Defect Accuracy:   {wf_a_e2e_acc*100:.2f}% ({res_df['wf_a_correct'].sum()}/{total_n})", flush=True)
    print(f"Workflow B E2E Defect Accuracy:   {wf_b_e2e_acc*100:.2f}% ({res_df['wf_b_correct'].sum()}/{total_n})", flush=True)
    print(f"False Alarms (Nominal -> Defect): {total_false_alarms} / 45 ({total_false_alarms/45*100:.2f}%)", flush=True)
    print(f"Defect Escapes (Defect -> Norm):  {total_escapes} / 45 ({total_escapes/45*100:.2f}%)", flush=True)
    print(f"Manual Review Rate:               {total_reviews} / {total_n} ({total_reviews/total_n*100:.2f}%)", flush=True)
    print(f"Mean Workflow A Latency:          {res_df['wf_a_latency_ms'].mean():.1f} ms", flush=True)
    print(f"Mean Workflow B Latency:          {res_df['wf_b_latency_ms'].mean():.1f} ms", flush=True)
    print("=" * 70, flush=True)

    # Plot 15x15 Confusion Matrix for Workflow B on the 90 specimens
    cm = confusion_matrix(y_true_cat, y_pred_cat, labels=CATEGORIES)
    fig, ax = plt.subplots(figsize=(10, 8), dpi=150)
    cax = ax.matshow(cm, cmap=plt.cm.Blues, alpha=0.8)
    fig.colorbar(cax)
    for i in range(len(CATEGORIES)):
        for j in range(len(CATEGORIES)):
            val = cm[i][j]
            ax.text(j, i, f"{val}", ha="center", va="center",
                    color="white" if val > cm.max()/2 else "black", fontsize=9)
    ax.set_xticks(range(len(CATEGORIES)))
    ax.set_yticks(range(len(CATEGORIES)))
    ax.set_xticklabels(CATEGORIES, rotation=45, ha="left", fontsize=8)
    ax.set_yticklabels(CATEGORIES, fontsize=8)
    ax.set_xlabel("Predicted Category (Workflow B)", fontweight="bold")
    ax.set_ylabel("True Category", fontweight="bold")
    ax.set_title(f"Workflow B: Stratified 90-Specimen Confusion Matrix\n(Category Recognition Accuracy: {cat_acc*100:.1f}%)", pad=20, fontweight="bold")
    plt.tight_layout()
    cm_path = os.path.join(OUT_DIR, "workflow_b_90specimen_confusion_matrix.png")
    plt.savefig(cm_path)
    plt.close()
    print(f"Workflow B 90-specimen confusion matrix saved to: {cm_path}", flush=True)

    return res_df

if __name__ == "__main__":
    run_workflow_b_evaluation()
