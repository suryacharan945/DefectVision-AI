import os
import json
import pandas as pd

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DV_DIR = os.path.join(ROOT_DIR, "DefectVisionAI")
REPORTS_DIR = os.path.join(DV_DIR, "reports")
LOGS_DIR = os.path.join(DV_DIR, "logs")
MODELS_DIR = os.path.join(DV_DIR, "models")
OUTPUT_DIR = os.path.join(ROOT_DIR, "frontend", "public", "data")

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("Exporting static data to:", OUTPUT_DIR)

# 1. Models Comparison
step8_fair = os.path.join(REPORTS_DIR, "step8_model_comparison_FAIR.csv")
if os.path.exists(step8_fair):
    df = pd.read_csv(step8_fair).fillna("")
    with open(os.path.join(OUTPUT_DIR, "models_comparison.json"), "w", encoding="utf-8") as f:
        json.dump(df.to_dict("records"), f, indent=2)
    print("Exported models_comparison.json")

# 2. AUROC Matrix
auroc_path = os.path.join(REPORTS_DIR, "step8_per_category_auroc_matrix.csv")
if os.path.exists(auroc_path):
    df = pd.read_csv(auroc_path).fillna("")
    with open(os.path.join(OUTPUT_DIR, "auroc_matrix.json"), "w", encoding="utf-8") as f:
        json.dump(df.to_dict("records"), f, indent=2)
    print("Exported auroc_matrix.json")

# 3. Reports Summary
summary_path = os.path.join(REPORTS_DIR, "final_research_summary.json")
if os.path.exists(summary_path):
    with open(summary_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    with open(os.path.join(OUTPUT_DIR, "reports_summary.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print("Exported reports_summary.json")

# 4. Drift Logs
drift_path = os.path.join(LOGS_DIR, "step12_drift_log_v3.csv")
if os.path.exists(drift_path):
    df = pd.read_csv(drift_path).fillna("")
    with open(os.path.join(OUTPUT_DIR, "drift_logs.json"), "w", encoding="utf-8") as f:
        json.dump(df.to_dict("records"), f, indent=2)
    print("Exported drift_logs.json")

# 5. RAG Entries
kb_path = os.path.join(MODELS_DIR, "rag_knowledge_base", "defect_knowledge_base.csv")
if os.path.exists(kb_path):
    df = pd.read_csv(kb_path).fillna("")
    with open(os.path.join(OUTPUT_DIR, "rag_entries.json"), "w", encoding="utf-8") as f:
        json.dump(df.to_dict("records"), f, indent=2)
    print("Exported rag_entries.json")

# 6. Sensitivity
sens_path = os.path.join(REPORTS_DIR, "step11_threshold_sensitivity.csv")
if os.path.exists(sens_path):
    df = pd.read_csv(sens_path).fillna("")
    with open(os.path.join(OUTPUT_DIR, "sensitivity.json"), "w", encoding="utf-8") as f:
        json.dump(df.to_dict("records"), f, indent=2)
    print("Exported sensitivity.json")

# 7. Baselines
baselines = {}
baseline_path = os.path.join(REPORTS_DIR, "step9_severity_baselines.csv")
if os.path.exists(baseline_path):
    bdf = pd.read_csv(baseline_path)
    for _, row in bdf.iterrows():
        cat = row["category"]
        baselines[cat] = {
            "mean_normal": float(row.get("mean_normal", 0.1)),
            "std_normal": float(row.get("std_normal", 0.05)),
            "threshold_patchcore": float(row.get("threshold_patchcore", row.get("optimal_threshold", 0.5))),
            "minor_threshold": float(row.get("minor_threshold", 0.4)),
            "moderate_threshold": float(row.get("moderate_threshold", 0.6)),
            "critical_threshold": float(row.get("critical_threshold", 0.8))
        }

# 8. Presets
descriptions = {
    "bottle": "Large structural fracture along bottle sidewall",
    "cable": "Cable missing conductor strand / deformed wire",
    "capsule": "Capsule squeeze and surface coating defect",
    "carpet": "Carpet weave puncture / localized fiber defect",
    "grid": "Metal grid bent wire and mesh distortion",
    "hazelnut": "Cracked shell and outer hull hole",
    "leather": "Surface fold, crease, and color stain defect",
    "metal_nut": "Nut thread scratch / heavy metal indentation",
    "pill": "Pill contamination / crack on tablet coating",
    "screw": "Thread damage / deformed screw head",
    "tile": "Ceramic tile deep crack / glaze scratch",
    "toothbrush": "Bristle defect / misaligned tuft pattern",
    "transistor": "Bent lead / semiconductor casing crack",
    "wood": "Wood grain scratch and surface hole",
    "zipper": "Broken zipper tooth / fabric tape tear"
}

known_categories = list(descriptions.keys())

presets = []
for cat in known_categories:
    demo_file = f"{cat}_similarity_demo.png"
    presets.append({
        "category": cat,
        "title": cat.replace("_", " ").title(),
        "filename": demo_file,
        "image_url": f"/outputs/similarity_search_samples/{demo_file}",
        "description": descriptions.get(cat, f"Industrial defect specimen for {cat}"),
        "baseline": baselines.get(cat, {
            "mean_normal": 0.12,
            "threshold_patchcore": 0.45,
            "minor_threshold": 0.35,
            "moderate_threshold": 0.55,
            "critical_threshold": 0.75
        })
    })

with open(os.path.join(OUTPUT_DIR, "presets.json"), "w", encoding="utf-8") as f:
    json.dump(presets, f, indent=2)
print("Exported presets.json")

# 9. Severity Logs (First 100 records for fast browser experience)
sev_path = os.path.join(LOGS_DIR, "step9_severity_log.csv")
if os.path.exists(sev_path):
    sdf = pd.read_csv(sev_path).fillna("")
    exp_path = os.path.join(LOGS_DIR, "step15_llm_explanations.csv")
    exp_map = {}
    if os.path.exists(exp_path):
        try:
            edf = pd.read_csv(exp_path)
            exp_map = dict(zip(edf["filepath"], edf["explanation"]))
        except Exception:
            pass

    records = sdf.sort_values("severity_score", ascending=False).to_dict("records")
    for idx, r in enumerate(records[:150]):
        r["id"] = f"DV-{idx + 1:04d}"
        r["filename"] = os.path.basename(r.get("filepath", f"sample_{idx}.png"))
        cat = r.get("category", "bottle")
        demo_file = f"{cat}_similarity_demo.png"
        r["display_image_url"] = f"/outputs/similarity_search_samples/{demo_file}"
        fp = r.get("filepath", "")
        if fp in exp_map:
            r["explanation"] = exp_map[fp]
        else:
            r["explanation"] = f"Surface anomaly detected on {cat.replace('_', ' ')}. Visual inspection indicates {r.get('defect_type', 'defect')} with {r.get('severity_level', 'Moderate')} severity ({float(r.get('severity_score', 65)):.1f}/100)."

    sev_payload = {
        "records": records[:150],
        "page": 1,
        "page_size": 20,
        "total_records": len(records),
        "total_pages": (len(records) + 19) // 20
    }
    with open(os.path.join(OUTPUT_DIR, "severity_logs.json"), "w", encoding="utf-8") as f:
        json.dump(sev_payload, f, indent=2)
    print("Exported severity_logs.json")

# 10. Batches
batch_dir = os.path.join(DV_DIR, "batch_inspections")
batches = []
if os.path.exists(batch_dir):
    for name in os.listdir(batch_dir):
        bpath = os.path.join(batch_dir, name)
        if os.path.isdir(bpath):
            rep_file = os.path.join(bpath, "batch_report.json")
            if os.path.exists(rep_file):
                try:
                    with open(rep_file, "r", encoding="utf-8") as f:
                        rep = json.load(f)
                        batches.append({
                            "batch_id": name,
                            "total_inspected": rep.get("total_inspected", 0),
                            "defective_count": rep.get("defective_count", 0),
                            "normal_count": rep.get("normal_count", 0),
                            "defect_rate_pct": rep.get("defect_rate_pct", 0.0),
                            "severity_distribution": rep.get("severity_distribution", {}),
                            "timestamp": rep.get("timestamp", "")
                        })
                        # Save full report for status queries
                        with open(os.path.join(OUTPUT_DIR, f"batch_{name}.json"), "w", encoding="utf-8") as bf:
                            json.dump({
                                "batch_id": name,
                                "status": "completed",
                                "progress": rep.get("total_inspected", 0),
                                "total": rep.get("total_inspected", 0),
                                "report": rep
                            }, bf, indent=2)
                except Exception as e:
                    print("Error reading batch:", e)

with open(os.path.join(OUTPUT_DIR, "batch_list.json"), "w", encoding="utf-8") as f:
    json.dump(batches, f, indent=2)
print("Exported batch_list.json")

# 11. Category Samples
category_samples = []
for cat in known_categories:
    demo_file = f"{cat}_similarity_demo.png"
    sample_path = os.path.join(ROOT_DIR, "frontend", "public", "outputs", "similarity_search_samples", demo_file)
    has_sample = os.path.exists(sample_path)
    category_samples.append({
        "category": cat,
        "has_sample": has_sample,
        "sample_url": f"/outputs/similarity_search_samples/{demo_file}" if has_sample else None,
        "baseline": baselines.get(cat, {})
    })

with open(os.path.join(OUTPUT_DIR, "category_samples.json"), "w", encoding="utf-8") as f:
    json.dump(category_samples, f, indent=2)
print("Exported category_samples.json")

print("All static data successfully exported!")

