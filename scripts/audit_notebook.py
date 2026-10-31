import json

nb_path = 'C:/Users/surya/Downloads/DefectVisionAI (1).ipynb'
with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

print(f"Total cells: {len(nb['cells'])}")
for idx, cell in enumerate(nb['cells']):
    ctype = cell.get('cell_type')
    src = ''.join(cell.get('source', []))
    lines = [l for l in src.split('\n') if l.strip()]
    first_non_comment = ""
    comment_header = ""
    for l in lines:
        if l.strip().startswith('#') and not comment_header and not l.strip().startswith('# ==') and not l.strip().startswith('# --'):
            comment_header = l.strip()
        elif not l.strip().startswith('#') and not first_non_comment:
            first_non_comment = l.strip()
    print(f"[{idx:02d}] ({ctype}, {len(lines)} lines) Header: {comment_header[:80]} | Code: {first_non_comment[:70]}")
