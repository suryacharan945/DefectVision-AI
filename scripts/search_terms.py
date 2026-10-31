import os

search_terms = ['visa', 'capsule', 'visa_development_v2']
matches = []

for root, dirs, files in os.walk('.'):
    if any(x in root for x in ['.venv', '.git', 'node_modules', '.next']):
        continue
    for f in files:
        if f.endswith(('.ipynb', '.py', '.json', '.md', '.csv', '.txt', '.sh')):
            filepath = os.path.join(root, f)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as fp:
                    content = fp.read().lower()
                    for term in search_terms:
                        if term in content:
                            matches.append((term, filepath))
            except Exception:
                pass

for term, p in matches:
    print(f"{term}: {p}")
