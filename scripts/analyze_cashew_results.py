import csv
import os
from collections import Counter

anno_file = r"G:\My Drive\DefectVisionAI\dataset\raw\visa\cashew\image_anno.csv"
anno_types = {}
with open(anno_file, "r", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        fn = os.path.basename(r["image"])
        anno_types[fn] = r["label"]

pred_file = r"release\phase49_independent_results\TEST_PREDICTIONS.csv"
rows = []
with open(pred_file, "r", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

type_counts = Counter()
type_tp = Counter()
type_fn = Counter()

for r in rows:
    if r["ground_truth"] == "1":
        dt = anno_types.get(r["filename"], "unknown")
        r["defect_type"] = dt
        type_counts[dt] += 1
        if r["error_type"] == "TP":
            type_tp[dt] += 1
        else:
            type_fn[dt] += 1

print("=== FINE-GRAINED DEFECT TYPE PERFORMANCE ===")
header = f"{'Defect Type':<40} | Total |  TP |  FN | Recall"
print(header)
print("-" * len(header))
for dt, total in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
    tp = type_tp[dt]
    fn = type_fn[dt]
    rec = tp / total * 100
    print(f"{dt:<40} | {total:>5} | {tp:>3} | {fn:>3} | {rec:>5.1f}%")

with open(pred_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

print("\nUpdated TEST_PREDICTIONS.csv with exact defect categories.")
