import re

with open('DefectVisionAI/app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines in DefectVisionAI/app.py: {len(lines)}")
for idx, l in enumerate(lines):
    m = re.search(r'@app\.(get|post|put|delete)\((.*?)\)', l)
    if m:
        print(f"L{idx+1:04d}: {m.group(1).upper()} {m.group(2)}")
