import os

cats = ['candle','cashew','chewinggum','fryum','macaroni1','macaroni2','pcb1','pcb2','pcb3','pcb4','pipe_fryum']
exp_dir = r"G:\My Drive\DefectVisionAI\experiments"

cat_matches = {c: [] for c in cats}

for root, dirs, files in os.walk(exp_dir):
    for f in files:
        if f.endswith(('.csv', '.json', '.py', '.log', '.txt', '.md')):
            p = os.path.join(root, f)
            try:
                with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
                    content = fp.read().lower()
                    for c in cats:
                        if c in content:
                            cat_matches[c].append(p)
            except Exception:
                pass

for c, paths in cat_matches.items():
    print(f"=== Category: {c} (matched in {len(paths)} files) ===")
    for p in paths[:5]:
        print(f"  {p}")
