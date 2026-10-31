import json
import re

import os

path = r'C:\Users\surya\Downloads\DefectVisionAI (1).ipynb'
with open(path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

print(f"Total cells: {len(nb['cells'])}")

for i, cell in enumerate(nb['cells']):
    src = ''.join(cell.get('source', []))
    if 'Step 11' in src or 'step11' in src or 'uncertainty' in src.lower():
        print(f"\n==========================================")
        print(f"=== Cell {i} (type: {cell.get('cell_type')}) ===")
        print(f"==========================================")
        safe_src = src.encode('ascii', errors='replace').decode('ascii')
        print(safe_src[:1500])
