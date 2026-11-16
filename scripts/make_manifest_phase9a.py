"""
make_manifest_phase9a.py
Generates cryptographic SHA-256 manifest for Phase 9A deliverables.
"""

import os
import hashlib
import json
import time

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def main():
    target_dir = "research/phase9a_publication_feasibility"
    files = [
        "RESEARCH_HISTORY_SUMMARY.md",
        "CLOSEST_RELATED_WORK.md",
        "EMPIRICAL_RESEARCH_QUESTION.md",
        "BENCHMARK_DESIGN.md",
        "DATA_AND_COMPUTE_FEASIBILITY.md",
        "PUBLICATION_PATH_ASSESSMENT.md",
        "FINAL_GO_NO_GO.md"
    ]

    manifest = {
        "phase": "9A",
        "phase_name": "Research Reset and Publication Feasibility",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "final_decision": "NO-GO — PRIORITIZE PRODUCT AND PORTFOLIO",
        "contingency_decision": "GO — APPLIED SYSTEMS PAPER (Conditional on mandatory academic indexing)",
        "files": []
    }

    for fname in files:
        fpath = os.path.join(target_dir, fname)
        if os.path.exists(fpath):
            sha = compute_sha256(fpath)
            size = os.path.getsize(fpath)
            manifest["files"].append({
                "filename": fname,
                "relative_path": fpath.replace("\\", "/"),
                "sha256": sha,
                "size_bytes": size
            })
            print(f"{fname}: {size} bytes | SHA256: {sha}")
        else:
            print(f"WARNING: Missing file {fpath}")

    out_path = os.path.join(target_dir, "ARTIFACT_MANIFEST.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"\nManifest successfully written to {out_path}")

if __name__ == "__main__":
    main()
